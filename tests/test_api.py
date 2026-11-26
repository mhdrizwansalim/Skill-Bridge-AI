import os
from pathlib import Path

import pytest
from fastapi.testclient import TestClient


TEST_DB = Path("/tmp/skillbridge_api_test.db")
TEST_DB.unlink(missing_ok=True)
os.environ["DATABASE_URL"] = f"sqlite:///{TEST_DB.as_posix()}"

from backend.main import app


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_candidate_profile_is_a_consistent_response(client):
    response = client.get("/candidate/resumes")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "success"
    assert isinstance(payload["resumes"], list)


def test_career_recommendations_are_normalized(client):
    response = client.get("/career/recommendations")
    assert response.status_code == 200
    first = response.json()["recommendations"][0]
    assert "career_title" in first
    assert "match_percentage" in first
    assert "matched_skills" in first
    assert "missing_skills" in first


def test_skill_gap_is_normalized(client):
    response = client.get("/career/skill-gap")
    assert response.status_code == 200
    payload = response.json()["skill_gap_analysis"]
    assert "candidate_skills" in payload
    assert "target_skills" in payload
    assert "skill_match_percentage" in payload


def test_job_description_analysis(client):
    response = client.post(
        "/jobs/analyze",
        json={
            "text": (
                "Data Scientist\nResponsibilities:\n"
                "- Build machine learning models\n"
                "- Develop SQL reports\n"
                "Required skills: Python, SQL, machine learning, statistics\n"
                "Education: Bachelor degree in Computer Science"
            )
        },
    )
    assert response.status_code == 200
    analysis = response.json()["analysis"]
    assert analysis["job_title"]
    assert "job_compatibility_percentage" in analysis


def test_cv_profile_and_generation(client):
    profile_response = client.get("/cv/profile")
    assert profile_response.status_code == 200
    profile = profile_response.json()["candidate"]
    generate_response = client.post("/cv/generate", json=profile)
    assert generate_response.status_code == 200
    assert generate_response.json()["download_url"] == "/cv/download"


def test_mock_interview_start_and_submit(client):
    start = client.post("/interview/start", json={"target_role": "Data Scientist"})
    assert start.status_code == 200
    questions = start.json()["questions"]

    submit = client.post(
        "/interview/submit",
        json={
            "target_role": "Data Scientist",
            "answers": [
                {
                    "question": item["question"],
                    "answer": (
                        "I would first define the problem, prepare and analyze the data, "
                        "build and test a machine-learning approach, and explain the measured result."
                    ),
                }
                for item in questions[:2]
            ],
        },
    )
    assert submit.status_code == 200
    assert 0 <= submit.json()["average_score"] <= 100


def test_invalid_resume_upload(client):
    response = client.post(
        "/resume/upload",
        files={"file": ("resume.txt", b"not a pdf", "text/plain")},
    )
    assert response.status_code == 400


def test_scanned_pdf_uses_ocr_or_returns_clear_error(client):
    with open("data/raw/test_resumes/scanned_test_resume.pdf", "rb") as file:
        response = client.post(
            "/resume/upload",
            files={"file": ("scanned_test_resume.pdf", file, "application/pdf")},
        )
    assert response.status_code in (200, 422)
    if response.status_code == 422:
        assert "OCR" in response.json()["detail"]
    else:
        assert "candidate" in response.json()


def test_candidate_profile_update(client):
    profile_response = client.get("/candidate/profile")
    assert profile_response.status_code == 200
    resume_id = profile_response.json()["resume_id"]
    update = client.put(
        f"/candidate/profile/{resume_id}",
        json={"summary": "Experienced in Python and data analysis."},
    )
    assert update.status_code == 200
    assert update.json()["candidate"]["summary"] == "Experienced in Python and data analysis."
