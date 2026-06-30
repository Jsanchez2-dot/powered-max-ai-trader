import streamlit as st
import plotly.graph_objects as go
from scanner_engine import scan_market, score_stock

st.set_page_config(page_title="Powered Max AI Trader", layout="wide")

st.title("Powered Max AI Trader")
st.caption("AI / semiconductor / high-volume stock scanner for Robinhood manual trading")

if "results" not in st.session_state:
    st.session_state.results = None
    st.session_state.chart_data = {}

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Strategy", "AI + High Volume")
with col2:
    st.metric("Min Avg Volume", "5M")
with col3:
    st.metric("Minimum Score", "85 Buy Setup")

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
            "entry_zone", "stop_loss", "target_1", "target_2", "target_3",
            "bullish_bos", "above_50ema", "above_200ema", "vfi_rising"
        ]],
        use_container_width=True
    )

    selected = st.selectbox("Select ticker for chart", df["ticker"].tolist())
    row = df[df["ticker"] == selected].iloc[0]

    st.subheader(f"{selected} Trade Card")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Score", int(row["score"]))
    c2.metric("Action", row["action"])
    c3.metric("Entry Zone", row["entry_zone"])
    c4.metric("Stop Loss", row["stop_loss"])

    c5, c6, c7 = st.columns(3)
    c5.metric("Target 1", row["target_1"])
    c6.metric("Target 2", row["target_2"])
    c7.metric("Target 3", row["target_3"])

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

        fig.update_layout(height=600, xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)

    st.download_button(
        "Download scanner_results.csv",
        data=df.to_csv(index=False),
        file_name="scanner_results.csv",
        mime="text/csv"
    )

st.warning("This is not financial advice. Use this as a scanner only and place trades manually in Robinhood after your own review.")
