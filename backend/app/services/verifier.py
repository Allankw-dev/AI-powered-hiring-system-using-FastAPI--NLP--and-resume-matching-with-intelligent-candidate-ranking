import hashlib
import re
from datetime import datetime


def file_checksum(file_bytes: bytes) -> str:
    """Generate SHA256 checksum for duplicate detection."""
    return hashlib.sha256(file_bytes).hexdigest()


def check_contact_info(text: str) -> tuple:
    """Check if resume has proper contact information."""
    flags = []
    score_deduction = 0

    has_email = bool(re.search(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text))
    has_phone = bool(re.search(r"\+?\d[\d\s\-]{8,}", text))

    if not has_email:
        flags.append("missing_email")
        score_deduction += 15

    if not has_phone:
        flags.append("missing_phone")
        score_deduction += 10

    return flags, score_deduction


def check_date_consistency(text: str) -> tuple:
    """Check for date inconsistencies in experience."""
    flags = []
    score_deduction = 0

    years = re.findall(r"\b((?:19|20)\d{2})\b", text)
    years = [int(y) for y in years]
    current_year = datetime.now().year

    future_years = [y for y in years if y > current_year]
    if future_years:
        flags.append("future_dates_detected")
        score_deduction += 20

    if years:
        earliest = min(years)
        if current_year - earliest > 50:
            flags.append("suspicious_date_range")
            score_deduction += 10

    return flags, score_deduction


def check_keyword_stuffing(text: str) -> tuple:
    """Detect keyword stuffing in resume."""
    flags = []
    score_deduction = 0

    common_keywords = ["python", "java", "sql", "excel", "management", "leadership"]
    lowered = text.lower()
    for keyword in common_keywords:
        # whole words only: "java" must not count every "javascript"
        count = len(re.findall(rf"\b{re.escape(keyword)}\b", lowered))
        if count > 15:
            flags.append(f"keyword_stuffing_{keyword}")
            score_deduction += 15
            break

    return flags, score_deduction


def check_resume_length(text: str) -> tuple:
    """Check if resume has adequate content."""
    flags = []
    score_deduction = 0

    word_count = len(text.split())

    if word_count < 50:
        flags.append("resume_too_short")
        score_deduction += 30
    elif word_count < 150:
        flags.append("resume_very_short")
        score_deduction += 15
    elif word_count > 2000:
        flags.append("resume_too_long")
        score_deduction += 5

    return flags, score_deduction


def check_experience_consistency(text: str) -> tuple:
    """Check if experience claims are consistent."""
    flags = []
    score_deduction = 0

    exp_mentions = re.findall(r"(\d+)\+?\s*years?\s+(?:of\s+)?experience", text.lower())
    if exp_mentions:
        years = [int(x) for x in exp_mentions]
        if max(years) > 40:
            flags.append("unrealistic_experience_claim")
            score_deduction += 20
        if len(set(years)) > 1 and max(years) - min(years) > 5:
            flags.append("inconsistent_experience_years")
            score_deduction += 10

    return flags, score_deduction


def basic_resume_verification(parsed_text: str) -> tuple:
    """
    Comprehensive resume verification.
    Returns: (status, flags, verification_score)
    """
    if not parsed_text or not parsed_text.strip():
        return "flagged", ["empty_resume"], 0.0

    all_flags = []
    total_deduction = 0.0
    base_score = 100.0

    # Run all checks
    checks = [
        check_resume_length(parsed_text),
        check_contact_info(parsed_text),
        check_keyword_stuffing(parsed_text),
        check_date_consistency(parsed_text),
        check_experience_consistency(parsed_text),
    ]

    for flags, deduction in checks:
        all_flags.extend(flags)
        total_deduction += deduction

    verification_score = max(0.0, base_score - total_deduction)

    # Determine status
    if verification_score >= 80:
        status = "verified"
    elif verification_score >= 50:
        status = "pending"
    else:
        status = "flagged"

    return status, all_flags, round(verification_score, 2)


def get_risk_assessment(flags: list, verification_score: float) -> dict:
    """Generate a risk assessment report."""
    if verification_score >= 80:
        risk_level = "Low"
        risk_color = "green"
    elif verification_score >= 50:
        risk_level = "Medium"
        risk_color = "yellow"
    else:
        risk_level = "High"
        risk_color = "red"

    return {
        "risk_level": risk_level,
        "risk_color": risk_color,
        "flags": flags,
        "verification_score": verification_score,
        "recommendation": "Proceed" if risk_level == "Low" else
                          "Review carefully" if risk_level == "Medium" else
                          "Manual verification required"
    }