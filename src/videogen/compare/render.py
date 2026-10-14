"""Render de una comparación de escala: escena Manim + voz Edge + mux sin cortes.

Reutiliza la fontanería probada del pádel (_render_manim / _edge_voice / _kokoro_voice).
Solo corre dentro de Actions (manim + cairo/pango + ffmpeg instalados ahí).
"""
from __future__ import annotations

import asyncio
import json
import os
import subprocess
from pathlib import Path

SCENE_FILE = Path(__file__).parent / "manim_scene.py"
EDGE_VOICE = "en-US-GuyNeural"


def _dur(path: Path) -> float:
    try:
        r = subprocess.run(
            ["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
             "-of", "csv=p=0", str(path)],
            capture_output=True, text=True,
        )
        return float((r.stdout or "0").strip() or 0)
    except Exception:
        return 0.0


def render_topic(topic: dict, work: Path) -> Path | None:
    """Genera el mp4 final (escena Manim + narración). Devuelve el path o None."""
    work.mkdir(parents=True, exist_ok=True)
    from ..padel import render as prender  # reutiliza _render_manim / voces

    # 1) Escena Manim (data-driven vía COMPARE_TOPIC)
    env_topic = json.dumps({k: topic[k] for k in ("title", "unit", "source", "items")
                            if k in topic}, ensure_ascii=False)
    os.environ["COMPARE_TOPIC"] = env_topic
    try:
        mp4 = prender._render_manim("ScaleCompare", SCENE_FILE)
    finally:
        os.environ.pop("COMPARE_TOPIC", None)
    if not mp4 or not Path(mp4).exists():
        print("  compare: manim render FALLÓ")
        return None
    silent = work / "scene.mp4"
    subprocess.run(["cp", str(mp4), str(silent)], check=False)

    # 2) Narración (Edge EN → fallback Kokoro local)
    narration = (topic.get("narration") or topic.get("title") or "").strip()
    voice = work / "voice.mp3"
    if narration:
        try:
            asyncio.run(prender._edge_voice(narration, voice, voice=EDGE_VOICE))
        except Exception as e:
            print(f"  compare: edge-tts falló ({type(e).__name__}) → kokoro")
            try:
                prender._kokoro_voice(narration, voice, lang="en")
            except Exception as e2:
                print(f"  compare: kokoro falló ({e2}) → sin voz")
                voice = None
    else:
        voice = None

    # 3) Mux sin cortes: congela el último frame hasta cubrir la voz + 1.2s de cola
    final = work / "final.mp4"
    if voice and voice.exists():
        vdur, adur = _dur(silent), _dur(voice)
        total = round(max(vdur, adur) + 1.2, 2)
        pad = round(max(0.0, total - vdur), 2)
        cmd = ["ffmpeg", "-y", "-loglevel", "error", "-i", str(silent), "-i", str(voice),
               "-filter_complex",
               f"[0:v]tpad=stop_mode=clone:stop_duration={pad}[v];[1:a]apad[a]",
               "-map", "[v]", "-map", "[a]", "-t", str(total),
               "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "veryfast",
               "-c:a", "aac", "-b:a", "160k", str(final)]
    else:
        cmd = ["ffmpeg", "-y", "-loglevel", "error", "-i", str(silent),
               "-c:v", "libx264", "-pix_fmt", "yuv420p", str(final)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0 or not final.exists():
        print(f"  compare: mux FALLÓ\n{(r.stderr or '')[-800:]}")
        return silent if silent.exists() else None
    return final
