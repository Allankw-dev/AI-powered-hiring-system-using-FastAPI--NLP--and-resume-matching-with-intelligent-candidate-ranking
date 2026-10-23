"""One shared rate limiter for the whole app.

Behind a reverse proxy (Render, Cloudflare...) the socket peer is the proxy, so
every visitor would share one rate-limit bucket. We read X-Forwarded-For
instead, but only trust the entry added by *our* proxies (counted from the
right) because anything further left can be spoofed by the client.
"""
from fastapi import Request
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.core.config import settings


def client_ip(request: Request) -> str:
    hops = settings.TRUSTED_PROXY_HOPS
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded and hops > 0:
        parts = [p.strip() for p in forwarded.split(",") if p.strip()]
        if len(parts) >= hops:
            return parts[-hops]
    return get_remote_address(request)


limiter = Limiter(key_func=client_ip, default_limits=["120/minute"])
