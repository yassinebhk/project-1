"""Descarga de B-roll desde Pexels API."""
from __future__ import annotations

import hashlib
import json
import os
import random
import time
from pathlib import Path

import requests

from .config import pexels_key, pexels_keys
from .models import VideoClip


PEXELS_SEARCH = "https://api.pexels.com/videos/search"

# Códigos transitorios: 429 = rate-limit (Pexels free = 200 req/h POR CLAVE; una
# tanda de ~15 canales en ráfaga los agota), 5xx = fallo temporal del servidor.
_RETRYABLE_STATUS = {429, 500, 502, 503, 504}


def _pexels_get(
    url: str, *, stream: bool = False, auth_keys: list[str] | None = None, **kwargs
) -> requests.Response:
    """GET con reintentos ante 429/5xx + ROTACIÓN de claves Pexels.

    Antes, un único 429 tumbaba la descarga de clips de un canal entero (y con
    ella el vídeo: "No hay clips para componer").

    - `auth_keys`: si se pasan varias claves, ante un 429 rota a la siguiente
      SIN esperar (cada clave tiene su propio cupo 200 req/h). Solo cuando se
      agotan todas en una vuelta aplica backoff.
    - Respeta `Retry-After` si viene; si no, backoff exponencial con jitter.

    Knobs: PEXELS_MAX_RETRIES (default 4), PEXELS_BACKOFF_BASE (default 2.0s).
    """
    attempts = max(1, int(os.environ.get("PEXELS_MAX_RETRIES", "4")))
    base = float(os.environ.get("PEXELS_BACKOFF_BASE", "2.0"))
    keys = [k for k in (auth_keys or []) if k]
    headers0 = dict(kwargs.pop("headers", None) or {})
    total = max(attempts, len(keys) or 1)  # al menos un intento por clave
    for i in range(total):
        headers = dict(headers0)
        if keys:
            headers["Authorization"] = keys[i % len(keys)]
        resp = requests.get(url, stream=stream, headers=headers, **kwargs)
        if resp.status_code not in _RETRYABLE_STATUS:
            resp.raise_for_status()
            return resp
        status = resp.status_code
        retry_after = (resp.headers.get("Retry-After") or "").strip()
        if stream:
            resp.close()
        if i == total - 1:
            resp.raise_for_status()  # agotados los intentos → propaga el error
        # Si queda otra clave sin probar en esta vuelta, rota SIN dormir.
        if keys and (i + 1) % len(keys) != 0:
            print(f"  pexels {status} → rota a clave #{(i + 1) % len(keys) + 1}/{len(keys)}")
            continue
        delay = (
            min(float(retry_after), 60.0)
            if retry_after.isdigit()
            else base * (2 ** (i // max(1, len(keys)))) + random.uniform(0.0, 1.0)
        )
        print(f"  pexels {status} → reintento en {delay:.1f}s")
        time.sleep(delay)
    raise RuntimeError("pexels: reintentos agotados")  # inalcanzable


def pexels_api_get(
    url: str, *, stream: bool = False, auth_keys: list[str] | None = None, **kwargs
) -> requests.Response:
    """Variante pública para callers que YA manejan `status != 200` con su propio
    fallback (fotos: aimages, thumbnails, ambient).

    Reintenta/rota igual que `_pexels_get`, pero DEVUELVE la respuesta del último
    intento (aunque sea 429) en vez de lanzar, para no romper su lógica. Las
    claves por defecto son todas las disponibles (rotación). Un error de
    conexión (sin respuesta) sí se propaga → lo captura el try/except del caller.
    """
    if auth_keys is None:
        auth_keys = pexels_keys() or [pexels_key()]
    try:
        return _pexels_get(url, stream=stream, auth_keys=auth_keys, **kwargs)
    except requests.HTTPError as e:
        if e.response is not None:
            return e.response
        raise


def _cache_key(keyword: str) -> str:
    return hashlib.sha1(keyword.lower().encode("utf-8")).hexdigest()[:12]


_NEGATIVE_TOKENS = {
    # Off-topic for nature/science docs
    "toy", "toys", "wooden", "cardboard", "drawing", "drawn",
    "cooked", "cooking", "grilled", "dish", "food", "recipe", "meal",
    "kitchen", "chef", "restaurant", "plate", "fried", "sushi",
    "cartoon", "puppet", "stuffed", "plush",
    "halloween", "costume", "fake", "mascot",
    # Modern lifestyle / outdoor people que rompen temas históricos o serios
    "hiker", "hiking", "hike", "climber", "climbing", "trekking", "trek",
    "backpacker", "backpack", "tourist", "tourism", "traveler", "traveller",
    "vlog", "vlogger", "selfie", "jogging", "jogger", "running", "runner",
    "trail", "camping", "camper", "yoga", "fitness", "workout", "gym",
    "influencer", "lifestyle", "fashion", "model", "smiling", "wedding",
    "businessman", "businesswoman", "office",
}


def _score_video(vid: dict, kw_tokens: set[str], orientation: str) -> float:
    """Puntúa un resultado de Pexels por relevancia + calidad técnica.

    Factores:
    - Match de tokens del keyword en URL/uploader (+3 cada uno)
    - **PENALIZA tokens negativos** que indican contenido off-topic (-5 cada uno)
    - Resolución máxima disponible (1080p +2, 1440p +0.5, 2160p +0.5)
    - Duración suficiente (+1 si ≥5s, +0.5 si ≥8s)
    - Orientación correcta (+0.5)
    """
    url = (vid.get("url") or "").lower()
    user_name = (vid.get("user", {}).get("name") or "").lower()
    haystack = f"{url} {user_name}"
    # Tokens del URL slug (separados por guiones)
    url_tokens = set(url.replace("/", "-").split("-"))

    score = 0.0
    for tok in kw_tokens:
        if len(tok) < 3:
            continue
        if tok in haystack:
            score += 3.0

    # Penalización fuerte por tokens negativos (cooked, toy, cartoon, etc.)
    for neg in _NEGATIVE_TOKENS:
        if neg in url_tokens:
            score -= 5.0

    duration = vid.get("duration", 0)
    if duration >= 5:
        score += 1.0
    if duration >= 8:
        score += 0.5

    files = vid.get("video_files", [])
    # Resolución máxima disponible (la dimensión larga)
    max_long = 0
    has_correct_orientation = False
    for f in files:
        w, h = f.get("width", 0), f.get("height", 0)
        if not w or not h:
            continue
        long_side = max(w, h)
        max_long = max(max_long, long_side)
        is_portrait = h > w
        if (orientation == "portrait" and is_portrait) or (
            orientation == "landscape" and not is_portrait
        ):
            has_correct_orientation = True

    if max_long >= 1920:  # full HD
        score += 2.0
    if max_long >= 2560:
        score += 0.5
    if max_long >= 3840:
        score += 0.5
    if has_correct_orientation:
        score += 0.5

    return score


PIXABAY_VIDEO_SEARCH = "https://pixabay.com/api/videos/"


def _search_clip_pexels(
    keyword: str,
    dest_dir: Path,
    cache_key: str,
    min_duration: float,
    orientation: str,
) -> VideoClip | None:
    """Fuente PRIMARIA: busca+descarga un clip en Pexels.

    Pide 15 candidatos, los puntúa por relevancia (URL slug match, duración,
    orientación) y descarga el mejor. Puede LANZAR si Pexels agota los
    reintentos (429 persistente) — lo captura search_clip para caer a Pixabay.
    """
    resp = _pexels_get(
        PEXELS_SEARCH,
        auth_keys=pexels_keys() or [pexels_key()],  # rotación si hay varias claves
        params={
            "query": keyword,
            "per_page": 15,
            "orientation": orientation,
            "size": "large",  # ≥1080p para no pixelar al escalar
        },
        timeout=30,
    )
    videos = resp.json().get("videos", [])
    if not videos:
        return None

    kw_tokens = set(keyword.lower().split())
    # Filtra por duración mínima y puntúa el resto
    scored = [
        (_score_video(v, kw_tokens, orientation), v)
        for v in videos
        if v.get("duration", 0) >= min_duration
    ]
    scored.sort(key=lambda x: x[0], reverse=True)

    for _, vid in scored:
        files = vid.get("video_files", [])
        # Long-side closest to 1920 (full HD). Para portrait queremos 1080x1920;
        # para landscape, 1920x1080. En ambos casos el lado largo = 1920.
        mp4s = [
            f
            for f in files
            if f.get("file_type") == "video/mp4"
            and max(f.get("width", 0), f.get("height", 0)) >= 1280
        ]
        if not mp4s:
            continue
        mp4s.sort(
            key=lambda f: abs(max(f.get("width", 0), f.get("height", 0)) - 1920)
        )
        chosen = mp4s[0]
        url = chosen["link"]
        out_path = dest_dir / f"{cache_key}.mp4"
        r = _pexels_get(url, stream=True, timeout=120)
        try:
            with open(out_path, "wb") as fp:
                for chunk in r.iter_content(chunk_size=1 << 20):
                    fp.write(chunk)
        finally:
            r.close()

        clip = VideoClip(
            path=str(out_path),
            duration_seconds=float(vid.get("duration", 0)),
            width=int(chosen.get("width", 0)),
            height=int(chosen.get("height", 0)),
            keyword=keyword,
        )
        (dest_dir / f"{cache_key}.json").write_text(
            clip.model_dump_json(indent=2), encoding="utf-8"
        )
        return clip
    return None


def _search_clip_pixabay(
    keyword: str,
    dest_dir: Path,
    cache_key: str,
    min_duration: float,
    orientation: str,
) -> VideoClip | None:
    """Fuente de RESPALDO cuando Pexels da 429 (cupo horario agotado en ráfaga)
    o 0 resultados.

    Pixabay tiene API de vídeo GRATIS con cupo INDEPENDIENTE de Pexels (y más
    holgado, ~100 req/min). La clave PIXABAY_API_KEY ya existe (se usa para fotos
    en aimages). Esto es la cura real mientras Pexels tiene PAUSADA la emisión de
    claves nuevas (27/10) → no se puede añadir PEXELS_API_KEY_2. Desactivable con
    PIXABAY_VIDEO_FALLBACK=0.
    """
    key = os.environ.get("PIXABAY_API_KEY", "").strip()
    if not key:
        return None
    r = requests.get(
        PIXABAY_VIDEO_SEARCH,
        params={"key": key, "q": keyword, "per_page": 20, "safesearch": "true"},
        timeout=30,
    )
    if r.status_code != 200:
        return None
    # Pixabay a veces manda content-type text/html con el JSON dentro → r.json()
    # parsea el body igual (ignora el content-type).
    hits = (r.json() or {}).get("hits", [])
    if not hits:
        return None

    kw_tokens = {t for t in keyword.lower().split() if t}
    want_portrait = orientation == "portrait"

    def _hit_score(hit: dict) -> float:
        tags = (hit.get("tags") or "").lower()
        return float(sum(1 for t in kw_tokens if t in tags))

    usable = [h for h in hits if float(h.get("duration", 0) or 0) >= min_duration] or hits
    usable.sort(key=_hit_score, reverse=True)

    for hit in usable:
        sizes = hit.get("videos") or {}
        cands = [
            v for v in sizes.values()
            if v.get("url") and max(v.get("width", 0), v.get("height", 0)) >= 1280
        ] or [v for v in sizes.values() if v.get("url")]
        if not cands:
            continue
        # Prioriza orientación correcta si existe; luego el lado largo más cercano a 1920.
        cands.sort(key=lambda v: (
            0 if ((v.get("height", 0) > v.get("width", 0)) == want_portrait) else 1,
            abs(max(v.get("width", 0), v.get("height", 0)) - 1920),
        ))
        chosen = cands[0]
        out_path = dest_dir / f"{cache_key}.mp4"
        try:
            dl = requests.get(chosen["url"], stream=True, timeout=120)
            dl.raise_for_status()
            try:
                with open(out_path, "wb") as fp:
                    for chunk in dl.iter_content(chunk_size=1 << 20):
                        fp.write(chunk)
            finally:
                dl.close()
        except Exception as e:  # noqa: BLE001 — prueba el siguiente hit
            print(f"  pixabay descarga falló: {type(e).__name__}")
            continue

        clip = VideoClip(
            path=str(out_path),
            duration_seconds=float(hit.get("duration", 0) or 0),
            width=int(chosen.get("width", 0)),
            height=int(chosen.get("height", 0)),
            keyword=keyword,
        )
        (dest_dir / f"{cache_key}.json").write_text(
            clip.model_dump_json(indent=2), encoding="utf-8"
        )
        print(f"  ✓ pixabay (respaldo) sirvió clip para '{keyword}'")
        return clip
    return None


def search_clip(
    keyword: str,
    dest_dir: Path,
    min_duration: float = 3.0,
    orientation: str = "portrait",
) -> VideoClip | None:
    """Busca un clip para `keyword`.

    Fuente primaria = Pexels. Si Pexels da 429 (cupo de la única clave agotado en
    ráfaga; Pexels tiene PAUSADA la emisión de claves nuevas) o 0 resultados, cae
    a **Pixabay vídeo** (cupo independiente, clave ya existente). Resultado
    cacheado en dest_dir. Devuelve None solo si NINGUNA fuente sirve clip.
    """
    dest_dir.mkdir(parents=True, exist_ok=True)
    cache_key = _cache_key(keyword)
    cached_meta = dest_dir / f"{cache_key}.json"
    if cached_meta.exists():
        clip = VideoClip.model_validate_json(cached_meta.read_text(encoding="utf-8"))
        mp4 = dest_dir / f"{cache_key}.mp4"
        if mp4.exists():
            clip.path = str(mp4)  # corrige ruta si la carpeta se movió (pending→uploaded)
            return clip

    # 1) Pexels (primaria)
    try:
        clip = _search_clip_pexels(keyword, dest_dir, cache_key, min_duration, orientation)
        if clip:
            return clip
    except Exception as e:  # noqa: BLE001 — 429 agotado u otro fallo → respaldo
        print(f"  pexels agotado para '{keyword}': {type(e).__name__} — pruebo Pixabay")

    # 2) Pixabay vídeo (respaldo; cupo independiente, clave gratis ya existe)
    if os.environ.get("PIXABAY_VIDEO_FALLBACK", "1").lower() not in ("0", "false", "no"):
        try:
            return _search_clip_pixabay(keyword, dest_dir, cache_key, min_duration, orientation)
        except Exception as e:  # noqa: BLE001
            print(f"  pixabay vídeo falló para '{keyword}': {type(e).__name__}")
    return None


def fetch_broll(
    keywords: list[str], dest_dir: Path, orientation: str = "portrait"
) -> list[VideoClip]:
    """Descarga clips para cada keyword. Mantiene orden."""
    clips: list[VideoClip] = []
    for kw in keywords:
        try:
            clip = search_clip(kw, dest_dir, orientation=orientation)
        except Exception as e:
            print(f"  pexels failed for '{kw}': {e}")
            clip = None
        if clip:
            clips.append(clip)
    return clips


_STOPWORDS = {
    "why", "how", "what", "when", "where", "who", "the", "a", "an",
    "of", "for", "to", "in", "on", "at", "is", "are", "do", "does",
    "about", "with", "from", "that", "this", "your", "you", "its",
    "their", "and", "or", "but", "so", "than", "then", "into", "as",
    "be", "will", "can", "did", "has", "have",
}

# Genéricos que SÍ forman compound natural y merecen prepend (world cup, ...).
_COMPOUND_HEADS = {"world"}


# Palabras demasiado genéricas para usarse solas como anchor visual:
# Pexels devuelve contenido abstracto/irrelevante. Si el primer token es uno
# de estos, combinamos con el siguiente para concretar (ej. "world" → "world cup").
_GENERIC_FIRST = {
    "world", "thing", "things", "people", "life", "history", "fact",
    "facts", "data", "story", "stories", "best", "top", "most", "new",
    "real", "secret", "secrets", "amazing", "biggest", "greatest",
}


def topic_subject_from_slug(slug: str) -> str:
    """Extrae el sujeto visual del slug para anclar el primer frame.

    Devuelve el primer token significativo; si es demasiado genérico
    (ej. "world", "facts"), lo combina con el siguiente para concretar.

    Ej: "octopus-three-hearts-mystery" → "octopus"
    Ej: "world-cup-2026-curious-facts" → "world cup"
    Ej: "why-do-cats-purr" → "cats"
    """
    tokens = [
        p.strip().lower()
        for p in slug.split("-")
        if p.strip() and p.strip().lower() not in _STOPWORDS and not p.isdigit()
    ]
    if not tokens:
        return slug.replace("-", " ")

    # Primer token no-genérico = sujeto real
    non_generic = [t for t in tokens if t not in _GENERIC_FIRST]
    if not non_generic:
        return tokens[0]
    core = non_generic[0]
    core_idx = tokens.index(core)
    # Solo prepend si el token previo forma compound natural (ej. "world cup").
    if core_idx > 0 and tokens[core_idx - 1] in _COMPOUND_HEADS:
        return f"{tokens[core_idx - 1]} {core}"
    return core


def fetch_clips_for_segments(
    segments,
    dest_dir: Path,
    orientation: str = "portrait",
    topic_anchor: str | None = None,
) -> None:
    """Para cada TimedSegment, descarga clips matching sus visual_keywords.
    Muta los segmentos in-place añadiendo .clips. Garantiza ≥1 clip por segmento.

    Si se pasa `topic_anchor`, se PREPONE como primer keyword del hook
    (índice 0), garantizando que la primera imagen del video sea on-topic.
    """
    last_good: VideoClip | None = None
    for seg in segments:
        # Confiamos en las keywords curadas por Gemini (la primera del teaser
        # es la imagen icónica del topic). El scoring + penalización filtran ruido.
        for kw in seg.visual_keywords:
            try:
                clip = search_clip(kw, dest_dir, orientation=orientation)
            except Exception as e:
                print(f"  pexels failed for '{kw}': {e}")
                continue
            if clip:
                seg.clips.append(clip)
                last_good = clip
        if not seg.clips:
            # Fallback: el sujeto del topic, o las primeras palabras del segmento
            fallback = topic_anchor or " ".join(seg.text.split()[:3])
            print(f"  ⚠ seg {seg.label}: sin clips, fallback a '{fallback}'")
            try:
                clip = search_clip(fallback, dest_dir, orientation=orientation)
                if clip:
                    seg.clips.append(clip)
                    last_good = clip
            except Exception:
                pass
        # Red de seguridad: si AÚN no hay clips (p.ej. Pexels 429 en ráfaga tras
        # agotar reintentos), reutiliza el último clip bueno. Un vídeo algo
        # repetitivo es infinitamente mejor que "No hay clips para componer".
        if not seg.clips and last_good is not None:
            print(f"  ↻ seg {seg.label}: reutilizo clip previo (evita abortar compose)")
            seg.clips.append(last_good)
