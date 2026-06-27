"""End-of-session summary via Mistral Large 3 (`mistral-large-latest`).

Produces a structured JSON payload: title, prose, keypoints, and action items.
"""

from __future__ import annotations

import json
from dataclasses import dataclass

import httpx

from ....domain.entities import AISummary, Session, Utterance

_SYSTEM = """\
You are summarising a conversation for the user who was one of its participants.
Given the full timestamped transcript, produce a JSON object with exactly these keys:
{
  "title":        "<5-8 word session title>",
  "prose":        "<1-2 sentence high-level summary>",
  "keypoints":    [{"heading": "<theme>", "bullets": ["<point>", ...]}, ...],
  "action_items": ["<concrete task>", ...]
}
keypoints: 3-5 thematic groups, 2-4 bullets each.
action_items: 0-8 concrete, specific tasks arising from the conversation.
Respond ONLY with a valid JSON object — no markdown fences, no explanation."""


@dataclass
class MistralSummarizer:
    api_key: str
    base_url: str = "https://api.mistral.ai/v1"
    model: str = "mistral-large-latest"

    async def summarize(self, session: Session, utterances: list[Utterance]) -> AISummary:
        transcript = "\n".join(f"[{u.t_start:.1f}s] {u.text}" for u in utterances)

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
                json={
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": _SYSTEM},
                        {"role": "user", "content": f"Transcript:\n\n{transcript}"},
                    ],
                    "temperature": 0.4,
                    "max_tokens": 1024,
                    "response_format": {"type": "json_object"},
                },
            )
            response.raise_for_status()

        data = json.loads(response.json()["choices"][0]["message"]["content"])
        return AISummary(
            session_id=session.id,
            title=data.get("title", session.name),
            prose=data.get("prose", ""),
            keypoints=data.get("keypoints", []),
            action_items=data.get("action_items", []),
        )
