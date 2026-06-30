import os
import requests


def format_trade_alert(row):
    return (
        f"Powered Max AI Trader\n"
        f"{row.get('ticker')} | {row.get('action')} | Score {row.get('score')}\n"
        f"Entry: {row.get('entry_zone')}\n"
        f"Stop: {row.get('stop_loss')}\n"
        f"T1: {row.get('target_1')} | T2: {row.get('target_2')} | T3: {row.get('target_3')}\n"
        f"Max R:R: {row.get('max_rr')}:1"
    )


def send_text_alert(message):
    """Send a text alert using a webhook service.

    Set SMS_WEBHOOK_URL in your environment. This is provider-neutral, so you can
    connect it to Zapier, Make, Pushover, Discord, Telegram, or an SMS provider.
    """
    webhook = os.getenv("SMS_WEBHOOK_URL")
    if not webhook:
        return {"sent": False, "reason": "SMS_WEBHOOK_URL is not set"}
    try:
        response = requests.post(webhook, json={"message": message}, timeout=10)
        return {"sent": response.ok, "status_code": response.status_code, "text": response.text[:200]}
    except Exception as exc:
        return {"sent": False, "reason": str(exc)}


def send_alerts_for_buy_setups(df):
    results = []
    if df is None or df.empty:
        return results
    for _, row in df[df["action"] == "BUY SETUP"].iterrows():
        results.append(send_text_alert(format_trade_alert(row)))
    return results
