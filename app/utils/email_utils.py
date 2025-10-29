import os

from fastapi_mail import ConnectionConfig, FastMail, MessageSchema
from pydantic import EmailStr

conf = ConnectionConfig(
    MAIL_USERNAME=os.environ["MAIL_USERNAME"],
    MAIL_PASSWORD=os.environ["MAIL_PASSWORD"],
    MAIL_FROM=os.environ["MAIL_FROM"],
    MAIL_PORT=int(os.environ["MAIL_PORT"]),
    MAIL_SERVER=os.environ["MAIL_SERVER"],
    MAIL_STARTTLS=os.environ["MAIL_STARTTLS"],
    MAIL_SSL_TLS=os.environ["MAIL_SSL_TLS"],
)

fm = FastMail(conf)


def send_verification_email(request, email: EmailStr, token: str, action: str):
    verify_link = f"{request.base_url}auth/{action}?token={token}"

    message = MessageSchema(
        subject="Verify your email",
        recipients=[email],
        body=f"Click the link to verify your account: {verify_link}",
        subtype="html",
    )
    fm.send_message(message)
