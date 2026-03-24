# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 프로젝트 개요

8개 테마 포트폴리오(A~H)에 각 1,000만원 가상 투자 후 매일 수익률을 자동 수집·계산하여 GitHub Pages 대시보드로 시각화하는 투자 시뮬레이션 플랫폼.

- **데이터 수집**: yfinance (US 마켓 전 종목)
- **저장소**: Google Sheets (gspread + 서비스 계정 인증)
- **자동화**: GitHub Actions 매일 UTC 23:00 (KST 08:00, 미국 장 마감 후)
- **프론트엔드**: GitHub Pages (순수 HTML + Chart.js, 빌드 없음)

## 로컬 실행 명령어

```bash
# 의존성 설치
pip install -r requirements.txt

# 환경변수 설정 (필수)
export GOOGLE_SHEETS_ID="..."
export GOOGLE_SERVICE_ACCOUNT_JSON='{"type":"service_account",...}'

# 파이프라인 전체 (순서 중요)
cd scripts
python collect_prices.py      # /tmp/prices_cache.json, /tmp/fx_cache.json 생성
python calculate_metrics.py   # /tmp/metrics_cache.json 생성
python collect_news.py
python generate_dashboard.py  # docs/data/dashboard_data.json 생성

# Sheets 초기화 (최초 1회 또는 포트폴리오 추가 시)
python init_sheets.py
```

스크립트는 모두 `scripts/` 디렉터리에서 실행해야 한다 (`from config import ...` 등 상대 임포트 사용).

## 아키텍처

### 데이터 파이프라인 흐름

```
collect_prices.py
  → /tmp/prices_cache.json (ticker→close)
  → /tmp/fx_cache.json (usd_krw)
  → Sheets: prices, fx_rate

calculate_metrics.py
  ← /tmp/prices_cache.json, /tmp/fx_cache.json
  ← Sheets: prices (전체 이력), holdings
  → /tmp/metrics_cache.json (포트폴리오별 metrics + history + holdings 상세)
  → Sheets: portfolio_value, analysis

collect_news.py
  ← Sheets: prices (당일 변동 ±2% 종목 필터링)
  → Sheets: news

generate_dashboard.py
  ← /tmp/metrics_cache.json
  → docs/data/dashboard_data.json
```

`/tmp/` 캐시 파일은 동일 Actions 실행 내 스크립트 간 데이터 전달용. 로컬 테스트 시에도 반드시 순서대로 실행해야 한다.

### `scripts/config.py` — 유일한 포트폴리오 정의 소스

`PORTFOLIOS` 딕셔너리가 단일 진실 공급원. 모든 Python 스크립트는 `PORTFOLIOS.items()`로 동적 순회하므로 **새 포트폴리오 추가 시 `config.py`만 수정하면 Python 파이프라인은 자동 반영**된다.

```python
PORTFOLIOS = {
    "ID": {
        "name": "...",
        "theme": "...",
        "holdings": [
            {"ticker": "...", "name": "...", "weight": 0.xx, "category": "etf"|"individual"},
            ...  # weight 합계 = 1.0
        ],
    },
}
```

### `scripts/update_sheets.py` — Sheets 공통 유틸

모든 스크립트가 임포트하는 공유 모듈:
- `get_spreadsheet()`: 서비스 계정 인증 + Spreadsheet 객체 반환 (모듈 수준 캐싱)
- `append_rows_dedup(spreadsheet, tab, rows, key_cols)`: 키 컬럼 기준 중복 제거 후 append
- `read_tab_as_records(spreadsheet, tab)`: 헤더를 키로 한 dict 리스트 반환

### `docs/` — GitHub Pages 정적 파일

HTML 파일은 런타임에 `docs/data/dashboard_data.json`을 `fetch()`로 로드. **HTML 파일 자체는 빌드 산출물이 아니라 저장소에 직접 커밋**.

`dashboard_data.json` 스키마:
```json
{
  "date": "YYYY-MM-DD",
  "usd_krw": 1350.5,
  "portfolios": {
    "A": {
      "name": "...", "theme": "...",
      "value_krw": 10000000, "pnl_krw": 0, "return_pct": 0.0,
      "metrics": {"cum_return": 0, "mdd": 0, "volatility": 0, "sharpe": 0, "beta": 1},
      "history": [{"date": "YYYY-MM-DD", "value": 10000000}, ...],
      "holdings": [{"ticker": "...", "name": "...", "weight": 0.25, "category": "etf", "return_pct": 0, "pnl_krw": 0}, ...]
    }
  }
}
```

### HTML 파일 색상 체계

새 포트폴리오를 추가하면 HTML도 수동으로 업데이트해야 한다:

| 포트폴리오 | 색상 |
|-----------|------|
| A | `#6366f1` (indigo) |
| B | `#f59e0b` (amber) |
| C | `#10b981` (emerald) |
| D | `#f97316` (orange) |
| E | `#8b5cf6` (violet) |
| F | `#06b6d4` (cyan) |
| G | `#ef4444` (red) |
| H | `#ec4899` (pink) |

`docs/index.html`의 수정 위치: `:root` CSS 변수, `.badge-X` 클래스, `PORTFOLIO_PAGES` 객체, `COLORS` 객체.
새 상세 페이지(`docs/portfolio_x.html`)는 기존 파일을 복사 후 `PORTFOLIO_ID`, `ACCENT`, `<title>`, `<h1>` 3곳만 변경.

## Google Sheets 탭 구조

| 탭 | 키 컬럼 | 설명 |
|----|---------|------|
| config | id | 포트폴리오 메타 |
| holdings | portfolio_id, ticker | 종목 구성 |
| prices | date, ticker | 일별 종가 (USD) |
| fx_rate | date | USD/KRW 환율 |
| portfolio_value | date, portfolio_id | 일별 평가금액 |
| analysis | date, portfolio_id | MDD·변동성·샤프·베타 |
| news | date, ticker, url | 관련 뉴스 (URL 기준 dedup) |

## GitHub Actions 워크플로우

| 파일 | 트리거 | 역할 |
|------|--------|------|
| `daily_update.yml` | 매일 UTC 23:00 + 수동 | 전체 파이프라인 실행 → Pages 배포 |
| `init_sheets.yml` | 수동만 | Sheets 탭 초기화 (포트폴리오 추가 후 재실행 필요) |

필요한 Secrets: `GOOGLE_SHEETS_ID`, `GOOGLE_SERVICE_ACCOUNT_JSON`
