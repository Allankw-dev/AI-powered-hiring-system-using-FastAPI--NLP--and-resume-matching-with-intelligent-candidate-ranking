"""Resume <-> job matching.

Score = 45% text similarity + 25% skills + 20% experience + 10% verification.

What is different from v1:
  * Skills are matched with word boundaries and aliases, so "r"/"go" no longer
    match inside every word and "java" no longer matches "javascript".
  * The job's own ``required_skills`` and ``min_experience`` fields are used
    (falling back to what can be read from the description).
  * Experience is computed from merged date ranges, ignores education entries
    and uses the current year instead of a hard-coded one.
  * Raw TF-IDF cosine similarity is rescaled (see SIMILARITY_FULL_MATCH).
"""
import html
import re
from datetime import datetime

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# ──────────────────────────────────────────────────────────────
# Tunables
# ──────────────────────────────────────────────────────────────
# A TF-IDF cosine of this value (between a CV and a job ad) counts as a 100%
# text match. Real CV/job pairs almost never exceed ~0.5, so without rescaling
# even great candidates would score ~30%. Ranking order is not affected.
SIMILARITY_FULL_MATCH = 0.50

WEIGHTS = {"semantic": 0.45, "skills": 0.25, "experience": 0.20, "verification": 0.10}

# ──────────────────────────────────────────────────────────────
# Skills: canonical name -> extra aliases
# ──────────────────────────────────────────────────────────────
SKILLS: dict[str, list[str]] = {
    # Languages
    "python": [], "java": [], "javascript": ["js", "ecmascript"], "typescript": [],
    "c++": ["cpp"], "c#": ["csharp", "c sharp"], "ruby": [], "php": [], "swift": [],
    "kotlin": [], "go": ["golang"], "rust": [], "scala": [], "r": ["r programming", "r language", "rstudio"],
    "matlab": [], "dart": [], "bash": ["shell scripting"],
    # Web
    "fastapi": [], "flask": [], "django": [], "react": ["react.js", "reactjs"], "react native": ["react-native"],
    "angular": ["angularjs"], "vue": ["vue.js", "vuejs"], "nodejs": ["node.js", "node js"],
    "express": ["express.js", "expressjs"], "spring": ["spring boot", "spring framework"],
    "laravel": [], "rails": ["ruby on rails"], "nextjs": ["next.js", "next js"], "flutter": [],
    "html": ["html5"], "css": ["css3"], "bootstrap": [], "tailwind css": ["tailwind", "tailwindcss"],
    "streamlit": [], "rest api": ["restful", "restful api", "restful apis", "rest apis"], "graphql": [],
    "microservices": ["microservice"],
    # Databases
    "sql": ["t-sql", "pl/sql"], "mysql": [], "postgresql": ["postgres"], "mongodb": ["mongo"],
    "redis": [], "sqlite": [], "oracle": [], "sql server": ["mssql", "ms sql"], "dynamodb": [],
    "firebase": [], "supabase": [], "elasticsearch": [],
    # Cloud / DevOps
    "aws": ["amazon web services"], "azure": [], "google cloud": ["gcp"], "docker": [],
    "kubernetes": ["k8s"], "terraform": [], "ci/cd": ["cicd", "ci cd"], "jenkins": [],
    "github actions": [], "linux": [], "nginx": [], "ansible": [], "kafka": [], "rabbitmq": [],
    # Data / AI
    "machine learning": [], "deep learning": [], "nlp": ["natural language processing"],
    "computer vision": [], "tensorflow": [], "pytorch": [], "keras": [],
    "scikit-learn": ["sklearn", "scikit learn"], "pandas": [], "numpy": [],
    "data analysis": ["data analytics"], "data science": [], "power bi": ["powerbi"], "tableau": [],
    "excel": ["ms excel", "microsoft excel"],
    # Tools / practices
    "git": [], "github": [], "gitlab": [], "agile": [], "scrum": [], "jira": [], "figma": [],
    "pytest": [], "selenium": [],
    # Soft skills
    "communication": [], "leadership": [], "teamwork": ["team work"], "problem solving": ["problem-solving"],
}

# Canonical names that are ordinary English words/letters: never match them
# case-insensitively, only through explicit aliases or the case-sensitive
# list-context patterns below.
_AMBIGUOUS = {"go", "r"}
_CASE_SENSITIVE_PATTERNS = {
    "go": r"(?<![\w+#.])Go(?=\s*[,;/|•·\n]|\s*$)",
    "r": r"(?<![\w+#.])R(?=\s*[,;/|•·\n]|\s*$)",
}

_LEFT = r"(?<![a-z0-9+#.])"
_RIGHT = r"(?![a-z0-9+#])"


def _alias_regex(alias: str) -> str:
    words = [re.escape(w) for w in alias.split(" ")]
    return _LEFT + r"[\s\-]+".join(words) + _RIGHT


def _build_pattern(names: list[str]) -> re.Pattern:
    return re.compile("|".join(_alias_regex(n) for n in names))


