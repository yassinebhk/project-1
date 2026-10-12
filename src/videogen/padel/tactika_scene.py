"""Escenas Manim 3D — formato @tactikapadel (réplica aprobada 10/10).

Diferencias vs manim_scene.py (formato 2D top-down):
- Pista en PERSPECTIVA 3D isométrica (ThreeDScene con cámara en phi/theta)
- Paredes de cristal semi-transparentes (Prism con fill_opacity bajo)
- Jugadores como silhouettes PNG (ImageMobject proyectados sobre la pista)
- Bola 3D (Sphere) con trayectoria 3D bezier + bounce visible
- Pastillas de labels sobre jugadores ("Tú", "Pareja", "Rival A", "Rival B")
- Slide de dato académico entre jugadas (big_number + fuente citada)
- Avatar narrador (Mark) añadido en overlay ffmpeg post-render — ver render.py

Pipeline con flag PADEL_FORMAT=tactika usa estas escenas; default manim.
Compatible con el runner Oracle (manim CE 0.18+). NO ejecutable localmente
sin pango/harfbuzz instalados.
"""
from __future__ import annotations

from manim import *
import numpy as np

config.frame_width = 9.0
config.frame_height = 16.0
config.pixel_width = 1080
config.pixel_height = 1920
config.frame_rate = 30

# Paleta copiada de manim_scene (coherencia de marca)
COURT_FLOOR = "#1f6e8c"  # azul pista
GLASS_C = "#9fd4e8"      # cristal semi-transparente
LINE_C = "#ffffff"       # líneas blancas
BALL_C = "#e8ff2a"       # bola amarilla
TRAIL_C = "#fff59d"      # estela
BG_C = "#0a0f16"         # fondo (grada oscura)
LABEL_BG = "#111827"     # pastilla label
LABEL_YOU = "#22c55e"    # verde (Tú/Pareja)
LABEL_RIVAL = "#ef4444"  # rojo (Rival A/B)

# Dimensiones pista real: 10x20m. En Manim trabajamos en unidades, cada "u" = 1m.
# Centramos en 0,0,0 → pista va de (-5,-10,0) a (5,10,0). Red en y=0.
COURT_W = 10.0
COURT_L = 20.0
WALL_H = 3.0            # cristal 3m
GLASS_SIDE_H = 2.0      # lateral de malla 4m total pero visible 2m


# ────────────────────────── BUILDERS BÁSICOS 3D ──────────────────────────

def _court_floor():
    """Pista azul 10×20 como Prism aplanado (grosor 0.05)."""
    floor = Prism(dimensions=[COURT_W, COURT_L, 0.05], fill_color=COURT_FLOOR,
                  fill_opacity=1.0, stroke_width=0)
    floor.shift(OUT * 0.025)
    return floor


def _court_lines():
    """Líneas blancas: contorno + servicio + cruz central."""
    z = 0.07
    corners = [
        np.array([-COURT_W/2, -COURT_L/2, z]), np.array([COURT_W/2, -COURT_L/2, z]),
        np.array([COURT_W/2, COURT_L/2, z]),  np.array([-COURT_W/2, COURT_L/2, z]),
    ]
    outline = VGroup(*[Line3D(corners[i], corners[(i+1) % 4], color=LINE_C, thickness=0.03)
                       for i in range(4)])
    # Red en y=0
    net = Line3D(np.array([-COURT_W/2, 0, z]), np.array([COURT_W/2, 0, z]),
                 color=LINE_C, thickness=0.05)
    # Líneas de servicio (y=±3m real → ±3 unidades aquí mapeo directo)
    serve_a = Line3D(np.array([-COURT_W/2, -3, z]), np.array([COURT_W/2, -3, z]),
                     color=LINE_C, thickness=0.03)
    serve_b = Line3D(np.array([-COURT_W/2, 3, z]), np.array([COURT_W/2, 3, z]),
                     color=LINE_C, thickness=0.03)
    # Línea central entre servicios
    center = Line3D(np.array([0, -3, z]), np.array([0, 3, z]),
                    color=LINE_C, thickness=0.03)
    return VGroup(outline, net, serve_a, serve_b, center)


