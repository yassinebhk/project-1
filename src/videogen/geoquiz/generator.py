"""Generador de vídeo GeoQuiz (EN) — "guess the country by its flag".

Sin voz (música + texto en pantalla → esquiva la limitación del TTS). Frames con
PIL (1080x1920) → concat con ffmpeg → música (helper de ranking). Banderas desde
flagcdn.com (dominio público). 5 rondas: bandera + cuenta atrás 3-2-1 → reveal
país + capital. Cierre con CTA "comment your score". Ver [[tanda-canales-02-10]].
"""
from __future__ import annotations

import os
import subprocess
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from ..config import ROOT

W, H = 1080, 1920
# Piel visual ACTIVA (se reasigna por episodio en _apply_theme → cada día sale una
# paleta distinta). WHITE se mantiene fijo: es el texto principal y el marco de la
# bandera, debe seguir legible sobre cualquier fondo. Defaults = tema "navy".
BG = (14, 23, 38)          # navy oscuro
ACCENT = (57, 224, 208)    # turquesa
GOLD = (245, 197, 66)
WHITE = (240, 244, 248)
MUTED = (150, 165, 185)
FONT_PATH = ROOT / "assets" / "fonts" / "Montserrat.ttf"
FLAG_CACHE = ROOT / "output" / "geoquiz_assets" / "flags"

# ── Rotación de piel visual (anti "contenido repetitivo" de TikTok, 17/10/26) ──
# TikTok capa lo que percibe como el MISMO vídeo repetido. El quiz variaba las
# preguntas pero la piel (fondo navy + intro idéntica + mismos colores) era clavada
# cada día → firma de contenido repetitivo. Rotamos paleta + copy por episodio (por
# día) para que cada subida se vea distinta. Todos los fondos son OSCUROS para que
# WHITE/MUTED sigan legibles y el marco blanco de la bandera funcione.
THEMES = [
    {"name": "navy",    "bg": (14, 23, 38), "accent": (57, 224, 208),  "gold": (245, 197, 66),  "muted": (150, 165, 185)},
    {"name": "plum",    "bg": (26, 16, 40), "accent": (200, 130, 255), "gold": (255, 185, 95),  "muted": (178, 162, 192)},
    {"name": "forest",  "bg": (10, 30, 22), "accent": (95, 230, 150),  "gold": (240, 205, 90),  "muted": (152, 182, 162)},
    {"name": "crimson", "bg": (32, 16, 22), "accent": (255, 115, 120), "gold": (245, 200, 100), "muted": (196, 162, 166)},
    {"name": "cyan",    "bg": (8, 30, 36),  "accent": (70, 214, 224),  "gold": (250, 210, 120), "muted": (150, 182, 186)},
    {"name": "indigo",  "bg": (18, 18, 46), "accent": (126, 152, 255), "gold": (255, 200, 110), "muted": (168, 172, 202)},
    {"name": "amber",   "bg": (32, 23, 14), "accent": (255, 172, 86),  "gold": (250, 222, 120), "muted": (198, 178, 156)},
]

