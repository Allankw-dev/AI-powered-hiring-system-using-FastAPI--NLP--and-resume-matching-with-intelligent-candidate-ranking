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

    .dash-header {
        display: flex; align-items: center; justify-content: space-between;
        margin-bottom: 24px; padding: 18px 24px;
        background: rgba(4,6,22,.85);
        border: 1px solid rgba(139,92,246,.2);
        border-radius: 16px;
        backdrop-filter: blur(20px);
        position: relative; overflow: hidden;
        flex-wrap: wrap; gap: 12px;
    }

    .dash-header::before {
        content:''; position:absolute; top:0; left:0; right:0; height:1px;
        background:linear-gradient(90deg,transparent,#8b5cf6,#60a5fa,transparent);
    }

    .header-brand { font-family:'Orbitron',sans-serif; font-size:10px; letter-spacing:5px; color:rgba(167,139,250,.5); text-transform:uppercase; }
    .header-title { font-family:'Orbitron',sans-serif; font-size:1.6rem; font-weight:900; background:linear-gradient(90deg,#a78bfa,#60a5fa,#c084fc); -webkit-background-clip:text; -webkit-text-fill-color:transparent; letter-spacing:2px; }
    .header-sub { font-family:'Exo 2',sans-serif; color:rgba(100,116,139,.7); font-size:11px; letter-spacing:2px; text-transform:uppercase; margin-top:2px; }

    .user-badge {
        padding: 8px 16px;
        background: rgba(139,92,246,.08);
        border: 1px solid rgba(139,92,246,.2);
        border-radius: 999px;
        font-family: 'Exo 2', sans-serif;
        font-size: 12px; color: #a78bfa; letter-spacing: 1px;
        white-space: nowrap;
    }

    /* ── STAT CARDS ── */
    .stat-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(130px, 1fr));
        gap: 12px;
        margin-bottom: 16px;
    }

    .stat-card {
        background: rgba(4,6,22,.85);
        border: 1px solid rgba(139,92,246,.18);
        border-radius: 16px; padding: 22px 18px;
        text-align: center; position: relative; overflow: hidden;
        transition: all .3s ease;
        backdrop-filter: blur(16px);
    }

    .stat-card::before {
        content:''; position:absolute; top:0; left:0; right:0; height:1.5px;
        background:linear-gradient(90deg,transparent,rgba(139,92,246,.6),transparent);
    }

    .stat-card:hover { border-color:rgba(139,92,246,.4); transform:translateY(-4px); box-shadow:0 0 25px rgba(139,92,246,.15); }

    .stat-icon { font-size:26px; margin-bottom:8px; filter:drop-shadow(0 0 8px rgba(139,92,246,.6)); }
    .stat-label { font-family:'Exo 2',sans-serif; color:rgba(100,116,139,.7); font-size:10px; letter-spacing:2px; text-transform:uppercase; margin-bottom:6px; }
    .stat-number { font-family:'Orbitron',sans-serif; font-size:38px; font-weight:900; background:linear-gradient(135deg,#a78bfa,#60a5fa); -webkit-background-clip:text; -webkit-text-fill-color:transparent; }

    .neon-divider { height:1px; background:linear-gradient(90deg,transparent,rgba(139,92,246,.4),rgba(59,130,246,.4),transparent); margin:20px 0; border:none; }

    .section-label { font-family:'Orbitron',sans-serif; font-size:11px; font-weight:700; color:rgba(139,92,246,.7); letter-spacing:3px; text-transform:uppercase; margin-bottom:14px; }

    /* ── QUICK ACTIONS ── */
    .action-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(130px, 1fr));
        gap: 10px;
        margin-bottom: 12px;
    }

    .action-card {
        background: rgba(4,6,22,.8);
        border: 1px solid rgba(139,92,246,.15);
        border-radius: 14px; padding: 18px 12px;
        text-align: center; transition: all .3s ease;
    }
    .action-card:hover { border-color:rgba(139,92,246,.35); box-shadow:0 0 20px rgba(139,92,246,.1); transform:translateY(-3px); }
    .action-icon { font-size:26px; margin-bottom:8px; filter:drop-shadow(0 0 8px rgba(139,92,246,.5)); }
    .action-label { font-family:'Exo 2',sans-serif; color:rgba(148,163,184,.8); font-size:13px; font-weight:600; }

    /* ── APPLICATION CARDS ── */
    .app-card {
        background: rgba(4,6,22,.8);
        border: 1px solid rgba(139,92,246,.15);
        border-radius: 14px; margin-bottom: 10px;
        overflow: hidden; transition: all .3s ease;
    }
    .app-card:hover { border-color:rgba(139,92,246,.3); box-shadow:0 0 15px rgba(139,92,246,.08); }

    .app-header {
        display:flex; justify-content:space-between; align-items:center;
        padding:14px 18px; background:rgba(139,92,246,.04);
        border-bottom:1px solid rgba(139,92,246,.08);
        flex-wrap: wrap; gap: 4px;
    }
    .app-job { font-family:'Exo 2',sans-serif; font-weight:700; color:#e2e8f0; font-size:14px; }
    .app-date { font-family:'Exo 2',sans-serif; color:rgba(100,116,139,.6); font-size:12px; }
    .app-body { padding:14px 18px; }

    .status-badge { padding:4px 12px; border-radius:999px; font-family:'Exo 2',sans-serif; font-size:11px; font-weight:600; letter-spacing:1px; text-transform:uppercase; display:inline-block; margin-bottom:10px; }
    .status-submitted { background:rgba(139,92,246,.15); color:#a78bfa; border:1px solid rgba(139,92,246,.3); }
    .status-shortlisted { background:rgba(16,185,129,.15); color:#34d399; border:1px solid rgba(16,185,129,.3); }
    .status-rejected { background:rgba(239,68,68,.15); color:#f87171; border:1px solid rgba(239,68,68,.3); }
    .status-pending { background:rgba(245,158,11,.15); color:#fbbf24; border:1px solid rgba(245,158,11,.3); }

    .score-row { display:flex; gap:8px; flex-wrap:wrap; }
    .score-chip { background:rgba(59,130,246,.07); border:1px solid rgba(59,130,246,.18); border-radius:7px; padding:5px 10px; font-family:'Exo 2',sans-serif; font-size:11px; color:#93c5fd; }
    .score-chip span { font-weight:700; color:#60a5fa; }

    /* ── MOBILE OVERRIDES ── */
    @media (max-width: 640px) {
        .header-title { font-size: 1.2rem; }
        .dash-header { padding: 14px 16px; }
        .stat-number { font-size: 28px; }
        .stat-card { padding: 16px 12px; }
        .score-chip { font-size: 10px; padding: 4px 8px; }
        .app-date { display: none; }
        .action-grid { grid-template-columns: repeat(2, 1fr); }
    }
    </style>

    <div class="city-bg"></div>
    """, unsafe_allow_html=True)

    # ── FETCH DATA ──
    resumes_response = my_resumes()
    applications_response = my_applications()
    jobs_response = list_jobs()

    resume_count = len(resumes_response.json()) if resumes_response.status_code == 200 else 0
    application_count = len(applications_response.json()) if applications_response.status_code == 200 else 0
    job_count = len(jobs_response.json()) if jobs_response.status_code == 200 else 0
    email = st.session_state.get("user_email", "Candidate")

    # ── HEADER ──
    st.markdown(f"""
    <div class="dash-header">
        <div>
            <div class="header-brand">AI Hiring System</div>
            <div class="header-title">DASHBOARD</div>
            <div class="header-sub">// Candidate Portal</div>
        </div>
        <div class="user-badge">👤 {email}</div>
    </div>
    """, unsafe_allow_html=True)

    # ── STAT CARDS (CSS grid — collapses cleanly on mobile) ──
    st.markdown(f"""
    <div class="stat-grid">
        <div class="stat-card">
            <div class="stat-icon">📄</div>
            <div class="stat-label">My Resumes</div>
            <div class="stat-number">{resume_count}</div>
        </div>
        <div class="stat-card">
            <div class="stat-icon">📨</div>
            <div class="stat-label">Applications</div>
            <div class="stat-number">{application_count}</div>
        </div>
        <div class="stat-card">
            <div class="stat-icon">💼</div>
            <div class="stat-label">Available Jobs</div>
            <div class="stat-number">{job_count}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="neon-divider"></div>', unsafe_allow_html=True)

    # ── QUICK ACTIONS (CSS grid — 2 cols on mobile, 4 on desktop) ──
    st.markdown('<div class="section-label">// Quick Actions</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="action-grid">
        <div class="action-card"><div class="action-icon">💼</div><div class="action-label">Browse Jobs</div></div>
        <div class="action-card"><div class="action-icon">📤</div><div class="action-label">Upload Resume</div></div>
        <div class="action-card"><div class="action-icon">📋</div><div class="action-label">My Applications</div></div>
        <div class="action-card"><div class="action-icon">👤</div><div class="action-label">My Profile</div></div>
    </div>
    """, unsafe_allow_html=True)

    # Buttons in a 2x2 grid on mobile via st.columns (Streamlit handles this better at 2 cols)
    b1, b2 = st.columns(2)
    with b1:
        if st.button("💼 Browse Jobs", key="go_jobs", use_container_width=True):
            st.session_state.page = "Jobs"
            st.rerun()
    with b2:
        if st.button("📤 Upload Resume", key="go_resume", use_container_width=True):
            st.session_state.page = "Upload Resume"
            st.rerun()

    b3, b4 = st.columns(2)
    with b3:
        if st.button("📋 My Applications", key="go_apps", use_container_width=True):
            st.session_state.page = "Applications"
            st.rerun()
    with b4:
        if st.button("👤 My Profile", key="go_profile", use_container_width=True):
            st.session_state.page = "Profile"
            st.rerun()

    st.markdown('<div class="neon-divider"></div>', unsafe_allow_html=True)

    # ── APPLICATIONS ──
    st.markdown('<div class="section-label">// My Application Status</div>', unsafe_allow_html=True)

    if applications_response.status_code == 200:
        apps = applications_response.json()
        if not apps:
            st.info("No applications yet. Browse jobs and apply!")
        else:
            for app in apps:
                status = app.get("status", "submitted").lower()
                status_class = f"status-{status}" if status in ["submitted", "shortlisted", "rejected", "pending"] else "status-submitted"
                st.markdown(f"""
                <div class="app-card">
                    <div class="app-header">
                        <div class="app-job">💼 Job #{app.get('job_id', 'N/A')} — Applied {str(app.get('applied_at', ''))[:10]}</div>
                        <div class="app-date">{str(app.get('applied_at', ''))[:10]}</div>
                    </div>
                    <div class="app-body">
                        <span class="status-badge {status_class}">{status.upper()}</span>
                        <div class="score-row">
                            <div class="score-chip">Overall <span>{app.get('overall_score', 'N/A')}</span></div>
                            <div class="score-chip">Semantic <span>{app.get('semantic_score', 'N/A')}</span></div>
                            <div class="score-chip">Skills <span>{app.get('skills_score', 'N/A')}</span></div>
                            <div class="score-chip">Experience <span>{app.get('experience_score', 'N/A')}</span></div>
                            <div class="score-chip">Verification <span>{app.get('verification_score', 'N/A')}</span></div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.error("Could not load applications.")