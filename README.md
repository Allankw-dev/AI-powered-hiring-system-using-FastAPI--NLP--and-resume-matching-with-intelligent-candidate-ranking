🚀 AI Hiring System.

An intelligent recruitment platform that automates candidate screening using AI-powered resume analysis, ranking applicants based on job requirements and helping recruiters make faster, smarter hiring decisions.

📌 Overview.

The AI Hiring System is a full-stack web application that:

Allows candidates to upload resumes

Uses AI/NLP to evaluate and score applicants

Ranks candidates based on relevance to job requirements

Provides an admin dashboard to manage hiring decisions

Enables communication with shortlisted candidates via email

✨ Features.
👤 Candidate Side

User authentication (Signup/Login)

Resume upload (PDF)

Automatic resume parsing

AI-based scoring

Personal dashboard to track submissions

🛠️ Admin Side

Secure admin login with OTP verification

View top-ranked candidates

Access detailed candidate insights

Send emails to selected applicants

Manage job postings

🤖 AI Capabilities

Resume skill extraction

Keyword matching

Experience evaluation

Candidate ranking algorithm

🧱 Tech Stack
🔹 Frontend

Streamlit (UI)

HTML/CSS (custom styling)

🔹 Backend

FastAPI

Python

🔹 Database

SQL Server

🔹 AI / NLP

Python NLP techniques (spaCy / custom parsing)

Resume analysis logic

🔹 Other Tools

Uvicorn (ASGI server)

Git & GitHub

📂 Project Structure
ai-hiring-system/
│
├── backend/
│   ├── app/
│   │   ├── models/
│   │   ├── routers/
│   │   ├── schemas/
│   │   ├── services/
│   │   └── core/
│
├── frontend/
│   ├── pages/
│   ├── api.py
│   └── app.py
│
├── uploads/
├── requirements.txt
└── README.md
⚙️ Installation & Setup
1️⃣ Clone the Repository
git clone https://github.com/your-username/ai-hiring-system.git
cd ai-hiring-system
2️⃣ Backend Setup
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8010
3️⃣ Frontend Setup
cd frontend
streamlit run app.py
🗄️ Database Configuration

Update your .env file:

SQL_SERVER=localhost\SQLEXPRESS
SQL_DATABASE=AIHiringDB
SQL_DRIVER=ODBC Driver 17 for SQL Server

SECRET_KEY=your_secret_key

SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
ADMIN_EMAIL=your_email@gmail.com
ADMIN_EMAIL_PASSWORD=your_password
🔐 Authentication Flow

Users sign up and log in normally

Admin login requires:

Email + Password

OTP verification (extra security layer)

📊 How It Works

Candidate uploads resume

System extracts:

Skills

Experience

Keywords

AI compares resume with job requirements

Generates a score

Candidates are ranked automatically

Admin reviews top candidates

📧 Email Integration

Admin can send emails to selected candidates

Useful for:

Interview invitations

Shortlisting notifications

🧠 Future Improvements

Advanced NLP models (BERT / LLM integration)

Real-time interview scheduling

Dashboard analytics

Multi-company support

Cloud deployment (AWS/Azure)

🏆 Why This Project?

Solves real-world hiring inefficiencies

Demonstrates full-stack + AI skills

Combines backend, frontend, and ML concepts

Portfolio-ready project for software engineering roles

👨‍💻 Author

Allan Kamau

💼 Software Engineer

🤖 AI & ML Enthusiast

🌐 Full Stack Developer

⭐ Support

If you like this project:

⭐ Star the repo

🍴 Fork it

📢 Share it
