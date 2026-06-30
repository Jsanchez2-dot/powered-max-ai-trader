import streamlit as st
import plotly.graph_objects as go
from scanner_engine import scan_market, score_stock
from core.alerts import send_alerts_for_buy_setups
from core.journal import add_trade, load_journal, journal_stats
from core.news import fetch_news_headlines, news_risk_score

st.set_page_config(page_title="Powered Max AI Trader", layout="wide")

st.title("Powered Max AI Trader v4")
st.caption("AI/high-volume scanner with LuxAlgo-style market structure, risk management, alerts, news, and journal")

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

    st.header("Alerts")
    send_sms = st.checkbox("Send text/webhook alerts for BUY SETUP", value=False)
    st.caption("Set SMS_WEBHOOK_URL in your environment for live alerts.")

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Strategy", "SMC + AI Stocks")
with col2:
    st.metric("Min Avg Volume", "5M")
with col3:
    st.metric("Minimum R:R", "3:1")
with col4:
    st.metric("Manual Broker", "Robinhood")

if st.button("Run Live Scan", type="primary"):
    with st.spinner("Scanning AI and high-volume stocks..."):
        st.session_state.results, st.session_state.chart_data = scan_market()
        if send_sms:
            send_alerts_for_buy_setups(st.session_state.results)

df = st.session_state.results

tab_scanner, tab_journal, tab_deploy = st.tabs(["Scanner", "Trade Journal", "Deployment / Alerts"])

with tab_scanner:
    if df is None:
        st.info("Click Run Live Scan to start.")
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
        display_cols = [
            "ticker", "score", "action", "trend_structure", "last_close", "relative_volume",
            "entry_zone", "stop_loss", "risk_per_share", "max_rr",
            "target_1", "rr_target_1", "target_2", "rr_target_2", "target_3", "rr_target_3",
            "bullish_bos", "choch_bullish", "mss_bullish", "order_block_confluence", "fvg_confluence",
            "above_50ema", "above_200ema", "vfi_rising"
        ]
        st.dataframe(df[[c for c in display_cols if c in df.columns]], use_container_width=True)

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

        st.subheader("LuxAlgo-Style Checklist")
        checklist = {
            "Bullish BOS": bool(row.get("bullish_bos", False)),
            "Bullish CHOCH": bool(row.get("choch_bullish", False)),
            "Bullish MSS": bool(row.get("mss_bullish", False)),
            "Order block confluence": bool(row.get("order_block_confluence", False)),
            "Fair value gap confluence": bool(row.get("fvg_confluence", False)),
            "In Fib 0.50-0.618 zone": bool(row.get("in_fib_zone", False)),
            "VFI rising": bool(row.get("vfi_rising", False)),
            "Risk/reward >= 3:1": float(row["max_rr"]) >= 3,
        }
        for label, passed in checklist.items():
            st.write(("✅ " if passed else "❌ ") + label)

        with st.expander("News Analysis"):
            headlines = fetch_news_headlines(selected)
            st.metric("News risk score", news_risk_score(headlines))
            for h in headlines:
                st.write("• " + h)

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

            fig.add_hrect(y0=float(row["entry_low"]), y1=float(row["entry_high"]), line_width=0, opacity=0.15, annotation_text="Fib Entry Zone")
            fig.add_hline(y=float(row["stop_loss"]), line_dash="dash", annotation_text="Stop")
            fig.add_hline(y=float(row["target_1"]), line_dash="dash", annotation_text="Target 1")
            fig.add_hline(y=float(row["target_2"]), line_dash="dash", annotation_text="Target 2")
            fig.add_hline(y=float(row["target_3"]), line_dash="dash", annotation_text="Target 3")

            fig.update_layout(height=650, xaxis_rangeslider_visible=False)
            st.plotly_chart(fig, use_container_width=True)

        with st.expander("Save this trade to journal"):
            notes = st.text_area("Trade notes", value="")
            if st.button("Add selected setup to journal"):
                add_trade({
                    "date": row["date"],
                    "ticker": selected,
                    "setup": row["action"],
                    "entry": row["entry_mid"],
                    "stop": row["stop_loss"],
                    "target_1": row["target_1"],
                    "target_2": row["target_2"],
                    "target_3": row["target_3"],
                    "shares": shares,
                    "notes": notes,
                })
                st.success("Trade saved to journal.")

        st.download_button(
            "Download scanner_results.csv",
            data=df.to_csv(index=False),
            file_name="scanner_results.csv",
            mime="text/csv"
        )

with tab_journal:
    journal = load_journal()
    stats = journal_stats(journal)
    j1, j2, j3 = st.columns(3)
    j1.metric("Trades", stats["trades"])
    j2.metric("Win rate", f"{stats['win_rate']}%")
    j3.metric("Total P/L", f"${stats['total_pnl']:,.2f}")
    st.dataframe(journal, use_container_width=True)

with tab_deploy:
    st.subheader("Cloud Deployment")
    st.write("Deploy this repo to Streamlit Community Cloud so you can open it from your phone without running Python locally.")
    st.code("streamlit run app.py")
    st.subheader("Text Alerts")
    st.write("Set an environment variable called SMS_WEBHOOK_URL to connect text alerts through Zapier, Make, Telegram, Discord, or an SMS provider.")
    st.write("When enabled in the sidebar, the app sends alerts for BUY SETUP signals after a scan.")

st.warning("This is not financial advice. Use this as a scanner only and place trades manually in Robinhood after your own review.")
