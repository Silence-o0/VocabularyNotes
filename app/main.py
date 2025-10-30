from dotenv import load_dotenv
from fastapi import FastAPI

load_dotenv()

from app.routers import auth, users  # noqa: E402

app = FastAPI()


app.include_router(auth.router)
app.include_router(users.router)
