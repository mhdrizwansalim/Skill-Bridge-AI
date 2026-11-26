import json
import re
from pathlib import Path

from backend.config import CV_PATH, PROJECT_ROOT


CANDIDATE_REPORT_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "candidates"
    / "complete_candidate_career_report.json"
)
RESUME_LIBRARY = CV_PATH / "resume_library"


def normalize_skill(skill: object) -> str:
    if not isinstance(skill, str):
        return ""
    text = re.sub(r"\s+", " ", skill.strip())
    return text.casefold()


def unique_skills(skills) -> list[str]:
    normalized = {}
    if not isinstance(skills, list):
        return []
    for skill in skills:
        cleaned = normalize_skill(skill)
        if cleaned:
            normalized.setdefault(cleaned, cleaned)
    return sorted(normalized.values(), key=str.lower)


def load_latest_profile() -> dict:
    saved_profiles = sorted(
        RESUME_LIBRARY.glob("*.json"),
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )
    if saved_profiles:
        with saved_profiles[0].open("r", encoding="utf-8") as file:
            return json.load(file)

    if CANDIDATE_REPORT_PATH.exists():
        with CANDIDATE_REPORT_PATH.open("r", encoding="utf-8") as file:
            report = json.load(file)
        if isinstance(report.get("candidate_profile"), dict):
            return report["candidate_profile"]

    return {}


def load_career_report() -> dict:
    if not CANDIDATE_REPORT_PATH.exists():
        return {}
    with CANDIDATE_REPORT_PATH.open("r", encoding="utf-8") as file:
        return json.load(file)


def normalize_career_recommendations() -> tuple[list[dict], dict]:
    report = load_career_report()
    profile = load_latest_profile()
    raw_recommendations = report.get("career_recommendations", [])
    if not isinstance(raw_recommendations, list):
        raw_recommendations = []

    candidate_skills = unique_skills(profile.get("skills"))
    normalized = []
    for item in raw_recommendations:
        if not isinstance(item, dict):
            continue

        title = item.get("Career") or item.get("career_title") or "Career"
        matched = unique_skills(
            item.get("Matched Skills")
            or item.get("matching_skills")
            or []
        )
        missing = unique_skills(
            item.get("Missing Skills")
            or item.get("missing_skills")
            or []
        )
        total_raw = item.get("Total Required Skills")
        total_required = (
            int(total_raw)
            if isinstance(total_raw, (int, float))
            else len(set(matched + missing))
        )
        if total_required <= 0:
            total_required = len(set(matched + missing))
        match_percentage = round(len(matched) * 100.0 / total_required, 2) if total_required else 0.0

        normalized.append(
            {
                "career_title": str(title),
                "match_percentage": match_percentage,
                "matched_skills": matched,
                "missing_skills": missing,
                "total_required_skills": total_required,
                "skill_development_recommendations": [
                    f"Learn or strengthen: {skill}"
                    for skill in missing[:5]
                ],
                "interpretation": (
                    "This low score indicates a skill gap in the current profile, "
                    "not a definitive judgment of your ability."
                ),
            }
        )

    return normalized, {
        "candidate_name": profile.get("name") or report.get("candidate_name"),
        "candidate_skills": candidate_skills,
    }


def normalize_skill_gap() -> dict:
    report = load_career_report()
    profile = load_latest_profile()
    candidate_skills = unique_skills(profile.get("skills"))

    raw_gap = report.get("skill_gap_analysis", {})
    if isinstance(raw_gap, list):
        raw_gap = raw_gap[0] if raw_gap else {}
    if not isinstance(raw_gap, dict):
        raw_gap = {}

    target_career = (
        raw_gap.get("Target Career")
        or raw_gap.get("target_career")
        or "Target career"
    )
    target_skills = unique_skills(
        raw_gap.get("Target Skills")
        or raw_gap.get("target_skills")
        or []
    )
    if not target_skills:
        target_skills = unique_skills(
            raw_gap.get("Missing Skills")
            or raw_gap.get("missing_skills")
            or []
        )

    candidate_set = set(candidate_skills)
    target_set = set(target_skills)
    matched = sorted(candidate_set.intersection(target_set), key=str.lower)
    missing = sorted(target_set.difference(candidate_set), key=str.lower)
    percentage = round(len(matched) * 100.0 / len(target_set), 2) if target_set else 0.0

    return {
        "candidate_skills": candidate_skills,
        "target_career": str(target_career),
        "target_skills": sorted(target_set, key=str.lower),
        "matched_skills": matched,
        "missing_skills": missing,
        "skill_match_percentage": percentage,
        "learning_priorities": [
            {"priority": index + 1, "skill": skill}
            for index, skill in enumerate(missing)
        ],
        "suggested_learning_sequence": missing,
        "interpretation": (
            "This match reflects overlap with the target career's listed skills "
            "and is not a definitive assessment of employability."
        ),
    }
