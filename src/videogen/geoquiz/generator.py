"""Generador de vídeo GeoQuiz (EN) — "guess the country by its flag".

Sin voz (música + texto en pantalla → esquiva la limitación del TTS). Frames con
PIL (1080x1920) → concat con ffmpeg → música (helper de ranking). Banderas desde
flagcdn.com (dominio público). 5 rondas: bandera + cuenta atrás 3-2-1 → reveal
país + capital. Cierre con CTA "comment your score". Ver [[tanda-canales-02-10]].
"""
from __future__ import annotations

import subprocess
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from ..config import ROOT

W, H = 1080, 1920
BG = (14, 23, 38)          # navy oscuro
ACCENT = (57, 224, 208)    # turquesa
GOLD = (245, 197, 66)
WHITE = (240, 244, 248)
MUTED = (150, 165, 185)
FONT_PATH = ROOT / "assets" / "fonts" / "Montserrat.ttf"
FLAG_CACHE = ROOT / "output" / "geoquiz_assets" / "flags"


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


def _frame_intro(path: Path) -> None:
    img = _base()
    d = ImageDraw.Draw(img)
    _text_center(d, W // 2, 470, "GUESS THE", _font(120), WHITE)
    _text_center(d, W // 2, 610, "COUNTRY", _font(170), ACCENT)
    _text_center(d, W // 2, 850, "flags · capitals · maps · monuments", _font(52), MUTED, max_w=1000)
    _text_center(d, W // 2, 1120, "10 questions", _font(104), GOLD)
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
        _text_center(d, W // 2, 1490, f"🏛 {text_payload}", _font(44), MUTED, max_w=980)
    img.save(path)


def _frame_outro(path: Path) -> None:
    img = _base()
    d = ImageDraw.Draw(img)
    _text_center(d, W // 2, 560, "How many", _font(120), WHITE)
    _text_center(d, W // 2, 700, "did you get?", _font(120), ACCENT)
    _text_center(d, W // 2, 1050, "Comment your score", _font(80), GOLD, max_w=940)
    _text_center(d, W // 2, 1420, "Follow for more geo quizzes", _font(62), MUTED, max_w=940)
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

    # construir frames + lista concat (duraciones en segundos)
    frames: list[tuple[Path, float]] = []
    intro = work / "f_intro.png"; _frame_intro(intro); frames.append((intro, 2.6))
    for i, q in enumerate(chosen, 1):
        for num, dur in ((3, 1.0), (2, 1.0), (1, 1.0)):
            fr = work / f"f_r{i}_{num}.png"
            _frame_round(fr, q["asset"], q["mode"], q["text"], i, n_rounds, num, q["tier"])
            frames.append((fr, dur))
        rv = work / f"f_r{i}_rev.png"
        _frame_reveal(rv, q["asset"], q["mode"], q["text"], i, n_rounds,
                      q["name"], q["capital"], q["flag"], q["tier"])
        frames.append((rv, 1.9))
    outro = work / "f_outro.png"; _frame_outro(outro); frames.append((outro, 2.8))

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
    title = f"Guess the country 🌍 | {n_rounds} questions, easy → hard"
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
        "slug": slug, "video_path": str(final),
        "title": title[:100], "description": desc[:4900],
        "tags": ["geography", "quiz", "flags", "capitals", "monuments", "guess the country",
                 "trivia", "geoquiz", "shorts"],
        "countries": [q["iso2"] for q in chosen],
        "pairs": [f"{q['iso2']}:{q['mode']}" for q in chosen],
        "round_key": "-".join(f"{q['iso2']}:{q['mode']}" for q in chosen),
    }
