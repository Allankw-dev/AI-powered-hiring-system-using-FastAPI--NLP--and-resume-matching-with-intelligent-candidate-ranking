import streamlit as st
from api import my_resumes, my_applications, list_jobs


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

    .dash-title {
        font-family: 'Orbitron', sans-serif;
        font-size: 2.2rem;
        font-weight: 900;
        background: linear-gradient(90deg, #a78bfa, #60a5fa);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        filter: drop-shadow(0 0 20px rgba(139,92,246,0.5));
        letter-spacing: 2px;
        margin-bottom: 4px;
    }

    .dash-sub {
        font-family: 'Exo 2', sans-serif;
        color: #475569;
        font-size: 15px;
        letter-spacing: 1px;
        margin-bottom: 28px;
    }

    .stat-card {
        background: rgba(139,92,246,0.05);
        border: 1px solid rgba(139,92,246,0.2);
        border-radius: 18px;
        padding: 24px 20px;
        text-align: center;
        position: relative;
        overflow: hidden;
        transition: all 0.3s ease;
    }

    .stat-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 2px;
        background: linear-gradient(90deg, transparent, rgba(139,92,246,0.8), transparent);
    }

    .stat-card:hover {
        border-color: rgba(139,92,246,0.45);
        box-shadow: 0 0 30px rgba(139,92,246,0.15), 0 10px 30px rgba(0,0,0,0.3);
        transform: translateY(-4px);
    }

    .stat-icon {
        font-size: 28px;
        margin-bottom: 10px;
        filter: drop-shadow(0 0 8px rgba(139,92,246,0.6));
    }

    .stat-label {
        font-family: 'Exo 2', sans-serif;
        color: #64748b;
        font-size: 12px;
        letter-spacing: 2px;
        text-transform: uppercase;
        margin-bottom: 8px;
    }

    .stat-number {
        font-family: 'Orbitron', sans-serif;
        font-size: 42px;
        font-weight: 900;
        background: linear-gradient(135deg, #a78bfa, #60a5fa);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        filter: drop-shadow(0 0 15px rgba(139,92,246,0.5));
    }

    .neon-divider {
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(139,92,246,0.5), rgba(59,130,246,0.5), transparent);
        margin: 28px 0;
        border: none;
    }

    .section-title {
        font-family: 'Orbitron', sans-serif;
        font-size: 16px;
        font-weight: 700;
        color: #a78bfa;
        letter-spacing: 2px;
        text-transform: uppercase;
        margin-bottom: 16px;
        padding-bottom: 10px;
        border-bottom: 1px solid rgba(139,92,246,0.15);
    }

    .dropdown-wrapper {
        background: rgba(139,92,246,0.04);
        border: 1px solid rgba(139,92,246,0.15);
        border-radius: 16px;
        overflow: hidden;
        margin-bottom: 12px;
        transition: all 0.3s ease;
    }

    .dropdown-wrapper:hover {
        border-color: rgba(139,92,246,0.3);
        box-shadow: 0 0 20px rgba(139,92,246,0.08);
    }

    .dropdown-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 16px 20px;
        cursor: pointer;
        background: rgba(139,92,246,0.06);
    }

    .dropdown-job-title {
        font-family: 'Exo 2', sans-serif;
        font-weight: 700;
        color: #e2e8f0;
        font-size: 15px;
    }

    .dropdown-job-company {
        font-family: 'Exo 2', sans-serif;
        color: #64748b;
        font-size: 13px;
        margin-top: 2px;
    }

    .status-badge {
        padding: 4px 12px;
        border-radius: 999px;
        font-family: 'Exo 2', sans-serif;
        font-size: 12px;
        font-weight: 600;
        letter-spacing: 1px;
        text-transform: uppercase;
    }

    .status-submitted {
        background: rgba(139,92,246,0.15);
        color: #a78bfa;
        border: 1px solid rgba(139,92,246,0.3);
    }

    .status-shortlisted {
        background: rgba(16,185,129,0.15);
        color: #34d399;
        border: 1px solid rgba(16,185,129,0.3);
    }

    .status-rejected {
        background: rgba(239,68,68,0.15);
        color: #f87171;
        border: 1px solid rgba(239,68,68,0.3);
    }

    .status-pending {
        background: rgba(245,158,11,0.15);
        color: #fbbf24;
        border: 1px solid rgba(245,158,11,0.3);
    }

    .score-row {
        display: flex;
        gap: 10px;
        flex-wrap: wrap;
        margin-top: 12px;
    }

    .score-chip {
        background: rgba(59,130,246,0.08);
        border: 1px solid rgba(59,130,246,0.2);
        border-radius: 8px;
        padding: 6px 12px;
        font-family: 'Exo 2', sans-serif;
        font-size: 12px;
        color: #93c5fd;
    }

    .score-chip span {
        font-weight: 700;
        color: #60a5fa;
    }

    .quick-action-card {
        background: rgba(139,92,246,0.04);
        border: 1px solid rgba(139,92,246,0.15);
        border-radius: 14px;
        padding: 20px;
        text-align: center;
        transition: all 0.3s ease;
        cursor: pointer;
    }

    .quick-action-card:hover {
        border-color: rgba(139,92,246,0.4);
        box-shadow: 0 0 20px rgba(139,92,246,0.12);
        transform: translateY(-3px);
    }

    .quick-action-icon {
        font-size: 28px;
        margin-bottom: 8px;
        filter: drop-shadow(0 0 8px rgba(139,92,246,0.5));
    }

    .quick-action-label {
        font-family: 'Exo 2', sans-serif;
        color: #94a3b8;
        font-size: 13px;
        font-weight: 600;
    }
    </style>
    """, unsafe_allow_html=True)

    # ── HEADER ──
    email = st.session_state.get("user_email", "Candidate")
    st.markdown(f'<div class="dash-title">Mission Control</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="dash-sub">// CANDIDATE PORTAL — {email.upper()}</div>', unsafe_allow_html=True)

    # ── FETCH DATA ──
    resumes_response = my_resumes()
    applications_response = my_applications()
    jobs_response = list_jobs()

    resume_count = len(resumes_response.json()) if resumes_response.status_code == 200 else 0
    application_count = len(applications_response.json()) if applications_response.status_code == 200 else 0
    job_count = len(jobs_response.json()) if jobs_response.status_code == 200 else 0

    # ── STAT CARDS ──
    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-icon">📄</div>
            <div class="stat-label">My Resumes</div>
            <div class="stat-number">{resume_count}</div>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-icon">📨</div>
            <div class="stat-label">Applications</div>
            <div class="stat-number">{application_count}</div>
        </div>
        """, unsafe_allow_html=True)

    with c3:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-icon">💼</div>
            <div class="stat-label">Available Jobs</div>
            <div class="stat-number">{job_count}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<div class="neon-divider"></div>', unsafe_allow_html=True)

    # ── QUICK ACTIONS ──
    st.markdown('<div class="section-title">// Quick Actions</div>', unsafe_allow_html=True)

    q1, q2, q3, q4 = st.columns(4)

    with q1:
        st.markdown('<div class="quick-action-card"><div class="quick-action-icon">💼</div><div class="quick-action-label">Browse Jobs</div></div>', unsafe_allow_html=True)
        if st.button("Go →", key="go_jobs"):
            st.session_state.page = "Jobs"
            st.rerun()

    with q2:
        st.markdown('<div class="quick-action-card"><div class="quick-action-icon">📤</div><div class="quick-action-label">Upload Resume</div></div>', unsafe_allow_html=True)
        if st.button("Go →", key="go_resume"):
            st.session_state.page = "Upload Resume"
            st.rerun()

    with q3:
        st.markdown('<div class="quick-action-card"><div class="quick-action-icon">📋</div><div class="quick-action-label">My Applications</div></div>', unsafe_allow_html=True)
        if st.button("Go →", key="go_apps"):
            st.session_state.page = "Applications"
            st.rerun()

    with q4:
        st.markdown('<div class="quick-action-card"><div class="quick-action-icon">👤</div><div class="quick-action-label">My Profile</div></div>', unsafe_allow_html=True)
        if st.button("Go →", key="go_profile"):
            st.session_state.page = "Profile"
            st.rerun()

    st.markdown('<div class="neon-divider"></div>', unsafe_allow_html=True)

    # ── APPLICATIONS DROPDOWN ──
    st.markdown('<div class="section-title">// My Application Status</div>', unsafe_allow_html=True)

    if applications_response.status_code == 200:
        apps = applications_response.json()
        if not apps:
            st.info("No applications yet. Browse jobs and apply!")
        else:
            for i, app in enumerate(apps):
                status = app.get("status", "submitted").lower()
                status_class = f"status-{status}" if status in ["submitted", "shortlisted", "rejected", "pending"] else "status-submitted"

                with st.expander(f"📋  {app.get('job_id', 'Job')}  —  Applied {str(app.get('applied_at', ''))[:10]}"):
                    st.markdown(f"""
                    <div style="padding: 8px 0;">
                        <span class="status-badge {status_class}">{status.upper()}</span>
                    </div>
                    <div class="score-row">
                        <div class="score-chip">Overall <span>{app.get('overall_score', 'N/A')}</span></div>
                        <div class="score-chip">Semantic <span>{app.get('semantic_score', 'N/A')}</span></div>
                        <div class="score-chip">Skills <span>{app.get('skills_score', 'N/A')}</span></div>
                        <div class="score-chip">Experience <span>{app.get('experience_score', 'N/A')}</span></div>
                        <div class="score-chip">Verification <span>{app.get('verification_score', 'N/A')}</span></div>
                    </div>
                    """, unsafe_allow_html=True)
    else:
        st.error("Could not load applications.")