def _glass_walls():
    """Paredes de cristal semi-transparentes en los dos fondos + laterales bajos."""
    # Fondo back (y=+10) y back (y=-10)
    back_pos = Prism(dimensions=[COURT_W, 0.1, WALL_H], fill_color=GLASS_C,
                     fill_opacity=0.18, stroke_color=GLASS_C, stroke_width=1)
    back_pos.shift(np.array([0, COURT_L/2, WALL_H/2]))
    back_neg = back_pos.copy().shift(np.array([0, -COURT_L, 0]))
    # Laterales (más bajos, visualmente)
    side_r = Prism(dimensions=[0.1, COURT_L, GLASS_SIDE_H], fill_color=GLASS_C,
                   fill_opacity=0.14, stroke_color=GLASS_C, stroke_width=1)
    side_r.shift(np.array([COURT_W/2, 0, GLASS_SIDE_H/2]))
    side_l = side_r.copy().shift(np.array([-COURT_W, 0, 0]))
    return VGroup(back_pos, back_neg, side_r, side_l)


def _net():
    """Red central (y=0): tira negra fina en vertical."""
    net = Prism(dimensions=[COURT_W, 0.08, 0.9], fill_color="#0b1218",
                fill_opacity=0.85, stroke_color="#334155", stroke_width=1)
    net.shift(np.array([0, 0, 0.45]))
    return net


def _player_figure(x, y, color, side="A"):
    """Figura humana estilizada 3D: sombra + cuerpo + hombros + cabeza + pala.
    Mucho más reconocible que un cilindro desde la cámara isométrica.

    El VGroup queda con centro Z ≈ 0.9 (parecido al cilindro antiguo z=0.875),
    así que los `self.play(...animate.move_to([x', y', 0.875]))` del resto del
    código siguen moviendo la figura rígida sin descuadres apreciables."""
    SKIN = "#f5c7a0"
    PADDLE = "#1a202c"
    # Sombra elíptica en el suelo bajo el jugador (profundidad)
    shadow = Ellipse(width=1.3, height=0.55, fill_color="#000000",
                     fill_opacity=0.4, stroke_width=0)
    shadow.move_to(np.array([x, y, 0.04]))
    # Tronco: cilindro ancho y corto (más humano que un palo)
    body = Cylinder(radius=0.42, height=1.1, direction=OUT,
                    fill_color=color, fill_opacity=1.0, stroke_width=0,
                    checkerboard_colors=[color, color],
                    resolution=(14, 1))
    body.move_to(np.array([x, y, 0.55]))  # z 0 → 1.1
    # Hombros: esfera que redondea arriba del tronco
    shoulders = Sphere(radius=0.46, resolution=(10, 10),
                       fill_color=color, fill_opacity=1.0, stroke_width=0,
                       checkerboard_colors=[color, color])
    shoulders.move_to(np.array([x, y, 1.1]))
    # Cabeza (tono piel para que destaque del tronco)
    head = Sphere(radius=0.28, resolution=(10, 10),
                  fill_color=SKIN, fill_opacity=1.0, stroke_width=0,
                  checkerboard_colors=[SKIN, SKIN])
    head.move_to(np.array([x, y, 1.55]))
    # Pala (prism oscuro al lado — el side define si va a derecha o izquierda)
    poff = 0.75 if side == "A" else -0.75
    paddle = Prism(dimensions=[0.08, 0.42, 0.3], fill_color=PADDLE,
                   fill_opacity=1.0, stroke_width=0)
    paddle.move_to(np.array([x + poff, y, 0.95]))
    return VGroup(shadow, body, shoulders, head, paddle)


def _ball_sphere(x, y, z=0.5):
    """Pelota amarilla 3D con halo exterior semi-transparente para visibilidad.

    La bola sola era demasiado pequeña contra la pista azul desde cámara
    isométrica. El halo (esfera r=0.42 opacity 0.3) la hace legible sin que
    parezca una pelota gigante poco realista."""
    halo = Sphere(radius=0.42, resolution=(10, 10), fill_color=BALL_C,
                  fill_opacity=0.3, stroke_width=0,
                  checkerboard_colors=[BALL_C, BALL_C])
    halo.move_to(np.array([x, y, z]))
    ball = Sphere(radius=0.26, resolution=(14, 14), fill_color=BALL_C,
                  fill_opacity=1.0, stroke_width=0,
                  checkerboard_colors=[BALL_C, BALL_C])
    ball.move_to(np.array([x, y, z]))
    return VGroup(halo, ball)


