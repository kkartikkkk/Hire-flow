"""Grok AI provider implementation.

Uses the OpenAI-compatible API provided by Grok Cloud.
Falls back to sandbox mock parser if no API key is provided.
"""

import json
import re
from typing import Any
import httpx

from app.ai.provider import AIProvider
from app.config import get_settings
from app.core.exceptions import AIException
from app.core.logging import get_logger

logger = get_logger(__name__)


class GrokProvider(AIProvider):
    """Grok Cloud AI provider using OpenAI-compatible API.

    Attributes:
        base_url: The API base URL.
        api_key: The API authentication key.
        model: The model identifier to use.
    """

    def __init__(self) -> None:
        settings = get_settings()
        self.base_url = settings.AI_BASE_URL
        self.api_key = settings.AI_API_KEY
        self.model = settings.AI_MODEL
        if not self.api_key:
            logger.warning("Grok API key is empty. Operating in SANDBOX (Mock) mode.")
        else:
            logger.info("GrokProvider initialized with model=%s", self.model)

    async def parse_resume(self, content: str) -> dict[str, Any]:
        """Parse resume content using Grok AI.

        If API key is missing, runs in Sandbox mode.
        """
        if not self.api_key or self.api_key.strip() in ("", "change-me", "your-grok-api-key"):
            return self._parse_resume_sandbox(content)

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        system_prompt = (
            "You are an expert resume parsing AI. Extract candidate information from the resume text.\n"
            "You MUST respond ONLY with a JSON object. No explanations, no markdown block wrappers.\n"
            "Respond exactly in this JSON format:\n"
            "{\n"
            "  \"name\": \"\",\n"
            "  \"email\": \"\",\n"
            "  \"phone\": \"\",\n"
            "  \"skills\": [],\n"
            "  \"education\": [],\n"
            "  \"experience\": [],\n"
            "  \"projects\": [],\n"
            "  \"certifications\": []\n"
            "}"
        )

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": content},
            ],
            "response_format": {"type": "json_object"},
            "temperature": 0.1,
        }

        # Try once with a retry in case of json validation failure
        for attempt in range(2):
            try:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    response = await client.post(
                        f"{self.base_url.rstrip('/')}/chat/completions",
                        headers=headers,
                        json=payload,
                    )
                    if response.status_code != 200:
                        logger.error("Grok API error: %d - %s", response.status_code, response.text)
                        raise AIException(f"Grok API returned status code {response.status_code}")

                    res_json = response.json()
                    choice_text = res_json["choices"][0]["message"]["content"].strip()
                    
                    # Clean markdown wrappers if returned
                    if choice_text.startswith("```json"):
                        choice_text = choice_text[7:]
                    if choice_text.endswith("```"):
                        choice_text = choice_text[:-3]
                    choice_text = choice_text.strip()

                    parsed_data = json.loads(choice_text)
                    
                    # Validate expected fields
                    expected_fields = ["name", "email", "phone", "skills", "education", "experience", "projects", "certifications"]
                    for field in expected_fields:
                        if field not in parsed_data:
                            parsed_data[field] = [] if field in ["skills", "education", "experience", "projects", "certifications"] else ""
                    
                    logger.info("Successfully parsed resume using Grok AI")
                    return parsed_data
            except (httpx.HTTPError, AIException) as exc:
                logger.error("Grok API parser attempt %d failed: %s", attempt + 1, exc)
                if attempt == 1:
                    raise AIException("Grok AI service is currently unavailable.") from exc
            except (KeyError, IndexError, json.JSONDecodeError) as exc:
                logger.error("Invalid JSON response from Grok Parser: %s", exc)
                if attempt == 1:
                    raise AIException("AI returned invalid JSON structure.") from exc

        raise AIException("Failed to retrieve valid parsed resume data.")

    async def calculate_fit_score(
        self,
        resume_data: dict[str, Any],
        job_requirements: dict[str, Any],
    ) -> dict[str, Any]:
        """Calculate candidate-job fit score using Grok AI.

        If API key is missing, runs in Sandbox mode.
        """
        if not self.api_key or self.api_key.strip() in ("", "change-me", "your-grok-api-key"):
            return self._calculate_fit_score_sandbox(resume_data, job_requirements)

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        system_prompt = (
            "You are an AI recruitment bot. Compare candidate profile against job requirements.\n"
            "You MUST respond ONLY with a JSON object. No explanations, no markdown blocks.\n"
            "Format of expected JSON response:\n"
            "{\n"
            "  \"score\": 0,\n"
            "  \"strengths\": [],\n"
            "  \"missing_skills\": [],\n"
            "  \"recommendation\": \"\",\n"
            "  \"summary\": \"\"\n"
            "}\n"
            "Note: score must be an integer between 0 and 100."
        )

        user_content = json.dumps({
            "candidate": resume_data,
            "job": job_requirements
        })

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content},
            ],
            "response_format": {"type": "json_object"},
            "temperature": 0.2,
        }

        for attempt in range(2):
            try:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    response = await client.post(
                        f"{self.base_url.rstrip('/')}/chat/completions",
                        headers=headers,
                        json=payload,
                    )
                    if response.status_code != 200:
                        logger.error("Grok API error: %d - %s", response.status_code, response.text)
                        raise AIException(f"Grok API returned status code {response.status_code}")

                    res_json = response.json()
                    choice_text = res_json["choices"][0]["message"]["content"].strip()

                    if choice_text.startswith("```json"):
                        choice_text = choice_text[7:]
                    if choice_text.endswith("```"):
                        choice_text = choice_text[:-3]
                    choice_text = choice_text.strip()

                    parsed_data = json.loads(choice_text)

                    # Ensure keys exist
                    if "score" not in parsed_data:
                        parsed_data["score"] = 50
                    if "strengths" not in parsed_data:
                        parsed_data["strengths"] = []
                    if "missing_skills" not in parsed_data:
                        parsed_data["missing_skills"] = []
                    if "recommendation" not in parsed_data:
                        parsed_data["recommendation"] = ""
                    if "summary" not in parsed_data:
                        parsed_data["summary"] = ""

                    logger.info("Successfully calculated fit score using Grok AI")
                    return parsed_data
            except (httpx.HTTPError, AIException) as exc:
                logger.error("Grok API fit-score attempt %d failed: %s", attempt + 1, exc)
                if attempt == 1:
                    raise AIException("Grok AI service is currently unavailable.") from exc
            except (KeyError, IndexError, json.JSONDecodeError) as exc:
                logger.error("Invalid JSON response from Grok Scorer: %s", exc)
                if attempt == 1:
                    raise AIException("AI returned invalid JSON structure.") from exc

        raise AIException("Failed to retrieve valid fit score assessment.")

    def _parse_resume_sandbox(self, content: str) -> dict[str, Any]:
        """Extract placeholder structures in sandbox mode."""
        logger.info("Running parse_resume in Sandbox Mode")

        # Heuristic email extractor
        email_match = re.search(r"[\w\.-]+@[\w\.-]+\.\w+", content)
        email = email_match.group(0) if email_match else "sandbox.candidate@example.com"

        # Heuristic phone extractor
        phone_match = re.search(r"\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}", content)
        phone = phone_match.group(0) if phone_match else "555-0199"

        # Heuristic name extractor
        lines = [line.strip() for line in content.split("\n") if line.strip()]
        name = lines[0] if lines else "Candidate Name"
        if len(name) > 50:
            name = name[:50]

        # Extract common keywords for skills
        known_skills = ["Python", "FastAPI", "React", "TypeScript", "SQL", "PostgreSQL", "Docker", "AWS", "Go", "Git"]
        extracted_skills = []
        for skill in known_skills:
            if re.search(r"\b" + re.escape(skill) + r"\b", content, re.IGNORECASE):
                extracted_skills.append(skill)
        
        if not extracted_skills:
            extracted_skills = ["Python", "General Software Engineering"]

        return {
            "name": name,
            "email": email,
            "phone": phone,
            "skills": extracted_skills,
            "experience": ["3 years as Backend Developer at Sandbox Inc."],
            "education": ["Bachelor of Science in Computer Science, State University (2021)"],
            "projects": ["Build ATS Candidate platform prototype"],
            "certifications": ["AWS Certified Solutions Architect"]
        }

    def _calculate_fit_score_sandbox(
        self,
        resume_data: dict[str, Any],
        job_requirements: dict[str, Any],
    ) -> dict[str, Any]:
        """Calculate mock score in sandbox mode."""
        logger.info("Running calculate_fit_score in Sandbox Mode")

        cand_skills = [s.lower() for s in resume_data.get("skills", [])]
        req_skills_str = job_requirements.get("required_skills", "")
        req_skills = [s.strip().lower() for s in req_skills_str.split(",") if s.strip()]

        matches = []
        gaps = []
        for req in req_skills:
            if any(req in cand for cand in cand_skills) or any(cand in req for cand in cand_skills):
                matches.append(req.title())
            else:
                gaps.append(req.title())

        match_count = len(matches)
        total_reqs = len(req_skills) if req_skills else 1
        ratio = match_count / total_reqs

        score = int(60 + (ratio * 35))
        score = min(max(score, 0), 100)

        strengths = [f"Matches required skill: {m}" for m in matches]
        if not strengths:
            strengths = ["Candidate has general software development skills."]

        missing_skills = [g for g in gaps]
        if not missing_skills:
            missing_skills = ["No major missing technical skills identified."]

        return {
            "score": score,
            "strengths": strengths,
            "missing_skills": missing_skills,
            "recommendation": "Highly recommend interviewing this candidate for the backend engineering role.",
            "summary": f"The candidate matches {match_count} of the {total_reqs} required skills.",
        }
