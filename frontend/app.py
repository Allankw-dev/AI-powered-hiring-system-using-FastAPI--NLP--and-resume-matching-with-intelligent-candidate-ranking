import streamlit as st

from pages import home
from pages import login
from pages import sign_up
from pages import dashboard
from pages import jobs
from pages import applications
from pages import upload_resume
from pages import profile
from pages import admin_panel
from pages import forgot_password
from pages import reset_password

st.set_page_config(page_title="AI Hiring System", page_icon="🤖", layout="wide")

# ---------------------------
# GLOBAL STYLES
# ---------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;600;700;900&family=Share+Tech+Mono&family=Rajdhani:wght@400;500;600;700&display=swap');

/* ── BASE ── */
.stApp {
    background: #000000;
    background-image:
        linear-gradient(rgba(0,255,65,0.03) 1px, transparent 1px),
        linear-gradient(90deg, rgba(0,255,65,0.03) 1px, transparent 1px);
    background-size: 40px 40px;
    color: #e0ffe0;
    font-family: 'Rajdhani', sans-serif;
}

#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

.block-container {
    padding-top: 1.2rem;
    padding-bottom: 2rem;
    max-width: 1300px;
}

/* ── SIDEBAR ── */
section[data-testid="stSidebar"] {
    background: rgba(0, 0, 0, 0.95);
    border-right: 1px solid rgba(0,255,65,0.2);
}

/* ── BUTTONS ── */
div.stButton > button {
    background: rgba(0,255,65,0.08) !important;
    border: 1px solid rgba(0,255,65,0.5) !important;
    color: #00ff41 !important;
    border-radius: 8px !important;
    font-family: 'Rajdhani', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.95rem !important;
    padding: 0.6rem 1.2rem !important;
    letter-spacing: 1px !important;
    transition: all 0.3s ease !important;
    text-transform: uppercase !important;
    box-shadow: 0 0 10px rgba(0,255,65,0.1) !important;
}

div.stButton > button:hover {
    background: rgba(0,255,65,0.18) !important;
    box-shadow: 0 0 20px rgba(0,255,65,0.4), inset 0 0 10px rgba(0,255,65,0.1) !important;
    border-color: #00ff41 !important;
}

/* ── INPUTS ── */
div[data-testid="stTextInput"] input,
div[data-testid="stTextArea"] textarea,
div[data-testid="stNumberInput"] input {
    background: rgba(0,255,65,0.04) !important;
    border: 1px solid rgba(0,255,65,0.25) !important;
    border-radius: 8px !important;
    color: #e0ffe0 !important;
    font-family: 'Share Tech Mono', monospace !important;
    font-size: 0.9rem !important;
}

div[data-testid="stTextInput"] input:focus,
div[data-testid="stTextArea"] textarea:focus {
    border-color: #00ff41 !important;
    box-shadow: 0 0 12px rgba(0,255,65,0.3) !important;
}

/* ── LABELS ── */
label, .stTextInput label, .stTextArea label {
    color: #00ff41 !important;
    font-family: 'Rajdhani', sans-serif !important;
    font-weight: 600 !important;
    letter-spacing: 1px !important;
    text-transform: uppercase !important;
    font-size: 0.8rem !important;
}

/* ── TABS ── */
div[data-testid="stTabs"] button {
    color: rgba(0,255,65,0.6) !important;
    font-family: 'Rajdhani', sans-serif !important;
    font-weight: 700 !important;
    letter-spacing: 1px !important;
    text-transform: uppercase !important;
    border-bottom: 2px solid transparent !important;
}

div[data-testid="stTabs"] button[aria-selected="true"] {
    color: #00ff41 !important;
    border-bottom: 2px solid #00ff41 !important;
    text-shadow: 0 0 10px rgba(0,255,65,0.6) !important;
}

/* ── DATAFRAME ── */
div[data-testid="stDataFrame"] {
    border: 1px solid rgba(0,255,65,0.2) !important;
    border-radius: 8px !important;
}

