# Powered Max AI Trader Product Plan

## Goal

Build a clean, mobile-friendly stock scanner that helps review high-volume AI and momentum stocks with market-structure scoring, risk planning, journal tracking, and alerts.

## User Experience

The app should be simple:

1. Open dashboard.
2. Pick scan universe.
3. Click scan.
4. Review top candidates.
5. Open trade card.
6. Review checklist, risk, position size, chart, and news.
7. Manually place trade in Robinhood if the user chooses.
8. Save setup to journal.

## Core Features

- AI/high-volume scanner
- Broad market universe option
- Market structure review
- BOS, CHOCH, MSS labels
- Order block zones
- Fair value gap zones
- Fibonacci confluence
- Volume and VFI confirmation
- Risk-to-reward calculator
- Position sizing by account size and risk percentage
- Trade journal
- Performance dashboard
- Text or webhook alerts
- Cloud deployment

## Safety Guardrails

- No automatic Robinhood execution.
- Manual review required.
- Alerts are informational.
- Every setup shows risk before potential reward.
- Earnings and news risk should be checked before taking a position.

## Build Order

### Phase 1: Usable Dashboard

- Clean mobile-first layout
- Simple scan controls
- Top candidate table
- Trade card with chart, risk, and checklist

### Phase 2: Larger Universe

- AI focus list
- User watchlist
- Full market list
- Volume and price filters
- Scan progress indicator

### Phase 3: Alerts

- Webhook alerts
- SMS provider integration through user-owned webhook
- Daily morning report

### Phase 4: Cloud

- Streamlit Community Cloud deployment
- Secrets configuration
- Browser and phone access

### Phase 5: Performance

- Trade journal analytics
- Win rate
- Average P/L
- Average risk-to-reward
- Drawdown tracking

## Next Priority

Make the app easier to run and deploy before adding more complex features.
