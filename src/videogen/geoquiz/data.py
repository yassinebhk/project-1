"""Datos del canal GeoQuiz (EN) — países + modos múltiples (bandera, capital, monumento,
silueta, dato geográfico).

100% verificable (datos públicos). Banderas → flagcdn.com (dominio público, sin API key).
Siluetas → djaiss/mapsicon CC0. Monumentos → Wikimedia Commons (CC-BY/public). Datos
geográficos curados verificables.

Expansión 14/10: 160+ países con continent + tier correcto (por reconocibilidad real,
no por continente). 4 modos: flag/capital/monument/silhouette/fact. 10 preguntas/vídeo
con mezcla fácil+medio+difícil. Dedup por (país, modo) para no repetir combinación.
"""
from __future__ import annotations

# ─────────── Países ───────────
# (iso2, nombre EN, capital, continent, tier)
#   tier: 1=fácil top-of-mind, 2=medio, 3=difícil
#   continent: EU, AS, AF, NA (North America), SA (South America), OC
COUNTRIES: list[tuple[str, str, str, str, int]] = [
    # ───── Fácil (1): top-of-mind global ─────
    ("fr", "France", "Paris", "EU", 1),
    ("de", "Germany", "Berlin", "EU", 1),
    ("it", "Italy", "Rome", "EU", 1),
    ("es", "Spain", "Madrid", "EU", 1),
    ("gb", "United Kingdom", "London", "EU", 1),
    ("pt", "Portugal", "Lisbon", "EU", 1),
    ("nl", "Netherlands", "Amsterdam", "EU", 1),
    ("gr", "Greece", "Athens", "EU", 1),
    ("se", "Sweden", "Stockholm", "EU", 1),
    ("no", "Norway", "Oslo", "EU", 1),
    ("us", "United States", "Washington, D.C.", "NA", 1),
    ("ca", "Canada", "Ottawa", "NA", 1),
    ("mx", "Mexico", "Mexico City", "NA", 1),
    ("br", "Brazil", "Brasília", "SA", 1),
    ("ar", "Argentina", "Buenos Aires", "SA", 1),
    ("jp", "Japan", "Tokyo", "AS", 1),
    ("cn", "China", "Beijing", "AS", 1),
    ("in", "India", "New Delhi", "AS", 1),
    ("kr", "South Korea", "Seoul", "AS", 1),
    ("ru", "Russia", "Moscow", "EU", 1),
    ("au", "Australia", "Canberra", "OC", 1),
    ("eg", "Egypt", "Cairo", "AF", 1),
    ("za", "South Africa", "Pretoria", "AF", 1),

    # ───── Medio (2): reconocibles con esfuerzo ─────
    ("be", "Belgium", "Brussels", "EU", 2),
    ("ie", "Ireland", "Dublin", "EU", 2),
    ("ch", "Switzerland", "Bern", "EU", 2),
    ("at", "Austria", "Vienna", "EU", 2),
    ("dk", "Denmark", "Copenhagen", "EU", 2),
    ("fi", "Finland", "Helsinki", "EU", 2),
    ("pl", "Poland", "Warsaw", "EU", 2),
    ("cz", "Czechia", "Prague", "EU", 2),
    ("hu", "Hungary", "Budapest", "EU", 2),
    ("ua", "Ukraine", "Kyiv", "EU", 2),
    ("tr", "Turkey", "Ankara", "AS", 2),
    ("is", "Iceland", "Reykjavík", "EU", 2),
    ("sa", "Saudi Arabia", "Riyadh", "AS", 2),
    ("ae", "United Arab Emirates", "Abu Dhabi", "AS", 2),
    ("il", "Israel", "Jerusalem", "AS", 2),
    ("ir", "Iran", "Tehran", "AS", 2),
    ("iq", "Iraq", "Baghdad", "AS", 2),
    ("th", "Thailand", "Bangkok", "AS", 2),
    ("vn", "Vietnam", "Hanoi", "AS", 2),
    ("id", "Indonesia", "Jakarta", "AS", 2),
    ("ph", "Philippines", "Manila", "AS", 2),
    ("my", "Malaysia", "Kuala Lumpur", "AS", 2),
    ("sg", "Singapore", "Singapore", "AS", 2),
    ("pk", "Pakistan", "Islamabad", "AS", 2),
    ("ng", "Nigeria", "Abuja", "AF", 2),
    ("ke", "Kenya", "Nairobi", "AF", 2),
    ("ma", "Morocco", "Rabat", "AF", 2),
    ("et", "Ethiopia", "Addis Ababa", "AF", 2),
    ("cl", "Chile", "Santiago", "SA", 2),
    ("co", "Colombia", "Bogotá", "SA", 2),
    ("pe", "Peru", "Lima", "SA", 2),
    ("ve", "Venezuela", "Caracas", "SA", 2),
    ("cu", "Cuba", "Havana", "NA", 2),
    ("gt", "Guatemala", "Guatemala City", "NA", 2),
    ("nz", "New Zealand", "Wellington", "OC", 2),

    # ───── Difícil (3): poco top-of-mind ─────
    ("ro", "Romania", "Bucharest", "EU", 3),
    ("bg", "Bulgaria", "Sofia", "EU", 3),
    ("hr", "Croatia", "Zagreb", "EU", 3),
    ("rs", "Serbia", "Belgrade", "EU", 3),
    ("sk", "Slovakia", "Bratislava", "EU", 3),
    ("si", "Slovenia", "Ljubljana", "EU", 3),
    ("lt", "Lithuania", "Vilnius", "EU", 3),
    ("lv", "Latvia", "Riga", "EU", 3),
    ("ee", "Estonia", "Tallinn", "EU", 3),
    ("al", "Albania", "Tirana", "EU", 3),
    ("mk", "North Macedonia", "Skopje", "EU", 3),
    ("ba", "Bosnia and Herzegovina", "Sarajevo", "EU", 3),
    ("me", "Montenegro", "Podgorica", "EU", 3),
    ("md", "Moldova", "Chișinău", "EU", 3),
    ("by", "Belarus", "Minsk", "EU", 3),
    ("ge", "Georgia", "Tbilisi", "AS", 3),
    ("am", "Armenia", "Yerevan", "AS", 3),
    ("az", "Azerbaijan", "Baku", "AS", 3),
    ("kz", "Kazakhstan", "Astana", "AS", 3),
    ("uz", "Uzbekistan", "Tashkent", "AS", 3),
    ("tm", "Turkmenistan", "Ashgabat", "AS", 3),
    ("tj", "Tajikistan", "Dushanbe", "AS", 3),
    ("kg", "Kyrgyzstan", "Bishkek", "AS", 3),
    ("mn", "Mongolia", "Ulaanbaatar", "AS", 3),
    ("af", "Afghanistan", "Kabul", "AS", 3),
    ("np", "Nepal", "Kathmandu", "AS", 3),
    ("bt", "Bhutan", "Thimphu", "AS", 3),
    ("mm", "Myanmar", "Naypyidaw", "AS", 3),
    ("kh", "Cambodia", "Phnom Penh", "AS", 3),
    ("la", "Laos", "Vientiane", "AS", 3),
    ("lk", "Sri Lanka", "Colombo", "AS", 3),
    ("bd", "Bangladesh", "Dhaka", "AS", 3),
    ("qa", "Qatar", "Doha", "AS", 3),
    ("kw", "Kuwait", "Kuwait City", "AS", 3),
    ("om", "Oman", "Muscat", "AS", 3),
    ("ye", "Yemen", "Sana'a", "AS", 3),
    ("jo", "Jordan", "Amman", "AS", 3),
    ("lb", "Lebanon", "Beirut", "AS", 3),
    ("sy", "Syria", "Damascus", "AS", 3),
    ("tw", "Taiwan", "Taipei", "AS", 3),
    ("dz", "Algeria", "Algiers", "AF", 3),
    ("tn", "Tunisia", "Tunis", "AF", 3),
    ("ly", "Libya", "Tripoli", "AF", 3),
    ("sd", "Sudan", "Khartoum", "AF", 3),
    ("gh", "Ghana", "Accra", "AF", 3),
    ("ci", "Ivory Coast", "Yamoussoukro", "AF", 3),
    ("sn", "Senegal", "Dakar", "AF", 3),
    ("ml", "Mali", "Bamako", "AF", 3),
    ("ne", "Niger", "Niamey", "AF", 3),
    ("td", "Chad", "N'Djamena", "AF", 3),
    ("cm", "Cameroon", "Yaoundé", "AF", 3),
    ("ug", "Uganda", "Kampala", "AF", 3),
    ("tz", "Tanzania", "Dodoma", "AF", 3),
    ("rw", "Rwanda", "Kigali", "AF", 3),
    ("mg", "Madagascar", "Antananarivo", "AF", 3),
    ("mz", "Mozambique", "Maputo", "AF", 3),
    ("zm", "Zambia", "Lusaka", "AF", 3),
    ("zw", "Zimbabwe", "Harare", "AF", 3),
    ("na", "Namibia", "Windhoek", "AF", 3),
    ("bw", "Botswana", "Gaborone", "AF", 3),
    ("ao", "Angola", "Luanda", "AF", 3),
    ("cd", "DR Congo", "Kinshasa", "AF", 3),
    ("cg", "Congo", "Brazzaville", "AF", 3),
    ("ga", "Gabon", "Libreville", "AF", 3),
    ("so", "Somalia", "Mogadishu", "AF", 3),
    ("er", "Eritrea", "Asmara", "AF", 3),
    ("mw", "Malawi", "Lilongwe", "AF", 3),
    ("bi", "Burundi", "Gitega", "AF", 3),
    ("bf", "Burkina Faso", "Ouagadougou", "AF", 3),
    ("bj", "Benin", "Porto-Novo", "AF", 3),
    ("tg", "Togo", "Lomé", "AF", 3),
    ("gn", "Guinea", "Conakry", "AF", 3),
    ("sl", "Sierra Leone", "Freetown", "AF", 3),
    ("lr", "Liberia", "Monrovia", "AF", 3),
    ("mr", "Mauritania", "Nouakchott", "AF", 3),
    ("uy", "Uruguay", "Montevideo", "SA", 3),
    ("py", "Paraguay", "Asunción", "SA", 3),
    ("bo", "Bolivia", "La Paz", "SA", 3),
    ("ec", "Ecuador", "Quito", "SA", 3),
    ("gy", "Guyana", "Georgetown", "SA", 3),
    ("sr", "Suriname", "Paramaribo", "SA", 3),
    ("ht", "Haiti", "Port-au-Prince", "NA", 3),
    ("do", "Dominican Republic", "Santo Domingo", "NA", 3),
    ("hn", "Honduras", "Tegucigalpa", "NA", 3),
    ("sv", "El Salvador", "San Salvador", "NA", 3),
    ("ni", "Nicaragua", "Managua", "NA", 3),
    ("cr", "Costa Rica", "San José", "NA", 3),
    ("pa", "Panama", "Panama City", "NA", 3),
    ("jm", "Jamaica", "Kingston", "NA", 3),
    ("bb", "Barbados", "Bridgetown", "NA", 3),
    ("tt", "Trinidad and Tobago", "Port of Spain", "NA", 3),
    ("fj", "Fiji", "Suva", "OC", 3),
    ("pg", "Papua New Guinea", "Port Moresby", "OC", 3),
    ("ws", "Samoa", "Apia", "OC", 3),
    ("to", "Tonga", "Nukuʻalofa", "OC", 3),
    ("vu", "Vanuatu", "Port Vila", "OC", 3),
    ("sb", "Solomon Islands", "Honiara", "OC", 3),
    ("lu", "Luxembourg", "Luxembourg", "EU", 3),
    ("mt", "Malta", "Valletta", "EU", 3),
    ("cy", "Cyprus", "Nicosia", "EU", 3),
    ("mc", "Monaco", "Monaco", "EU", 3),
    ("sm", "San Marino", "San Marino", "EU", 3),
    ("ad", "Andorra", "Andorra la Vella", "EU", 3),
    ("li", "Liechtenstein", "Vaduz", "EU", 3),
    ("va", "Vatican City", "Vatican City", "EU", 3),
]

