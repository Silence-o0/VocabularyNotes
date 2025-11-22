from fastapi import FastAPI

from app.routers import auth, dictlists, languages, users

app = FastAPI()


app.include_router(auth.router)
app.include_router(users.router)
app.include_router(languages.router)
app.include_router(dictlists.router)
