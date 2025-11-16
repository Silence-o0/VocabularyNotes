from fastapi_mail import ConnectionConfig, FastMail, MessageSchema

from app import constants

conf = ConnectionConfig(
    MAIL_USERNAME=constants.MAIL_USERNAME,
    MAIL_PASSWORD=constants.MAIL_PASSWORD,
    MAIL_FROM=constants.MAIL_FROM,
    MAIL_PORT=constants.MAIL_PORT,
    MAIL_SERVER=constants.MAIL_SERVER,
    MAIL_STARTTLS=constants.MAIL_STARTTLS,
    MAIL_SSL_TLS=constants.MAIL_SSL_TLS,
)

fm = FastMail(conf)


async def send_verification_email(request, email: str, token: str, action: str):
    verify_link = f"{request.base_url}auth/{action}?token={token}"

    message = MessageSchema(
        subject="Verify your email",
        recipients=[email],
        body=f"Click the link to verify your account: {verify_link}",
        subtype="html",
    )
    await fm.send_message(message)