CONTINENTS = ("EU", "AS", "AF", "NA", "SA", "OC")


def by_iso2(iso2: str):
    for c in COUNTRIES:
        if c[0] == iso2:
            return c
    return None


def by_tier(tier: int) -> list[tuple]:
    return [c for c in COUNTRIES if c[4] == tier]


def flag_url(iso2: str, width: int = 1280) -> str:
    """Bandera CC0 pública (flagcdn.com)."""
    return f"https://flagcdn.com/w{width}/{iso2.lower()}.png"


def silhouette_url(iso2: str) -> str:
    """Silueta país PNG CC0 (djaiss/mapsicon). Fondo transparente, forma blanca."""
    return f"https://cdn.jsdelivr.net/gh/djaiss/mapsicon@master/all/{iso2.lower()}/1024.png"


# ─────────── Monumentos famosos ───────────
# (iso2 país, nombre monumento, URL imagen Wikimedia Commons CC-BY/PD)
# Son fotos emblemáticas identificables → país.
MONUMENTS: list[tuple[str, str, str]] = [
    ("fr", "Eiffel Tower", "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a8/Tour_Eiffel_Wikimedia_Commons.jpg/800px-Tour_Eiffel_Wikimedia_Commons.jpg"),
    ("in", "Taj Mahal", "https://upload.wikimedia.org/wikipedia/commons/thumb/b/bd/Taj_Mahal%2C_Agra%2C_India_edit3.jpg/800px-Taj_Mahal%2C_Agra%2C_India_edit3.jpg"),
    ("cn", "Great Wall", "https://upload.wikimedia.org/wikipedia/commons/thumb/5/51/The_Great_Wall_of_China_at_Jinshanling-edit.jpg/800px-The_Great_Wall_of_China_at_Jinshanling-edit.jpg"),
    ("it", "Colosseum", "https://upload.wikimedia.org/wikipedia/commons/thumb/5/53/Colosseum_in_Rome%2C_Italy_-_April_2007.jpg/800px-Colosseum_in_Rome%2C_Italy_-_April_2007.jpg"),
    ("br", "Christ the Redeemer", "https://upload.wikimedia.org/wikipedia/commons/thumb/7/79/Christ_the_Redeemer_-_Cristo_Redentor.jpg/800px-Christ_the_Redeemer_-_Cristo_Redentor.jpg"),
    ("pe", "Machu Picchu", "https://upload.wikimedia.org/wikipedia/commons/thumb/e/eb/Machu_Picchu%2C_Peru.jpg/800px-Machu_Picchu%2C_Peru.jpg"),
    ("us", "Statue of Liberty", "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a1/Statue_of_Liberty_7.jpg/800px-Statue_of_Liberty_7.jpg"),
    ("gb", "Big Ben", "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c0/London_November_2013-14a.jpg/800px-London_November_2013-14a.jpg"),
    ("au", "Sydney Opera House", "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4f/Sydney_Opera_House_-_Dec_2008.jpg/800px-Sydney_Opera_House_-_Dec_2008.jpg"),
    ("eg", "Pyramids of Giza", "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e3/Kheops-Pyramid.jpg/800px-Kheops-Pyramid.jpg"),
    ("gr", "Parthenon", "https://upload.wikimedia.org/wikipedia/commons/thumb/4/41/The_Parthenon_in_Athens.jpg/800px-The_Parthenon_in_Athens.jpg"),
    ("ru", "Saint Basil's Cathedral", "https://upload.wikimedia.org/wikipedia/commons/thumb/3/35/Moscow_July_2011-7a.jpg/800px-Moscow_July_2011-7a.jpg"),
    ("jp", "Mount Fuji", "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1f/MtFuji_FujiCity.jpg/800px-MtFuji_FujiCity.jpg"),
    ("kh", "Angkor Wat", "https://upload.wikimedia.org/wikipedia/commons/thumb/4/45/20171126_Angkor_Wat_4712_DxO.jpg/800px-20171126_Angkor_Wat_4712_DxO.jpg"),
    ("de", "Brandenburg Gate", "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5c/Brandenburger_Tor_abends.jpg/800px-Brandenburger_Tor_abends.jpg"),
    ("es", "Sagrada Família", "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a3/Sagrada_Familia_01.jpg/800px-Sagrada_Familia_01.jpg"),
    ("nl", "Amsterdam canals", "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b5/Amsterdam_Prinsengracht_in_de_zomer.jpg/800px-Amsterdam_Prinsengracht_in_de_zomer.jpg"),
    ("in", "Gateway of India", "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5c/Gateway_of_India_%28Transparent%29.png/640px-Gateway_of_India_%28Transparent%29.png"),
    ("jo", "Petra", "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4b/The_Treasury%2C_Petra_%286251101960%29.jpg/800px-The_Treasury%2C_Petra_%286251101960%29.jpg"),
    ("mx", "Chichen Itza", "https://upload.wikimedia.org/wikipedia/commons/thumb/1/14/El_Castillo%2C_Chichen_Itza.jpg/800px-El_Castillo%2C_Chichen_Itza.jpg"),
    ("ca", "CN Tower", "https://upload.wikimedia.org/wikipedia/commons/thumb/4/48/Toronto_-_ON_-_Toronto_Harbourfront7.jpg/800px-Toronto_-_ON_-_Toronto_Harbourfront7.jpg"),
    ("tr", "Hagia Sophia", "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0e/Istanbul_Hagia_Sophia_2013.jpg/800px-Istanbul_Hagia_Sophia_2013.jpg"),
    ("ir", "Persepolis", "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f7/Persepolis%2C_Iran_%2843%29.jpg/800px-Persepolis%2C_Iran_%2843%29.jpg"),
    ("ar", "Perito Moreno Glacier", "https://upload.wikimedia.org/wikipedia/commons/thumb/8/83/Perito_Moreno_Glacier_Patagonia_Argentina_Luca_Galuzzi_2005.JPG/800px-Perito_Moreno_Glacier_Patagonia_Argentina_Luca_Galuzzi_2005.JPG"),
    ("za", "Table Mountain", "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d1/Table_Mountain_DanieVDM.jpg/800px-Table_Mountain_DanieVDM.jpg"),
    ("tz", "Mount Kilimanjaro", "https://upload.wikimedia.org/wikipedia/commons/thumb/b/bd/Mount_Kilimanjaro_Dec_2009.JPG/800px-Mount_Kilimanjaro_Dec_2009.JPG"),
    ("ke", "Maasai Mara", "https://upload.wikimedia.org/wikipedia/commons/thumb/7/78/Masai_Mara_landscape.jpg/800px-Masai_Mara_landscape.jpg"),
    ("ma", "Jemaa el-Fnaa Marrakesh", "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8f/Jemaa_el_Fna_at_night.jpg/800px-Jemaa_el_Fna_at_night.jpg"),
    ("il", "Western Wall", "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f4/Western_Wall%2C_Jerusalem%2C_November_2014.jpg/800px-Western_Wall%2C_Jerusalem%2C_November_2014.jpg"),
    ("cu", "Havana Capitol", "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9b/El_Capitolio_de_la_Habana_DSC_0043.jpg/800px-El_Capitolio_de_la_Habana_DSC_0043.jpg"),
]


