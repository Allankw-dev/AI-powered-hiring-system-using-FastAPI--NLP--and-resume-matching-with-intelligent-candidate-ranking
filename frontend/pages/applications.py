import streamlit as st
from api import list_jobs, my_resumes, apply_to_job, my_applications


def render():
    st.markdown("""
    <style>
    .page-title {
        font-size: 38px;
        font-weight: 800;
        color: #ffffff;
        margin-bottom: 6px;
    }

    .page-subtitle {
        font-size: 16px;
        color: #cbd5e1;
        margin-bottom: 24px;
    }

    .card {
        background: linear-gradient(135deg, #1e293b, #0f172a);
        border: 1px solid #334155;
        border-radius: 20px;
        padding: 24px;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.25);
        margin-bottom: 20px;
    }

    .card-title {
        font-size: 22px;
        font-weight: 700;
        color: #f8fafc;
        margin-bottom: 14px;
    }

    .small-text {
        color: #94a3b8;
        font-size: 14px;
        margin-bottom: 10px;
    }

    div.stButton > button {
        width: 100%;
        background: linear-gradient(90deg, #2563eb, #7c3aed);
        color: white;
        font-size: 16px;
        font-weight: 600;
        border: none;
        border-radius: 12px;
        padding: 12px 18px;
        transition: 0.3s ease;
    }

    div.stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.25);
    }

    .info-box {
        padding: 12px 14px;
        border-radius: 12px;
        background: #1d4ed8;
        color: white;
        font-weight: 500;
        margin-top: 10px;
    }

    .warning-box {
        padding: 12px 14px;
        border-radius: 12px;
        background: #92400e;
        color: white;
        font-weight: 500;
        margin-top: 10px;
    }

    .success-box {
        padding: 12px 14px;
        border-radius: 12px;
        background: #166534;
        color: white;
        font-weight: 500;
        margin-top: 10px;
    }

    .section-divider {
        margin-top: 12px;
        margin-bottom: 12px;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="page-title"> My Applications</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="page-subtitle">Apply for open jobs using your uploaded resumes and track your submitted applications.</div>',
        unsafe_allow_html=True
    )

    if "token" not in st.session_state or not st.session_state.get("token"):
        st.markdown('<div class="warning-box">Please log in first.</div>', unsafe_allow_html=True)
        return

    jobs_response = list_jobs()
    resumes_response = my_resumes()

    if jobs_response.status_code != 200:
        try:
            st.error(jobs_response.json().get("detail", "Could not load jobs."))
        except Exception:
            st.error(jobs_response.text if jobs_response.text else "Could not load jobs.")
        return

    if resumes_response.status_code != 200:
        try:
            st.error(resumes_response.json().get("detail", "Could not load resumes."))
        except Exception:
            st.error(resumes_response.text if resumes_response.text else "Could not load resumes.")
        return

    jobs = jobs_response.json()
    resumes = resumes_response.json()

    if not jobs:
        st.markdown('<div class="info-box">No jobs available at the moment.</div>', unsafe_allow_html=True)
        return

    if not resumes:
        st.markdown('<div class="warning-box">Upload a resume before applying.</div>', unsafe_allow_html=True)
        return

    left_col, right_col = st.columns([1.5, 1])

    with left_col:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">Apply for a Job</div>', unsafe_allow_html=True)
        st.markdown('<div class="small-text">Select a job and choose the resume you want to use for that application.</div>', unsafe_allow_html=True)

        job_options = {
            f"{j['id']} - {j['title']} at {j['company']}": j["id"]
            for j in jobs
        }
        resume_options = {
            f"{r['id']} - {r['file_name']}": r["id"]
            for r in resumes
        }

        selected_job = st.selectbox("Select Job", list(job_options.keys()))
        selected_resume = st.selectbox("Select Resume", list(resume_options.keys()))

        if st.button("Apply Now"):
            job_id = job_options[selected_job]
            resume_id = resume_options[selected_resume]

            response = apply_to_job(job_id, resume_id)

            if response.status_code in [200, 201]:
                st.markdown('<div class="success-box">Application submitted successfully.</div>', unsafe_allow_html=True)
                st.rerun()
            else:
                try:
                    st.error(response.json().get("detail", "Application failed"))
                except Exception:
                    st.error(response.text if response.text else "Application failed")

        st.markdown('</div>', unsafe_allow_html=True)

    with right_col:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">Quick Tips</div>', unsafe_allow_html=True)
        st.markdown("""
        <div class="small-text">
        • Choose the resume that best matches the job.<br><br>
        • Make sure your uploaded CV is updated.<br><br>
        • Apply carefully to roles that fit your skills.<br><br>
        • Track your applications below after submission.
        </div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    st.markdown("###  My Submitted Applications")

    apps_response = my_applications()
    if apps_response.status_code == 200:
        apps = apps_response.json()
        if apps:
            st.dataframe(apps, use_container_width=True)
        else:
            st.info("No applications yet.")
    else:
        try:
            st.error(apps_response.json().get("detail", "Could not load applications."))
        except Exception:
            st.error(apps_response.text if apps_response.text else "Could not load applications.")