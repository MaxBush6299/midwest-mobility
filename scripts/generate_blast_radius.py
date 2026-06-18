"""Generate ``governance/blast_radius.json`` from the source metadata.

Run from the repo root:

    .venv\\Scripts\\python.exe scripts\\generate_blast_radius.py

The output is the computed blast-radius graph for every agent, ready to be
served by the trace UI's ``/agents/{name}/blast-radius`` endpoint without
the request path having to re-import + re-validate the source metadata on
every call. Re-run whenever the profile YAMLs or governance JSON change.
"""

from __future__ import annotations

import json
from pathlib import Path

from mmc_agents.governance.blast_radius import compute_all_blast_radii
from mmc_agents.governance.metadata import load_infra_metadata, load_kb_metadata

_REPO_ROOT = Path(__file__).resolve().parents[1]
_OUTPUT = _REPO_ROOT / "governance" / "blast_radius.json"


def main() -> None:
    kb_meta = load_kb_metadata()
    infra_meta = load_infra_metadata()
    radii = compute_all_blast_radii(kb_meta, infra_meta)
    payload = {
        "schema_version": "1.0",
        "description": (
            "Per-agent blast radius — generated from governance/kb_metadata.json "
            "and governance/infra_metadata.json by scripts/generate_blast_radius.py. "
            "Do not edit by hand; re-run the generator after changing profiles or governance JSON."
        ),
        "agents": {name: br.model_dump() for name, br in radii.items()},
    }
    _OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    _OUTPUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {_OUTPUT.relative_to(_REPO_ROOT)} ({len(radii)} agents)")


if __name__ == "__main__":
    main()
