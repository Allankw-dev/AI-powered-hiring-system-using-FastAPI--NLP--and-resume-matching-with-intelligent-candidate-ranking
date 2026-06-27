import streamlit as st
import base64
from api import my_resumes, my_applications, get_my_profile, update_my_profile, upload_profile_picture


def render():
    if not st.session_state.get("token"):
        st.warning("Please log in first.")
        st.stop()

    if st.session_state.get("role") != "candidate":
        st.error("Access denied. Candidates only.")
        st.stop()

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

    .page-header {
        margin-bottom: 24px; padding: 18px 24px;
        background: rgba(4,6,22,.85);
        border: 1px solid rgba(139,92,246,.2);
        border-radius: 16px;
        backdrop-filter: blur(20px);
        position: relative; overflow: hidden;
    }
    .page-header::before { content:''; position:absolute; top:0; left:0; right:0; height:1px; background:linear-gradient(90deg,transparent,#8b5cf6,#60a5fa,transparent); }
    .page-brand { font-family:'Orbitron',sans-serif; font-size:10px; letter-spacing:5px; color:rgba(167,139,250,.5); text-transform:uppercase; }
    .page-title { font-family:'Orbitron',sans-serif; font-size:1.6rem; font-weight:900; background:linear-gradient(90deg,#a78bfa,#60a5fa,#c084fc); -webkit-background-clip:text; -webkit-text-fill-color:transparent; letter-spacing:2px; }
    .page-sub { font-family:'Exo 2',sans-serif; color:rgba(100,116,139,.7); font-size:11px; letter-spacing:2px; text-transform:uppercase; margin-top:2px; }

    .profile-card {
        background: rgba(4,6,22,.85);
        border: 1px solid rgba(139,92,246,.2);
        border-radius: 16px; padding: 28px;
        backdrop-filter: blur(20px);
        position: relative; overflow: hidden;
        margin-bottom: 16px;
    }
    .profile-card::before { content:''; position:absolute; top:0; left:0; right:0; height:1px; background:linear-gradient(90deg,transparent,rgba(139,92,246,.5),transparent); }

    .avatar-wrapper {
        width: 120px; height: 120px;
        border-radius: 50%;
        border: 2px solid rgba(139,92,246,.4);
        box-shadow: 0 0 25px rgba(139,92,246,.3);
        overflow: hidden;
        margin: 0 auto 16px;
        background: rgba(139,92,246,.1);
        display: flex; align-items: center; justify-content: center;
        font-size: 48px;
    }

    .profile-name {
        font-family: 'Orbitron', sans-serif;
        font-size: 1.3rem; font-weight: 700;
        background: linear-gradient(90deg,#a78bfa,#60a5fa);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        text-align: center; letter-spacing: 1px; margin-bottom: 4px;
    }

    .profile-email {
        font-family: 'Exo 2', sans-serif;
        color: rgba(100,116,139,.8); font-size: 13px;
        text-align: center; letter-spacing: 1px; margin-bottom: 8px;
    }

    .role-badge {
        display: inline-block; padding: 4px 16px;
        background: rgba(139,92,246,.12);
        border: 1px solid rgba(139,92,246,.3);
        border-radius: 999px; color: #a78bfa;
        font-family: 'Exo 2', sans-serif; font-size: 11px;
        letter-spacing: 2px; text-transform: uppercase;
        margin: 0 auto; display: block; text-align: center; width: fit-content;
    }

    .section-card {
        background: rgba(4,6,22,.85);
        border: 1px solid rgba(139,92,246,.15);
        border-radius: 16px; padding: 24px;
        backdrop-filter: blur(20px);
        position: relative; overflow: hidden;
        margin-bottom: 16px;
    }
    .section-card::before { content:''; position:absolute; top:0; left:0; right:0; height:1px; background:linear-gradient(90deg,transparent,rgba(139,92,246,.3),transparent); }

    .section-label { font-family:'Orbitron',sans-serif; font-size:11px; font-weight:700; color:rgba(139,92,246,.7); letter-spacing:3px; text-transform:uppercase; margin-bottom:16px; padding-bottom:10px; border-bottom:1px solid rgba(139,92,246,.1); }

    .resume-item {
        background: rgba(139,92,246,.04);
        border: 1px solid rgba(139,92,246,.12);
        border-radius: 10px; padding: 14px 16px;
        margin-bottom: 10px; transition: all .3s ease;
    }
    .resume-item:hover { border-color:rgba(139,92,246,.3); box-shadow:0 0 15px rgba(139,92,246,.08); }
    .resume-name { font-family:'Exo 2',sans-serif; font-weight:700; color:#e2e8f0; font-size:14px; margin-bottom:6px; }
    .resume-meta { display:flex; gap:10px; flex-wrap:wrap; }
    .resume-chip { background:rgba(59,130,246,.07); border:1px solid rgba(59,130,246,.18); border-radius:6px; padding:3px 10px; font-family:'Exo 2',sans-serif; font-size:11px; color:#93c5fd; }

    .neon-divider { height:1px; background:linear-gradient(90deg,transparent,rgba(139,92,246,.4),rgba(59,130,246,.4),transparent); margin:20px 0; border:none; }

    .status-submitted { background:rgba(139,92,246,.15); color:#a78bfa; border:1px solid rgba(139,92,246,.3); padding:3px 10px; border-radius:999px; font-size:11px; font-family:'Exo 2',sans-serif; }
    .status-shortlisted { background:rgba(16,185,129,.15); color:#34d399; border:1px solid rgba(16,185,129,.3); padding:3px 10px; border-radius:999px; font-size:11px; font-family:'Exo 2',sans-serif; }
    .status-rejected { background:rgba(239,68,68,.15); color:#f87171; border:1px solid rgba(239,68,68,.3); padding:3px 10px; border-radius:999px; font-size:11px; font-family:'Exo 2',sans-serif; }
    </style>

    <div class="city-bg"></div>
    """, unsafe_allow_html=True)

    # ── HEADER ──
    st.markdown("""
    <div class="page-header">
        <div class="page-brand">AI Hiring System</div>
        <div class="page-title">MY PROFILE</div>
        <div class="page-sub">// Manage your account & details</div>
    </div>
    """, unsafe_allow_html=True)

    # ── FETCH PROFILE ──
    profile_response = get_my_profile()
    profile = profile_response.json() if profile_response.status_code == 200 else {}
    email = st.session_state.get("user_email", profile.get("email", "Unknown"))
    full_name = profile.get("full_name", "")
    profile_picture = profile.get("profile_picture", None)

    # ── PROFILE CARD ──
    left_col, right_col = st.columns([1, 2])

    with left_col:
        st.markdown('<div class="profile-card" style="text-align:center;">', unsafe_allow_html=True)

        if profile_picture:
            st.markdown(f"""
            <div class="avatar-wrapper">
                <img src="{profile_picture}" style="width:100%;height:100%;object-fit:cover;" />
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="avatar-wrapper">👤</div>
            """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="profile-name">{full_name or "Your Name"}</div>
        <div class="profile-email">{email}</div>
        <div class="role-badge">✦ Candidate</div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        uploaded_pic = st.file_uploader("📸 Upload Profile Picture", type=["jpg", "jpeg", "png"], key="pic_upload")
        if uploaded_pic:
            if st.button("💾 Save Picture", use_container_width=True):
                with st.spinner("Uploading..."):
                    r = upload_profile_picture(uploaded_pic)
                if r.status_code == 200:
                    st.success("✅ Profile picture updated!")
                    st.rerun()
                else:
                    st.error("Failed to upload picture.")

        st.markdown('</div>', unsafe_allow_html=True)

    with right_col:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-label">// Edit Profile Details</div>', unsafe_allow_html=True)

        with st.form("edit_profile_form"):
            new_name = st.text_input("👤 Full Name", value=full_name)
            new_email = st.text_input("📧 Email Address", value=email)
            save = st.form_submit_button("💾 Save Changes", use_container_width=True)

        if save:
            r = update_my_profile(new_name, new_email)
            if r.status_code == 200:
                st.success("✅ Profile updated successfully!")
                st.rerun()
            else:
                try:
                    st.error(r.json().get("detail", "Failed to update profile."))
                except Exception:
                    st.error("Failed to update profile.")

        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="neon-divider"></div>', unsafe_allow_html=True)

    # ── RESUMES ──
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-label">// My Resumes</div>', unsafe_allow_html=True)

    resume_response = my_resumes()
    if resume_response.status_code == 200:
        resumes = resume_response.json()
        if resumes:
            for r in resumes:
                status = r.get('verification_status', 'pending')
                st.markdown(f"""
                <div class="resume-item">
                    <div class="resume-name">📄 {r.get('file_name', 'N/A')}</div>
                    <div class="resume-meta">
                        <div class="resume-chip">⏱ {r.get('experience_years', 0)} yrs exp</div>
                        <div class="resume-chip">🔍 {status.upper()}</div>
                        <div class="resume-chip">📅 {str(r.get('created_at', ''))[:10]}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No resumes uploaded yet.")
    else:
        st.error("Could not load resumes.")

    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="neon-divider"></div>', unsafe_allow_html=True)

    # ── APPLICATIONS ──
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-label">// My Applications</div>', unsafe_allow_html=True)

    app_response = my_applications()
    if app_response.status_code == 200:
        apps = app_response.json()
        if apps:
            for app in apps:
                status = app.get("status", "submitted").lower()
                status_class = f"status-{status}" if status in ["submitted", "shortlisted", "rejected"] else "status-submitted"
                st.markdown(f"""
                <div class="resume-item">
                    <div class="resume-name">💼 Job #{app.get('job_id', 'N/A')}</div>
                    <div class="resume-meta">
                        <span class="{status_class}">{status.upper()}</span>
                        <div class="resume-chip">Score: {app.get('overall_score', 'N/A')}</div>
                        <div class="resume-chip">📅 {str(app.get('applied_at', ''))[:10]}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No applications yet.")
    else:
        st.error("Could not load applications.")

    st.markdown('</div>', unsafe_allow_html=True)