def _label_pill(player_mobj, text, text_color=LABEL_YOU):
    """Pastilla label sobre un jugador. Billboarded (orientación fija a cámara)
    + se mueve CON el jugador vía add_updater (si el jugador se desplaza con
    .animate.move_to(), la label le sigue sin tener que animarla a mano)."""
    txt = Text(text, font_size=28, color=text_color, weight=BOLD)
    bg = RoundedRectangle(width=txt.width + 0.4, height=txt.height + 0.25,
                          corner_radius=0.12, stroke_width=0,
                          fill_color=LABEL_BG, fill_opacity=0.9)
    pill = VGroup(bg, txt)
    pill.move_to(player_mobj.get_top() + OUT * 0.3)
    pill.add_updater(lambda m, p=player_mobj: m.move_to(p.get_top() + OUT * 0.3))
    return pill


# ────────────────────────── BASE 3D SCENE ──────────────────────────

class TactikaBase(ThreeDScene):
    """Base compartida: construye la pista 3D con cámara isométrica y jugadores."""

    def build_court(self, you=((-1.7, -7), (1.7, -7)), rivals=((-1.5, 7), (1.5, 7))):
        self.camera.background_color = BG_C
        # Cámara isométrica desde esquina (ángulo @tactikapadel aproximado):
        # phi = inclinación desde Z (65º), theta = rotación XY (-80º) para ver 3/4
        self.set_camera_orientation(phi=65 * DEGREES, theta=-80 * DEGREES,
                                    zoom=0.55)
        floor = _court_floor()
        lines = _court_lines()
        glass = _glass_walls()
        net = _net()
        self.play(FadeIn(floor), FadeIn(glass), run_time=0.5)
        self.play(Create(lines), FadeIn(net), run_time=0.6)
        # side A/B alterna la mano de la pala para que no se solape pareja
        self.blues = [_player_figure(x, y, LABEL_YOU, side=("A" if i == 0 else "B"))
                      for i, (x, y) in enumerate(you)]
        self.reds = [_player_figure(x, y, LABEL_RIVAL, side=("A" if i == 0 else "B"))
                     for i, (x, y) in enumerate(rivals)]
        self.play(*[FadeIn(p) for p in self.blues + self.reds], run_time=0.5)
        # Labels fijas-a-cámara (always_face_camera)
        labels_you = ["TÚ", "PAREJA"]
        labels_rv = ["RIVAL A", "RIVAL B"]
        self.labels = VGroup()
        for p, name in zip(self.blues, labels_you):
            pill = _label_pill(p, name, text_color=LABEL_YOU)
            self.add_fixed_orientation_mobjects(pill)
            self.labels.add(pill)
        for p, name in zip(self.reds, labels_rv):
            pill = _label_pill(p, name, text_color=LABEL_RIVAL)
            self.add_fixed_orientation_mobjects(pill)
            self.labels.add(pill)
        self.play(*[FadeIn(l) for l in self.labels], run_time=0.4)
        self.title_mobj = None

    def title_card(self, text, color=YELLOW, run_time=0.5):
        """Título fijo-a-cámara en la parte superior (overlay sobre la escena 3D).

        Manim-CE idiom para ThreeDScene: add_fixed_in_frame_mobjects añade al
        overlay fijo (no rota con cámara) pero NO está en self.mobjects, así que
        FadeIn/FadeOut y self.remove() no funcionan sobre él. Hay que animar con
        .set_opacity() y liberar con remove_fixed_in_frame_mobjects()."""
        t = Text(text, font_size=52, color=color, weight=BOLD)
        if t.width > 8.4:
            t.scale_to_fit_width(8.4)
        t.to_edge(UP, buff=0.35)
        t.set_opacity(0.0)
        self.add_fixed_in_frame_mobjects(t)
        if self.title_mobj is not None:
            self.play(self.title_mobj.animate.set_opacity(0.0), run_time=run_time * 0.5)
            self.remove_fixed_in_frame_mobjects(self.title_mobj)
        self.play(t.animate.set_opacity(1.0), run_time=run_time)
        self.title_mobj = t

    def ball_arc_3d(self, start, peak_z, end):
        """Trayectoria bezier 3D (parábola con pico en peak_z). Línea gruesa
        amarilla brillante para que el recorrido se lea desde cámara isométrica
        contra pista azul (stroke_width=5 era invisible desde el ángulo picado)."""
        s = np.array(start); e = np.array(end)
        mid = (s + e) / 2
        mid[2] = peak_z
        return CubicBezier(s, s + np.array([0, 0, peak_z * 0.5]),
                           e + np.array([0, 0, peak_z * 0.5]), e,
                           color=BALL_C, stroke_width=14)

    def animate_ball(self, path, run_time=1.0, rate=linear, mark_impact=True):
        """Añade la bola al inicio y la mueve a lo largo del path 3D.
        Si mark_impact=True, deja un dot amarillo en el end-point del arco
        marcando el punto de bote (ayuda a seguir el recorrido entre arcos)."""
        start_pt = path.get_start()
        end_pt = path.get_end()
        ball = _ball_sphere(start_pt[0], start_pt[1], start_pt[2])
        self.add(ball)
        self.play(Create(path), MoveAlongPath(ball, path), run_time=run_time, rate_func=rate)
        if mark_impact:
            # Dot amarillo en el end-point: señala punto de bote/impacto
            impact = Sphere(radius=0.18, resolution=(8, 8), fill_color=TRAIL_C,
                            fill_opacity=0.75, stroke_width=0,
                            checkerboard_colors=[TRAIL_C, TRAIL_C])
            impact.move_to(end_pt)
            self.add(impact)
        return ball

    def academic_slide(self, fact: dict, hold: float = 4.0):
        """Slide fullscreen con dato académico (big number + fuente). Se superpone
        a la escena 3D con un panel sólido fijo-a-cámara. Al salir, el panel
        desaparece y la escena 3D queda intacta debajo. Oculta temporalmente el
        título para que no se vea encima del panel."""
        panel = Rectangle(width=9.4, height=16.4, fill_color=BG_C,
                          fill_opacity=1.0, stroke_width=0)
        big = Text(fact["big_number"] + (" " + fact["unit"] if fact.get("unit") else ""),
                   font_size=180, color=BALL_C, weight=BOLD)
        if big.width > 7.5:
            big.scale_to_fit_width(7.5)
        big.move_to(UP * 2.0)
        ctx = Text(fact["context"], font_size=46, color=LINE_C, weight=BOLD,
                   line_spacing=1.1, should_center=True)
        if ctx.width > 8.0:
            ctx.scale_to_fit_width(8.0)
        ctx.next_to(big, DOWN, buff=0.8)
        cite = Text(f"Fuente: {fact['cite_short']}", font_size=28, color="#9ca3af",
                    slant="ITALIC")
        if cite.width > 7.5:
            cite.scale_to_fit_width(7.5)
        cite.to_edge(DOWN, buff=0.9)
        # Oculta título del formato táctica para evitar overlap con el panel
        if self.title_mobj is not None:
            self.play(self.title_mobj.animate.set_opacity(0.0), run_time=0.2)
        # Añade en orden: panel al fondo primero, texto encima
        for m in (panel, big, ctx, cite):
            m.set_opacity(0.0)
        self.add_fixed_in_frame_mobjects(panel, big, ctx, cite)
        self.play(panel.animate.set_opacity(1.0), run_time=0.3)
        self.play(big.animate.set_opacity(1.0), run_time=0.5)
        self.play(ctx.animate.set_opacity(1.0), cite.animate.set_opacity(1.0), run_time=0.4)
        self.wait(hold)
        self.play(panel.animate.set_opacity(0.0), big.animate.set_opacity(0.0),
                  ctx.animate.set_opacity(0.0), cite.animate.set_opacity(0.0),
                  run_time=0.4)
        self.remove_fixed_in_frame_mobjects(panel, big, ctx, cite)
        # Restaura título si existía
        if self.title_mobj is not None:
            self.play(self.title_mobj.animate.set_opacity(1.0), run_time=0.2)

    def outro(self, recap: str, cta: str = "SIGUE PARA MÁS\nPÁDEL CON DATOS", hold: float = 3.0):
        panel = Rectangle(width=9.4, height=16.4, fill_color=BG_C,
                          fill_opacity=1.0, stroke_width=0)
        rtxt = Text(recap, font_size=58, color=LABEL_YOU, weight=BOLD,
                    line_spacing=1.1, should_center=True)
        if rtxt.width > 8.0:
            rtxt.scale_to_fit_width(8.0)
        rtxt.move_to(UP * 1.2)
        ctxt = Text(cta, font_size=48, color=BALL_C, weight=BOLD,
                    line_spacing=1.15, should_center=True)
        if ctxt.width > 7.6:
            ctxt.scale_to_fit_width(7.6)
        ctxt.next_to(rtxt, DOWN, buff=1.3)
        for m in (panel, rtxt, ctxt):
            m.set_opacity(0.0)
        self.add_fixed_in_frame_mobjects(panel, rtxt, ctxt)
        self.play(panel.animate.set_opacity(1.0), run_time=0.4)
        self.play(rtxt.animate.set_opacity(1.0), run_time=0.9)
        self.play(ctxt.animate.set_opacity(1.0), run_time=0.6)
        self.wait(hold)


