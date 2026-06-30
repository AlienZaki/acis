"""Synthesize scripted conversations to WAV using macOS `say` + `afconvert`.

Each speaker gets a different voice. Turns are concatenated into one audio
stream that mimics a real recorded conversation, then split into 3-second
chunks to match the ACIS pipeline's chunk size.
"""

from __future__ import annotations

import io
import os
import subprocess
import tempfile
import wave

from acis.domain.entities import Utterance

# macOS TTS voices — enough for 3-person conversations
_VOICES: dict[str, str] = {
    "Alice":   "Samantha",
    "Bob":     "Tom",
    "Carol":   "Karen",
    "Dave":    "Alex",
    "Eve":     "Victoria",
    "Frank":   "Daniel",
}
_DEFAULT_VOICE = "Samantha"

SAMPLE_RATE = 16_000
CHUNK_SECS = 3.0


def _voice_for(speaker: str) -> str:
    return _VOICES.get(speaker, _DEFAULT_VOICE)


def _synthesize_text(voice: str, text: str) -> bytes:
    """Return 16 kHz mono 16-bit PCM WAV bytes for `text` spoken in `voice`."""
    with tempfile.TemporaryDirectory() as tmpdir:
        aiff = os.path.join(tmpdir, "out.aiff")
        wav = os.path.join(tmpdir, "out.wav")
        subprocess.run(["say", "-v", voice, "-o", aiff, text], check=True, capture_output=True)
        subprocess.run(
            ["afconvert", "-f", "WAVE", "-d", "LEI16@16000", "-c", "1", aiff, wav],
            check=True, capture_output=True,
        )
        with open(wav, "rb") as f:
            return f.read()


def _pcm(wav_bytes: bytes) -> bytes:
    buf = io.BytesIO(wav_bytes)
    with wave.open(buf, "rb") as wf:
        return wf.readframes(wf.getnframes())


def _wrap_wav(pcm: bytes) -> bytes:
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(pcm)
    return buf.getvalue()


def _silence(secs: float = 0.3) -> bytes:
    """Short silence between speakers."""
    return b"\x00" * int(SAMPLE_RATE * secs * 2)


def synthesize_script(utterances: list[Utterance]) -> bytes:
    """Synthesize all utterance turns and return one concatenated WAV."""
    pcm_parts: list[bytes] = []
    for utt in utterances:
        text = utt.text
        # Strip "Speaker: " prefix added by ScriptGenerator
        if ": " in text:
            speaker, spoken = text.split(": ", 1)
        else:
            speaker, spoken = "Alice", text
        voice = _voice_for(speaker.strip())
        turn_wav = _synthesize_text(voice, spoken)
        pcm_parts.append(_pcm(turn_wav))
        pcm_parts.append(_silence())      # brief pause between turns

    return _wrap_wav(b"".join(pcm_parts))


def split_chunks(wav_bytes: bytes, chunk_secs: float = CHUNK_SECS) -> list[bytes]:
    """Split a WAV into fixed-size chunks, each with its own WAV header."""
    all_pcm = _pcm(wav_bytes)
    chunk_size = int(SAMPLE_RATE * chunk_secs * 2)  # bytes: 2 bytes per 16-bit sample
    chunks = []
    for i in range(0, len(all_pcm), chunk_size):
        chunk = all_pcm[i : i + chunk_size]
        if len(chunk) < chunk_size:
            chunk += b"\x00" * (chunk_size - len(chunk))  # pad last chunk
        chunks.append(_wrap_wav(chunk))
    return chunks
