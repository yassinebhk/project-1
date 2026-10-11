"""Render de una táctica de pádel: escena Manim + voz Edge + música + mux SIN cortes.

Se ejecuta dentro del job de GitHub Actions que instala manim+cairo/pango+ffmpeg
(solo para command=padel-once). Reproduce el pipeline validado del render-test:
  1. manim -qm --disable_caching <Scene>  → mp4 mudo 1080x1920
  2. Edge TTS (en-US-GuyNeural, rate -6%)  → voice.mp3 (narración didáctica)
  3. Pixabay music (best-effort)           → music.mp3
  4. mux: tpad congela la tarjeta de cierre + apad en la voz → final sin cortes

Feature flag PADEL_FORMAT (default "manim"):
  - "manim"   → formato 2D top-down original ([[padel-formato-ganador-manim]])
  - "tactika" → formato 3D isométrico réplica @tactikapadel (nuevo 10/10),
                voz en ES-ES-AlvaroNeural, slide dato académico incluido,
                avatar narrador "Mark" como overlay ffmpeg bottom-left.
"""
from __future__ import annotations

import asyncio
import os
import random
import subprocess
from pathlib import Path

# Flag de formato: default manim (seguro, probado). Para activar tactika en el
# runner, exportar PADEL_FORMAT=tactika en el env del step.
PADEL_FORMAT = os.environ.get("PADEL_FORMAT", "manim").strip().lower()

MANIM_SCENE_FILE = Path(__file__).parent / "manim_scene.py"
TACTIKA_SCENE_FILE = Path(__file__).parent / "tactika_scene.py"

# Voz: tactika narra en español (coincide con audiencia pádel ES hispanohablante);
# el formato manim viejo mantiene inglés para no romper los vídeos ya alineados.
EDGE_VOICE_EN = "en-US-GuyNeural"
EDGE_VOICE_ES = "es-ES-AlvaroNeural"
EDGE_RATE = "-6%"
AVATAR_PATH = Path(__file__).parent / "assets" / "mark_avatar.png"


def _render_manim(scene_class: str, scene_file: Path, topic_env: str | None = None) -> Path | None:
    base = scene_file.parent
    media = base / "media"
    subprocess.run(["rm", "-rf", str(media)], check=False)
    env = dict(os.environ)
    if topic_env:
        env["PADEL_TOPIC"] = topic_env  # plantillas data-driven leen esto
    cmd = ["manim", "-qm", "--disable_caching", str(scene_file.name), scene_class]
    r = subprocess.run(cmd, cwd=str(base), capture_output=True, text=True, timeout=900, env=env)
    if r.returncode != 0:
        print(f"  padel: manim FAIL ({scene_class})\n{r.stderr[-1500:]}")
        return None
    hits = [h for h in (base / "media").rglob(f"{scene_class}.mp4") if "videos" in h.parts]
    if not hits:
        hits = list((base / "media").rglob(f"{scene_class}.mp4"))
    return hits[0] if hits else None


async def _edge_voice(text: str, out: Path, voice: str = EDGE_VOICE_EN) -> None:
    import edge_tts
    await edge_tts.Communicate(text, voice, rate=EDGE_RATE).save(str(out))


def _ensure_avatar(work: Path) -> Path | None:
    """Devuelve path al avatar narrador 'Mark'. Prioridad:
      1. Asset manual commiteado (assets/mark_avatar.png)
      2. Generado on-demand via Pollinations anon y cacheado por run
      3. None → el pipeline sigue sin overlay (fallback silencioso)
    """
    if AVATAR_PATH.exists():
        return AVATAR_PATH
    cached = work / "mark_avatar.png"
    if cached.exists() and cached.stat().st_size > 3000:
        return cached
    try:
        import urllib.parse as _up
        import urllib.request as _ur
        prompt = ("professional male padel coach bust portrait, friendly cartoon flat vector style, "
                  "beard, headband, polo shirt green, shoulders up, centered, plain dark background")
        url = (f"https://image.pollinations.ai/prompt/{_up.quote(prompt)}"
               f"?width=400&height=400&nologo=true&model=flux&seed=42")
        req = _ur.Request(url, headers={"User-Agent": "Mozilla/5.0 padel-tactika"})
        with _ur.urlopen(req, timeout=90) as r:
            data = r.read()
        if len(data) < 3000:
            print(f"  padel: avatar Pollinations too small ({len(data)}B), skip")
            return None
        cached.write_bytes(data)
        return cached
    except Exception as e:
        print(f"  padel: avatar fetch fail — {type(e).__name__}: {e}")
        return None


