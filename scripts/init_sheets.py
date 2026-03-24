"""
init_sheets.py — One-time setup script.

Creates all required Google Sheets tabs and seeds config + holdings data.
Run this once before the daily pipeline starts.

Usage:
    python scripts/init_sheets.py

Required env vars:
    GOOGLE_SHEETS_ID              — Spreadsheet ID from the URL
    GOOGLE_SERVICE_ACCOUNT_JSON   — Service account key JSON (as string)
"""

import json
import os
import sys
from datetime import date

import gspread
from google.oauth2.service_account import Credentials

from config import PORTFOLIOS

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

TAB_HEADERS = {
    "config":          ["id", "name", "theme", "created_at", "active"],
    "holdings":        ["portfolio_id", "ticker", "name", "market", "weight", "category"],
    "prices":          ["date", "ticker", "close", "currency"],
    "fx_rate":         ["date", "usd_krw"],
    "portfolio_value": ["date", "portfolio_id", "value_krw", "pnl_krw", "return_pct"],
    "analysis":        ["date", "portfolio_id", "cum_return", "mdd", "volatility", "sharpe", "beta"],
    "news":            ["date", "ticker", "portfolio_id", "title", "url", "source"],
}


def get_client() -> gspread.Client:
    key_json = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON")
    if not key_json:
        raise EnvironmentError("GOOGLE_SERVICE_ACCOUNT_JSON env var is not set.")
    info = json.loads(key_json)
    creds = Credentials.from_service_account_info(info, scopes=SCOPES)
    return gspread.authorize(creds)


def get_or_create_worksheet(spreadsheet: gspread.Spreadsheet, title: str) -> gspread.Worksheet:
    """Return existing worksheet or create a new one."""
    try:
        return spreadsheet.worksheet(title)
    except gspread.WorksheetNotFound:
        ws = spreadsheet.add_worksheet(title=title, rows=5000, cols=20)
        print(f"  Created tab: {title}")
        return ws


def init_tab(spreadsheet: gspread.Spreadsheet, tab_name: str) -> gspread.Worksheet:
    """Ensure tab exists and has correct headers in row 1."""
    ws = get_or_create_worksheet(spreadsheet, tab_name)
    headers = TAB_HEADERS[tab_name]
    first_row = ws.row_values(1)
    if first_row != headers:
        ws.update("A1", [headers])
        print(f"  Set headers for: {tab_name}")
    return ws


def seed_config(ws: gspread.Worksheet) -> None:
    """Write portfolio metadata rows (skip if already present)."""
    existing = ws.get_all_records()
    existing_ids = {r["id"] for r in existing}
    today = date.today().isoformat()

    rows = []
    for pid, portfolio in PORTFOLIOS.items():
        if pid not in existing_ids:
            rows.append([pid, portfolio["name"], portfolio["theme"], today, True])

    if rows:
        ws.append_rows(rows, value_input_option="USER_ENTERED")
        print(f"  Seeded {len(rows)} portfolios into config tab.")
    else:
        print("  config tab: already seeded, skipping.")


def seed_holdings(ws: gspread.Worksheet) -> None:
    """Write holdings rows (skip if already present)."""
    existing = ws.get_all_records()
    existing_keys = {(r["portfolio_id"], r["ticker"]) for r in existing}

    rows = []
    for pid, portfolio in PORTFOLIOS.items():
        for h in portfolio["holdings"]:
            key = (pid, h["ticker"])
            if key not in existing_keys:
                rows.append([
                    pid,
                    h["ticker"],
                    h["name"],
                    "US",
                    h["weight"],
                    h["category"],
                ])

    if rows:
        ws.append_rows(rows, value_input_option="USER_ENTERED")
        print(f"  Seeded {len(rows)} holdings into holdings tab.")
    else:
        print("  holdings tab: already seeded, skipping.")


def main() -> None:
    sheets_id = os.environ.get("GOOGLE_SHEETS_ID")
    if not sheets_id:
        raise EnvironmentError("GOOGLE_SHEETS_ID env var is not set.")

    print("Connecting to Google Sheets...")
    client = get_client()
    spreadsheet = client.open_by_key(sheets_id)
    print(f"Opened spreadsheet: {spreadsheet.title}")

    print("\nInitializing tabs...")
    worksheets = {}
    for tab_name in TAB_HEADERS:
        worksheets[tab_name] = init_tab(spreadsheet, tab_name)

    print("\nSeeding initial data...")
    seed_config(worksheets["config"])
    seed_holdings(worksheets["holdings"])

    print("\nDone! Google Sheets is ready.")
    print(f"Spreadsheet URL: https://docs.google.com/spreadsheets/d/{sheets_id}")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
