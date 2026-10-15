"""Catálogo de la tanda 02/10 — canales narrados nuevos (pre-cableados) sobre
`simple_channel`. Cada uno = 1 SimpleChannelConfig + su system prompt en prompts/.

Elegidos tras deep-research (3 estudios): encajan con faceless + coste cero +
veracidad + no-YMYL, y la purga de AI-slop premia la fuente citada. Todos ES salvo
nota (ES = menos competencia + infra propia). Geo-quiz (EN) va aparte (generador
propio). Ver [[stoic-mind-nuevo-canal]].
"""
from __future__ import annotations

from .simple_channel import SimpleChannelConfig

_SRC = "— cita SIEMPRE una fuente real y verificable en pantalla (el hecho concreto)."

# ───────────────────────── 1) Enigmas / misterios documentados (ES) ─────────────────────────
# Dedup DURO vs WaitWhy: NADA de crimen. Solo historia/arqueología/exploración/ciencia
# sin resolver, documentada. [[waitwhy-contaminacion-fallback-yt]]
MISTERIOS = SimpleChannelConfig(
    slug="misterios", prefix="YT_MISTERIOS", display_name="Enigmas sin Resolver",
    platform_key="youtube_misterios", lang="es", system_prompt_file="batch_es_system.md",
    tone="suspense documental, sobrio e intrigante; nunca sensacionalista ni pseudociencia",
    category_id="27", emoji="🗿", cross_teaser="🗿 Enigma sin resolver",
    theme_desc=("A Spanish faceless channel about REAL, documented unsolved mysteries of "
                "history, archaeology and exploration (NOT crime): lost cities, ancient "
                "artifacts, unexplained-but-sourced events, disappearances of expeditions."),
    veracity_rules=("- Only REAL documented cases with a citable source. NEVER invent details, "
                    "dates or 'facts'. If a popular theory is debunked, say so. No crime cases."),
    seed=[
        {"key": "antikythera", "titulo": "El mecanismo de Anticitera: un ordenador de hace 2000 años",
         "hook": "En un naufragio griego encontraron un engranaje imposible para su época.",
         "angle": "El mecanismo de Anticitera (~150-100 a.C.), calculaba posiciones astronómicas; fuente: Museo Arqueológico Nacional de Atenas / estudios Nature.",
         "visual": "engranajes de bronce corroídos, mar egeo, museo oscuro"},
        {"key": "gobekli_tepe", "titulo": "Göbekli Tepe: el templo que reescribió la historia",
         "hook": "Es 6000 años más antiguo que Stonehenge y no debería existir.",
         "angle": "Göbekli Tepe (~9600 a.C.) desafía la idea de que la agricultura precede a los templos; fuente: Instituto Arqueológico Alemán (DAI).",
         "visual": "pilares de piedra en T, excavación, atardecer en Anatolia"},
        {"key": "nazca", "titulo": "Las líneas de Nazca: ¿para quién se dibujaron?",
         "hook": "Solo se ven completas desde el cielo. Y nadie podía volar.",
         "angle": "Geoglifos de Nazca (~500 a.C.-500 d.C.), función aún debatida (agua/astronomía/ritual); fuente: UNESCO / líneas y geoglifos de Nazca.",
         "visual": "desierto peruano, geoglifo del colibrí, vista aérea"},
        {"key": "voynich", "titulo": "El manuscrito Voynich: el libro que nadie sabe leer",
         "hook": "600 años y ni los mejores criptógrafos lo han descifrado.",
         "angle": "Manuscrito Voynich (datado ~s.XV por carbono-14), idioma/sistema sin descifrar; fuente: Biblioteca Beinecke, Universidad de Yale.",
         "visual": "páginas de pergamino con escritura extraña, plantas dibujadas, biblioteca antigua"},
        {"key": "tunguska", "titulo": "Tunguska: la explosión que arrasó un bosque sin cráter",
         "hook": "En 1908 algo tumbó 80 millones de árboles. No dejó cráter.",
         "angle": "Evento de Tunguska (1908), probable explosión de un bólido en el aire; fuente: NASA / estudios sobre el evento.",
         "visual": "bosque siberiano derribado radialmente, cielo rojo, taiga"},
        {"key": "wow_signal", "titulo": "La señal Wow!: 72 segundos desde el espacio",
         "hook": "Un radiotelescopio captó una señal tan fuerte que el astrónomo escribió 'Wow!'.",
         "angle": "Señal Wow! (1977, telescopio Big Ear), origen aún no confirmado ni repetido; fuente: Universidad Estatal de Ohio / SETI.",
         "visual": "radiotelescopio nocturno, impresión con '6EQUJ5', cielo estrellado"},
        {"key": "mary_celeste", "titulo": "Mary Celeste: el barco hallado intacto y sin tripulación",
         "hook": "Comida en la mesa, carga intacta, y ni un alma a bordo.",
         "angle": "Mary Celeste (1872), tripulación desaparecida sin explicación confirmada; fuente: archivos marítimos / Smithsonian.",
         "visual": "velero a la deriva, mar en calma, camarote vacío"},
        {"key": "fawcett_z", "titulo": "La ciudad perdida de Z y la desaparición de Fawcett",
         "hook": "Un explorador entró en el Amazonas buscando una ciudad. No volvió.",
         "angle": "Percy Fawcett desapareció en 1925 buscando 'Z'; hallazgos recientes (Kuhikugu) sugieren urbanismo amazónico real; fuente: Royal Geographical Society.",
         "visual": "selva amazónica densa, mapa antiguo, niebla sobre el río"},
        {"key": "rapa_nui_moai", "titulo": "Moái de Pascua: cómo 'caminaron' estatuas de 80 toneladas",
         "hook": "Movieron estatuas gigantes sin ruedas ni grúas. ¿Cómo?",
         "angle": "Transporte de los moái de Rapa Nui; experimentos (Lipo/Hunt) muestran que pudieron 'caminar' balanceándolas con cuerdas; fuente: Journal of Archaeological Science.",
         "visual": "moáis en fila, cantera Rano Raraku, costa de Pascua"},
    ],
)

