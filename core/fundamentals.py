import math
import yfinance as yf


def safe_number(value, default=None):
    try:
        if value is None:
            return default
        if isinstance(value, float) and math.isnan(value):
            return default
        return float(value)
    except Exception:
        return default


def compact_money(value):
    value = safe_number(value)
    if value is None:
        return "N/A"
    abs_value = abs(value)
    if abs_value >= 1_000_000_000_000:
        return f"${value / 1_000_000_000_000:.2f}T"
    if abs_value >= 1_000_000_000:
        return f"${value / 1_000_000_000:.2f}B"
    if abs_value >= 1_000_000:
        return f"${value / 1_000_000:.2f}M"
    return f"${value:,.0f}"


def percent(value):
    value = safe_number(value)
    if value is None:
        return "N/A"
    return f"{value * 100:.1f}%"


def get_financial_snapshot(ticker):
    stock = yf.Ticker(ticker)
    info = stock.info or {}

    market_cap = safe_number(info.get("marketCap"))
    revenue_growth = safe_number(info.get("revenueGrowth"))
    earnings_growth = safe_number(info.get("earningsGrowth"))
    profit_margin = safe_number(info.get("profitMargins"))
    gross_margin = safe_number(info.get("grossMargins"))
    operating_margin = safe_number(info.get("operatingMargins"))
    forward_pe = safe_number(info.get("forwardPE"))
    trailing_pe = safe_number(info.get("trailingPE"))
    debt_to_equity = safe_number(info.get("debtToEquity"))
    current_ratio = safe_number(info.get("currentRatio"))
    beta = safe_number(info.get("beta"))

    financial_score = 0
    financial_score += 15 if revenue_growth is not None and revenue_growth > 0.10 else 0
    financial_score += 15 if earnings_growth is not None and earnings_growth > 0.10 else 0
    financial_score += 15 if profit_margin is not None and profit_margin > 0.10 else 0
    financial_score += 10 if gross_margin is not None and gross_margin > 0.35 else 0
    financial_score += 10 if operating_margin is not None and operating_margin > 0.10 else 0
    financial_score += 10 if current_ratio is not None and current_ratio >= 1 else 0
    financial_score += 10 if debt_to_equity is None or debt_to_equity < 150 else 0
    financial_score += 10 if forward_pe is not None and 0 < forward_pe < 60 else 0
    financial_score += 5 if market_cap is not None and market_cap > 2_000_000_000 else 0

    return {
        "company_name": info.get("shortName", ticker),
        "sector": info.get("sector", "N/A"),
        "industry": info.get("industry", "N/A"),
        "market_cap": market_cap,
        "market_cap_display": compact_money(market_cap),
        "revenue_growth": revenue_growth,
        "revenue_growth_display": percent(revenue_growth),
        "earnings_growth": earnings_growth,
        "earnings_growth_display": percent(earnings_growth),
        "profit_margin": profit_margin,
        "profit_margin_display": percent(profit_margin),
        "gross_margin": gross_margin,
        "gross_margin_display": percent(gross_margin),
        "operating_margin": operating_margin,
        "operating_margin_display": percent(operating_margin),
        "forward_pe": forward_pe,
        "trailing_pe": trailing_pe,
        "debt_to_equity": debt_to_equity,
        "current_ratio": current_ratio,
        "beta": beta,
        "financial_score": min(financial_score, 100),
    }
