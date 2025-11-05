import smtplib
import requests
from email.message import EmailMessage
import os

def send_alert_if_needed(tx, result, correlation_id):
    # Email
    if os.getenv("EMAIL_ENABLED", "false").lower() == "true":
        msg = EmailMessage()
        msg.set_content(f"ALERT [{correlation_id}]: {tx['sender_account']} → {tx['receiver_account']}, {tx['amount']}")
        msg["Subject"] = f"Fraud Alert [{correlation_id}]"
        msg["From"] = os.getenv("SMTP_FROM", "radar@example.com")
        msg["To"] = os.getenv("ALERT_EMAIL", "analyst@example.com")
        try:
            with smtplib.SMTP(os.getenv("SMTP_HOST", "localhost"), int(os.getenv("SMTP_PORT", "587"))) as s:
                s.send_message(msg)
        except Exception:
            pass

    # Webhook
    webhook_url = os.getenv("WEBHOOK_URL")
    if webhook_url:
        payload = {
            "correlationId": correlation_id,
            "transaction": tx,
            "reasons": result["reasons"],
            "ml_score": result.get("ml_score")
        }
        try:
            requests.post(webhook_url, json=payload, timeout=5)
        except Exception:
            pass