# ───────────────────────── 2) Sesgos cognitivos / modelos mentales (ES) ─────────────────────────
SESGOS = SimpleChannelConfig(
    slug="sesgos", prefix="YT_SESGOS", display_name="Mente Racional",
    platform_key="youtube_sesgos", lang="es", system_prompt_file="batch_es_system.md",
    tone="didáctico, claro y cercano; como un amigo listo que te revela cómo te engaña tu mente",
    category_id="27", emoji="🧠", cross_teaser="🧠 Sesgo cognitivo",
    to_tiktok=False, to_ig=True,  # IG sí; TikTok NO (06/10: foco TikTok solo what-if)
    ig_hashtags=["psicologia", "sesgoscognitivos", "mente", "aprende", "curiosidades", "shorts"],
    longform=True, shorts_per_day=1,  # user 03/10: + long-form 1×/sem, cap 1 short/día
    theme_desc=("A Spanish faceless channel explaining ONE cognitive bias / mental model per "
                "video, grounded in real behavioral science (Kahneman, Tversky, Ariely, etc.)."),
    veracity_rules=("- Each bias MUST trace to named, real research (e.g. Kahneman & Tversky). "
                    "Cite it. NO pop-psychology, NO 'dark psychology', NO manipulation claims, "
                    "NO unfalsifiable 'facts'."),
    seed=[
        {"key": "anchoring", "titulo": "El efecto ancla: por qué el primer número te manipula",
         "hook": "Te enseñan un precio altísimo primero… y ya has caído.",
         "angle": "Anclaje (Tversky & Kahneman, 1974): la primera cifra sesga estimaciones posteriores; cómo contrarrestarlo.",
         "visual": "balanza, etiquetas de precio, cerebro ilustrado minimal"},
        {"key": "loss_aversion", "titulo": "Aversión a la pérdida: perder duele el doble que ganar",
         "hook": "Perder 100€ duele más de lo que alegra ganarlos. No es casualidad.",
         "angle": "Aversión a la pérdida (Kahneman & Tversky, teoría prospectiva, 1979): las pérdidas pesan ~2x; ejemplos cotidianos.",
         "visual": "balanza desnivelada, billetes, gráfico de utilidad"},
        {"key": "sunk_cost", "titulo": "La falacia del coste hundido: por qué no sabes rendirte",
         "hook": "Sigues con algo malo solo porque ya invertiste en ello.",
         "angle": "Falacia del coste hundido: decidir por lo ya gastado en vez del valor futuro; cómo detectarla.",
         "visual": "entrada de cine rota, reloj, persona dudando"},
        {"key": "confirmation", "titulo": "Sesgo de confirmación: solo ves lo que ya crees",
         "hook": "Tu cerebro busca pruebas de lo que ya piensas e ignora el resto.",
         "angle": "Sesgo de confirmación (Wason, 1960): buscamos info que confirma creencias; cómo romperlo.",
         "visual": "lupa, burbuja, piezas de puzzle que no encajan"},
        {"key": "dunning_kruger", "titulo": "Dunning-Kruger: por qué los que menos saben se creen expertos",
         "hook": "Cuanto menos sabes de algo, más crees que lo dominas.",
         "angle": "Efecto Dunning-Kruger (1999): baja competencia → sobreestimación; y el reverso en expertos.",
         "visual": "montaña con pico y valle, gráfico confianza vs conocimiento"},
        {"key": "availability", "titulo": "Heurística de disponibilidad: por qué temes lo improbable",
         "hook": "Temes al avión y no al coche. Tu memoria te engaña.",
         "angle": "Heurística de disponibilidad (Tversky & Kahneman): juzgamos probabilidad por lo fácil que viene a la mente.",
         "visual": "titulares de prensa, avión, cerebro con focos"},
        {"key": "survivorship", "titulo": "Sesgo del superviviente: los aviones de la Segunda Guerra",
         "hook": "Reforzaron los aviones donde NO tenían agujeros. ¿Por qué acertaron?",
         "angle": "Sesgo del superviviente (Abraham Wald, SRG): solo vemos a los que 'sobreviven'; el caso de los bombarderos.",
         "visual": "diagrama de bombardero con impactos, hangar, blueprint"},
        {"key": "halo_effect", "titulo": "Efecto halo: por qué lo guapo te parece competente",
         "hook": "Si alguien es atractivo, le atribuyes talento sin pruebas.",
         "angle": "Efecto halo (Thorndike, 1920): un rasgo positivo contamina el juicio global; en entrevistas y marcas.",
         "visual": "retrato con halo de luz, currículums, foco"},
        {"key": "framing", "titulo": "Efecto marco: '90% sin grasa' vs '10% de grasa'",
         "hook": "Es el mismo dato. Pero uno te lo compras y el otro no.",
         "angle": "Efecto marco (Tversky & Kahneman): la forma de presentar la info cambia la decisión; ejemplos de salud y compra.",
         "visual": "dos etiquetas idénticas con texto distinto, carrito, cerebro"},
    ],
)

# ───────────────────────── 3) Filosofía profunda (ES) — distinta de Stoic Mind ─────────────────────────
FILOSOFIA = SimpleChannelConfig(
    slug="filosofia", prefix="YT_FILOSOFIA", display_name="Abismo",
    platform_key="youtube_filosofia", lang="es", system_prompt_file="batch_es_system.md",
    tone="contemplativo, profundo y cinematográfico; nada de autoayuda barata ni frases de calendario",
    category_id="27", emoji="🕯️", cross_teaser="🕯️ Filosofía",
    theme_desc=("A Spanish faceless channel on DEPTH philosophy — Jung, Nietzsche, Schopenhauer, "
                "Camus, Kierkegaard, Plato — applied to the human condition. DISTINCT from a "
                "stoicism channel: focus on depth-psychology and existentialism, not Stoic quotes."),
    veracity_rules=("- Attribute ideas to the right philosopher and their real work (e.g. Jung "
                    "'Aion', Nietzsche 'Thus Spoke Zarathustra'). Explain the idea in your own "
                    "words; do NOT fabricate verbatim quotes. No self-help pseudoscience."),
    seed=[
        {"key": "jung_shadow", "titulo": "La sombra de Jung: lo que escondes te gobierna",
         "hook": "Lo que más odias en otros suele ser lo que niegas en ti.",
         "angle": "La 'sombra' de Jung: los rasgos reprimidos del inconsciente; integrarla, no negarla (obra: Aion).",
         "visual": "silueta y sombra, espejo oscuro, figura entre niebla"},
        {"key": "nietzsche_eternal", "titulo": "El eterno retorno de Nietzsche: ¿repetirías tu vida?",
         "hook": "¿Y si tuvieras que vivir tu vida idéntica, infinitas veces?",
         "angle": "El eterno retorno (Nietzsche, 'La gaya ciencia'): prueba para vivir de forma que aceptarías repetirlo todo.",
         "visual": "reloj circular, desierto infinito, estrellas en bucle"},
        {"key": "schopenhauer_desire", "titulo": "Schopenhauer: por qué conseguir lo que quieres no te llena",
         "hook": "Logras lo que deseabas… y a los días vuelves a estar vacío.",
         "angle": "Schopenhauer ('El mundo como voluntad y representación'): el deseo oscila entre dolor y aburrimiento.",
         "visual": "péndulo, habitación vacía, mar gris"},
        {"key": "camus_sisyphus", "titulo": "Camus y Sísifo: cómo ser feliz en lo absurdo",
         "hook": "Empuja una roca que siempre vuelve a caer. Y aun así sonríe.",
         "angle": "Camus ('El mito de Sísifo'): el absurdo no se resuelve, se rebela uno viviéndolo plenamente.",
         "visual": "figura empujando roca montaña, atardecer, cumbre"},
        {"key": "plato_cave", "titulo": "La caverna de Platón: ¿y si solo ves sombras?",
         "hook": "Encadenados desde niños, creen que las sombras son el mundo.",
         "angle": "La alegoría de la caverna (Platón, 'La República'): percepción vs realidad; el precio de salir.",
         "visual": "cueva con fuego, sombras en la pared, luz cegadora en la salida"},
        {"key": "kierkegaard_anxiety", "titulo": "Kierkegaard: la angustia es el vértigo de la libertad",
         "hook": "La angustia no es miedo a algo: es el vértigo de poder elegir.",
         "angle": "Kierkegaard ('El concepto de la angustia'): la libertad genera angustia; qué hacer con ella.",
         "visual": "borde de acantilado, encrucijada, cielo abierto"},
        {"key": "nietzsche_become", "titulo": "'Llega a ser el que eres' — Nietzsche explicado",
         "hook": "No eres una copia. Pero vives como si lo fueras.",
         "angle": "Nietzsche ('Así habló Zaratustra'): convertirse en uno mismo frente al rebaño; autosuperación.",
         "visual": "figura ascendiendo, águila, montaña al amanecer"},
        {"key": "jung_persona", "titulo": "La 'persona' de Jung: la máscara que crees que eres",
         "hook": "Enseñas una máscara tantas horas que olvidas quitártela.",
         "angle": "La 'persona' de Jung: la máscara social; el peligro de identificarte con ella.",
         "visual": "máscara teatral, rostro difuminado, foco de escenario"},
    ],
)

