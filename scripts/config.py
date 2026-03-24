"""
Portfolio configuration data for A~D portfolios.
Each portfolio has 10,000,000 KRW initial investment.
All tickers are US market (yfinance compatible).
"""

INITIAL_INVESTMENT = 10_000_000  # KRW per portfolio

PORTFOLIOS = {
    "A": {
        "name": "AI·빅테크·반도체",
        "theme": "인공지능 인프라, 빅테크 플랫폼, 반도체 설계/제조 전 밸류체인",
        "holdings": [
            {"ticker": "QQQ",  "name": "Invesco Nasdaq-100 ETF",      "weight": 0.25, "category": "etf"},
            {"ticker": "SOXX", "name": "iShares Semiconductor ETF",   "weight": 0.20, "category": "etf"},
            {"ticker": "SMH",  "name": "VanEck Semiconductor ETF",    "weight": 0.18, "category": "etf"},
            {"ticker": "CHAT", "name": "Roundhill Generative AI ETF", "weight": 0.10, "category": "etf"},
            {"ticker": "NVDA", "name": "Nvidia",                      "weight": 0.07, "category": "etf"},
            {"ticker": "PLTR", "name": "Palantir Technologies",       "weight": 0.04, "category": "individual"},
            {"ticker": "TSM",  "name": "Taiwan Semiconductor (TSMC)", "weight": 0.04, "category": "individual"},
            {"ticker": "AVGO", "name": "Broadcom",                    "weight": 0.03, "category": "individual"},
            {"ticker": "TSLA", "name": "Tesla",                       "weight": 0.03, "category": "individual"},
            {"ticker": "MU",   "name": "Micron Technology",           "weight": 0.03, "category": "individual"},
            {"ticker": "AMAT", "name": "Applied Materials",           "weight": 0.03, "category": "individual"},
        ],
    },
    "B": {
        "name": "금·원자재·식품",
        "theme": "인플레이션 헤지, 안전자산, 실물 원자재, 농산물 식량 안보",
        "holdings": [
            {"ticker": "GLD",  "name": "SPDR Gold Shares",            "weight": 0.25, "category": "etf"},
            {"ticker": "SLV",  "name": "iShares Silver Trust",        "weight": 0.20, "category": "etf"},
            {"ticker": "PDBC", "name": "Invesco Commodity ETF",       "weight": 0.18, "category": "etf"},
            {"ticker": "DBA",  "name": "Invesco Agriculture ETF",     "weight": 0.10, "category": "etf"},
            {"ticker": "GDX",  "name": "VanEck Gold Miners ETF",      "weight": 0.07, "category": "etf"},
            {"ticker": "NEM",  "name": "Newmont Corporation",         "weight": 0.04, "category": "individual"},
            {"ticker": "WPM",  "name": "Wheaton Precious Metals",     "weight": 0.04, "category": "individual"},
            {"ticker": "GOLD", "name": "Barrick Gold",                "weight": 0.03, "category": "individual"},
            {"ticker": "FNV",  "name": "Franco-Nevada",               "weight": 0.03, "category": "individual"},
            {"ticker": "COPX", "name": "Global X Copper Miners ETF",  "weight": 0.03, "category": "individual"},
            {"ticker": "KGC",  "name": "Kinross Gold",                "weight": 0.03, "category": "individual"},
        ],
    },
    "C": {
        "name": "바이오·헬스케어",
        "theme": "바이오텍 혁신, 유전체 치료, 비만·항암·희귀질환 신약 개발",
        "holdings": [
            {"ticker": "IBB",  "name": "iShares Biotechnology ETF",        "weight": 0.28, "category": "etf"},
            {"ticker": "XBI",  "name": "SPDR S&P Biotech ETF",             "weight": 0.22, "category": "etf"},
            {"ticker": "XLV",  "name": "Health Care Select Sector SPDR",   "weight": 0.20, "category": "etf"},
            {"ticker": "ARKG", "name": "ARK Genomic Revolution ETF",       "weight": 0.10, "category": "etf"},
            {"ticker": "LLY",  "name": "Eli Lilly",                        "weight": 0.05, "category": "individual"},
            {"ticker": "NVO",  "name": "Novo Nordisk",                     "weight": 0.04, "category": "individual"},
            {"ticker": "REGN", "name": "Regeneron Pharmaceuticals",        "weight": 0.03, "category": "individual"},
            {"ticker": "CRSP", "name": "CRISPR Therapeutics",              "weight": 0.03, "category": "individual"},
            {"ticker": "MRNA", "name": "Moderna",                          "weight": 0.03, "category": "individual"},
            {"ticker": "RXRX", "name": "Recursion Pharmaceuticals",        "weight": 0.02, "category": "individual"},
        ],
    },
    "D": {
        "name": "에너지",
        "theme": "전통 화석연료, 청정에너지 전환, 핵에너지, AI 데이터센터 전력 수요",
        "holdings": [
            {"ticker": "XLE",  "name": "Energy Select Sector SPDR ETF",   "weight": 0.28, "category": "etf"},
            {"ticker": "VDE",  "name": "Vanguard Energy ETF",             "weight": 0.20, "category": "etf"},
            {"ticker": "XOP",  "name": "S&P Oil & Gas Explor ETF",        "weight": 0.15, "category": "etf"},
            {"ticker": "ICLN", "name": "iShares Global Clean Energy ETF", "weight": 0.10, "category": "etf"},
            {"ticker": "URA",  "name": "Global X Uranium ETF",            "weight": 0.07, "category": "etf"},
            {"ticker": "CVX",  "name": "Chevron Corporation",             "weight": 0.04, "category": "individual"},
            {"ticker": "LNG",  "name": "Cheniere Energy",                 "weight": 0.04, "category": "individual"},
            {"ticker": "CEG",  "name": "Constellation Energy",            "weight": 0.03, "category": "individual"},
            {"ticker": "FSLR", "name": "First Solar",                     "weight": 0.03, "category": "individual"},
            {"ticker": "VG",   "name": "Venture Global LNG",              "weight": 0.03, "category": "individual"},
            {"ticker": "SMR",  "name": "NuScale Power",                   "weight": 0.03, "category": "individual"},
        ],
    },
    "E": {
        "name": "방산·우주·사이버보안",
        "theme": "지정학 리스크, NATO 국방비 확대, AI 기반 사이버 위협, 우주 경쟁",
        "holdings": [
            {"ticker": "ITA",  "name": "iShares U.S. Aerospace & Defense ETF", "weight": 0.25, "category": "etf"},
            {"ticker": "SHLD", "name": "Global X Defense Tech ETF",            "weight": 0.20, "category": "etf"},
            {"ticker": "XAR",  "name": "SPDR S&P Aerospace & Defense ETF",     "weight": 0.15, "category": "etf"},
            {"ticker": "HACK", "name": "Amplify Cybersecurity ETF",            "weight": 0.12, "category": "etf"},
            {"ticker": "BUG",  "name": "Global X Cybersecurity ETF",           "weight": 0.08, "category": "etf"},
            {"ticker": "LMT",  "name": "Lockheed Martin",                      "weight": 0.04, "category": "individual"},
            {"ticker": "RTX",  "name": "RTX Corporation",                      "weight": 0.04, "category": "individual"},
            {"ticker": "CRWD", "name": "CrowdStrike",                          "weight": 0.03, "category": "individual"},
            {"ticker": "PANW", "name": "Palo Alto Networks",                   "weight": 0.03, "category": "individual"},
            {"ticker": "RKLB", "name": "Rocket Lab",                           "weight": 0.03, "category": "individual"},
            {"ticker": "KTOS", "name": "Kratos Defense",                       "weight": 0.03, "category": "individual"},
        ],
    },
    "F": {
        "name": "금융·핀테크",
        "theme": "금리 사이클, 전통 대형 은행, 디지털 결제 혁신, 암호화폐 금융화",
        "holdings": [
            {"ticker": "XLF",  "name": "Financial Select Sector SPDR ETF", "weight": 0.30, "category": "etf"},
            {"ticker": "VFH",  "name": "Vanguard Financials Index ETF",    "weight": 0.20, "category": "etf"},
            {"ticker": "KRE",  "name": "SPDR S&P Regional Banking ETF",    "weight": 0.15, "category": "etf"},
            {"ticker": "FINX", "name": "Global X FinTech ETF",             "weight": 0.15, "category": "etf"},
            {"ticker": "JPM",  "name": "JPMorgan Chase",                   "weight": 0.04, "category": "individual"},
            {"ticker": "V",    "name": "Visa",                             "weight": 0.04, "category": "individual"},
            {"ticker": "COIN", "name": "Coinbase",                         "weight": 0.03, "category": "individual"},
            {"ticker": "SQ",   "name": "Block (Square)",                   "weight": 0.03, "category": "individual"},
            {"ticker": "HOOD", "name": "Robinhood Markets",                "weight": 0.03, "category": "individual"},
            {"ticker": "SOFI", "name": "SoFi Technologies",                "weight": 0.03, "category": "individual"},
        ],
    },
    "G": {
        "name": "중국·신흥국",
        "theme": "미중 디커플링, 중국 AI 굴기, 신흥시장 성장, 지정학 리스크 vs 저평가 기회",
        "holdings": [
            {"ticker": "MCHI", "name": "iShares MSCI China ETF",             "weight": 0.25, "category": "etf"},
            {"ticker": "KWEB", "name": "KraneShares CSI China Internet ETF", "weight": 0.20, "category": "etf"},
            {"ticker": "FXI",  "name": "iShares China Large-Cap ETF",        "weight": 0.15, "category": "etf"},
            {"ticker": "EEM",  "name": "iShares MSCI Emerging Markets ETF",  "weight": 0.20, "category": "etf"},
            {"ticker": "BABA", "name": "Alibaba Group",                      "weight": 0.05, "category": "individual"},
            {"ticker": "BIDU", "name": "Baidu",                              "weight": 0.04, "category": "individual"},
            {"ticker": "PDD",  "name": "PDD Holdings (Temu)",                "weight": 0.04, "category": "individual"},
            {"ticker": "NIO",  "name": "NIO",                                "weight": 0.03, "category": "individual"},
            {"ticker": "XPEV", "name": "XPeng",                              "weight": 0.02, "category": "individual"},
            {"ticker": "SE",   "name": "Sea Limited",                        "weight": 0.02, "category": "individual"},
        ],
    },
    "H": {
        "name": "소비재·경기순환",
        "theme": "경기 사이클, 필수소비재(방어주) vs 경기소비재(공격주), 인플레이션 소비 패턴",
        "holdings": [
            {"ticker": "XLY",   "name": "Consumer Discretionary Select Sector SPDR ETF", "weight": 0.25, "category": "etf"},
            {"ticker": "XLP",   "name": "Consumer Staples Select Sector SPDR ETF",       "weight": 0.25, "category": "etf"},
            {"ticker": "VCR",   "name": "Vanguard Consumer Discretionary ETF",           "weight": 0.15, "category": "etf"},
            {"ticker": "IBUY",  "name": "Amplify Online Retail ETF",                     "weight": 0.15, "category": "etf"},
            {"ticker": "AMZN",  "name": "Amazon",                                        "weight": 0.05, "category": "individual"},
            {"ticker": "COST",  "name": "Costco Wholesale",                              "weight": 0.04, "category": "individual"},
            {"ticker": "LVMUY", "name": "LVMH (ADR)",                                    "weight": 0.03, "category": "individual"},
            {"ticker": "MELI",  "name": "MercadoLibre",                                  "weight": 0.03, "category": "individual"},
            {"ticker": "SHOP",  "name": "Shopify",                                       "weight": 0.03, "category": "individual"},
            {"ticker": "DPZ",   "name": "Domino's Pizza",                                "weight": 0.02, "category": "individual"},
        ],
    },
}

# Benchmark for beta calculation
BENCHMARK_TICKER = "SPY"

# Risk-free rate for Sharpe ratio (annualized)
RISK_FREE_RATE = 0.045

def get_all_tickers() -> list[str]:
    """Return deduplicated list of all tickers across all portfolios."""
    tickers = set()
    for portfolio in PORTFOLIOS.values():
        for h in portfolio["holdings"]:
            tickers.add(h["ticker"])
    tickers.add(BENCHMARK_TICKER)
    return sorted(tickers)


def get_portfolio_tickers(portfolio_id: str) -> list[str]:
    """Return tickers for a specific portfolio."""
    return [h["ticker"] for h in PORTFOLIOS[portfolio_id]["holdings"]]
