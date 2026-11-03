# 🤖 AI-Powered Hiring System

> An intelligent recruitment platform built with FastAPI, Streamlit and PostgreSQL. It uses NLP and machine learning to screen resumes, score candidates and rank them for recruiters.

[![Live Demo](https://img.shields.io/badge/Live%20Demo-Streamlit-FF4B4B?style=for-the-badge&logo=streamlit)](https://ai-powered-hiring-system.streamlit.app)
[![Backend](https://img.shields.io/badge/Backend-Render-46E3B7?style=for-the-badge&logo=render)](https://ai-powered-hiring-system-using-fastapi-c1ya.onrender.com)
[![Database](https://img.shields.io/badge/Database-Supabase-3ECF8E?style=for-the-badge&logo=supabase)](https://supabase.com)
[![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python)](https://python.org)
[![CI](https://img.shields.io/github/actions/workflow/status/Allankw-dev/AI-powered-hiring-system-using-FastAPI--NLP--and-resume-matching-with-intelligent-candidate-ranking/ci.yml?branch=main&style=for-the-badge&label=CI)](https://github.com/Allankw-dev/AI-powered-hiring-system-using-FastAPI--NLP--and-resume-matching-with-intelligent-candidate-ranking/actions)

**Jump to:** [Features](#-features) · [Security](#-security) · [Privacy](#-privacy--legal) · [Getting started](#-getting-started) · [Scripts](#-maintenance-scripts) · [API](#-api) · [Deployment](#-deployment)

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
- **Candidates** — sign up (18+, with explicit consent), upload resumes (PDF/TXT), apply, see their own matched/missing skills, manage their profile and picture, **download or delete all their data**
- **Admins** — post jobs, review AI-ranked candidates (all jobs or one job), shortlist/reject, email candidates. Admins sign in with **password + emailed one-time code**.

### 🤖 Hira assistant
Floating chat bubble powered by **Claude** (set `ANTHROPIC_API_KEY`) or **Gemini** as a fallback (`GEMINI_API_KEY`). It has no access to anyone's account or data. It is rate limited per visitor and has a daily cap.

---

## 🔐 Security

Security is tested, not just claimed: the suite includes regression tests that walk **every route** to check access control, plus CI runs a dependency audit, a static scan and a secret scan on each push. The full findings and remaining risks are in **[SECURITY_AUDIT.md](SECURITY_AUDIT.md)**.

| Area | What is in place |
|------|------------------|
| **Passwords** | Argon2id hashes (legacy bcrypt hashes are upgraded automatically on the next login). Strength rules and a common-password check on signup **and** reset. |
| **Sessions** | JWTs (PyJWT) with required `exp`/`iat`/issuer, fixed HMAC algorithm, and a binding to the current password, so a password change or reset signs out every other device. |
| **Admin access** | Mandatory 2FA (a password alone never yields an admin token). Codes expire in 5 minutes and die after 5 wrong guesses. The whole admin router is protected at router level, roles are read from the database (never trusted from the token), and admin actions are written to the log. Admins are created only with `scripts/manage_admin.py`. |
| **Brute-force protection** | Per-route rate limits that see the real client IP behind Render's proxy, a temporary lock after repeated wrong passwords (per account + IP, and per account across IPs), per-visitor daily chat allowance. |
| **Input & output** | HTML and control characters are stripped from names, job fields and email subjects. Everything the frontend renders as HTML is escaped (`frontend/safe.py`). Emails and the chat widget escape output. |
| **Uploads** | Size limit, extension allow-list, real file-signature check, sanitised names. Files are never served statically; a user can only fetch their own profile picture. |
| **Web hardening** | CORS limited to your frontend, security headers on every response (CSP, `X-Frame-Options`, `nosniff`, HSTS in production, no-store), request-body size limits, `/docs` off in production, no internal error details sent to clients. |
| **Secrets & config** | All secrets are `SecretStr` and never printed. The app refuses to start in production with a weak `SECRET_KEY` or invalid settings. `scripts/check_env.py` validates a configuration without printing secrets. |
| **Database** | Parameterised ORM queries only, TLS enforced to remote Postgres, and `scripts/enable_rls.py` locks the tables against Supabase's public REST API. |
| **Supply chain** | Version-ranged requirements, `pip-audit` + `bandit` + secret scan in CI, Dependabot updates, least-privilege CI token. |

**Found a vulnerability?** Please report it privately (GitHub → Security → *Report a vulnerability*, or contact the author) instead of opening a public issue.

---

## 🔏 Privacy & legal

Built-in, not bolted on. The full checklist (what was done, how to verify it, what is still up to you) is in **[COMPLIANCE.md](COMPLIANCE.md)**.

| | |
|---|---|
| **Legal pages** | Privacy Policy, Terms of Service, Cookie Policy and Refund Policy in [`/legal`](legal) (shown in the app, linked from every page). They are templates drafted from what the app actually does, **not legal advice: have them reviewed before launch.** |
| **Consent & age** | Sign-up has two separate, unticked boxes (Terms + Privacy, and "I am 18+"). Both are enforced by the API and stored with the date and text version. |
| **Your data** | *Profile → Privacy & data*: download everything as JSON, or permanently delete the account (resumes and files, applications, scores, messages, consents). |
| **Email** | Candidate emails carry an unsubscribe link and one-click headers; unsubscribed addresses cannot be emailed. |
| **Honest marketing** | No invented statistics, no fake notifications or progress bars. Tests fail if known unsupported claims return. |
| **Cookies** | One session security cookie, no tracking. A test fails if a tracker is added without updating the policy. |
| **Accessibility** | Checked in a real browser: axe-core reports 0 issues on the main pages, text contrast meets WCAG AA, everything works from the keyboard. |
| **Licences** | [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) lists fonts and every dependency with its licence. |

**Before going live** set `CONTACT_EMAIL` (and `API_PUBLIC_URL`) on Render, and `CONTACT_EMAIL` in the Streamlit secrets.

---

## 🛠️ Tech stack
**Backend:** FastAPI · SQLAlchemy · PostgreSQL (Supabase) · pdfplumber · scikit-learn · argon2-cffi / bcrypt · PyJWT · slowapi · bleach · httpx
**Frontend:** Streamlit · requests
**Infra:** Render (API) · Streamlit Cloud (UI) · Supabase (DB) · Resend or Gmail SMTP (email) · GitHub Actions (CI)

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
For local development set `ENVIRONMENT=development` in `.env`. With `OTP_DELIVERY=log` the admin code is printed in the terminal instead of emailed. In development `/docs` is available at `http://localhost:8000/docs`.

### 2. Frontend
```bash
cd frontend
pip install -r requirements.txt
```
Create `frontend/.streamlit/secrets.toml` (it is git-ignored):
```toml
API_URL = "http://localhost:8000"
# optional, shown in the legal pages and footer:
# CONTACT_EMAIL = "you@example.com"
# OPERATOR_NAME = "Allan Kamau"
# OPERATOR_LOCATION = "Nairobi, Kenya"
```
```bash
streamlit run app.py
```
Admins sign in at the **Admin 2FA login** page (`pages/admin_2FA_login.py`).

### 3. Tests
```bash
cd backend
pip install -r requirements-dev.txt
python -m pytest                       # backend + security regression tests
pip-audit -r requirements.txt          # known-vulnerable dependencies
bandit -r app scripts -ll              # static security scan
python -m scripts.scan_secrets         # secrets in tracked files
```
Chat-widget (JavaScript) tests live in `frontend/tests/` and run in CI.

---

## 🧰 Maintenance scripts

Run these from `backend/` (they use the same `.env` / environment variables as the app).

| Command | What it does |
|---------|--------------|
| `python -m scripts.init_db` | Create any missing tables (never drops anything). |
| `python -m scripts.manage_admin create\|promote\|demote\|set-password <email>` | The only way admins are created or changed. |
| `python -m scripts.check_env` | Validate your configuration before deploying. Never prints a secret; exits non-zero on problems. |
| `python -m scripts.enable_rls [--apply]` | Postgres only. Turn on row-level security for every table so Supabase's public REST API cannot read them. Dry run by default; safe to repeat. |
| `python -m scripts.generate_notices` | Regenerate `THIRD_PARTY_NOTICES.md` (licences of all dependencies and fonts). |
| `python -m scripts.scan_secrets [--history]` | Scan tracked files (and optionally all past commits) for committed secrets. Output is redacted. |

---

## ⚙️ Environment variables

Copy `backend/.env.example` and fill it in. Never commit the real `.env`.

| Variable | Required | Purpose |
|----------|----------|---------|
| `DATABASE_URL` | ✅ | PostgreSQL URL |
| `SECRET_KEY` | ✅ | JWT signing key, **at least 32 characters** in production (`python -c "import secrets; print(secrets.token_urlsafe(48))"`) |
| `RESEND_API_KEY` + `EMAIL_FROM` | one of | Email over HTTPS (recommended on Render) |
| `ADMIN_EMAIL` + `ADMIN_EMAIL_PASSWORD` | the two | Gmail SMTP fallback (use an App Password) |
| `ANTHROPIC_API_KEY` / `GEMINI_API_KEY` | optional | Chat assistant (Claude first) |
| `ENVIRONMENT` | optional | `production` (default), `development` or `test` |
| `FRONTEND_URL` | optional | Used in password-reset links, and as the default allowed CORS origin |
| `CORS_ORIGINS` | optional | Empty (default) = only `FRONTEND_URL`. Or a comma-separated list. |
| `CONTACT_EMAIL` | **set before launch** | Privacy/support contact shown in the legal pages, the footer and email footers |
| `OPERATOR_NAME`, `OPERATOR_LOCATION` | optional | Who runs the service (defaults: Allan Kamau, Nairobi, Kenya) |
| `API_PUBLIC_URL` | recommended | Public https URL of this API; enables one-click unsubscribe headers in emails |
| `ENABLE_DOCS` | optional | `true` to expose `/docs` (off in production by default) |
| `OTP_DELIVERY` | optional | `email` (default) or `log` (prints the code in the server log — emergency use only) |
| `TRUSTED_PROXY_HOPS` | optional | Proxies in front of the API (default 1) |
| `LOGIN_MAX_FAILURES`, `LOGIN_LOCKOUT_MINUTES` | optional | Wrong-password lock-out (default 5 failures / 15 minutes) |
| `CHAT_DAILY_LIMIT`, `CHAT_PER_IP_DAILY_LIMIT` | optional | Chat caps: all visitors together / per visitor |
| `MAX_UPLOAD_MB` | optional | Resume size limit (default 5) |
| `DB_SSLMODE`, `ALLOWED_HOSTS` | optional | Database TLS mode; optional Host-header allow-list |

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
| Users | `GET/PUT /users/me` · `POST /users/me/upload-picture` · `GET /users/me/picture` · `GET /users/me/export` (download my data) · `DELETE /users/me` (delete my account, needs the password) |
| Email | `POST /unsubscribe/{token}` (public; the signed link from the bottom of an email) |
| Utilities | `POST /chat` · `GET /health` |

All routes except sign-up, login, password reset, chat and health require a bearer token. Interactive docs are at `/docs` only when `ENVIRONMENT` is not `production` (or `ENABLE_DOCS=true`).

---

## 📁 Project structure

```
backend/
├── app/
│   ├── core/        config · database · db_setup · security · dependencies · limiter · middleware · sanitize · legal
│   ├── models/      user · job · resume · application · email_log · consent · email_optout
│   ├── routers/     auth · password_reset · jobs · resumes · applications · admin · users · chat
│   ├── schemas/     Pydantic request/response models (input validation + sanitising)
│   ├── services/    ai_engine · ranking · verifier · resume_validator · email · otp · login_throttle · chat
│   └── main.py
├── scripts/         init_db · manage_admin · check_env · enable_rls · scan_secrets · generate_notices
├── tests/           pytest suite (functional + security regression tests)
├── requirements.txt · requirements-dev.txt
frontend/
├── app.py · api.py · safe.py · legal_pages.py · chat_widget.py
├── pages/           home · login · sign_up · admin_2FA_login · dashboard · jobs · applications · profile · …
├── tests/           chat widget tests
└── requirements.txt
.streamlit/config.toml   Streamlit hardening (XSRF protection, no error details for visitors)
.github/                 CI workflow · Dependabot
legal/                   Privacy Policy, Terms, Cookie Policy, Refund Policy (templates: have them reviewed)
COMPLIANCE.md            The 20-point legal/compliance checklist: done, how to verify, what is left for you
THIRD_PARTY_NOTICES.md   Licences of fonts and dependencies
SECURITY_AUDIT.md        Findings, fixes and remaining risks
UPGRADE_NOTES.md         What changed between releases and what to do when deploying
```

---

## 🌍 Deployment

**Backend (Render)** — root directory `backend`, build command `pip install -r requirements.txt`, start command:
```
uvicorn app.main:app --host 0.0.0.0 --port $PORT --no-server-header
```
Set the environment variables above. Uploaded files live on the instance disk, which is wiped on redeploy (parsed text is kept in the database).
If every visitor shares one rate-limit bucket, sign in as admin and open `/admin/client-ip`, then raise `TRUSTED_PROXY_HOPS`.

**Frontend (Streamlit Cloud)** — main file `frontend/app.py`; secret `API_URL = "https://<your-render-app>.onrender.com"` (it must be `https://`; the app refuses to talk to a remote API over plain http).

**First-deploy checklist**
1. `python -m scripts.check_env` with your production values reports no problems.
2. Rotate any credential that has ever been committed (see [SECURITY_AUDIT.md](SECURITY_AUDIT.md)).
3. On Supabase, run `python -m scripts.enable_rls --apply` once.
4. Create your admin: `python -m scripts.manage_admin create you@example.com`.
5. Set `CONTACT_EMAIL` and `API_PUBLIC_URL` (Render) and `CONTACT_EMAIL` (Streamlit secrets), then have the texts in `/legal` reviewed (see [COMPLIANCE.md](COMPLIANCE.md)).
6. If the chat bubble cannot reach the API, set `CORS_ORIGINS` to your exact Streamlit URL.

**Continuous integration** — every push runs the tests, a dependency vulnerability audit, a static security scan and a secret scan (backend), plus compile and widget tests (frontend). Dependabot opens weekly update pull requests.

---

## ⚠️ Known limitations
- Login lock-outs, OTP attempt counters and chat caps are held in memory: they reset on restart and are not shared between several server processes (fine for a single Render instance).
- Resumes are personal data. Parsed text is stored in the database; consider a retention policy.
- The chat bubble and home page use `st.components.v1.html`, which Streamlit is phasing out, so Streamlit is capped below 1.67 until that is migrated.

The complete list is in [SECURITY_AUDIT.md](SECURITY_AUDIT.md#4-known-limitations-and-residual-risk).

---

## 👨‍💻 Author
**Allan Kamau** — [@Allankw-dev](https://github.com/Allankw-dev) · [Ko-fi](https://ko-fi.com/allankamau20)

## 📄 License
MIT

<div align="center"><strong>Built with ❤️ in Nairobi, Kenya 🇰🇪</strong></div>