# Variantes de copy de intro/outro — cambian los frames 1º y último (los que más
# pesan en el hash perceptual) además del color.
INTRO_COPY = [
    {"l1": "GUESS THE",  "l2": "COUNTRY",   "sub": "flags · capitals · maps · monuments"},
    {"l1": "CAN YOU",    "l2": "GUESS IT?", "sub": "flags · capitals · silhouettes"},
    {"l1": "NAME THE",   "l2": "COUNTRY",   "sub": "one shot — how many can you get?"},
    {"l1": "COUNTRY",    "l2": "QUIZ",      "sub": "how good is your geography?"},
    {"l1": "GEO",        "l2": "CHALLENGE", "sub": "flags · capitals · maps"},
]
# OJO: la fuente (Montserrat) NO tiene glifos de emoji → cualquier emoji sale como
# cuadro "tofu" en el frame. Mantener el copy SIN emojis (van en title/description).
# Plantillas de título (metadata YT/caption) — rotan por día para no repetir el
# mismo título clavado (otra señal de contenido repetitivo). El emoji aquí SÍ vale:
# es texto de metadata, no se renderiza con la fuente del frame.
TITLES = [
    "Guess the country 🌍 | {n} questions, easy → hard",
    "Can you guess all {n}? 🌍 Geography quiz",
    "Name the country 🌍 | {n}-question geo quiz",
    "Geo challenge 🌍 | {n} countries, easy → hard",
    "How good is your geography? 🌍 {n} questions",
]
OUTRO_COPY = [
    {"l1": "How many",   "l2": "did you get?", "cta": "Comment your score",       "follow": "Follow for more geo quizzes"},
    {"l1": "What's your", "l2": "score?",      "cta": "Drop it in the comments",  "follow": "Follow for a quiz every day"},
    {"l1": "Did you",    "l2": "ace it?",      "cta": "Comment how many you got", "follow": "Follow — new quiz daily"},
    {"l1": "Count your", "l2": "correct ones", "cta": "Tell me your score below", "follow": "Follow for more"},
]


def _rotation_index() -> int:
    """Índice de tema para hoy. GEOQUIZ_THEME (nombre o nº) lo fuerza (preview/test);
    si no, rota por día del calendario → días seguidos salen con piel distinta."""
    override = os.environ.get("GEOQUIZ_THEME", "").strip()
    if override:
        for i, t in enumerate(THEMES):
            if t["name"] == override.lower():
                return i
        try:
            return int(override) % len(THEMES)
        except ValueError:
            pass
    return datetime.now(timezone.utc).toordinal() % len(THEMES)


def _apply_theme(idx: int) -> str:
    """Reasigna la paleta activa (globals) al tema idx. Devuelve el nombre."""
    global BG, ACCENT, GOLD, MUTED
    t = THEMES[idx % len(THEMES)]
    BG, ACCENT, GOLD, MUTED = t["bg"], t["accent"], t["gold"], t["muted"]
    return t["name"]


def _font(size: int):
    try:
        return ImageFont.truetype(str(FONT_PATH), size)
    except Exception:
        return ImageFont.load_default()


def _text_center(draw, cx, y, text, font, fill, max_w=None):
    """Dibuja texto centrado horizontalmente en cx. Devuelve alto usado."""
    lines = [text]
    if max_w:
        words = text.split()
        lines, cur = [], ""
        for w in words:
            test = (cur + " " + w).strip()
            if draw.textlength(test, font=font) <= max_w:
                cur = test
            else:
                if cur:
                    lines.append(cur)
                cur = w
        if cur:
            lines.append(cur)
    yy = y
    asc, desc = font.getmetrics()
    lh = asc + desc + 8
    for ln in lines:
        wline = draw.textlength(ln, font=font)
        draw.text((cx - wline / 2, yy), ln, font=font, fill=fill)
        yy += lh
    return yy - y


def _fit_font(draw, text: str, size: int, max_w: int):
    """Fuente que garantiza que `text` cabe en una línea de ancho max_w (encoge
    hasta 40px). Evita que un titular largo (ej. 'CHALLENGE') se salga del frame."""
    f = _font(size)
    while size > 40 and draw.textlength(text, font=f) > max_w:
        size -= 6
        f = _font(size)
    return f


