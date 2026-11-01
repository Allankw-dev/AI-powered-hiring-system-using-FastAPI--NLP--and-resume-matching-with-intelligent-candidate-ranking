"""Escaping helpers: use these for ANY server-provided text that goes into HTML
(``st.markdown(..., unsafe_allow_html=True)``). Streamlit does not escape for you there.
"""
import html


def esc(value) -> str:
    """Plain text -> HTML-safe text (names, emails, statuses)."""
    return html.escape(str(value if value is not None else ""), quote=True)


def esc_stored(value) -> str:
    """For text the backend stored: undo any old entity-encoding first, then escape everything,
    so a stray ``<script>`` or an old ``&amp;`` can never turn into live markup."""
    return html.escape(html.unescape(str(value if value is not None else "")), quote=True)


def plain(value) -> str:
    """Text for st.text()/st.write(): entities decoded, nothing interpreted as HTML or markdown."""
    return html.unescape(str(value if value is not None else ""))
