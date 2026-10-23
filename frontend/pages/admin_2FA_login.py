import requests
import streamlit as st

from api import admin_request_otp, admin_verify_otp, error_message

st.set_page_config(page_title="Admin 2FA Login", page_icon="🛡️", layout="centered")

st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg,#0f172a,#1e293b,#334155);
}

.card {
    background: rgba(255,255,255,0.08);
    padding: 2rem;
    border-radius: 20px;
    box-shadow: 0 8px 24px rgba(0,0,0,0.25);
    backdrop-filter: blur(8px);
    color: white;
    max-width: 600px;
    margin: auto;
    margin-top: 40px;
}
</style>
""", unsafe_allow_html=True)

st.session_state.setdefault("otp_requested", False)

st.markdown('<div class="card">', unsafe_allow_html=True)
st.title("🛡️ Admin 2FA Login")


def _reset_flow():
    st.session_state["otp_requested"] = False
    st.session_state.pop("admin_email", None)


try:
    if not st.session_state["otp_requested"]:
        st.caption("Step 1 of 2 — enter your admin email and password. We will email you a 6-digit code.")
        email = st.text_input("Admin Email")
        password = st.text_input("Password", type="password")

        if st.button("Send me a code", use_container_width=True):
            if not email or not password:
                st.warning("Please enter both email and password.")
            else:
                with st.spinner("Checking credentials..."):
                    response = admin_request_otp(email.strip().lower(), password)
                if response.status_code == 200:
                    st.session_state["otp_requested"] = True
                    st.session_state["admin_email"] = email.strip().lower()
                    st.rerun()
                else:
                    st.error(error_message(response, "Request failed"))
    else:
        st.caption(f"Step 2 of 2 — enter the 6-digit code sent to {st.session_state['admin_email']}. It expires in 5 minutes.")
        otp_code = st.text_input("Code", max_chars=6, type="password")

        col_verify, col_back = st.columns(2)
        with col_verify:
            verify_clicked = st.button("Verify & sign in", use_container_width=True)
        with col_back:
            if st.button("Start over", use_container_width=True):
                _reset_flow()
                st.rerun()

        if verify_clicked:
            if not otp_code.strip():
                st.warning("Please enter the code.")
            else:
                with st.spinner("Verifying..."):
                    response = admin_verify_otp(st.session_state["admin_email"], otp_code.strip())
                if response.status_code == 200:
                    data = response.json()
                    st.session_state["token"] = data["access_token"]
                    st.session_state["role"] = data.get("role", "admin")
                    st.session_state["user_email"] = st.session_state["admin_email"]
                    st.session_state["page"] = "Admin Panel"
                    _reset_flow()
                    st.success("Signed in. Redirecting...")
                    st.switch_page("app.py")
                else:
                    st.error(error_message(response, "Code verification failed"))
except requests.exceptions.Timeout:
    st.warning("⏳ Server is waking up — please wait 30 seconds and try again.")
except requests.exceptions.ConnectionError:
    st.error("❌ Could not connect to the backend.")

st.markdown("</div>", unsafe_allow_html=True)
