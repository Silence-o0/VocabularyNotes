import os

from fastapi_mail import ConnectionConfig, FastMail, MessageSchema
from pydantic import EmailStr

conf = ConnectionConfig(
    MAIL_USERNAME=os.getenv("MAIL_USERNAME"),
    MAIL_PASSWORD=os.getenv("MAIL_PASSWORD"),
    MAIL_FROM=os.getenv("MAIL_FROM"),
    MAIL_PORT=int(os.getenv("MAIL_PORT")),
    MAIL_SERVER=os.getenv("MAIL_SERVER"),
    MAIL_STARTTLS=os.getenv("MAIL_STARTTLS"),
    MAIL_SSL_TLS=os.getenv("MAIL_SSL_TLS"),
)

fm = FastMail(conf)


async def send_verification_email(request, email: EmailStr, token: str, action: str):
    verify_link = f"{request.base_url}auth/{action}?token={token}"

    message = MessageSchema(
        subject="Verify your email",
        recipients=[email],
        body=f"Click the link to verify your account: {verify_link}",
        subtype="html",
    )
    await fm.send_message(message)
