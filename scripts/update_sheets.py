"""
update_sheets.py — Shared Google Sheets utility for the pipeline.

Provides:
  - get_spreadsheet()       : authenticated gspread Spreadsheet object
  - append_rows_dedup()     : append rows, skipping duplicates by key columns
  - read_tab_as_records()   : read a worksheet as list of dicts
  - overwrite_tab_data()    : replace all data rows (keep header)
"""

import json
import os
from typing import Any

import gspread
from google.oauth2.service_account import Credentials

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

_spreadsheet_cache: gspread.Spreadsheet | None = None


def _get_client() -> gspread.Client:
    key_json = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON")
    if not key_json:
        raise EnvironmentError("GOOGLE_SERVICE_ACCOUNT_JSON env var is not set.")
    info = json.loads(key_json)
    creds = Credentials.from_service_account_info(info, scopes=SCOPES)
    return gspread.authorize(creds)


def get_spreadsheet() -> gspread.Spreadsheet:
    global _spreadsheet_cache
    if _spreadsheet_cache is not None:
        return _spreadsheet_cache
    sheets_id = os.environ.get("GOOGLE_SHEETS_ID")
    if not sheets_id:
        raise EnvironmentError("GOOGLE_SHEETS_ID env var is not set.")
    client = _get_client()
    _spreadsheet_cache = client.open_by_key(sheets_id)
    return _spreadsheet_cache


def _make_key(row: list, key_cols: list[int]) -> tuple:
    return tuple(str(row[i]) for i in key_cols)


def append_rows_dedup(
    spreadsheet: gspread.Spreadsheet,
    tab: str,
    rows: list[list],
    key_cols: list[int],
) -> int:
    """
    Append rows to a worksheet, skipping any row whose key already exists.
    Returns the number of rows actually appended.
    """
    if not rows:
        return 0

    ws = spreadsheet.worksheet(tab)
    existing = ws.get_all_values()
    # Build set of existing keys from data rows (skip header row 0)
    existing_keys = set()
    for existing_row in existing[1:]:
        existing_keys.add(_make_key(existing_row, key_cols))

    new_rows = [r for r in rows if _make_key(r, key_cols) not in existing_keys]
    if new_rows:
        ws.append_rows(new_rows, value_input_option="USER_ENTERED")
    return len(new_rows)


def read_tab_as_records(
    spreadsheet: gspread.Spreadsheet,
    tab: str,
) -> list[dict[str, Any]]:
    """Read all data rows from a tab, returning list of dicts keyed by header."""
    ws = spreadsheet.worksheet(tab)
    return ws.get_all_records()


def overwrite_tab_data(
    spreadsheet: gspread.Spreadsheet,
    tab: str,
    header: list[str],
    rows: list[list],
) -> None:
    """Replace all data in a tab (keeps header in row 1, clears rest, writes rows)."""
    ws = spreadsheet.worksheet(tab)
    # Clear all data below header
    all_values = ws.get_all_values()
    if len(all_values) > 1:
        last_row = len(all_values)
        ws.delete_rows(2, last_row)

    # Ensure header is correct
    ws.update("A1", [header])

    if rows:
        ws.append_rows(rows, value_input_option="USER_ENTERED")
