import json
import re
from pathlib import Path
from typing import Iterable

import requests

from backend.config import CV_PATH, OLLAMA_MODEL, OLLAMA_URL, PROJECT_ROOT


MENTOR_PROFILE_PATH = (
    PROJECT_ROOT / "data" / "processed" / "career_mentor" / "mentor_candidate_profile.json"
)
CAREER_CHUNKS_PATH = (
    PROJECT_ROOT / "data" / "processed" / "career_mentor" / "career_text_chunks.json"
)
RESUME_LIBRARY = CV_PATH / "resume_library"


def load_candidate_profile() -> dict:
    saved_profiles = sorted(
        RESUME_LIBRARY.glob("*.json"),
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )
    if saved_profiles:
        with saved_profiles[0].open("r", encoding="utf-8") as file:
            return json.load(file)

    if MENTOR_PROFILE_PATH.exists():
        with MENTOR_PROFILE_PATH.open("r", encoding="utf-8") as file:
            return json.load(file)

    raise FileNotFoundError("No candidate profile is available for the career mentor.")


def _tokens(text: str) -> set[str]:
    return {
        token
        for token in re.findall(r"[a-z0-9]+", text.lower())
        if len(token) > 2
    }


def retrieve_context(question: str, limit: int = 5) -> list[dict]:
    if not CAREER_CHUNKS_PATH.exists():
        return []

    with CAREER_CHUNKS_PATH.open("r", encoding="utf-8") as file:
        chunks = json.load(file)

    question_tokens = _tokens(question)
    ranked = []
    for chunk in chunks:
        if not isinstance(chunk, dict):
            continue
        searchable = " ".join(
            str(chunk.get(field, ""))
            for field in ("title", "text", "category")
        )
        overlap = len(question_tokens.intersection(_tokens(searchable)))
        if overlap:
            ranked.append((overlap, chunk))

    ranked.sort(key=lambda item: item[0], reverse=True)
    return [chunk for _, chunk in ranked[:limit]]


def build_prompt(question: str, candidate_profile: dict, context: Iterable[dict]) -> str:
    context_text = "\n\n".join(
        f"{chunk.get('title', 'Career context')}: {chunk.get('text', '')}"
        for chunk in context
    )
    return (
        "You are the grounded SkillBridge AI Career Mentor. "
        "Use only the candidate profile and retrieved career context below. "
        "Do not invent qualifications, experience, skills, or achievements. "
        "If context is insufficient, say what information is missing.\n\n"
        f"Candidate profile:\n{json.dumps(candidate_profile, ensure_ascii=False)}\n\n"
        f"Retrieved career context:\n{context_text or 'No matching career context was retrieved.'}\n\n"
        f"Candidate question:\n{question}"
    )


def generate_answer(question: str) -> tuple[str, dict, list[dict]]:
    candidate_profile = load_candidate_profile()
    context = retrieve_context(question)
    prompt = build_prompt(question, candidate_profile, context)

    try:
        response = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json={"model": OLLAMA_MODEL, "prompt": prompt, "stream": False},
            timeout=180,
        )
        response.raise_for_status()
        payload = response.json()
    except requests.RequestException as error:
        raise RuntimeError(
            f"Ollama is unavailable at {OLLAMA_URL}. Configure OLLAMA_URL and OLLAMA_MODEL."
        ) from error

    answer = payload.get("response")
    if not isinstance(answer, str) or not answer.strip():
        raise RuntimeError("Ollama returned an empty mentor response.")

    return answer.strip(), candidate_profile, context
