# 🤖 AI-Powered Hiring System

> An intelligent recruitment platform built with FastAPI, Streamlit and PostgreSQL. It uses NLP and machine learning to screen resumes, score candidates and rank them for recruiters.

[![Live Demo](https://img.shields.io/badge/Live%20Demo-Streamlit-FF4B4B?style=for-the-badge&logo=streamlit)](https://ai-powered-hiring-system.streamlit.app)
[![Backend](https://img.shields.io/badge/Backend-Render-46E3B7?style=for-the-badge&logo=render)](https://ai-powered-hiring-system-using-fastapi-c1ya.onrender.com)
[![Database](https://img.shields.io/badge/Database-Supabase-3ECF8E?style=for-the-badge&logo=supabase)](https://supabase.com)
[![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python)](https://python.org)

---

## ✨ Features

### 🧠 AI-Powered Resume Analysis
- **Text similarity** — TF-IDF (unigrams + bigrams) cosine similarity between resume and job, rescaled to 0–100
- **Skill extraction** — ~100 skills with aliases and word-boundary matching (`java` ≠ `javascript`, `sql` ≠ `mysql`)
- **Job-driven matching** — uses the job's own *required skills* and *minimum experience* fields
- **Experience estimation** — explicit claims ("5+ years of experience") or merged date ranges; education dates are ignored
- **Fraud checks** — keyword stuffing, inconsistent dates, very short resumes, missing contact info, the same CV used on two accounts

### 📊 Candidate scoring
| Component | Weight | Description |
|-----------|--------|-------------|
| Text similarity | 45% | Resume-to-job similarity |
| Skills | 25% | Required skills found in the resume |
| Experience | 20% | Years of experience vs requirement |
| Verification | 10% | Resume authenticity checks |

Applications are ranked per job (`ranking_position`). Admins can re-score a job's applications after editing it.

### 👥 Roles
- **Candidates** — sign up, upload resumes (PDF/TXT), apply, see their own matched/missing skills
- **Admins** — post jobs, review AI-ranked candidates (all jobs or one job), shortlist/reject, email candidates. Admins sign in with **password + emailed one-time code**.

### 🤖 Hira assistant
Floating chat bubble powered by **Claude** (set `ANTHROPIC_API_KEY`) or **Gemini** as a fallback (`GEMINI_API_KEY`). It has no access to anyone's account or data, is rate limited, and has a daily cap.

### 🔐 Security
- JWT auth + bcrypt; password strength enforced on signup **and** reset
- Admin 2FA is mandatory — a password alone never yields an admin token; OTPs expire in 5 minutes and die after 5 wrong guesses
- Self-service signup can only create candidates; admins are managed with `scripts/manage_admin.py`
- Password-reset tokens are stored hashed, single-use, 1 hour
- Rate limiting that sees the real client IP behind Render's proxy
- Upload checks: size limit, extension allow-list, real file signature, sanitized names
- Output escaping in emails and the chat widget; no internal error details sent to clients
- App refuses to start in production without a strong `SECRET_KEY`

---

## 🛠️ Tech stack
**Backend:** FastAPI · SQLAlchemy · PostgreSQL (Supabase) · pdfplumber · scikit-learn · passlib/bcrypt · python-jose · slowapi · bleach · httpx
**Frontend:** Streamlit · requests
**Infra:** Render (API) · Streamlit Cloud (UI) · Supabase (DB) · Resend or Gmail SMTP (email)

---

## 🚀 Getting started

```bash
git clone https://github.com/Allankw-dev/AI-powered-hiring-system-using-FastAPI--NLP--and-resume-matching-with-intelligent-candidate-ranking.git
cd AI-powered-hiring-system-using-FastAPI--NLP--and-resume-matching-with-intelligent-candidate-ranking
```

### 1. Backend
```bash
cd backend
python -m venv venv
venv\Scripts\activate            # Windows   (macOS/Linux: source venv/bin/activate)
pip install -r requirements.txt
copy .env.example .env           # macOS/Linux: cp .env.example .env   — then fill it in
python -m scripts.init_db        # creates any missing tables (never drops anything)
python -m scripts.manage_admin create you@example.com --name "Your Name"
uvicorn app.main:app --reload
```
For local development set `ENVIRONMENT=development` in `.env`; with `OTP_DELIVERY=log` the admin code is printed in the terminal instead of emailed.

### 2. Frontend
```bash
cd frontend
pip install streamlit requests
```
`.streamlit/secrets.toml`:
```toml
API_URL = "http://localhost:8000"
```
```bash
streamlit run app.py
```
Admins sign in at the **Admin 2FA login** page (`pages/admin_2FA_login.py`).

### 3. Tests
```bash
cd backend && pip install -r requirements-dev.txt && python -m pytest
```

---

## ⚙️ Environment variables

| Variable | Required | Purpose |
|----------|----------|---------|
| `DATABASE_URL` | ✅ | PostgreSQL URL |
| `SECRET_KEY` | ✅ | JWT signing key (`python -c "import secrets; print(secrets.token_urlsafe(48))"`) |
| `RESEND_API_KEY` + `EMAIL_FROM` | one of | Email over HTTPS (recommended on Render) |
| `ADMIN_EMAIL` + `ADMIN_EMAIL_PASSWORD` | the two | Gmail SMTP fallback |
| `ANTHROPIC_API_KEY` / `GEMINI_API_KEY` | optional | Chat assistant (Claude first) |
| `FRONTEND_URL` | optional | Used in password-reset links |
| `CORS_ORIGINS` | optional | `*` (default) or a comma-separated list |
| `OTP_DELIVERY` | optional | `email` (default) or `log` |
| `TRUSTED_PROXY_HOPS` | optional | Proxies in front of the API (default 1) |
| `MAX_UPLOAD_MB`, `CHAT_DAILY_LIMIT`, `ENVIRONMENT` | optional | See `.env.example` |

---

## 🔌 API

| Area | Endpoints |
|------|-----------|
| Auth | `POST /auth/signup` · `POST /auth/login` (candidates) · `POST /auth/admin/request-otp` · `POST /auth/admin/verify-otp` |
| Password | `POST /password/forgot` · `POST /password/reset` |
| Jobs | `GET /jobs/` · `GET /jobs/{id}` · `POST /jobs/` · `PUT /jobs/{id}` · `DELETE /jobs/{id}` (admin; 409 if it has applications) |
| Resumes | `POST /resumes/upload` · `GET /resumes/my` · `DELETE /resumes/{id}` |
| Applications | `POST /applications/` · `GET /applications/my` |
| Admin | `GET /admin/top-candidates?job_id=&limit=` · `POST /admin/applications/{id}/shortlist` · `…/reject` · `POST /admin/send-email` · `POST /admin/jobs/{id}/rescore` · `GET /admin/client-ip` |
| Users | `GET/PUT /users/me` · `POST /users/me/upload-picture` |
| Utilities | `POST /chat` · `GET /health` |

Interactive docs: `/docs`.

---

## 📁 Project structure

```
backend/
├── app/
│   ├── core/        config · database · security · limiter · dependencies
│   ├── models/      user · job · resume · application · email_log
│   ├── routers/     auth · password_reset · jobs · resumes · applications · admin · users · chat
│   ├── schemas/     Pydantic models
│   ├── services/    ai_engine · ranking · verifier · resume_validator · email · otp · chat
│   └── main.py
├── scripts/         init_db.py · manage_admin.py
├── tests/           pytest suite
└── requirements.txt
frontend/
├── app.py · api.py · chat_widget.py
├── pages/           home · login · sign_up · admin_2FA_login · dashboard · jobs · applications · …
└── tests/           chat widget tests
```

---

## 🌍 Deployment

**Backend (Render)** — root `backend`, build `pip install -r requirements.txt`, start:
```
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```
Set the environment variables above. Uploaded files live on the instance disk, which is wiped on redeploy (parsed text is kept in the database).
If every visitor shares one rate-limit bucket, sign in as admin and open `/admin/client-ip`, then raise `TRUSTED_PROXY_HOPS`.

**Frontend (Streamlit Cloud)** — main file `frontend/app.py`; secret `API_URL = "https://<your-render-app>.onrender.com"`.

---

## 👨‍💻 Author
**Allan Kamau** — [@Allankw-dev](https://github.com/Allankw-dev) · [Ko-fi](https://ko-fi.com/allankamau20)

## 📄 License
MIT

<div align="center"><strong>Built with ❤️ in Nairobi, Kenya 🇰🇪</strong></div>
