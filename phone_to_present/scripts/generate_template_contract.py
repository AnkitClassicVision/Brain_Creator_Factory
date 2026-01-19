#!/usr/bin/env python3
"""
Generate a deterministic "template contract" from templates/presentation_template.md:
- required {{PLACEHOLDERS}}
- required local image refs (charts/*)
- best-effort slide count estimate

This prevents docs from drifting away from the actual template.
"""

from __future__ import annotations

import argparse
import hashlib
import re
from pathlib import Path
from urllib.parse import unquote


PLACEHOLDER_RE = re.compile(r"\{\{([A-Z0-9_]+)\}\}")
MD_IMAGE_RE = re.compile(r"!\[[^\]]*]\(([^)]+)\)")
HTML_IMAGE_RE = re.compile(r"<img[^>]+src=['\"]([^'\"]+)['\"][^>]*>", re.IGNORECASE)


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def extract_placeholders(text: str) -> list[str]:
    return sorted(set(PLACEHOLDER_RE.findall(text)))


def _normalize_md_link_target(raw: str) -> str:
    target = raw.strip()
    if target.startswith("<") and target.endswith(">"):
        target = target[1:-1].strip()
    target = target.split()[0].strip()
    target = target.strip("'\"")
    return unquote(target)


def extract_image_refs(text: str) -> list[str]:
    refs: set[str] = set()
    for m in MD_IMAGE_RE.finditer(text):
        refs.add(_normalize_md_link_target(m.group(1)))
    for m in HTML_IMAGE_RE.finditer(text):
        refs.add(unquote(m.group(1).strip()))
    return sorted(r for r in refs if r)


def md_slide_separators_count(md_text: str) -> int:
    """
    Best-effort slide count for a Marp markdown file:
    - ignore YAML frontmatter fenced by leading '---' ... '---'
    - count slide separators as lines that are exactly '---'
    """
    lines = md_text.splitlines()
    i = 0

    while i < len(lines) and not lines[i].strip():
        i += 1

    if i < len(lines) and lines[i].strip() == "---":
        i += 1
        while i < len(lines) and lines[i].strip() != "---":
            i += 1
        if i < len(lines) and lines[i].strip() == "---":
            i += 1

    seps = 0
    for line in lines[i:]:
        if line.strip() == "---":
            seps += 1
    return seps


def render_markdown_contract(*, template_rel: str, template_text: str) -> str:
    placeholders = extract_placeholders(template_text)
    images = extract_image_refs(template_text)
    charts = [p for p in images if p.startswith("charts/")]
    other_assets = [p for p in images if not p.startswith("charts/")]
    slide_est = md_slide_separators_count(template_text) + 1

    lines: list[str] = []
    lines.append("# Template Contract (Generated)")
    lines.append("")
    lines.append(f"- Template: `{template_rel}`")
    lines.append(f"- Template SHA256: `{sha256_text(template_text)}`")
    lines.append(f"- Slide count estimate: `{slide_est}`")
    lines.append("")
    lines.append("## Required Placeholders")
    for p in placeholders:
        lines.append(f"- `{p}`")
    lines.append("")
    lines.append("## Required Local Assets")
    lines.append("### Charts (template-referenced)")
    for p in charts:
        lines.append(f"- `{p}`")
    if other_assets:
        lines.append("")
        lines.append("### Other Images")
        for p in other_assets:
            lines.append(f"- `{p}`")
    lines.append("")
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a template contract from the Marp template.")
    parser.add_argument(
        "--template",
        type=Path,
        default=Path("templates/presentation_template.md"),
        help="Path to the Marp template (default: templates/presentation_template.md).",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("workflow/template_contract.md"),
        help="Output markdown path (default: workflow/template_contract.md).",
    )
    args = parser.parse_args()

    template_path: Path = args.template
    if not template_path.exists():
        raise SystemExit(f"Template not found: {template_path}")

    template_text = template_path.read_text(encoding="utf-8")
    contract = render_markdown_contract(template_rel=str(template_path), template_text=template_text)

    out_path: Path = args.out
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(contract, encoding="utf-8")

    print(f"[OK] Wrote template contract: {out_path}")
    print(f"[OK] Template file SHA256: {sha256_file(template_path)}")


if __name__ == "__main__":
    main()