def monument_url(iso2: str) -> tuple[str, str] | None:
    """Devuelve (nombre, url) del primer monumento del país. None si no hay."""
    for m in MONUMENTS:
        if m[0] == iso2:
            return (m[1], m[2])
    return None


# ─────────── Datos geográficos distintivos ───────────
# Hecho curado + verificable que apunta a UN país concreto.
GEO_FACTS: dict[str, str] = {
    "fi": "The country with the most lakes in the world — over 180,000.",
    "ca": "The country with the longest coastline on Earth.",
    "va": "The smallest country in the world — 0.49 km².",
    "ru": "The largest country in the world by area.",
    "mc": "The second smallest country — famous for Formula 1 Grand Prix.",
    "au": "The only country that is also a continent.",
    "cl": "The longest country from north to south — over 4,300 km.",
    "jp": "An island nation of over 14,000 islands.",
    "id": "The world's largest archipelago — over 17,000 islands.",
    "nl": "A country where ~26% of the land lies below sea level.",
    "br": "The country containing most of the Amazon rainforest.",
    "mn": "The least densely populated independent country.",
    "ne": "A landlocked African country named after a river.",
    "bo": "A country whose capital, La Paz, is the highest in the world.",
    "pe": "Home to Machu Picchu and the Nazca Lines.",
    "no": "A European country famous for its fjords and the midnight sun.",
    "is": "A European island nation that sits on two tectonic plates.",
    "nz": "A country with more sheep than people.",
    "sg": "A tiny Asian city-state with four official languages.",
    "sa": "The country where Mecca and Medina are located.",
    "ir": "The ancient Persian empire — modern name since 1935.",
    "eg": "The country split in two by Africa's longest river.",
    "mg": "An island country famous for lemurs — east of mainland Africa.",
    "cr": "A Central American country without an army since 1948.",
    "bt": "A Himalayan kingdom that measures Gross National Happiness.",
    "lu": "A European grand duchy — one of the wealthiest countries per capita.",
    "sm": "The oldest surviving sovereign state and republic in the world.",
    "li": "A micro-state between Switzerland and Austria.",
    "mt": "A Mediterranean archipelago where 'The Maltese Falcon' got its name.",
    "ad": "A Pyrenean micro-state between Spain and France.",
}


def fact_text(iso2: str) -> str | None:
    return GEO_FACTS.get(iso2)
