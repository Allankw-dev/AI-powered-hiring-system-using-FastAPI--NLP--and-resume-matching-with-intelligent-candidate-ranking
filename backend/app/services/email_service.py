"""Outgoing email.

Provider choice:
  * RESEND_API_KEY set  -> Resend over HTTPS (works on hosts that block SMTP)
  * else ADMIN_EMAIL + ADMIN_EMAIL_PASSWORD set -> SMTP (Gmail by default)
Raises EmailError when nothing is configured or sending fails.
"""
import html
import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)

BRAND = "AI Hiring System"


class EmailError(Exception):
    pass


def _from_address() -> str:
    if settings.EMAIL_FROM:
        return settings.EMAIL_FROM
    if settings.RESEND_API_KEY:
        return f"{BRAND} <onboarding@resend.dev>"
    return f"{BRAND} <{settings.ADMIN_EMAIL}>"


def _send_resend(to: str, subject: str, html_body: str) -> None:
    try:
        resp = httpx.post(
            "https://api.resend.com/emails",
            headers={"Authorization": f"Bearer {settings.RESEND_API_KEY}"},
            json={"from": _from_address(), "to": [to], "subject": subject, "html": html_body},
            timeout=15.0,
        )
    except httpx.HTTPError as exc:
        raise EmailError(f"Resend request failed: {exc.__class__.__name__}") from exc
    if resp.status_code >= 300:
        raise EmailError(f"Resend rejected the email (HTTP {resp.status_code}): {resp.text[:200]}")


def _send_smtp(to: str, subject: str, html_body: str) -> None:
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = _from_address()
    msg["To"] = to
    msg.attach(MIMEText(html_body, "html"))
    try:
        if settings.SMTP_PORT == 465:
            server = smtplib.SMTP_SSL(settings.SMTP_SERVER, settings.SMTP_PORT, timeout=15)
        else:
            server = smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT, timeout=15)
            server.ehlo()
            server.starttls()
        with server:
            server.login(settings.ADMIN_EMAIL, settings.ADMIN_EMAIL_PASSWORD)
            server.sendmail(settings.ADMIN_EMAIL, to, msg.as_string())
    except (smtplib.SMTPException, OSError) as exc:
        raise EmailError(f"SMTP send failed: {exc.__class__.__name__}") from exc


def send_email(recipient_email: str, subject: str, html_body: str) -> None:
    if settings.RESEND_API_KEY:
        _send_resend(recipient_email, subject, html_body)
    elif settings.ADMIN_EMAIL and settings.ADMIN_EMAIL_PASSWORD:
        _send_smtp(recipient_email, subject, html_body)
    else:
        raise EmailError("No email provider configured (set RESEND_API_KEY or ADMIN_EMAIL/ADMIN_EMAIL_PASSWORD).")
    logger.info("Email sent (subject=%r)", subject)


def send_email_safely(recipient_email: str, subject: str, html_body: str) -> None:
    """For background tasks: never raise, just log."""
    try:
        send_email(recipient_email, subject, html_body)
    except EmailError:
        logger.exception("Background email failed (subject=%r)", subject)


def _wrap(inner: str) -> str:
    return f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <h2 style="color: #8b5cf6;">{BRAND}</h2>
        {inner}
        <hr/>
        <small style="color:#94a3b8;">{BRAND} · Powered by AI</small>
    </div>
    """


def send_reset_email(recipient_email: str, reset_link: str) -> None:
    safe_link = html.escape(reset_link, quote=True)
    body = _wrap(f"""
        <p>Hello,</p>
        <p>We received a request to reset your password.</p>
        <p>
            <a href="{safe_link}"
               style="background:#8b5cf6;color:white;padding:12px 24px;
                      border-radius:8px;text-decoration:none;display:inline-block;">
                Reset My Password
            </a>
        </p>
        <p>This link will expire in <strong>1 hour</strong>.</p>
        <p>If you did not request this, you can safely ignore this email.</p>
    """)
    send_email_safely(recipient_email, "Reset Your Password", body)


def send_otp_email(recipient_email: str, otp_code: str) -> None:
    """Raises EmailError (the caller must know if the code could not be delivered)."""
    body = _wrap(f"""
        <p>Your admin sign-in code is:</p>
        <p style="font-size:32px;letter-spacing:8px;font-weight:bold;color:#8b5cf6;">{html.escape(otp_code)}</p>
        <p>It expires in <strong>5 minutes</strong>. If you did not try to sign in, change your password.</p>
    """)
    send_email(recipient_email, "Your admin sign-in code", body)


def send_admin_email(recipient_email: str, subject: str, message_body: str) -> None:
    # The admin types plain text: escape it and keep the line breaks.
    safe = html.escape(message_body).replace("\n", "<br>")
    body = _wrap(f"""
        <div style="background:#f8fafc;padding:20px;border-radius:8px;border-left:4px solid #8b5cf6;">
            {safe}
        </div>
    """)
    send_email_safely(recipient_email, subject, body)
