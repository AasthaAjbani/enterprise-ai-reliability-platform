import os

from fastapi import FastAPI
from fastapi.middleware.cors import (
    CORSMiddleware,
)

from app.api.reliability_routes import (
    router as reliability_router,
)

from app.api.deployment_routes import (
    router as deployment_router,
)

from app.api.self_healing_routes import (
    router as self_healing_router,
)


# =========================================================
# APPLICATION
# =========================================================

app = FastAPI(
    title=
        "Enterprise AI Reliability Platform",

    description=
        (
            "Production-style AI reliability "
            "monitoring, drift detection, "
            "anomaly detection, root-cause "
            "analysis, controlled model promotion, "
            "rollback, and autonomous self-healing."
        ),

    version="1.0.0",
)


# =========================================================
# CORS
# =========================================================

allowed_origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8501",
    "http://127.0.0.1:8501",
]


# ---------------------------------------------------------
# Production frontend URL
# ---------------------------------------------------------

frontend_url = os.getenv(
    "FRONTEND_URL"
)


if frontend_url:

    allowed_origins.append(
        frontend_url.rstrip("/")
    )


# ---------------------------------------------------------
# CORS middleware
# ---------------------------------------------------------

app.add_middleware(
    CORSMiddleware,

    allow_origins=
        allowed_origins,

    allow_credentials=
        True,

    allow_methods=[
        "*"
    ],

    allow_headers=[
        "*"
    ],
)


# =========================================================
# API ROUTERS
# =========================================================

# ---------------------------------------------------------
# Reliability monitoring
#
# Includes:
# /api/reliability
# /api/data-quality
# /api/drift
# /api/performance
# /api/root-causes
# /api/anomalies
# ---------------------------------------------------------

app.include_router(
    reliability_router
)


# ---------------------------------------------------------
# Deployment lifecycle
#
# Includes:
# /api/deployment
# ---------------------------------------------------------

app.include_router(
    deployment_router
)


# ---------------------------------------------------------
# Autonomous self-healing lifecycle
#
# Includes:
# /api/self-healing
# ---------------------------------------------------------

app.include_router(
    self_healing_router
)


# =========================================================
# ROOT ENDPOINT
# =========================================================

@app.get("/")
def root():

    return {

        "service":
            "Enterprise AI Reliability Platform",

        "status":
            "running",

        "version":
            "1.0.0",

        "capabilities": [
            "data-quality-monitoring",
            "data-drift-detection",
            "model-performance-monitoring",
            "anomaly-detection",
            "root-cause-analysis",
            "challenger-model-training",
            "quality-gate-evaluation",
            "model-promotion",
            "model-rollback",
            "conditional-self-healing",
        ],

        "endpoints": {

            "health":
                "/health",

            "reliability":
                "/api/reliability",

            "deployment":
                "/api/deployment",

            "self_healing":
                "/api/self-healing",

            "docs":
                "/docs",
        },
    }


# =========================================================
# HEALTH ENDPOINT
# =========================================================

@app.get("/health")
def health():

    return {

        "status":
            "healthy",

        "service":
            "enterprise-ai-reliability-platform",
    }