"""Voxtral Mini ASR via Mistral /v1/audio/transcriptions.

Sends raw WAV bytes as a multipart upload and returns the recognised text.
Silence / no-speech returns an empty string.
"""

from __future__ import annotations

from dataclasses import dataclass

import httpx


@dataclass
class VoxtralASR:
    api_key: str
    base_url: str = "https://api.mistral.ai/v1"
    model: str = "voxtral-mini-latest"

    async def transcribe(self, wav_bytes: bytes) -> str:
        """POST WAV bytes to Voxtral; return transcript (empty string on silence)."""
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{self.base_url}/audio/transcriptions",
                headers={"Authorization": f"Bearer {self.api_key}"},
                files={"file": ("audio.wav", wav_bytes, "audio/wav")},
                data={"model": self.model},
            )
            response.raise_for_status()
        return response.json().get("text", "").strip()
