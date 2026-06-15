import streamlit as st
from api import sign_up


def render():
    st.markdown("""
    <div style="
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 22px;
        padding: 30px;
        box-shadow: 0 8px 24px rgba(0,0,0,0.2);
        margin-top: 10px;
    ">
        <h2 style="margin-top:0; color:white;">Create Account</h2>
        <p style="color:#cbd5e1;">Sign up to upload your resume, browse jobs, and apply easily.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    with st.form("signup_form"):
        full_name = st.text_input("Full Name")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")

        # ✅ NEW FIELD
        sex = st.selectbox("Sex", ["Male", "Female", "Other"])

        submitted = st.form_submit_button("Create Account")

    if submitted:
        if not full_name or not email or not password or not confirm_password:
            st.warning("Please fill in all fields.")
            return

        if password != confirm_password:
            st.error("Passwords do not match.")
            return

        # ✅ PASS sex to API
        response = sign_up(full_name, email, password, sex)

        if response.status_code in [200, 201]:
            st.success("Account created successfully. You can now log in.")
        else:
            try:
                st.error(response.json().get("detail", "Sign up failed."))
            except Exception:
                st.error("Sign up failed.")