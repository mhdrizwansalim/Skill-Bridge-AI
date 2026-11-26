import re
from typing import Iterable

from backend.services.cv_service import load_profile


QUESTION_BANK = {
    "data": [
        "Describe a data project, including the problem, your approach, and the result.",
        "How would you prepare and clean a dataset for analysis?",
        "Explain the difference between supervised and unsupervised learning.",
        "How do you evaluate whether a machine-learning model is reliable?",
        "How would you explain a technical result to a non-technical stakeholder?",
    ],
    "software": [
        "Describe a project you built and explain the main technical decisions.",
        "How do you approach debugging a difficult production issue?",
        "What factors do you consider when designing a maintainable system?",
        "Explain how you would test a new feature.",
        "How do you collaborate with a team during code review?",
    ],
    "general": [
        "Tell me about a project that demonstrates skills relevant to this role.",
        "What are your strongest qualifications for this role?",
        "Describe a difficult challenge and the steps you used to address it.",
        "How do you plan and prioritize your learning?",
        "What would you do in your first 30 days in this role?",
    ],
}


def select_question_set(target_role: str) -> list[str]:
    role = target_role.lower()
    if any(word in role for word in ("data", "machine learning", "ai", "analytics", "science")):
        return QUESTION_BANK["data"].copy()
    if any(word in role for word in ("software", "developer", "engineer", "full stack", "backend", "frontend")):
        return QUESTION_BANK["software"].copy()
    return QUESTION_BANK["general"].copy()


def evaluate_answer(answer: str, role: str, candidate_skills: Iterable[str]) -> dict:
    cleaned = answer.strip()
    words = re.findall(r"[a-z0-9]+", cleaned.lower())
    role_terms = set(re.findall(r"[a-z0-9]+", role.lower()))
    skill_terms = set(
        term
        for skill in candidate_skills
        for term in re.findall(r"[a-z0-9]+", str(skill).lower())
    )
    answer_terms = set(words)

    relevance = bool(answer_terms.intersection(role_terms.union(skill_terms)))
    structure = any(
        marker in cleaned.lower()
        for marker in ("first", "because", "result", "approach", "step", "example")
    )
    specificity = len(set(words)) >= 25
    length = len(words) >= 20
    clarity = len(cleaned.split(".")) >= 2

    criteria = {
        "relevance": 20 if relevance else 5,
        "specificity": 20 if specificity else 8,
        "structure": 20 if structure else 8,
        "answer_length": 20 if length else 8,
        "clarity": 20 if clarity else 8,
    }
    score = sum(criteria.values())

    feedback = []
    if not relevance:
        feedback.append("Connect the answer more clearly to the target role or relevant skills.")
    if not structure:
        feedback.append("Use a clear structure: situation or task, action, and result.")
    if not specificity:
        feedback.append("Add a concrete example or measurable result.")
    if not length:
        feedback.append("Expand the answer with enough context and detail.")
    if not clarity:
        feedback.append("Use complete sentences and explain the reasoning in a clear sequence.")
    if not feedback:
        feedback.append("Strong answer. Keep the example concise and tie the result to impact.")

    return {
        "score": score,
        "criteria": criteria,
        "feedback": feedback,
        "transparent_method": (
            "Local rule-based score based on role/skill relevance, specificity, "
            "structure, answer length, and clarity."
        ),
    }
