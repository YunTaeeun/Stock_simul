"""
backfill_prices.py — Backfill historical price data for tickers missing from Sheets.

Finds the earliest date already in the `prices` tab and fetches yfinance history
for any ticker not covered from that start date. Useful when new portfolios (E~H)
are added after the simulation has already started.

Usage:
    cd scripts
    python backfill_prices.py
"""

import json
import sys
from datetime import date, timedelta

import yfinance as yf
import pandas as pd

from config import PORTFOLIOS, BENCHMARK_TICKER, get_all_tickers
from update_sheets import get_spreadsheet, read_tab_as_records, append_rows_dedup


def get_start_date(price_records: list[dict]) -> str | None:
    """Return the earliest date found in existing price records."""
    dates = [r["date"] for r in price_records if r.get("date")]
    return min(dates) if dates else None


def fetch_history(tickers: list[str], start: str, end: str) -> dict[str, dict[str, float]]:
    """
    Fetch daily closing prices for each ticker from start to end (inclusive).

    Returns: { date_str: { ticker: close_price } }
    """
    print(f"Fetching history for {len(tickers)} tickers from {start} to {end}...")
    # yfinance end date is exclusive, add 1 day
    end_dt = (pd.Timestamp(end) + pd.Timedelta(days=1)).strftime("%Y-%m-%d")
    data = yf.download(tickers, start=start, end=end_dt, auto_adjust=True, progress=False)

    result: dict[str, dict[str, float]] = {}

    if data.empty:
        return result

    if isinstance(data.columns, pd.MultiIndex):
        close_data = data["Close"]
    else:
        close_data = data[["Close"]]
        if len(tickers) == 1:
            close_data.columns = tickers

    for idx, row in close_data.iterrows():
        day = str(idx.date())
        for ticker in tickers:
            if ticker in close_data.columns:
                val = row[ticker]
                if pd.notna(val):
                    result.setdefault(day, {})[ticker] = round(float(val), 4)

    return result


def main() -> None:
    spreadsheet = get_spreadsheet()

    print("Reading existing prices from Sheets...")
    price_records = read_tab_as_records(spreadsheet, "prices")

    start_date = get_start_date(price_records)
    if not start_date:
        print("No existing price data found. Run the daily pipeline first.", file=sys.stderr)
        sys.exit(1)

    today = date.today().isoformat()
    print(f"Simulation start date detected: {start_date}")
    print(f"Backfill target range: {start_date} → {today}")

    # Find which (date, ticker) pairs already exist
    existing_keys = {(r["date"], r["ticker"]) for r in price_records}

    all_tickers = get_all_tickers()

    # Find tickers that are missing ANY day in the range
    missing_tickers = set()
    for ticker in all_tickers:
        # Check if this ticker has data from the start date
        ticker_dates = {r["date"] for r in price_records if r["ticker"] == ticker}
        if start_date not in ticker_dates:
            missing_tickers.add(ticker)

    if not missing_tickers:
        print("All tickers already have data from the start date. Nothing to backfill.")
        return

    print(f"Tickers missing history: {sorted(missing_tickers)}")

    # Fetch historical data
    history = fetch_history(list(missing_tickers), start_date, today)

    if not history:
        print("No historical data returned from yfinance.", file=sys.stderr)
        sys.exit(1)

    # Build rows to insert (skip already-existing keys)
    rows = []
    for day, ticker_prices in sorted(history.items()):
        for ticker, close in ticker_prices.items():
            if (day, ticker) not in existing_keys:
                rows.append([day, ticker, close, "USD"])

    if not rows:
        print("No new rows to insert (all already present).")
        return

    print(f"Inserting {len(rows)} missing price rows into Sheets...")
    append_rows_dedup(spreadsheet, "prices", rows, key_cols=[0, 1])
    print("Backfill complete.")
    print("Now re-run calculate_metrics.py and generate_dashboard.py to refresh the dashboard.")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
