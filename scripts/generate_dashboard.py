"""
generate_dashboard.py — Generate dashboard_data.json and copy HTML files to docs/.

Reads /tmp/metrics_cache.json and writes:
  - docs/data/dashboard_data.json   (used by all HTML pages via fetch)

The HTML files (index.html, portfolio_a~d.html) are static and already in docs/.
This script only updates the data JSON that the HTML pages load at runtime.

Usage:
    python scripts/generate_dashboard.py
"""

import json
import os
import sys
from pathlib import Path

METRICS_CACHE = "/tmp/metrics_cache.json"
DOCS_DATA_DIR = Path(__file__).parent.parent / "docs" / "data"


def main() -> None:
    if not os.path.exists(METRICS_CACHE):
        print("ERROR: metrics cache not found. Run calculate_metrics.py first.", file=sys.stderr)
        sys.exit(1)

    with open(METRICS_CACHE) as f:
        data = json.load(f)

    DOCS_DATA_DIR.mkdir(parents=True, exist_ok=True)
    out_path = DOCS_DATA_DIR / "dashboard_data.json"

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"Written dashboard data to {out_path}")
    print(f"  Updated at: {data.get('date', 'unknown')}")
    print(f"  Portfolios: {list(data.get('portfolios', {}).keys())}")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
