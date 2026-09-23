import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.reliability_routes import (
    router as reliability_router,
)


app = FastAPI(
    title="Enterprise AI Reliability Platform",
    description=(
        "Platform for monitoring AI model health, "
        "data quality, data drift, model performance, "
        "anomalies and root causes."
    ),
    version="1.0.0",
)


# ---------------------------------------------------------
# CORS
# ---------------------------------------------------------

allowed_origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8501",
    "http://127.0.0.1:8501",
]


frontend_url = os.getenv("FRONTEND_URL")


if frontend_url:
    allowed_origins.append(
        frontend_url.rstrip("/")
    )


app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------
# ROUTES
# ---------------------------------------------------------

app.include_router(
    reliability_router
)


@app.get("/")
def root():
    return {
        "message":
            "Enterprise AI Reliability Platform is running."
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }