"""Topics semilla de comparaciones de escala — datos reales + fuente citable.

Cada topic: key, title, unit, source, narration (voz EN) + items[{name,value}].
El refresher dinámico (vía LLM cheap-first) se añadirá tras validar el visual;
de momento rota sobre estos seeds verificables.
"""
from __future__ import annotations

import json
import os
import random
from datetime import datetime, timezone
from pathlib import Path

from ..config import ROOT

LEDGER_PATH = ROOT / "output" / "compare_ledger.json"

SEED: list[dict] = [
    {
        "key": "planets", "title": "Planet sizes compared", "unit": "km",
        "source": "Source: NASA",
        "narration": ("How big are the planets, really? By diameter, Jupiter dwarfs "
                      "everything. Saturn is next. And Earth? Barely a stripe next to "
                      "the giants. The Moon is tiny. Follow for more scale comparisons."),
        "items": [
            {"name": "Jupiter", "value": 139820}, {"name": "Saturn", "value": 116460},
            {"name": "Neptune", "value": 49244}, {"name": "Earth", "value": 12742},
            {"name": "Mars", "value": 6779}, {"name": "Moon", "value": 3475},
        ],
    },
    {
        "key": "tall_buildings", "title": "Tallest buildings on Earth", "unit": "m",
        "source": "Source: CTBUH",
        "narration": ("The tallest buildings in the world, by height. The Burj Khalifa "
                      "still towers over everything at over 800 metres. Merdeka 118 and "
                      "the Shanghai Tower follow. Follow for more scale comparisons."),
        "items": [
            {"name": "Burj Khalifa", "value": 828}, {"name": "Merdeka 118", "value": 679},
            {"name": "Shanghai Tower", "value": 632}, {"name": "Abraj Al-Bait", "value": 601},
            {"name": "Ping An", "value": 599}, {"name": "One WTC", "value": 541},
        ],
    },
    {
        "key": "fastest_animals", "title": "Fastest animals on Earth", "unit": "km/h",
        "source": "Source: public records",
        "narration": ("The fastest animals alive. In a dive, the peregrine falcon hits "
                      "nearly 390 kilometres an hour. On land, the cheetah tops 100. And "
                      "the fastest human? Not even close. Follow for more comparisons."),
        "items": [
            {"name": "Peregrine falcon", "value": 389}, {"name": "Golden eagle", "value": 240},
            {"name": "Cheetah", "value": 110}, {"name": "Pronghorn", "value": 98},
            {"name": "Lion", "value": 80}, {"name": "Usain Bolt", "value": 44},
        ],
    },
    {
        "key": "largest_countries", "title": "Largest countries by area", "unit": "M km²",
        "source": "Source: UN",
        "narration": ("The biggest countries on Earth by area. Russia is in a league of "
                      "its own, almost twice the size of Canada. China and the US are "
                      "neck and neck. Follow for more scale comparisons."),
        "items": [
            {"name": "Russia", "value": 17.1}, {"name": "Canada", "value": 10.0},
            {"name": "China", "value": 9.6}, {"name": "USA", "value": 9.5},
            {"name": "Brazil", "value": 8.5}, {"name": "Australia", "value": 7.7},
        ],
    },
    {
        "key": "ocean_trenches", "title": "Deepest ocean trenches", "unit": "m",
        "source": "Source: NOAA",
        "narration": ("How deep does the ocean go? The Mariana Trench plunges almost "
                      "11 kilometres down — deeper than Everest is tall. The Tonga and "
                      "Philippine trenches aren't far behind. Follow for more."),
        "items": [
            {"name": "Mariana", "value": 10935}, {"name": "Tonga", "value": 10882},
            {"name": "Kuril–Kamchatka", "value": 10542}, {"name": "Philippine", "value": 10540},
            {"name": "Puerto Rico", "value": 8376},
        ],
    },
    {
        "key": "biggest_animals", "title": "Biggest animals by length", "unit": "m",
        "source": "Source: public records",
        "narration": ("The biggest animals on Earth, by length. The blue whale is the "
                      "largest animal that has ever lived — longer than a basketball "
                      "court. A human barely registers. Follow for more comparisons."),
        "items": [
            {"name": "Blue whale", "value": 30}, {"name": "Whale shark", "value": 12},
            {"name": "Great white", "value": 6}, {"name": "Giraffe", "value": 5.5},
            {"name": "Human", "value": 1.7},
        ],
    },
]


def _load_ledger() -> dict[str, str]:
    if not LEDGER_PATH.exists():
        return {}
    try:
        return json.loads(LEDGER_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {}


def mark_used(key: str) -> None:
    LEDGER_PATH.parent.mkdir(parents=True, exist_ok=True)
    d = _load_ledger()
    d[key] = datetime.now(timezone.utc).isoformat()
    LEDGER_PATH.write_text(json.dumps(d, indent=2, ensure_ascii=False), encoding="utf-8")


def pick_topic() -> dict:
    """Rota: el topic usado hace más tiempo (o nunca). COMPARE_TOPIC_KEY fuerza uno."""
    forced = os.environ.get("COMPARE_TOPIC_KEY", "").strip()
    if forced:
        for t in SEED:
            if t["key"] == forced:
                return t
    used = _load_ledger()
    never = [t for t in SEED if t["key"] not in used]
    if never:
        return random.choice(never)
    return min(SEED, key=lambda t: used.get(t["key"], ""))