_PATTERNS: dict[str, re.Pattern] = {}
_CS_PATTERNS: dict[str, re.Pattern] = {}
_ALIAS_TO_CANONICAL: dict[str, str] = {}

for _canon, _aliases in SKILLS.items():
    _names = list(_aliases) if _canon in _AMBIGUOUS else [_canon, *_aliases]
    if _names:
        _PATTERNS[_canon] = _build_pattern(_names)
    if _canon in _CASE_SENSITIVE_PATTERNS:
        _CS_PATTERNS[_canon] = re.compile(_CASE_SENSITIVE_PATTERNS[_canon], re.MULTILINE)
    _ALIAS_TO_CANONICAL[_canon] = _canon
    for _a in _aliases:
        _ALIAS_TO_CANONICAL[_a] = _canon


def _normalize_text(text: str) -> str:
    """Job ads are stored HTML-escaped (bleach) - undo that for scoring."""
    return html.unescape(text or "")


def has_skill(skill: str, text: str, lowered: str | None = None) -> bool:
    """Is ``skill`` (canonical or custom) mentioned in ``text``?"""
    low = lowered if lowered is not None else text.lower()
    pattern = _PATTERNS.get(skill)
    if pattern is not None and pattern.search(low):
        return True
    cs = _CS_PATTERNS.get(skill)
    if cs is not None and cs.search(text):
        return True
    if skill not in SKILLS:  # custom skill typed by the admin
        return bool(_build_pattern([skill]).search(low))
    return False


def extract_skills(text: str) -> list[str]:
    """All known skills mentioned in ``text`` (sorted canonical names)."""
    if not text:
        return []
    text = _normalize_text(text)
    low = text.lower()
    return sorted(s for s in SKILLS if has_skill(s, text, low))


def parse_required_skills(raw: str | None) -> list[str]:
    """Turn the admin's 'Python, SQL; Docker' field into canonical skill names."""
    if not raw:
        return []
    out: list[str] = []
    for token in re.split(r"[,;\n|/•]+", _normalize_text(raw)):
        token = re.sub(r"\s+", " ", token).strip().lower().strip(".")
        if not token or len(token) > 40:
            continue
        canon = _ALIAS_TO_CANONICAL.get(token, token)
        if canon not in out:
            out.append(canon)
    return out


# ──────────────────────────────────────────────────────────────
# Experience
# ──────────────────────────────────────────────────────────────
_MONTH = r"(?:jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec)[a-z]*\.?\s+"
_RANGE_RE = re.compile(
    rf"(?:{_MONTH})?((?:19|20)\d{{2}})\s*(?:-|–|—|to)\s*(?:{_MONTH})?((?:19|20)\d{{2}}|present|current|now|date)",
    re.IGNORECASE,
)
_EDU_RE = re.compile(
    r"universit|college|school|\bbsc\b|b\.sc|\bmsc\b|m\.sc|bachelor|master|diploma|degree|gpa|"
    r"certificat|education|a-level|o-level|kcse|kcpe|expected|graduat|\bphd\b|academy|course|bootcamp",
    re.IGNORECASE,
)
_EXPLICIT_PATTERNS = [
    re.compile(r"(\d+(?:\.\d+)?)\s*\+?\s*(?:years?|yrs?)\s+(?:of\s+)?(?:[a-z\-]+\s+){0,2}experience"),
    re.compile(r"experience\s+(?:of\s+)?(\d+(?:\.\d+)?)\s*\+?\s*(?:years?|yrs?)"),
    re.compile(r"(\d+(?:\.\d+)?)\s*\+?\s*(?:years?|yrs?)\s+(?:in|with)\b"),
]


def _date_range_years(text: str, now_year: int) -> float:
    lines = text.splitlines()
    # character offset of each line start -> to find the line of a match
    starts, pos = [], 0
    for ln in lines:
        starts.append(pos)
        pos += len(ln) + 1

    def line_index(offset: int) -> int:
        lo, hi = 0, len(starts) - 1
        while lo < hi:
            mid = (lo + hi + 1) // 2
            if starts[mid] <= offset:
                lo = mid
            else:
                hi = mid - 1
        return lo

    intervals: list[tuple[float, float]] = []
    for m in _RANGE_RE.finditer(text):
        idx = line_index(m.start())
        context = " ".join(lines[max(0, idx - 1): idx + 1])  # this line + the one above
        if _EDU_RE.search(context):
            continue  # education, not work experience
        start = int(m.group(1))
        end_raw = m.group(2).lower()
        end = now_year if end_raw in {"present", "current", "now", "date"} else int(end_raw)
        if start > now_year or end < start:
            continue
        end = min(end, now_year)
        intervals.append((start, max(end, start + 0.5)))

    if not intervals:
        return 0.0
    intervals.sort()
    merged = [list(intervals[0])]
    for s, e in intervals[1:]:
        if s <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], e)
        else:
            merged.append([s, e])
    return float(sum(e - s for s, e in merged))


