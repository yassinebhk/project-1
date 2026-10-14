"""Pipeline GeoQuiz (EN) — "guess the country by its flag" (sin voz).

Pre-cableado: sin YT_GEOQUIZ_* hace NO-OP (no genera). Dedup PROPIO por SET de países
(round_key) + cooldown por país → NO repite la misma ronda. Desactiva el guardarraíl
de dedup POR TÍTULO en su subida (el título es fijo por diseño = marca de serie; el
contenido varía por banderas). Ver [[tanda-canales-02-10]], [[dedup-semantico-titulo]].
"""
from __future__ import annotations

import json
import os
import random
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any

from ..config import ROOT
from . import generator, data

LEDGER = ROOT / "output" / "geoquiz_ledger.json"
GEOQUIZ_ROOT = ROOT / "output" / "geoquiz_uploaded"
YT_PREFIX = "YT_GEOQUIZ"
DISPLAY_NAME = "GeoQuiz"
COUNTRY_COOLDOWN_DAYS = 45
N_ROUNDS = 10  # expansión 14/10: 10 preguntas por vídeo (3 fácil + 4 medio + 3 difícil)
# Modos de pregunta disponibles. "flag" clásico, resto nuevos (14/10):
#   capital: muestra nombre de capital → ¿qué país?
#   monument: muestra foto monumento → ¿qué país? (solo países en data.MONUMENTS)
#   silhouette: muestra silueta mapa país → ¿qué país?
#   fact: muestra dato geográfico distintivo → ¿qué país? (solo países en data.GEO_FACTS)
QUESTION_MODES = ("flag", "capital", "monument", "silhouette", "fact")


def _load_ledger() -> dict:
    if not LEDGER.exists():
        return {"countries": {}, "rounds": []}
    try:
        d = json.loads(LEDGER.read_text(encoding="utf-8"))
        d.setdefault("countries", {})
        d.setdefault("rounds", [])
        return d
    except Exception:
        return {"countries": {}, "rounds": []}


def _save_ledger(d: dict) -> None:
    LEDGER.parent.mkdir(parents=True, exist_ok=True)
    LEDGER.write_text(json.dumps(d, indent=2, ensure_ascii=False), encoding="utf-8")


def _pair_recent(led: dict, iso2: str, mode: str) -> bool:
    """Dedup por par (país, modo) — permite el mismo país con otro modo pronto,
    pero evita misma combinación hasta COUNTRY_COOLDOWN_DAYS."""
    key = f"{iso2}:{mode}"
    ts = (led.get("pairs") or {}).get(key)
    if not ts:
        return False
    try:
        return (datetime.now(timezone.utc) - datetime.fromisoformat(ts)) < timedelta(days=COUNTRY_COOLDOWN_DAYS)
    except Exception:
        return False


def _pick_from_tier(led: dict, tier: int, modes: list[str], n: int) -> list[tuple]:
    """Toma n countries del tier dado con mezcla de modos. Fuerza diversidad
    por continente (no 2 países del mismo continente seguidos) y evita pares
    (país, modo) ya usados recientemente.

    Devuelve lista [(country_tuple, mode), ...] de longitud n."""
    pool = [c for c in data.COUNTRIES if c[4] == tier]
    random.shuffle(pool)
    picked: list[tuple] = []
    continents_used: list[str] = []
    mode_idx = 0
    for c in pool:
        if len(picked) >= n:
            break
        iso2, _, _, continent, _ = c
        # Buscar un modo válido para este país (no usado reciente + país tiene datos para ese modo)
        chosen_mode = None
        for _ in range(len(modes)):
            m = modes[mode_idx % len(modes)]
            mode_idx += 1
            # Filtros por modo:
            if m == "monument" and not data.monument_url(iso2):
                continue  # el país no tiene monumento registrado
            if m == "fact" and not data.fact_text(iso2):
                continue  # el país no tiene fact registrado
            if _pair_recent(led, iso2, m):
                continue
            chosen_mode = m
            break
        if not chosen_mode:
            continue
        # Preferimos no repetir mismo continente consecutivo (soft)
        if len(continents_used) >= 2 and continents_used[-1] == continent and continents_used[-2] == continent:
            continue
        picked.append((c, chosen_mode))
        continents_used.append(continent)
    return picked


def _pick_candidates(led: dict) -> list[tuple]:
    """Pick 10 preguntas = 3 fácil + 4 medio + 3 difícil con mezcla de 4+ modos.
    Devuelve [(country_tuple, mode), ...]."""
    # NOTA 14/10: "monument" descartado del pick activo — Wikimedia Commons tiene
    # thumbnail sizes impredecibles por archivo (algunos aceptan /500px/, otros
    # /640px/ etc.) → fallos aleatorios 400/404. Pool data.MONUMENTS se conserva
    # para re-activar cuando migremos a Wikimedia Commons API con resolver dinámico.
    modes_easy = ["flag", "capital"]
    modes_mid = ["flag", "capital", "silhouette"]
    modes_hard = ["flag", "capital", "silhouette", "fact"]
    out = []
    out += _pick_from_tier(led, 1, modes_easy, 3)
    out += _pick_from_tier(led, 2, modes_mid, 4)
    out += _pick_from_tier(led, 3, modes_hard, 3)
    # Ordenar por tier (ya debería estar) para progresión visual
    out.sort(key=lambda item: item[0][4])
    return out