# ────────────────────────── 8 TÁCTICAS 3D ──────────────────────────

class TactikaLob(TactikaBase):
    """El globo — toma la red."""
    NARRATION = (
        "Los rivales dominan la red y tú estás clavado al fondo. Si fuerzas un passing bajo, "
        "les regalas una volea fácil. La solución es el globo. Toma la bola temprano, levántala "
        "alta y profunda, hacia el cristal del fondo. Les obligas a girarse y correr. Y mientras "
        "retroceden, tu pareja y tú subís a la red. Controla la red y controlarás el punto."
    )
    FACT_KEY = "net_control_wins_70pct"

    def construct(self):
        from videogen.padel.academic_pool import by_key
        self.build_court(you=((-1.7, -7), (1.7, -7)), rivals=((-1.5, 7), (1.5, 7)))
        self.title_card("Dominan la red", color=LABEL_RIVAL)
        self.wait(2.0)
        # Dato académico
        f = by_key(self.FACT_KEY)
        if f:
            self.academic_slide(f, hold=3.5)
        # Globo profundo
        self.title_card("Juega el GLOBO", color=BALL_C)
        path = self.ball_arc_3d(start=(-1.7, -6, 1.0), peak_z=6.0, end=(-0.5, 9.5, 0.3))
        ball = self.animate_ball(path, run_time=1.1, rate=linear)
        # Rebote al fondo
        bounce = self.ball_arc_3d(start=(-0.5, 9.5, 0.3), peak_z=1.5, end=(0.5, 5.0, 0.3))
        self.play(Create(bounce), MoveAlongPath(ball, bounce), run_time=0.7, rate_func=rush_from)
        self.wait(0.8)
        # Rivales retroceden
        self.title_card("Retroceden", color="#f97316")
        self.play(self.reds[0].animate.move_to(np.array([-1.5, 9, 0.875])),
                  self.reds[1].animate.move_to(np.array([1.5, 9, 0.875])),
                  run_time=1.0)
        self.wait(1.5)
        # Tú subes a la red
        self.title_card("Subes a la red", color=LABEL_YOU)
        self.play(self.blues[0].animate.move_to(np.array([-1.7, -2, 0.875])),
                  self.blues[1].animate.move_to(np.array([1.7, -2, 0.875])),
                  run_time=1.0)
        self.wait(2.0)
        self.outro("Controla la red\n=\ncontrola el punto")


