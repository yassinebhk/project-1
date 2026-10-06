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
COUNTRY_COOLDOWN_DAYS = 21
N_ROUNDS = 5


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


def _country_recent(led: dict, iso2: str) -> bool:
    ts = led["countries"].get(iso2)
    if not ts:
        return False
    try:
        return (datetime.now(timezone.utc) - datetime.fromisoformat(ts)) < timedelta(days=COUNTRY_COOLDOWN_DAYS)
    except Exception:
        return False


def _pick_candidates(led: dict, k: int = 14) -> list[tuple]:
    pool = list(data.COUNTRIES)
    random.shuffle(pool)
    fresh = [c for c in pool if not _country_recent(led, c[0])]
    rest = [c for c in pool if _country_recent(led, c[0])]
    cand = (fresh + rest)[:k]
    # mezcla de dificultad: ordena para que no salgan 5 difíciles seguidos
    cand.sort(key=lambda c: c[3])
    # intercala fácil/medio/difícil
    random.shuffle(cand)
    return cand


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
    candidates = _pick_candidates(led)
    print(f"  geoquiz: generando ronda #{ep} ({len(candidates)} candidatos)")
    meta = generator.generate_geoquiz(GEOQUIZ_ROOT, candidates, n_rounds=N_ROUNDS)
    if not meta:
        _notify("❌ GeoQuiz falló generación", urgent=True)
        return {"status": "gen_fail"}
    # Efecto SERIE (research: 'Parte X' + follow = 2-3× tasa de follow).
    meta["title"] = f"Guess the country by its flag #{ep} 🏴 | Only 1% score 5/5"[:100]

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
    for iso2 in meta["countries"]:
        led["countries"][iso2] = now
    led["rounds"].append(meta["round_key"])
    led.setdefault("by_day", {})[today] = _today_count(led) + 1
    _save_ledger(led)
    _notify(f"🌍 <b>{DISPLAY_NAME}</b> #{ep} → {'Telegram para TikTok ✅' if tt_ok else 'generado'}"
            f"\n<i>{', '.join(meta['countries'])}</i>" + (f"\nYT: {url}" if url else ""))
    return {"status": "ok", "slug": meta["slug"], "url": url,
            "yt_status": yt_status, "tt": tt_ok, "round_key": meta["round_key"]}
