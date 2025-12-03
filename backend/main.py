from fastapi import FastAPI
from backend.routers import upload


app = FastAPI(title="ChatZ")

app.include_router(upload.router)