class TactikaBandeja(TactikaBase):
    """Bandeja — defensa activa en vez de remate plano."""
    NARRATION = (
        "Te meten un globo y tiras un remate plano arriesgado? Si fallas, les regalas la red. "
        "Juega la bandeja. Es un remate cortado, controlado. Golpéala delante, cruzada y "
        "profunda, baja sobre la red. No ganas el punto, pero conservas la red. Y eso es "
        "lo que te permite ganar los siguientes."
    )
    FACT_KEY = "backhand_80pct_bandeja"

    def construct(self):
        from videogen.padel.academic_pool import by_key
        self.build_court(you=((-1.7, -2), (1.7, -2)), rivals=((-1.5, 6), (1.5, 6)))
        self.title_card("Te meten un globo", color=LABEL_RIVAL)
        lob_in = self.ball_arc_3d(start=(0, 6, 1), peak_z=5.5, end=(-1.5, -5, 1.5))
        ball = self.animate_ball(lob_in, run_time=1.0, rate=linear)
        self.wait(0.6)
        # Dato académico sobre bandejas
        f = by_key(self.FACT_KEY)
        if f:
            self.academic_slide(f, hold=3.5)
        self.title_card("Juega la BANDEJA", color=BALL_C)
        band = self.ball_arc_3d(start=(-1.5, -5, 1.5), peak_z=2.5, end=(3.5, 8, 0.3))
        self.play(Create(band), MoveAlongPath(ball, band), run_time=1.0, rate_func=linear)
        self.wait(1.2)
        self.title_card("Mantienes la red", color=LABEL_YOU)
        self.wait(2.0)
        self.outro("Control >\npotencia")


