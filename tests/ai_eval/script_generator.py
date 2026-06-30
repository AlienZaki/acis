"""Generate synthetic conversation scripts via Mistral for pipeline evaluation."""

from __future__ import annotations

import json
from dataclasses import dataclass

import httpx

from acis.domain.entities import Utterance

_SYSTEM = """\
You are a scriptwriter for AI system evaluation.
Write a realistic spoken conversation between 2-3 participants on the given topic.
The conversation should be natural, contain technical or domain-specific terms,
include at least one question someone asks, mention at least one person by name,
and include at least one concrete next step or decision.

Respond ONLY with a JSON array of utterances:
[
  {"speaker": "Alice", "text": "...", "t_start": 0.0},
  {"speaker": "Bob",   "text": "...", "t_start": 6.0},
  ...
]

Rules:
- 10-20 turns total
- t_start increments realistically (5-10 seconds per turn)
- Each turn is 1-3 sentences
- No stage directions, no scene descriptions
- Respond ONLY with the JSON array"""


@dataclass
class ScriptGenerator:
    api_key: str
    base_url: str = "https://api.mistral.ai/v1"
    model: str = "mistral-small-latest"

    async def generate(self, topic: str) -> list[Utterance]:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                f"{self.base_url}/chat/completions",
                headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
                json={
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": _SYSTEM},
                        {"role": "user", "content": f"Topic: {topic}"},
                    ],
                    "temperature": 0.9,
                    "max_tokens": 1500,
                },
            )
            resp.raise_for_status()

        raw = resp.json()["choices"][0]["message"]["content"].strip()
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[-1]
        if raw.endswith("```"):
            raw = raw.rsplit("\n", 1)[0]

        turns = json.loads(raw.strip())
        return [
            Utterance(
                text=f"{t['speaker']}: {t['text']}",
                t_start=float(t.get("t_start", i * 7.0)),
                t_end=float(t.get("t_start", i * 7.0)) + 6.0,
            )
            for i, t in enumerate(turns)
            if isinstance(t, dict) and t.get("text")
        ]
