import pandas as pd

from scanner_engine import score_stock
from core.universe import get_universe
from core.catalysts import get_catalyst_snapshot
from core.fundamentals import get_financial_snapshot


def enrich_result(result, include_news=True, include_financials=True):
    if not result:
        return result

    ticker = result["ticker"]
    score = int(result.get("score", 0))

    if include_news:
        catalyst = get_catalyst_snapshot(ticker)
        result["news_score"] = catalyst.get("news_score", 50)
        result["news_bias"] = catalyst.get("news_bias", "Neutral")
        result["positive_news_hits"] = ", ".join(catalyst.get("positive_hits", []))
        result["negative_news_hits"] = ", ".join(catalyst.get("negative_hits", []))
        result["momentum_news_hits"] = ", ".join(catalyst.get("momentum_hits", []))
        result["headlines"] = catalyst.get("headlines", [])

        if result["news_score"] >= 70:
            score += 10
        elif result["news_score"] <= 35:
            score -= 10

    if include_financials:
        financials = get_financial_snapshot(ticker)
        result.update(financials)
        financial_score = int(financials.get("financial_score", 50))
        if financial_score >= 75:
            score += 10
        elif financial_score <= 35:
            score -= 5

    result["score"] = max(0, min(100, score))

    if result["score"] >= 85 and float(result.get("max_rr", 0)) >= 3:
        result["action"] = "BUY SETUP"
    elif result["score"] >= 70:
        result["action"] = "WATCH"
    else:
        result["action"] = "WAIT"

    return result


def enhanced_scan_market(universe_mode="AI Focus", max_symbols=100, include_news=True, include_financials=True, progress_callback=None):
    rows = []
    chart_data = {}
    symbols = get_universe(mode=universe_mode, max_symbols=max_symbols)
    total = len(symbols)

    for idx, ticker in enumerate(symbols, start=1):
        if progress_callback:
            progress_callback(idx, total, ticker)
        try:
            result, df = score_stock(ticker)
            if result:
                result = enrich_result(result, include_news=include_news, include_financials=include_financials)
                rows.append(result)
                chart_data[ticker] = df
        except Exception as exc:
            print(f"{ticker}: {exc}")
            continue

    out = pd.DataFrame(rows)
    if not out.empty:
        out = out.sort_values(["score", "relative_volume"], ascending=False)
        out.to_csv("scanner_results.csv", index=False)
    return out, chart_data
