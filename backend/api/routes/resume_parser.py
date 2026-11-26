import csv
import json
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

import fitz
from fastapi import APIRouter, HTTPException

from backend.config import PROJECT_ROOT, CV_PATH


router = APIRouter(prefix="/resume", tags=["Resume"])

UPLOAD_PATH = PROJECT_ROOT / "data" / "processed" / "uploaded_resumes"
RESUME_LIBRARY = CV_PATH / "resume_library"


# Used only if the project's processed skills CSV is not available.
DEFAULT_SKILLS = [
    "Python",
    "SQL",
    "Machine Learning",
    "Deep Learning",
    "Data Analysis",
    "Pandas",
    "NumPy",
    "Data Visualization",
    "Statistics",
    "Excel",
    "Power BI",
    "Tableau",
    "Java",
    "JavaScript",
    "HTML",
    "CSS",
    "Natural Language Processing",
    "TensorFlow",
    "PyTorch",
    "Git",
]


# Different resumes use different headings for the same section.
SECTION_ALIASES = {
    "summary": [
        "professional summary",
        "summary",
        "profile",
        "career objective",
        "objective",
    ],
    "experience": [
        "work experience",
        "professional experience",
        "employment history",
        "experience",
    ],
    "education": [
        "education",
        "academic background",
        "qualifications",
    ],
    "skills": [
        "technical skills",
        "key skills",
        "skills",
        "core competencies",
    ],
    "projects": [
        "projects",
        "personal projects",
        "academic projects",
    ],
    "certifications": [
        "certifications",
        "certificates",
        "licenses",
    ],
    "achievements": [
        "achievements",
        "awards",
        "honors",
    ],
    "languages": [
        "languages",
        "language proficiency",
    ],
}


def extract_pdf_text(pdf_path):
    """Extract embedded text, then OCR when text is unavailable."""
    page_text = []

    with fitz.open(pdf_path) as document:
        for page in document:
            page_text.append(page.get_text("text") or "")

    embedded_text = "\n".join(page_text).strip()
    if len(embedded_text) >= 50:
        return embedded_text

    tesseract = shutil.which("tesseract")
    if not tesseract:
        return ""

    ocr_text = []
    with fitz.open(pdf_path) as document:
        with tempfile.TemporaryDirectory(prefix="skillbridge_ocr_") as temp_dir:
            temp_path = Path(temp_dir)
            for page_number, page in enumerate(document):
                pix = page.get_pixmap(matrix=fitz.Matrix(2.5, 2.5), alpha=False)
                image_path = temp_path / f"page-{page_number + 1}.png"
                pix.save(image_path)
                try:
                    result = subprocess.run(
                        [tesseract, str(image_path), "stdout", "--psm", "6", "-l", "eng"],
                        check=True,
                        capture_output=True,
                        text=True,
                        timeout=120,
                    )
                    ocr_text.append(result.stdout)
                except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
                    continue

    return "\n".join(ocr_text).strip()


def load_skill_names():
    """Load skill names from the project's processed skill vocabulary."""
    possible_files = [
        PROJECT_ROOT / "data" / "processed" / "unified_skills.csv",
        PROJECT_ROOT / "data" / "processed" / "unified_skills_standardized.csv",
    ]

    for csv_path in possible_files:
        if not csv_path.is_file():
            continue

        with csv_path.open(
            "r",
            encoding="utf-8-sig",
            newline="",
        ) as csv_file:
            reader = csv.DictReader(csv_file)

            possible_columns = [
                "Skill Name",
                "skill_name",
                "skill",
                "name",
            ]

            skill_column = next(
                (
                    column
                    for column in possible_columns
                    if column in (reader.fieldnames or [])
                ),
                None,
            )

            if skill_column is None:
                continue

            skills = {
                row[skill_column].strip()
                for row in reader
                if row.get(skill_column)
                and row[skill_column].strip()
            }

            if skills:
                return sorted(skills, key=str.lower)

    return DEFAULT_SKILLS.copy()


def extract_contact_details(text):
    """Extract basic contact details using regular expressions."""
    contact = {
        "name": None,
        "email": None,
        "phone": None,
        "linkedin": None,
        "github": None,
    }

    email_match = re.search(
        r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",
        text,
    )

    phone_match = re.search(
        r"(?<!\d)(?:\+?\d{1,3}[ .-]?)?"
        r"(?:\(?\d{2,5}\)?[ .-]?)?\d{5,10}(?!\d)",
        text,
    )

    linkedin_match = re.search(
        r"(?:https?://)?(?:www\.)?linkedin\.com/in/[A-Za-z0-9_-]+",
        text,
        re.IGNORECASE,
    )

    github_match = re.search(
        r"(?:https?://)?(?:www\.)?github\.com/[A-Za-z0-9_-]+",
        text,
        re.IGNORECASE,
    )

    contact["email"] = email_match.group(0) if email_match else None
    contact["phone"] = phone_match.group(0).strip() if phone_match else None
    contact["linkedin"] = linkedin_match.group(0) if linkedin_match else None
    contact["github"] = github_match.group(0) if github_match else None

    # Use the first non-empty line as a possible name, with basic checks.
    ignored_first_lines = {
        "resume",
        "curriculum vitae",
        "cv",
        "profile",
        "professional summary",
    }

    first_lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    if first_lines:
        first_line = first_lines[0]

        looks_like_name = (
            len(first_line.split()) <= 5
            and first_line.lower() not in ignored_first_lines
            and not re.search(r"@|https?://|\d", first_line)
        )

        if looks_like_name:
            contact["name"] = first_line

    return contact


