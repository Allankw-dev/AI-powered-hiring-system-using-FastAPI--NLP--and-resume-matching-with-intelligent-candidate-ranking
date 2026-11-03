"""Compliance regression tests: legal documents, honest marketing claims, consent defaults, licensing."""
import re
from pathlib import Path

import pytest

from app.core.legal import LEGAL_VERSION

REPO = Path(__file__).resolve().parents[2]
LEGAL = REPO / "legal"
FRONTEND = REPO / "frontend"
ALLOWED_PLACEHOLDERS = {"LEGAL_VERSION", "OPERATOR_NAME", "OPERATOR_LOCATION", "CONTACT_EMAIL"}


def _frontend_sources():
    return [p for p in FRONTEND.rglob("*.py") if "tests" not in p.parts and "node_modules" not in p.parts]


# ───────────── policies exist and say what the law expects ─────────────
REQUIRED = {
    "privacy-policy.md": ["Who is responsible", "What we collect", "Automated scoring", "Who can see your data", "How long we keep",
                          "Your rights", "Children", "Contact", "Download my data", "Delete my account", "Anthropic", "Supabase", "Render"],
    "terms-of-service.md": ["18 or older", "Acceptable use", "Fees", "Liability", "Ending your account", "governed by the laws of Kenya", "free"],
    "cookie-policy.md": ["_streamlit_xsrf", "strictly necessary", "No analytics", "Google Fonts"],
    "refund-policy.md": ["free", "nothing to refund", "before"],
}


@pytest.mark.parametrize("name,needles", REQUIRED.items())
def test_legal_documents_exist_and_cover_the_essentials(name, needles):
    text = (LEGAL / name).read_text(encoding="utf-8")
    missing = [n for n in needles if n.lower() not in text.lower()]
    assert not missing, f"{name} is missing: {missing}"


@pytest.mark.parametrize("name", REQUIRED)
def test_legal_documents_only_use_known_placeholders_and_carry_the_version(name):
    text = (LEGAL / name).read_text(encoding="utf-8")
    assert set(re.findall(r"\{\{(\w+)\}\}", text)) <= ALLOWED_PLACEHOLDERS
    assert "{{LEGAL_VERSION}}" in text and "{{CONTACT_EMAIL}}" in text  # dated, and says how to reach the operator


def test_frontend_and_backend_agree_on_the_legal_version():
    match = re.search(r'LEGAL_VERSION = "([^"]+)"', (FRONTEND / "legal_pages.py").read_text())
    assert match and match.group(1) == LEGAL_VERSION


def test_every_data_processor_in_the_code_is_named_in_the_privacy_policy():
    policy = (LEGAL / "privacy-policy.md").read_text().lower()
    code = "\n".join(p.read_text() for p in (REPO / "backend" / "app").rglob("*.py")).lower()
    expected = {"api.anthropic.com": "anthropic", "generativelanguage.googleapis.com": "gemini", "api.resend.com": "resend", "smtp": "gmail"}
    for host, name in expected.items():
        if host in code:
            assert name in policy, f"the code talks to {host} but the privacy policy does not mention {name}"
    for host in set(re.findall(r"https://([a-z0-9.-]+\.[a-z]{2,})", "\n".join(p.read_text() for p in _frontend_sources()))):
        if host.endswith("googleapis.com") or host.endswith("gstatic.com"):
            assert "google fonts" in policy


# ───────────── marketing claims we cannot prove must stay out ─────────────
BANNED_CLAIMS = [
    r"98\s*%", r"\b10x\b", r"500\+", r"bit secure", r"256-bit", r"free forever", r"hire better forever", r"understands context",
    r"verif\w* resume authenticity", r"high precision", r"\bmatch accuracy\b", r"military", r"100% secure", r"guaranteed",
    r"data-driven hiring decisions", r"instantly", r"24/7",
]


def test_no_unsupported_marketing_claims_in_the_frontend_or_chat_prompt():
    sources = _frontend_sources() + [REPO / "backend" / "app" / "services" / "chat_service.py"]
    hits = []
    for path in sources:
        text = path.read_text(encoding="utf-8")
        for pattern in BANNED_CLAIMS:
            for m in re.finditer(pattern, text, flags=re.IGNORECASE):
                hits.append(f"{path.relative_to(REPO)}: '{m.group(0)}'")
    assert not hits, "claims that cannot be backed up: " + "; ".join(hits)


