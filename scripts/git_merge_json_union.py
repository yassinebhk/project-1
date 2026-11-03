#!/usr/bin/env python3
"""Git merge driver: UNIÓN de arrays JSON append-only (sin perder entradas).

Varios canales hacen append al MISMO fichero JSON compartido (p. ej.
`output/ig_publish_log.json`, al que escriben todos los canales que publican en
Instagram). Cuando dos jobs commitean en ventanas solapadas, el merge textual
por defecto de git da `CONFLICT (content)` en el punto del append y el rebase
del commit-back falla → se pierde el commit ENTERO (incluidos los ledgers de
dedup que iban en el mismo commit). Ver `.github/workflows/_videogen-job.yml`.

Este driver resuelve ese conflicto de forma determinista: parsea las dos
versiones (nuestra y la de ellos), UNE todas las entradas deduplicando por una
clave estable y reescribe un JSON válido. Es el equivalente, para arrays JSON
multilínea, del `merge=union` que `.gitattributes` ya aplica a los `.jsonl`
(ahí la unión textual basta porque cada entrada es UNA línea; aquí no, porque
cada entrada ocupa varias líneas y la unión textual rompería el JSON).

Se configura con los marcadores  %A %B  (NUESTRA, SUYA) — ver
`.github/workflows/_videogen-job.yml`, que registra:
    git config merge.jsonunion.driver "python3 scripts/git_merge_json_union.py %A %B"
Para una UNIÓN append-only no hace falta la base (%O): basta ours ∪ theirs.
El driver escribe el resultado en %A (el fichero que git conserva) y sale 0.
SEGURIDAD: ante CUALQUIER problema (JSON inválido, formato inesperado…) sale
con código 1 SIN tocar %A → git deja el conflicto y el bucle de reintentos del
workflow actúa como hasta ahora. Es decir, nunca puede empeorar ni corromper.
"""
import json
import sys


def _entry_key(e):
    """Clave estable para deduplicar. Soporta arrays de objetos y de escalares."""
    if isinstance(e, dict):
        # media_id es único para posts OK; para skip/fail puede faltar → compuesto.
        mid = e.get("media_id")
        if mid:
            return ("mid", mid)
        return ("c", e.get("ts"), e.get("slug"), e.get("status"), e.get("title"))
    # array de escalares (p. ej. stock_used.json) → dedup por valor.
    return ("v", e)


def _ts(e):
    return e.get("ts", "") if isinstance(e, dict) else ""


def main(argv):
    if len(argv) < 3:
        return 1
    ours_path, theirs_path = argv[1], argv[2]  # %A (destino), %B
    try:
        with open(ours_path, encoding="utf-8") as f:
            ours = json.load(f)
        with open(theirs_path, encoding="utf-8") as f:
            theirs = json.load(f)
    except Exception:
        return 1  # no parseable → declina, deja el conflicto (sin corromper)

    # Solo sabemos unir listas append-only. Cualquier otra cosa → declina.
    if not isinstance(ours, list) or not isinstance(theirs, list):
        return 1

    merged = []
    seen = set()
    for e in ours + theirs:
        try:
            k = _entry_key(e)
        except Exception:
            return 1
        if k in seen:
            continue
        seen.add(k)
        merged.append(e)

    # Orden cronológico estable si hay timestamps (mantiene diffs limpios).
    try:
        if all(isinstance(e, dict) for e in merged):
            merged.sort(key=_ts)
    except Exception:
        pass  # orden no crítico; si falla, se queda el orden de unión

    try:
        with open(ours_path, "w", encoding="utf-8") as f:
            json.dump(merged, f, indent=2, ensure_ascii=False)
            f.write("\n")
    except Exception:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
