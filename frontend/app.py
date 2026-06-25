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
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;600;700;900&family=Exo+2:wght@300;400;600;700&display=swap');

/* ── BASE ── */
.stApp {
    background: radial-gradient(ellipse at top, #0d0221 0%, #090118 40%, #000000 100%);
    background-attachment: fixed;
    color: #e2e8f0;
    font-family: 'Exo 2', sans-serif;
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
    background: rgba(9, 1, 24, 0.97);
    border-right: 1px solid rgba(139, 92, 246, 0.2);
}

/* ── BUTTONS ── */
div.stButton > button {
    background: linear-gradient(135deg, rgba(139,92,246,0.15), rgba(59,130,246,0.15)) !important;
    border: 1px solid rgba(139,92,246,0.5) !important;
    color: #c4b5fd !important;
    border-radius: 10px !important;
    font-family: 'Exo 2', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.9rem !important;
    padding: 0.6rem 1.2rem !important;
    letter-spacing: 1px !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 0 12px rgba(139,92,246,0.2) !important;
}

div.stButton > button:hover {
    background: linear-gradient(135deg, rgba(139,92,246,0.3), rgba(59,130,246,0.3)) !important;
    box-shadow: 0 0 25px rgba(139,92,246,0.5), 0 0 50px rgba(139,92,246,0.2) !important;
    border-color: #8b5cf6 !important;
    color: #ffffff !important;
}

/* ── INPUTS ── */
div[data-testid="stTextInput"] input,
div[data-testid="stTextArea"] textarea,
div[data-testid="stNumberInput"] input {
    background: rgba(139,92,246,0.05) !important;
    border: 1px solid rgba(139,92,246,0.25) !important;
    border-radius: 10px !important;
    color: #e2e8f0 !important;
    font-family: 'Exo 2', sans-serif !important;
}

div[data-testid="stTextInput"] input:focus,
div[data-testid="stTextArea"] textarea:focus {
    border-color: #8b5cf6 !important;
    box-shadow: 0 0 15px rgba(139,92,246,0.4), 0 0 30px rgba(139,92,246,0.15) !important;
}

/* ── LABELS ── */
label {
    color: #a78bfa !important;
    font-family: 'Exo 2', sans-serif !important;
    font-weight: 600 !important;
    letter-spacing: 0.5px !important;
}

/* ── TABS ── */
div[data-testid="stTabs"] button {
    color: rgba(167,139,250,0.6) !important;
    font-family: 'Exo 2', sans-serif !important;
    font-weight: 600 !important;
}

div[data-testid="stTabs"] button[aria-selected="true"] {
    color: #a78bfa !important;
    border-bottom: 2px solid #8b5cf6 !important;
    text-shadow: 0 0 15px rgba(139,92,246,0.8) !important;
}

/* ── SELECTBOX ── */
div[data-testid="stSelectbox"] > div {
    background: rgba(139,92,246,0.05) !important;
    border: 1px solid rgba(139,92,246,0.25) !important;
    border-radius: 10px !important;
    color: #e2e8f0 !important;
}

/* ── RADIO NAV ── */
div[role="radiogroup"] {
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
    margin-bottom: 10px;
}

div[role="radiogroup"] label {
    background: rgba(139,92,246,0.06);
    border: 1px solid rgba(139,92,246,0.2);
    border-radius: 10px;
    padding: 6px 14px;
    transition: all 0.2s ease;
}

div[role="radiogroup"] label:hover {
    background: rgba(139,92,246,0.15);
    border-color: rgba(139,92,246,0.5);
    box-shadow: 0 0 12px rgba(139,92,246,0.3);
}

div[role="radiogroup"] label p {
    color: #c4b5fd !important;
    font-family: 'Exo 2', sans-serif !important;
    font-weight: 600 !important;
}

div[data-testid="stRadio"] > label {
    display: none;
}

/* ── ALERTS ── */
div[data-testid="stAlert"] {
    border-radius: 10px !important;
    border-left: 3px solid #8b5cf6 !important;
    background: rgba(139,92,246,0.08) !important;
}

/* ── DIVIDER ── */
hr {
    border-color: rgba(139,92,246,0.2) !important;
}

/* ── DATAFRAME ── */
div[data-testid="stDataFrame"] {
    border: 1px solid rgba(139,92,246,0.2) !important;
    border-radius: 10px !important;
}

/* ── CUSTOM COMPONENTS ── */
.cyber-title {
    font-family: 'Orbitron', sans-serif;
    font-size: 2.4rem;
    font-weight: 900;
    background: linear-gradient(135deg, #a78bfa, #60a5fa, #c084fc);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    text-shadow: none;
    filter: drop-shadow(0 0 20px rgba(139,92,246,0.6));
    letter-spacing: 2px;
    margin-bottom: 0.3rem;
}

.cyber-subtitle {
    color: rgba(167,139,250,0.7);
    font-size: 1rem;
    letter-spacing: 1px;
    margin-bottom: 1.5rem;
}

.glass-card {
    background: rgba(139,92,246,0.04);
    border: 1px solid rgba(139,92,246,0.18);
    border-radius: 16px;
    padding: 1.5rem;
    backdrop-filter: blur(12px);
    box-shadow: 0 8px 32px rgba(0,0,0,0.5), 0 0 20px rgba(139,92,246,0.05), inset 0 1px 0 rgba(139,92,246,0.1);
    margin-bottom: 1rem;
    transition: all 0.3s ease;
}

.glass-card:hover {
    border-color: rgba(139,92,246,0.35);
    box-shadow: 0 8px 32px rgba(0,0,0,0.5), 0 0 30px rgba(139,92,246,0.15), inset 0 1px 0 rgba(139,92,246,0.15);
}

.nav-bar {
    background: rgba(9,1,24,0.85);
    border: 1px solid rgba(139,92,246,0.25);
    border-radius: 14px;
    padding: 12px 18px;
    margin-bottom: 16px;
    backdrop-filter: blur(12px);
    box-shadow: 0 0 30px rgba(139,92,246,0.08), inset 0 1px 0 rgba(139,92,246,0.1);
}

.nav-label {
    color: rgba(167,139,250,0.5);
    font-size: 0.7rem;
    letter-spacing: 3px;
    text-transform: uppercase;
    margin-bottom: 6px;
}

.status-box {
    padding: 0.7rem 1.2rem;
    border-radius: 10px;
    margin-bottom: 1rem;
    font-size: 0.9rem;
    font-weight: 600;
}

.status-admin {
    background: rgba(139,92,246,0.1);
    color: #c4b5fd;
    border: 1px solid rgba(139,92,246,0.35);
    box-shadow: 0 0 20px rgba(139,92,246,0.15), inset 0 0 20px rgba(139,92,246,0.05);
}

.status-candidate {
    background: rgba(59,130,246,0.1);
    color: #93c5fd;
    border: 1px solid rgba(59,130,246,0.35);
    box-shadow: 0 0 20px rgba(59,130,246,0.15), inset 0 0 20px rgba(59,130,246,0.05);
}

.neon-divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(139,92,246,0.6), rgba(59,130,246,0.6), transparent);
    margin: 1rem 0;
    border: none;
    box-shadow: 0 0 10px rgba(139,92,246,0.3);
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

st.markdown('<div class="nav-bar"><div class="nav-label">Navigation</div>', unsafe_allow_html=True)

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
        if st.button("Logout"):
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
            f'<div class="status-box status-admin">🛡️ Logged in as Admin • {st.session_state.user_email}</div>',
            unsafe_allow_html=True
        )
    elif is_candidate():
        st.markdown(
            f'<div class="status-box status-candidate">👤 Logged in as Candidate • {st.session_state.user_email}</div>',
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