class TactikaBackWall(TactikaBase):
    """Bajada de pared — defensa paciente."""
    NARRATION = (
        "Una bola rapidísima hacia tu cristal del fondo y tú entras a golpear temprano? "
        "Así la mandas a la red. Deja que pase, que choque contra la pared y vuelva. "
        "Con el bote delante tuyo, agáchate y levántala. Un globo alto y profundo al "
        "otro campo. Acabas de convertir una defensa en un reset limpio."
    )
    FACT_KEY = "glass_rebound_40pct_defense"

    def construct(self):
        from videogen.padel.academic_pool import by_key
        self.build_court(you=((-1.7, -3), (1.7, -3)), rivals=((-1.5, 6), (1.5, 6)))
        self.title_card("Bola al cristal del fondo")
        inc = self.ball_arc_3d(start=(0, 6, 1), peak_z=2.5, end=(-1.5, -9, 1.0))
        ball = self.animate_ball(inc, run_time=0.9, rate=linear)
        self.wait(0.4)
        f = by_key(self.FACT_KEY)
        if f:
            self.academic_slide(f, hold=3.5)
        self.title_card("Deja que trabaje la pared", color=BALL_C)
        reb = self.ball_arc_3d(start=(-1.5, -9, 0.3), peak_z=1.0, end=(-1.5, -4, 0.8))
        self.play(Create(reb), MoveAlongPath(ball, reb), run_time=0.7, rate_func=rush_from)
        self.wait(1.0)
        self.title_card("Levanta un globo profundo", color=LABEL_YOU)
        lob = self.ball_arc_3d(start=(-1.5, -4, 0.8), peak_z=6.0, end=(-0.5, 9, 0.3))
        self.play(Create(lob), MoveAlongPath(ball, lob), run_time=1.0, rate_func=linear)
        self.wait(1.8)
        self.outro("Defensa →\nreset limpio")


class TactikaSmash(TactikaBase):
    """Por tres — remate ganador."""
    NARRATION = (
        "Bola corta y alta cómoda arriba? Es tu momento. Golpea abajo y fuerte hacia la "
        "esquina. La bola rebota en el suelo, sube disparada contra el cristal del fondo "
        "y sale por encima de la valla lateral. Eso es el por tres. Imposible de devolver. "
        "Pero úsalo solo cuando la bola está alta y corta."
    )
    FACT_KEY = "rally_length_7_strokes"

    def construct(self):
        from videogen.padel.academic_pool import by_key
        self.build_court(you=((-1.7, -2), (1.7, -2)), rivals=((-1.5, 7), (1.5, 7)))
        self.title_card("Bola corta y alta", color=BALL_C)
        setup = self.ball_arc_3d(start=(-1.7, -2, 2.5), peak_z=2.8, end=(-1.5, -1.5, 2.0))
        ball = self.animate_ball(setup, run_time=0.5, rate=linear)
        f = by_key(self.FACT_KEY)
        if f:
            self.academic_slide(f, hold=3.5)
        self.title_card("REMATE por tres", color=BALL_C)
        smash = self.ball_arc_3d(start=(-1.5, -1.5, 2.0), peak_z=0.8, end=(-1.5, 9.5, 0.2))
        self.play(Create(smash), MoveAlongPath(ball, smash), run_time=0.5, rate_func=rush_into)
        # Rebote cristal fondo
        up = self.ball_arc_3d(start=(-1.5, 9.5, 0.2), peak_z=5.5, end=(7, 2, 2.5))
        self.play(Create(up), MoveAlongPath(ball, up), run_time=0.9, rate_func=linear)
        self.wait(1.4)
        self.outro("Imposible\nde devolver")


