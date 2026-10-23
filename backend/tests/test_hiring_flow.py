import json

from tests.conftest import PASSWORD, make_user, minimal_pdf

CV = (
    "Jane Doe  jane@example.com  +254 712 345678\n"
    "Backend developer with 3 years of experience building REST APIs.\n"
    "Skills: Python, FastAPI, PostgreSQL, Docker, Git, Linux, SQL.\n"
    "Experience: Backend Developer at Acme 2022 - 2025. Built and deployed microservices, "
    "wrote unit tests, improved performance of database queries and mentored interns. " * 3
)


def create_job(client, admin_headers, **overrides):
    body = {
        "title": "Backend Engineer", "company": "Acme",
        "description": "Build Python backend services with FastAPI and PostgreSQL for our customers.",
        "required_skills": "Python, FastAPI, PostgreSQL, Kubernetes", "min_experience": 2,
    }
    body.update(overrides)
    r = client.post("/jobs/", json=body, headers=admin_headers)
    assert r.status_code == 201, r.text
    return r.json()


def upload_txt(client, headers, text=CV, name="cv.txt"):
    return client.post("/resumes/upload", headers=headers, files={"file": (name, text.encode(), "text/plain")})


# ── permissions ──
def test_candidates_cannot_manage_jobs_or_see_admin_endpoints(client, candidate_headers):
    body = {"title": "Hack", "company": "X", "description": "x" * 20}
    assert client.post("/jobs/", json=body, headers=candidate_headers).status_code == 403
    assert client.get("/admin/top-candidates", headers=candidate_headers).status_code == 403
    assert client.post("/admin/jobs/1/rescore", headers=candidate_headers).status_code == 403
    assert client.get("/jobs/").status_code in (401, 403)  # no token


def test_job_validation(client, admin_headers):
    r = client.post("/jobs/", json={"title": "x", "company": "", "description": "short"}, headers=admin_headers)
    assert r.status_code == 422
    r = client.post("/jobs/", json={"title": "Dev", "company": "A", "description": "x" * 20, "min_experience": -3}, headers=admin_headers)
    assert r.status_code == 422


# ── resume upload ──
def test_upload_txt_and_pdf(client, candidate_headers):
    r = upload_txt(client, candidate_headers)
    assert r.status_code == 200, r.text
    data = r.json()
    assert "python" in data["skills"] and data["experience_years"] == 3.0

    pdf = minimal_pdf("Jane Doe python developer with 5 years of experience. " * 5)
    r = client.post("/resumes/upload", headers=candidate_headers, files={"file": ("my cv.pdf", pdf, "application/pdf")})
    assert r.status_code == 200, r.text
    assert r.json()["file_name"] == "my cv.pdf" and r.json()["experience_years"] == 5.0


def test_upload_rejections(client, candidate_headers):
    assert client.post("/resumes/upload", headers=candidate_headers, files={"file": ("evil.exe", b"MZ", "application/octet-stream")}).status_code == 400
    assert client.post("/resumes/upload", headers=candidate_headers, files={"file": ("fake.pdf", b"not a pdf at all", "application/pdf")}).status_code == 400
    assert client.post("/resumes/upload", headers=candidate_headers, files={"file": ("empty.txt", b"", "text/plain")}).status_code == 400
    big = b"a" * (5 * 1024 * 1024 + 10)
    assert client.post("/resumes/upload", headers=candidate_headers, files={"file": ("big.txt", big, "text/plain")}).status_code == 413


def test_path_traversal_filename_is_neutralised(client, candidate_headers):
    r = upload_txt(client, candidate_headers, name="../../../../etc/passwd.txt")
    assert r.status_code == 200
    assert "/" not in r.json()["file_name"] and ".." not in r.json()["file_name"].replace("...", "")


def test_duplicate_is_per_user_and_cross_account_reuse_is_flagged(client, db, candidate_headers):
    assert upload_txt(client, candidate_headers).status_code == 200
    dup = upload_txt(client, candidate_headers)
    assert dup.status_code == 400 and "already uploaded" in dup.json()["detail"]

    make_user(db, "other@example.com")
    tok = client.post("/auth/login", json={"email": "other@example.com", "password": PASSWORD}).json()["access_token"]
    r = upload_txt(client, {"Authorization": f"Bearer {tok}"})
    assert r.status_code == 200
    assert "resume_used_by_another_account" in r.json()["risk_flags"]


def test_delete_resume_rules(client, admin_headers, candidate_headers):
    rid = upload_txt(client, candidate_headers).json()["id"]
    assert client.delete(f"/resumes/{rid}", headers=candidate_headers).status_code == 200
    rid = upload_txt(client, candidate_headers).json()["id"]
    job = create_job(client, admin_headers)
    client.post("/applications/", json={"job_id": job["id"], "resume_id": rid}, headers=candidate_headers)
    assert client.delete(f"/resumes/{rid}", headers=candidate_headers).status_code == 409


