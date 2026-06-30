import pandas as pd
import yfinance as yf
from datetime import datetime

from core.indicators import (
    add_base_indicators,
    detect_market_structure,
    detect_fair_value_gaps,
    detect_order_blocks,
    fib_zone,
)
from core.risk import risk_reward

MIN_AVG_VOLUME = 5_000_000
MIN_PRICE = 10
LOOKBACK = "1y"


def load_watchlist(path="watchlist_ai.txt"):
    with open(path, "r") as f:
        return [x.strip().upper() for x in f.readlines() if x.strip()]


def get_data(ticker):
    df = yf.download(ticker, period=LOOKBACK, interval="1d", auto_adjust=True, progress=False)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [c[0] for c in df.columns]
    return df


def _overlaps(price_low, price_high, zone_low, zone_high):
    return max(price_low, zone_low) <= min(price_high, zone_high)


def _nearest_zone(zones, zone_type=None):
    filtered = [z for z in zones if zone_type is None or z["type"] == zone_type]
    return filtered[-1] if filtered else None


def score_stock(ticker):
    df = get_data(ticker)
    if df.empty or len(df) < 220:
        return None, df

    df = add_base_indicators(df)
    last = df.iloc[-1]
    last_close = float(last["Close"])
    avg_vol_20 = float(last["AVG_VOL20"])
    rvol = float(last["RVOL"]) if avg_vol_20 else 0

    if last_close < MIN_PRICE or avg_vol_20 < MIN_AVG_VOLUME:
        return None, df

    structure = detect_market_structure(df, lookback=80)
    fvgs = detect_fair_value_gaps(df, lookback=120)
    order_blocks = detect_order_blocks(df, lookback=120)

    swing_high = float(structure["last_swing_high"])
    swing_low = float(structure["last_swing_low"])
    fib_618, fib_50 = fib_zone(swing_low, max(swing_high, last_close))
    in_fib_zone = fib_618 <= last_close <= fib_50

    bullish_ob = _nearest_zone(order_blocks, "bullish")
    bearish_ob = _nearest_zone(order_blocks, "bearish")
    bullish_fvg = _nearest_zone(fvgs, "bullish")
    bearish_fvg = _nearest_zone(fvgs, "bearish")

    has_ob_confluence = bool(bullish_ob and _overlaps(fib_618, fib_50, bullish_ob["low"], bullish_ob["high"]))
    has_fvg_confluence = bool(bullish_fvg and _overlaps(fib_618, fib_50, bullish_fvg["low"], bullish_fvg["high"]))

    above_200 = last_close > float(last["EMA200"])
    above_50 = last_close > float(last["EMA50"])
    vfi_now = float(last["VFI"]) if pd.notna(last["VFI"]) else 0
    vfi_prev = float(df["VFI"].iloc[-5]) if pd.notna(df["VFI"].iloc[-5]) else 0
    vfi_rising = vfi_now > vfi_prev

    entry_low = fib_618
    entry_high = fib_50
    entry_mid = (entry_low + entry_high) / 2
    stop = swing_low * 0.985
    target_1 = swing_high
    target_2 = entry_mid + (entry_mid - stop) * 2
    target_3 = entry_mid + (entry_mid - stop) * 3

    risk_per_share = max(entry_mid - stop, 0)
    rr_target_1 = risk_reward(entry_mid, stop, target_1)
    rr_target_2 = risk_reward(entry_mid, stop, target_2)
    rr_target_3 = risk_reward(entry_mid, stop, target_3)
    max_rr = max(rr_target_1, rr_target_2, rr_target_3)

    score = 0
    score += 15 if structure["bullish_bos"] else 0
    score += 10 if structure["choch_bullish"] else 0
    score += 10 if structure["mss_bullish"] else 0
    score += 10 if structure["trend_structure"] == "bullish" else 0
    score += 10 if in_fib_zone else 0
    score += 10 if has_ob_confluence else 0
    score += 10 if has_fvg_confluence else 0
    score += 10 if vfi_rising else 0
    score += 5 if vfi_now > 0 else 0
    score += 5 if rvol >= 1.5 else 0
    score += 5 if above_50 else 0
    score += 5 if above_200 else 0
    score += 5 if max_rr >= 3 else 0
    score = min(score, 100)

    if score >= 85 and max_rr >= 3:
        action = "BUY SETUP"
    elif score >= 70:
        action = "WATCH"
    else:
        action = "WAIT"

    result = {
        "ticker": ticker,
        "date": datetime.now().strftime("%Y-%m-%d"),
        "last_close": round(last_close, 2),
        "avg_volume_20": int(avg_vol_20),
        "relative_volume": round(rvol, 2),
        "score": score,
        "action": action,
        "trend_structure": structure["trend_structure"],
        "bullish_bos": structure["bullish_bos"],
        "bearish_bos": structure["bearish_bos"],
        "choch_bullish": structure["choch_bullish"],
        "choch_bearish": structure["choch_bearish"],
        "mss_bullish": structure["mss_bullish"],
        "mss_bearish": structure["mss_bearish"],
        "above_50ema": above_50,
        "above_200ema": above_200,
        "vfi": round(vfi_now, 2),
        "vfi_rising": vfi_rising,
        "fib_50": round(fib_50, 2),
        "fib_618": round(fib_618, 2),
        "in_fib_zone": in_fib_zone,
        "bullish_order_block": bullish_ob,
        "bearish_order_block": bearish_ob,
        "bullish_fvg": bullish_fvg,
        "bearish_fvg": bearish_fvg,
        "order_block_confluence": has_ob_confluence,
        "fvg_confluence": has_fvg_confluence,
        "entry_low": round(entry_low, 2),
        "entry_high": round(entry_high, 2),
        "entry_mid": round(entry_mid, 2),
        "entry_zone": f"{round(entry_low, 2)} - {round(entry_high, 2)}",
        "stop_loss": round(stop, 2),
        "risk_per_share": round(risk_per_share, 2),
        "target_1": round(target_1, 2),
        "target_2": round(target_2, 2),
        "target_3": round(target_3, 2),
        "rr_target_1": round(rr_target_1, 2),
        "rr_target_2": round(rr_target_2, 2),
        "rr_target_3": round(rr_target_3, 2),
        "max_rr": round(max_rr, 2),
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