def test_the_home_page_stats_are_facts_you_can_check():
    from app.services import ai_engine
    home = (FRONTEND / "pages" / "home.py").read_text()
    skills = next(v for n, v in vars(ai_engine).items() if n.isupper() and isinstance(v, dict) and len(v) > 50)
    assert f'stat-number">{len(skills)}<' in home, "the 'skills recognised' number no longer matches the skills list"


# ───────────── forms, nudges and dark patterns ─────────────
def test_signup_checkboxes_start_unticked_and_are_separate():
    src = (FRONTEND / "pages" / "sign_up.py").read_text()
    boxes = re.findall(r"st\.checkbox\([^\n]*\)", src)
    assert len(boxes) == 2 and all("value=False" in b for b in boxes)
    assert "Terms of Service" in boxes[0] and "18" in boxes[1]
    assert "prog-step" not in src  # no fake "almost done" progress bar on a one-step form


def test_chat_widget_has_no_fake_notification_badge_and_says_it_is_an_ai():
    src = (FRONTEND / "chat_widget.py").read_text()
    assert "ai-notif" not in src and "aiNotifDot" not in src
    assert "AI" in src and "do not share personal details" in src


def test_account_deletion_and_data_download_are_easy_to_find_on_the_profile_page():
    src = (FRONTEND / "pages" / "profile.py").read_text()
    assert "Delete my account" in src and "Download my data" in src and "Privacy & data" in src


def test_cookie_notice_is_informational_with_balanced_buttons():
    src = (FRONTEND / "legal_pages.py").read_text()
    assert "no tracking or advertising cookies" in src and '"Got it"' in src and "Read the cookie policy" in src


def test_cookie_config_matches_the_policy():
    """If analytics/tracking tools are ever added, the cookie policy and the notice must change first."""
    code = "\n".join(p.read_text() for p in _frontend_sources()).lower()
    for tracker in ("googletagmanager", "google-analytics", "gtag(", "fbq(", "hotjar", "segment.com", "mixpanel", "plausible", "posthog"):
        assert tracker not in code, f"{tracker} found: update the cookie policy and ask for consent before adding trackers"


# ───────────── accessibility basics ─────────────
def test_images_have_alt_text_and_decorative_canvas_is_hidden_from_screen_readers():
    for path in _frontend_sources():
        for tag in re.findall(r"<img\b[^>]*>", path.read_text()):
            assert "alt=" in tag, f"{path.name}: image without alt text: {tag[:60]}"
    assert 'aria-hidden="true"' in (FRONTEND / "pages" / "home.py").read_text()


def test_embedded_pages_declare_a_language_and_title():
    home = (FRONTEND / "pages" / "home.py").read_text()
    assert '<html lang="en">' in home and "<title>" in home
    assert '<html lang="en">' in (FRONTEND / "chat_widget.py").read_text()


def test_keyboard_focus_is_never_hidden_without_a_replacement():
    css = (FRONTEND / "app.py").read_text()
    assert ":focus-visible" in css and "prefers-reduced-motion" in css


# ───────────── licensing ─────────────
def test_notices_list_the_fonts_in_use_and_every_backend_dependency():
    notices = (REPO / "THIRD_PARTY_NOTICES.md").read_text()
    fonts_used = set(re.findall(r"family=([A-Za-z0-9+]+)", (FRONTEND / "app.py").read_text()))
    for font in fonts_used:
        assert font.replace("+", " ") in notices, f"font {font} is used but not listed in THIRD_PARTY_NOTICES.md"
    assert "SIL Open Font License" in notices
    for dep in re.findall(r"^([A-Za-z][A-Za-z0-9_.-]+)", (REPO / "backend" / "requirements.txt").read_text(), flags=re.M):
        assert dep.lower() in notices.lower(), f"{dep} missing from THIRD_PARTY_NOTICES.md"


def test_no_image_or_font_files_are_shipped_without_a_licence_entry():
    shipped = [p for p in REPO.rglob("*") if p.suffix.lower() in {".png", ".jpg", ".jpeg", ".gif", ".svg", ".ico", ".ttf", ".woff", ".woff2"}
               and ".git" not in p.parts and "node_modules" not in p.parts]
    assert shipped == [], f"add a licence entry to THIRD_PARTY_NOTICES.md for: {shipped}"


def test_business_details_are_available_in_the_app():
    src = (FRONTEND / "legal_pages.py").read_text()
    assert "OPERATOR_NAME" in src and "CONTACT_EMAIL" in src and "render_contact" in src and "Nairobi, Kenya" in src
