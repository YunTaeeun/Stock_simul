"""
calculate_metrics.py — Calculate portfolio values and risk metrics.

Reads:
  - /tmp/prices_cache.json  (from collect_prices.py)
  - /tmp/fx_cache.json      (from collect_prices.py)
  - Google Sheets `prices`  (full history for MDD/volatility/beta)
  - Google Sheets `holdings`

Writes to:
  - Google Sheets `portfolio_value`
  - Google Sheets `analysis`
  - /tmp/metrics_cache.json  (for generate_dashboard.py)
"""

import json
import os
import sys
from datetime import date

import numpy as np
import pandas as pd
import yfinance as yf

from config import PORTFOLIOS, BENCHMARK_TICKER, RISK_FREE_RATE, INITIAL_INVESTMENT
from update_sheets import get_spreadsheet, read_tab_as_records, append_rows_dedup

PRICES_CACHE = "/tmp/prices_cache.json"
FX_CACHE = "/tmp/fx_cache.json"
METRICS_CACHE = "/tmp/metrics_cache.json"


def load_caches() -> tuple[dict, float, str]:
    with open(PRICES_CACHE) as f:
        price_data = json.load(f)
    with open(FX_CACHE) as f:
        fx_data = json.load(f)
    return price_data["prices"], fx_data["usd_krw"], price_data["date"]


def build_prices_df(records: list[dict]) -> pd.DataFrame:
    """Convert Sheets price records to a date×ticker DataFrame of close prices."""
    if not records:
        return pd.DataFrame()
    df = pd.DataFrame(records)
    df["date"] = pd.to_datetime(df["date"])
    df["close"] = pd.to_numeric(df["close"], errors="coerce")
    pivot = df.pivot_table(index="date", columns="ticker", values="close", aggfunc="last")
    return pivot.sort_index()


def compute_portfolio_return(
    prices_df: pd.DataFrame,
    holdings: list[dict],
    today_prices: dict[str, float],
) -> tuple[float, pd.Series]:
    """
    Compute portfolio cumulative return and daily return series.

    Returns:
        cum_return_pct: cumulative return from start date as percentage
        daily_returns: pd.Series of daily portfolio returns
    """
    tickers = [h["ticker"] for h in holdings]
    weights = {h["ticker"]: h["weight"] for h in holdings}

    # Filter to relevant tickers present in history
    available = [t for t in tickers if t in prices_df.columns]
    if not available:
        return 0.0, pd.Series(dtype=float)

    sub = prices_df[available].dropna(how="all")
    if sub.empty:
        return 0.0, pd.Series(dtype=float)

    # Daily returns per ticker
    ticker_returns = sub.pct_change().fillna(0)

    # Portfolio daily return = weighted sum
    port_daily = sum(
        ticker_returns[t] * weights.get(t, 0)
        for t in available
    )

    # Cumulative return from first day
    start_price = sub.iloc[0]
    end_price = {t: today_prices.get(t, sub[t].iloc[-1]) for t in available}
    cum_return = sum(
        ((end_price[t] / start_price[t]) - 1) * weights.get(t, 0)
        for t in available
        if start_price[t] > 0
    )

    return round(cum_return * 100, 4), port_daily


def compute_mdd(daily_returns: pd.Series) -> float:
    """Maximum Drawdown as a negative percentage."""
    if daily_returns.empty:
        return 0.0
    cum = (1 + daily_returns).cumprod()
    rolling_max = cum.cummax()
    drawdown = (cum - rolling_max) / rolling_max
    return round(float(drawdown.min()) * 100, 4)


def compute_volatility(daily_returns: pd.Series) -> float:
    """Annualized volatility (std of daily returns × √252) in %."""
    if len(daily_returns) < 2:
        return 0.0
    return round(float(daily_returns.std()) * (252 ** 0.5) * 100, 4)


def compute_sharpe(daily_returns: pd.Series) -> float:
    """Annualized Sharpe ratio (risk-free rate = RISK_FREE_RATE)."""
    if len(daily_returns) < 2:
        return 0.0
    daily_rf = RISK_FREE_RATE / 252
    excess = daily_returns - daily_rf
    if excess.std() == 0:
        return 0.0
    return round(float(excess.mean() / excess.std()) * (252 ** 0.5), 4)


def compute_beta(
    port_daily: pd.Series,
    benchmark_daily: pd.Series,
) -> float:
    """Beta of portfolio vs benchmark."""
    if len(port_daily) < 5 or len(benchmark_daily) < 5:
        return 1.0
    aligned = pd.concat([port_daily, benchmark_daily], axis=1).dropna()
    if aligned.shape[0] < 5:
        return 1.0
    p = aligned.iloc[:, 0]
    b = aligned.iloc[:, 1]
    var_b = float(b.var())
    if var_b == 0:
        return 1.0
    return round(float(np.cov(p, b)[0][1] / var_b), 4)


