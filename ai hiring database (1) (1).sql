-- =========================================
-- AI HIRING SYSTEM DATABASE
-- SIMPLIFIED VERSION FOR DATABASE 1
-- =========================================

-- CREATE DATABASE
IF DB_ID('AIHiringDB') IS NULL
BEGIN
    CREATE DATABASE AIHiringDB;
END
GO

USE AIHiringDB;
GO


-- =========================================
-- USERS TABLE
-- =========================================
CREATE TABLE dbo.Users (
    id INT IDENTITY(1,1) PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(120) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL DEFAULT 'candidate',
    created_at DATETIME NOT NULL DEFAULT GETDATE()
);
GO

-- =========================================
-- JOBS TABLE
-- =========================================
CREATE TABLE dbo.Jobs (
    id INT IDENTITY(1,1) PRIMARY KEY,
    title VARCHAR(100) NOT NULL,
    company VARCHAR(100) NOT NULL,
    description VARCHAR(MAX) NOT NULL,
    required_skills VARCHAR(255) NULL,
    min_experience INT NOT NULL DEFAULT 0,
    created_by INT NOT NULL,
    created_at DATETIME NOT NULL DEFAULT GETDATE(),

    CONSTRAINT FK_Jobs_Users
        FOREIGN KEY (created_by) REFERENCES dbo.Users(id)
);
GO

-- =========================================
-- RESUMES TABLE
-- =========================================
CREATE TABLE dbo.Resumes (
    id INT IDENTITY(1,1) PRIMARY KEY,
    user_id INT NOT NULL,
    file_name VARCHAR(255) NOT NULL,
    file_path VARCHAR(255) NOT NULL,
    upload_date DATETIME NOT NULL DEFAULT GETDATE(),

    CONSTRAINT FK_Resumes_Users
        FOREIGN KEY (user_id) REFERENCES dbo.Users(id)
);
GO

-- =========================================
-- APPLICATIONS TABLE
-- =========================================
CREATE TABLE dbo.Applications (
    id INT IDENTITY(1,1) PRIMARY KEY,
    user_id INT NOT NULL,
    job_id INT NOT NULL,
    resume_id INT NOT NULL,
    ai_score FLOAT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'submitted',
    applied_at DATETIME NOT NULL DEFAULT GETDATE(),

    CONSTRAINT FK_Applications_Users
        FOREIGN KEY (user_id) REFERENCES dbo.Users(id),

    CONSTRAINT FK_Applications_Jobs
        FOREIGN KEY (job_id) REFERENCES dbo.Jobs(id),

    CONSTRAINT FK_Applications_Resumes
        FOREIGN KEY (resume_id) REFERENCES dbo.Resumes(id)
);
GO

-- =========================================
-- SCORES TABLE
-- =========================================
CREATE TABLE dbo.Scores (
    id INT IDENTITY(1,1) PRIMARY KEY,
    application_id INT NOT NULL,
    semantic_score FLOAT NULL,
    skills_score FLOAT NULL,
    experience_score FLOAT NULL,
    verification_score FLOAT NULL,
    overall_score FLOAT NULL,

    CONSTRAINT FK_Scores_Applications
        FOREIGN KEY (application_id) REFERENCES dbo.Applications(id)
);
GO

-- =========================================
-- EMAIL LOGS TABLE
-- =========================================
CREATE TABLE dbo.EmailLogs (
    id INT IDENTITY(1,1) PRIMARY KEY,
    user_id INT NOT NULL,
    application_id INT NOT NULL,
    subject VARCHAR(255) NOT NULL,
    message VARCHAR(MAX) NOT NULL,
    sent_at DATETIME NOT NULL DEFAULT GETDATE(),

    CONSTRAINT FK_EmailLogs_Users
        FOREIGN KEY (user_id) REFERENCES dbo.Users(id),

    CONSTRAINT FK_EmailLogs_Applications
        FOREIGN KEY (application_id) REFERENCES dbo.Applications(id)
);
GO

-- =========================================
-- SAMPLE DATA: USERS
-- =========================================
INSERT INTO dbo.Users (full_name, email, password_hash, role)
VALUES
('Allan Kamau', 'admin@gmail.com', 'admin123hash', 'admin'),
('Brian Otieno', 'brian@gmail.com', 'brian123hash', 'candidate'),
('Mary Wanjiku', 'mary@gmail.com', 'mary123hash', 'candidate');
GO

