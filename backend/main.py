from fastapi import FastAPI
from backend.routers import upload, extract


app = FastAPI(title="ChatZ")

app.include_router(upload.router)
app.include_router(extract.router)