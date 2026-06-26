import requests
import streamlit as st
from api import login


def render():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;600;700;900&family=Exo+2:wght@300;400;600;700&display=swap');

    .login-wrapper {
        max-width: 480px;
        margin: 0 auto;
    }

    .login-card {
        background: rgba(139,92,246,0.04);
        border: 1px solid rgba(139,92,246,0.2);
        border-radius: 24px;
        padding: 40px 36px;
        position: relative;
        overflow: hidden;
        box-shadow: 0 0 60px rgba(139,92,246,0.08), 0 20px 40px rgba(0,0,0,0.4);
    }

    .login-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 2px;
        background: linear-gradient(90deg, transparent, #8b5cf6, #3b82f6, transparent);
        box-shadow: 0 0 15px rgba(139,92,246,0.6);
    }

    .login-card::after {
        content: '';
        position: absolute;
        top: -100px;
        right: -100px;
        width: 300px;
        height: 300px;
        background: radial-gradient(circle, rgba(139,92,246,0.08) 0%, transparent 70%);
        border-radius: 50%;
        pointer-events: none;
    }

    .login-icon {
        font-size: 40px;
        text-align: center;
        margin-bottom: 16px;
        filter: drop-shadow(0 0 15px rgba(139,92,246,0.7));
    }

    .login-title {
        font-family: 'Orbitron', sans-serif;
        font-size: 1.8rem;
        font-weight: 900;
        text-align: center;
        background: linear-gradient(90deg, #a78bfa, #60a5fa);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        filter: drop-shadow(0 0 15px rgba(139,92,246,0.5));
        letter-spacing: 2px;
        margin-bottom: 8px;
    }

    .login-subtitle {
        font-family: 'Exo 2', sans-serif;
        text-align: center;
        color: #475569;
        font-size: 14px;
        letter-spacing: 1px;
        margin-bottom: 28px;
    }

    .neon-divider {
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(139,92,246,0.4), transparent);
        margin: 24px 0;
        border: none;
    }

    .login-footer {
        font-family: 'Exo 2', sans-serif;
        text-align: center;
        color: #334155;
        font-size: 12px;
        letter-spacing: 1px;
        margin-top: 20px;
        text-transform: uppercase;
    }
    </style>
    """, unsafe_allow_html=True)

    # Center the login card
    _, center, _ = st.columns([1, 2, 1])

    with center:
        st.markdown("""
        <div class="login-card">
            <div class="login-icon">🔐</div>
            <div class="login-title">ACCESS PORTAL</div>
            <div class="login-subtitle">// Enter your credentials to continue</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        with st.form("login_form"):
            email = st.text_input("📧  Email Address")
            password = st.text_input("🔑  Password", type="password")
            submitted = st.form_submit_button("⚡ LOGIN", use_container_width=True)

        if submitted:
            if not email or not password:
                st.warning("Please enter both email and password.")
            else:
                try:
                    with st.spinner("Authenticating... please wait"):
                        response = login(email, password)

                    if response.status_code == 200:
                        data = response.json()
                        st.session_state["token"] = data.get("access_token")
                        st.session_state["role"] = data.get("role", "candidate")
                        st.session_state["user_email"] = email
                        st.success("✅ Access granted. Redirecting...")
                        st.rerun()
                    else:
                        try:
                            st.error(response.json().get("detail", "Login failed."))
                        except Exception:
                            st.error(response.text if response.text else "Login failed.")

                except requests.exceptions.Timeout:
                    st.warning("⏳ Server is waking up — please try again in 30 seconds.")

                except requests.exceptions.ConnectionError:
                    st.error("❌ Could not connect to backend.")

                except Exception as e:
                    st.error(f"Unexpected error: {str(e)}")

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

        st.markdown('<div class="login-footer">// SECURE CONNECTION ESTABLISHED</div>', unsafe_allow_html=True)