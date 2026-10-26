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
THREEJS_DIR = Path(__file__).parent / "threejs"

# Voz: tactika narra en español (coincide con audiencia pádel ES hispanohablante);
# el formato manim viejo mantiene inglés para no romper los vídeos ya alineados.
EDGE_VOICE_EN = "en-US-GuyNeural"
EDGE_VOICE_ES = "es-ES-AlvaroNeural"
EDGE_RATE = "-6%"
AVATAR_PATH = Path(__file__).parent / "assets" / "mark_avatar.png"


def _render_threejs(tactic_key: str, work: Path) -> Path | None:
    """Renderiza una táctica con el pipeline Three.js (puppeteer frame-by-frame).

    Usa el runner Node en `src/videogen/padel/threejs/`:
      - scene.html carga Three.js, UAL character + 43 anims, overlays HTML
      - render.js (puppeteer) captura 540 PNGs @30fps → ffmpeg → mp4 1080x1920

    Devuelve path al mp4 mudo (voz y música se añaden fuera, como el flujo
    manim). Si npm no está disponible o falla, devuelve None y el pipeline
    cae al formato que haya puesto el caller como fallback.
    """
    out_mp4 = work / f"threejs_{tactic_key}.mp4"
    env = dict(os.environ)
    env["SCENE"] = tactic_key
    env["OUT_MP4"] = str(out_mp4)
    env["FPS"] = env.get("FPS", "30")
    # Asegura node_modules instalados — solo primera vez
    nm = THREEJS_DIR / "node_modules"
    if not nm.exists():
        print(f"  padel/threejs: primera vez — npm install (cache $TMPDIR)")
        r = subprocess.run(
            ["npm", "install", "--cache", os.environ.get("TMPDIR", "/tmp") + "/npm-cache-padel"],
            cwd=str(THREEJS_DIR), capture_output=True, text=True, timeout=600, env=env,
        )
        if r.returncode != 0:
            print(f"  padel/threejs: npm install FAIL\n{r.stderr[-1500:]}")
            return None
    r = subprocess.run(
        ["npm", "run", "render"], cwd=str(THREEJS_DIR),
        capture_output=True, text=True, timeout=1500, env=env,
    )
    if r.returncode != 0 or not out_mp4.exists():
        print(f"  padel/threejs: render FAIL\n{r.stderr[-1500:]}\n{r.stdout[-500:]}")
        return None
    return out_mp4


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


def _kokoro_voice(text: str, out: Path, lang: str = "es") -> None:
    """Fallback TTS local vía Kokoro-onnx cuando edge-tts falla (403 Microsoft
    bloqueando IP del runner self-hosted). Local, offline, gratis.

    Descarga el modelo ~350MB la primera vez a ~/.kokoro/ y luego lo cachea.
    Convierte WAV→MP3 con ffmpeg para mantener compat con el resto del pipeline.
    """
    import subprocess
    import urllib.request
    from kokoro_onnx import Kokoro
    import soundfile as sf

    voice = "em_alex" if lang == "es" else "am_michael"
    model_dir = Path.home() / ".kokoro"
    model_dir.mkdir(exist_ok=True)
    model_path = model_dir / "kokoro-v1.0.onnx"
    voices_path = model_dir / "voices-v1.0.bin"
    base = "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0"
    if not model_path.exists():
        print(f"  padel: kokoro descargando modelo ~350MB → {model_path}")
        urllib.request.urlretrieve(f"{base}/kokoro-v1.0.onnx", model_path)
    if not voices_path.exists():
        urllib.request.urlretrieve(f"{base}/voices-v1.0.bin", voices_path)

    k = Kokoro(str(model_path), str(voices_path))
    audio, sr = k.create(text, voice=voice, speed=1.05, lang=lang)
    wav_tmp = out.with_suffix(".wav")
    sf.write(str(wav_tmp), audio, sr)
    subprocess.run(
        ["ffmpeg", "-y", "-loglevel", "error", "-i", str(wav_tmp),
         "-codec:a", "libmp3lame", "-b:a", "128k", str(out)],
        check=True,
    )
    wav_tmp.unlink(missing_ok=True)


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


