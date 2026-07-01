# Powered Max AI Trader

All-stock scanner for momentum, market structure, news catalysts, company financials, and Robinhood-friendly manual trade planning.

## Current Features

- AI focus, custom watchlist, and full-market scanner groundwork
- News catalyst scoring for momentum
- Company financial snapshot and financial score
- LuxAlgo-style market-structure review
- BOS / CHOCH / MSS labels
- Order block and fair value gap logic
- Fibonacci entry-zone confluence
- Risk-to-reward calculator
- Position sizing by account size and risk percentage
- Trade journal
- Performance tracking base
- Text/webhook alert hook
- Mobile-friendly dashboard theme
- Barebones-style dashboard prototype

## Recommended dashboard

Run the newer minimalist dashboard:

```bash
git pull
pip3 install -r requirements.txt
python3 -m streamlit run app_barebones.py
```

Then open:

```text
http://localhost:8501
```

## Original dashboard

```bash
python3 -m streamlit run app.py
```

## Cloud deployment

See:

```text
docs/DEPLOYMENT.md
```

For cloud deployment, use this main file path:

```text
app_barebones.py
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
