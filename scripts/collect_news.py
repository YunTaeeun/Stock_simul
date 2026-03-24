"""
collect_news.py — Collect news from Google News RSS for notable movers.

Targets tickers whose daily return exceeded ±2%.
Fetches top 3 articles per ticker and writes to Google Sheets `news` tab.
Also appends news to /tmp/metrics_cache.json for the dashboard.

Usage:
    python scripts/collect_news.py
"""

import json
import os
import sys
import time
from datetime import date
from urllib.parse import quote

import feedparser
import requests

from config import PORTFOLIOS
from update_sheets import get_spreadsheet, append_rows_dedup

METRICS_CACHE = "/tmp/metrics_cache.json"
MOVE_THRESHOLD = 0.02  # ±2% daily move triggers news fetch
MAX_ARTICLES = 3
REQUEST_DELAY = 1.0  # seconds between RSS requests


def build_rss_url(ticker: str) -> str:
    query = quote(f"{ticker} stock")
    return f"https://news.google.com/rss/search?q={query}&hl=en-US&gl=US&ceid=US:en"


def fetch_ticker_news(ticker: str) -> list[dict]:
    """Fetch up to MAX_ARTICLES news items for a ticker from Google News RSS."""
    url = build_rss_url(ticker)
    try:
        headers = {"User-Agent": "Mozilla/5.0 (compatible; PortfolioSimulator/1.0)"}
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
        feed = feedparser.parse(resp.content)
        articles = []
        for entry in feed.entries[:MAX_ARTICLES]:
            articles.append({
                "title": entry.get("title", ""),
                "url": entry.get("link", ""),
                "source": entry.get("source", {}).get("title", "Google News")
                if isinstance(entry.get("source"), dict)
                else entry.get("source", "Google News"),
            })
        return articles
    except Exception as e:
        print(f"  Warning: could not fetch news for {ticker}: {e}", file=sys.stderr)
        return []


def get_notable_tickers(metrics_cache: dict) -> dict[str, list[str]]:
    """
    Return dict of {ticker: [portfolio_ids]} for tickers with notable moves.
    Falls back to all tickers if no history is available yet.
    """
    notable: dict[str, list[str]] = {}

    for pid, pdata in metrics_cache.get("portfolios", {}).items():
        for h in pdata.get("holdings", []):
            ticker = h["ticker"]
            ret = abs(h.get("return_pct", 0.0))
            # On first run (ret=0), include a few tickers to seed the news tab
            if ret >= MOVE_THRESHOLD * 100 or ret == 0.0:
                if ticker not in notable:
                    notable[ticker] = []
                if pid not in notable[ticker]:
                    notable[ticker].append(pid)

    return notable


def main() -> None:
    today = date.today().isoformat()

    # Load metrics cache to find notable movers
    if not os.path.exists(METRICS_CACHE):
        print("No metrics cache found — skipping news collection.", file=sys.stderr)
        sys.exit(0)

    with open(METRICS_CACHE) as f:
        metrics_cache = json.load(f)

    notable_tickers = get_notable_tickers(metrics_cache)
    print(f"Fetching news for {len(notable_tickers)} tickers: {list(notable_tickers.keys())}")

    spreadsheet = get_spreadsheet()
    all_news_rows = []
    news_by_portfolio: dict[str, list[dict]] = {}

    for ticker, portfolio_ids in notable_tickers.items():
        time.sleep(REQUEST_DELAY)
        articles = fetch_ticker_news(ticker)
        print(f"  {ticker}: {len(articles)} articles")

        for article in articles:
            for pid in portfolio_ids:
                row = [
                    today,
                    ticker,
                    pid,
                    article["title"],
                    article["url"],
                    article["source"],
                ]
                all_news_rows.append(row)

                # Accumulate for metrics cache
                if pid not in news_by_portfolio:
                    news_by_portfolio[pid] = []
                news_by_portfolio[pid].append({
                    "date": today,
                    "ticker": ticker,
                    "title": article["title"],
                    "url": article["url"],
                    "source": article["source"],
                })

    # Write to Sheets
    if all_news_rows:
        appended = append_rows_dedup(
            spreadsheet,
            tab="news",
            rows=all_news_rows,
            key_cols=[0, 1, 3],  # (date, ticker, title)
        )
        print(f"Appended {appended} news rows to Sheets.")
    else:
        print("No news rows to append.")

    # Update metrics cache with news
    for pid, news_list in news_by_portfolio.items():
        if pid in metrics_cache.get("portfolios", {}):
            metrics_cache["portfolios"][pid]["news"] = news_list[:10]

    with open(METRICS_CACHE, "w") as f:
        json.dump(metrics_cache, f, ensure_ascii=False, indent=2)
    print(f"Updated metrics cache with news.")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
