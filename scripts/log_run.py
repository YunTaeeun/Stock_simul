"""
log_run.py — GitHub Actions 실행 결과를 run_logs 탭에 기록.

daily_update.yml의 마지막 스텝에서 항상(성공/실패 무관) 호출됨.

환경변수 (GitHub Actions가 주입):
    STEP_COLLECT_PRICES    : success | failure | skipped
    STEP_CALC_METRICS      : success | failure | skipped
    STEP_COLLECT_NEWS      : success | failure | skipped
    STEP_GEN_DASHBOARD     : success | failure | skipped
    STEP_COLLECT_PRICES_LOG: stderr/stdout 로그 (최대 2000자)
    STEP_CALC_METRICS_LOG  : ...
    STEP_COLLECT_NEWS_LOG  : ...
    STEP_GEN_DASHBOARD_LOG : ...
    GH_RUN_ID              : Actions run ID
    GH_RUN_URL             : Actions run URL
    GOOGLE_SHEETS_ID
    GOOGLE_SERVICE_ACCOUNT_JSON
"""

import os
import sys
from datetime import datetime, timezone

from update_sheets import get_spreadsheet

TAB = "run_logs"
HEADERS = [
    "run_at",          # KST datetime
    "run_date",        # YYYY-MM-DD
    "overall_status",  # success | failure
    "collect_prices",
    "calc_metrics",
    "collect_news",
    "gen_dashboard",
    "error_summary",   # 첫 번째 실패 스텝의 로그 요약
    "gh_run_id",
    "gh_run_url",
]

MAX_LOG_CHARS = 1500


def _truncate(text: str, max_chars: int = MAX_LOG_CHARS) -> str:
    if len(text) <= max_chars:
        return text
    half = max_chars // 2
    return text[:half] + "\n...[중략]...\n" + text[-half:]


def main() -> None:
    now_utc = datetime.now(timezone.utc)
    # KST = UTC+9
    now_kst = now_utc.replace(tzinfo=None)
    run_at = (now_utc.strftime("%Y-%m-%d %H:%M:%S UTC"))
    run_date = now_utc.strftime("%Y-%m-%d")

    steps = {
        "collect_prices": os.environ.get("STEP_COLLECT_PRICES", "unknown"),
        "calc_metrics":   os.environ.get("STEP_CALC_METRICS",   "unknown"),
        "collect_news":   os.environ.get("STEP_COLLECT_NEWS",   "unknown"),
        "gen_dashboard":  os.environ.get("STEP_GEN_DASHBOARD",  "unknown"),
    }
    step_logs = {
        "collect_prices": os.environ.get("STEP_COLLECT_PRICES_LOG", ""),
        "calc_metrics":   os.environ.get("STEP_CALC_METRICS_LOG",   ""),
        "collect_news":   os.environ.get("STEP_COLLECT_NEWS_LOG",   ""),
        "gen_dashboard":  os.environ.get("STEP_GEN_DASHBOARD_LOG",  ""),
    }

    failed_steps = [k for k, v in steps.items() if v == "failure"]
    overall = "failure" if failed_steps else "success"

    # 실패한 스텝들의 로그 합산
    error_summary = ""
    if failed_steps:
        parts = []
        for s in failed_steps:
            log = step_logs.get(s, "").strip()
            if log:
                parts.append(f"[{s}]\n{_truncate(log)}")
        error_summary = "\n\n".join(parts) if parts else f"Failed steps: {failed_steps}"

    gh_run_id  = os.environ.get("GH_RUN_ID", "")
    gh_run_url = os.environ.get("GH_RUN_URL", "")

    row = [
        run_at,
        run_date,
        overall,
        steps["collect_prices"],
        steps["calc_metrics"],
        steps["collect_news"],
        steps["gen_dashboard"],
        error_summary,
        gh_run_id,
        gh_run_url,
    ]

    spreadsheet = get_spreadsheet()

    # 탭 없으면 생성
    try:
        ws = spreadsheet.worksheet(TAB)
    except Exception:
        ws = spreadsheet.add_worksheet(title=TAB, rows=3000, cols=len(HEADERS))
        ws.update("A1", [HEADERS])
        print(f"Created tab: {TAB}")

    # 헤더 확인/수정
    first_row = ws.row_values(1)
    if first_row != HEADERS:
        ws.update("A1", [HEADERS])

    ws.append_rows([row], value_input_option="USER_ENTERED")
    print(f"Logged run: {overall} | {run_at}")
    if failed_steps:
        print(f"Failed steps: {failed_steps}", file=sys.stderr)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"log_run.py ERROR: {e}", file=sys.stderr)
        sys.exit(0)  # 로그 기록 실패가 전체 파이프라인을 막으면 안 됨
