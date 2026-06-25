import streamlit as st
from api import (
    top_candidates,
    shortlist_candidate,
    reject_candidate,
    send_candidate_email,
    create_job,
    list_jobs,
    update_job,
    delete_job
)


def render():
    st.markdown("""
    <style>
    .section-card {
        background: rgba(255, 255, 255, 0.08);
        padding: 1.2rem;
        border-radius: 18px;
        box-shadow: 0 8px 24px rgba(0,0,0,0.22);
        backdrop-filter: blur(8px);
        margin-bottom: 1rem;
        border: 1px solid rgba(255,255,255,0.08);
    }
    .page-title {
        color: white;
        font-size: 2.2rem;
        font-weight: 700;
        margin-bottom: 0.3rem;
    }
    .page-subtitle {
        color: #cbd5e1;
        margin-bottom: 1.2rem;
    }
    .info-box {
        background: rgba(37, 99, 235, 0.16);
        border: 1px solid rgba(96, 165, 250, 0.25);
        color: #dbeafe;
        padding: 0.9rem 1rem;
        border-radius: 14px;
        margin-bottom: 1rem;
    }
    .job-card {
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 16px;
        padding: 16px;
        margin-bottom: 12px;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="page-title">🛡️ Admin Panel</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="page-subtitle">Manage jobs, review candidates, and communicate with applicants.</div>',
        unsafe_allow_html=True
    )

    if "token" not in st.session_state or not st.session_state.get("token"):
        st.warning("Please log in first.")
        return

    role = st.session_state.get("role", "")
    email = st.session_state.get("user_email", "Unknown admin")

    if role != "admin":
        st.error("Access denied. Admin only.")
        return

    st.markdown(
        f'<div class="info-box">✅ Logged in as <strong>Admin</strong> • {email}</div>',
        unsafe_allow_html=True
    )

    tab1, tab2 = st.tabs(["📢 Post Jobs", "🏆 Candidate Review"])

    with tab1:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.subheader("Post a New Job")

        with st.form("create_job_form"):
            title = st.text_input("Job Title")
            company = st.text_input("Company Name")
            description = st.text_area("Job Description", height=180)
            required_skills = st.text_input("Required Skills (comma separated)")
            min_experience = st.number_input(
                "Minimum Experience (Years)",
                min_value=0,
                max_value=50,
                step=1
            )
            submitted = st.form_submit_button("Post Job")

        if submitted:
            if not title.strip() or not company.strip() or not description.strip():
                st.warning("Please fill in Job Title, Company Name, and Description.")
            else:
                response = create_job(
                    title=title,
                    company=company,
                    description=description,
                    required_skills=required_skills,
                    min_experience=min_experience
                )
                if response.status_code in [200, 201]:
                    st.success("Job posted successfully.")
                    st.rerun()
                else:
                    try:
                        st.error(response.json().get("detail", "Failed to post job"))
                    except Exception:
                        st.error("Failed to post job")

        st.markdown("---")
        st.subheader("Available Jobs")

        jobs_response = list_jobs()
        if jobs_response.status_code == 200:
            jobs = jobs_response.json()
            if not jobs:
                st.info("No jobs have been posted yet.")
            else:
                for job in jobs:
                    with st.expander(f"📋 {job.get('title')} — {job.get('company')}"):
                        st.markdown(f"**Description:** {job.get('description', 'N/A')}")
                        st.markdown(f"**Required Skills:** {job.get('required_skills', 'N/A')}")
                        st.markdown(f"**Min Experience:** {job.get('min_experience', 0)} years")

                        col1, col2 = st.columns(2)

                        with col1:
                            if st.button("✏️ Edit", key=f"edit_{job['id']}"):
                                st.session_state[f"editing_{job['id']}"] = True

                        with col2:
                            if st.button("🗑️ Delete", key=f"delete_{job['id']}"):
                                r = delete_job(job["id"])
                                if r.status_code == 200:
                                    st.success("Job deleted.")
                                    st.rerun()
                                else:
                                    st.error("Failed to delete job.")

                        if st.session_state.get(f"editing_{job['id']}"):
                            with st.form(key=f"edit_form_{job['id']}"):
                                new_title = st.text_input("Title", value=job.get("title", ""))
                                new_company = st.text_input("Company", value=job.get("company", ""))
                                new_description = st.text_area("Description", value=job.get("description", ""), height=150)
                                new_skills = st.text_input("Required Skills", value=job.get("required_skills", ""))
                                new_experience = st.number_input("Min Experience", value=int(job.get("min_experience", 0)), min_value=0)
                                save = st.form_submit_button("💾 Save Changes")
                                cancel = st.form_submit_button("Cancel")

                            if save:
                                r = update_job(job["id"], new_title, new_company, new_description, new_skills, new_experience)
                                if r.status_code == 200:
                                    st.success("Job updated!")
                                    st.session_state[f"editing_{job['id']}"] = False
                                    st.rerun()
                                else:
                                    st.error("Failed to update job.")

                            if cancel:
                                st.session_state[f"editing_{job['id']}"] = False
                                st.rerun()
        else:
            st.warning("Could not load jobs.")

        st.markdown('</div>', unsafe_allow_html=True)

    with tab2:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.subheader("Top 20 Candidates by Score")

        response = top_candidates()
        if response.status_code != 200:
            try:
                st.error(response.json().get("detail", "Admin access required"))
            except Exception:
                st.error("Admin access required")
            st.markdown('</div>', unsafe_allow_html=True)
            return

        candidates = response.json()
        if not candidates:
            st.info("No candidates found.")
            st.markdown('</div>', unsafe_allow_html=True)
            return

        st.dataframe(candidates, use_container_width=True)

        st.markdown("---")
        st.subheader("Review Candidate")

        option_map = {
            f"{c['application_id']} - {c['applicant_name']} ({c['overall_score']})": c
            for c in candidates
        }

        selected_label = st.selectbox("Select Candidate", list(option_map.keys()))
        selected = option_map[selected_label]

        col1, col2 = st.columns(2)

        with col1:
            st.write("**Applicant:**", selected.get("applicant_name", "N/A"))
            st.write("**Email:**", selected.get("applicant_email", "N/A"))
            st.write("**Job:**", f"{selected.get('job_title', 'N/A')} at {selected.get('company', 'N/A')}")
            st.write("**Status:**", selected.get("status", "N/A"))

        with col2:
            st.write("**Overall Score:**", selected.get("overall_score", "N/A"))
            st.write("**Semantic Score:**", selected.get("semantic_score", "N/A"))
            st.write("**Skills Score:**", selected.get("skills_score", "N/A"))
            st.write("**Experience Score:**", selected.get("experience_score", "N/A"))
            st.write("**Verification Score:**", selected.get("verification_score", "N/A"))

        action_col1, action_col2 = st.columns(2)

        with action_col1:
            if st.button("Shortlist Candidate"):
                r = shortlist_candidate(selected["application_id"])
                if r.status_code == 200:
                    st.success("Candidate shortlisted.")
                    st.rerun()
                else:
                    try:
                        st.error(r.json().get("detail", "Could not shortlist candidate"))
                    except Exception:
                        st.error("Could not shortlist candidate")

        with action_col2:
            if st.button("Reject Candidate"):
                r = reject_candidate(selected["application_id"])
                if r.status_code == 200:
                    st.success("Candidate rejected.")
                    st.rerun()
                else:
                    try:
                        st.error(r.json().get("detail", "Could not reject candidate"))
                    except Exception:
                        st.error("Could not reject candidate")

        st.markdown("---")
        st.subheader("Send Email to Candidate")

        default_subject = "Application Update - You Have Been Shortlisted"
        default_body = f"""Dear {selected.get('applicant_name', 'Candidate')},

We are pleased to inform you that after reviewing your application, you have been shortlisted for the next stage of our hiring process.

We will contact you soon with further details.

Best regards,
Admin
AI Hiring Platform
"""

        subject = st.text_input("Email Subject", value=default_subject)
        message_body = st.text_area("Email Body", value=default_body, height=220)

        if st.button("Send Email"):
            r = send_candidate_email(selected["application_id"], subject, message_body)
            if r.status_code == 200:
                st.success("Email sent successfully.")
            else:
                try:
                    st.error(r.json().get("detail", "Failed to send email"))
                except Exception:
                    st.error("Failed to send email")

        st.markdown('</div>', unsafe_allow_html=True)