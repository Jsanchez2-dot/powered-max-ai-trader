import numpy as np
import pandas as pd


def ema(series, span):
    return series.ewm(span=span, adjust=False).mean()


def atr(df, length=14):
    high_low = df["High"] - df["Low"]
    high_close = (df["High"] - df["Close"].shift()).abs()
    low_close = (df["Low"] - df["Close"].shift()).abs()
    true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    return true_range.rolling(length).mean()


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


def add_base_indicators(df):
    df = df.copy()
    df["EMA20"] = ema(df["Close"], 20)
    df["EMA50"] = ema(df["Close"], 50)
    df["EMA200"] = ema(df["Close"], 200)
    df["ATR14"] = atr(df, 14)
    df["AVG_VOL20"] = df["Volume"].rolling(20).mean()
    df["RVOL"] = df["Volume"] / df["AVG_VOL20"]
    df["VFI"] = calculate_vfi(df["Close"], df["High"], df["Low"], df["Volume"])
    return df


def find_pivots(df, left=3, right=3):
    df = df.copy()
    df["pivot_high"] = False
    df["pivot_low"] = False
    highs = df["High"].values
    lows = df["Low"].values
    for i in range(left, len(df) - right):
        df.iloc[i, df.columns.get_loc("pivot_high")] = highs[i] == max(highs[i-left:i+right+1])
        df.iloc[i, df.columns.get_loc("pivot_low")] = lows[i] == min(lows[i-left:i+right+1])
    return df


def detect_market_structure(df, lookback=50):
    recent = find_pivots(df.tail(lookback).copy())
    highs = recent[recent["pivot_high"]]
    lows = recent[recent["pivot_low"]]
    last_close = float(df["Close"].iloc[-1])

    last_swing_high = float(highs["High"].iloc[-1]) if not highs.empty else float(df["High"].tail(20).max())
    last_swing_low = float(lows["Low"].iloc[-1]) if not lows.empty else float(df["Low"].tail(20).min())

    bullish_bos = last_close > last_swing_high
    bearish_bos = last_close < last_swing_low

    if len(highs) >= 2 and len(lows) >= 2:
        higher_high = highs["High"].iloc[-1] > highs["High"].iloc[-2]
        higher_low = lows["Low"].iloc[-1] > lows["Low"].iloc[-2]
        lower_high = highs["High"].iloc[-1] < highs["High"].iloc[-2]
        lower_low = lows["Low"].iloc[-1] < lows["Low"].iloc[-2]
    else:
        higher_high = higher_low = lower_high = lower_low = False

    trend = "bullish" if higher_high and higher_low else "bearish" if lower_high and lower_low else "neutral"
    choch_bullish = bullish_bos and trend == "bearish"
    choch_bearish = bearish_bos and trend == "bullish"
    mss_bullish = bullish_bos or choch_bullish
    mss_bearish = bearish_bos or choch_bearish

    return {
        "last_swing_high": round(last_swing_high, 2),
        "last_swing_low": round(last_swing_low, 2),
        "trend_structure": trend,
        "bullish_bos": bullish_bos,
        "bearish_bos": bearish_bos,
        "choch_bullish": choch_bullish,
        "choch_bearish": choch_bearish,
        "mss_bullish": mss_bullish,
        "mss_bearish": mss_bearish,
    }


def detect_fair_value_gaps(df, lookback=80):
    gaps = []
    data = df.tail(lookback)
    for i in range(2, len(data)):
        prev2 = data.iloc[i-2]
        curr = data.iloc[i]
        date = data.index[i]
        if curr["Low"] > prev2["High"]:
            gaps.append({"type": "bullish", "low": float(prev2["High"]), "high": float(curr["Low"]), "date": str(date.date())})
        if curr["High"] < prev2["Low"]:
            gaps.append({"type": "bearish", "low": float(curr["High"]), "high": float(prev2["Low"]), "date": str(date.date())})
    return gaps[-5:]


def detect_order_blocks(df, lookback=80):
    data = df.tail(lookback).copy()
    atr_val = float(data["ATR14"].dropna().iloc[-1]) if "ATR14" in data and not data["ATR14"].dropna().empty else 0
    blocks = []
    for i in range(1, len(data)-1):
        row = data.iloc[i]
        nxt = data.iloc[i+1]
        body = abs(float(row["Close"] - row["Open"]))
        next_range = abs(float(nxt["Close"] - row["Close"]))
        impulse = next_range > atr_val * 0.75 if atr_val else next_range > body
        if row["Close"] < row["Open"] and nxt["Close"] > nxt["Open"] and impulse:
            blocks.append({"type": "bullish", "low": float(row["Low"]), "high": float(row["Open"]), "date": str(data.index[i].date())})
        if row["Close"] > row["Open"] and nxt["Close"] < nxt["Open"] and impulse:
            blocks.append({"type": "bearish", "low": float(row["Open"]), "high": float(row["High"]), "date": str(data.index[i].date())})
    return blocks[-5:]


def fib_zone(low, high):
    fib_50 = high - (high - low) * 0.50
    fib_618 = high - (high - low) * 0.618
    return round(fib_618, 2), round(fib_50, 2)
