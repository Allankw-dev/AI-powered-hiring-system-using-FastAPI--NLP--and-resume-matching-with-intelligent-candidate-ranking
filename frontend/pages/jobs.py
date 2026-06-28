import streamlit as st
from api import list_jobs, apply_to_job, my_resumes


def render():
    if not st.session_state.get("token"):
        st.warning("Please log in first.")
        st.stop()

    if st.session_state.get("role") != "candidate":
        st.error("Access denied. Candidates only.")
        st.stop()

    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@700;900&family=Exo+2:wght@300;400;600;700&display=swap');

    .stApp {
        background: #000510 !important;
    }

    .page-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 24px;
    }

    .page-title {
        font-family: 'Orbitron', sans-serif;
        font-size: 22px;
        font-weight: 900;
        background: linear-gradient(90deg, #38bdf8, #06b6d4);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: 2px;
    }

    .job-count {
        font-size: 12px;
        color: #38bdf8;
        background: rgba(56,189,248,0.1);
        border: 1px solid rgba(56,189,248,0.3);
        border-radius: 999px;
        padding: 4px 14px;
        font-family: 'Exo 2', sans-serif;
        letter-spacing: 1px;
    }

    .neon-line {
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(56,189,248,0.4), rgba(6,182,212,0.4), transparent);
        margin: 20px 0;
        border: none;
    }

    .jobs-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
        gap: 14px;
    }

    .job-card {
        background: rgba(4,6,22,0.85);
        border: 1px solid rgba(56,189,248,0.15);
        border-radius: 16px;
        overflow: hidden;
        transition: all 0.3s;
        backdrop-filter: blur(12px);
        position: relative;
        margin-bottom: 14px;
    }

    .job-card::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 2px;
        background: linear-gradient(90deg, #38bdf8, #06b6d4);
    }

    .job-card:hover {
        border-color: rgba(56,189,248,0.4);
        box-shadow: 0 0 24px rgba(56,189,248,0.12);
        transform: translateY(-3px);
    }

    .card-top {
        padding: 18px 18px 14px;
        border-bottom: 1px solid rgba(56,189,248,0.08);
    }

    .card-badge {
        display: inline-block;
        font-size: 10px;
        font-family: 'Exo 2', sans-serif;
        letter-spacing: 1.5px;
        text-transform: uppercase;
        padding: 3px 10px;
        border-radius: 999px;
        margin-bottom: 10px;
    }

    .badge-tech    { background: rgba(56,189,248,0.1);  color: #38bdf8; border: 1px solid rgba(56,189,248,0.25); }
    .badge-design  { background: rgba(168,85,247,0.1);  color: #c084fc; border: 1px solid rgba(168,85,247,0.25); }
    .badge-data    { background: rgba(16,185,129,0.1);  color: #34d399; border: 1px solid rgba(16,185,129,0.25); }
    .badge-default { background: rgba(100,116,139,0.1); color: #94a3b8; border: 1px solid rgba(100,116,139,0.25); }

    .job-title {
        font-family: 'Orbitron', sans-serif;
        font-size: 13px;
        font-weight: 700;
        color: #e2e8f0;
        margin-bottom: 6px;
    }

    .job-company {
        font-size: 12px;
        color: #94a3b8;
        display: flex;
        align-items: center;
        gap: 6px;
    }

    .company-dot {
        width: 6px; height: 6px;
        border-radius: 50%;
        background: #38bdf8;
        box-shadow: 0 0 6px rgba(56,189,248,0.8);
        display: inline-block;
    }

    .card-body {
        padding: 14px 18px;
    }

    .job-desc {
        font-size: 11px;
        color: #64748b;
        line-height: 1.6;
        margin-bottom: 12px;
    }

    .skills-row {
        display: flex;
        flex-wrap: wrap;
        gap: 5px;
        margin-bottom: 12px;
    }

    .skill {
        background: rgba(6,182,212,0.07);
        border: 1px solid rgba(6,182,212,0.2);
        border-radius: 6px;
        padding: 3px 9px;
        font-size: 10px;
        color: #67e8f9;
        letter-spacing: 0.5px;
    }

    .card-footer {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-top: 4px;
    }

    .exp-tag {
        font-size: 11px;
        color: #475569;
    }

    .exp-tag span {
        color: #38bdf8;
        font-weight: 600;
    }
    </style>
    """, unsafe_allow_html=True)

    # ── fetch data ──────────────────────────────────────────────
    response = list_jobs()
    if response.status_code != 200:
        st.error("Could not load jobs.")
        st.stop()

    jobs = response.json()

    resume_response = my_resumes()
    resumes = resume_response.json() if resume_response.status_code == 200 else []
    resume_options = {r["file_name"]: r["id"] for r in resumes}

    # ── header ──────────────────────────────────────────────────
    st.markdown(f"""
    <div class="page-header">
        <div class="page-title">💼 Available Jobs</div>
        <div class="job-count">{len(jobs)} opening{"s" if len(jobs) != 1 else ""}</div>
    </div>
    """, unsafe_allow_html=True)

    # ── search bar ──────────────────────────────────────────────
    search = st.text_input("", placeholder="🔍  Search jobs, skills, companies...", label_visibility="collapsed")

    st.markdown('<div class="neon-line"></div>', unsafe_allow_html=True)

    if not jobs:
        st.info("No jobs available right now.")
        st.stop()

    # ── filter by search ────────────────────────────────────────
    if search:
        q = search.lower()
        jobs = [
            j for j in jobs
            if q in j.get("title", "").lower()
            or q in j.get("company", "").lower()
            or q in j.get("required_skills", "").lower()
            or q in j.get("description", "").lower()
        ]
        if not jobs:
            st.info("No jobs match your search.")
            st.stop()

    # ── badge helper ────────────────────────────────────────────
    def get_badge(job):
        title = job.get("title", "").lower()
        skills = job.get("required_skills", "").lower()
        if any(k in title + skills for k in ["data", "sql", "analytics", "statistics", "tableau", "r,"]):
            return "badge-data", "Data"
        if any(k in title + skills for k in ["design", "figma", "ux", "ui", "prototype"]):
            return "badge-design", "Design"
        if any(k in title + skills for k in ["python", "ml", "ai", "engineer", "backend", "frontend", "cloud", "devops"]):
            return "badge-tech", "Tech"
        return "badge-default", "General"

    # ── skills helper ───────────────────────────────────────────
    def render_skills(skills_str):
        if not skills_str:
            return ""
        skills = [s.strip() for s in skills_str.split(",") if s.strip()]
        return "".join(f'<div class="skill">{s}</div>' for s in skills)

    # ── job cards ───────────────────────────────────────────────
    for job in jobs:
        badge_class, badge_label = get_badge(job)
        skills_html = render_skills(job.get("required_skills", ""))
        exp = job.get("min_experience", 0)

        st.markdown(f"""
        <div class="job-card">
            <div class="card-top">
                <div class="card-badge {badge_class}">{badge_label}</div>
                <div class="job-title">{job.get("title", "Untitled")}</div>
                <div class="job-company">
                    <div class="company-dot"></div>
                    {job.get("company", "Unknown")}
                </div>
            </div>
            <div class="card-body">
                <div class="job-desc">{job.get("description", "")}</div>
                <div class="skills-row">{skills_html}</div>
                <div class="card-footer">
                    <div class="exp-tag">Min exp: <span>{exp} yr{"s" if exp != 1 else ""}</span></div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # apply controls (Streamlit widgets — can't live inside HTML)
        if resumes:
            col1, col2 = st.columns([3, 1])
            with col1:
                selected_resume = st.selectbox(
                    "Resume",
                    list(resume_options.keys()),
                    key=f"resume_{job['id']}",
                    label_visibility="collapsed",
                )
            with col2:
                if st.button("🚀 Apply", key=f"apply_{job['id']}", use_container_width=True):
                    resume_id = resume_options[selected_resume]
                    apply_response = apply_to_job(job["id"], resume_id)
                    if apply_response.status_code in [200, 201]:
                        st.success("Application submitted!")
                    else:
                        try:
                            st.error(apply_response.json().get("detail", "Application failed."))
                        except Exception:
                            st.error("Application failed.")
        else:
            st.info("Upload a resume first before applying.")

        st.markdown("<div style='margin-bottom:8px'></div>", unsafe_allow_html=True)