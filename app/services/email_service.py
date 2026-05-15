import aiosmtplib
from email.message import EmailMessage
<<<<<<< HEAD
from app.config import settings


async def send_alert_email(subject: str, body: str, to_email: str):
    message = EmailMessage()
    message["From"] = settings.SMTP_USER
=======
import os

SMTP_HOST = os.getenv("SMTP_HOST", "smtp.mailtrap.io")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASS = os.getenv("SMTP_PASS", "")

async def send_alert_email(subject: str, body: str, to_email: str):
    message = EmailMessage()
    message["From"] = SMTP_USER
>>>>>>> 36b22f616c006a8fae6fd7833e030d6d32b07ede
    message["To"] = to_email
    message["Subject"] = subject
    message.set_content(body)

    await aiosmtplib.send(
        message,
<<<<<<< HEAD
        hostname=settings.SMTP_HOST,
        port=settings.SMTP_PORT,
        username=settings.SMTP_USER,
        password=settings.SMTP_PASS,
        start_tls=True,
=======
        hostname=SMTP_HOST,
        port=SMTP_PORT,
        username=SMTP_USER,
        password=SMTP_PASS,
        start_tls=True
>>>>>>> 36b22f616c006a8fae6fd7833e030d6d32b07ede
    )