class TactikaDrop(TactikaBase):
    """Dejada — sorprender a los rivales profundos."""
    NARRATION = (
        "Los dos rivales atrás, pegados al cristal? No les sigas pegando fuerte. "
        "Sorpréndelos. Quita toda la potencia y suéltala blanda, justo por encima de la red, "
        "que muera antes de que puedan correr. Cuanto más atrás estén, más mortal es la dejada. "
        "Y disimúlala como un golpe normal hasta el último segundo."
    )
    FACT_KEY = "unforced_errors_50pct"

    def construct(self):
        from videogen.padel.academic_pool import by_key
        self.build_court(you=((-1.7, -2), (1.7, -2)), rivals=((-1.5, 8), (1.5, 8.5)))
        self.title_card("Rivales clavados atrás", color=LABEL_RIVAL)
        self.wait(1.5)
        f = by_key(self.FACT_KEY)
        if f:
            self.academic_slide(f, hold=3.5)
        self.title_card("Suelta la DEJADA", color=BALL_C)
        drop = self.ball_arc_3d(start=(-1.5, -2, 1.5), peak_z=2.0, end=(-1.0, 1.2, 0.3))
        ball = self.animate_ball(drop, run_time=1.0, rate=rush_from)
        self.wait(1.5)
        self.title_card("Demasiado lejos", color=LABEL_YOU)
        self.wait(2.0)
        self.outro("Cuanto + lejos,\n+ mortal")


class TactikaServe(TactikaBase):
    """Saque abierto a cristal."""
    NARRATION = (
        "Perdiendo el saque con un flojo plano al centro? El saque monta el punto entero. "
        "Saca por abajo, por debajo de la cintura, y abre hacia la esquina, que pegue contra "
        "el cristal lateral y arrastre al rival fuera de la pista. Luego sube inmediatamente "
        "a la red. Un saque inteligente, y atacas desde la primera bola."
    )
    FACT_KEY = "serve_wide_60pct_pro"

    def construct(self):
        from videogen.padel.academic_pool import by_key
        self.build_court(you=((2.0, -7), (-1.5, -5)), rivals=((-1.5, 6), (1.5, 6)))
        self.title_card("Tu saque")
        self.wait(1.0)
        f = by_key(self.FACT_KEY)
        if f:
            self.academic_slide(f, hold=3.5)
        self.title_card("Saca ABIERTO", color=BALL_C)
        serve = self.ball_arc_3d(start=(2.0, -6, 0.8), peak_z=1.8, end=(-4.5, 4, 0.3))
        ball = self.animate_ball(serve, run_time=0.9, rate=linear)
        kick = self.ball_arc_3d(start=(-4.5, 4, 0.3), peak_z=0.8, end=(-6, 5, 1.0))
        self.play(Create(kick), MoveAlongPath(ball, kick), run_time=0.5, rate_func=rush_from)
        self.wait(1.0)
        self.title_card("Sube a la red", color=LABEL_YOU)
        self.play(self.blues[0].animate.move_to(np.array([2.0, -2, 0.875])),
                  self.blues[1].animate.move_to(np.array([-1.5, -2, 0.875])),
                  run_time=1.0)
        self.wait(1.8)
        self.outro("Ataca desde\nla 1ª bola")


