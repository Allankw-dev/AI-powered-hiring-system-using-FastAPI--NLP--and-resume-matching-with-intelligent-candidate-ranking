import streamlit as st
from api import sign_up


def render():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;600;700;900&family=Exo+2:wght@300;400;600;700&display=swap');

    .signup-card {
        background: rgba(139,92,246,0.04);
        border: 1px solid rgba(139,92,246,0.2);
        border-radius: 24px;
        padding: 40px 36px;
        position: relative;
        overflow: hidden;
        box-shadow: 0 0 60px rgba(139,92,246,0.08), 0 20px 40px rgba(0,0,0,0.4);
    }

    .signup-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 2px;
        background: linear-gradient(90deg, transparent, #8b5cf6, #3b82f6, transparent);
        box-shadow: 0 0 15px rgba(139,92,246,0.6);
    }

    .signup-card::after {
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

    .signup-icon {
        font-size: 40px;
        text-align: center;
        margin-bottom: 16px;
        filter: drop-shadow(0 0 15px rgba(139,92,246,0.7));
    }

    .signup-title {
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

    .signup-subtitle {
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

    .signup-footer {
        font-family: 'Exo 2', sans-serif;
        text-align: center;
        color: #334155;
        font-size: 12px;
        letter-spacing: 1px;
        margin-top: 20px;
        text-transform: uppercase;
    }

    .step-indicator {
        display: flex;
        justify-content: center;
        gap: 8px;
        margin-bottom: 24px;
    }

    .step-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: rgba(139,92,246,0.3);
        border: 1px solid rgba(139,92,246,0.4);
    }

    .step-dot.active {
        background: #8b5cf6;
        box-shadow: 0 0 10px rgba(139,92,246,0.8);
    }
    </style>
    """, unsafe_allow_html=True)

    _, center, _ = st.columns([1, 2, 1])

    with center:
        st.markdown("""
        <div class="signup-card">
            <div class="signup-icon">🚀</div>
            <div class="signup-title">JOIN THE SYSTEM</div>
            <div class="signup-subtitle">// Create your account to get started</div>
            <div class="step-indicator">
                <div class="step-dot active"></div>
                <div class="step-dot active"></div>
                <div class="step-dot active"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        with st.form("signup_form"):
            full_name = st.text_input("👤  Full Name")
            email = st.text_input("📧  Email Address")

            col1, col2 = st.columns(2)
            with col1:
                password = st.text_input("🔑  Password", type="password")
            with col2:
                confirm_password = st.text_input("🔑  Confirm Password", type="password")

            sex = st.selectbox("⚧  Gender", ["Male", "Female", "Other"])

            submitted = st.form_submit_button("⚡ CREATE ACCOUNT", use_container_width=True)

        if submitted:
            if not full_name or not email or not password or not confirm_password:
                st.warning("⚠️ Please fill in all fields.")
            elif password != confirm_password:
                st.error("❌ Passwords do not match.")
            else:
                with st.spinner("Creating your account... please wait"):
                    response = sign_up(full_name, email, password, sex)

                if response.status_code in [200, 201]:
                    st.success("✅ Account created! You can now log in.")
                    st.balloons()
                else:
                    try:
                        st.error(response.json().get("detail", "Sign up failed."))
                    except Exception:
                        st.error("Sign up failed.")

        st.markdown('<div class="neon-divider"></div>', unsafe_allow_html=True)

        if st.button("🔐 Already have an account? Login", use_container_width=True):
            st.session_state.page = "Login"
            st.rerun()

        st.markdown('<div class="signup-footer">// SECURE ENCRYPTED REGISTRATION</div>', unsafe_allow_html=True)