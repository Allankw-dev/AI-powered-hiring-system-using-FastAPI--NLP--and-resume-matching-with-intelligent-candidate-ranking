import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.core.config import settings
from app.core.limiter import limiter
from app.routers import admin, applications, auth, chat, jobs, password_reset, resumes, users

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger("app")


@asynccontextmanager
async def lifespan(_: FastAPI):
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    if not settings.email_configured:
        logger.warning("No email provider configured: admin 2FA codes and reset emails cannot be sent.")
    if not (settings.ANTHROPIC_API_KEY or settings.GEMINI_API_KEY):
        logger.warning("No chat API key configured: the Hira assistant is disabled.")
    yield


app = FastAPI(title="AI Hiring Platform", version="1.1.0", lifespan=lifespan)

# ── Rate limiting ──
app.state.limiter = limiter


@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={"detail": "Too many requests. Please wait a moment and try again."},
        headers={"Retry-After": "60"},
    )


@app.exception_handler(Exception)
async def unhandled_error_handler(request: Request, exc: Exception):
    # Details go to the server log, never to the client.
    logger.exception("Unhandled error on %s %s", request.method, request.url.path)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


app.add_middleware(SlowAPIMiddleware)

# ── CORS ──
# The API uses bearer tokens (no cookies), so credentials are never needed.
# Restrict with CORS_ORIGINS="https://your-app.streamlit.app" if you want to.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

# ── Routers ──
for module in (auth, jobs, resumes, applications, admin, users, password_reset, chat):
    app.include_router(module.router)


@app.api_route("/", methods=["GET", "HEAD"])
def home():
    return {"message": "AI Hiring Platform API is running"}


@app.api_route("/health", methods=["GET", "HEAD"])
def health():
    return {"status": "ok"}