class TactikaPositioning(TactikaBase):
    """Posición de pareja — moverse como uno."""
    NARRATION = (
        "Corriendo cada bola solo mientras tu pareja mira? Eso es equipo perdedor. "
        "En pádel os movéis como uno. Lado a lado, dos metros entre vosotros, deslizando "
        "juntos. Izquierda, derecha, delante, atrás, como si os uniera una cuerda. "
        "Cubrid el medio, no dejéis hueco. Moveros como pareja, y la pista no tiene agujeros."
    )
    FACT_KEY = "winning_pairs_share_court"

    def construct(self):
        from videogen.padel.academic_pool import by_key
        self.build_court(you=((-1.5, -4), (1.5, -4)), rivals=((-1.5, 5), (1.5, 5)))
        self.title_card("Moveros como pareja", color=LABEL_YOU)
        self.wait(1.5)
        f = by_key(self.FACT_KEY)
        if f:
            self.academic_slide(f, hold=3.5)
        self.title_card("Deslizad JUNTOS", color=BALL_C)
        self.play(self.blues[0].animate.move_to(np.array([-3.5, -4, 0.875])),
                  self.blues[1].animate.move_to(np.array([-0.5, -4, 0.875])),
                  run_time=0.9)
        self.play(self.blues[0].animate.move_to(np.array([0.5, -4, 0.875])),
                  self.blues[1].animate.move_to(np.array([3.5, -4, 0.875])),
                  run_time=0.9)
        self.play(self.blues[0].animate.move_to(np.array([-1.5, -1, 0.875])),
                  self.blues[1].animate.move_to(np.array([1.5, -1, 0.875])),
                  run_time=0.9)
        self.wait(1.5)
        self.outro("Sin huecos\nen el medio")


class TactikaDefense(TactikaBase):
    """Defensa paciente."""
    NARRATION = (
        "Están en la red bombardeándote? No contraataques desde el fondo, les regalas "
        "bolas fáciles. Defiende con paciencia. Los dos atrás, bajos, absorbe la presión. "
        "Y luego levanta un globo alto y profundo para sacarles de la red y resetear el "
        "punto. Sobrevive la tormenta, y el punto se vuelve a tu favor."
    )
    FACT_KEY = "distance_covered_1500m"

    def construct(self):
        from videogen.padel.academic_pool import by_key
        self.build_court(you=((-1.7, -3), (1.7, -3)), rivals=((-1.5, 2), (1.5, 2)))
        self.title_card("Bombardean la red", color=LABEL_RIVAL)
        smash = self.ball_arc_3d(start=(0, 2, 2.5), peak_z=1.0, end=(-1.5, -5, 1.5))
        ball = self.animate_ball(smash, run_time=0.6, rate=rush_into)
        self.wait(0.6)
        f = by_key(self.FACT_KEY)
        if f:
            self.academic_slide(f, hold=3.5)
        self.title_card("Baja y absorbe", color=BALL_C)
        self.play(self.blues[0].animate.move_to(np.array([-1.7, -8, 0.875])),
                  self.blues[1].animate.move_to(np.array([1.7, -8, 0.875])),
                  run_time=0.9)
        self.wait(1.2)
        self.title_card("Globo de RESET", color=LABEL_YOU)
        reset = self.ball_arc_3d(start=(0, -7.5, 1.0), peak_z=7.0, end=(0.5, 9, 0.3))
        self.play(Create(reset), MoveAlongPath(ball, reset), run_time=1.1, rate_func=linear)
        self.play(self.reds[0].animate.move_to(np.array([-1.5, 6, 0.875])),
                  self.reds[1].animate.move_to(np.array([1.5, 6, 0.875])),
                  run_time=0.9)
        self.wait(1.6)
        self.outro("Sobrevive y\ngana el punto")


# ────────────────────────── REGISTRO ──────────────────────────

TACTIKA_TACTICS = {
    "lob":         {"scene": "TactikaLob",         "title": "El Globo"},
    "back_wall":   {"scene": "TactikaBackWall",    "title": "Bajada de Pared"},
    "bandeja":     {"scene": "TactikaBandeja",     "title": "La Bandeja"},
    "smash":       {"scene": "TactikaSmash",       "title": "Remate por Tres"},
    "drop_shot":   {"scene": "TactikaDrop",        "title": "La Dejada"},
    "serve":       {"scene": "TactikaServe",       "title": "El Saque"},
    "positioning": {"scene": "TactikaPositioning", "title": "Posición"},
    "defense":     {"scene": "TactikaDefense",     "title": "Defensa"},
}


def narration_for(scene_name: str) -> str:
    return globals()[scene_name].NARRATION