def _base() -> Image.Image:
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    # viñeta sutil arriba/abajo
    for i in range(220):
        a = int(40 * (1 - i / 220))
        d.line([(0, i), (W, i)], fill=(BG[0] + a // 6, BG[1] + a // 6, BG[2] + a // 5))
    return img


def _paste_image(img: Image.Image, src: Path, cy: int, max_w: int = 820, max_h: int = 820,
                 frame: bool = True, transparent_ok: bool = False,
                 tint_rgb: tuple[int, int, int] | None = None) -> None:
    """Pega imagen (bandera/monumento/silueta) centrada horizontalmente, altura cy.
    frame=True añade marco blanco (solo para rect photos). transparent_ok=True conserva
    transparencia (siluetas PNG). tint_rgb colorea el alpha de la silueta (ej. cyan para
    legibilidad sobre fondo navy — mapsicon devuelve siluetas negras)."""
    try:
        if transparent_ok:
            fl = Image.open(src).convert("RGBA")
        else:
            fl = Image.open(src).convert("RGB")
    except Exception:
        return
    # Escalar manteniendo aspect
    r = min(max_w / fl.width, max_h / fl.height)
    fw, fh = int(fl.width * r), int(fl.height * r)
    fl = fl.resize((fw, fh), Image.LANCZOS)
    # Tint: reemplaza el color pintado por tint_rgb manteniendo alpha
    if transparent_ok and tint_rgb is not None:
        base = Image.new("RGBA", fl.size, tint_rgb + (255,))
        fl = Image.composite(base, Image.new("RGBA", fl.size, (0, 0, 0, 0)), fl.split()[3])
    x = (W - fw) // 2
    y = cy - fh // 2
    d = ImageDraw.Draw(img)
    if frame and not transparent_ok:
        d.rectangle([x - 8, y - 8, x + fw + 8, y + fh + 8], fill=WHITE)
    if transparent_ok:
        img.paste(fl, (x, y), fl)
    else:
        img.paste(fl, (x, y))


def _paste_flag(img: Image.Image, flag: Path, cy: int) -> None:
    _paste_image(img, flag, cy, max_w=780, max_h=560, frame=True)


PROMPT_BY_MODE = {
    "flag":       "What country is this?",
    "capital":    "What country's capital is this?",
    "monument":   "What country is this?",
    "silhouette": "What country is this?",
    "fact":       "What country?",
}


def _frame_intro(path: Path, copy: dict, n_rounds: int = 10) -> None:
    img = _base()
    d = ImageDraw.Draw(img)
    _text_center(d, W // 2, 470, copy["l1"], _fit_font(d, copy["l1"], 120, W - 80), WHITE)
    _text_center(d, W // 2, 610, copy["l2"], _fit_font(d, copy["l2"], 170, W - 80), ACCENT)
    _text_center(d, W // 2, 850, copy["sub"], _font(52), MUTED, max_w=1000)
    _text_center(d, W // 2, 1120, f"{n_rounds} questions", _font(104), GOLD)
    _text_center(d, W // 2, 1280, "easy → hard", _font(72), WHITE)
    _text_center(d, W // 2, 1550, "Comment your score below", _font(60), MUTED, max_w=900)
    img.save(path)


def _draw_countdown(d: ImageDraw.ImageDraw, number: int, cy: int) -> None:
    cx, r = W // 2, 110
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=GOLD, width=10)
    num = str(number)
    f = _font(140)
    wnum = d.textlength(num, font=f)
    asc, desc = f.getmetrics()
    d.text((cx - wnum / 2, cy - (asc + desc) / 2), num, font=f, fill=WHITE)


def _frame_round(path: Path, asset: Path | None, mode: str, text_payload: str,
                 rnd: int, total: int, number: int, country_tier: int) -> None:
    """Un frame de pregunta (durante cuenta atrás 3/2/1)."""
    img = _base()
    d = ImageDraw.Draw(img)
    tier_label = {1: "EASY", 2: "MEDIUM", 3: "HARD"}.get(country_tier, "")
    tier_color = {1: ACCENT, 2: GOLD, 3: (240, 110, 110)}.get(country_tier, ACCENT)
    _text_center(d, W // 2, 180, f"Q {rnd}/{total}", _font(64), MUTED)
    _text_center(d, W // 2, 260, tier_label, _font(44), tier_color)
    _text_center(d, W // 2, 340, PROMPT_BY_MODE.get(mode, "What country?"), _font(60), WHITE, max_w=980)
    if mode == "flag" and asset:
        _paste_flag(img, asset, 900)
    elif mode == "monument" and asset:
        _paste_image(img, asset, 900, max_w=820, max_h=820, frame=True)
    elif mode == "silhouette" and asset:
        _paste_image(img, asset, 900, max_w=820, max_h=820, frame=False, transparent_ok=True,
                     tint_rgb=ACCENT)  # cyan sobre fondo navy
    elif mode == "capital":
        # Texto grande centrado con la capital
        _text_center(d, W // 2, 760, "Capital:", _font(60), MUTED)
        _text_center(d, W // 2, 900, text_payload, _font(140), ACCENT, max_w=1000)
    elif mode == "fact":
        _text_center(d, W // 2, 720, text_payload, _font(60), WHITE, max_w=960)
    _draw_countdown(d, number, 1480)
    _text_center(d, W // 2, 1660, "Name it!", _font(56), MUTED)
    img.save(path)


def _frame_reveal(path: Path, asset: Path | None, mode: str, text_payload: str,
                  rnd: int, total: int, name: str, capital: str, flag_asset: Path | None,
                  country_tier: int) -> None:
    """Frame de respuesta (muestra país + capital + bandera siempre)."""
    img = _base()
    d = ImageDraw.Draw(img)
    tier_label = {1: "EASY", 2: "MEDIUM", 3: "HARD"}.get(country_tier, "")
    tier_color = {1: ACCENT, 2: GOLD, 3: (240, 110, 110)}.get(country_tier, ACCENT)
    _text_center(d, W // 2, 180, f"Q {rnd}/{total}", _font(60), MUTED)
    _text_center(d, W // 2, 260, tier_label, _font(44), tier_color)
    # En reveal mostramos la bandera (aun si la pregunta no era de bandera)
    if flag_asset:
        _paste_flag(img, flag_asset, 700)
    _text_center(d, W // 2, 1120, name, _font(104), ACCENT, max_w=980)
    _text_center(d, W // 2, 1300, f"Capital: {capital}", _font(60), WHITE, max_w=980)
    if mode == "fact" and text_payload:
        _text_center(d, W // 2, 1490, text_payload, _font(42), MUTED, max_w=980)
    elif mode == "monument" and text_payload:
        # Sin emoji 🏛: la fuente no lo tiene y saldría como cuadro roto (tofu).
        _text_center(d, W // 2, 1490, text_payload, _font(44), MUTED, max_w=980)
    img.save(path)


def _frame_outro(path: Path, copy: dict) -> None:
    img = _base()
    d = ImageDraw.Draw(img)
    _text_center(d, W // 2, 560, copy["l1"], _fit_font(d, copy["l1"], 120, W - 80), WHITE)
    _text_center(d, W // 2, 700, copy["l2"], _fit_font(d, copy["l2"], 120, W - 80), ACCENT)
    _text_center(d, W // 2, 1050, copy["cta"], _font(80), GOLD, max_w=940)
    _text_center(d, W // 2, 1420, copy["follow"], _font(62), MUTED, max_w=940)
    img.save(path)


def _download_url(url: str, dest: Path, attempts: int = 4) -> Path | None:
    """Descarga con reintento + requests (mejor manejo IncompleteRead que urllib
    stock). Antes se perdían preguntas silenciosamente contra CDN flakey."""
    import time as _time
    if dest.exists() and dest.stat().st_size > 1000:
        return dest
    dest.parent.mkdir(parents=True, exist_ok=True)
    last_err = None
    # Wikimedia bloquea Mozilla/5.0 genérico. Usar UA con nombre de app + URL
    # (Wikimedia Foundation User-Agent policy requires identifiable UA).
    headers = {"User-Agent": "GeoQuizBot/1.0 (https://github.com/yassinebhk; contact: 72581389+yassinebhk@users.noreply.github.com)"}
    for i in range(attempts):
        try:
            try:
                import requests
                r = requests.get(url, headers=headers, timeout=30, stream=False)
                r.raise_for_status()
                data = r.content
            except ImportError:
                req = urllib.request.Request(url, headers=headers)
                data = urllib.request.urlopen(req, timeout=30).read()
            if len(data) < 500:
                last_err = f"too small ({len(data)}B)"
                _time.sleep(0.6 * (i + 1))
                continue
            dest.write_bytes(data)
            return dest
        except Exception as e:
            last_err = f"{type(e).__name__}: {str(e)[:80]}"
            _time.sleep(0.8 * (i + 1))
    print(f"  geoquiz: download {url[-80:]} fail tras {attempts} intentos ({last_err})")
    return None


def _download_flag(iso2: str, dest: Path) -> Path | None:
    from .data import flag_url
    return _download_url(flag_url(iso2), dest)


def generate_geoquiz(out_dir: Path, questions: list[tuple], n_rounds: int = 10) -> dict | None:
    """questions: lista de ((iso2, name, capital, continent, tier), mode). mode ∈
    flag/capital/monument/silhouette/fact.
    Para cada pregunta descarga el asset necesario (bandera siempre; monumento o
    silueta si procede). Si el asset falla, descarta esa pregunta y sigue."""
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    slug = f"geoquiz_{ts}"
    work = out_dir / slug
    work.mkdir(parents=True, exist_ok=True)
    from . import data as _data

    chosen: list[dict] = []  # [{iso2, name, capital, tier, mode, asset: Path|None, flag: Path|None, text: str}]
    for item in questions:
        country, mode = item
        iso2, name, capital, continent, tier = country
        # Siempre descargamos la bandera (se usa en el reveal)
        flag = _download_flag(iso2, FLAG_CACHE / f"{iso2}.png")
        asset = None
        text = ""
        if mode == "flag":
            asset = flag
        elif mode == "monument":
            mon = _data.monument_url(iso2)
            if mon:
                mon_name, mon_url = mon
                text = mon_name
                safe = "".join(ch if ch.isalnum() else "_" for ch in mon_name)[:40]
                asset = _download_url(mon_url, FLAG_CACHE.parent / "monuments" / f"{iso2}_{safe}.jpg")
        elif mode == "silhouette":
            asset = _download_url(_data.silhouette_url(iso2),
                                  FLAG_CACHE.parent / "silhouettes" / f"{iso2}.png")
        elif mode == "capital":
            text = capital
        elif mode == "fact":
            text = _data.fact_text(iso2) or ""
        # Validaciones por modo (asset obligatorio para los que usan imagen)
        if mode in ("flag", "monument", "silhouette") and not asset:
            print(f"  geoquiz: {iso2}/{mode} descartado (asset no disponible)")
            continue
        if mode in ("capital", "fact") and not text:
            print(f"  geoquiz: {iso2}/{mode} descartado (sin texto)")
            continue
        chosen.append({
            "iso2": iso2, "name": name, "capital": capital, "tier": tier,
            "mode": mode, "asset": asset, "flag": flag, "text": text,
        })
        if len(chosen) >= n_rounds:
            break
    if len(chosen) < 5:
        print(f"  geoquiz: solo {len(chosen)} preguntas OK (<5) — abort")
        return None
    n_rounds = len(chosen)

    # Piel visual del episodio: rota paleta + copy por día (anti contenido repetitivo).
    # Se aplica ANTES de construir ningún frame → intro/round/reveal/outro usan esta paleta.
    theme_name = _apply_theme(_rotation_index())
    _ordinal = datetime.now(timezone.utc).toordinal()
    intro_copy = INTRO_COPY[_ordinal % len(INTRO_COPY)]
    outro_copy = OUTRO_COPY[_ordinal % len(OUTRO_COPY)]
    print(f"  geoquiz: piel visual = tema '{theme_name}' · intro '{intro_copy['l1']} {intro_copy['l2']}'")

    # construir frames + lista concat (duraciones en segundos)
    frames: list[tuple[Path, float]] = []
    intro = work / "f_intro.png"; _frame_intro(intro, intro_copy, n_rounds); frames.append((intro, 2.6))
    for i, q in enumerate(chosen, 1):
        for num, dur in ((3, 1.0), (2, 1.0), (1, 1.0)):
            fr = work / f"f_r{i}_{num}.png"
            _frame_round(fr, q["asset"], q["mode"], q["text"], i, n_rounds, num, q["tier"])
            frames.append((fr, dur))
        rv = work / f"f_r{i}_rev.png"
        _frame_reveal(rv, q["asset"], q["mode"], q["text"], i, n_rounds,
                      q["name"], q["capital"], q["flag"], q["tier"])
        frames.append((rv, 1.9))
    outro = work / "f_outro.png"; _frame_outro(outro, outro_copy); frames.append((outro, 2.8))

    # Secuencia numerada (image2) = método robusto entre versiones de ffmpeg:
    # cada frame se repite dur*fps veces y se codifica a 30 fps constante.
    import shutil
    fps = 30
    seq = work / "seq"
    seq.mkdir(exist_ok=True)
    idx = 0
    for p, dur in frames:
        for _ in range(max(1, round(dur * fps))):
            shutil.copyfile(p, seq / f"{idx:05d}.png")
            idx += 1

    raw = work / "raw.mp4"
    # -preset ultrafast: el contenido son frames estáticos (banderas + texto), así que
    # la calidad es idéntica a 'medium' pero encodea 5-10× más rápido. Clave para que
    # corra en la VM e2-micro del puente (CPU burstable débil, que con el preset por
    # defecto superaba el timeout de ffmpeg). También acelera CI/Oracle.
    cmd = ["ffmpeg", "-y", "-framerate", str(fps), "-i", str(seq / "%05d.png"),
           "-c:v", "libx264", "-preset", "ultrafast", "-pix_fmt", "yuv420p", "-r", str(fps),
           "-movflags", "+faststart", str(raw)]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=900)
    if r.returncode != 0 or not raw.exists():
        print(f"  geoquiz: ffmpeg encode fail: {r.stderr[-400:]}")
        return None

    # SIN música (user 06/10): el vídeo sale MUDO para que en TikTok se le añada el
    # sonido que esté en TENDENCIA (truco del research: sonido trending = alcance gratis).
    # Añadir música propia solo competiría con el audio trending de TikTok.
    final = raw

    names = ", ".join(q["name"] for q in chosen)
    modes = sorted(set(q["mode"] for q in chosen))
    title = TITLES[_ordinal % len(TITLES)].format(n=n_rounds)
    desc = (
        f"Can you name all {n_rounds} countries? Comment your score below!\n\n"
        f"Modes used: {', '.join(modes)}.\n"
        f"Countries: {names}.\n\n"
        "New geography quiz every day — follow to test yourself.\n\n"
        "Flags: public domain (flagcdn.com). Silhouettes: djaiss/mapsicon (CC0). "
        "Monuments: Wikimedia Commons.\n\n"
        "#geography #quiz #flags #capitals #guessthecountry #trivia #geoquiz #shorts #learnontiktok"
    )
    return {
        "slug": slug, "video_path": str(final), "theme": theme_name,
        "title": title[:100], "description": desc[:4900],
        "tags": ["geography", "quiz", "flags", "capitals", "monuments", "guess the country",
                 "trivia", "geoquiz", "shorts"],
        "countries": [q["iso2"] for q in chosen],
        "pairs": [f"{q['iso2']}:{q['mode']}" for q in chosen],
        "round_key": "-".join(f"{q['iso2']}:{q['mode']}" for q in chosen),
    }
