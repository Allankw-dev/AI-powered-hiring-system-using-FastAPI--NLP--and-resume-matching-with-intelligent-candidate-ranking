from app.services.ai_engine import (
    calculate_match, estimate_experience, extract_skills, parse_required_skills,
)


def test_short_skill_names_do_not_match_inside_words():
    skills = extract_skills("I graduated and love good google design, React and Postgres.")
    assert "r" not in skills and "go" not in skills
    assert "react" in skills and "postgresql" in skills


def test_java_is_not_javascript_and_sql_is_not_mysql():
    skills = extract_skills("Built apps in JavaScript with MySQL.")
    assert "javascript" in skills and "mysql" in skills
    assert "java" not in skills and "sql" not in skills


def test_ambiguous_skills_need_context():
    assert "go" not in extract_skills("We go to market fast.")
    assert "go" in extract_skills("Languages: Python, Go, Rust")
    assert "go" in extract_skills("Wrote services in Golang")
    assert "r" in extract_skills("Skills: Python, R, SQL")
    assert "r" not in extract_skills("R&D team")  # "R" glued to '&'


def test_special_characters_in_skills():
    skills = extract_skills("C++, C#, Node.js, CI/CD, scikit-learn, machine-learning")
    for s in ("c++", "c#", "nodejs", "ci/cd", "scikit-learn", "machine learning"):
        assert s in skills


def test_required_skills_parsing_uses_aliases_and_keeps_custom_skills():
    parsed = parse_required_skills("Python, Node.js; Postgres | Go\nSAP ABAP")
    assert parsed == ["python", "nodejs", "postgresql", "go", "sap abap"]


def test_explicit_experience_claim_wins():
    assert estimate_experience("Backend developer with 5+ years of experience in APIs") == 5.0
    assert estimate_experience("Minimum 2 years of professional experience required") == 2.0


def test_education_dates_are_not_experience():
    cv = (
        "EDUCATION\nBSc Computer Science, St Paul's University\n2024 - 2027\n\n"
        "EXPERIENCE\nBackend Developer, Acme\n2023 - 2024\n"
    )
    assert estimate_experience(cv, now_year=2026) == 1.0


def test_overlapping_jobs_are_merged_and_present_uses_current_year():
    cv = "Dev at A 2020 - 2023\nFreelance 2021 - 2023\nDev at B 2023 - Present"
    # 2020..2026 merged = 6 years (not 3 + 2 + 3)
    assert estimate_experience(cv, now_year=2026) == 6.0


def test_job_fields_drive_scoring():
    cv = "Python and Docker developer. 3 years of experience building REST APIs with FastAPI."
    result = calculate_match(
        job_desc="We build backend services for our customers.",
        resume_text=cv,
        required_skills="Python, Docker, Kubernetes, FastAPI",
        min_experience=3,
    )
    assert result["job_skills"] == ["python", "docker", "kubernetes", "fastapi"]
    assert set(result["matched_skills"]) == {"python", "docker", "fastapi"}
    assert result["missing_skills"] == ["kubernetes"]
    assert result["skills_score"] == 75.0
    assert result["experience_score"] == 100.0


def test_min_experience_is_used_over_description():
    cv = "Developer with 2 years of experience."
    result = calculate_match("Great job.", cv, min_experience=4)
    assert result["required_experience"] == 4
    assert result["experience_score"] == 50.0


def test_better_candidate_ranks_higher_and_scores_are_bounded():
    job = "Senior Python backend developer. FastAPI, PostgreSQL, Docker, REST APIs, 3+ years of experience."
    strong = "Python backend developer, 4 years of experience with FastAPI, PostgreSQL, Docker and REST APIs."
    weak = "Graphic designer skilled in Photoshop and Illustrator and brand identity."
    a, b = calculate_match(job, strong), calculate_match(job, weak)
    assert a["overall_score"] > b["overall_score"]
    for r in (a, b):
        for key in ("overall_score", "semantic_score", "skills_score", "experience_score"):
            assert 0 <= r[key] <= 100


def test_html_escaped_job_text_is_handled():
    r = calculate_match("Python &amp; Docker developer", "Python and Docker", required_skills="")
    assert set(r["job_skills"]) == {"python", "docker"}
