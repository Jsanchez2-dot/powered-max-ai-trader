# Deployment Guide

## Option 1: Run locally

```bash
git pull
pip3 install -r requirements.txt
python3 -m streamlit run app_barebones.py
```

Open:

```text
http://localhost:8501
```

## Option 2: Deploy to Streamlit Community Cloud

1. Go to Streamlit Community Cloud.
2. Sign in with GitHub.
3. Choose this repository: `Jsanchez2-dot/powered-max-ai-trader`.
4. Set main file path to:

```text
app_barebones.py
```

5. Deploy.

## Environment variables

Add these in the cloud app secrets/settings area when ready:

```text
SMS_WEBHOOK_URL="your webhook URL"
NEWS_API_KEY="your news API key"
```

## Text alerts

The app uses a webhook approach. This lets the user connect alerts to:

- Zapier
- Make
- Telegram
- Discord
- Pushover
- SMS providers

The app should only send informational scanner alerts. It should not submit brokerage orders.
