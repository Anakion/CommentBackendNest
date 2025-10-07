import os
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from starlette.staticfiles import StaticFiles

from src.api.v1 import comments
from src.api.v1 import captcha
from src.api.v1 import websocket

os.makedirs("uploads/images", exist_ok=True)
os.makedirs("uploads/texts", exist_ok=True)

app = FastAPI(
    title="Comment System API",
    description="Система комментариев с капчей и файлами",
    version="1.0.0",
)

app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

app.include_router(comments.router)
app.include_router(captcha.router)
app.include_router(websocket.router)

@app.get("/")
async def root():
    return {"message": "Comment System API"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
