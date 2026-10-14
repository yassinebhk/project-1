"""Pipeline Scale Compare (EN) — comparaciones de escala animadas (Manim).

Cada run: rota 1 topic (datos reales), renderiza la escena de barras a escala +
narración Edge, sube a YT_COMPARE (Short) y crospostea. 100% gratis.
Sin YT_COMPARE_REFRESH_TOKEN → render OK pero NO sube (no-op, no contamina).
"""
from __future__ import annotations

import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from ..config import ROOT

YT_PREFIX = "YT_COMPARE"
DISPLAY_NAME = "Scale Compare"
WORK_ROOT = ROOT / "output" / "compare_uploaded"


def _notify(text: str, urgent: bool = False) -> None:
    from ..notify_batch import add
    add(text, urgent=urgent)


def run_once() -> dict[str, Any]:
    from . import topics as ctopics, render as crender

    topic = ctopics.pick_topic()
    key = topic["key"]
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    slug = f"compare_{key}_{ts}"
    work = WORK_ROOT / slug

    final = crender.render_topic(topic, work)
    if not final or not Path(final).exists():
        _notify(f"❌ Scale Compare falló render · {key}", urgent=True)
        return {"status": "gen_fail", "topic": key}

    title = f"{topic['title']} #shorts"[:100]
    description = (
        f"{topic['title']} — real data, to scale.\n\n"
        f"{topic.get('source', '')}\n\n"
        f"Follow for more scale comparisons.\n\n"
        f"#shorts #comparison #scale #sizecomparison #didyouknow"
    )
    tags = ["comparison", "size comparison", "scale", "facts", "did you know", "shorts"]

    if not os.environ.get(YT_PREFIX + "_REFRESH_TOKEN"):
        ctopics.mark_used(key)
        _notify(f"⏸️ Scale Compare sin {YT_PREFIX}_REFRESH_TOKEN → render OK, no sube · {key}")
        return {"status": "no_channel", "topic": key}

    from ..upload_youtube import upload_video
    prev = os.environ.get("YT_CHANNEL_PREFIX", "")
    os.environ["YT_CHANNEL_PREFIX"] = YT_PREFIX
    url, yt_status = "", "skip"
    try:
        vid = upload_video(Path(final), title=title, description=description[:4900],
                           tags=tags, category_id="27", is_short=True, privacy="public")
        url = f"https://youtube.com/shorts/{vid}"
        yt_status = "ok"
    except Exception as e:
        print(f"  compare upload fail: {type(e).__name__}: {e}")
        yt_status = f"fail: {type(e).__name__}"
    finally:
        if prev:
            os.environ["YT_CHANNEL_PREFIX"] = prev
        else:
            os.environ.pop("YT_CHANNEL_PREFIX", None)

    ctopics.mark_used(key)
    _notify(f"✅ <b>{DISPLAY_NAME}</b> · YT: {url or yt_status}\n<i>{topic['title']}</i>")

    try:
        from .. import crosspost_full
        cross = crosspost_full.crosspost_short_from_mp4(
            Path(final), title, url, teaser=f"📐 {topic['title']}",
            channel_label="compare", slug=slug,
        )
        _notify(f"📐 <b>Compare · RRSS</b> {crosspost_full.summary_line(cross)}")
    except Exception as e:
        print(f"  compare crosspost fail: {e}")

    return {"status": "ok" if yt_status == "ok" else yt_status,
            "slug": slug, "url": url, "topic": key, "yt_status": yt_status}