def _notify(text: str, urgent: bool = False) -> None:
    from ..notify_batch import add
    add(text, urgent=urgent)


def _episode(led: dict) -> int:
    return len(led.get("rounds", [])) + 1


def _today_count(led: dict) -> int:
    today = datetime.now(timezone.utc).date().isoformat()
    return (led.get("by_day") or {}).get(today, 0)


def run_once() -> dict[str, Any]:
    """GeoQuiz = formato #1 de TikTok para nosotros (research 06/10): sin voz, quiz,
    comment-bait + follow CTA. DESTINO PRINCIPAL = TikTok (el MP4 va a Telegram para
    subida manual a @interest_stuff). YT es OPCIONAL (si algún día hay canal YT_GEOQUIZ).
    Siempre GENERA; cap diario GEOQUIZ_PER_DAY (default 1) para no inundar Telegram."""
    has_creds = bool(os.environ.get(YT_PREFIX + "_REFRESH_TOKEN"))
    led = _load_ledger()

    cap = int(os.environ.get("GEOQUIZ_PER_DAY", "1") or "1")
    if _today_count(led) >= cap:
        print(f"  geoquiz: tope diario ({cap}) alcanzado — skip")
        return {"status": "skip_daily_cap"}

    ep = _episode(led)
    questions = _pick_candidates(led)
    if len(questions) < N_ROUNDS:
        _notify(f"⚠️ GeoQuiz: solo {len(questions)} preguntas disponibles (esperado {N_ROUNDS}). "
                "Pool/modos agotados → considera añadir más países/monumentos/facts.", urgent=False)
    print(f"  geoquiz: generando ronda #{ep} ({len(questions)} preguntas, mix tier+modo)")
    meta = generator.generate_geoquiz(GEOQUIZ_ROOT, questions, n_rounds=len(questions))
    if not meta:
        _notify("❌ GeoQuiz falló generación", urgent=True)
        return {"status": "gen_fail"}
    # Efecto SERIE. Título varía: resalta el modo si todo el vídeo es un solo modo, si no mix.
    meta["title"] = f"Guess the country — Geo Quiz #{ep} 🌍 | 10 questions, easy → hard"[:100]

    # YT upload OPCIONAL (destino principal es TikTok). Sin canal → se omite, no rompe.
    url, yt_status = "", "skip_no_channel"
    if has_creds:
        from ..upload_youtube import upload_video
        prev_prefix = os.environ.get("YT_CHANNEL_PREFIX", "")
        prev_guard = os.environ.get("DEDUP_UPLOAD_GUARD")
        os.environ["YT_CHANNEL_PREFIX"] = YT_PREFIX
        os.environ["DEDUP_UPLOAD_GUARD"] = "0"  # título fijo de serie
        try:
            vid = upload_video(
                Path(meta["video_path"]), title=meta["title"], description=meta["description"],
                tags=meta.get("tags", []), category_id="27", is_short=True, privacy="public",
            )
            url = f"https://youtube.com/shorts/{vid}"
            yt_status = "ok"
        except Exception as e:
            print(f"  geoquiz upload fail: {type(e).__name__}: {e}")
            yt_status = f"fail: {type(e).__name__}"
        finally:
            if prev_prefix:
                os.environ["YT_CHANNEL_PREFIX"] = prev_prefix
            else:
                os.environ.pop("YT_CHANNEL_PREFIX", None)
            if prev_guard is not None:
                os.environ["DEDUP_UPLOAD_GUARD"] = prev_guard
            else:
                os.environ.pop("DEDUP_UPLOAD_GUARD", None)

    # TikTok (destino principal): el MP4 va a Telegram → subida manual a @interest_stuff.
    tt_ok = False
    try:
        from ..notify_batch import send_video_for_tiktok
        tt_ok = send_video_for_tiktok(meta["video_path"], DISPLAY_NAME, meta["title"], url)
    except Exception as e:
        print(f"  geoquiz: TT tg fail — {e}")

    now = datetime.now(timezone.utc).isoformat()
    today = datetime.now(timezone.utc).date().isoformat()
    led.setdefault("pairs", {})
    for iso2 in meta["countries"]:
        led["countries"][iso2] = now
    for pair in meta.get("pairs", []):
        led["pairs"][pair] = now  # pair = "iso2:mode"
    led["rounds"].append(meta["round_key"])
    led.setdefault("by_day", {})[today] = _today_count(led) + 1
    _save_ledger(led)
    _notify(f"🌍 <b>{DISPLAY_NAME}</b> #{ep} → {'Telegram para TikTok ✅' if tt_ok else 'generado'}"
            f"\n<i>{', '.join(meta['countries'])}</i>" + (f"\nYT: {url}" if url else ""))
    return {"status": "ok", "slug": meta["slug"], "url": url,
            "yt_status": yt_status, "tt": tt_ok, "round_key": meta["round_key"]}