def fetch_benchmark_returns(prices_df: pd.DataFrame) -> pd.Series:
    """Get SPY daily returns from history or yfinance fallback."""
    if BENCHMARK_TICKER in prices_df.columns:
        return prices_df[BENCHMARK_TICKER].pct_change().fillna(0)
    # Fallback: fetch from yfinance
    spy = yf.download(BENCHMARK_TICKER, period="1y", auto_adjust=True, progress=False)
    return spy["Close"].squeeze().pct_change().fillna(0)


def main() -> None:
    today_prices, usd_krw, today_str = load_caches()
    today = date.today().isoformat()

    spreadsheet = get_spreadsheet()

    # Load full price history from Sheets
    price_records = read_tab_as_records(spreadsheet, "prices")
    prices_df = build_prices_df(price_records)
    benchmark_returns = fetch_benchmark_returns(prices_df)

    portfolio_value_rows = []
    analysis_rows = []
    metrics_cache = {"date": today, "usd_krw": usd_krw, "portfolios": {}}

    for pid, portfolio in PORTFOLIOS.items():
        holdings = portfolio["holdings"]
        tickers = [h["ticker"] for h in holdings]
        weights = {h["ticker"]: h["weight"] for h in holdings}

        cum_return_pct, daily_returns = compute_portfolio_return(
            prices_df, holdings, today_prices
        )

        # Portfolio value in KRW
        value_krw = round(INITIAL_INVESTMENT * (1 + cum_return_pct / 100))
        pnl_krw = value_krw - INITIAL_INVESTMENT

        mdd = compute_mdd(daily_returns)
        volatility = compute_volatility(daily_returns)
        sharpe = compute_sharpe(daily_returns)
        beta = compute_beta(daily_returns, benchmark_returns)

        portfolio_value_rows.append([
            today, pid, value_krw, pnl_krw, round(cum_return_pct, 4)
        ])
        analysis_rows.append([
            today, pid, round(cum_return_pct, 4), mdd, volatility, sharpe, beta
        ])

        # Per-holding returns for dashboard
        holding_details = []
        for h in holdings:
            ticker = h["ticker"]
            weight = h["weight"]
            if ticker in prices_df.columns:
                series = prices_df[ticker].dropna()
                if len(series) >= 2:
                    start = float(series.iloc[0])
                    end = today_prices.get(ticker, float(series.iloc[-1]))
                    ret_pct = round((end / start - 1) * 100, 4) if start > 0 else 0.0
                else:
                    ret_pct = 0.0
            else:
                ret_pct = 0.0
            pnl = round(INITIAL_INVESTMENT * weight * ret_pct / 100)
            holding_details.append({
                "ticker": ticker,
                "name": h["name"],
                "weight": weight,
                "category": h["category"],
                "return_pct": ret_pct,
                "pnl_krw": pnl,
            })

        # History for chart
        history = []
        if not daily_returns.empty:
            cum_series = (1 + daily_returns).cumprod() * INITIAL_INVESTMENT
            for dt, val in cum_series.items():
                history.append({"date": str(dt.date()), "value": round(float(val))})

        metrics_cache["portfolios"][pid] = {
            "name": portfolio["name"],
            "theme": portfolio["theme"],
            "value_krw": value_krw,
            "pnl_krw": pnl_krw,
            "return_pct": round(cum_return_pct, 2),
            "metrics": {
                "cum_return": round(cum_return_pct, 2),
                "mdd": mdd,
                "volatility": volatility,
                "sharpe": sharpe,
                "beta": beta,
            },
            "history": history,
            "holdings": holding_details,
        }

        print(
            f"Portfolio {pid}: value={value_krw:,} KRW  "
            f"return={cum_return_pct:.2f}%  MDD={mdd:.2f}%  "
            f"vol={volatility:.2f}%  sharpe={sharpe:.2f}  beta={beta:.2f}"
        )

    # Write to Sheets
    append_rows_dedup(spreadsheet, "portfolio_value", portfolio_value_rows, key_cols=[0, 1])
    append_rows_dedup(spreadsheet, "analysis", analysis_rows, key_cols=[0, 1])
    print("Updated portfolio_value and analysis tabs.")

    # Save metrics cache
    with open(METRICS_CACHE, "w") as f:
        json.dump(metrics_cache, f, ensure_ascii=False, indent=2)
    print(f"Saved metrics cache to {METRICS_CACHE}")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
