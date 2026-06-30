import os
from fastapi import FastAPI
from app.core.config import settings
from app.routers import auth, jobs, resumes, applications, admin
from app.routers import users
from app.routers import password_reset

os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

app = FastAPI(title="AI Hiring Platform", version="1.0.0")

app.include_router(auth.router)
app.include_router(jobs.router)
app.include_router(resumes.router)
app.include_router(applications.router)
app.include_router(admin.router)
app.include_router(users.router)
app.include_router(password_reset.router)


@app.api_route("/", methods=["GET", "HEAD"])
def home():
    return {"message": "AI Hiring Platform API is running"}


@app.api_route("/health", methods=["GET", "HEAD"])
def health():
    return {"status": "ok"}