# ───────────────────────── 4) ¿Qué pasaría si? / curiosidades (ES) ─────────────────────────
CURIOSIDADES = SimpleChannelConfig(
    slug="curiosidades", prefix="YT_CURIOSIDADES", display_name="¿Qué Pasaría Si?",
    platform_key="youtube_curiosidades", lang="es", system_prompt_file="batch_es_system.md",
    tone="curioso y energético, divulgativo; asombro con rigor científico",
    category_id="27", emoji="🤔", cross_teaser="🤔 ¿Qué pasaría si…",
    shorts_per_day=2,  # 06/10: es el formato GANADOR en YouTube (628 views/vid, 2.3% eng)
    to_tiktok=False,  # 06/10: TikTok pasa a GeoQuiz (formato #1 TikTok, sin voz); what-if = solo YouTube
    theme_desc=("A Spanish faceless channel of 'what if' hypotheticals and surprising facts, "
                "GROUNDED IN REAL SCIENCE (physics, biology, astronomy). The hypothetical is the "
                "hook; the payoff is real science."),
    veracity_rules=("- The scenario can be hypothetical, but the SCIENCE explaining it must be real "
                    "and citable. NEVER present fiction as fact. Non-YMYL (no medical scenarios "
                    "framed as advice)."),
    seed=[
        {"key": "earth_stop", "titulo": "¿Qué pasaría si la Tierra dejara de girar?",
         "hook": "Si la Tierra se parase de golpe, seguirías moviéndote a 1600 km/h.",
         "angle": "Inercia: a 0° la superficie gira ~1670 km/h; parada súbita = catástrofe; física real (NASA).",
         "visual": "Tierra desde el espacio, vientos huracanados, atmósfera"},
        {"key": "no_moon", "titulo": "¿Qué pasaría si desapareciera la Luna?",
         "hook": "Sin Luna, los días se acortarían y el eje de la Tierra bailaría.",
         "angle": "La Luna estabiliza el eje terrestre y genera mareas; su ausencia alteraría clima y rotación (fuente: NASA).",
         "visual": "luna llena, mareas, eje terrestre inclinado"},
        {"key": "everyone_jump", "titulo": "¿Qué pasaría si todos saltáramos a la vez?",
         "hook": "8000 millones saltando juntos… ¿movemos la Tierra?",
         "angle": "La masa humana es ínfima frente a la Tierra: el efecto es despreciable; cálculo físico real.",
         "visual": "multitud saltando, planeta, flechas de fuerza"},
        {"key": "black_hole_fall", "titulo": "¿Qué pasaría si cayeras en un agujero negro?",
         "hook": "Te estirarías como un espagueti. Tiene nombre científico.",
         "angle": "'Espaguetización' por gradiente de marea; dilatación temporal cerca del horizonte (relatividad general).",
         "visual": "agujero negro, disco de acreción, estrellas curvadas"},
        {"key": "light_speed", "titulo": "¿Qué pasaría si viajaras a la velocidad de la luz?",
         "hook": "Para ti el tiempo casi se detendría frente al resto del universo.",
         "angle": "Dilatación del tiempo (relatividad especial); por qué ningún objeto con masa la alcanza.",
         "visual": "nave estelar, estrellas en líneas, reloj deformado"},
        {"key": "sun_disappear", "titulo": "¿Qué pasaría si el Sol desapareciera ahora?",
         "hook": "Lo verías 8 minutos más. La gravedad también tardaría.",
         "angle": "La luz del Sol tarda ~8 min 20 s; la Tierra saldría despedida en línea recta (fuente: NASA).",
         "visual": "sol, sistema solar, oscuridad progresiva"},
        {"key": "no_insects", "titulo": "¿Qué pasaría si desaparecieran los insectos?",
         "hook": "Sin insectos, la cadena alimentaria se derrumba en meses.",
         "angle": "Polinización y descomposición dependen de insectos; colapso ecológico documentado (estudios de biodiversidad).",
         "visual": "abeja en flor, campo, ecosistema"},
        {"key": "deepest_hole", "titulo": "¿Qué pasaría si cavaras hasta el centro de la Tierra?",
         "hook": "El pozo más profundo jamás cavado no llega ni al 0,2% del camino.",
         "angle": "Kola Superdeep (~12,2 km) vs radio terrestre (~6371 km); calor y presión lo impiden (fuente: proyecto Kola).",
         "visual": "corte de la Tierra por capas, taladro, magma"},
    ],
)

