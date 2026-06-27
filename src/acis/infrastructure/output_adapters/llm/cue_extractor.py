"""Extract the four cue types from a rolling transcript via 4 parallel Mistral calls.

Each call uses a focused system prompt for one cue type and returns a JSON array
of {title, body} objects.  Results are deduplicated upstream by ``CueDeduplicator``.
"""

from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass
from uuid import uuid4

import httpx

from ....domain.entities import Cue, CueType

_SYSTEMS: dict[CueType, str] = {
    "concept": """\
You are an ambient AI assistant listening to a real conversation.
Extract 0-3 CONCEPTS: technical terms, frameworks, theories, or ideas that the \
participants might benefit from a quick definition of.
For each return: {"title": "Term name", "body": "One clear sentence definition."}
Only extract concepts that are clearly present and would genuinely help.
Respond ONLY with a JSON array (e.g. [{"title": "...", "body": "..."}]).
If no strong concepts: respond with [].""",
    "answer": """\
You are an ambient AI assistant listening to a real conversation.
Extract 0-2 QUESTIONS the participants are explicitly asking or clearly wondering about.
For each return: {"title": "Short question (≤8 words)", "body": "One sentence direct answer."}
Only answer questions clearly present in the transcript.  Do not invent questions.
Respond ONLY with a JSON array.
If no answerable questions: respond with [].""",
    "suggestion": """\
You are an ambient AI assistant listening to a real conversation.
Extract 0-2 SUGGESTIONS: follow-up questions to ask, unexplored angles, or concrete next steps.
For each return: {"title": "Suggestion headline (≤8 words)", "body": "One sentence elaboration."}
Only suggest things directly relevant to the current discussion.
Respond ONLY with a JSON array.
If nothing useful: respond with [].""",
    "bio": """\
You are an ambient AI assistant listening to a real conversation.
Extract 0-2 PEOPLE mentioned by name who the participants might want quick background on.
For each return: {"title": "Person's full name", "body": "One sentence: role/title and why relevant."}
Only include people explicitly named in the transcript.  Never invent names.
Respond ONLY with a JSON array.
If no named people: respond with [].""",
}


@dataclass
class MistralCueExtractor:
    api_key: str
    base_url: str = "https://api.mistral.ai/v1"
    model: str = "mistral-small-latest"

    async def _call_one(self, cue_type: CueType, transcript: str) -> list[Cue]:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
                json={
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": _SYSTEMS[cue_type]},
                        {"role": "user", "content": f"Transcript:\n\n{transcript}"},
                    ],
                    "temperature": 0.3,
                    "max_tokens": 512,
                },
            )
            response.raise_for_status()

        raw = response.json()["choices"][0]["message"]["content"].strip()
        # Strip markdown code fences that models add despite instructions.
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[-1]
        if raw.endswith("```"):
            raw = raw.rsplit("\n", 1)[0]
        try:
            parsed = json.loads(raw.strip())
            items: list[dict] = parsed if isinstance(parsed, list) else next(
                (v for v in parsed.values() if isinstance(v, list)), []
            )
        except (json.JSONDecodeError, AttributeError):
            return []

        return [
            Cue(
                id=str(uuid4()),
                cue_type=cue_type,
                title=item["title"],
                body=item["body"],
                session_id="",  # patched in by extract()
            )
            for item in items
            if isinstance(item, dict) and "title" in item and "body" in item
        ]

    async def extract(self, transcript: str, session_id: str) -> list[Cue]:
        if not transcript.strip():
            return []

        results = await asyncio.gather(
            self._call_one("concept", transcript),
            self._call_one("answer", transcript),
            self._call_one("suggestion", transcript),
            self._call_one("bio", transcript),
            return_exceptions=True,
        )

        from dataclasses import replace

        cues: list[Cue] = []
        for group in results:
            if isinstance(group, list):
                cues.extend(replace(cue, session_id=session_id) for cue in group)
        return cues
