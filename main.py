from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.routes import base, songs

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
    ],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(base.router)
app.include_router(songs.router)


@app.get("/")
async def root():
    return "Hello world."
