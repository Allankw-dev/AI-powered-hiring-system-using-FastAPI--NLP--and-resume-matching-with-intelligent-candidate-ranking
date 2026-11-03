import logging
import os
import importlib
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.trustedhost import TrustedHostMiddleware
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.core.config import settings
from app.core.limiter import limiter
from app.core.middleware import BodySizeLimitMiddleware, SecurityHeadersMiddleware, error_headers
from app.core.db_setup import ensure_tables
from app.routers import admin, applications, auth, chat, jobs, password_reset, resumes, unsubscribe, users

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger("app")
importlib.import_module("app.models")  # registers every table on Base.metadata
# These libraries log full request URLs at INFO level; keep them quiet.
for _noisy in ("httpx", "httpcore", "multipart"):
    logging.getLogger(_noisy).setLevel(logging.WARNING)


@asynccontextmanager
async def lifespan(_: FastAPI):
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    try:
        ensure_tables()  # adds tables introduced by an update; never alters existing ones
    except Exception:  # noqa: BLE001 - the API can still start; the error is logged
        logger.exception("Could not create missing tables")
    if not settings.email_configured:
        logger.warning("No email provider configured: admin 2FA codes and reset emails cannot be sent.")
    if not (settings.ANTHROPIC_API_KEY or settings.GEMINI_API_KEY):
        logger.warning("No chat API key configured: the Hira assistant is disabled.")
    yield


# debug is explicitly off (it would put stack traces in HTTP responses), and the
# interactive docs / schema are only served when ENABLE_DOCS is on (default: not in production).
_docs = settings.docs_enabled
app = FastAPI(
    title="AI Hiring Platform",
    version="1.2.0",
    lifespan=lifespan,
    debug=False,
    docs_url="/docs" if _docs else None,
    redoc_url=None,
    openapi_url="/openapi.json" if _docs else None,
)

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
    # ServerErrorMiddleware runs outside our middleware, so add the headers here too.
    return JSONResponse(status_code=500, content={"detail": "Internal server error"}, headers=error_headers())


app.add_middleware(SlowAPIMiddleware)

# ── CORS ──
# The API uses bearer tokens (no cookies), so credentials are never needed.
# By default only the Streamlit frontend (FRONTEND_URL) may call us from a browser.
# Add more with CORS_ORIGINS="https://a.example,https://b.example".
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
    max_age=600,
)

# Optional Host-header allow-list (set ALLOWED_HOSTS=api.example.com to turn on).
if settings.allowed_host_list:
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.allowed_host_list)

# Added last = runs first: oversized bodies are refused before anything else sees them,
# and every response (including errors and CORS preflights) gets the security headers.
app.add_middleware(BodySizeLimitMiddleware)
app.add_middleware(SecurityHeadersMiddleware)

# ── Routers ──
for module in (auth, jobs, resumes, applications, admin, users, password_reset, unsubscribe, chat):
    app.include_router(module.router)


@app.api_route("/", methods=["GET", "HEAD"], include_in_schema=False)
def home():
    return {"message": "AI Hiring Platform API is running"}


@app.api_route("/health", methods=["GET", "HEAD"], include_in_schema=False)
def health():
    return {"status": "ok"}
