import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime

MIN_AVG_VOLUME = 5_000_000
MIN_PRICE = 10
LOOKBACK = "1y"


def load_watchlist(path="watchlist_ai.txt"):
    with open(path, "r") as f:
        return [x.strip().upper() for x in f.readlines() if x.strip()]


def ema(series, span):
    return series.ewm(span=span, adjust=False).mean()


def calculate_vfi(close, high, low, volume, length=130, coef=0.2, vcoef=2.5):
    typical = (high + low + close) / 3
    inter = np.log(typical).diff()
    vinter = inter.rolling(30).std()
    cutoff = coef * vinter * close
    vave = volume.rolling(length).mean().shift(1)
    vmax = vave * vcoef
    vc = np.minimum(volume, vmax)
    mf = typical.diff()
    vcp = np.where(mf > cutoff, vc, np.where(mf < -cutoff, -vc, 0))
    return pd.Series(vcp, index=close.index).rolling(length).sum() / vave


def get_data(ticker):
    df = yf.download(ticker, period=LOOKBACK, interval="1d", auto_adjust=True, progress=False)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [c[0] for c in df.columns]
    return df


def score_stock(ticker):
    df = get_data(ticker)
    if df.empty or len(df) < 160:
        return None, df

    close, high, low, volume = df["Close"], df["High"], df["Low"], df["Volume"]
    last_close = float(close.iloc[-1])
    avg_vol_20 = float(volume.rolling(20).mean().iloc[-1])
    rvol = float(volume.iloc[-1] / avg_vol_20) if avg_vol_20 else 0

    if last_close < MIN_PRICE or avg_vol_20 < MIN_AVG_VOLUME:
        return None, df

    df["EMA50"] = ema(close, 50)
    df["EMA200"] = ema(close, 200)
    df["VFI"] = calculate_vfi(close, high, low, volume)

    swing_high = float(df["High"].iloc[-21:-1].max())
    swing_low = float(df["Low"].iloc[-21:-1].min())

    bullish_bos = last_close > swing_high
    above_200 = last_close > float(df["EMA200"].iloc[-1])
    above_50 = last_close > float(df["EMA50"].iloc[-1])

    vfi_now = float(df["VFI"].iloc[-1]) if not pd.isna(df["VFI"].iloc[-1]) else 0
    vfi_prev = float(df["VFI"].iloc[-5]) if not pd.isna(df["VFI"].iloc[-5]) else 0
    vfi_rising = vfi_now > vfi_prev

    move_high = max(swing_high, last_close)
    move_low = swing_low
    fib_50 = move_high - (move_high - move_low) * 0.50
    fib_618 = move_high - (move_high - move_low) * 0.618
    in_fib_zone = fib_618 <= last_close <= fib_50

    score = 0
    score += 20 if bullish_bos else 0
    score += 15 if above_200 else 0
    score += 10 if above_50 else 0
    score += 15 if vfi_rising else 0
    score += 10 if vfi_now > 0 else 0
    score += 10 if rvol >= 1.5 else 0
    score += 10 if in_fib_zone else 0
    score += 10 if last_close > swing_low else 0

    if score >= 85:
        action = "BUY SETUP"
    elif score >= 70:
        action = "WATCH"
    else:
        action = "WAIT"

    stop = swing_low * 0.985
    target_1 = swing_high
    target_2 = last_close + (last_close - stop) * 2
    target_3 = last_close + (last_close - stop) * 3

    result = {
        "ticker": ticker,
        "date": datetime.now().strftime("%Y-%m-%d"),
        "last_close": round(last_close, 2),
        "avg_volume_20": int(avg_vol_20),
        "relative_volume": round(rvol, 2),
        "score": score,
        "action": action,
        "bullish_bos": bullish_bos,
        "above_50ema": above_50,
        "above_200ema": above_200,
        "vfi": round(vfi_now, 2),
        "vfi_rising": vfi_rising,
        "fib_50": round(fib_50, 2),
        "fib_618": round(fib_618, 2),
        "in_fib_zone": in_fib_zone,
        "entry_zone": f"{round(fib_618, 2)} - {round(fib_50, 2)}",
        "stop_loss": round(stop, 2),
        "target_1": round(target_1, 2),
        "target_2": round(target_2, 2),
        "target_3": round(target_3, 2),
    }
    return result, df


def scan_market():
    rows = []
    chart_data = {}
    for ticker in load_watchlist():
        try:
            result, df = score_stock(ticker)
            if result:
                rows.append(result)
                chart_data[ticker] = df
        except Exception as exc:
            print(f"{ticker}: {exc}")
            continue

    out = pd.DataFrame(rows)
    if not out.empty:
        out = out.sort_values("score", ascending=False)
        out.to_csv("scanner_results.csv", index=False)
    return out, chart_data
