import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

GMAIL_SENDER = os.getenv("GMAIL_SENDER")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")


def send_email(to: str, subject: str, body: str) -> dict:
    """
    Sends a single email via Gmail SMTP.
    Returns a dict with status and any error message.
    """
    try:
        msg = MIMEMultipart()
        msg["From"] = GMAIL_SENDER
        msg["To"] = to
        msg["Subject"] = subject

        msg.attach(MIMEText(body, "plain"))

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(GMAIL_SENDER, GMAIL_APP_PASSWORD)
            server.sendmail(GMAIL_SENDER, to, msg.as_string())

        return {"status": "sent", "error": None}

    except Exception as e:
        return {"status": "failed", "error": str(e)}