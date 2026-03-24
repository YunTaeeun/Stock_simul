"""
collect_prices.py — Collect stock prices and USD/KRW exchange rate via yfinance.

Writes results to:
  - Google Sheets `prices` tab  (date, ticker, close, currency)
  - Google Sheets `fx_rate` tab (date, usd_krw)

Also saves a local cache at /tmp/prices_cache.json for use by
calculate_metrics.py in the same pipeline run.

Usage:
    python scripts/collect_prices.py
"""

import json
import os
import sys
from datetime import date, timedelta

import yfinance as yf
import pandas as pd

from config import PORTFOLIOS, BENCHMARK_TICKER, get_all_tickers
from update_sheets import get_spreadsheet, append_rows_dedup

PRICES_CACHE = "/tmp/prices_cache.json"
FX_CACHE = "/tmp/fx_cache.json"


def fetch_prices(tickers: list[str]) -> dict[str, float]:
    """Fetch the latest closing price for each ticker."""
    print(f"Fetching prices for {len(tickers)} tickers...")
    data = yf.download(tickers, period="5d", auto_adjust=True, progress=False)

    prices = {}
    if isinstance(data.columns, pd.MultiIndex):
        close_data = data["Close"]
    else:
        close_data = data[["Close"]]
        close_data.columns = tickers

    for ticker in tickers:
        if ticker in close_data.columns:
            series = close_data[ticker].dropna()
            if not series.empty:
                prices[ticker] = round(float(series.iloc[-1]), 4)
                print(f"  {ticker}: {prices[ticker]}")
            else:
                print(f"  {ticker}: NO DATA", file=sys.stderr)
        else:
            print(f"  {ticker}: NOT FOUND", file=sys.stderr)

    return prices


def fetch_fx_rate() -> float:
    """Fetch USD/KRW exchange rate."""
    print("Fetching USD/KRW exchange rate...")
    data = yf.download("USDKRW=X", period="5d", auto_adjust=True, progress=False)
    close = data["Close"]
    # yfinance may return a DataFrame (single-column) or Series depending on version
    if isinstance(close, pd.DataFrame):
        close = close.iloc[:, 0]
    close = close.dropna()
    if close.empty:
        raise ValueError("Could not fetch USD/KRW rate.")
    val = close.iloc[-1]
    # Guard against scalar still being a Series
    if isinstance(val, pd.Series):
        val = val.iloc[0]
    rate = round(float(val), 2)
    print(f"  USD/KRW: {rate}")
    return rate


def build_price_rows(prices: dict[str, float], today: str) -> list[list]:
    """Build rows for the prices tab."""
    rows = []
    for ticker, close in prices.items():
        rows.append([today, ticker, close, "USD"])
    return rows


def main() -> None:
    today = date.today().isoformat()
    tickers = get_all_tickers()

    # Collect prices
    prices = fetch_prices(tickers)
    fx_rate = fetch_fx_rate()

    # Save local cache for downstream scripts
    with open(PRICES_CACHE, "w") as f:
        json.dump({"date": today, "prices": prices}, f)
    with open(FX_CACHE, "w") as f:
        json.dump({"date": today, "usd_krw": fx_rate}, f)
    print(f"Saved price cache to {PRICES_CACHE}")
    print(f"Saved FX cache to {FX_CACHE}")

    # Write to Google Sheets
    spreadsheet = get_spreadsheet()

    price_rows = build_price_rows(prices, today)
    append_rows_dedup(
        spreadsheet,
        tab="prices",
        rows=price_rows,
        key_cols=[0, 1],  # (date, ticker)
    )
    print(f"Updated prices tab: {len(price_rows)} rows for {today}")

    fx_rows = [[today, fx_rate]]
    append_rows_dedup(
        spreadsheet,
        tab="fx_rate",
        rows=fx_rows,
        key_cols=[0],  # (date,)
    )
    print(f"Updated fx_rate tab: {fx_rate} for {today}")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