-- =========================================
-- SAMPLE DATA: JOBS
-- =========================================
INSERT INTO dbo.Jobs (title, company, description, required_skills, min_experience, created_by)
VALUES
('Software Engineer', 'Tech Corp', 'Develop and maintain software systems', 'Python, SQL, Git', 2, 1),
('Data Analyst', 'Data Solutions', 'Analyze data and prepare reports', 'Excel, SQL, Power BI', 1, 1);
GO

-- =========================================
-- SAMPLE DATA: RESUMES
-- =========================================
INSERT INTO dbo.Resumes (user_id, file_name, file_path)
VALUES
(2, 'Brian_CV.pdf', 'uploads/Brian_CV.pdf'),
(3, 'Mary_CV.pdf', 'uploads/Mary_CV.pdf');
GO

-- =========================================
-- SAMPLE DATA: APPLICATIONS
-- =========================================
INSERT INTO dbo.Applications (user_id, job_id, resume_id, ai_score, status)
VALUES
(2, 1, 1, 78.5, 'submitted'),
(3, 2, 2, 85.0, 'submitted');
GO

-- =========================================
-- SAMPLE DATA: SCORES
-- =========================================
INSERT INTO dbo.Scores (application_id, semantic_score, skills_score, experience_score, verification_score, overall_score)
VALUES
(1, 80, 75, 70, 90, 78.75),
(2, 88, 82, 79, 91, 85.00);
GO

-- =========================================
-- SAMPLE DATA: EMAIL LOGS
-- =========================================
INSERT INTO dbo.EmailLogs (user_id, application_id, subject, message)
VALUES
(2, 1, 'Application Update', 'You have been shortlisted for the next stage.'),
(3, 2, 'Application Update', 'Your application has been received successfully.');
GO

-- =========================================
-- BASIC QUERIES
-- =========================================

-- View all users
SELECT * FROM dbo.Users;
GO

-- View all jobs
SELECT * FROM dbo.Jobs;
GO

-- View all resumes
SELECT * FROM dbo.Resumes;
GO

-- View all applications
SELECT * FROM dbo.Applications;
GO

-- View all scores
SELECT * FROM dbo.Scores;
GO

-- View all email logs
SELECT * FROM dbo.EmailLogs;
GO

-- Select all admins
SELECT * 
FROM dbo.Users
WHERE role = 'admin';
GO

-- Select all candidates
SELECT * 
FROM dbo.Users
WHERE role = 'candidate';
GO

-- =========================================
-- ADVANCED BUT FEW QUERIES
-- =========================================

-- 1. Candidates who have applied for jobs
SELECT DISTINCT u.full_name, u.email
FROM dbo.Users u, dbo.Applications a
WHERE u.id = a.user_id
AND u.role = 'candidate';
GO

-- 2. Candidates who have not applied for any job
SELECT u.full_name, u.email
FROM dbo.Users u
WHERE u.role = 'candidate'
AND NOT EXISTS (
    SELECT *
    FROM dbo.Applications a
    WHERE a.user_id = u.id
);
GO

-- 3. Jobs with no applicants
SELECT j.title, j.company
FROM dbo.Jobs j
WHERE NOT EXISTS (
    SELECT *
    FROM dbo.Applications a
    WHERE a.job_id = j.id
);
GO

-- 4. Highest scoring application
SELECT *
FROM dbo.Applications
WHERE ai_score = (
    SELECT MAX(ai_score)
    FROM dbo.Applications
);
GO

-- 5. Admins who posted jobs
SELECT DISTINCT u.full_name, u.email
FROM dbo.Users u, dbo.Jobs j
WHERE u.id = j.created_by
AND u.role = 'admin';
GO

-- 6. Get candidate names with detailed scores
SELECT u.full_name, s.overall_score, s.semantic_score, s.skills_score
FROM dbo.Scores s
JOIN dbo.Applications a ON s.application_id = a.id
JOIN dbo.Users u ON a.user_id = u.id;
GO

-- 7. View email history
SELECT u.full_name, e.subject, e.sent_at
FROM dbo.EmailLogs e
JOIN dbo.Users u ON e.user_id = u.id;
GO