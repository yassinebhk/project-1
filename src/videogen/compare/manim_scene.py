"""Escena Manim — comparación de ESCALA (barras proporcionales a datos reales).

Data-driven: lee COMPARE_TOPIC (JSON) del entorno:
  {"title": "...", "unit": "km", "source": "Source: NASA",
   "items": [{"name": "Jupiter", "value": 139820}, ...]}

Visual 9:16: título arriba, barras horizontales a escala (ancho ∝ valor/máx) que
CRECEN una a una con su etiqueta + valor, y fuente abajo. Distinto de Global
Rankings (que es un bar-chart-race matplotlib): aquí es escala proporcional limpia.

    manim -qm --disable_caching manim_scene.py ScaleCompare
"""
from manim import *  # noqa: F403
import json
import os

config.frame_width = 9.0
config.frame_height = 16.0
config.pixel_width = 1080
config.pixel_height = 1920
config.frame_rate = 30

BG = "#0b1020"
BAR_COLORS = ["#4cc9f0", "#4895ef", "#4361ee", "#7209b7", "#f72585", "#ffba08", "#06d6a0"]

_DEFAULT = {
    "title": "Planet sizes compared",
    "unit": "km", "source": "Source: NASA",
    "items": [
        {"name": "Jupiter", "value": 139820},
        {"name": "Saturn", "value": 116460},
        {"name": "Neptune", "value": 49244},
        {"name": "Earth", "value": 12742},
        {"name": "Mars", "value": 6779},
        {"name": "Moon", "value": 3475},
    ],
}


def _fmt(v: float, unit: str) -> str:
    a = abs(float(v))
    if a >= 1e9:
        s = f"{v/1e9:.1f}B"
    elif a >= 1e6:
        s = f"{v/1e6:.1f}M"
    elif a >= 1e4:
        s = f"{v/1e3:.0f}k"
    elif a >= 1e3:
        s = f"{v/1e3:.1f}k"
    elif float(v) == int(v):
        s = f"{int(v)}"
    else:
        s = f"{v:.1f}"
    return f"{s} {unit}".strip()


def _load_topic() -> dict:
    try:
        t = json.loads(os.environ.get("COMPARE_TOPIC", "") or "{}")
    except Exception:
        t = {}
    if not t or not t.get("items"):
        return _DEFAULT
    return t


class ScaleCompare(Scene):
    def construct(self):
        topic = _load_topic()
        title = str(topic.get("title", ""))[:60]
        unit = str(topic.get("unit", ""))
        source = str(topic.get("source", ""))[:72]
        items = [i for i in topic["items"] if float(i.get("value", 0) or 0) > 0][:6]
        items = sorted(items, key=lambda x: float(x.get("value", 0)), reverse=True)
        if not items:
            items = _DEFAULT["items"]
        maxv = max(float(i.get("value", 0)) for i in items) or 1.0

        self.camera.background_color = BG

        # Título
        t = Text(title, font_size=52, color=WHITE, weight=BOLD)
        if t.width > 8.2:
            t.scale_to_fit_width(8.2)
        t.to_edge(UP, buff=0.7)
        self.play(FadeIn(t, shift=DOWN * 0.3), run_time=0.5)

        n = len(items)
        top, bottom = 5.6, -5.6
        row_h = (top - bottom) / max(n, 1)
        max_w = 6.1
        left_x = -3.9

        for idx, it in enumerate(items):
            name = str(it.get("name", ""))[:26]
            val = float(it.get("value", 0))
            w = max(max_w * (val / maxv), 0.28)
            y = top - row_h * (idx + 0.5)
            color = BAR_COLORS[idx % len(BAR_COLORS)]

            nm = Text(name, font_size=30, color=WHITE, weight=BOLD)
            if nm.width > 7.6:
                nm.scale_to_fit_width(7.6)
            nm.move_to([left_x, y + row_h * 0.30, 0], aligned_edge=LEFT)

            bar = Rectangle(width=w, height=row_h * 0.46, fill_color=color,
                            fill_opacity=1.0, stroke_width=0)
            bar.move_to([left_x + w / 2, y - row_h * 0.10, 0], aligned_edge=LEFT)

            vl = Text(_fmt(val, unit), font_size=28, color=color, weight=BOLD)
            vl.next_to(bar, RIGHT, buff=0.18)
            if vl.get_right()[0] > 4.3:  # no se sale de pantalla → dentro de la barra
                vl.set_color(WHITE).move_to(bar.get_center())

            self.play(FadeIn(nm, shift=RIGHT * 0.2), run_time=0.18)
            self.play(GrowFromEdge(bar, LEFT), FadeIn(vl), run_time=0.55)

        if source:
            src = Text(source, font_size=24, color=GREY_B)
            if src.width > 8.2:
                src.scale_to_fit_width(8.2)
            src.to_edge(DOWN, buff=0.55)
            self.play(FadeIn(src), run_time=0.4)

        self.wait(2.0)