# ───────────────────────── 5) Espacio / universo (ES) ─────────────────────────
ESPACIO = SimpleChannelConfig(
    slug="espacio", prefix="YT_ESPACIO", display_name="Cosmos",
    platform_key="youtube_espacio", lang="es", system_prompt_file="batch_es_system.md",
    tone="asombro cósmico, evocador y divulgativo; datos reales que dejan sin palabras",
    category_id="27", emoji="🪐", cross_teaser="🪐 Cosmos",
    theme_desc=("A Spanish faceless channel of astronomy & space facts — scale of the universe, "
                "stars, black holes, planets — using real data and NASA/ESA public-domain imagery."),
    veracity_rules=("- Only real, current astronomy from citable sources (NASA, ESA, peer-reviewed). "
                    "No astrology, no aliens-as-fact, no speculation presented as established."),
    seed=[
        {"key": "neutron_star", "titulo": "Una cucharada de estrella de neutrones pesa como una montaña",
         "hook": "Una cucharadita de esta estrella pesaría mil millones de toneladas.",
         "angle": "Densidad de las estrellas de neutrones (~10^17 kg/m³); restos de supernovas (fuente: NASA).",
         "visual": "estrella de neutrones, púlsar girando, campo estelar"},
        {"key": "venus_day", "titulo": "En Venus, un día dura más que un año",
         "hook": "Venus gira tan lento que su día supera a su año.",
         "angle": "Rotación de Venus ~243 días terrestres vs órbita ~225 días (fuente: NASA planetary fact sheet).",
         "visual": "Venus nublado, órbita, sol"},
        {"key": "voyager", "titulo": "La Voyager 1: el objeto humano más lejano",
         "hook": "Lanzada en 1977, ya está fuera del sistema solar.",
         "angle": "Voyager 1 en el espacio interestelar desde 2012, a >24.000 millones de km (fuente: NASA/JPL).",
         "visual": "sonda Voyager, disco dorado, espacio profundo"},
        {"key": "olympus_mons", "titulo": "Olympus Mons: un volcán 3 veces el Everest",
         "hook": "El volcán más alto conocido está en Marte y es colosal.",
         "angle": "Olympus Mons ~22 km de altura (~2,5x Everest); fuente: NASA/USGS Marte.",
         "visual": "Marte rojo, volcán gigante, superficie marciana"},
        {"key": "scream_space", "titulo": "¿Por qué no se puede gritar en el espacio?",
         "hook": "En el espacio nadie te oiría. Y hay una razón física.",
         "angle": "El sonido necesita un medio; el vacío no propaga ondas sonoras (física básica, fuente: NASA).",
         "visual": "astronauta en el vacío, ondas, estrellas"},
        {"key": "light_delay_sun", "titulo": "El Sol que ves es el Sol de hace 8 minutos",
         "hook": "Si el Sol se apagara, lo seguirías viendo 8 minutos.",
         "angle": "La luz tarda ~8 min 20 s en llegar del Sol; para estrellas lejanas, años (fuente: NASA).",
         "visual": "sol, rayo de luz, reloj, Tierra"},
        {"key": "universe_scale", "titulo": "Si el Sol fuera una pelota, la Tierra sería un grano",
         "hook": "La escala del universo es tan brutal que el cerebro no la procesa.",
         "angle": "Escala del sistema solar y distancias (años luz); comparación a escala (fuente: NASA).",
         "visual": "modelo a escala planetas, vía láctea, cosmos"},
        {"key": "rogue_planets", "titulo": "Planetas errantes: mundos sin estrella vagando a oscuras",
         "hook": "Hay planetas que no orbitan ninguna estrella. Vagan solos.",
         "angle": "Planetas errantes expulsados de sus sistemas, miles de millones posibles (fuente: NASA/estudios).",
         "visual": "planeta oscuro solitario, campo estelar, nebulosa"},
    ],
)


# ───────────────────────── 6) Datos Increíbles (ES) — reconvierte IA Autónomos ─────────────────────────
# 06/10: IA Autónomos (muerto, eng 0,6%) → curiosidades/ciencia tipo "amazing facts"
# (formato Zack D. Films, 2º canal de curiosidad tras el éxito del what-if). REUTILIZA
# el canal YT_IA ya autorizado (sin reauth; el usuario solo renombra el canal en Studio).
DATOS = SimpleChannelConfig(
    slug="datos", prefix="YT_IA", display_name="Datos Increíbles",
    platform_key="youtube_ia", lang="es", system_prompt_file="batch_es_system.md",
    tone="asombroso y divulgativo; un dato que deja loco pero 100% verificable",
    category_id="27", emoji="🤯", cross_teaser="🤯 Dato increíble", shorts_per_day=1,
    theme_desc=("A Spanish faceless channel of ONE amazing-but-true fact per short "
                "(science, history, nature, the human body, physics) — the 'did you "
                "know?!' format. NOT hypotheticals (that's another channel), NOT only space."),
    veracity_rules=("- Each fact MUST be real and citable (source on screen). NO myths, "
                    "NO exaggeration, NO 'facts' that are debunked urban legends."),
    seed=[
        {"key": "octopus_hearts", "titulo": "Los pulpos tienen 3 corazones (y sangre azul)",
         "hook": "Un pulpo tiene TRES corazones. Y su sangre es azul.",
         "angle": "2 corazones branquiales + 1 sistémico; sangre con hemocianina (cobre) = azul. Fuente: biología marina.",
         "visual": "pulpo nadando, primer plano tentáculos, océano profundo"},
        {"key": "honey_never", "titulo": "La miel nunca caduca: se ha comido miel de 3000 años",
         "hook": "Arqueólogos comieron miel de 3000 años… y estaba perfecta.",
         "angle": "Baja humedad + pH ácido + peróxido impiden bacterias; miel comestible en tumbas egipcias. Fuente: Smithsonian.",
         "visual": "miel goteando, tarro, tumba egipcia dorada"},
        {"key": "trees_vs_stars", "titulo": "Hay más árboles en la Tierra que estrellas en la Vía Láctea",
         "hook": "La Tierra tiene más árboles que estrellas nuestra galaxia.",
         "angle": "~3 billones de árboles (estudio Nature 2015) vs 100-400 mil millones de estrellas en la Vía Láctea.",
         "visual": "bosque infinito aéreo, vía láctea, comparación"},
        {"key": "lightning_hotter", "titulo": "Un rayo es 5 veces más caliente que la superficie del Sol",
         "hook": "Un rayo alcanza 5× la temperatura de la superficie del Sol.",
         "angle": "Rayo ~30.000 °C vs superficie solar ~5.500 °C. Fuente: NOAA/física atmosférica.",
         "visual": "rayo cayendo, tormenta, sol"},
        {"key": "cleopatra_time", "titulo": "Cleopatra vivió más cerca del iPhone que de las pirámides",
         "hook": "Cleopatra está más cerca en el tiempo de ti que de las pirámides.",
         "angle": "Pirámide de Guiza ~2560 a.C.; Cleopatra ~30 a.C.; iPhone 2007. La diferencia lo confirma.",
         "visual": "pirámides, busto de Cleopatra, línea temporal"},
        {"key": "banana_radioactive", "titulo": "Los plátanos son (un poco) radiactivos",
         "hook": "Te comes algo radiactivo casi cada día: el plátano.",
         "angle": "Potasio-40 natural emite radiación mínima; existe la 'dosis banana' como unidad informal. Fuente: física nuclear.",
         "visual": "plátano, símbolo radiactivo suave, cocina"},
        {"key": "body_bacteria", "titulo": "Tienes tantas bacterias como células humanas",
         "hook": "La mitad de 'tú' no es humano: son bacterias.",
         "angle": "Ratio ~1:1 bacterias:células humanas (revisión Sender et al., 2016). No eres solo tú.",
         "visual": "microbioma ilustración, intestino, bacterias"},
        {"key": "blue_whale_heart", "titulo": "El corazón de una ballena azul pesa como un coche",
         "hook": "El corazón de la ballena azul pesa como un coche pequeño.",
         "angle": "~180 kg; late tan fuerte que se detectaría a kilómetros. Fuente: ROM / biología.",
         "visual": "ballena azul, océano, escala con coche"},
        {"key": "everest_base", "titulo": "El Everest NO es la montaña más alta (medida desde la base)",
         "hook": "El Everest es el más ALTO, pero no la montaña más grande.",
         "angle": "Mauna Kea mide ~10.200 m desde su base submarina vs Everest 8.849 m sobre el mar. Fuente: USGS.",
         "visual": "Everest nevado, Mauna Kea, corte del océano"},
        {"key": "eiffel_summer", "titulo": "La Torre Eiffel crece 15 cm en verano",
         "hook": "La Torre Eiffel es más alta en verano que en invierno.",
         "angle": "El hierro se dilata con el calor → ~15 cm más alta en verano. Fuente: física de materiales.",
         "visual": "Torre Eiffel, sol de verano, termómetro"},
    ],
)


