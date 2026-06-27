import requests
import streamlit as st

API_BASE_URL = st.secrets.get("API_URL", "http://localhost:8000")
REQUEST_TIMEOUT = 60


# ------------------------------
# AUTH HEADERS
# ------------------------------
def get_headers():
    token = st.session_state.get("token")
    if token:
        return {"Authorization": f"Bearer {token}"}
    return {}


def get_headers_without_content_type():
    token = st.session_state.get("token")
    if token:
        return {"Authorization": f"Bearer {token}"}
    return {}


# ------------------------------
# AUTH ROUTES
# ------------------------------
def sign_up(full_name, email, password, sex):
    return requests.post(
        f"{API_BASE_URL}/auth/signup",
        json={
            "full_name": full_name,
            "email": email,
            "password": password,
            "sex": sex
        },
        timeout=REQUEST_TIMEOUT
    )


def login(email, password):
    return requests.post(
        f"{API_BASE_URL}/auth/login",
        json={
            "email": email,
            "password": password
        },
        timeout=REQUEST_TIMEOUT
    )


def admin_request_otp(email, password):
    return requests.post(
        f"{API_BASE_URL}/auth/admin/request-otp",
        json={
            "email": email,
            "password": password
        },
        timeout=REQUEST_TIMEOUT
    )


def admin_verify_otp(email, otp_code):
    return requests.post(
        f"{API_BASE_URL}/auth/admin/verify-otp",
        json={
            "email": email,
            "otp_code": otp_code
        },
        timeout=REQUEST_TIMEOUT
    )


# ------------------------------
# JOB ROUTES
# ------------------------------
def list_jobs():
    return requests.get(
        f"{API_BASE_URL}/jobs/",
        headers=get_headers(),
        timeout=REQUEST_TIMEOUT
    )


def get_job(job_id):
    return requests.get(
        f"{API_BASE_URL}/jobs/{job_id}",
        headers=get_headers(),
        timeout=REQUEST_TIMEOUT
    )


def create_job(title, company, description, required_skills, min_experience):
    return requests.post(
        f"{API_BASE_URL}/jobs/",
        headers=get_headers(),
        json={
            "title": title,
            "company": company,
            "description": description,
            "required_skills": required_skills,
            "min_experience": min_experience
        },
        timeout=REQUEST_TIMEOUT
    )
def update_job(job_id, title, company, description, required_skills, min_experience):
    return requests.put(
        f"{API_BASE_URL}/jobs/{job_id}",
        headers=get_headers(),
        json={
            "title": title,
            "company": company,
            "description": description,
            "required_skills": required_skills,
            "min_experience": min_experience
        },
        timeout=REQUEST_TIMEOUT
    )

def delete_job(job_id):
    return requests.delete(
        f"{API_BASE_URL}/jobs/{job_id}",
        headers=get_headers(),
        timeout=REQUEST_TIMEOUT
    )


# ------------------------------
# RESUME ROUTES
# ------------------------------
def upload_resume(file):
    return requests.post(
        f"{API_BASE_URL}/resumes/upload",
        headers=get_headers_without_content_type(),
        files={"file": (file.name, file, file.type)},
        timeout=REQUEST_TIMEOUT
    )


def my_resumes():
    return requests.get(
        f"{API_BASE_URL}/resumes/my",
        headers=get_headers(),
        timeout=REQUEST_TIMEOUT
    )


# ------------------------------
# APPLICATION ROUTES
# ------------------------------
def apply_to_job(job_id, resume_id):
    return requests.post(
        f"{API_BASE_URL}/applications/",
        headers=get_headers(),
        json={
            "job_id": job_id,
            "resume_id": resume_id
        },
        timeout=REQUEST_TIMEOUT
    )


def my_applications():
    return requests.get(
        f"{API_BASE_URL}/applications/my",
        headers=get_headers(),
        timeout=REQUEST_TIMEOUT
    )


# ------------------------------
# ADMIN ROUTES
# ------------------------------
def top_candidates():
    return requests.get(
        f"{API_BASE_URL}/admin/top-candidates",
        headers=get_headers(),
        timeout=REQUEST_TIMEOUT
    )


def shortlist_candidate(application_id):
    return requests.post(
        f"{API_BASE_URL}/admin/shortlist/{application_id}",
        headers=get_headers(),
        timeout=REQUEST_TIMEOUT
    )


def reject_candidate(application_id):
    return requests.post(
        f"{API_BASE_URL}/admin/reject/{application_id}",
        headers=get_headers(),
        timeout=REQUEST_TIMEOUT
    )


def send_candidate_email(application_id, subject, message_body):
    return requests.post(
        f"{API_BASE_URL}/admin/send-email",
        headers=get_headers(),
        json={
            "application_id": application_id,
            "subject": subject,
            "message_body": message_body
        },
        timeout=REQUEST_TIMEOUT
    )


# ------------------------------
# PROFILE ROUTES
# ------------------------------
def get_my_profile():
    return requests.get(
        f"{API_BASE_URL}/users/me",
        headers=get_headers(),
        timeout=REQUEST_TIMEOUT
    )


def update_my_profile(full_name, email):
    return requests.put(
        f"{API_BASE_URL}/users/me",
        headers=get_headers(),
        json={
            "full_name": full_name,
            "email": email
        },
        timeout=REQUEST_TIMEOUT
    )


def upload_profile_picture(file):
    return requests.post(
        f"{API_BASE_URL}/profile/me/upload-picture",
        headers=get_headers_without_content_type(),
        files={"file": (file.name, file, file.type)},
        timeout=REQUEST_TIMEOUT
    )


# ------------------------------
# PASSWORD RESET ROUTES
# ------------------------------
def forgot_password(email):
    return requests.post(
        f"{API_BASE_URL}/password/forgot",
        json={"email": email},
        timeout=REQUEST_TIMEOUT
    )


def reset_password(token, new_password):
    return requests.post(
        f"{API_BASE_URL}/password/reset",
        json={
            "token": token,
            "new_password": new_password
        },
        timeout=REQUEST_TIMEOUT
    )