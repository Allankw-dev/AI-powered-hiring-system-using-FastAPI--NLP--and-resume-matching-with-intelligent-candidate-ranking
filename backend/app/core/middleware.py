"""Pure-ASGI middleware: security headers and request-size limits.

Written as raw ASGI (not BaseHTTPMiddleware) so they cannot interfere with
streaming responses or background tasks.
"""
import json

from app.core.config import settings

# Paths that carry file uploads and therefore get the larger body limit.
_UPLOAD_PATHS = ("/resumes/upload", "/users/me/upload-picture")
# The interactive docs (only when ENABLE_DOCS) load scripts from a CDN, so a strict CSP would break them.
_DOC_PATHS = ("/docs", "/redoc", "/openapi.json")

_BASE_HEADERS = {
    b"x-content-type-options": b"nosniff",
    b"x-frame-options": b"DENY",
    b"referrer-policy": b"no-referrer",
    b"permissions-policy": b"camera=(), microphone=(), geolocation=(), payment=(), usb=(), interest-cohort=()",
    b"cross-origin-opener-policy": b"same-origin",
    b"x-permitted-cross-domain-policies": b"none",
}
_API_CSP = b"default-src 'none'; frame-ancestors 'none'; base-uri 'none'; form-action 'none'"


def error_headers() -> dict[str, str]:
    """The same headers as plain strings, for responses created by the 500 handler."""
    out = {k.decode(): v.decode() for k, v in _BASE_HEADERS.items()}
    out.update({"content-security-policy": _API_CSP.decode(), "cache-control": "no-store", "pragma": "no-cache"})
    if settings.is_production and settings.HSTS_ENABLED:
        out["strict-transport-security"] = "max-age=31536000; includeSubDomains"
    return out


class SecurityHeadersMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        is_docs = scope["path"].startswith(_DOC_PATHS)

        async def send_with_headers(message):
            if message["type"] == "http.response.start":
                headers = [(k, v) for k, v in message.get("headers", []) if k.lower() != b"server"]
                present = {k.lower() for k, _ in headers}
                extra = dict(_BASE_HEADERS)
                if not is_docs:
                    extra[b"content-security-policy"] = _API_CSP
                    extra[b"cache-control"] = b"no-store"  # API answers hold personal data: never cache them
                    extra[b"pragma"] = b"no-cache"
                if settings.is_production and settings.HSTS_ENABLED:
                    extra[b"strict-transport-security"] = b"max-age=31536000; includeSubDomains"
                headers += [(k, v) for k, v in extra.items() if k not in present]
                message = {**message, "headers": headers}
            await send(message)

        await self.app(scope, receive, send_with_headers)


class BodySizeLimitMiddleware:
    """Rejects oversized request bodies before the app buffers them in memory.

    1. A declared Content-Length over the limit is refused immediately.
    2. A chunked body (no Content-Length) is counted as it streams in; once it goes over
       the limit the app is told the client disconnected (so it stops reading) and the
       caller gets a clean 413 instead of whatever error the app would have produced.
    """

    def __init__(self, app):
        self.app = app

    @staticmethod
    def _limit_for(path: str) -> int:
        if path.startswith(_UPLOAD_PATHS):
            # file + multipart framing
            return max(settings.max_upload_bytes, settings.max_picture_bytes) + 1024 * 1024
        return settings.max_json_body_bytes

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        limit = self._limit_for(scope["path"])
        declared = dict(scope["headers"]).get(b"content-length")
        if declared is not None:
            try:
                too_big = int(declared) > limit
            except ValueError:
                too_big = True
            if too_big:
                await self._reject(send)
                return

        received = 0
        too_large = False
        answered = False

        async def counting_receive():
            nonlocal received, too_large
            if too_large:
                return {"type": "http.disconnect"}
            message = await receive()
            if message["type"] == "http.request":
                received += len(message.get("body", b""))
                if received > limit:
                    too_large = True
                    return {"type": "http.disconnect"}
            return message

        async def guarded_send(message):
            nonlocal answered
            if too_large:
                # Whatever the app tries to say now is moot: we answer 413 ourselves, once.
                if not answered:
                    answered = True
                    await self._reject(send)
                return
            if message["type"] == "http.response.start":
                answered = True
            await send(message)

        try:
            await self.app(scope, counting_receive, guarded_send)
        except Exception:
            if not too_large:
                raise
        if too_large and not answered:
            await self._reject(send)

    @staticmethod
    async def _reject(send):
        body = json.dumps({"detail": "Request body too large"}).encode()
        await send({
            "type": "http.response.start",
            "status": 413,
            "headers": [(b"content-type", b"application/json"), (b"content-length", str(len(body)).encode())],
        })
        await send({"type": "http.response.body", "body": body})
