# 📊 Portfolio Simulator

8개 테마 포트폴리오에 각 1,000만원을 가상 투자하고, 매일 수익률을 자동 수집하며 학습하는 투자 시뮬레이션 플랫폼입니다.

> ⚠️ 이 프로젝트는 **투자 학습 목적의 가상 시뮬레이션**입니다. 실제 투자 판단의 근거로 사용하지 마세요.

## 포트폴리오 구성

| ID | 테마 | 주요 종목 |
|----|------|---------|
| A | AI·빅테크·반도체 | QQQ, SOXX, SMH, NVDA, PLTR |
| B | 금·원자재·식품 | GLD, SLV, PDBC, NEM, WPM |
| C | 바이오·헬스케어 | IBB, XBI, XLV, LLY, NVO |
| D | 에너지 | XLE, VDE, XOP, URA, CEG |
| E | 방산·우주·사이버보안 | ITA, SHLD, XAR, HACK, LMT |
| F | 금융·핀테크 | XLF, VFH, KRE, FINX, JPM |
| G | 중국·신흥국 | MCHI, KWEB, FXI, EEM, BABA |
| H | 소비재·경기순환 | XLY, XLP, VCR, IBUY, AMZN |

## 기술 스택

- **데이터 수집**: Python + yfinance
- **데이터 저장**: Google Sheets (gspread)
- **자동화**: GitHub Actions (매일 UTC 23:00)
- **대시보드**: GitHub Pages (HTML + Chart.js)
- **뉴스**: Google News RSS

---

## 초기 설정 가이드

### 1. Google Cloud 서비스 계정 설정

1. [Google Cloud Console](https://console.cloud.google.com/) 접속
2. 새 프로젝트 생성 (또는 기존 프로젝트 선택)
3. **API 및 서비스 → 라이브러리** 에서 활성화:
   - Google Sheets API
   - Google Drive API
4. **API 및 서비스 → 사용자 인증 정보 → 서비스 계정 만들기**
5. 서비스 계정 생성 후 **키 → JSON 키 추가** → JSON 파일 다운로드

### 2. Google Sheets 생성

1. [Google Sheets](https://sheets.google.com) 에서 새 스프레드시트 생성
2. 스프레드시트 이름: `Portfolio Simulator` (자유)
3. URL에서 Spreadsheet ID 복사:
   ```
   https://docs.google.com/spreadsheets/d/[SPREADSHEET_ID]/edit
   ```
4. 서비스 계정 이메일(JSON의 `client_email`)을 스프레드시트 **편집자**로 공유

### 3. GitHub Secrets 등록

레포지토리 **Settings → Secrets and variables → Actions → New repository secret**:

| Secret 이름 | 값 |
|------------|-----|
| `GOOGLE_SHEETS_ID` | 스프레드시트 ID (위에서 복사한 값) |
| `GOOGLE_SERVICE_ACCOUNT_JSON` | 다운로드한 JSON 파일의 전체 내용을 붙여넣기 |

### 4. GitHub Pages 설정

**Settings → Pages**:
- Source: `Deploy from a branch` → **GitHub Actions** 선택

### 5. 최초 Sheets 초기화

로컬에서 1회 실행:

```bash
pip install -r requirements.txt

export GOOGLE_SHEETS_ID="your_spreadsheet_id"
export GOOGLE_SERVICE_ACCOUNT_JSON='{"type":"service_account",...}'  # JSON 내용

cd scripts
python init_sheets.py
```

성공 시 Sheets에 7개 탭(config, holdings, prices, fx_rate, portfolio_value, analysis, news)이 생성됩니다.

### 6. 수동 실행 테스트

GitHub Actions **Actions 탭 → Daily Portfolio Update → Run workflow** 클릭

---

## 파일 구조

```
Stock_simul/
├── .github/workflows/
│   └── daily_update.yml    # 매일 UTC 23:00 자동 실행
├── scripts/
│   ├── config.py           # 포트폴리오 A~H 구성 데이터
│   ├── init_sheets.py      # 최초 1회: Sheets 탭 초기화
│   ├── collect_prices.py   # yfinance 주가·환율 수집
│   ├── calculate_metrics.py # MDD·변동성·샤프·베타 계산
│   ├── collect_news.py     # Google News RSS 수집
│   ├── update_sheets.py    # gspread 공통 유틸
│   └── generate_dashboard.py # dashboard_data.json 생성
├── docs/                   # GitHub Pages 루트
│   ├── index.html          # 비교 대시보드
│   ├── portfolio_a.html    # AI·반도체 상세
│   ├── portfolio_b.html    # 금·원자재 상세
│   ├── portfolio_c.html    # 바이오 상세
│   ├── portfolio_d.html    # 에너지 상세
│   ├── portfolio_e.html    # 방산·우주·사이버보안 상세
│   ├── portfolio_f.html    # 금융·핀테크 상세
│   ├── portfolio_g.html    # 중국·신흥국 상세
│   ├── portfolio_h.html    # 소비재·경기순환 상세
│   └── data/
│       └── dashboard_data.json  # 매일 자동 갱신
└── requirements.txt
```

## Google Sheets 탭 구조

| 탭명 | 설명 |
|------|------|
| config | 포트폴리오 메타 정보 |
| holdings | 종목 구성 및 비중 |
| prices | 종목별 일별 종가 |
| fx_rate | USD/KRW 환율 이력 |
| portfolio_value | 포트폴리오별 일별 평가금액 |
| analysis | MDD·변동성·샤프·베타 이력 |
| news | 관련 뉴스 피드 |
