import time
import yfinance as yf

POSITIVE_TERMS = [
    "upgrade", "beats", "beat", "raises", "raised", "strong demand", "record", "contract",
    "partnership", "approval", "launch", "guidance raised", "buy rating", "price target raised",
    "earnings beat", "revenue beat", "ai demand", "new customer", "expansion"
]

NEGATIVE_TERMS = [
    "downgrade", "misses", "miss", "cuts", "cut", "lawsuit", "investigation", "probe",
    "guidance cut", "price target cut", "weak demand", "layoffs", "recall", "sec", "fraud",
    "short report", "bankruptcy", "delisting", "offering", "dilution"
]

MOMENTUM_TERMS = [
    "surges", "jumps", "rallies", "breakout", "momentum", "volume", "record high",
    "unusual volume", "squeeze", "outperform", "strong earnings"
]


def get_yahoo_news(ticker, max_items=8):
    try:
        items = yf.Ticker(ticker).news or []
    except Exception:
        return []

    headlines = []
    for item in items[:max_items]:
        title = item.get("title") or item.get("content", {}).get("title") or ""
        publisher = item.get("publisher") or item.get("content", {}).get("provider", {}).get("displayName", "")
        link = item.get("link") or item.get("content", {}).get("canonicalUrl", {}).get("url", "")
        published = item.get("providerPublishTime") or item.get("content", {}).get("pubDate")
        if isinstance(published, (int, float)):
            published = time.strftime("%Y-%m-%d", time.localtime(published))
        headlines.append({
            "title": title,
            "publisher": publisher,
            "link": link,
            "published": published,
        })
    return headlines


def catalyst_score_from_headlines(headlines):
    text = " ".join([h.get("title", "") for h in headlines]).lower()
    if not text.strip():
        return {
            "news_score": 50,
            "news_bias": "Neutral",
            "positive_hits": [],
            "negative_hits": [],
            "momentum_hits": [],
        }

    positive_hits = [term for term in POSITIVE_TERMS if term in text]
    negative_hits = [term for term in NEGATIVE_TERMS if term in text]
    momentum_hits = [term for term in MOMENTUM_TERMS if term in text]

    score = 50
    score += min(len(positive_hits) * 8, 30)
    score += min(len(momentum_hits) * 5, 20)
    score -= min(len(negative_hits) * 10, 40)
    score = max(0, min(100, score))

    if score >= 70:
        bias = "Positive catalyst"
    elif score <= 35:
        bias = "Negative catalyst"
    else:
        bias = "Neutral"

    return {
        "news_score": score,
        "news_bias": bias,
        "positive_hits": positive_hits,
        "negative_hits": negative_hits,
        "momentum_hits": momentum_hits,
    }


def get_catalyst_snapshot(ticker):
    headlines = get_yahoo_news(ticker)
    score = catalyst_score_from_headlines(headlines)
    score["headlines"] = headlines
    return score