# ── applications / ranking ──
def test_apply_scores_ranks_and_hides_rank_from_candidates(client, db, admin_headers, candidate_headers):
    job = create_job(client, admin_headers)
    rid = upload_txt(client, candidate_headers).json()["id"]

    r = client.post("/applications/", json={"job_id": job["id"], "resume_id": rid}, headers=candidate_headers)
    assert r.status_code == 200, r.text
    res = r.json()
    assert set(res["matched_skills"]) == {"python", "fastapi", "postgresql"}
    assert res["missing_skills"] == ["kubernetes"]
    assert res["skills_score"] == 75.0 and res["experience_score"] == 100.0
    assert res["ranking_position"] == 1 and res["ranking_label"]

    # second candidate with a weaker CV ranks below
    make_user(db, "weak@example.com")
    tok = client.post("/auth/login", json={"email": "weak@example.com", "password": PASSWORD}).json()["access_token"]
    weak_h = {"Authorization": f"Bearer {tok}"}
    weak_rid = upload_txt(client, weak_h, text="Graphic designer. Photoshop, Illustrator, branding. " * 12).json()["id"]
    client.post("/applications/", json={"job_id": job["id"], "resume_id": weak_rid}, headers=weak_h)

    top = client.get("/admin/top-candidates", headers=admin_headers).json()
    assert [t["applicant_email"] for t in top] == ["cand@example.com", "weak@example.com"]
    assert [t["ranking_position"] for t in top] == [1, 2]
    assert set(top[0]["matched_skills"]) == {"python", "fastapi", "postgresql"}
    assert len(client.get(f"/admin/top-candidates?job_id={job['id']}&limit=1", headers=admin_headers).json()) == 1
    assert client.get("/admin/top-candidates?job_id=9999", headers=admin_headers).json() == []

    mine = client.get("/applications/my", headers=candidate_headers).json()
    assert len(mine) == 1 and "ranking_position" not in mine[0] and mine[0]["missing_skills"] == ["kubernetes"]


def test_cannot_apply_twice_or_with_someone_elses_resume(client, db, admin_headers, candidate_headers):
    job = create_job(client, admin_headers)
    rid = upload_txt(client, candidate_headers).json()["id"]
    body = {"job_id": job["id"], "resume_id": rid}
    assert client.post("/applications/", json=body, headers=candidate_headers).status_code == 200
    assert client.post("/applications/", json=body, headers=candidate_headers).status_code == 400

    make_user(db, "thief@example.com")
    tok = client.post("/auth/login", json={"email": "thief@example.com", "password": PASSWORD}).json()["access_token"]
    assert client.post("/applications/", json=body, headers={"Authorization": f"Bearer {tok}"}).status_code == 404


def test_rescore_after_editing_the_job(client, admin_headers, candidate_headers):
    job = create_job(client, admin_headers)
    rid = upload_txt(client, candidate_headers).json()["id"]
    before = client.post("/applications/", json={"job_id": job["id"], "resume_id": rid}, headers=candidate_headers).json()

    edit = {**job, "required_skills": "Python, FastAPI, PostgreSQL"}
    edit.pop("id")
    assert client.put(f"/jobs/{job['id']}", json=edit, headers=admin_headers).status_code == 200
    r = client.post(f"/admin/jobs/{job['id']}/rescore", headers=admin_headers)
    assert r.status_code == 200 and r.json()["rescored"] == 1

    top = client.get("/admin/top-candidates", headers=admin_headers).json()[0]
    assert top["skills_score"] == 100.0 and top["overall_score"] > before["overall_score"]
    assert top["missing_skills"] == []


def test_job_with_applications_cannot_be_deleted(client, admin_headers, candidate_headers):
    job = create_job(client, admin_headers)
    rid = upload_txt(client, candidate_headers).json()["id"]
    client.post("/applications/", json={"job_id": job["id"], "resume_id": rid}, headers=candidate_headers)
    assert client.delete(f"/jobs/{job['id']}", headers=admin_headers).status_code == 409
    empty = create_job(client, admin_headers, title="Other")
    assert client.delete(f"/jobs/{empty['id']}", headers=admin_headers).status_code == 200


def test_shortlist_reject_and_email(client, admin_headers, candidate_headers, monkeypatch):
    sent = []
    monkeypatch.setattr("app.routers.admin.send_admin_email", lambda **kw: sent.append(kw))
    job = create_job(client, admin_headers)
    rid = upload_txt(client, candidate_headers).json()["id"]
    app_id = client.post("/applications/", json={"job_id": job["id"], "resume_id": rid}, headers=candidate_headers).json()["application_id"]

    assert client.post(f"/admin/applications/{app_id}/shortlist", headers=admin_headers).status_code == 200
    assert client.get("/admin/top-candidates", headers=admin_headers).json()[0]["status"] == "shortlisted"
    assert client.post(f"/admin/applications/{app_id}/reject", headers=admin_headers).status_code == 200
    assert client.post("/admin/applications/999/reject", headers=admin_headers).status_code == 404

    r = client.post("/admin/send-email", headers=admin_headers,
                    json={"application_id": app_id, "subject": "Hi", "message_body": "<script>x</script>\nline2"})
    assert r.status_code == 200 and sent[0]["recipient_email"] == "cand@example.com"


def test_admin_email_body_is_html_escaped():
    from app.services import email_service
    captured = {}
    email_service.send_email = lambda to, subject, body: captured.update(body=body)
    email_service.send_admin_email("a@b.com", "Subject", "<script>alert(1)</script>\nSecond line")
    assert "<script>" not in captured["body"] and "&lt;script&gt;" in captured["body"] and "<br>" in captured["body"]