def estimate_experience(text: str, now_year: int | None = None) -> float:
    """Years of experience stated in (or inferred from) a CV or job ad."""
    if not text:
        return 0.0
    text = _normalize_text(text)
    now_year = now_year or datetime.now().year

    claims: list[float] = []
    low = text.lower()
    for pattern in _EXPLICIT_PATTERNS:
        claims.extend(float(x) for x in pattern.findall(low))
    claims = [c for c in claims if 0 < c <= 50]
    if claims:
        return float(max(claims))

    return round(min(_date_range_years(text, now_year), 40.0), 1)


# ──────────────────────────────────────────────────────────────
# Scoring pieces
# ──────────────────────────────────────────────────────────────
def clean_text(text: str) -> str:
    if not text:
        return ""
    text = _normalize_text(text).lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def calculate_skill_gap(job_skills: list, resume_skills: list) -> dict:
    matched = [s for s in job_skills if s in resume_skills]
    missing = [s for s in job_skills if s not in resume_skills]
    extra = [s for s in resume_skills if s not in job_skills]
    return {
        "matched": matched,
        "missing": missing,
        "extra_skills": extra,
        "match_rate": round(len(matched) / len(job_skills) * 100, 2) if job_skills else 100.0,
    }


def calculate_semantic_score(job_text: str, resume_text: str) -> float:
    """TF-IDF cosine similarity (unigrams+bigrams), rescaled to 0-100."""
    job_clean = clean_text(job_text)
    resume_clean = clean_text(resume_text)
    if not job_clean or not resume_clean:
        return 0.0
    try:
        vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2), min_df=1, sublinear_tf=True)
        matrix = vectorizer.fit_transform([job_clean, resume_clean])
        cosine = float(cosine_similarity(matrix[0:1], matrix[1:2])[0][0])
    except ValueError:  # e.g. only stop-words left
        return 0.0
    return round(min(cosine / SIMILARITY_FULL_MATCH, 1.0) * 100, 2)


def get_experience_score(job_desc: str, resume_text: str, min_experience: float | None = None) -> tuple:
    required = float(min_experience) if min_experience and min_experience > 0 else estimate_experience(job_desc)
    have = estimate_experience(resume_text)
    score = min(have / required, 1.0) * 100 if required > 0 else 100.0
    return round(score, 2), required, have


def ranking_label(overall_score: float) -> str:
    if overall_score >= 80:
        return "Excellent Match"
    if overall_score >= 60:
        return "Good Match"
    if overall_score >= 40:
        return "Fair Match"
    return "Weak Match"


def calculate_match(
    job_desc: str,
    resume_text: str,
    verification_score: float = 100.0,
    *,
    required_skills: str | None = None,
    min_experience: float | None = None,
    job_title: str = "",
) -> dict:
    """Full match analysis between one job and one resume."""
    job_desc = _normalize_text(job_desc)
    job_text = " ".join(p for p in (job_title, job_desc, _normalize_text(required_skills)) if p)

    semantic_score = calculate_semantic_score(job_text, resume_text)

    job_skills = parse_required_skills(required_skills) or extract_skills(job_desc)
    resume_text_n = _normalize_text(resume_text)
    resume_low = resume_text_n.lower()
    resume_skills = extract_skills(resume_text_n)
    # custom/ambiguous skills the admin listed explicitly may not be in SKILLS
    for skill in job_skills:
        if skill not in resume_skills and has_skill(skill, resume_text_n, resume_low):
            resume_skills.append(skill)
    gap = calculate_skill_gap(job_skills, resume_skills)
    skills_score = gap["match_rate"]

    experience_score, job_exp, resume_exp = get_experience_score(job_desc, resume_text_n, min_experience)

    overall = (
        WEIGHTS["semantic"] * semantic_score
        + WEIGHTS["skills"] * skills_score
        + WEIGHTS["experience"] * experience_score
        + WEIGHTS["verification"] * verification_score
    )

    return {
        "overall_score": round(overall, 2),
        "semantic_score": round(semantic_score, 2),
        "skills_score": round(skills_score, 2),
        "experience_score": round(experience_score, 2),
        "verification_score": round(verification_score, 2),
        "matched_skills": gap["matched"],
        "missing_skills": gap["missing"],
        "extra_skills": gap["extra_skills"],
        "resume_skills": sorted(resume_skills),
        "job_skills": job_skills,
        "resume_experience": resume_exp,
        "required_experience": job_exp,
        "ranking_label": ranking_label(overall),
    }


def recommend_jobs(resume_text: str, jobs: list) -> list:
    """Best-matching jobs for a candidate. ``jobs``: dicts with id/title/company/description/required_skills."""
    results = []
    for job in jobs:
        m = calculate_match(
            job.get("description", ""),
            resume_text,
            required_skills=job.get("required_skills"),
            min_experience=job.get("min_experience"),
            job_title=job.get("title", ""),
        )
        results.append({
            "job_id": job.get("id"),
            "job_title": job.get("title"),
            "company": job.get("company"),
            "match_score": round((m["semantic_score"] + m["skills_score"]) / 2, 2),
            "matched_skills": m["matched_skills"],
            "missing_skills": m["missing_skills"],
        })
    return sorted(results, key=lambda x: x["match_score"], reverse=True)
