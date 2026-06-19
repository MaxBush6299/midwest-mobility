"""Plant content generator (Gate D Tasks 8, 9).

Two-phase generator for cloned plants:

1. **Mechanical phase** (Task 8): scrub plant-local identifiers from
   CSVs under ``plants/<plant>/kb/08_Logs_Data/`` and apply
   deterministic jitter to date and numeric-quantity columns.

2. **Narrative phase** (Task 9): regenerate KB markdown narratives by
   sending each Plant 7 source doc to an LLM with a plant-specific
   prompt and validating the response has no source-plant remnants.

CLI:
    # mechanical only (no LLM):
    python scripts/generate_plant_content.py --plant plant4 --mechanical-only
    # full (mechanical + narrative; requires Foundry chat client):
    python scripts/generate_plant_content.py --plant plant4

Substitutions (applied globally to each CSV body; header is preserved
byte-for-byte because none of these patterns appear in the schema row):

* ``MMC_P7``        -> ``MMC_<plant_code>``
* ``PM-P7-``        -> ``PM-<plant_code>-``
* ``INC-P7-``       -> ``INC-<plant_code>-``
* ``TRN-P7-``       -> ``TRN-<plant_code>-``
* ``P7-L<n>-...``   -> ``<plant_code>-L<n>-...``

Cross-plant shared scenario IDs (``BRK-CAL-XYZ``, ``Acme Brakes``, etc.)
are NOT mutated; the regex set above is intentionally narrow.

Jitter seed: ``sha256(f"{plant_id}:{filename}:{row_index}")``. Same seed
on every run, so output is byte-deterministic.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import re
import sys
from datetime import date, timedelta
from pathlib import Path
from typing import Sequence

import yaml

_DATE_VALUE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
_QTY_HEADER_KEYWORDS: tuple[str, ...] = (
    "hours",
    "duration",
    "qty",
    "quantity",
    "score",
    "volume",
)

# Columns whose values get name-substituted per plant. Header match is
# case-insensitive on these tokens.
_NAME_HEADER_KEYWORDS: tuple[str, ...] = (
    "employee_name",
    "trainer",
    "technician",
    "reported_by",
    "investigated_by",
)

# Role-style labels and contractor placeholders are preserved verbatim
# across plants — they aren't real names.
_PRESERVE_LITERALLY: frozenset[str] = frozenset(
    {
        "EHS Manager",
        "Line Supervisor",
        "Line Lead",
        "Operator",
        "Supervisor",
        "Quality Mgr",
    }
)


def _is_role_label(value: str) -> bool:
    if value in _PRESERVE_LITERALLY:
        return True
    return value.startswith("Contractor -")


# Per-plant employee + trainer rosters. Plant 7 is the source-of-truth
# plant and keeps its original names; cloned plants get a locale-appropriate
# roster so multi-plant queries don't collapse to identical headcounts.
#
# The mapping from a Plant 7 name to a plant-specific name is
# deterministic: ``sha256(plant_id + ":" + original)`` mod len(roster).
# Collisions are accepted; with ~80 candidates and 88 distinct source
# names the few collisions just mean two Plant 7 employees map to the
# same Plant 4 employee, which is realistic.
_NAME_ROSTERS: dict[str, list[str]] = {
    "plant4": [
        # Mexican / Hispanic names for Monterrey plant.
        "Alejandro Hernández", "Ana López", "Andrés Ramírez", "Antonio Soto",
        "Beatriz Castillo", "Carlos Vargas", "Carmen Mendoza", "César Aguilar",
        "Claudia Torres", "Cristina Reyes", "Daniela Gutiérrez", "David Ortiz",
        "Diana Salinas", "Eduardo Méndez", "Elena Cordero", "Emilio Cruz",
        "Enrique Castañeda", "Esteban Lara", "Fernanda Ríos", "Fernando Solís",
        "Francisco Ibarra", "Gabriela Núñez", "Gerardo Cabrera", "Gloria Peña",
        "Guadalupe Cervantes", "Hector Galindo", "Hugo Quintero", "Ignacio Beltrán",
        "Inés Padilla", "Isabel Domínguez", "Jaime Carrillo", "Javier Pacheco",
        "Jorge Espinoza", "José Luis Acosta", "Juan Pablo Tovar", "Julia Santana",
        "Karina Velázquez", "Laura Bautista", "Leonardo Treviño", "Leticia Aragón",
        "Lorena Flores", "Lucía Camacho", "Luis Estrada", "Manuel Becerra",
        "Marcela Olvera", "María Elena Zúñiga", "Mariana Tapia", "Mario Jiménez",
        "Martha Cisneros", "Mauricio Arellano", "Miguel Ángel Cuéllar",
        "Mónica Avalos", "Natalia Carrasco", "Néstor Maldonado", "Norma Esquivel",
        "Octavio Pineda", "Olivia Magaña", "Óscar Robles", "Pablo Rivera",
        "Patricia Zamora", "Paula Bermúdez", "Pedro Quiroz", "Rafael Cárdenas",
        "Ramón Linares", "Raquel Mejía", "Raúl Tello", "Rebeca Avila",
        "Ricardo Hidalgo", "Roberto Cantú", "Rocío Bravo", "Rodolfo Rangel",
        "Rosa María Pulido", "Salvador Tirado", "Sandra Lugo", "Santiago Vega",
        "Sergio Montaño", "Silvia Anguiano", "Sofía Alarcón", "Tomás Negrete",
        "Verónica Madrigal", "Víctor Manuel Solano", "Yolanda Garibay",
    ],
}

_TRAINER_ROSTERS: dict[str, list[str]] = {
    "plant4": [
        "L. Ramírez",
        "M. Sánchez",
        "J. Castillo",
        "P. Hernández",
        "C. Aguilar",
        "R. Domínguez",
    ],
}


def derive_plant_code(profile: dict, plant_id: str) -> str:
    """Return profile['plant_code'] if present, else derive from plant_id."""
    code = profile.get("plant_code")
    if code:
        return str(code)
    suffix = plant_id[len("plant"):]
    return f"P{suffix.upper()}"


def build_substitutions(plant_code: str) -> list[tuple[re.Pattern[str], str]]:
    """Ordered (pattern, replacement) pairs scrubbing P7 -> plant_code tokens.

    Deliberately narrow: only well-known work-order/equipment prefixes are
    rewritten so cross-plant scenario IDs (BRK-CAL-XYZ, Acme Brakes, etc.)
    are never touched.
    """
    return [
        (re.compile(r"MMC_P7"), f"MMC_{plant_code}"),
        (re.compile(r"\bPM-P7-"), f"PM-{plant_code}-"),
        (re.compile(r"\bINC-P7-"), f"INC-{plant_code}-"),
        (re.compile(r"\bTRN-P7-"), f"TRN-{plant_code}-"),
        # Equipment IDs like P7-L1-CMM-04, P7-L2-ROB-001
        (re.compile(r"\bP7-L(\d)-"), rf"{plant_code}-L\1-"),
    ]


def _row_seed(plant_id: str, filename: str, row_index: int) -> int:
    """Deterministic per-row seed used for date + quantity jitter."""
    digest = hashlib.sha256(
        f"{plant_id}:{filename}:{row_index}".encode("utf-8")
    ).hexdigest()
    return int(digest[:16], 16)


def jitter_date(value: str, seed: int) -> str:
    """Shift an ISO date by a deterministic offset in [-3, +3] days."""
    if not _DATE_VALUE_RE.match(value):
        return value
    try:
        d = date.fromisoformat(value)
    except ValueError:
        return value
    offset = (seed % 7) - 3
    return (d + timedelta(days=offset)).isoformat()


def jitter_numeric(value: str, seed: int) -> str:
    """Scale a numeric value by a deterministic factor in [-5%, +5%].

    Preserves the source's decimal precision so "2.0" stays "2.1", "92"
    stays an integer "93", etc.
    """
    try:
        n = float(value)
    except ValueError:
        return value
    factor = 1.0 + (((seed >> 16) % 11) - 5) / 100.0
    new = n * factor
    if "." in value:
        decimals = len(value.split(".", 1)[1])
        return f"{new:.{decimals}f}"
    return str(int(round(new)))


def _is_date_header(name: str) -> bool:
    return "date" in name.lower()


def _is_quantity_header(name: str) -> bool:
    n = name.lower()
    return any(k in n for k in _QTY_HEADER_KEYWORDS)


def _is_name_header(name: str) -> bool:
    n = name.lower()
    return any(k == n or k in n for k in _NAME_HEADER_KEYWORDS)


def _is_trainer_header(name: str) -> bool:
    return name.lower() == "trainer"


def _substitute_name(plant_id: str, original: str, roster: list[str]) -> str:
    """Deterministic per-plant name replacement.

    Same ``original`` always maps to the same roster entry within a plant,
    so a single Plant 7 employee appearing in N rows maps to a single
    plant-specific employee across all those rows. Role-style labels
    (``EHS Manager``, ``Operator``, etc.) and contractor placeholders are
    preserved verbatim.
    """
    if not original or _is_role_label(original):
        return original
    if not roster:
        return original
    h = hashlib.sha256(f"{plant_id}:{original}".encode("utf-8")).digest()
    idx = int.from_bytes(h[:8], "big") % len(roster)
    return roster[idx]


def process_csv(path: Path, plant_id: str, plant_code: str) -> None:
    """Apply substitutions + per-row jitter to a CSV in place."""
    subs = build_substitutions(plant_code)
    raw = path.read_text(encoding="utf-8")
    for pat, repl in subs:
        raw = pat.sub(repl, raw)

    name_roster = _NAME_ROSTERS.get(plant_id, [])
    trainer_roster = _TRAINER_ROSTERS.get(plant_id, [])

    reader = csv.reader(io.StringIO(raw))
    rows = list(reader)
    if not rows:
        return
    header = rows[0]
    out_rows: list[list[str]] = [header]
    for row_index, row in enumerate(rows[1:]):
        seed = _row_seed(plant_id, path.name, row_index)
        new_row: list[str] = []
        for col_idx, cell in enumerate(row):
            col_name = header[col_idx] if col_idx < len(header) else ""
            if _is_date_header(col_name):
                new_row.append(jitter_date(cell, seed))
            elif _is_quantity_header(col_name):
                new_row.append(jitter_numeric(cell, seed))
            elif _is_trainer_header(col_name) and trainer_roster:
                new_row.append(_substitute_name(plant_id, cell, trainer_roster))
            elif _is_name_header(col_name) and name_roster:
                new_row.append(_substitute_name(plant_id, cell, name_roster))
            else:
                new_row.append(cell)
        out_rows.append(new_row)

    buf = io.StringIO()
    writer = csv.writer(buf, lineterminator="\n")
    for r in out_rows:
        writer.writerow(r)
    path.write_text(buf.getvalue(), encoding="utf-8")


def run_mechanical_phase(plant_dir: Path, plant_id: str, plant_code: str) -> int:
    csv_dir = plant_dir / "kb" / "08_Logs_Data"
    if not csv_dir.is_dir():
        return 0
    count = 0
    for csv_path in sorted(csv_dir.glob("*.csv")):
        process_csv(csv_path, plant_id, plant_code)
        count += 1
    return count


# ---------------------------------------------------------------------------
# Narrative LLM regeneration phase (Task 9)
# ---------------------------------------------------------------------------

_FORBIDDEN_REMNANT_RE = re.compile(r"MMC_P7|Plant 7|plant7|P7-L")


class NarrativeContaminationError(RuntimeError):
    """Raised when an LLM response retains source-plant identifiers."""

    def __init__(self, path: Path, remnants: list[str]) -> None:
        self.path = path
        self.remnants = remnants
        super().__init__(
            f"narrative output for {path} contains forbidden source-plant "
            f"remnants: {sorted(set(remnants))}"
        )


def build_narrative_prompt(source_doc: str, profile: dict) -> str:
    """Build the LLM prompt for rewriting a Plant 7 narrative as the new plant.

    The prompt includes the full source doc verbatim, the target plant's
    location/lines/standards from the profile, and an explicit ban on
    source-plant identifiers so the model doesn't leak them.
    """
    plant_id = profile.get("plant_id", "")
    plant_code = profile.get("plant_code") or (
        f"P{plant_id[len('plant'):].upper()}" if plant_id.startswith("plant") else ""
    )
    display_name = profile.get("display_name", "")
    location = profile.get("location") or {}
    city = location.get("city", "")
    state = location.get("state", "")
    country = location.get("country", "")
    lines = profile.get("lines") or []
    line_lines = "\n".join(
        f"  - {ln.get('id', '?')}: {ln.get('name', '?')} "
        f"(equipment prefix {ln.get('equipment_prefix', '?')})"
        for ln in lines
    )
    standards = ", ".join(profile.get("standards") or []) or "(inherit from source)"

    return (
        f"You are rewriting an MMC plant knowledge-base document as the "
        f"target plant ({display_name}, plant_id={plant_id}, "
        f"plant_code={plant_code}).\n\n"
        f"Target plant context:\n"
        f"  Location: {city}, {state}, {country}\n"
        f"  Production lines:\n{line_lines}\n"
        f"  Regulatory standards: {standards}\n\n"
        f"Rules:\n"
        f"  1. Preserve the document's STRUCTURE, sections, and intent.\n"
        f"  2. Substitute plant-local identifiers: every MMC_P7, Plant 7, "
        f"plant7, and P7-L<n>-... equipment ID must be rewritten using "
        f"the target plant's identifiers ({plant_code}, etc.).\n"
        f"  3. Keep cross-plant shared scenario IDs unchanged "
        f"(e.g. BRK-CAL-XYZ, Acme Brakes).\n"
        f"  4. Adapt regulatory references to the target plant's "
        f"jurisdiction (e.g. NOM-STPS for MX, OSHA for US).\n"
        f"  5. NEVER emit MMC_P7, Plant 7, plant7, or any P7-L<n>-... "
        f"identifier in the output.\n\n"
        f"Source document (rewrite as the target plant):\n"
        f"---SOURCE---\n"
        f"{source_doc}\n"
        f"---END SOURCE---\n"
    )


def _call_chat_client(client: object, prompt: str) -> str:
    """Invoke chat client via .complete(prompt) or .invoke(prompt) fallback."""
    method = getattr(client, "complete", None) or getattr(client, "invoke", None)
    if method is None:
        raise TypeError(
            f"chat client {type(client).__name__} has neither .complete() "
            f"nor .invoke() method"
        )
    response = method(prompt)
    if isinstance(response, str):
        return response
    # Tolerate response objects with .content (OpenAI-style) or .text.
    for attr in ("content", "text", "message"):
        val = getattr(response, attr, None)
        if isinstance(val, str):
            return val
    raise TypeError(
        f"chat client returned unsupported response type {type(response).__name__}; "
        f"expected str or object with .content/.text/.message"
    )


def _scan_for_remnants(text: str) -> list[str]:
    return _FORBIDDEN_REMNANT_RE.findall(text)


def regenerate_narrative_file(
    source: Path,
    dest: Path,
    profile: dict,
    chat_client: object,
) -> None:
    """Rewrite a Plant 7 narrative as the target plant via the chat client.

    Raises ``NarrativeContaminationError`` (and refuses to write dest) if
    the LLM response retains any source-plant identifiers.
    """
    source_doc = source.read_text(encoding="utf-8")
    prompt = build_narrative_prompt(source_doc, profile)
    response = _call_chat_client(chat_client, prompt)

    remnants = _scan_for_remnants(response)
    if remnants:
        raise NarrativeContaminationError(dest, remnants)

    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(response, encoding="utf-8")


def _default_chat_client() -> object:
    """Lazily import the production chat client.

    Kept lazy so tests can import this module without pulling in
    azure-identity / Foundry SDKs.
    """
    from mmc_agents.orchestrator.model_config import manager_chat_client

    return manager_chat_client()


# ---------------------------------------------------------------------------
# Cross-plant BOM link (Task 10)
# ---------------------------------------------------------------------------

# Parts that are deliberately shared across plants (cross-plant scenario IDs).
# Expand this set as more shared scenarios land.
SHARED_BOM_PART_IDS: frozenset[str] = frozenset({"BRK-CAL-XYZ"})

_P7_EQUIP_PREFIX_RE = re.compile(r"^P7-")


def ensure_cross_plant_bom_link(
    bom_path: Path, plant_id: str, plant_code: str
) -> int:
    """Add target-plant rows for each shared scenario Part_ID found in source.

    Idempotent: if a row for (Part_ID, target plant_id) already exists, it is
    not duplicated. Returns the number of new rows appended.

    Equipment_ID values prefixed with ``P7-`` are rewritten to use the target
    plant_code's letter+digit prefix (e.g. ``P7-L1-CMM-04`` -> ``P4-L1-CMM-04``).
    Equipment IDs without that prefix are copied verbatim. If an
    ``Annual_Volume`` column exists, the target row's value is scaled by 0.6
    (rounded to int) to reflect a smaller secondary-source allocation; if no
    such column exists, this is a no-op.
    """
    import csv as _csv

    text = bom_path.read_text(encoding="utf-8")
    if not text:
        return 0
    reader = _csv.reader(text.splitlines())
    rows = list(reader)
    if not rows:
        return 0
    header = rows[0]
    body = [r for r in rows[1:] if r]

    try:
        col_part = header.index("Part_ID")
        col_plant = header.index("Plant_ID")
        col_plant_code = header.index("Plant_Code")
        col_equip = header.index("Equipment_ID")
    except ValueError as exc:
        raise ValueError(f"bom CSV missing required column: {exc}") from None
    col_volume = header.index("Annual_Volume") if "Annual_Volume" in header else -1

    m = re.search(r"P([A-Z0-9]+)$", plant_code)
    equip_prefix = f"P{m.group(1)}-" if m else None

    existing_target_keys = {
        (r[col_part], r[col_plant]) for r in body if len(r) > col_plant
    }

    added_rows: list[list[str]] = []
    for r in body:
        if len(r) <= max(col_part, col_plant, col_plant_code, col_equip):
            continue
        part_id = r[col_part]
        if part_id not in SHARED_BOM_PART_IDS:
            continue
        if r[col_plant] == plant_id:
            continue
        if (part_id, plant_id) in existing_target_keys:
            continue
        new_row = list(r)
        new_row[col_plant] = plant_id
        new_row[col_plant_code] = plant_code
        if equip_prefix is not None:
            new_row[col_equip] = _P7_EQUIP_PREFIX_RE.sub(equip_prefix, new_row[col_equip])
        if col_volume >= 0 and len(new_row) > col_volume:
            try:
                base = int(float(new_row[col_volume]))
                new_row[col_volume] = str(int(base * 0.6))
            except (TypeError, ValueError):
                pass
        added_rows.append(new_row)
        existing_target_keys.add((part_id, plant_id))

    if not added_rows:
        return 0

    trailing = "\n" if text.endswith("\n") else ""
    buf = io.StringIO()
    writer = _csv.writer(buf, lineterminator="\n")
    for row in added_rows:
        writer.writerow(row)
    appended = buf.getvalue()

    body_text = text.rstrip("\n")
    bom_path.write_text(
        body_text + "\n" + appended.rstrip("\n") + trailing, encoding="utf-8"
    )
    return len(added_rows)


def run_narrative_phase(
    plant_dir: Path,
    source_plant_dir: Path,
    profile: dict,
    chat_client: object,
) -> int:
    """Rewrite every cloned KB markdown using the source plant's doc as input.

    Maps ``plants/<plant>/kb/<sub>/MMC_<P?>_<rest>.md`` back to the
    corresponding ``plants/<source>/kb/<sub>/MMC_P7_<rest>.md`` and
    overwrites the cloned file with the LLM regenerated version.
    """
    plant_code = derive_plant_code(profile, profile.get("plant_id", ""))
    count = 0
    for dest_md in sorted((plant_dir / "kb").rglob("*.md")):
        rel = dest_md.relative_to(plant_dir / "kb")
        # Find the corresponding Plant 7 source: same subdir, MMC_P7_<rest>.
        source_name = re.sub(
            rf"^MMC_{re.escape(plant_code)}_", "MMC_P7_", dest_md.name
        )
        source_md = source_plant_dir / "kb" / rel.parent / source_name
        if not source_md.is_file():
            # No source counterpart (e.g. plant-specific stub); skip silently.
            continue
        regenerate_narrative_file(source_md, dest_md, profile, chat_client)
        count += 1
    return count


def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="generate_plant_content",
        description=(
            "Generate plant-specific content for a cloned plant: mechanical "
            "CSV substitutions + deterministic jitter, plus (in Task 9) LLM "
            "narrative regeneration."
        ),
    )
    p.add_argument("--plant", required=True, help="plant_id (e.g. plant4)")
    p.add_argument(
        "--plants-root",
        type=Path,
        default=Path("plants"),
        help="root containing per-plant subdirectories (default: plants)",
    )
    p.add_argument(
        "--enterprise-root",
        type=Path,
        default=Path("enterprise"),
        help="root containing enterprise CSVs (default: enterprise)",
    )
    p.add_argument(
        "--source-plant",
        default="plant7",
        help="source plant_id whose KB narratives seed the LLM rewrite (default: plant7)",
    )
    p.add_argument(
        "--mechanical-only",
        action="store_true",
        help="skip the LLM narrative regeneration phase (Task 9)",
    )
    return p


def main(argv: Sequence[str] | None = None) -> int:
    args = build_arg_parser().parse_args(argv)
    plant_dir = args.plants_root / args.plant
    profile_path = plant_dir / "profile.yaml"
    if not profile_path.is_file():
        print(f"plant profile not found: {profile_path}", file=sys.stderr)
        return 1
    try:
        profile = yaml.safe_load(profile_path.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError as exc:
        print(f"failed to parse profile YAML: {exc}", file=sys.stderr)
        return 1
    if not isinstance(profile, dict):
        print("profile must be a YAML mapping", file=sys.stderr)
        return 1

    plant_code = derive_plant_code(profile, args.plant)
    n = run_mechanical_phase(plant_dir, args.plant, plant_code)
    print(f"mechanical: processed {n} CSV file(s) for {args.plant} ({plant_code})")

    bom_path = args.enterprise_root / "supply-chain" / "data" / "bom_where_used.csv"
    if bom_path.is_file():
        added = ensure_cross_plant_bom_link(bom_path, args.plant, plant_code)
        print(f"bom: added {added} cross-plant row(s) to {bom_path}")

    if args.mechanical_only:
        return 0

    source_plant_dir = args.plants_root / args.source_plant
    if not source_plant_dir.is_dir():
        print(
            f"source plant directory not found: {source_plant_dir} "
            "(needed for narrative rewrite; use --mechanical-only to skip)",
            file=sys.stderr,
        )
        return 1

    try:
        chat_client = _default_chat_client()
    except Exception as exc:
        print(
            f"failed to initialize chat client ({exc}); "
            "rerun with --mechanical-only to skip the narrative phase",
            file=sys.stderr,
        )
        return 1

    try:
        m = run_narrative_phase(plant_dir, source_plant_dir, profile, chat_client)
    except NarrativeContaminationError as exc:
        print(f"narrative validation failed: {exc}", file=sys.stderr)
        return 1
    print(f"narrative: rewrote {m} markdown file(s) from {args.source_plant}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
