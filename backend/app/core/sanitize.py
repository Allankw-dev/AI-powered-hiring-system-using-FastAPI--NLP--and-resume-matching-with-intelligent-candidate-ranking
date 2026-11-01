"""Input sanitising for free-text form fields.

Rule of the project: store *plain text* (no HTML, no control characters) and
escape it again wherever it is rendered. This module is the "strip" half.
"""
import html
import re

import bleach

# C0/C1 control characters except tab (\x09) and newline (\x0a).
_CONTROL_CHARS = re.compile(r"[\x00-\x08\x0b-\x1f\x7f-\x9f]")
# Characters that can reorder or hide text (bidi overrides, zero-width).
_INVISIBLE = re.compile(r"[\u200b-\u200f\u202a-\u202e\u2066-\u2069\ufeff]")


def strip_html(text: str) -> str:
    """Remove every HTML tag and return plain text (entities decoded)."""
    return html.unescape(bleach.clean(text, tags=[], attributes={}, strip=True))


def clean_line(value: str) -> str:
    """Single-line field (names, titles, email subjects): no tags, no control chars, no newlines."""
    value = strip_html(value or "")
    value = _CONTROL_CHARS.sub("", value)
    value = _INVISIBLE.sub("", value)
    return re.sub(r"\s+", " ", value).strip()


def clean_text(value: str) -> str:
    """Multi-line field (descriptions, messages): no tags, no control chars, newlines kept."""
    value = strip_html(value or "")
    value = _CONTROL_CHARS.sub("", value.replace("\r\n", "\n").replace("\r", "\n"))
    return _INVISIBLE.sub("", value).strip()


def strip_controls(value: str) -> str:
    """Keep the text exactly as typed (it is escaped when rendered) but drop control characters."""
    value = (value or "").replace("\r\n", "\n").replace("\r", "\n")
    return _INVISIBLE.sub("", _CONTROL_CHARS.sub("", value)).strip()