# ───────────────────────── 7) Estafas y seguridad online (ES) ─────────────────────────
# Dedup vs WaitWhy: NO corrupción política; aquí estafas/ciberfraude MODERNOS, enfoque
# defensivo (cómo funciona + cómo protegerte). Fuentes: INCIBE/OSI/Policía/INTERPOL.
SCAMS = SimpleChannelConfig(
    slug="scams", prefix="YT_SCAMS", display_name="Alerta Estafas",
    platform_key="youtube_scams", lang="es", system_prompt_file="batch_es_system.md",
    tone="divulgación de seguridad: directo y útil, cómo funciona la estafa y cómo protegerte; sin alarmismo ni culpar a personas concretas",
    category_id="27", emoji="🚨", cross_teaser="🚨 Alerta estafa", refresh_interval_days=10,
    theme_desc=("A Spanish faceless channel explaining how modern scams and cyber-fraud work "
                "and how to protect yourself: phishing, pig-butchering, SIM-swap, vishing, "
                "QR/quishing, fake tech support, romance scams, OTP social engineering. "
                "Defensive/educational, never a how-to-commit."),
    veracity_rules=("- Only REAL, documented scam mechanics with a citable source (INCIBE, OSI, "
                    "Policía/Guardia Civil, INTERPOL, bank advisories). Defensive framing ONLY: "
                    "how it works + how to protect yourself. NEVER instructions to commit fraud. "
                    "Do NOT accuse named people/companies. No financial advice."),
    seed=[
        {"key": "phishing", "titulo": "Cómo un email de phishing vacía tu cuenta en 2 minutos",
         "hook": "Ese correo de 'tu banco' no es de tu banco.",
         "angle": "Phishing: suplantan a una entidad para robar credenciales; señales: urgencia, enlace falso, dominio raro. Fuente: INCIBE/OSI.",
         "visual": "email falso de banco, candado roto, cursor sobre enlace sospechoso"},
        {"key": "pig_butchering", "titulo": "La estafa del 'cerdo cebado': amor y cripto",
         "hook": "Te enamoran durante semanas. Luego viene la 'inversión'.",
         "angle": "Pig butchering: relación falsa + plataforma cripto falsa con ganancias ficticias hasta que te vacían. Fuente: INTERPOL / FBI IC3.",
         "visual": "chat de móvil con corazones, gráfico cripto falso subiendo, cartera vacía"},
        {"key": "sim_swap", "titulo": "SIM swapping: cómo te roban el móvil sin tocarlo",
         "hook": "De repente te quedas sin cobertura. Es el primer síntoma.",
         "angle": "El atacante duplica tu SIM para recibir tus SMS y saltarse el 2FA. Fuente: INCIBE/OSI; usa 2FA por app, no SMS.",
         "visual": "tarjeta SIM duplicada, móvil sin señal, código 2FA interceptado"},
        {"key": "quishing", "titulo": "El QR del parquímetro que te roba la tarjeta",
         "hook": "Escaneas un QR para pagar y acabas en una web falsa.",
         "angle": "Quishing: QR manipulados que llevan a webs de pago fraudulentas. Fuente: OSI; verifica la URL tras escanear.",
         "visual": "pegatina QR sobre un parquímetro, web de pago falsa, móvil escaneando"},
        {"key": "fake_support", "titulo": "La llamada de 'soporte técnico' que te instala un ladrón",
         "hook": "'Su ordenador tiene un virus' — y te piden instalar un programa.",
         "angle": "Soporte técnico falso: te hacen instalar software de control remoto para robar. Fuente: OSI; ninguna empresa real llama así.",
         "visual": "ventana de acceso remoto, teléfono con número oculto, pantalla controlada"},
        {"key": "vishing_otp", "titulo": "Por qué nunca debes dar el código que te llega por SMS",
         "hook": "Si te piden 'el código de 6 dígitos', cuelga.",
         "angle": "Ingeniería social del OTP: te llaman fingiendo ser el banco para que cantes el código. Fuente: INCIBE; el banco nunca lo pide.",
         "visual": "SMS con código, llamada entrante 'Banco', mano dudando"},
    ],
)

# ───────────────────────── 8) AI explained / weekly (EN) ─────────────────────────
# Dedup vs AI Tools Weekly: aquí CONCEPTOS/novedades de IA (cómo funciona), no reseñas de
# herramientas. Seeds evergreen (sin fecha) para no envejecer; news en vivo vía RSS = mejora futura.
AINEWS = SimpleChannelConfig(
    slug="ainews", prefix="YT_AINEWS", display_name="AI Decoded",
    platform_key="youtube_ainews", lang="en", system_prompt_file="batch_en_system.md",
    tone="clear, concrete tech explainer; concepts + why they matter; no hype",
    category_id="28", emoji="🤖", cross_teaser="🤖 AI decoded", refresh_interval_days=7,
    theme_desc=("An English faceless channel explaining AI concepts, milestones and developments "
                "for a general audience: how LLMs work, agents, open vs closed models, context "
                "windows, hallucinations, RAG, training vs inference, AI safety. Explainers, "
                "not tool reviews."),
    veracity_rules=("- Cite the concrete source (paper, official announcement, docs). No hype or "
                    "unverified capability claims; label speculation. No financial advice "
                    "(no 'buy NVIDIA'). Explain, don't predict."),
    seed=[
        {"key": "next_token", "titulo": "How ChatGPT actually works (it just predicts the next word)",
         "hook": "It doesn't 'know' anything. It predicts one token at a time.",
         "angle": "LLMs are next-token predictors; the Transformer let this scale. Source: 'Attention Is All You Need' (Vaswani et al., 2017).",
         "visual": "text completing word by word, transformer diagram, probability bars"},
        {"key": "ai_agent", "titulo": "What an 'AI agent' really is (and why everyone builds them)",
         "hook": "A chatbot answers. An agent acts.",
         "angle": "An AI agent loops: plan → use tools → observe → repeat, to do multi-step tasks. Source: public tool-use/function-calling docs.",
         "visual": "loop diagram plan-act-observe, tool icons, terminal running"},
        {"key": "hallucination", "titulo": "Why AI confidently makes things up",
         "hook": "It's not lying. It's doing exactly what it was trained to do.",
         "angle": "Hallucinations: predicting plausible text without grounding; reduced with retrieval/citations. Source: model-provider docs + grounding research.",
         "visual": "confident wrong answer, fabricated citation, question mark"},
        {"key": "context_window", "titulo": "What a 'context window' is (the AI's short-term memory)",
         "hook": "The AI forgets everything outside its context window.",
         "angle": "Context window = max tokens attended at once; bigger = more input but more compute. Source: model-provider specs.",
         "visual": "sliding window over text, token counter, memory fading"},
        {"key": "open_vs_closed", "titulo": "Open vs closed AI models: the real difference",
         "hook": "Some AIs you can download. Others you can only rent.",
         "angle": "Open-weight models ship weights you can run; closed models are API-only. Source: official model licenses/announcements.",
         "visual": "download icon vs cloud lock, weights file, API endpoint"},
        {"key": "rag", "titulo": "The trick that stops AI from making things up (RAG)",
         "hook": "How you make AI answer from YOUR documents.",
         "angle": "Retrieval-Augmented Generation fetches relevant text and feeds it in so answers are grounded + citable. Source: RAG paper (Lewis et al., 2020).",
         "visual": "search over documents, retrieved snippets, grounded answer"},
    ],
)

