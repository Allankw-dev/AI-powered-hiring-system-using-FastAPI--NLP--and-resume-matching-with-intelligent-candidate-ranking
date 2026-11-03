"""Legal pages, footer, cookie notice, business details and the unsubscribe page.

The legal texts live in /legal/*.md at the repo root (readable on GitHub too). They contain
{{PLACEHOLDERS}} that are filled in here. Keep LEGAL_VERSION equal to backend/app/core/legal.py
(a test checks that).
"""
import re
from pathlib import Path

import requests
import streamlit as st

LEGAL_VERSION = "2026-11-01"
LEGAL_DIR = Path(__file__).resolve().parents[1] / "legal"
LEGAL_PAGES = {
    "Privacy Policy": "privacy-policy.md",
    "Terms of Service": "terms-of-service.md",
    "Cookie Policy": "cookie-policy.md",
    "Refund Policy": "refund-policy.md",
}
# Pages anybody may open without signing in (used by the route guard in app.py).
PUBLIC_EXTRA_PAGES = [*LEGAL_PAGES, "Contact", "Unsubscribe"]
GITHUB_PROFILE = "https://github.com/Allankw-dev"


def _secret(name: str, default: str = "") -> str:
    try:
        return str(st.secrets.get(name, default) or default)
    except Exception:  # no secrets file (local development)
        return default


def operator() -> dict:
    """Who runs the service. Set OPERATOR_NAME / OPERATOR_LOCATION / CONTACT_EMAIL in the Streamlit secrets."""
    email = _secret("CONTACT_EMAIL")
    return {
        "name": _secret("OPERATOR_NAME", "Allan Kamau"),
        "location": _secret("OPERATOR_LOCATION", "Nairobi, Kenya"),
        "email": email,
        # Without an email address we still give people a real way to reach us.
        "email_or_fallback": email or f"the contact details on our GitHub profile ({GITHUB_PROFILE})",
    }


def _fill(text: str) -> str:
    op = operator()
    text = (text.replace("{{LEGAL_VERSION}}", LEGAL_VERSION)
                .replace("{{OPERATOR_NAME}}", op["name"])
                .replace("{{OPERATOR_LOCATION}}", op["location"])
                .replace("{{CONTACT_EMAIL}}", op["email_or_fallback"]))
    # In-app view: the footer buttons do the navigating, so turn "[Cookie Policy](?nav=…)" into plain bold text.
    return re.sub(r"\[([^\]]+)\]\(\?nav=[^)]+\)", r"**\1**", text)


def _go(page: str):
    st.session_state.page = page
    st.rerun()


def render_legal(page: str):
    path = LEGAL_DIR / LEGAL_PAGES[page]
    st.markdown('<div class="legal-doc">', unsafe_allow_html=True)
    if path.is_file():
        st.markdown(_fill(path.read_text(encoding="utf-8")))
    else:
        st.error("This document could not be loaded. Please contact us.")
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("---")
    if st.button("← Back to home", key="legal_back"):
        _go("Home")
    cols = st.columns(len(LEGAL_PAGES))
    for col, name in zip(cols, LEGAL_PAGES):
        if col.button(name, key=f"legal_other_{name}", use_container_width=True, disabled=(name == page)):
            _go(name)


def render_contact():
    op = operator()
    st.markdown("## Contact and business details")
    st.markdown(f"""
**Service:** AI Hiring System (a free resume-screening and ranking tool)
**Operated by:** {op['name']} (an individual, running this as an independent project)
**Location:** {op['location']}
**Email (support and privacy requests):** {op['email'] or 'not published yet; please use the GitHub profile below'}
**Project page:** [{GITHUB_PROFILE}]({GITHUB_PROFILE})

**Privacy requests:** you can download or delete your own data yourself under **Profile → Privacy & data**.
For anything else (correction, objection, human review of a score, a complaint) write to the contact above.
""")
    st.caption(f"Legal texts version {LEGAL_VERSION}")
    if st.button("← Back to home", key="contact_back"):
        _go("Home")


def render_footer():
    """Legal links on every page, plus who is behind the service."""
    op = operator()
    st.markdown('<div class="neon-divider"></div>', unsafe_allow_html=True)
    cols = st.columns(5)
    for col, name in zip(cols, [*LEGAL_PAGES, "Contact"]):
        if col.button(name, key=f"footer_{name}", use_container_width=True):
            _go(name)
    contact = f" · {op['email']}" if op["email"] else ""
    st.markdown(
        f'<div class="legal-footer">AI Hiring System is operated by {op["name"]}, {op["location"]}{contact}. '
        "Free to use. Candidates must be 18 or older.</div>",
        unsafe_allow_html=True,
    )


def render_cookie_notice():
    """Information bar. There are no optional cookies, so there is nothing to opt in or out of;
    the two buttons are equally prominent. If tracking is ever added this MUST become an opt-in."""
    if st.session_state.get("cookie_notice_ok"):
        return
    with st.container(border=True):
        st.markdown(
            "**Cookies:** this site uses one security cookie that it needs in order to work. "
            "There are no tracking or advertising cookies."
        )
        c1, c2, _ = st.columns([1, 2, 6])
        if c1.button("Got it", key="cookie_ok"):
            st.session_state.cookie_notice_ok = True
            st.rerun()
        if c2.button("Read the cookie policy", key="cookie_read"):
            st.session_state.cookie_notice_ok = True
            _go("Cookie Policy")


def render_unsubscribe(api_base_url: str):
    token = st.session_state.get("unsubscribe_token", "")
    st.markdown("## Unsubscribe from application emails")
    if st.button("← Back to home", key="unsub_back"):
        _go("Home")
    if not token:
        st.info("This page needs the link from the bottom of one of our emails.")
        return
    st.write("Confirm below and we will stop sending you application emails (updates about jobs you applied for). "
             "You will still receive security emails such as password resets.")
    if st.session_state.get("unsubscribe_done"):
        st.success(st.session_state.unsubscribe_done)
        return
    if st.button("Yes, unsubscribe me", key="unsub_confirm"):
        try:
            r = requests.post(f"{api_base_url}/unsubscribe/{token}", timeout=30)
        except requests.RequestException:
            st.error("Could not reach the server. Please try again in a moment.")
            return
        if r.status_code == 200:
            st.session_state.unsubscribe_done = f"Done. {r.json().get('email', 'Your address')} will not receive these emails any more."
            st.rerun()
        else:
            try:
                detail = r.json().get("detail", "Something went wrong.")
            except ValueError:
                detail = "Something went wrong."
            st.error(detail)
