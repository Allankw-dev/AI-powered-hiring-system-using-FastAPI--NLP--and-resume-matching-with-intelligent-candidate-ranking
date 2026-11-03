"""Check the environment variables before you deploy. Never prints a secret value.

    python -m scripts.check_env            # uses the current environment / .env
Exit code 1 if something is wrong (the app would refuse to start or be insecure).
"""
import sys

from pydantic import ValidationError

OK, WARN, FAIL = "  [ ok ]", "  [warn]", "  [FAIL]"


def main() -> int:
    try:
        from app.core.config import Settings
        s = Settings()
    except ValidationError as exc:
        print(f"{FAIL} settings are invalid:")
        for err in exc.errors():
            print(f"         {'.'.join(map(str, err['loc'])) or 'settings'}: {err['msg']}")
        return 1

    problems = 0
    checks: list[tuple[str, str]] = []

    def add(level: str, text: str):
        nonlocal problems
        problems += level == FAIL
        checks.append((level, text))

    prod = s.is_production
    add(OK, f"ENVIRONMENT = {s.ENVIRONMENT}")
    key = s.SECRET_KEY.get_secret_value()
    add(OK if len(key) >= 32 else FAIL, f"SECRET_KEY length {len(key)} (need 32+)")
    url = s.DATABASE_URL.get_secret_value()
    add(OK, f"DATABASE_URL driver = {url.split('://', 1)[0]}")
    if prod and url.startswith("sqlite"):
        add(FAIL, "DATABASE_URL is SQLite in production (data is lost on every redeploy)")
    if prod and "sslmode=disable" in url:
        add(FAIL, "DATABASE_URL has sslmode=disable in production")
    add(OK if s.email_configured else WARN, "email provider configured" if s.email_configured else "no email provider: admin 2FA and password reset emails cannot be sent")
    add(OK if s.OTP_DELIVERY == "email" else (FAIL if prod else WARN), f"OTP_DELIVERY = {s.OTP_DELIVERY}")
    add(OK if (s.ANTHROPIC_API_KEY or s.GEMINI_API_KEY) else WARN, "chat API key present" if (s.ANTHROPIC_API_KEY or s.GEMINI_API_KEY) else "no chat API key: Hira is disabled")
    origins = s.cors_origin_list
    add(FAIL if (prod and "*" in origins) else OK, f"CORS allows: {', '.join(origins) or 'nothing'}")
    add(FAIL if (prod and s.docs_enabled) else OK, f"/docs {'ENABLED' if s.docs_enabled else 'disabled'}")
    add(OK if s.FRONTEND_URL.startswith("https://") or not prod else FAIL, f"FRONTEND_URL = {s.FRONTEND_URL}")
    add(OK if s.CONTACT_EMAIL else (WARN if prod else OK), "CONTACT_EMAIL set (privacy requests)" if s.CONTACT_EMAIL else "CONTACT_EMAIL is not set: the legal pages and email footers have no contact address")
    add(OK if s.API_PUBLIC_URL else WARN, "API_PUBLIC_URL set (one-click unsubscribe headers on)" if s.API_PUBLIC_URL else "API_PUBLIC_URL not set: emails carry an unsubscribe link but no one-click header")
    add(OK if s.TRUSTED_PROXY_HOPS >= 1 or not prod else WARN, f"TRUSTED_PROXY_HOPS = {s.TRUSTED_PROXY_HOPS}")

    for level, text in checks:
        print(f"{level} {text}")
    print("\nProblems: " + (str(problems) if problems else "none"))
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
