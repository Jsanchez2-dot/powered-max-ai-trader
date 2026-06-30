import os
import requests


def fetch_news_headlines(ticker):
    """Fetch basic news headlines.

    Optional: set NEWS_API_KEY to use NewsAPI-compatible endpoints later.
    For now, this returns a clean placeholder so the dashboard is ready for a real data provider.
    """
    api_key = os.getenv("NEWS_API_KEY")
    if not api_key:
        return ["News API key not configured yet."]

    url = "https://newsapi.org/v2/everything"
    params = {
        "q": ticker,
        "apiKey": api_key,
        "language": "en",
        "sortBy": "publishedAt",
        "pageSize": 5,
    }
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        return [article.get("title", "") for article in data.get("articles", []) if article.get("title")]
    except Exception as exc:
        return [f"News fetch error: {exc}"]


def news_risk_score(headlines):
    negative_words = ["lawsuit", "downgrade", "miss", "fraud", "investigation", "guidance cut"]
    positive_words = ["upgrade", "beat", "contract", "ai demand", "partnership", "raise"]
    text = " ".join(headlines).lower()
    score = 50
    score += sum(10 for word in positive_words if word in text)
    score -= sum(10 for word in negative_words if word in text)
    return max(0, min(100, score))
