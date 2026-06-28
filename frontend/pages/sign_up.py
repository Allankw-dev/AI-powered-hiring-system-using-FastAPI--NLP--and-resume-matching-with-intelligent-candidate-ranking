import streamlit as st
from api import sign_up, login


def render():
    # Redirect if already logged in
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

    .brand-bar { text-align:center; margin-bottom:18px; }
    .brand-name { font-family:'Orbitron',sans-serif; font-size:12px; letter-spacing:7px; color:rgba(167,139,250,.55); text-transform:uppercase; }
    .brand-tagline { font-family:'Exo 2',sans-serif; font-size:10px; letter-spacing:3px; color:rgba(100,116,139,.45); text-transform:uppercase; margin-top:3px; }

    .signup-card {
        background: rgba(4,6,22,.9);
        border: 1px solid rgba(139,92,246,.22);
        border-radius: 22px;
        padding: 36px 36px 28px;
        position: relative;
        overflow: hidden;
        box-shadow: 0 0 40px rgba(139,92,246,.2), 0 20px 60px rgba(0,0,0,.5);
        backdrop-filter: blur(28px);
        margin-bottom: 16px;
    }

    .signup-card::before {
        content:''; position:absolute; top:0; left:0; right:0; height:1.5px;
        background:linear-gradient(90deg,transparent,#8b5cf6,#60a5fa,#c084fc,transparent);
        box-shadow:0 0 18px rgba(139,92,246,.7);
    }

    .corner { position:absolute; width:14px; height:14px; border-color:rgba(139,92,246,.55); border-style:solid; }
    .c-tl{top:10px;left:10px;border-width:1.5px 0 0 1.5px}
    .c-tr{top:10px;right:10px;border-width:1.5px 1.5px 0 0}
    .c-bl{bottom:10px;left:10px;border-width:0 0 1.5px 1.5px}
    .c-br{bottom:10px;right:10px;border-width:0 1.5px 1.5px 0}

    .card-top {
        display:flex; align-items:center; gap:16px;
        margin-bottom:20px; padding-bottom:18px;
        border-bottom:1px solid rgba(139,92,246,.1);
    }

    .icon-box {
        width:52px; height:52px; flex-shrink:0;
        background:rgba(139,92,246,.1);
        border:1px solid rgba(139,92,246,.3);
        border-radius:14px;
        display:flex; align-items:center; justify-content:center;
        font-size:24px;
        box-shadow:0 0 20px rgba(139,92,246,.2);
    }

    .card-title { font-family:'Orbitron',sans-serif; font-size:1.5rem; font-weight:900; background:linear-gradient(90deg,#a78bfa,#60a5fa,#c084fc); -webkit-background-clip:text; -webkit-text-fill-color:transparent; letter-spacing:3px; }
    .card-sub { font-family:'Exo 2',sans-serif; color:rgba(100,116,139,.7); font-size:11px; letter-spacing:1.5px; text-transform:uppercase; margin-top:3px; }

    .progress-bar { display:flex; gap:6px; margin-bottom:20px; }
    .prog-step { flex:1; height:3px; border-radius:2px; background:rgba(139,92,246,.15); border:1px solid rgba(139,92,246,.2); }
    .prog-step.active { background:rgba(139,92,246,.4); border-color:rgba(139,92,246,.6); box-shadow:0 0 8px rgba(139,92,246,.4); }

    .neon-divider { height:1px; background:linear-gradient(90deg,transparent,rgba(139,92,246,.2),transparent); margin:16px 0; border:none; }

    .bottom-stats {
        display:flex; justify-content:space-around; margin-top:14px;
        padding:10px; background:rgba(139,92,246,.03);
        border:1px solid rgba(139,92,246,.08); border-radius:10px;
    }
    .bstat { text-align:center; }
    .bstat-num { font-family:'Orbitron',sans-serif; font-size:13px; font-weight:700; background:linear-gradient(90deg,#a78bfa,#60a5fa); -webkit-background-clip:text; -webkit-text-fill-color:transparent; }
    .bstat-lbl { font-family:'Exo 2',sans-serif; font-size:9px; color:rgba(100,116,139,.55); letter-spacing:1px; text-transform:uppercase; margin-top:2px; }

    .footer-text { font-family:'Exo 2',sans-serif; text-align:center; color:rgba(51,65,85,.8); font-size:9px; letter-spacing:2px; margin-top:14px; text-transform:uppercase; }

    .city-bg {
        position:fixed; bottom:0; left:0; right:0; height:45%;
        background: linear-gradient(to top, rgba(139,92,246,.04), transparent),
            repeating-linear-gradient(90deg, rgba(18,8,45,.95) 0px, rgba(18,8,45,.95) 24px, rgba(28,12,60,.95) 24px, rgba(28,12,60,.95) 28px);
        pointer-events:none; z-index:0;
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

        <div class="signup-card">
            <div class="corner c-tl"></div>
            <div class="corner c-tr"></div>
            <div class="corner c-bl"></div>
            <div class="corner c-br"></div>

            <div class="card-top">
                <div class="icon-box">🚀</div>
                <div>
                    <div class="card-title">SIGN UP</div>
                    <div class="card-sub">// Join the future of hiring</div>
                </div>
            </div>

            <div class="progress-bar">
                <div class="prog-step active"></div>
                <div class="prog-step active"></div>
                <div class="prog-step active"></div>
                <div class="prog-step active"></div>
                <div class="prog-step"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        with st.form("signup_form"):
            full_name = st.text_input("👤 Full Name")
            email = st.text_input("📧 Email Address")

            col1, col2 = st.columns(2)
            with col1:
                password = st.text_input("🔑 Password", type="password")
            with col2:
                confirm_password = st.text_input("🔑 Confirm Password", type="password")

            sex = st.selectbox("⚧ Gender", ["Male", "Female", "Other"])
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
                    st.success("✅ Account created! Logging you in...")
                    with st.spinner("Logging in..."):
                        login_response = login(email, password)
                    if login_response.status_code == 200:
                        data = login_response.json()
                        st.session_state["token"] = data.get("access_token")
                        st.session_state["role"] = data.get("role", "candidate")
                        st.session_state["user_email"] = email
                        role = data.get("role", "candidate")
                        if role == "admin":
                            st.session_state["page"] = "Admin Panel"
                        else:
                            st.session_state["page"] = "Dashboard"
                        st.rerun()
                    else:
                        st.session_state["page"] = "Login"
                        st.rerun()
                else:
                    try:
                        st.error(response.json().get("detail", "Sign up failed."))
                    except Exception:
                        st.error("Sign up failed.")

        st.markdown("""
        <div class="bottom-stats">
            <div class="bstat"><div class="bstat-num">Free</div><div class="bstat-lbl">Forever</div></div>
            <div class="bstat"><div class="bstat-num">AI</div><div class="bstat-lbl">Powered</div></div>
            <div class="bstat"><div class="bstat-num">256</div><div class="bstat-lbl">Bit Secure</div></div>
            <div class="bstat"><div class="bstat-num">24/7</div><div class="bstat-lbl">Available</div></div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="neon-divider"></div>', unsafe_allow_html=True)

        if st.button("🔐 Already have an account? Log In", use_container_width=True):
            st.session_state.page = "Login"
            st.rerun()

        st.markdown('<div class="footer-text">// secure encrypted registration · ai hiring system</div>', unsafe_allow_html=True)