"""Hira, the in-app assistant.

Provider order: Claude (ANTHROPIC_API_KEY) -> Gemini (GEMINI_API_KEY).
Keys travel in headers (never in the URL) and a daily cap protects your quota.
"""
import asyncio
import logging
import threading
from datetime import date

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are Hira, the assistant of an AI-powered hiring platform. You help candidates and admins.

PLATFORM FACTS:
- FastAPI backend, Streamlit frontend, PostgreSQL database.
- Match score = text similarity 45%, skills 25%, experience 20%, resume verification 10%.
- Features: resume upload (PDF/TXT), job matching, resume consistency checks, admin panel, 2FA for admins.
- Consistency checks look for keyword stuffing, inconsistent dates, very short resumes and missing contact info. A flag is a prompt for a human to look closer, never proof of fraud.
- Text similarity compares the words of the resume and the job post; it does not "understand" meaning.
- The software never accepts or rejects anyone: a recruiter makes every decision.
- Candidates can download or delete all their data under Profile > Privacy & data, and can unsubscribe from application emails.
- Candidates sign up, upload resumes, apply to jobs and track applications.
- Admins post/edit/delete jobs, review top candidates, shortlist/reject, and email candidates.

RULES:
- You have NO access to any user's account, resume, scores or database. Never claim to see or change them.
- Never promise a hiring outcome. Be honest that scores are an aid, not a decision.
- Be friendly, accurate and concise (under 200 words unless more detail is needed).
- Do not ask for or encourage sharing personal details (ID numbers, phone numbers, health data) in the chat.
- Never state accuracy percentages or claim the scoring is perfect or unbiased.
- Plain text with simple **bold** only."""

UNAVAILABLE = "Chat is temporarily unavailable."
TROUBLE = "Sorry, I'm having trouble right now. Please try again!"

_lock = threading.Lock()
_usage = {"day": date.today(), "count": 0}
_per_visitor: dict[str, int] = {}
_MAX_TRACKED_VISITORS = 50_000


class ChatLimitReached(Exception):
    pass


def _take_daily_slot(visitor: str | None = None) -> None:
    """Spend one chat call from the global daily cap and from this visitor's own allowance."""
    with _lock:
        today = date.today()
        if _usage["day"] != today:
            _usage["day"], _usage["count"] = today, 0
            _per_visitor.clear()
        if _usage["count"] >= settings.CHAT_DAILY_LIMIT:
            raise ChatLimitReached
        if visitor is not None:
            used = _per_visitor.get(visitor, 0)
            if used >= settings.CHAT_PER_IP_DAILY_LIMIT:
                raise ChatLimitReached
            if used == 0 and len(_per_visitor) >= _MAX_TRACKED_VISITORS:
                raise ChatLimitReached  # table full of junk IPs: fail closed rather than grow forever
            _per_visitor[visitor] = used + 1
        _usage["count"] += 1


def _normalize_history(history: list[dict]) -> list[dict]:
    """Keep the last turns, make sure it starts with 'user' and roles alternate."""
    cleaned: list[dict] = []
    for turn in history[-12:]:
        role = "assistant" if turn["role"] == "assistant" else "user"
        if cleaned and cleaned[-1]["role"] == role:
            cleaned[-1]["content"] += "\n" + turn["content"]
        else:
            cleaned.append({"role": role, "content": turn["content"]})
    while cleaned and cleaned[0]["role"] != "user":
        cleaned.pop(0)
    return cleaned


def _check(resp: httpx.Response, provider: str) -> None:
    """Log WHY a provider rejected the request (the body never contains our key), then raise."""
    if resp.status_code >= 400:
        logger.error("%s API returned %s: %s", provider, resp.status_code, resp.text[:300])
    resp.raise_for_status()


# Temporary provider problems worth retrying (rate limit / overloaded / 5xx).
_TRANSIENT = {429, 500, 502, 503, 504, 529}
_ATTEMPTS = 3


async def _post(client: httpx.AsyncClient, provider: str, url: str, **kwargs) -> httpx.Response:
    """POST, retrying briefly on temporary errors. Real errors (400/401/403/404) are returned at once."""
    for attempt in range(1, _ATTEMPTS + 1):
        resp = await client.post(url, **kwargs)
        if resp.status_code not in _TRANSIENT or attempt == _ATTEMPTS:
            return resp
        logger.warning("%s returned %s, retrying (%s/%s)", provider, resp.status_code, attempt, _ATTEMPTS - 1)
        await asyncio.sleep(1.5 * attempt)
    return resp


async def _ask_claude(client: httpx.AsyncClient, message: str, history: list[dict]) -> str:
    messages = _normalize_history(history)
    if messages and messages[-1]["role"] == "user":
        messages[-1]["content"] += "\n" + message
    else:
        messages.append({"role": "user", "content": message})
    resp = await _post(
        client, "Claude",
        "https://api.anthropic.com/v1/messages",
        headers={
            "x-api-key": settings.ANTHROPIC_API_KEY.get_secret_value(),
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
        json={"model": settings.ANTHROPIC_MODEL, "max_tokens": 500, "system": SYSTEM_PROMPT, "messages": messages},
    )
    _check(resp, "Claude")
    blocks = resp.json().get("content", [])
    return "".join(b.get("text", "") for b in blocks if b.get("type") == "text").strip()


async def _ask_gemini(client: httpx.AsyncClient, message: str, history: list[dict]) -> str:
    contents = [
        {"role": "user" if t["role"] == "user" else "model", "parts": [{"text": t["content"]}]}
        for t in _normalize_history(history)
    ]
    contents.append({"role": "user", "parts": [{"text": message}]})
    resp = await _post(
        client, "Gemini",
        f"https://generativelanguage.googleapis.com/v1beta/models/{settings.GEMINI_MODEL}:generateContent",
        headers={"x-goog-api-key": settings.GEMINI_API_KEY.get_secret_value(), "content-type": "application/json"},
        json={
            "system_instruction": {"parts": [{"text": SYSTEM_PROMPT}]},
            "contents": contents,
            "generationConfig": {"maxOutputTokens": 500},
        },
    )
    _check(resp, "Gemini")
    return resp.json()["candidates"][0]["content"]["parts"][0]["text"].strip()


async def generate_reply(message: str, history: list[dict], visitor: str | None = None) -> str:
    providers = []
    if settings.ANTHROPIC_API_KEY:
        providers.append(("Claude", _ask_claude))
    if settings.GEMINI_API_KEY:
        providers.append(("Gemini", _ask_gemini))
    if not providers:
        return UNAVAILABLE

    _take_daily_slot(visitor)  # may raise ChatLimitReached

    async with httpx.AsyncClient(timeout=30.0) as client:
        for name, ask in providers:
            try:
                reply = await ask(client, message, history)
                if reply:
                    return reply
            except (httpx.HTTPError, KeyError, IndexError, ValueError) as exc:
                logger.warning("Chat provider %s failed: %s", name, exc)
    return TROUBLE