def _overlay_avatar(video: Path, work: Path) -> Path:
    """Añade avatar narrador 'Mark' fijo en bottom-left (formato tactika).
    Si no hay avatar disponible (asset ni fetch), devuelve el vídeo intacto —
    el formato tactika sigue siendo válido sin él."""
    av = _ensure_avatar(work)
    if not av:
        print(f"  padel: avatar no disponible, salto overlay")
        return video
    out = work / "with_avatar.mp4"
    # Pollinations añade un watermark "pollinations.ai" ~95x25px en la esquina
    # inferior-derecha incluso con nologo=true. Recorto el 15% inferior-derecho
    # del avatar antes de escalar. Luego lo escalo a 180px y lo pego abajo-izq.
    fc = ("[1:v]crop=iw*0.80:ih*0.85:iw*0.10:0,scale=180:-1[av];"
          "[0:v][av]overlay=32:main_h-overlay_h-32")
    cmd = ["ffmpeg", "-y", "-i", str(video), "-i", str(av),
           "-filter_complex", fc, "-c:v", "libx264", "-pix_fmt", "yuv420p",
           "-preset", "veryfast", "-c:a", "copy", str(out)]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    if r.returncode != 0:
        print(f"  padel: avatar overlay FAIL (silent)\n{r.stderr[-800:]}")
        return video
    return out


def _fetch_music(work: Path) -> Path | None:
    # BGM libre: Pixabay (403 hoy) → Freesound. Ver videogen.music.
    from .. import music
    queries = ["upbeat energetic sport", "motivational upbeat",
               "electronic upbeat", "corporate positive energetic"]
    return music.fetch_bgm(queries, work / "music.mp3", min_dur=15)


def _probe_dur(p: Path) -> float:
    try:
        out = subprocess.run(
            ["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
             "-of", "csv=p=0", str(p)],
            capture_output=True, text=True, timeout=60).stdout.strip()
        return float(out)
    except Exception:
        return 0.0


def _mux(video: Path, voice: Path, music: Path | None, work: Path) -> Path:
    vdur, adur = _probe_dur(video), _probe_dur(voice)
    final_len = round(max(vdur, adur) + 1.2, 2)
    pad = round(max(0.0, final_len - vdur), 2)
    out = work / "final.mp4"
    if music:
        fc = (f"[1:v]tpad=stop_mode=clone:stop_duration={pad}[v];"
              f"[2:a]apad[vo];[0:a]volume=0.09[bg];"
              f"[vo][bg]amix=inputs=2:duration=first:dropout_transition=0[a]")
        cmd = ["ffmpeg", "-y", "-stream_loop", "-1", "-i", str(music),
               "-i", str(video), "-i", str(voice), "-filter_complex", fc,
               "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-pix_fmt", "yuv420p",
               "-preset", "veryfast", "-c:a", "aac", "-b:a", "160k", "-t", str(final_len), str(out)]
    else:
        fc = f"[0:v]tpad=stop_mode=clone:stop_duration={pad}[v];[1:a]apad[a]"
        cmd = ["ffmpeg", "-y", "-i", str(video), "-i", str(voice), "-filter_complex", fc,
               "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-pix_fmt", "yuv420p",
               "-preset", "veryfast", "-c:a", "aac", "-b:a", "160k", "-t", str(final_len), str(out)]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    if r.returncode != 0:
        print(f"  padel: mux FAIL\n{r.stderr[-1200:]}")
        return video
    return out


def render_topic(topic: dict, work: Path) -> Path | None:
    """Renderiza cualquier topic (tactic/fact/compare/checklist) completo
    (vídeo+voz+música). Devuelve mp4 final o None.

    Si PADEL_FORMAT=tactika, usa escenas 3D tactika_scene.py SOLO para tactics
    (fact/compare/checklist siguen con el formato card manim original, que ya
    funciona bien y no necesita 3D)."""
    import json as _json
    from . import manim_scene
    fmt = topic.get("format", "tactic")
    topic_env = None
    use_tactika = PADEL_FORMAT == "tactika" and fmt == "tactic"
    scene_file = TACTIKA_SCENE_FILE if use_tactika else MANIM_SCENE_FILE
    voice_name = EDGE_VOICE_ES if use_tactika else EDGE_VOICE_EN

    if fmt == "tactic":
        if use_tactika:
            from . import tactika_scene
            scene = tactika_scene.TACTIKA_TACTICS[topic["tactic"]]["scene"]
            narration = tactika_scene.narration_for(scene)
        else:
            scene = manim_scene.TACTICS[topic["tactic"]]["scene"]
            narration = manim_scene.narration_for(scene)
    else:
        scene = manim_scene.FORMAT_SCENES[fmt]
        narration = topic.get("narration") or manim_scene.narration_for(scene)
        topic_env = _json.dumps(topic, ensure_ascii=False)
    work.mkdir(parents=True, exist_ok=True)
    print(f"  padel: render Manim {scene} (format={fmt}, mode={'tactika-3D' if use_tactika else 'classic-2D'})")
    silent = _render_manim(scene, scene_file, topic_env=topic_env)
    if not silent:
        return None
    voice = work / "voice.mp3"
    try:
        asyncio.run(_edge_voice(narration, voice, voice=voice_name))
    except Exception as e:
        print(f"  padel: voice FAIL ({e})")
        return None
    music = _fetch_music(work)
    print(f"  padel: mux (music={'sí' if music else 'no'})")
    final = _mux(silent, voice, music, work)
    # Overlay avatar narrador solo en tactika (si el PNG existe).
    if use_tactika and final:
        final = _overlay_avatar(final, work)
    return final
