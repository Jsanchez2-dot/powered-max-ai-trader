# Powered Max AI Trader

AI / semiconductor / high-volume stock scanner for Robinhood manual trading.

## Current Features

- AI and high-volume stock scanner
- LuxAlgo-style market-structure review
- BOS / CHOCH / MSS labels
- Order block and fair value gap logic
- Fibonacci entry-zone confluence
- Risk-to-reward calculator
- Position sizing by account size and risk percentage
- Trade journal
- Performance tracking base
- News analysis hook
- Text/webhook alert hook
- Mobile-friendly dashboard theme

## Run locally

```bash
git pull
pip3 install -r requirements.txt
python3 -m streamlit run app.py
```

Then open:

```text
http://localhost:8501
```

Click **Run Live Scan**.

## Cloud deployment

See:

```text
docs/DEPLOYMENT.md
```

## Text alerts

See:

```text
docs/TEXT_ALERTS.md
```

## Product plan

See:

```text
docs/PRODUCT_PLAN.md
```

## Robinhood

This app does not place trades automatically. Use the signals to manually place trades in Robinhood.

## Important

This is not financial advice. It is a scanner and decision-support tool only.
