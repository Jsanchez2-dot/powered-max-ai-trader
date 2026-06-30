from pathlib import Path
import pandas as pd

JOURNAL_PATH = Path("trade_journal.csv")
COLUMNS = [
    "date", "ticker", "setup", "entry", "stop", "target_1", "target_2", "target_3",
    "shares", "exit_price", "pnl", "result", "notes"
]


def load_journal():
    if JOURNAL_PATH.exists():
        return pd.read_csv(JOURNAL_PATH)
    return pd.DataFrame(columns=COLUMNS)


def add_trade(trade):
    df = load_journal()
    row = {col: trade.get(col, "") for col in COLUMNS}
    df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
    df.to_csv(JOURNAL_PATH, index=False)
    return df


def journal_stats(df):
    if df.empty or "pnl" not in df:
        return {"trades": 0, "win_rate": 0, "total_pnl": 0}
    pnl = pd.to_numeric(df["pnl"], errors="coerce").fillna(0)
    wins = (pnl > 0).sum()
    trades = len(df)
    return {
        "trades": trades,
        "win_rate": round((wins / trades) * 100, 2) if trades else 0,
        "total_pnl": round(float(pnl.sum()), 2),
        "average_pnl": round(float(pnl.mean()), 2) if trades else 0,
    }
