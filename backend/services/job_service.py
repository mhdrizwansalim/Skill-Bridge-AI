import csv
import re
from typing import Iterable

from backend.config import PROJECT_ROOT
from backend.services.cv_service import load_profile


def normalize_skill(skill: str) -> str:
    return re.sub(r"\s+", " ", skill.strip()).casefold()


def load_skill_vocabulary() -> list[str]:
    path = PROJECT_ROOT / "data" / "processed" / "unified_skills.csv"
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)
        fields = reader.fieldnames or []
        skill_field = next(
            (field for field in ("Skill Name", "skill_name", "skill", "name") if field in fields),
            None,
        )
        if not skill_field:
            return []
        skills = {
            row[skill_field].strip()
            for row in reader
            if row.get(skill_field) and row[skill_field].strip()
        }
    return sorted(skills, key=str.lower)


def extract_skills(text: str) -> tuple[list[str], list[str]]:
    text_lower = text.lower()
    found = []
    for skill in load_skill_vocabulary():
        pattern = r"(?<![a-z0-9])" + re.escape(skill.lower()) + r"(?![a-z0-9])"
        if re.search(pattern, text_lower):
            found.append(skill)

    preferred_lines = [
        line
        for line in text.splitlines()
        if re.search(r"\b(preferred|nice to have|bonus)\b", line, re.IGNORECASE)
    ]
    preferred_text = "\n".join(preferred_lines).lower()
    preferred = [
        skill
        for skill in found
        if re.search(r"(?<![a-z0-9])" + re.escape(skill.lower()) + r"(?![a-z0-9])", preferred_text)
    ]
    required = [skill for skill in found if skill not in preferred]
    return sorted(set(required), key=str.lower), sorted(set(preferred), key=str.lower)


def extract_job_title(text: str) -> str:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if not lines:
        return "Job role"
    for line in lines[:8]:
        match = re.search(
            r"(?:job\s*title|role|position)\s*[:\-]\s*(.+)",
            line,
            re.IGNORECASE,
        )
        if match:
            return match.group(1).strip()
    first = lines[0]
    if len(first) <= 100:
        return first
    return "Job role"


def extract_experience(text: str) -> list[str]:
    return [
        line.strip()
        for line in text.splitlines()
        if re.search(r"\b(years?|yrs?|experience)\b", line, re.IGNORECASE)
    ]


def extract_education(text: str) -> list[str]:
    keywords = r"\b(bachelor|master|degree|b\.?tech|b\.?e\.?|m\.?tech|mba|phd|diploma)\b"
    return [
        line.strip()
        for line in text.splitlines()
        if re.search(keywords, line, re.IGNORECASE)
    ]


def extract_responsibilities(text: str) -> list[str]:
    bullets = []
    in_responsibilities = False
    for line in text.splitlines():
        stripped = line.strip()
        if re.search(r"responsibilities|what you.?ll do|duties", stripped, re.IGNORECASE):
            in_responsibilities = True
            continue
        if in_responsibilities and re.match(r"^[•\-*]|\d+\.", stripped):
            bullets.append(re.sub(r"^[•\-*]\s*|\d+\.\s*", "", stripped))
    if bullets:
        return bullets
    return [
        stripped
        for stripped in (line.strip() for line in text.splitlines())
        if stripped and re.match(r"^[•\-*]\s+", stripped)
    ]


def analyze_job_description(text: str) -> dict:
    profile = load_profile()
    candidate_skills = {
        normalize_skill(skill)
        for skill in profile.get("skills", [])
        if isinstance(skill, str)
    }
    required, preferred = extract_skills(text)
    required_normalized = {normalize_skill(skill) for skill in required}
    preferred_normalized = {normalize_skill(skill) for skill in preferred}
    all_required = required_normalized.union(preferred_normalized)

    matched = sorted(candidate_skills.intersection(all_required), key=str.lower)
    missing = sorted(all_required.difference(candidate_skills), key=str.lower)
    required_missing = sorted(required_normalized.difference(candidate_skills), key=str.lower)
    compatibility = round(len(matched) * 100.0 / len(all_required), 2) if all_required else 0.0

    return {
        "job_title": extract_job_title(text),
        "required_skills": sorted(required_normalized, key=str.lower),
        "preferred_skills": sorted(preferred_normalized, key=str.lower),
        "experience_requirements": extract_experience(text),
        "education_requirements": extract_education(text),
        "responsibilities": extract_responsibilities(text),
        "candidate_skills": sorted(candidate_skills, key=str.lower),
        "job_compatibility_percentage": compatibility,
        "matched_skills": matched,
        "missing_skills": missing,
        "required_skill_gaps": required_missing,
        "improvement_recommendations": [
            f"Learn or strengthen: {skill}"
            for skill in required_missing[:10]
        ],
        "interpretation": (
            "Compatibility reflects overlap with explicitly detected job skills "
            "and is not a definitive assessment of role suitability."
        ),
    }
