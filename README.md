
# 🤖 AI-Powered Hiring System.

> An intelligent recruitment platform built with FastAPI, Streamlit, and PostgreSQL — powered by NLP and machine learning to automate resume screening, candidate scoring, and hiring decisions..

[![Live Demo](https://img.shields.io/badge/Live%20Demo-Streamlit-FF4B4B?style=for-the-badge&logo=streamlit)](https://ai-powered-hiring-system.streamlit.app)
[![Backend](https://img.shields.io/badge/Backend-Render-46E3B7?style=for-the-badge&logo=render)](https://ai-powered-hiring-system-using-fastapi-c1ya.onrender.com)
[![Database](https://img.shields.io/badge/Database-Supabase-3ECF8E?style=for-the-badge&logo=supabase)](https://supabase.com)
[![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python)](https://python.org)

---

## ✨ Features.

### 🧠 AI-Powered Resume Analysis
- **Semantic Scoring** — TF-IDF cosine similarity between resumes and job descriptions
- **Skill Extraction** — 50+ skill taxonomy for accurate matching
- **Experience Estimation** — Regex-based extraction of years of experience
- **Fraud Detection** — Flags keyword stuffing, inconsistent dates, and suspicious patterns

### 📊 Intelligent Candidate Scoring
| Component | Weight | Description |
|-----------|--------|-------------|
| Semantic Score | 45% | Resume-to-job similarity |
| Skills Score | 25% | Required skills matched |
| Experience Score | 20% | Years of experience vs requirement |
| Verification Score | 10% | Resume authenticity |

### 👥 Dual Role System
- **Candidates** — Sign up, upload resumes, apply for jobs, track application status
- **Admins** — Post jobs, view AI-ranked candidates, shortlist/reject, send emails

### 🤖 Hira AI Assistant
- Floating chat bubble powered by **Claude AI**
- Helps candidates with resume tips and job matching advice
- Helps admins analyze candidates and make decisions
- Answers any question about the platform

### 🔐 Security
- JWT authentication with bcrypt password hashing
- Rate limiting on all auth endpoints (slowapi)
- CORS protection restricted to frontend origin
- Input sanitization with bleach
- All secrets stored in environment variables
- Password strength validation

---

## 🛠️ Tech Stack

### Backend
| Technology | Purpose |
|-----------|---------|
| **FastAPI** | REST API framework |
| **SQLAlchemy** | ORM for database operations |
| **PostgreSQL** | Production database (Supabase) |
| **pdfplumber** | PDF text extraction |
| **scikit-learn** | TF-IDF vectorization & cosine similarity |
| **passlib + bcrypt** | Password hashing |
| **python-jose** | JWT token generation |
| **slowapi** | Rate limiting |
| **bleach** | Input sanitization |
| **httpx** | Async HTTP for Claude API |

### Frontend
| Technology | Purpose |
|-----------|---------|
| **Streamlit** | Web application framework |
| **HTML/CSS/JS** | Custom UI components |
| **requests** | HTTP client for API calls |

### Infrastructure
| Service | Purpose |
|---------|---------|
| **Render** | Backend hosting |
| **Streamlit Cloud** | Frontend hosting |
| **Supabase** | PostgreSQL database |
| **UptimeRobot** | Backend uptime monitoring |
| **Gmail SMTP** | Email notifications |

---

## 🚀 Getting Started

### Prerequisites
- Python 3.12+
- PostgreSQL database (Supabase recommended)
- Gmail account with App Password enabled

### 1. Clone the repository
```bash
git clone https://github.com/Allankw-dev/AI-powered-hiring-system-using-FastAPI--NLP--and-resume-matching-with-intelligent-candidate-ranking.git
cd ai-hiring-system
```

### 2. Backend Setup
```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

Create a `.env` file in the backend directory:
```env
SECRET_KEY=your-secret-key-here
DATABASE_URL=postgresql://user:password@host:5432/dbname
ADMIN_EMAIL=your-email@gmail.com
ADMIN_EMAIL_PASSWORD=your-gmail-app-password
ADMIN_EMAILS=your-email@gmail.com
ANTHROPIC_API_KEY=your-anthropic-api-key
FRONTEND_URL=http://localhost:8501
```

Run the backend:
```bash
uvicorn app.main:app --reload
```

### 3. Frontend Setup
```bash
cd frontend
pip install streamlit requests
```

Create `.streamlit/secrets.toml`:
```toml
API_URL = "http://localhost:8000"
```

Run the frontend:
```bash
streamlit run app.py
```

---

## 📁 Project Structure

```
ai-hiring-system/
├── backend/
│   ├── app/
│   │   ├── core/
│   │   │   ├── config.py        # Settings & environment variables
│   │   │   ├── database.py      # SQLAlchemy engine & session
│   │   │   ├── dep.py           # FastAPI dependencies
│   │   │   └── security.py      # JWT & bcrypt utilities
│   │   ├── models/
│   │   │   ├── user.py          # User table
│   │   │   ├── job.py           # Job table
│   │   │   ├── resume.py        # Resume table
│   │   │   ├── application.py   # Application table
│   │   │   └── email_log.py     # Email log table
│   │   ├── routers/
│   │   │   ├── auth.py          # Signup, login, OTP
│   │   │   ├── jobs.py          # Job CRUD
│   │   │   ├── resumes.py       # Resume upload & parsing
│   │   │   ├── applications.py  # Job applications & AI scoring
│   │   │   ├── admin.py         # Admin operations
│   │   │   ├── users.py         # Profile management
│   │   │   └── password_reset.py # Password reset flow
│   │   ├── schemas/             # Pydantic validation models
│   │   ├── services/
│   │   │   ├── ai_engine.py     # TF-IDF scoring & skill matching
│   │   │   ├── resume_parser.py # PDF text extraction
│   │   │   ├── verifier.py      # Fraud detection
│   │   │   ├── email_service.py # Gmail SMTP
│   │   │   └── otp_service.py   # OTP generation & verification
│   │   └── main.py              # FastAPI app entry point
│   └── requirements.txt
└── frontend/
    ├── pages/
    │   ├── home.py              # Landing page with neural network bg
    │   ├── login.py             # Login page
    │   ├── sign_up.py           # Registration page
    │   ├── dashboard.py         # Candidate dashboard
    │   ├── jobs.py              # Job listings
    │   ├── applications.py      # Application tracking
    │   ├── upload_resume.py     # Resume upload
    │   ├── profile.py           # User profile
    │   ├── admin_panel.py       # Admin control panel
    │   ├── forgot_password.py   # Password recovery
    │   └── reset_password.py    # Password reset
    ├── api.py                   # All backend API calls
    └── app.py                   # Main Streamlit app + AI assistant
```

---

## 🔌 API Endpoints

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/signup` | Register new user |
| POST | `/auth/login` | Login & get JWT token |
| POST | `/auth/admin/request-otp` | Request admin OTP |
| POST | `/auth/admin/verify-otp` | Verify admin OTP |

### Jobs
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/jobs/` | List all jobs |
| POST | `/jobs/` | Create job (admin only) |
| PUT | `/jobs/{id}` | Update job (admin only) |
| DELETE | `/jobs/{id}` | Delete job (admin only) |

### Resumes & Applications
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/resumes/upload` | Upload resume PDF |
| GET | `/resumes/my` | Get my resumes |
| POST | `/applications/` | Apply to job (triggers AI scoring) |
| GET | `/applications/my` | Get my applications |

### Admin
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/admin/top-candidates` | Top 20 AI-ranked candidates |
| POST | `/admin/applications/{id}/shortlist` | Shortlist candidate |
| POST | `/admin/applications/{id}/reject` | Reject candidate |
| POST | `/admin/send-email` | Send email to candidate |

### AI & Utilities
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/chat` | Hira AI assistant (Claude) |
| GET | `/health` | Health check |

---

## 🤖 How the AI Scoring Works

```
Resume PDF Upload
      ↓
Text Extraction (pdfplumber)
      ↓
┌─────────────────────────────────────┐
│           AI Scoring Engine         │
│                                     │
│  Semantic Score (45%)               │
│  → TF-IDF vectorization             │
│  → Cosine similarity with job desc  │
│                                     │
│  Skills Score (25%)                 │
│  → Extract skills from resume       │
│  → Match against required skills    │
│                                     │
│  Experience Score (20%)             │
│  → Extract years from resume        │
│  → Compare to job requirement       │
│                                     │
│  Verification Score (10%)           │
│  → Check resume authenticity        │
│  → Flag suspicious patterns         │
└─────────────────────────────────────┘
      ↓
Overall Score (0-100)
      ↓
Ranking Label: Excellent / Good / Fair / Weak
```

---

## 🔒 Security Features

- 🔑 **JWT Authentication** — Signed with strong secret key
- 🔐 **Bcrypt Hashing** — Passwords never stored in plain text
- 🚦 **Rate Limiting** — 5 login attempts/minute, 3 signups/minute
- 🛡️ **CORS Protection** — Restricted to frontend domain only
- 🧹 **Input Sanitization** — bleach strips malicious HTML
- ✅ **Password Validation** — Minimum 8 chars, uppercase, number required
- 🔒 **Admin Protection** — Admin password reset blocked
- 🏊 **Connection Pooling** — Efficient database connections

---

## 🌍 Deployment

### Backend (Render)
1. Connect GitHub repo to Render
2. Set root directory to `backend`
3. Set start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. Add environment variables

### Frontend (Streamlit Cloud)
1. Connect GitHub repo to Streamlit Cloud
2. Set main file path to `frontend/app.py`
3. Add secrets in Settings → Secrets

---

## 👨‍💻 Author

**Allan Kamau**
- GitHub: [@Allankw-dev](https://github.com/Allankw-dev)
- Email: allankamau517@gmail.com
- Ko-fi: [ko-fi.com/allankamau20](https://ko-fi.com/allankamau20)

---

## 📄 License

This project is licensed under the MIT License.

---

<div align="center">
  <strong>Built with ❤️ in Nairobi, Kenya 🇰🇪</strong>
</div>








