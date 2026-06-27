"""Centralised configuration — single source of truth for secrets + service config.

Modelled on the WCS settings pattern: a pydantic-settings ``Settings`` loaded
once at import, reading from the process environment and a local ``.env``.

All field names match the env var names in ``.env.example`` so nothing in the
launchd config or ``.env`` needs changing when adapters are swapped.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

_ROOT_ENV = Path(__file__).resolve().parents[3] / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=_ROOT_ENV, extra="ignore", case_sensitive=True)

    # ── Mistral API ──
    MISTRAL_API_KEY: str | None = None
    MISTRAL_BASE_URL: str = "https://api.mistral.ai/v1"

    # ── Server ──
    ACIS_SERVE_HOST: str = "0.0.0.0"
    ACIS_SERVE_PORT: int = 8765

    # ── Storage ──
    ACIS_DB_PATH: str = "~/.acis/acis.db"

    # ── Models ──
    # voxtral-mini-latest: stable batch alias for POST /v1/audio/transcriptions.
    # The -realtime-2602 variant only works with Mistral's WebSocket streaming API.
    ACIS_ASR_MODEL: str = "voxtral-mini-latest"
    # mistral-medium-latest is now Medium 3.5 ($1.50/1M in) — far too costly for
    # ~1,020 cue-extraction calls per session; Small 4 handles structured JSON well
    ACIS_CUE_MODEL: str = "mistral-small-latest"
    # Large 3 still the right call for the single end-of-session summary;
    # swap to magistral-small-latest to A/B test reasoning-chain keypoints
    ACIS_SUMMARY_MODEL: str = "mistral-large-latest"

    # ── Pipeline tuning ──
    ACIS_CUE_THRESHOLD_WORDS: int = 50

    # ── Audio capture (CLI / sounddevice mode) ──
    ACIS_AUDIO_SAMPLE_RATE: int = 16000
    ACIS_AUDIO_CHUNK_SECS: float = 3.0


@lru_cache
def get_settings() -> Settings:
    """Cached singleton. Tests can call ``get_settings.cache_clear()`` to inject overrides."""
    return Settings()


settings = get_settings()