def extract_resume_sections(text):
    """Collect text appearing below recognized resume section headings."""
    heading_lookup = {
        alias.lower(): section
        for section, aliases in SECTION_ALIASES.items()
        for alias in aliases
    }

    collected_sections = {
        section: []
        for section in SECTION_ALIASES
    }

    current_section = None

    for line in text.splitlines():
        cleaned_line = line.strip()

        if not cleaned_line:
            continue

        normalized_heading = re.sub(
            r"^[#*•\-\s]+",
            "",
            cleaned_line.lower(),
        )
        normalized_heading = re.sub(
            r"[:\s]+$",
            "",
            normalized_heading,
        )

        matched_section = heading_lookup.get(normalized_heading)

        if matched_section:
            current_section = matched_section
        elif current_section:
            collected_sections[current_section].append(cleaned_line)

    return {
        section: "\n".join(lines).strip()
        for section, lines in collected_sections.items()
    }


def extract_skills(text):
    """Find skills from the project's vocabulary without inventing skills."""
    found_skills = []
    text_lower = text.lower()

    for skill in load_skill_names():
        skill_pattern = (
            r"(?<![a-zA-Z0-9])"
            + re.escape(skill.lower())
            + r"(?![a-zA-Z0-9])"
        )

        if re.search(skill_pattern, text_lower):
            found_skills.append(skill)

    return sorted(set(found_skills), key=str.lower)


def create_candidate_profile(
    filename,
    file_path,
    contact,
    sections,
    skills,
):
    """Create a profile using the top-level format from Notebook 08."""
    return {
        "candidate_id": Path(filename).stem,
        "name": contact.get("name"),
        "email": contact.get("email"),
        "phone": contact.get("phone"),
        "linkedin": contact.get("linkedin"),
        "github": contact.get("github"),
        "skills": skills,
        "summary": sections.get("summary", ""),
        "education": sections.get("education", ""),
        "experience": sections.get("experience", ""),
        "projects": sections.get("projects", ""),
        "certifications": sections.get("certifications", ""),
        "achievements": sections.get("achievements", ""),
        "languages": sections.get("languages", ""),
        "source_file": str(file_path),
        "extraction_method": "embedded text or OCR",
    }


@router.get("/parse/{filename}")
def parse_resume(filename: str):
    """Parse an uploaded PDF and save its structured candidate profile."""

    # Prevent access to files outside the designated upload directory.
    if Path(filename).name != filename or not filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Invalid PDF filename.",
        )

    file_path = UPLOAD_PATH / filename

    if not file_path.is_file():
        raise HTTPException(
            status_code=404,
            detail="Uploaded resume not found.",
        )

    try:
        extracted_text = extract_pdf_text(file_path)

        if len(extracted_text.strip()) < 50:
            raise HTTPException(
                status_code=422,
                detail=(
                    "Not enough readable text found in this PDF. "
                    "No readable text was found. Install Tesseract OCR and ensure "
                    "the 'eng' language data is available."
                ),
            )

        contact = extract_contact_details(extracted_text)
        sections = extract_resume_sections(extracted_text)
        skills = extract_skills(extracted_text)

        profile = create_candidate_profile(
            filename,
            file_path,
            contact,
            sections,
            skills,
        )

        RESUME_LIBRARY.mkdir(
            parents=True,
            exist_ok=True,
        )

        profile_path = RESUME_LIBRARY / f"{profile['candidate_id']}.json"

        with profile_path.open("w", encoding="utf-8") as json_file:
            json.dump(
                profile,
                json_file,
                indent=2,
                ensure_ascii=False,
            )

        return {
            "status": "success",
            "filename": filename,
            "profile_id": profile["candidate_id"],
            "profile_saved": True,
            "candidate": profile,
            "extraction": {
                "characters_extracted": len(extracted_text),
                "skills_found": len(skills),
                "name_found": bool(contact.get("name")),
                "email_found": bool(contact.get("email")),
            },
        }

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Resume parsing failed: {str(exc)}",
        ) from exc