/* ── SELECTBOX ── */
div[data-testid="stSelectbox"] > div {
    background: rgba(0,255,65,0.04) !important;
    border: 1px solid rgba(0,255,65,0.25) !important;
    border-radius: 8px !important;
    color: #e0ffe0 !important;
}

/* ── RADIO NAV ── */
div[role="radiogroup"] {
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
    margin-bottom: 10px;
}

div[role="radiogroup"] label {
    background: rgba(0,255,65,0.05);
    border: 1px solid rgba(0,255,65,0.2);
    border-radius: 8px;
    padding: 6px 14px;
    transition: all 0.2s ease;
}

div[role="radiogroup"] label:hover {
    background: rgba(0,255,65,0.12);
    border-color: rgba(0,255,65,0.5);
}

div[role="radiogroup"] label p {
    color: #00ff41 !important;
    font-family: 'Rajdhani', sans-serif !important;
    font-weight: 600 !important;
    letter-spacing: 1px !important;
    font-size: 0.85rem !important;
    text-transform: uppercase !important;
}

div[data-testid="stRadio"] > label {
    display: none;
}

/* ── ALERTS ── */
div[data-testid="stAlert"] {
    border-radius: 8px !important;
    border-left: 3px solid #00ff41 !important;
    background: rgba(0,255,65,0.06) !important;
}

/* ── DIVIDER ── */
hr {
    border-color: rgba(0,255,65,0.15) !important;
}

/* ── CUSTOM COMPONENTS ── */
.cyber-title {
    font-family: 'Orbitron', sans-serif;
    font-size: 2.4rem;
    font-weight: 900;
    color: #00ff41;
    text-shadow: 0 0 20px rgba(0,255,65,0.6), 0 0 40px rgba(0,255,65,0.3);
    letter-spacing: 3px;
    text-transform: uppercase;
    margin-bottom: 0.3rem;
}

.cyber-subtitle {
    font-family: 'Share Tech Mono', monospace;
    color: rgba(0,255,65,0.6);
    font-size: 0.9rem;
    letter-spacing: 2px;
    margin-bottom: 1.5rem;
}

.glass-card {
    background: rgba(0,255,65,0.03);
    border: 1px solid rgba(0,255,65,0.15);
    border-radius: 12px;
    padding: 1.5rem;
    backdrop-filter: blur(10px);
    box-shadow: 0 8px 32px rgba(0,0,0,0.4), inset 0 1px 0 rgba(0,255,65,0.1);
    margin-bottom: 1rem;
}

.glass-card:hover {
    border-color: rgba(0,255,65,0.3);
    box-shadow: 0 8px 32px rgba(0,0,0,0.4), 0 0 20px rgba(0,255,65,0.08), inset 0 1px 0 rgba(0,255,65,0.1);
}

.nav-bar {
    background: rgba(0,0,0,0.8);
    border: 1px solid rgba(0,255,65,0.2);
    border-radius: 12px;
    padding: 12px 18px;
    margin-bottom: 16px;
    backdrop-filter: blur(10px);
    box-shadow: 0 0 30px rgba(0,255,65,0.05);
}

.nav-label {
    font-family: 'Share Tech Mono', monospace;
    color: rgba(0,255,65,0.5);
    font-size: 0.7rem;
    letter-spacing: 3px;
    text-transform: uppercase;
    margin-bottom: 6px;
}

.status-box {
    padding: 0.7rem 1rem;
    border-radius: 8px;
    margin-bottom: 1rem;
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.85rem;
    letter-spacing: 1px;
}

.status-admin {
    background: rgba(0,255,65,0.06);
    color: #00ff41;
    border: 1px solid rgba(0,255,65,0.3);
    box-shadow: 0 0 15px rgba(0,255,65,0.1);
}

.status-candidate {
    background: rgba(0,200,255,0.06);
    color: #00c8ff;
    border: 1px solid rgba(0,200,255,0.3);
    box-shadow: 0 0 15px rgba(0,200,255,0.1);
}