def _overlay_endcard(video: Path, work: Path, handle: str, lang: str = "en") -> Path:
    """Superpone un end-card de SUSCRIPCIÓN full-frame los últimos ~2.5s → la palanca
    de conversión views→subs que faltaba en Pádel. Graceful: cualquier fallo devuelve
    el vídeo original (un overlay decorativo nunca debe tumbar el render)."""
    try:
        from .. import graphics
        dur = _probe_dur(video)
        if dur < 4:
            return video
        ec = graphics.render_endcard_overlay_png(work / "endcard.png", handle, "Padel Pro", lang=lang)
        start = round(dur - 2.5, 2)
        out = work / "final_endcard.mp4"
        cmd = ["ffmpeg", "-y", "-loglevel", "error", "-i", str(video), "-i", str(ec),
               "-filter_complex",
               f"[0:v][1:v]overlay=0:0:enable='between(t\\,{start}\\,{dur + 0.5})'[v]",
               "-map", "[v]", "-map", "0:a?", "-c:v", "libx264", "-pix_fmt", "yuv420p",
               "-preset", "veryfast", "-c:a", "copy", str(out)]
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
        if r.returncode == 0 and out.exists() and out.stat().st_size > 10000:
            print(f"  padel: end-card suscripción · {handle}")
            return out
        print(f"  padel: end-card overlay FAIL (silent)\n{r.stderr[-400:]}")
    except Exception as e:
        print(f"  padel: end-card skip ({type(e).__name__}: {e})")
    return video


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
    # Modos de formato pádel:
    #   PADEL_FORMAT=threejs → nueva réplica @tactikapadel completa (3D realista,
    #     avatar Mark + pastillas + fondo gradas + narración timeline). Solo
    #     aplicable a tactics; falls back a manim para fact/compare/checklist.
    #   PADEL_FORMAT=tactika → formato 3D isométrico manim (viejo).
    #   PADEL_FORMAT=manim (default) → 2D top-down manim original.
    # Modo threejs: por ahora solo la táctica 'lob' tiene scene definida en
    # scene.html; el resto (bandeja/back_wall/smash/drop_shot/serve/positioning/
    # defense) cae a manim/tactika hasta que se amplíe TACTICS en scene.html.
    THREEJS_SUPPORTED = {"lob", "bandeja", "back_wall", "smash", "drop_shot", "serve", "positioning", "defense"}
    use_threejs = (PADEL_FORMAT == "threejs"
                   and fmt == "tactic"
                   and topic.get("tactic") in THREEJS_SUPPORTED)
    use_tactika = PADEL_FORMAT == "tactika" and fmt == "tactic" and not use_threejs
    scene_file = TACTIKA_SCENE_FILE if use_tactika else MANIM_SCENE_FILE
    voice_name = EDGE_VOICE_ES if (use_tactika or use_threejs) else EDGE_VOICE_EN

    if fmt == "tactic":
        tactic_key = topic["tactic"]
        if use_threejs:
            # scene.html tiene narración embedded sincronizada por timeline;
            # aquí mantenemos el concat de bullets por táctica para que TTS
            # genere audio alineado (el pipeline threejs no lo lee del HTML).
            # Las bullets deben coincidir con las de scene.html → TACTICS[t].narration
            THREEJS_NARRATION = {
                "lob": ("El globo. Clave cuando dominan la red. Elévala profunda por encima de ellos. "
                        "Los fuerza a retroceder al fondo. Mientras recuperan posición, tú avanzas a la red. "
                        "Controlar la red, es controlar el punto."),
                "bandeja": ("La bandeja. Tu respuesta cuando te globean. No retrocedas: salta y golpea descendente. "
                            "La pelota cae profunda sin perder la red. Impides que recuperen la posición. "
                            "La bandeja mantiene el control de la red."),
                "back_wall": ("La pared de fondo es tu aliada. Deja que bote primero el suelo, luego la pared. "
                              "Esperas el rebote con pala baja. Devuelves con control, no con fuerza. "
                              "Dominar la pared es dominar el fondo."),
                "smash": ("El remate. El golpe definitivo. No vayas con todo: elige el ángulo. "
                          "Cruza la bola o busca la pared de fondo. Fuerza sin ángulo es error asegurado. "
                          "Ángulo gana puntos. Fuerza los regala."),
                "drop_shot": ("La dejada. El golpe de sorpresa. Rivales lejos de la red: oportunidad. "
                              "Tacto suave, bola muy cerca de la red. No pueden llegar. Punto para ti. "
                              "Timing y suavidad, fórmula ganadora."),
                "serve": ("El saque. Tu primer movimiento del punto. Siempre bajo. Siempre cruzado. "
                          "Busca los pies, no el espacio. Devolución débil igual a tú con control. "
                          "Saque bajo igual a saque efectivo."),
                "positioning": ("El posicionamiento es el ochenta por ciento del pádel. Siempre juntos. Siempre en paralelo. "
                                "Nunca uno arriba y otro atrás. Avanzáis y retrocedéis como una unidad. "
                                "Juntos ganáis más. Separados perdéis más."),
                "defense": ("Rivales en la red. Toca defender. Levanta la bola. Alta y profunda. "
                            "Al centro: dudan quién la golpea. Esperas tu oportunidad para subir. "
                            "Defensa paciente, punto ganado."),
            }
            narration = THREEJS_NARRATION.get(tactic_key, THREEJS_NARRATION["lob"])
            scene = tactic_key
        elif use_tactika:
            from . import tactika_scene
            scene = tactika_scene.TACTIKA_TACTICS[tactic_key]["scene"]
            narration = tactika_scene.narration_for(scene)
        else:
            scene = manim_scene.TACTICS[tactic_key]["scene"]
            narration = manim_scene.narration_for(scene)
    else:
        scene = manim_scene.FORMAT_SCENES[fmt]
        narration = topic.get("narration") or manim_scene.narration_for(scene)
        topic_env = _json.dumps(topic, ensure_ascii=False)
    work.mkdir(parents=True, exist_ok=True)
    mode_label = "threejs-tactika" if use_threejs else ("tactika-3D" if use_tactika else "classic-2D")
    print(f"  padel: render {scene} (format={fmt}, mode={mode_label})")
    if use_threejs:
        silent = _render_threejs(topic["tactic"], work)
        if not silent:
            # Fallback a manim si threejs falla (p.ej. puppeteer sin Chrome en
            # el runner, o npm install roto). Mantiene el pipeline funcional
            # aunque la rama 3D nueva falle en producción.
            print(f"  padel/threejs: FAIL → fallback a manim scene")
            fallback_scene = manim_scene.TACTICS[topic["tactic"]]["scene"]
            silent = _render_manim(fallback_scene, MANIM_SCENE_FILE)
    else:
        silent = _render_manim(scene, scene_file, topic_env=topic_env)
    if not silent:
        return None
    voice = work / "voice.mp3"
    try:
        asyncio.run(_edge_voice(narration, voice, voice=voice_name))
    except Exception as e:
        # edge-tts da 403 recurrente contra wss://speech.platform.bing.com
        # en el runner self-hosted (Mac). Issue externo de Microsoft Bing
        # bloqueando el token DRM/IP. Fallback a Kokoro local — slower pero
        # offline y gratis. [[coste-cero-obligatorio]]
        print(f"  padel: edge-tts FAIL ({type(e).__name__}) — fallback Kokoro local")
        try:
            lang = "es" if (use_tactika or use_threejs) else "en"
            _kokoro_voice(narration, voice, lang=lang)
        except Exception as e2:
            print(f"  padel: kokoro FAIL también ({e2})")
            return None
    music = _fetch_music(work)
    print(f"  padel: mux (music={'sí' if music else 'no'})")
    final = _mux(silent, voice, music, work)
    # Overlay avatar narrador: solo en tactika manim (threejs ya tiene al avatar
    # Mark incrustado en el DOM capturado por puppeteer, no hay que remuxar).
    if use_tactika and final:
        final = _overlay_avatar(final, work)
    # End-card de suscripción los últimos ~2.5s (conversión views→subs). Solo si Padel
    # tiene canal propio (si cae a un host, el @handle no aplica). Reversible ENDCARD_DISABLE=1.
    if (final and os.environ.get("ENDCARD_DISABLE", "").lower() not in ("1", "true", "yes")
            and os.environ.get("YT_PADEL_REFRESH_TOKEN")):
        final = _overlay_endcard(final, work, "@PadelProES",
                                 lang="es" if use_tactika else "en")
    return final
