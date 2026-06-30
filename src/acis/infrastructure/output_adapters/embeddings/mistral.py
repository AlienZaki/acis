"""Mistral embeddings via POST /v1/embeddings.

Embeds cue titles so ``SemanticDeduplicator`` can drop near-duplicate cues the
rolling extraction window keeps re-deriving (e.g. "How many companies are in the
center?" vs "...in the Gründungszentrum?").
"""

from __future__ import annotations

from dataclasses import dataclass

import httpx


@dataclass
class MistralEmbedder:
    api_key: str
    base_url: str = "https://api.mistral.ai/v1"
    model: str = "mistral-embed"

    async def embed(self, texts: list[str]) -> list[list[float]]:
        """Return one embedding vector per input text (empty input → empty list)."""
        if not texts:
            return []
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{self.base_url}/embeddings",
                headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
                json={"model": self.model, "input": texts},
            )
            response.raise_for_status()
        data = response.json()["data"]
        return [item["embedding"] for item in data]
