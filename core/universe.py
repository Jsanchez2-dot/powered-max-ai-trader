from pathlib import Path
import pandas as pd

AI_TICKERS = [
    "NVDA", "AMD", "AVGO", "MU", "TSM", "SMCI", "ANET", "VRT", "MRVL", "COHR",
    "AAOI", "CRDO", "NBIS", "PLTR", "ORCL", "SNOW", "DDOG", "MDB", "AI", "SOUN",
    "ARM", "ALAB", "MSFT", "GOOGL", "META", "AMZN", "TSLA", "AAPL", "NOW", "NET",
    "DELL", "HPE", "QCOM", "INTC", "AMAT", "LRCX", "KLAC", "ASML", "TER", "MPWR",
    "CLS", "WDC", "STX", "PSTG", "IONQ", "QBTS", "RGTI", "PATH", "U", "APP"
]

NASDAQ_TRADER_URL = "https://www.nasdaqtrader.com/dynamic/SymDir/nasdaqlisted.txt"
OTHER_LISTED_URL = "https://www.nasdaqtrader.com/dynamic/SymDir/otherlisted.txt"
CACHE_DIR = Path("data")
CACHE_DIR.mkdir(exist_ok=True)


def clean_symbol(symbol):
    if not isinstance(symbol, str):
        return None
    symbol = symbol.strip().upper()
    if not symbol or symbol in {"FILE CREATION TIME", "SYMBOL"}:
        return None
    if "$" in symbol or "." in symbol or " " in symbol:
        return None
    return symbol


def load_watchlist(path="watchlist_ai.txt"):
    file_path = Path(path)
    if not file_path.exists():
        return AI_TICKERS
    symbols = []
    for line in file_path.read_text().splitlines():
        symbol = clean_symbol(line)
        if symbol:
            symbols.append(symbol)
    return list(dict.fromkeys(symbols))


def fetch_public_market_symbols(limit=None):
    """Fetch a broad NASDAQ/NYSE/AMEX symbol list.

    This uses Nasdaq Trader symbol directories. If the download fails, it falls back
    to the AI ticker list so the app remains usable.
    """
    try:
        nasdaq = pd.read_csv(NASDAQ_TRADER_URL, sep="|")
        other = pd.read_csv(OTHER_LISTED_URL, sep="|")
        symbols = []
        if "Symbol" in nasdaq.columns:
            symbols.extend(nasdaq["Symbol"].dropna().tolist())
        if "ACT Symbol" in other.columns:
            symbols.extend(other["ACT Symbol"].dropna().tolist())
        clean = [s for s in (clean_symbol(x) for x in symbols) if s]
        clean = list(dict.fromkeys(clean))
        if limit:
            clean = clean[:limit]
        pd.Series(clean).to_csv(CACHE_DIR / "market_universe.csv", index=False, header=False)
        return clean
    except Exception:
        cached = CACHE_DIR / "market_universe.csv"
        if cached.exists():
            symbols = pd.read_csv(cached, header=None)[0].dropna().astype(str).tolist()
            return symbols[:limit] if limit else symbols
        return AI_TICKERS[:limit] if limit else AI_TICKERS


def get_universe(mode="AI Focus", max_symbols=100):
    if mode == "AI Focus":
        return AI_TICKERS[:max_symbols]
    if mode == "My Watchlist":
        return load_watchlist()[:max_symbols]
    if mode == "Full Market":
        return fetch_public_market_symbols(limit=max_symbols)
    return AI_TICKERS[:max_symbols]
