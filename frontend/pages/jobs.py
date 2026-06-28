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
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;600;700;900&family=Exo+2:wght@300;400;600;700&display=swap');

    .stApp {
        background: #000510 !important;
        background-image:
            radial-gradient(ellipse at 20% 50%, rgba(0,100,255,0.12) 0%, transparent 50%),
            radial-gradient(ellipse at 80% 20%, rgba(0,200,220,0.1) 0%, transparent 45%) !important;
    }

    [data-testid="stAppViewContainer"] { background: transparent !important; }
    [data-testid="stHeader"] { background: transparent !important; }

    .page-header {
        display: flex; align-items: center; justify-content: space-between;
        margin-bottom: 24px;
    }

    .page-title {
        font-family: 'Orbitron', sans-serif;
        font-size: 1.5rem; font-weight: 900;
        background: linear-gradient(90deg, #38bdf8, #06b6d4);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        letter-spacing: 2px;
    }

    .job-count {
        font-size: 12px; color: #38bdf8;
        background: rgba(56,189,248,0.1);
        border: 1px solid rgba(56,189,248,0.3);
        border-radius: 999px; padding: 4px 14px;
        font-family: 'Exo 2', sans-serif; letter-spacing: 1px;
    }

    .neon-divider {
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(56,189,248,0.4), rgba(6,182,212,0.4), transparent);
        margin: 16px 0; border: none;
    }

    .jobs-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
        gap: 16px;
        margin-bottom: 20px;
    }

    .job-card {
        background: rgba(4,6,22,0.85);
        border: 1px solid rgba(56,189,248,0.15);
        border-radius: 16px; overflow: hidden;
        transition: all 0.3s ease;
        backdrop-filter: blur(12px);
        position: relative;
    }

    .job-card::before {
        content: '';
        position: absolute; top: 0; left: 0; right: 0; height: 2px;
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
        display: inline-block; font-size: 10px;
        font-family: 'Exo 2', sans-serif;
        letter-spacing: 1.5px; text-transform: uppercase;
        padding: 3px 10px; border-radius: 999px; margin-bottom: 10px;
        background: rgba(56,189,248,0.1); color: #38bdf8;
        border: 1px solid rgba(56,189,248,0.25);
    }

    .job-title {
        font-family: 'Orbitron', sans-serif;
        font-size: 13px; font-weight: 700;
        color: #e2e8f0; margin-bottom: 6px;
    }

    .job-company {
        font-size: 12px; color: #94a3b8;
        display: flex; align-items: center; gap: 6px;
        font-family: 'Exo 2', sans-serif;
    }

    .company-dot {
        width: 6px; height: 6px; border-radius: 50%;
        background: #38bdf8; box-shadow: 0 0 6px rgba(56,189,248,0.8);
        flex-shrink: 0;
    }

    .card-body { padding: 14px 18px; }

    .job-desc {
        font-family: 'Exo 2', sans-serif;
        font-size: 12px; color: #64748b;
        line-height: 1.6; margin-bottom: 12px;
    }

    .skills-row { display: flex; flex-wrap: wrap; gap: 5px; margin-bottom: 14px; }

    .skill {
        background: rgba(6,182,212,0.07);
        border: 1px solid rgba(6,182,212,0.2);
        border-radius: 6px; padding: 3px 9px;
        font-size: 10px; color: #67e8f9;
        font-family: 'Exo 2', sans-serif; letter-spacing: 0.5px;
    }

    .exp-tag {
        font-family: 'Exo 2', sans-serif;
        font-size: 11px; color: #475569;
        margin-bottom: 12px;
    }

    .exp-tag span { color: #38bdf8; font-weight: 700; }

    @media (max-width: 640px) {
        .page-title { font-size: 1.1rem; }
        .jobs-grid { grid-template-columns: 1fr; }
    }
    </style>
    """, unsafe_allow_html=True)

    # ── FETCH DATA ──
    response = list_jobs()
    if response.status_code != 200:
        st.error("Could not load jobs.")
        st.stop()

    jobs = response.json()
    if not jobs:
        st.info("No jobs available right now.")
        st.stop()

    resume_response = my_resumes()
    resumes = resume_response.json() if resume_response.status_code == 200 else []
    resume_options = {r["file_name"]: r["id"] for r in resumes}

    # ── HEADER ──
    st.markdown(f"""
    <div class="page-header">
        <div class="page-title">💼 Available Jobs</div>
        <div class="job-count">{len(jobs)} opening{"s" if len(jobs) != 1 else ""}</div>
    </div>
    <hr class="neon-divider">
    """, unsafe_allow_html=True)

    # ── JOB CARDS GRID ──
    # Render cards in rows of 2 using st.columns for button interactivity
    cols_per_row = 2
    for i in range(0, len(jobs), cols_per_row):
        row_jobs = jobs[i:i + cols_per_row]
        cols = st.columns(len(row_jobs))

        for col, job in zip(cols, row_jobs):
            with col:
                skills = job.get("required_skills", "")
                skill_chips = "".join(
                    f'<span class="skill">{s.strip()}</span>'
                    for s in skills.split(",") if s.strip()
                ) if skills else '<span class="skill">Not specified</span>'

                st.markdown(f"""
                <div class="job-card">
                    <div class="card-top">
                        <div class="card-badge">// Position</div>
                        <div class="job-title">{job["title"]}</div>
                        <div class="job-company">
                            <div class="company-dot"></div>
                            {job.get("company", "Unknown")}
                        </div>
                    </div>
                    <div class="card-body">
                        <div class="job-desc">{job.get("description", "No description provided.")}</div>
                        <div class="skills-row">{skill_chips}</div>
                        <div class="exp-tag">Min experience: <span>{job.get("min_experience", 0)} yrs</span></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                if resumes:
                    selected_resume = st.selectbox(
                        "Resume",
                        list(resume_options.keys()),
                        key=f"resume_{job['id']}",
                        label_visibility="collapsed",
                    )
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
                    st.info("Upload a resume first.")

        st.markdown("<br>", unsafe_allow_html=True)