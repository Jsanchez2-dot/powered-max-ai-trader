# Powered Max AI Trader

AI / semiconductor / high-volume stock scanner for Robinhood manual trading.

## What it does

- Scans AI and semiconductor stocks
- Filters for high volume and minimum price
- Scores each ticker using trend, volume, VFI, Fibonacci, and BOS-style rules
- Shows Buy Setup / Watch / Wait signals
- Builds a local Streamlit web dashboard
- Exports scanner results to CSV

## Quick start

```bash
pip install -r requirements.txt
streamlit run app.py
```

Then open:

```text
http://localhost:8501
```

Click **Run Daily Scan**.

## Robinhood

This app does not place trades automatically. Use the signals to manually place trades in Robinhood.

## Important

This is not financial advice. It is a trading scanner and decision-support tool only.
