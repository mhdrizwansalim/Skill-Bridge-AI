import json
from pathlib import Path
from typing import Iterable

from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

from backend.config import CV_PATH, PROJECT_ROOT


RESUME_LIBRARY = CV_PATH / "resume_library"
CV_OUTPUT_DIR = CV_PATH
CV_OUTPUT_PATH = CV_OUTPUT_DIR / "skillbridge_generated_cv.pdf"
CV_DATA_PATH = CV_OUTPUT_DIR / "generated_cv.json"
UPDATED_PROFILE_PATH = CV_OUTPUT_DIR / "updated_candidate.json"


def load_profile() -> dict:
    saved_profiles = sorted(
        RESUME_LIBRARY.glob("*.json"),
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )
    if saved_profiles:
        with saved_profiles[0].open("r", encoding="utf-8") as file:
            return normalize_profile(json.load(file))

    if UPDATED_PROFILE_PATH.exists():
        with UPDATED_PROFILE_PATH.open("r", encoding="utf-8") as file:
            profile = json.load(file)
        if isinstance(profile, dict):
            return normalize_profile(profile)

    return normalize_profile({})


def normalize_profile(profile: dict) -> dict:
    personal = profile.get("personal_details") or {}
    name = (
        profile.get("name")
        or profile.get("full_name")
        or personal.get("full_name")
    )
    email = profile.get("email") or personal.get("email")
    phone = profile.get("phone") or personal.get("phone")
    linkedin = profile.get("linkedin") or personal.get("linkedin")
    github = profile.get("github") or personal.get("github")
    portfolio = personal.get("portfolio")
    if not github:
        github = portfolio

    skills = profile.get("skills") or []
    if isinstance(skills, str):
        skills = [skill.strip() for skill in skills.split(",") if skill.strip()]
    elif not isinstance(skills, list):
        skills = []

    def text_value(field: str) -> str:
        value = profile.get(field, "")
        if isinstance(value, list):
            lines = []
            for item in value:
                if isinstance(item, dict):
                    lines.append(
                        " - ".join(
                            str(part).strip()
                            for part in item.values()
                            if part
                        )
                    )
                elif item:
                    lines.append(str(item))
            return "\n".join(lines)
        return str(value or "")

    summary = profile.get("summary") or personal.get("professional_summary") or ""

    return {
        "name": name or "",
        "email": email or "",
        "phone": phone or "",
        "linkedin": linkedin or "",
        "github": github or "",
        "summary": text_value("summary") or str(summary or ""),
        "skills": sorted(set(str(skill).strip() for skill in skills if str(skill).strip()), key=str.lower),
        "education": text_value("education"),
        "experience": text_value("experience"),
        "projects": text_value("projects"),
        "certifications": text_value("certifications"),
        "achievements": text_value("achievements"),
        "languages": text_value("languages"),
    }


def generate_cv(profile: dict) -> dict:
    normalized = normalize_profile(profile)
    CV_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    document = SimpleDocTemplate(
        str(CV_OUTPUT_PATH),
        pagesize=A4,
        rightMargin=0.65 * inch,
        leftMargin=0.65 * inch,
        topMargin=0.55 * inch,
        bottomMargin=0.55 * inch,
        title="SkillBridge Generated CV",
    )
    styles = getSampleStyleSheet()
    name_style = styles["Title"]
    name_style.alignment = TA_LEFT
    heading_style = styles["Heading2"]
    body_style = styles["BodyText"]

    story = []
    story.append(Paragraph(normalized["name"] or "Candidate", name_style))

    contact = "  |  ".join(
        value
        for value in (
            normalized["email"],
            normalized["phone"],
            normalized["linkedin"],
            normalized["github"],
        )
        if value
    )
    if contact:
        story.append(Paragraph(contact, body_style))
    story.append(Spacer(1, 0.12 * inch))

    sections = (
        ("Professional Summary", normalized["summary"]),
        ("Skills", ", ".join(normalized["skills"])),
        ("Education", normalized["education"]),
        ("Experience", normalized["experience"]),
        ("Projects", normalized["projects"]),
        ("Certifications", normalized["certifications"]),
        ("Achievements", normalized["achievements"]),
        ("Languages", normalized["languages"]),
    )
    for title, content in sections:
        if content:
            story.append(Paragraph(title, heading_style))
            for paragraph in str(content).split("\n"):
                if paragraph.strip():
                    story.append(Paragraph(paragraph.strip(), body_style))
            story.append(Spacer(1, 0.08 * inch))

    document.build(story)

    with CV_DATA_PATH.open("w", encoding="utf-8") as file:
        json.dump(normalized, file, indent=2, ensure_ascii=False)

    return normalized
