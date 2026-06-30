# Text Alert Setup

The app is designed to send scanner alerts through a webhook.

## Why webhook alerts

A webhook is flexible and lets the user choose the alert provider. It can connect to SMS, Telegram, Discord, email, or push notifications.

## Required setting

Set this environment variable:

```text
SMS_WEBHOOK_URL="your webhook URL"
```

## Suggested setup

### Zapier or Make

1. Create a webhook trigger.
2. Copy the webhook URL.
3. Add it as `SMS_WEBHOOK_URL` in Streamlit secrets or local environment.
4. Connect the webhook to a text message, email, or app notification action.

### Local testing

Create a `.env` file using `.env.example` as a template.

Never commit real keys or webhook URLs to GitHub.

## Alert contents

Alerts should include:

- Ticker
- Score
- Status
- Entry zone
- Stop
- Targets
- Risk-to-reward

## Rule

Alerts are informational only. The user reviews the setup and places any trade manually.
