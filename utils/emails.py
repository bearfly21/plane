from dotenv import load_dotenv
import os
import smtplib
from email.message import EmailMessage

load_dotenv()

SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASS = os.getenv("SMTP_PASS")

if not SMTP_USER or not SMTP_PASS:
    raise RuntimeError("SMTP credentials not set")


def send_invite_email(to_email: str, team_name: str, token: str):
    try:
        link = f"http://localhost:8000/teams/accept-invite?token={token}"
        msg = EmailMessage()
        msg["Subject"] = f"Invitation to join team {team_name}"
        msg["From"] = SMTP_USER
        msg["To"] = to_email
        msg.set_content(f"Click to accept: {link}")

        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as smtp:
            smtp.starttls()
            smtp.login(SMTP_USER, SMTP_PASS)
            smtp.send_message(msg)
    except Exception as e:
        print(f"[ERROR] Failed to send email to {to_email}: {e}")