# ───────────────────────── 9) Business / money breakdowns (EN) ─────────────────────────
# Cómo ganan dinero las empresas (datos públicos). NO consejo de inversión (no YMYL).
BUSINESS = SimpleChannelConfig(
    slug="business", prefix="YT_BUSINESS", display_name="Money Machines",
    platform_key="youtube_business", lang="en", system_prompt_file="batch_en_system.md",
    tone="sharp business explainer, concrete numbers from public filings; analytical, no advice",
    category_id="27", emoji="💰", cross_teaser="💰 How it profits", refresh_interval_days=14,
    theme_desc=("An English faceless channel explaining how companies and products actually make "
                "money, and why businesses rise or fall, using public financials. 'How the "
                "business works', never investment advice."),
    veracity_rules=("- Use PUBLIC data (annual reports, SEC 10-K, reputable press) and cite it on "
                    "screen. No stock tips, price targets or predictions (no YMYL). Don't assert "
                    "unproven claims about a company's intent."),
    seed=[
        {"key": "ikea_maze", "titulo": "Why IKEA is built like a maze (it makes you spend more)",
         "hook": "You can't take a shortcut in IKEA. That's on purpose.",
         "angle": "IKEA's one-way layout maximizes product exposure (the 'Gruen effect'). Source: retail-design analysis / reputable press.",
         "visual": "IKEA floor-plan arrows, showroom maze, full cart"},
        {"key": "costco_membership", "titulo": "Costco barely profits on what it sells — here's the real engine",
         "hook": "Costco makes most of its profit before you buy anything.",
         "angle": "Membership fees make up the bulk of Costco's operating income; goods sell near cost. Source: Costco annual report (10-K).",
         "visual": "membership card, warehouse aisles, receipt near cost"},
        {"key": "spotify_payout", "titulo": "Why Spotify pays artists so little per stream",
         "hook": "One stream pays a fraction of a cent. Here's why.",
         "angle": "Spotify pays ~2/3 of revenue to rights holders via a pooled pro-rata model; per-stream is tiny. Source: Spotify 'Loud & Clear' / annual report.",
         "visual": "stream counter, tiny coin, revenue pie split"},
        {"key": "printer_ink", "titulo": "Why printers are cheap but ink costs more than perfume",
         "hook": "They basically give you the printer for free.",
         "angle": "Razor-and-blades model: cheap hardware, profit on consumables (ink). Source: industry/press analysis.",
         "visual": "cheap printer price tag, expensive ink cartridge, perfume comparison"},
        {"key": "amazon_aws", "titulo": "Amazon's real money machine isn't the store — it's AWS",
         "hook": "The shopping site barely profits. The cloud carries it.",
         "angle": "AWS provides the majority of Amazon's operating income despite smaller revenue. Source: Amazon annual report (10-K) segment data.",
         "visual": "store box vs server racks, operating-income bar chart"},
        {"key": "free_apps", "titulo": "How 'free' apps actually make money off you",
         "hook": "If it's free, the product is your attention — or your data.",
         "angle": "Free apps monetize via ads, in-app purchases, subscriptions or data. Source: app-economy reports.",
         "visual": "app store 'free', ad banner, in-app purchase popup"},
    ],
)

# ───────────────────────── 10) Geography / geopolitics explainer (EN) ─────────────────────────
# Por qué el mapa es como es / por qué unos países son ricos. Evergreen, SIN conflictos vivos.
GEOGRAPHY = SimpleChannelConfig(
    slug="geography", prefix="YT_GEOGRAPHY", display_name="Map Decoded",
    platform_key="youtube_geography", lang="en", system_prompt_file="batch_en_system.md",
    tone="curious geography/economics explainer; factual, evergreen, no live conflicts or taking sides",
    category_id="27", emoji="🗺️", cross_teaser="🗺️ Map decoded", refresh_interval_days=14,
    theme_desc=("An English faceless channel explaining why the world map looks the way it does "
                "and why some places are rich or poor: geography, history, economics, climate. "
                "Evergreen; avoid live geopolitical conflicts."),
    veracity_rules=("- Factual geography/history/economics with a citable source (World Bank, UN, "
                    "Britannica, Köppen climate). Evergreen ONLY: NO live conflicts, NO taking "
                    "political sides, NO sensitive current events."),
    seed=[
        {"key": "ru_timezones", "titulo": "Why Russia has 11 time zones",
         "hook": "When it's breakfast in one part of Russia, it's already midnight in another.",
         "angle": "Russia spans ~11 time zones due to its east-west extent (~9,000 km). Source: Britannica / official time-zone data.",
         "visual": "map of Russia with time-zone bands, clocks, sunrise and sunset"},
        {"key": "netherlands_sea", "titulo": "Why the Netherlands pumped the sea out to make land",
         "hook": "They didn't find this land. They drained it.",
         "angle": "Polders reclaimed from the sea, kept dry by dikes and pumps; large areas would flood without them. Source: Dutch government / Britannica.",
         "visual": "dikes, polder grid, pumping station, sea-level line"},
        {"key": "singapore_rich", "titulo": "How Singapore got rich with almost no resources",
         "hook": "No oil, no farmland, barely any water — yet one of the richest.",
         "angle": "A strategic port plus trade, manufacturing, finance and governance drove growth. Source: World Bank GDP-per-capita data.",
         "visual": "port cranes, skyline, shipping-lane map"},
        {"key": "mercator", "titulo": "Why Africa looks small on your map (it isn't)",
         "hook": "Greenland looks as big as Africa. Africa is ~14x bigger.",
         "angle": "The Mercator projection inflates areas near the poles; Africa ~30.4M km² vs Greenland ~2.2M. Source: cartography / area figures.",
         "visual": "Mercator vs true-size overlay, Africa swallowing Greenland"},
        {"key": "canada_border", "titulo": "Why almost all Canadians live near the US border",
         "hook": "The world's 2nd-biggest country is mostly empty.",
         "angle": "Most of Canada's population lives within ~150 km of the US border, driven by climate and arable land. Source: Statistics Canada.",
         "visual": "Canada population-density map, thin southern strip, cold north"},
        {"key": "chile_shape", "titulo": "Why Chile is so absurdly long and thin",
         "hook": "~4,300 km long, ~350 km wide at most.",
         "angle": "Chile is hemmed between the Andes and the Pacific, stretching along the coast. Source: Britannica / geography.",
         "visual": "map of Chile, Andes wall, Pacific coast"},
    ],
)

