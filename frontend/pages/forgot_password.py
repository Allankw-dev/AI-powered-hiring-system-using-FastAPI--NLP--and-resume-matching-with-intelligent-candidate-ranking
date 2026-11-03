import streamlit as st
from api import forgot_password


def render():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;600;700;900&family=Exo+2:wght@300;400;600;700&display=swap');

    .stApp {
        background: #000510 !important;
        background-image:
            radial-gradient(ellipse at 20% 50%, rgba(120,40,200,0.15) 0%, transparent 50%),
            radial-gradient(ellipse at 80% 20%, rgba(40,80,200,0.12) 0%, transparent 45%) !important;
    }

    .city-bg {
        position:fixed; bottom:0; left:0; right:0; height:45%;
        background: linear-gradient(to top, rgba(139,92,246,.04), transparent),
            repeating-linear-gradient(90deg, rgba(18,8,45,.95) 0px, rgba(18,8,45,.95) 24px, rgba(28,12,60,.95) 24px, rgba(28,12,60,.95) 28px);
        pointer-events:none; z-index:0;
    }

    .forgot-card {
        background: rgba(5, 8, 25, 0.88);
        border: 1px solid rgba(139,92,246,0.25);
        border-radius: 20px; padding: 40px 38px;
        position: relative; overflow: hidden;
        box-shadow: 0 0 40px rgba(139,92,246,0.25), 0 0 80px rgba(139,92,246,0.08);
        backdrop-filter: blur(24px); margin-bottom: 20px;
    }

    .forgot-card::before {
        content: ''; position: absolute; top: 0; left: 0; right: 0; height: 1px;
        background: linear-gradient(90deg, transparent, #8b5cf6, #60a5fa, #c084fc, transparent);
        box-shadow: 0 0 15px rgba(139,92,246,0.6);
    }

    .corner-tl, .corner-tr, .corner-bl, .corner-br {
        position: absolute; width: 16px; height: 16px;
        border-color: rgba(139,92,246,0.5); border-style: solid;
    }
    .corner-tl { top: 10px; left: 10px; border-width: 1.5px 0 0 1.5px; }
    .corner-tr { top: 10px; right: 10px; border-width: 1.5px 1.5px 0 0; }
    .corner-bl { bottom: 10px; left: 10px; border-width: 0 0 1.5px 1.5px; }
    .corner-br { bottom: 10px; right: 10px; border-width: 0 1.5px 1.5px 0; }

    .forgot-icon { font-size: 44px; text-align: center; margin-bottom: 12px; filter: drop-shadow(0 0 15px rgba(139,92,246,0.7)); }
    .forgot-title {
        font-family: 'Orbitron', sans-serif; font-size: 1.7rem; font-weight: 900;
        text-align: center; background: linear-gradient(90deg, #a78bfa, #60a5fa, #c084fc);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        filter: drop-shadow(0 0 12px rgba(139,92,246,0.5));
        letter-spacing: 3px; margin-bottom: 6px;
    }
    .forgot-subtitle {
        font-family: 'Exo 2', sans-serif; text-align: center;
        color: rgba(100,116,139,0.7); font-size: 11px;
        letter-spacing: 2px; margin-bottom: 28px; text-transform: uppercase;
    }

    .brand-bar { text-align:center; margin-bottom:20px; }
    .brand-name { font-family:'Orbitron',sans-serif; font-size:12px; letter-spacing:7px; color:rgba(167,139,250,.55); text-transform:uppercase; }
    .brand-tagline { font-family:'Exo 2',sans-serif; font-size:10px; letter-spacing:3px; color:rgba(100,116,139,.45); text-transform:uppercase; margin-top:3px; }

    .neon-divider { height:1px; background:linear-gradient(90deg,transparent,rgba(139,92,246,0.3),transparent); margin:20px 0; border:none; }

    .info-box {
        background: rgba(59,130,246,0.08); border: 1px solid rgba(59,130,246,0.25);
        border-radius: 10px; padding: 14px 16px; margin-bottom: 16px;
        font-family: 'Exo 2', sans-serif; color: rgba(147,197,253,0.8);
        font-size: 13px; line-height: 1.6;
    }

    .success-box {
        background: rgba(16,185,129,0.1); border: 1px solid rgba(16,185,129,0.3);
        border-radius: 12px; padding: 24px; text-align: center; margin-bottom: 16px;
    }
    .success-icon { font-size: 48px; margin-bottom: 12px; }
    .success-title { font-family:'Orbitron',sans-serif; font-size:1.2rem; color:#34d399; letter-spacing:2px; margin-bottom:8px; }
    .success-text { font-family:'Exo 2',sans-serif; color:rgba(52,211,153,0.7); font-size:13px; line-height:1.6; }

    .footer-text { font-family:'Exo 2',sans-serif; text-align:center; color:rgba(51,65,85,0.9); font-size:9px; letter-spacing:2px; margin-top:18px; text-transform:uppercase; }
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
        """, unsafe_allow_html=True)

        # Show success state
        if st.session_state.get("forgot_password_sent"):
            st.markdown("""
            <div class="success-box">
                <div class="success-icon">📧</div>
                <div class="success-title">EMAIL SENT!</div>
                <div class="success-text">
                    If your email exists in our system, a password reset link has been sent.<br><br>
                    Check your inbox and click the link to reset your password.<br>
                    The link expires in <strong>1 hour</strong>.
                </div>
            </div>
            """, unsafe_allow_html=True)

            if st.button("🔐 Back to Login", use_container_width=True):
                st.session_state.forgot_password_sent = False
                st.session_state.page = "Login"
                st.rerun()

            if st.button("🔁 Resend Email", use_container_width=True):
                st.session_state.forgot_password_sent = False
                st.rerun()

            st.markdown('<div class="footer-text">// encrypted connection (https)</div>', unsafe_allow_html=True)
            return

        st.markdown("""
        <div class="forgot-card">
            <div class="corner-tl"></div><div class="corner-tr"></div>
            <div class="corner-bl"></div><div class="corner-br"></div>
            <div class="forgot-icon"></div>
            <div class="forgot-title">FORGOT PASSWORD</div>
            <div class="forgot-subtitle">// recover access to your account</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="info-box">
            📨 Enter your registered email address and we'll send you a secure link to reset your password.
        </div>
        """, unsafe_allow_html=True)

        with st.form("forgot_password_form"):
            email = st.text_input(" Email Address")
            submitted = st.form_submit_button("SEND RESET LINK", use_container_width=True)

        if submitted:
            if not email.strip():
                st.warning("⚠️ Please enter your email address.")
            else:
                with st.spinner("Sending reset link..."):
                    response = forgot_password(email)

                if response.status_code == 200:
                    st.session_state.forgot_password_sent = True
                    st.rerun()
                else:
                    st.error("❌ Could not send reset link. Please try again.")

        st.markdown('<div class="neon-divider"></div>', unsafe_allow_html=True)

        if st.button("🔐 Back to Login", use_container_width=True):
            st.session_state.page = "Login"
            st.rerun()

        st.markdown('<div class="footer-text">// encrypted connection (https)</div>', unsafe_allow_html=True)