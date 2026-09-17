import smtplib
from email.message import EmailMessage

from app.core.config import settings


def send_contact_email(
    name: str,
    email: str,
    subject: str,
    message: str,
) -> None:
    msg = EmailMessage()

    msg["From"] = settings.smtp_username
    msg["To"] = settings.contact_receiver_email
    msg["Reply-To"] = email
    msg["Subject"] = f"Portfolio Contact: {subject or 'New Message'}"

    msg.set_content(
        f"""New message from your portfolio website.

Name: {name}
Email: {email}
Subject: {subject or 'No subject'}

Message:
{message}
"""
    )

    with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
        server.starttls()
        server.login(
            settings.smtp_username,
            settings.smtp_password,
        )
        server.send_message(msg)