# ───────────────────────── 11) True crime EN (clon de WaitWhy en inglés) ─────────────────────────
# La apuesta de mayor EV: true crime es el ÚNICO formato probado (WaitWhy flagship). En EN el
# mercado es enorme y el RPM más alto. Replica el nicho GANADOR de WaitWhy (fraude/corrupción
# económico-financiera, [[waitwhy-nicho-ganador-corrupcion-fraude-es]]) con casos internacionales
# CON SENTENCIA FIRME. Veracidad crítica (riesgo legal/difamación): solo condenas finales,
# públicas y documentadas. [[veracidad-obligatoria]]
TRUECRIME = SimpleChannelConfig(
    slug="truecrime", prefix="YT_TRUECRIME", display_name="Convicted",
    platform_key="youtube_truecrime", lang="en", system_prompt_file="batch_en_system.md",
    tone="sober true-crime narration: tense and gripping but factual, never sensationalist; the crime, the trail, the verdict",
    category_id="27", emoji="⚖️", cross_teaser="⚖️ Convicted", refresh_interval_days=10,
    theme_desc=("An English faceless true-crime channel on major financial and corporate crime: "
                "frauds, Ponzi schemes, corruption and white-collar takedowns that ended in a "
                "FINAL conviction. International, documented cases — the scheme, how it unraveled, "
                "the sentence."),
    veracity_rules=("- ONLY real cases with a FINAL conviction/sentence on public record (court "
                    "records, DOJ/SEC, reputable press). State the actual sentence and CITE the "
                    "source on screen. Name only public figures convicted in a final judgment. "
                    "NO speculation about guilt, NO unproven allegations, NO ongoing/acquitted "
                    "cases, NO private victim details, NO gore. Facts only."),
    seed=[
        {"key": "madoff", "titulo": "Bernie Madoff: the $65 billion lie that lasted decades",
         "hook": "It was the biggest Ponzi scheme in history — and it ran in plain sight.",
         "angle": "Bernie Madoff ran a ~$65B Ponzi scheme; pleaded guilty in 2009 and was sentenced to 150 years. Source: US DOJ / SEC.",
         "visual": "Wall Street facade, falling stock ticker, courthouse steps, handcuffs"},
        {"key": "theranos", "titulo": "Theranos: the blood-test startup built on a fake machine",
         "hook": "A $9 billion company — and its core technology never worked.",
         "angle": "Elizabeth Holmes (Theranos) was convicted of fraud in 2022 and sentenced to ~11 years. Source: US DOJ.",
         "visual": "lab vials, broken device, Silicon Valley office, verdict headline"},
        {"key": "ftx", "titulo": "FTX: how a crypto giant collapsed in a week",
         "hook": "One of the biggest crypto exchanges vanished almost overnight.",
         "angle": "Sam Bankman-Fried (FTX) was convicted of fraud in 2023 and sentenced to 25 years. Source: US DOJ.",
         "visual": "crypto charts crashing, empty office, courtroom sketch"},
        {"key": "enron", "titulo": "Enron: the energy giant that faked its own success",
         "hook": "It was 'America's most innovative company' — until the books were opened.",
         "angle": "Enron collapsed in 2001 on accounting fraud; Jeffrey Skilling was convicted in 2006. Source: US DOJ.",
         "visual": "corporate tower, shredded documents, stock collapse graph"},
        {"key": "stanford", "titulo": "Allen Stanford: the $7 billion certificate-of-deposit fraud",
         "hook": "He sold 'safe' deposits that were anything but.",
         "angle": "Allen Stanford ran a ~$7B Ponzi scheme; convicted in 2012 and sentenced to 110 years. Source: US DOJ / SEC.",
         "visual": "offshore bank, Caribbean island, fake certificates, gavel"},
        {"key": "anna_delvey", "titulo": "Anna 'Delvey': the fake heiress who fooled New York",
         "hook": "She posed as a German heiress to con banks and hotels.",
         "angle": "Anna Sorokin ('Delvey') was convicted of grand larceny and theft of services in 2019. Source: New York State court / reputable press.",
         "visual": "luxury hotel lobby, designer bags, unpaid bills, courtroom"},
        {"key": "galleon", "titulo": "Raj Rajaratnam: the insider-trading ring worth millions",
         "hook": "He traded on secrets whispered over the phone — and got caught on tape.",
         "angle": "Raj Rajaratnam (Galleon Group) was convicted of insider trading in 2011 and sentenced to 11 years. Source: US DOJ / SEC.",
         "visual": "trading floor, wiretap waveform, phone call, handcuffs"},
        {"key": "belfort", "titulo": "Jordan Belfort: the 'Wolf of Wall Street' pump-and-dump",
         "hook": "The real story behind the movie — and the real sentence.",
         "angle": "Jordan Belfort (Stratton Oakmont) pleaded guilty to securities fraud and money laundering in 1999. Source: US DOJ.",
         "visual": "boiler-room phones, penny-stock chart, yacht, courtroom"},
    ],
)

# ───────────────────────── 12) How it's made / cómo se fabrica (EN) ─────────────────────────
# Faceless, visual, evergreen y sin riesgo legal/YMYL. Familia 'Decoded' (AI Decoded, Map Decoded).
# Evitamos el nombre registrado "How It's Made" (marca TV) → "Factory Decoded".
HOWMADE = SimpleChannelConfig(
    slug="howmade", prefix="YT_HOWMADE", display_name="Factory Decoded",
    platform_key="youtube_howmade", lang="en", system_prompt_file="batch_en_system.md",
    tone="calm, satisfying process explainer; step by step, concrete and precise; no filler",
    category_id="28", emoji="🏭", cross_teaser="🏭 How it's made", refresh_interval_days=14,
    theme_desc=("An English faceless channel explaining how everyday objects and materials are "
                "manufactured, step by step: the real industrial process from raw material to "
                "finished product. Visual, satisfying, evergreen."),
    veracity_rules=("- Describe the REAL manufacturing process from reputable sources "
                    "(manufacturers, industry bodies, Britannica/encyclopedias). Do NOT invent or "
                    "guess steps; if a detail varies by maker, say so. Evergreen only. Cite the "
                    "source of the process on screen."),
    seed=[
        {"key": "glass", "titulo": "How flat glass is made (it floats on molten metal)",
         "hook": "Window glass is poured onto a bath of liquid tin.",
         "angle": "Float-glass process: molten glass floats on molten tin to form a perfectly flat sheet (Pilkington process). Source: Britannica / industry.",
         "visual": "molten glass ribbon, tin bath glow, cooling sheet, cutting line"},
        {"key": "pencil", "titulo": "How a pencil is made (there's no lead in it)",
         "hook": "The 'lead' is actually graphite mixed with clay.",
         "angle": "Graphite + clay fired into a core, glued between two cedar slats, shaped and painted. Source: manufacturer / Britannica.",
         "visual": "graphite-clay paste, cedar slats, grooved wood, paint line"},
        {"key": "chocolate", "titulo": "How chocolate is made (from bitter bean to sweet bar)",
         "hook": "The raw cacao bean tastes nothing like chocolate.",
         "angle": "Bean to bar: ferment, dry, roast, grind to liquor, conch, temper, mold. Source: industry / food-science references.",
         "visual": "cacao pods, roasting beans, conching machine, molded bars"},
        {"key": "mirror", "titulo": "How a mirror is made (a sheet of glass + a metal coat)",
         "hook": "A mirror is just glass with a very thin layer of silver.",
         "angle": "Silvering: a reflective metal layer (silver/aluminum) is deposited on glass and sealed. Source: Britannica / industry.",
         "visual": "glass sheet, silvering spray, reflective coat, backing paint"},
        {"key": "paper", "titulo": "How paper is made from a tree",
         "hook": "It starts as wood chips and ends as a smooth sheet.",
         "angle": "Pulping wood into fibers, screening into a mat, pressing and drying into paper. Source: industry / Britannica.",
         "visual": "wood chips, pulp slurry, rolling press, drying rollers"},
        {"key": "can", "titulo": "How an aluminum can is made from a flat disc",
         "hook": "A whole can is drawn from one small circle of metal.",
         "angle": "Drawing-and-ironing: a flat aluminum disc is cupped, stretched into a wall, trimmed and shaped. Source: industry.",
         "visual": "aluminum sheet, punched discs, drawn cup, finished can line"},
        {"key": "matches", "titulo": "How a match is made (chemistry on a stick)",
         "hook": "The spark comes from two chemicals that must meet.",
         "angle": "Match head (oxidizer + binder) ignites by friction against a striker strip (red phosphorus). Source: Britannica / chemistry references.",
         "visual": "match splints, dipping heads, striker strip, ignition"},
        {"key": "jeans", "titulo": "How jeans are made (and why they're blue)",
         "hook": "Denim gets its color from one very old dye: indigo.",
         "angle": "Cotton is woven into denim, dyed with indigo, cut and sewn into jeans. Source: industry / textile references.",
         "visual": "cotton yarn, indigo dye vat, denim loom, sewing line"},
    ],
)