.neon-divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(0,255,65,0.4), transparent);
    margin: 1rem 0;
    border: none;
}
</style>
""", unsafe_allow_html=True)

# ---------------------------
# SESSION DEFAULTS
# ---------------------------
if "token" not in st.session_state:
    st.session_state.token = None

if "role" not in st.session_state:
    st.session_state.role = None

if "user_email" not in st.session_state:
    st.session_state.user_email = None

if "page" not in st.session_state:
    st.session_state.page = "Home"

# ---------------------------
# HELPERS
# ---------------------------
def is_logged_in():
    return st.session_state.get("token") is not None

def is_admin():
    return st.session_state.get("role") == "admin"

def is_candidate():
    return st.session_state.get("role") == "candidate"

def logout():
    st.session_state.token = None
    st.session_state.role = None
    st.session_state.user_email = None
    st.session_state.page = "Home"
    st.rerun()

def route_guard(page_name: str):
    public_pages = ["Home", "Login", "Sign Up", "Forgot Password", "Reset Password"]
    candidate_pages = ["Dashboard", "Jobs", "Applications", "Upload Resume", "Profile"]
    admin_pages = ["Admin Panel"]

    if page_name in public_pages:
        return

    if page_name in candidate_pages:
        if not is_logged_in():
            st.warning("Please log in first.")
            st.session_state.page = "Login"
            st.rerun()
        if not is_candidate():
            st.error("Access denied. Candidates only.")
            st.session_state.page = "Home"
            st.rerun()

    if page_name in admin_pages:
        if not is_logged_in():
            st.warning("Please log in first.")
            st.session_state.page = "Login"
            st.rerun()
        if not is_admin():
            st.error("Access denied. Admins only.")
            st.session_state.page = "Home"
            st.rerun()

# ---------------------------
# TOP NAVIGATION
# ---------------------------
nav_pages = [
    "Home", "Login", "Sign Up", "Dashboard", "Jobs",
    "Applications", "Upload Resume", "Profile", "Admin Panel"
]

current_nav_page = st.session_state.page if st.session_state.page in nav_pages else "Home"

st.markdown('<div class="nav-bar"><div class="nav-label">// SYSTEM NAVIGATION</div>', unsafe_allow_html=True)

col_nav, col_user = st.columns([9, 1])

with col_nav:
    selected_page = st.radio(
        "Navigation",
        nav_pages,
        index=nav_pages.index(current_nav_page),
        horizontal=True,
        label_visibility="collapsed"
    )

with col_user:
    if is_logged_in():
        if st.button("⏻ EXIT"):
            logout()

st.markdown('</div>', unsafe_allow_html=True)

if st.session_state.page in nav_pages and selected_page != st.session_state.page:
    st.session_state.page = selected_page
    st.rerun()

st.markdown('<div class="neon-divider"></div>', unsafe_allow_html=True)

# ---------------------------
# LOGIN STATUS
# ---------------------------
if is_logged_in() and st.session_state.user_email:
    if is_admin():
        st.markdown(
            f'<div class="status-box status-admin">▶ ADMIN ACCESS GRANTED // {st.session_state.user_email}</div>',
            unsafe_allow_html=True
        )
    elif is_candidate():
        st.markdown(
            f'<div class="status-box status-candidate">▶ CANDIDATE SESSION ACTIVE // {st.session_state.user_email}</div>',
            unsafe_allow_html=True
        )

# ---------------------------
# ROUTING
# ---------------------------
page = st.session_state.page
route_guard(page)

if page == "Home":
    home.render()
elif page == "Login":
    login.render()
elif page == "Sign Up":
    sign_up.render()
elif page == "Dashboard":
    dashboard.render()
elif page == "Jobs":
    jobs.render()
elif page == "Applications":
    applications.render()
elif page == "Upload Resume":
    upload_resume.render()
elif page == "Profile":
    profile.render()
elif page == "Admin Panel":
    admin_panel.render()
elif page == "Forgot Password":
    forgot_password.render()
elif page == "Reset Password":
    reset_password.render()
else:
    st.session_state.page = "Home"
    st.rerun()