import os

from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.environ["DATABASE_URL"]

ACCESS_TOKEN_EXPIRE_MINUTES = int(os.environ["ACCESS_TOKEN_EXPIRE_MINUTES"])
VERIFY_TOKEN_EXPIRE_MINUTES = int(os.environ["VERIFY_TOKEN_EXPIRE_MINUTES"])
SECRET_KEY = os.environ["SECRET_KEY"]

MAIL_USERNAME = os.environ["MAIL_USERNAME"]
MAIL_PASSWORD = os.environ["MAIL_PASSWORD"]
MAIL_FROM = os.environ["MAIL_FROM"]
MAIL_PORT = int(os.environ["MAIL_PORT"])
MAIL_SERVER = os.environ["MAIL_SERVER"]
MAIL_STARTTLS = os.environ["MAIL_STARTTLS"]
MAIL_SSL_TLS = os.environ["MAIL_SSL_TLS"]

JWT_ALGORITM = "HS256"
