import streamlit as st
import plotly.graph_objects as go

from enhanced_scanner import enhanced_scan_market
from scanner_engine import score_stock
from core.fundamentals import get_financial_snapshot
from core.catalysts import get_catalyst_snapshot
from core.journal import add_trade, load_journal, journal_stats

st.set_page_config(page_title="Powered Max AI Trader", layout="wide")

st.title("Powered Max AI Trader")
st.caption("Minimal investing-style dashboard for all-stock scanning, news catalysts, financials, technical structure, and risk planning.")

if "scan_df" not in st.session_state:
    st.session_state.scan_df = None

with st.sidebar:
    st.header("Scan")
    universe = st.selectbox("Universe", ["AI Focus", "My Watchlist", "Full Market"])
    max_symbols = st.slider("Symbols to scan", 25, 500, 100, 25)
    use_news = st.checkbox("Include news catalyst", True)
    use_financials = st.checkbox("Include company financials", True)

    st.header("Risk")
    account_size = st.number_input("Account size", 100.0, value=10000.0, step=500.0)
    risk_pct = st.number_input("Risk %", 0.1, 10.0, value=1.0, step=0.1)
    max_risk = account_size * risk_pct / 100
    st.metric("Max risk", f"${max_risk:,.2f}")

if st.button("Run Scan", type="primary", use_container_width=True):
    bar = st.progress(0)
    status = st.empty()

    def progress(i, total, ticker):
        bar.progress(min(i / total, 1.0))
        status.caption(f"Scanning {ticker} ({i}/{total})")

    df, charts = enhanced_scan_market(
        universe_mode=universe,
        max_symbols=max_symbols,
        include_news=use_news,
        include_financials=use_financials,
        progress_callback=progress,
    )
    st.session_state.scan_df = df
    status.empty()

df = st.session_state.scan_df

tab1, tab2, tab3 = st.tabs(["Scanner", "Company", "Journal"])

with tab1:
    if df is None:
        st.info("Set your filters and run a scan.")
    elif df.empty:
        st.warning("No matches found with these filters.")
    else:
        c1, c2, c3 = st.columns(3)
        c1.metric("Results", len(df))
        c2.metric("Top score", int(df["score"].max()))
        c3.metric("Avg news score", round(df.get("news_score", 50).mean(), 1) if "news_score" in df else "N/A")

        columns = ["ticker", "score", "action", "news_score", "news_bias", "financial_score", "last_close", "relative_volume", "entry_zone", "stop_loss", "max_rr"]
        st.dataframe(df[[x for x in columns if x in df.columns]], use_container_width=True, hide_index=True)

        ticker = st.selectbox("Open ticker", df["ticker"].tolist())
        row = df[df["ticker"] == ticker].iloc[0]

        st.subheader(f"{ticker} Trade Card")
        m1, m2, m3, m4, m5 = st.columns(5)
        m1.metric("Score", int(row["score"]))
        m2.metric("Action", row["action"])
        m3.metric("News", row.get("news_score", "N/A"))
        m4.metric("Financial", row.get("financial_score", "N/A"))
        m5.metric("R:R", row["max_rr"])

        risk_per_share = float(row["risk_per_share"])
        shares = int(max_risk // risk_per_share) if risk_per_share > 0 else 0
        st.write(f"Entry zone: **{row['entry_zone']}** | Stop: **${row['stop_loss']}** | Shares: **{shares}**")

        _, chart_df = score_stock(ticker)
        if chart_df is not None and not chart_df.empty:
            fig = go.Figure()
            fig.add_trace(go.Candlestick(x=chart_df.index, open=chart_df["Open"], high=chart_df["High"], low=chart_df["Low"], close=chart_df["Close"], name=ticker))
            if "EMA50" in chart_df:
                fig.add_trace(go.Scatter(x=chart_df.index, y=chart_df["EMA50"], name="EMA50"))
            fig.add_hrect(y0=float(row["entry_low"]), y1=float(row["entry_high"]), opacity=0.15, line_width=0)
            fig.add_hline(y=float(row["stop_loss"]), line_dash="dash")
            fig.add_hline(y=float(row["target_1"]), line_dash="dot")
            fig.add_hline(y=float(row["target_2"]), line_dash="dot")
            fig.add_hline(y=float(row["target_3"]), line_dash="dot")
            fig.update_layout(height=600, xaxis_rangeslider_visible=False)
            st.plotly_chart(fig, use_container_width=True)

        if st.button("Save to journal"):
            add_trade({"date": row["date"], "ticker": ticker, "setup": row["action"], "entry": row["entry_mid"], "stop": row["stop_loss"], "shares": shares, "notes": "Saved from scanner"})
            st.success("Saved.")

with tab2:
    ticker = st.text_input("Ticker", value="NVDA").upper()
    if ticker:
        f = get_financial_snapshot(ticker)
        n = get_catalyst_snapshot(ticker)
        st.subheader(f"{f['company_name']} ({ticker})")
        a, b, c, d = st.columns(4)
        a.metric("Market cap", f["market_cap_display"])
        b.metric("Revenue growth", f["revenue_growth_display"])
        c.metric("Profit margin", f["profit_margin_display"])
        d.metric("Financial score", f["financial_score"])
        st.write(f"Sector: **{f['sector']}** | Industry: **{f['industry']}**")
        st.metric("News catalyst", n["news_score"], n["news_bias"])
        for item in n.get("headlines", [])[:8]:
            if item.get("title"):
                st.write(f"• {item['title']}")

with tab3:
    journal = load_journal()
    stats = journal_stats(journal)
    x, y, z = st.columns(3)
    x.metric("Trades", stats["trades"])
    y.metric("Win rate", f"{stats['win_rate']}%")
    z.metric("Total P/L", f"${stats['total_pnl']:,.2f}")
    st.dataframe(journal, use_container_width=True, hide_index=True)

st.warning("Research tool only. Review every setup before placing any trade.")
