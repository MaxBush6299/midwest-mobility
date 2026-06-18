"""Plant clone CLI (Gate D Task 6).

Renders a new ``plants/<plant_id>/`` directory tree from a plant profile
YAML and a Jinja2 template tree (``templates/plant_template/``).

The renderer walks every file under ``--template``; ``*.j2`` files have
their content rendered through Jinja2 with the profile + derived
context, every path component is rendered (so ``{{ plant_code }}`` in
directory names and filenames is substituted), and the trailing
``.j2`` suffix is stripped. Non-``.j2`` files are copied verbatim.

CLI:
    python scripts/clone_plant.py \\
        --profile plants/plant4.profile.yaml \\
        --template templates/plant_template \\
        --output-root plants \\
        [--force]

Refuses to overwrite an existing ``<output_root>/<plant_id>/`` directory
unless ``--force`` is passed; with ``--force`` the existing directory is
removed and re-rendered.
"""
from __future__ import annotations

import argparse
import re
import shutil
import sys
from pathlib import Path
from typing import Sequence

import yaml
from jinja2 import Environment, FileSystemLoader, StrictUndefined

PLANT_ID_RE = re.compile(r"^plant[a-z0-9]+$")
REQUIRED_KEYS: tuple[str, ...] = ("plant_id", "display_name", "lines", "agents", "kb")


def validate_profile(profile: dict) -> list[str]:
    """Return a list of human-readable validation errors (empty == valid)."""
    errors: list[str] = []
    missing = [k for k in REQUIRED_KEYS if k not in profile]
    if missing:
        errors.append(
            f"profile missing required keys: {missing} (need {list(REQUIRED_KEYS)})"
        )
    plant_id = profile.get("plant_id")
    if plant_id is not None and not PLANT_ID_RE.match(str(plant_id)):
        errors.append(
            f"invalid plant_id {plant_id!r}: must match {PLANT_ID_RE.pattern}"
        )
    return errors


def build_context(profile: dict) -> dict:
    """Build the Jinja render context from a validated profile.

    The profile is passed through verbatim and then enriched with derived
    convenience variables. Explicit keys in the profile always win over
    derived defaults — Plant 7's legacy profile (no ``plant_code``) and a
    Plant 4 profile that pins ``plant_code: P4`` both work.
    """
    plant_id: str = profile["plant_id"]
    # "7" from "plant7", "10" from "plant10", "x" from "plantx" (test fixtures).
    suffix = plant_id[len("plant"):]
    ctx: dict = dict(profile)
    ctx.setdefault("plant_code", f"P{suffix.upper()}")
    ctx.setdefault("plant_name", f"Plant {suffix.upper()}")
    ctx.setdefault("plant_display_name", profile.get("display_name", ""))
    ctx.setdefault(
        "primary_lines",
        [line.get("name", line.get("id", "")) for line in profile.get("lines", [])],
    )
    kb = profile.get("kb") or {}
    ctx.setdefault("kb_id_env", kb.get("kb_id_env", ""))
    return ctx


def _render_path_parts(env: Environment, parts: Sequence[str], ctx: dict) -> list[str]:
    """Render Jinja in each path component independently."""
    return [env.from_string(part).render(**ctx) for part in parts]


def render_tree(template_dir: Path, output_dir: Path, ctx: dict) -> None:
    """Walk template_dir and materialize a rendered copy under output_dir."""
    env = Environment(
        loader=FileSystemLoader(str(template_dir)),
        undefined=StrictUndefined,
        keep_trailing_newline=True,
    )
    for src in sorted(template_dir.rglob("*")):
        if src.is_dir():
            continue
        rel = src.relative_to(template_dir)
        rendered_parts = _render_path_parts(env, rel.parts, ctx)
        # Strip trailing .j2 from the final component (the filename).
        if rendered_parts[-1].endswith(".j2"):
            rendered_parts[-1] = rendered_parts[-1][: -len(".j2")]
        dst = output_dir.joinpath(*rendered_parts)
        dst.parent.mkdir(parents=True, exist_ok=True)
        if src.suffix == ".j2":
            content = env.get_template(rel.as_posix()).render(**ctx)
            dst.write_text(content, encoding="utf-8")
        else:
            # Literal file: copy bytes, preserve mtime.
            shutil.copy2(src, dst)


def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="clone_plant",
        description="Render plants/<plant_id>/ from a profile + Jinja2 template tree.",
    )
    p.add_argument(
        "--profile",
        required=True,
        type=Path,
        help="path to plant profile YAML (e.g. plants/plant4.profile.yaml)",
    )
    p.add_argument(
        "--template",
        required=True,
        type=Path,
        help="path to template directory (e.g. templates/plant_template)",
    )
    p.add_argument(
        "--output-root",
        required=True,
        type=Path,
        help="root under which <plant_id>/ is created (e.g. plants/)",
    )
    p.add_argument(
        "--force",
        action="store_true",
        help="overwrite an existing <output-root>/<plant_id>/ directory",
    )
    return p


def main(argv: Sequence[str] | None = None) -> int:
    args = build_arg_parser().parse_args(argv)

    if not args.profile.is_file():
        print(f"profile not found: {args.profile}", file=sys.stderr)
        return 1
    if not args.template.is_dir():
        print(f"template directory not found: {args.template}", file=sys.stderr)
        return 1

    try:
        profile = yaml.safe_load(args.profile.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        print(f"failed to parse profile YAML: {exc}", file=sys.stderr)
        return 1
    if not isinstance(profile, dict):
        print("profile must be a YAML mapping at the top level", file=sys.stderr)
        return 1

    errors = validate_profile(profile)
    if errors:
        for err in errors:
            print(err, file=sys.stderr)
        return 1

    plant_id: str = profile["plant_id"]
    plant_dir = args.output_root / plant_id
    if plant_dir.exists():
        if not args.force:
            print(
                f"Refusing to overwrite existing plant directory: {plant_dir}",
                file=sys.stderr,
            )
            return 1
        shutil.rmtree(plant_dir)

    plant_dir.mkdir(parents=True, exist_ok=True)
    ctx = build_context(profile)
    render_tree(args.template, plant_dir, ctx)
    print(f"Rendered {plant_id} -> {plant_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
