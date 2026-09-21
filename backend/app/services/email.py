import resend
from app.core.config import settings


def send_contact_email(
    name: str,
    email: str,
    subject: str,
    message: str,
):
    resend.api_key = settings.resend_api_key

    params = {
        "from": settings.resend_from_email,
        "to": [settings.contact_receiver_email],
        "subject": subject or f"New message from {name}",
        "reply_to": email,
        "html": f"""
        <h2>New Portfolio Contact Message</h2>

        <p><strong>Name:</strong> {name}</p>
        <p><strong>Email:</strong> {email}</p>
        <p><strong>Subject:</strong> {subject}</p>

        <hr>

        <p><strong>Message:</strong></p>
        <p>{message}</p>
        """,
    }

    return resend.Emails.send(params)