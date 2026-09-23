# import resend
# from app.core.config import settings


# def send_contact_email(
#     name: str,
#     email: str,
#     subject: str,
#     message: str,
# ):
#     resend.api_key = settings.resend_api_key

#     params = {
#         "from": settings.resend_from_email,
#         "to": [settings.contact_receiver_email],
#         "subject": subject or f"New message from {name}",
#         "reply_to": email,
#         "html": f"""
#         <h2>New Portfolio Contact Message</h2>

#         <p><strong>Name:</strong> {name}</p>
#         <p><strong>Email:</strong> {email}</p>
#         <p><strong>Subject:</strong> {subject}</p>

#         <hr>

#         <p><strong>Message:</strong></p>
#         <p>{message}</p>
#         """,
#     }

#     return resend.Emails.send(params)

import resend
from app.core.config import settings


def send_contact_email(
    name: str,
    email: str,
    subject: str,
    message: str,
):
    if not settings.resend_api_key:
        raise RuntimeError("RESEND_API_KEY is not configured")

    if not settings.resend_from_email:
        raise RuntimeError("RESEND_FROM_EMAIL is not configured")

    if not settings.contact_receiver_email:
        raise RuntimeError("CONTACT_RECEIVER_EMAIL is not configured")

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

    response = resend.Emails.send(params)

    print("Resend response:", response)

    return response