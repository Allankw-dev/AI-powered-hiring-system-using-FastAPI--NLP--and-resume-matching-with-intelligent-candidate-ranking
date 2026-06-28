import requests
import streamlit as st
from api import login


def render():
    if st.session_state.get("token"):
        role = st.session_state.get("role", "candidate")
        if role == "admin":
            st.session_state["page"] = "Admin Panel"
        else:
            st.session_state["page"] = "Dashboard"
        st.rerun()

    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;600;700;900&family=Exo+2:wght@300;400;600;700&display=swap');

    .stApp {
        background: #000510 !important;
        background-image:
            radial-gradient(ellipse at 20% 50%, rgba(120,40,200,0.15) 0%, transparent 50%),
            radial-gradient(ellipse at 80% 20%, rgba(40,80,200,0.12) 0%, transparent 45%) !important;
    }

    .login-card {
        background: rgba(5, 8, 25, 0.88);
        border: 1px solid rgba(139,92,246,0.25);
        border-radius: 20px;
        padding: 40px 38px;
        position: relative;
        overflow: hidden;
        box-shadow: 0 0 40px rgba(139,92,246,0.25), 0 0 80px rgba(139,92,246,0.08);
        backdrop-filter: blur(24px);
        margin-bottom: 20px;
    }

    .login-card::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 1px;
        background: linear-gradient(90deg, transparent, #8b5cf6, #60a5fa, #c084fc, transparent);
        box-shadow: 0 0 15px rgba(139,92,246,0.6);
    }

    .corner-tl, .corner-tr, .corner-bl, .corner-br {
        position: absolute;
        width: 16px; height: 16px;
        border-color: rgba(139,92,246,0.5);
        border-style: solid;
    }
    .corner-tl { top: 10px; left: 10px; border-width: 1.5px 0 0 1.5px; }
    .corner-tr { top: 10px; right: 10px; border-width: 1.5px 1.5px 0 0; }
    .corner-bl { bottom: 10px; left: 10px; border-width: 0 0 1.5px 1.5px; }
    .corner-br { bottom: 10px; right: 10px; border-width: 0 1.5px 1.5px 0; }

    .login-icon {
        font-size: 44px;
        text-align: center;
        margin-bottom: 12px;
        filter: drop-shadow(0 0 15px rgba(139,92,246,0.7));
    }

    .login-title {
        font-family: 'Orbitron', sans-serif;
        font-size: 1.9rem;
        font-weight: 900;
        text-align: center;
        background: linear-gradient(90deg, #a78bfa, #60a5fa, #c084fc);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        filter: drop-shadow(0 0 12px rgba(139,92,246,0.5));
        letter-spacing: 4px;
        margin-bottom: 6px;
    }

    .login-subtitle {
        font-family: 'Exo 2', sans-serif;
        text-align: center;
        color: rgba(100,116,139,0.7);
        font-size: 11px;
        letter-spacing: 2px;
        margin-bottom: 30px;
        text-transform: uppercase;
    }

    .brand-bar {
        text-align: center;
        margin-bottom: 20px;
    }

    .brand-name {
        font-family: 'Orbitron', sans-serif;
        font-size: 13px;
        letter-spacing: 6px;
        color: rgba(167,139,250,0.6);
        text-transform: uppercase;
    }

    .brand-tagline {
        font-family: 'Exo 2', sans-serif;
        font-size: 10px;
        letter-spacing: 3px;
        color: rgba(100,116,139,0.5);
        text-transform: uppercase;
        margin-top: 4px;
    }

    .neon-divider {
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(139,92,246,0.3), transparent);
        margin: 20px 0;
        border: none;
    }

    .footer-text {
        font-family: 'Exo 2', sans-serif;
        text-align: center;
        color: rgba(51,65,85,0.9);
        font-size: 9px;
        letter-spacing: 2px;
        margin-top: 18px;
        text-transform: uppercase;
    }

    .city-bg {
        position: fixed;
        bottom: 0; left: 0; right: 0;
        height: 45%;
        background:
            linear-gradient(to top, rgba(139,92,246,0.04), transparent),
            repeating-linear-gradient(
                90deg,
                rgba(18,8,45,0.95) 0px,
                rgba(18,8,45,0.95) 24px,
                rgba(28,12,60,0.95) 24px,
                rgba(28,12,60,0.95) 28px
            );
        pointer-events: none;
        z-index: 0;
    }
    </style>

    <div class="city-bg"></div>
    """, unsafe_allow_html=True)

    _, center, _ = st.columns([1, 2, 1])

    with center:
        st.markdown("""
        <div class="brand-bar">
            <div class="brand-name">AI Hiring System</div>
            <div class="brand-tagline">// Next-Gen Recruitment Platform</div>
        </div>

        <div class="login-card">
            <div class="corner-tl"></div>
            <div class="corner-tr"></div>
            <div class="corner-bl"></div>
            <div class="corner-br"></div>
            <div class="login-icon">🔐</div>
            <div class="login-title">LOG IN</div>
            <div class="login-subtitle">// access your account</div>
        </div>
        """, unsafe_allow_html=True)

        with st.form("login_form"):
            email = st.text_input("📧 Email")
            password = st.text_input("🔑 Password", type="password")
            submitted = st.form_submit_button("⚡ LOG IN", use_container_width=True)

        if submitted:
            if not email or not password:
                st.warning("Please enter both email and password.")
            else:
                try:
                    with st.spinner("Authenticating..."):
                        response = login(email, password)
                    if response.status_code == 200:
                        data = response.json()
                        st.session_state["token"] = data.get("access_token")
                        st.session_state["role"] = data.get("role", "candidate")
                        st.session_state["user_email"] = email
                        role = data.get("role", "candidate")
                        if role == "admin":
                            st.session_state["page"] = "Admin Panel"
                        else:
                            st.session_state["page"] = "Dashboard"
                        st.success("✅ Access granted!")
                        st.balloons()
                        st.rerun()
     
                    else:
                        try:
                            st.error(response.json().get("detail", "Login failed."))
                        except Exception:
                            st.error("Login failed.")

                except requests.exceptions.Timeout:
                    st.warning("⏳ Server waking up — try again in 30 seconds.")
                except requests.exceptions.ConnectionError:
                    st.error("❌ Could not connect to backend.")
                except Exception as e:
                    st.error(f"Error: {str(e)}")

        st.markdown('<div class="neon-divider"></div>', unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔁 Forgot Password?", use_container_width=True):
                st.session_state.page = "Forgot Password"
                st.rerun()
        with col2:
            if st.button("✨ Create Account", use_container_width=True):
                st.session_state.page = "Sign Up"
                st.rerun()

        st.markdown('<div class="footer-text">// 256-bit encrypted · secure connection</div>', unsafe_allow_html=True)