"""Configuración central. Carga .env y expone settings."""
from __future__ import annotations

import os
from pathlib import Path
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[2]
load_dotenv(ROOT / ".env")

OUTPUT_DIR = ROOT / "output"
PENDING_DIR = OUTPUT_DIR / "pending_review"
APPROVED_DIR = OUTPUT_DIR / "approved"
UPLOADED_DIR = OUTPUT_DIR / "uploaded"
MUSIC_DIR = ROOT / "music"
ASSETS_DIR = ROOT / "assets"
SECRETS_DIR = ROOT / "secrets"
PROMPTS_DIR = ROOT / "prompts"

for d in (PENDING_DIR, APPROVED_DIR, UPLOADED_DIR, SECRETS_DIR):
    d.mkdir(parents=True, exist_ok=True)


def _require(key: str) -> str:
    val = os.environ.get(key, "").strip()
    if not val or val.startswith("sk-ant-xxx") or val == "xxx":
        raise RuntimeError(
            f"Missing env var {key}. Copy .env.example to .env and fill it in."
        )
    return val


def elevenlabs_key() -> str:
    return _require("ELEVENLABS_API_KEY")


def elevenlabs_voice(lang: str) -> str:
    key = f"ELEVENLABS_VOICE_ID_{lang.upper()}"
    return _require(key)


def pexels_key() -> str:
    return _require("PEXELS_API_KEY")


def pexels_keys() -> list[str]:
    """Todas las claves Pexels disponibles, para ROTACIÓN.

    El free tier son 200 req/h POR CLAVE. Una tanda de catchup (~15 canales)
    las agota y da 429. Crear claves extra en pexels.com es gratis → con 2-3
    claves el límite efectivo se multiplica y el 429 casi desaparece.

    Fuentes (en orden, dedup): PEXELS_API_KEY (admite varias separadas por
    comas) + PEXELS_API_KEY_2, _3, … Devuelve [] si no hay ninguna.
    """
    raw: list[str] = []
    raw += [p.strip() for p in os.environ.get("PEXELS_API_KEY", "").split(",")]
    i = 2
    while True:
        v = os.environ.get(f"PEXELS_API_KEY_{i}", "").strip()
        if not v:
            break
        raw.append(v)
        i += 1
    seen: set[str] = set()
    out: list[str] = []
    for k in raw:
        if k and k not in seen:
            seen.add(k)
            out.append(k)
    return out


def gemini_key() -> str | None:
    """Requerida para script (Gemini Flash) y opcional para Veo hook."""
    val = os.environ.get("GEMINI_API_KEY", "").strip()
    return val or None


def pollinations_token() -> str | None:
    """Opcional. Token de Pollinations (tier registrado, más límite)."""
    val = os.environ.get("POLLINATIONS_TOKEN", "").strip()
    return val or None


def telegram_token() -> str:
    return _require("TELEGRAM_BOT_TOKEN")


def telegram_chat_id() -> str | None:
    val = os.environ.get("TELEGRAM_CHAT_ID", "").strip()
    return val or None


def default_duration() -> int:
    return int(os.environ.get("VIDEO_DEFAULT_DURATION_SECONDS", "60"))
