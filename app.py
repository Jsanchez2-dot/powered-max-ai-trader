import streamlit as st
import plotly.graph_objects as go
from scanner_engine import scan_market, score_stock

st.set_page_config(page_title="Powered Max AI Trader", layout="wide")

st.title("Powered Max AI Trader v3")
st.caption("AI / semiconductor / high-volume stock scanner with risk-to-reward and position sizing")

if "results" not in st.session_state:
    st.session_state.results = None
    st.session_state.chart_data = {}

with st.sidebar:
    st.header("Risk Settings")
    account_size = st.number_input("Account size ($)", min_value=100.0, value=10000.0, step=500.0)
    risk_percent = st.number_input("Risk per trade (%)", min_value=0.1, max_value=10.0, value=1.0, step=0.1)
    dollar_risk = account_size * (risk_percent / 100)
    st.metric("Max dollar risk", f"${dollar_risk:,.2f}")
    st.caption("Position size = max dollar risk / risk per share")

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Strategy", "AI + High Volume")
with col2:
    st.metric("Min Avg Volume", "5M")
with col3:
    st.metric("Minimum R:R", "3:1")

if st.button("Run Daily Scan", type="primary"):
    with st.spinner("Scanning AI stocks..."):
        st.session_state.results, st.session_state.chart_data = scan_market()

df = st.session_state.results

if df is None:
    st.info("Click Run Daily Scan to start.")
elif df.empty:
    st.warning("No qualifying stocks found today.")
else:
    buy_count = (df["action"] == "BUY SETUP").sum()
    watch_count = (df["action"] == "WATCH").sum()

    a, b, c = st.columns(3)
    a.metric("Buy Setups", int(buy_count))
    b.metric("Watchlist", int(watch_count))
    c.metric("Stocks Scanned", len(df))

    st.subheader("Top Trade Setups")
    st.dataframe(
        df[[
            "ticker", "score", "action", "last_close", "relative_volume",
            "entry_zone", "stop_loss", "risk_per_share", "max_rr",
            "target_1", "rr_target_1", "target_2", "rr_target_2", "target_3", "rr_target_3",
            "bullish_bos", "above_50ema", "above_200ema", "vfi_rising"
        ]],
        use_container_width=True
    )

    selected = st.selectbox("Select ticker for chart", df["ticker"].tolist())
    row = df[df["ticker"] == selected].iloc[0]

    risk_per_share = float(row["risk_per_share"])
    shares = int(dollar_risk // risk_per_share) if risk_per_share > 0 else 0
    position_cost = shares * float(row["entry_mid"])
    max_loss = shares * risk_per_share
    profit_t1 = shares * (float(row["target_1"]) - float(row["entry_mid"]))
    profit_t2 = shares * (float(row["target_2"]) - float(row["entry_mid"]))
    profit_t3 = shares * (float(row["target_3"]) - float(row["entry_mid"]))

    st.subheader(f"{selected} Trade Card")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Score", int(row["score"]))
    c2.metric("Action", row["action"])
    c3.metric("Entry Zone", row["entry_zone"])
    c4.metric("Stop Loss", f"${row['stop_loss']}")

    c5, c6, c7, c8 = st.columns(4)
    c5.metric("Risk / Share", f"${risk_per_share:.2f}")
    c6.metric("Max R:R", f"{row['max_rr']}:1")
    c7.metric("Shares", shares)
    c8.metric("Position Cost", f"${position_cost:,.2f}")

    st.subheader("Risk-to-Reward Calculator")
    r1, r2, r3, r4 = st.columns(4)
    r1.metric("Max Loss", f"${max_loss:,.2f}")
    r2.metric(f"Target 1 ${row['target_1']}", f"${profit_t1:,.2f}", f"R:R {row['rr_target_1']}:1")
    r3.metric(f"Target 2 ${row['target_2']}", f"${profit_t2:,.2f}", f"R:R {row['rr_target_2']}:1")
    r4.metric(f"Target 3 ${row['target_3']}", f"${profit_t3:,.2f}", f"R:R {row['rr_target_3']}:1")

    st.subheader("Trade Checklist")
    checklist = {
        "Bullish BOS": bool(row["bullish_bos"]),
        "Above 50 EMA": bool(row["above_50ema"]),
        "Above 200 EMA": bool(row["above_200ema"]),
        "VFI rising": bool(row["vfi_rising"]),
        "In Fib 0.50-0.618 zone": bool(row.get("in_fib_zone", False)),
        "Risk/reward >= 3:1": float(row["max_rr"]) >= 3,
    }
    for label, passed in checklist.items():
        st.write(("✅ " if passed else "❌ ") + label)

    _, chart_df = score_stock(selected)
    if chart_df is not None and not chart_df.empty:
        fig = go.Figure()
        fig.add_trace(go.Candlestick(
            x=chart_df.index,
            open=chart_df["Open"],
            high=chart_df["High"],
            low=chart_df["Low"],
            close=chart_df["Close"],
            name=selected
        ))

        if "EMA50" in chart_df.columns:
            fig.add_trace(go.Scatter(x=chart_df.index, y=chart_df["EMA50"], name="EMA50"))
        if "EMA200" in chart_df.columns:
            fig.add_trace(go.Scatter(x=chart_df.index, y=chart_df["EMA200"], name="EMA200"))

        fig.add_hline(y=float(row["entry_low"]), line_dash="dot", annotation_text="Entry Low")
        fig.add_hline(y=float(row["entry_high"]), line_dash="dot", annotation_text="Entry High")
        fig.add_hline(y=float(row["stop_loss"]), line_dash="dash", annotation_text="Stop")
        fig.add_hline(y=float(row["target_1"]), line_dash="dash", annotation_text="Target 1")
        fig.add_hline(y=float(row["target_2"]), line_dash="dash", annotation_text="Target 2")
        fig.add_hline(y=float(row["target_3"]), line_dash="dash", annotation_text="Target 3")

        fig.update_layout(height=650, xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)

    st.download_button(
        "Download scanner_results.csv",
        data=df.to_csv(index=False),
        file_name="scanner_results.csv",
        mime="text/csv"
    )

st.warning("This is not financial advice. Use this as a scanner only and place trades manually in Robinhood after your own review.")