# ───────────────────────── 13) Persuasión y lenguaje corporal basado en evidencia (EN) ─────────────────────────
# Adyacente a Mente Racional (sesgos) pero DISTINTO: sesgos = tus propios sesgos cognitivos;
# aquí = influencia social + comunicación no verbal (cómo te influyen los demás y qué dice de
# verdad el lenguaje corporal). ANTI pseudociencia: NADA de "dark psychology" ni mitos (Mehrabian
# 7%, "brazos cruzados = mentira"); solo evidencia revisada + desmontar mitos. Enfoque defensivo
# (reconocer la influencia sobre ti), nunca "cómo manipular". [[veracidad-obligatoria]]
PERSUASION = SimpleChannelConfig(
    slug="persuasion", prefix="YT_PERSUASION", display_name="Mind Signals",
    platform_key="youtube_persuasion", lang="en", system_prompt_file="batch_en_system.md",
    tone="evidence-based psychology explainer; myth-busting, defensive ('spot it when it's used on you'), never a manipulation how-to",
    category_id="27", emoji="🧩", cross_teaser="🧩 Mind signals", refresh_interval_days=10,
    theme_desc=("An English faceless channel on the evidence-based psychology of persuasion, "
                "influence and nonverbal communication: how people really influence each other, "
                "what body language actually shows (and the popular myths), framed defensively so "
                "viewers can recognize it — never a manipulation how-to."),
    veracity_rules=("- ONLY established, peer-reviewed findings tied to NAMED research (Cialdini, "
                    "Asch, Ekman with caveats, Chartrand & Bargh, DePaulo). Actively DEBUNK popular "
                    "myths (Mehrabian '7%-38%-55%', 'crossed arms = lying', NLP eye-direction). "
                    "Defensive framing only ('recognize it when used on you'); NEVER 'how to "
                    "manipulate'. NO 'dark psychology', NO pseudoscience. Cite the study on screen."),
    seed=[
        {"key": "mehrabian_myth", "titulo": "The '93% of communication is body language' myth",
         "hook": "That famous stat is real research — used completely wrong.",
         "angle": "Mehrabian's 7-38-55 figures came from narrow studies on feelings about single words, NOT all communication. Source: Mehrabian & Wiener (1967).",
         "visual": "the 7-38-55 pie, a big red 'myth' stamp, original study page"},
        {"key": "cialdini_six", "titulo": "The 6 triggers that make you say yes",
         "hook": "Persuasion isn't magic — it's six repeatable principles.",
         "angle": "Cialdini's principles: reciprocity, commitment, social proof, authority, liking, scarcity. Source: Cialdini, 'Influence' (1984).",
         "visual": "six labeled icons, a checklist, a hand shaking"},
        {"key": "lie_detection", "titulo": "Can you really spot a liar from body language? (No)",
         "hook": "People detect lies barely better than a coin flip.",
         "angle": "Meta-analysis: average lie-detection accuracy is ~54%, and 'tells' like gaze aversion are unreliable. Source: DePaulo et al. (2003).",
         "visual": "coin flip, crossed-out 'tells', 54% accuracy bar"},
        {"key": "reciprocity", "titulo": "Why a free sample makes you buy",
         "hook": "A tiny gift creates a surprisingly strong urge to give back.",
         "angle": "Reciprocity: an unsolicited favor increases compliance (the classic soda-then-raffle study). Source: Regan (1971) / Cialdini.",
         "visual": "free sample tray, a gift, a wallet opening"},
        {"key": "foot_in_door", "titulo": "The 'foot in the door' technique",
         "hook": "Say yes to something small and you'll likely say yes to something big.",
         "angle": "A small initial request raises compliance with a larger later one. Source: Freedman & Fraser (1966).",
         "visual": "a small checkbox, then a big one, a door opening"},
        {"key": "social_proof", "titulo": "Why we copy the crowd (even when it's wrong)",
         "hook": "People will agree with an obviously wrong group — just to fit in.",
         "angle": "Conformity: many participants matched clearly wrong group answers on a line task. Source: Asch conformity experiments (1951).",
         "visual": "line-length cards, a crowd, one person caving"},
        {"key": "mirroring", "titulo": "The 'chameleon effect': why we mirror each other",
         "hook": "We unconsciously copy the posture of people we talk to.",
         "angle": "Mimicking a partner's mannerisms happens automatically and increases liking. Source: Chartrand & Bargh (1999).",
         "visual": "two people mirroring posture, synced gestures"},
        {"key": "scarcity", "titulo": "Why 'only 2 left' makes you want it more",
         "hook": "The same item feels more valuable when it's scarce.",
         "angle": "Scarcity raises perceived value; cookies were rated higher when supply looked limited. Source: Worchel et al. (1975) / Cialdini.",
         "visual": "'only 2 left' tag, a countdown, a crowded checkout"},
    ],
)

BATCH: list[SimpleChannelConfig] = [MISTERIOS, SESGOS, FILOSOFIA, CURIOSIDADES, ESPACIO, DATOS,
                                    SCAMS, AINEWS, BUSINESS, GEOGRAPHY,
                                    TRUECRIME, HOWMADE, PERSUASION]


def by_slug(slug: str) -> SimpleChannelConfig | None:
    for c in BATCH:
        if c.slug == slug:
            return c
    return None
