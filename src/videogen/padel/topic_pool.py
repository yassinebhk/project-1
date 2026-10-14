"""Padel Pro (EN) — consejos de pádel narrados sobre METRAJE REAL (Pexels).
Sin diagramas: el pipeline narrado fetchea clips reales de pádel por visual_keywords.
Cada topic = 1 consejo (subject curado para exactitud). Cooldown 90d."""
from __future__ import annotations


TOPICS = [
    {"key": "lob", "titulo": "The lob that wins the net back",
     "hook": "Getting passed at the net? Do this.",
     "subject": "When opponents take the net, lift a high, deep lob toward the back glass. "
                "It pushes them back and lets you recover the net. Aim deep, not hard."},
    {"key": "bandeja", "titulo": "Stop smashing — hit the bandeja",
     "hook": "You smash everything and lose the point?",
     "subject": "The bandeja is a controlled slice overhead: keep it low and deep, "
                "stay at the net instead of a risky flat smash. Control beats power."},
    {"key": "back_wall", "titulo": "Play off the back glass like a pro",
     "hook": "Scared of the back wall?",
     "subject": "Let the ball pass you, bounce, come off the glass and drop. Wait, turn side-on, "
                "and guide it deep with control. Patience, not power."},
    {"key": "positioning", "titulo": "Move as a pair",
     "hook": "You and your partner out of sync?",
     "subject": "Move together as if tied by a short rope. When one goes, the other follows. "
                "Cover the middle and close the gaps between you."},
    {"key": "por_tres", "titulo": "The out-of-court smash",
     "hook": "The most spectacular shot in padel.",
     "subject": "The por-tres: smash the ball so it bounces hard and flies out over the back fence. "
                "Hit up and through with a fast wrist. If it leaves the court, point won."},
    {"key": "serve", "titulo": "The smart serve",
     "hook": "Serving to win the point? Wrong.",
     "subject": "The serve is to win the net, not the point. Serve into the side wall to make the "
                "return awkward, then move up to the net with your partner immediately."},
    {"key": "drop_shot", "titulo": "The drop shot",
     "hook": "Rivals glued to the back wall?",
     "subject": "With soft hands, drop the ball short just over the net when opponents are deep. "
                "It breaks their rhythm and forces a weak reply."},
    {"key": "defense", "titulo": "Defend the smash",
     "hook": "Getting smashed on every point?",
     "subject": "Split-step, stay low, and block deep rather than swinging big. Use the side and "
                "back walls to buy time, and wait for your chance to lob and reset."},

    # ───── FACT (curiosidades + histórico + dimensiones) ─────
    {"key": "history_1969", "format": "fact",
     "titulo": "The origin of padel",
     "kicker": "DID YOU KNOW?",
     "title": "Padel was born\nin a backyard",
     "lines": ["Invented in 1969 in Acapulco, Mexico",
               "By Enrique Corcuera — no room for a tennis court",
               "So he walled in a smaller one"],
     "punch": "Now played in 90+ countries",
     "cite": "International Padel Federation (FIP)"},
    {"key": "court_size", "format": "fact",
     "titulo": "The exact size of a padel court",
     "kicker": "COURT GEOMETRY",
     "title": "20 by 10 meters",
     "lines": ["Length: exactly 20 meters",
               "Width: exactly 10 meters",
               "Walls: 3 or 4 meters high (glass + mesh)"],
     "punch": "Half the size of tennis",
     "cite": "FIP Padel Rules — 2024"},
    {"key": "net_heights", "format": "fact",
     "titulo": "The net is lower in the middle on purpose",
     "kicker": "NET DIFFERENCE",
     "title": "88 vs 92",
     "lines": ["88 cm high at the center",
               "92 cm high at the posts",
               "Favors crosscourt rallies — physics of the dip"],
     "punch": "Hit middle = less margin",
     "cite": "FIP Rulebook, Rule 7"},
    {"key": "spain_argentina", "format": "fact",
     "titulo": "Why Spain and Argentina rule padel",
     "kicker": "WHO WINS?",
     "title": "Two countries\ndominate",
     "lines": ["Spain hosts 70%+ of pro tournaments",
               "Argentina trained early-era legends (Belasteguín, Lima)",
               "Together: 90%+ of all WPT/Premier titles since 2000"],
     "punch": "The duopoly of padel",
     "cite": "Premier Padel + WPT historical standings"},

    # ───── COMPARE (grips + palas) ─────
    {"key": "racket_shapes", "format": "compare",
     "titulo": "Round vs Teardrop vs Diamond — which padel racket?",
     "kicker": "WHICH RACKET?",
     "title": "Round vs Teardrop vs Diamond",
     "items": [{"name": "ROUND", "shape": "round"},
               {"name": "TEARDROP", "shape": "teardrop"},
               {"name": "DIAMOND", "shape": "diamond"}],
     "attrs": [{"label": "Control", "values": [95, 70, 45]},
               {"label": "Power", "values": [45, 70, 95]},
               {"label": "Forgiveness", "values": [95, 65, 40]}],
     "punch": "Round = control\nDiamond = power",
     "cite": "Padel racket manufacturer specs"},
    {"key": "grip_types", "format": "compare",
     "titulo": "Continental vs Eastern vs Western — which padel grip?",
     "kicker": "WHICH GRIP?",
     "title": "Continental vs Eastern vs Western",
     "items": [{"name": "CONTINENTAL", "shape": "round"},
               {"name": "EASTERN", "shape": "teardrop"},
               {"name": "WESTERN", "shape": "diamond"}],
     "attrs": [{"label": "Versatility", "values": [95, 70, 40]},
               {"label": "Topspin",     "values": [45, 65, 95]},
               {"label": "Volley ease", "values": [95, 60, 25]}],
     "punch": "Padel = continental\nEverything from one grip",
     "cite": "USPTA Padel Coaching Guide"},

    # ───── CHECKLIST (errores + rutinas) ─────
    {"key": "beginner_mistakes", "format": "checklist",
     "titulo": "3 mistakes killing your padel game",
     "kicker": "BEGINNER FIXES",
     "title": "3 mistakes killing\nyour game",
     "tips": ["Stop smashing everything — control beats power",
              "Get out of no man's land — net or back, never the middle",
              "Use the walls — let the ball rebound, don't fear it"],
     "punch": "Fix these and you'll\njump a level fast",
     "cite": "Common coaching advice"},
    {"key": "warmup_routine", "format": "checklist",
     "titulo": "The 3-minute padel warm-up every player skips",
     "kicker": "WARM-UP",
     "title": "3 minutes = better game\n+ no injuries",
     "tips": ["Shoulder mobility circles — both directions, 30 seconds",
              "Side-to-side lunges — mimic match footwork",
              "Mini-rally close to the net — gradually step back"],
     "punch": "Three minutes saves\nyour whole match",
     "cite": "Sports medicine basics"},
]


def all_topics() -> list[dict]:
    return list(TOPICS)


def by_key(key: str):
    for t in TOPICS:
        if t["key"] == key:
            return t
    return None
