#!/usr/bin/env python3
"""
Deterministically render a Marp deck (HTML + PPTX) from a populated .md file
and fail fast on common "client-facing" issues:
- unreplaced {{VARIABLE}} tokens
- missing local images
- Marp render failures

Writes a render manifest JSON with hashes + slide count for auditability.
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import re
import subprocess
import sys
import zipfile
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import unquote

import numpy as np
from PIL import Image, ImageChops, ImageFilter

UNREPLACED_TOKEN_RE = re.compile(r"\{\{[A-Z0-9_]+\}\}")
MD_IMAGE_RE = re.compile(r"!\[[^\]]*]\(([^)]+)\)")
HTML_IMAGE_RE = re.compile(r"<img[^>]+src=['\"]([^'\"]+)['\"][^>]*>", re.IGNORECASE)
PPTX_SLIDE_RE = re.compile(r"^ppt/slides/slide\d+\.xml$")
PPTX_SLIDE_IMAGE_RE = re.compile(r"^ppt/media/Slide-(\d+)-image-1\.(png|jpe?g)$", re.IGNORECASE)
URL_SCHEME_RE = re.compile(r"^[a-zA-Z][a-zA-Z0-9+.-]*://")
CORE_XML_CREATED_RE = re.compile(r"(<dcterms:created[^>]*>)[^<]+(</dcterms:created>)")
CORE_XML_MODIFIED_RE = re.compile(r"(<dcterms:modified[^>]*>)[^<]+(</dcterms:modified>)")
FIXED_RENDERED_AT = "1980-01-01T00:00:00Z"

EMOJI_RANGES: tuple[tuple[int, int], ...] = (
    (0x1F1E6, 0x1F1FF),  # flags
    (0x1F300, 0x1F5FF),  # symbols & pictographs
    (0x1F600, 0x1F64F),  # emoticons
    (0x1F680, 0x1F6FF),  # transport & map
    (0x1F700, 0x1F77F),  # alchemical symbols
    (0x1F780, 0x1F7FF),  # geometric shapes extended
    (0x1F800, 0x1F8FF),  # arrows
    (0x1F900, 0x1F9FF),  # supplemental symbols & pictographs
    (0x1FA00, 0x1FA6F),  # chess symbols, etc.
    (0x1FA70, 0x1FAFF),  # symbols & pictographs extended-A
    (0x2600, 0x26FF),  # misc symbols
    (0x2700, 0x27BF),  # dingbats
)


@dataclass(frozen=True)
class FileInfo:
    path: str
    bytes: int
    sha256: str


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def file_info(path: Path) -> FileInfo:
    return FileInfo(
        path=str(path),
        bytes=path.stat().st_size,
        sha256=sha256_file(path),
    )


def marp_version(marp_bin: str) -> str:
    proc = subprocess.run([marp_bin, "--version"], capture_output=True, text=True)
    out = (proc.stdout or proc.stderr or "").strip()
    return out


def run_marp(marp_bin: str, md_path: Path, out_path: Path, extra_args: list[str]) -> None:
    cmd = [
        marp_bin,
        str(md_path),
        "-o",
        str(out_path),
        "--allow-local-files",
        "--no-stdin",
        *extra_args,
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError((proc.stderr or proc.stdout or "").strip() or "Marp failed")


def extract_unreplaced_tokens(text: str) -> list[str]:
    return sorted(set(UNREPLACED_TOKEN_RE.findall(text)))


def is_emoji_char(ch: str) -> bool:
    cp = ord(ch)
    if cp in {0xFE0F, 0x200D}:  # variation selector-16, zero-width joiner
        return True
    for lo, hi in EMOJI_RANGES:
        if lo <= cp <= hi:
            return True
    return False


def find_emoji_lines(text: str, *, max_lines: int = 50) -> list[str]:
    """
    Return human-readable violations with 1-based line numbers.
    Conservative check: reject common emoji codepoint ranges + VS16/ZWJ sequences.
    """
    violations: list[str] = []
    for i, line in enumerate(text.splitlines(), start=1):
        emojis = sorted({ch for ch in line if is_emoji_char(ch)})
        if not emojis:
            continue
        snippet = line.strip()
        if len(snippet) > 140:
            snippet = snippet[:139] + "…"
        violations.append(f"Line {i}: {''.join(emojis)} :: {snippet}")
        if len(violations) >= max_lines:
            break
    return violations


def _normalize_md_link_target(raw: str) -> str:
    target = raw.strip()

    # Handle <path with spaces>
    if target.startswith("<") and target.endswith(">"):
        target = target[1:-1].strip()

    # Remove optional title: (path "title")
    target = target.split()[0].strip()
    target = target.strip("'\"")
    return target


def extract_image_refs(text: str) -> list[str]:
    refs: set[str] = set()

    for m in MD_IMAGE_RE.finditer(text):
        refs.add(_normalize_md_link_target(m.group(1)))

    for m in HTML_IMAGE_RE.finditer(text):
        refs.add(m.group(1).strip())

    return sorted(refs)


def is_remote_ref(ref: str) -> bool:
    if ref.startswith("data:"):
        return True
    return bool(URL_SCHEME_RE.match(ref))


def resolve_local_ref(md_path: Path, ref: str) -> Path:
    decoded = unquote(ref)
    # If someone wrote absolute paths, preserve them; else resolve relative to the md file.
    candidate = Path(decoded)
    if candidate.is_absolute():
        return candidate
    return (md_path.parent / candidate).resolve()


def pptx_slide_count(pptx_path: Path) -> int:
    with zipfile.ZipFile(pptx_path, "r") as z:
        slides = [name for name in z.namelist() if PPTX_SLIDE_RE.match(name)]
    return len(slides)


def normalize_core_xml(xml_bytes: bytes, *, fixed_iso_utc: str) -> bytes:
    """
    Marp PPTX exports include created/modified timestamps that change every run.
    Normalize these to keep PPTX bytes stable when the markdown source is identical.
    """
    try:
        text = xml_bytes.decode("utf-8")
    except Exception:
        return xml_bytes

    text2 = CORE_XML_CREATED_RE.sub(rf"\\1{fixed_iso_utc}\\2", text)
    text2 = CORE_XML_MODIFIED_RE.sub(rf"\\1{fixed_iso_utc}\\2", text2)
    return text2.encode("utf-8")


def normalize_pptx_for_determinism(pptx_path: Path) -> dict[str, str]:
    """
    Rewrite the PPTX zip with:
    - fixed ZipInfo timestamps
    - normalized docProps/core.xml created/modified timestamps

    Returns normalization metadata for the render manifest.
    """
    fixed_iso = "1980-01-01T00:00:00Z"
    fixed_zip_dt = (1980, 1, 1, 0, 0, 0)  # minimum valid zip datetime

    tmp = pptx_path.with_suffix(".pptx.tmp")
    with zipfile.ZipFile(pptx_path, "r") as zin:
        entries: list[tuple[str, bytes, bool]] = []
        for name in zin.namelist():
            is_dir = name.endswith("/")
            data = b"" if is_dir else zin.read(name)
            if name == "docProps/core.xml" and not is_dir:
                data = normalize_core_xml(data, fixed_iso_utc=fixed_iso)
            entries.append((name, data, is_dir))

    with zipfile.ZipFile(tmp, "w") as zout:
        for name, data, is_dir in sorted(entries, key=lambda x: x[0]):
            info = zipfile.ZipInfo(name)
            info.date_time = fixed_zip_dt
            if is_dir:
                info.external_attr = 0o40775 << 16  # mark as directory on unixy unzip tools
                zout.writestr(info, b"", compress_type=zipfile.ZIP_STORED)
            else:
                zout.writestr(info, data, compress_type=zipfile.ZIP_DEFLATED)

    tmp.replace(pptx_path)
    return {"fixed_iso_utc": fixed_iso, "fixed_zip_datetime": "-".join(map(str, fixed_zip_dt))}


def md_slide_separators_count(md_text: str) -> int:
    """
    Best-effort slide count for a Marp markdown file:
    - ignore YAML frontmatter fenced by leading '---' ... '---'
    - count slide separators as lines that are exactly '---'
    """
    lines = md_text.splitlines()
    i = 0

    # Skip leading empty lines
    while i < len(lines) and not lines[i].strip():
        i += 1

    # Detect YAML frontmatter
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


def extract_slide_images(pptx_path: Path) -> dict[int, bytes]:
    """
    Marp PPTX exports commonly embed each slide as a full-slide image.
    Extract those images keyed by slide number.
    """
    out: dict[int, bytes] = {}
    with zipfile.ZipFile(pptx_path, "r") as z:
        for name in z.namelist():
            m = PPTX_SLIDE_IMAGE_RE.match(name)
            if not m:
                continue
            slide_num = int(m.group(1))
            out[slide_num] = z.read(name)
    return out


def slide_content_margins(
    image_bytes: bytes,
    *,
    analysis_size: tuple[int, int] = (1280, 720),
    blur_radius: float = 3.0,
    diff_threshold: int = 20,
    trim_percentile: float = 1.0,
) -> dict[str, int] | None:
    """
    Heuristic, deterministic margin check:
    - downscale to analysis_size for stable thresholds
    - blur the image and take abs diff to highlight high-frequency content (text/tables/charts)
    - compute a trimmed bounding box of the diff mask to ignore tiny edge artifacts

    Returns margins (left/top/right/bottom) in pixels at analysis_size, or None if no content was detected.
    """
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    if img.size != analysis_size:
        img = img.resize(analysis_size, Image.Resampling.BILINEAR)

    blurred = img.filter(ImageFilter.GaussianBlur(radius=blur_radius))
    diff = ImageChops.difference(img, blurred).convert("L")
    arr = np.array(diff, dtype=np.uint8)
    mask = arr > diff_threshold
    if not mask.any():
        return None

    ys, xs = np.where(mask)
    lo = float(trim_percentile)
    hi = 100.0 - lo
    x1 = int(np.percentile(xs, lo))
    x2 = int(np.percentile(xs, hi))
    y1 = int(np.percentile(ys, lo))
    y2 = int(np.percentile(ys, hi))

    w, h = analysis_size
    return {"left": x1, "top": y1, "right": (w - 1 - x2), "bottom": (h - 1 - y2)}


def main() -> None:
    parser = argparse.ArgumentParser(description="Render + verify a Marp deck from a populated markdown file.")
    parser.add_argument("md_path", type=Path, help="Path to populated Marp markdown (source of truth).")
    parser.add_argument("--marp", default="marp", help="Marp CLI binary (default: marp).")
    parser.add_argument("--min-left", type=int, default=40, help="Min left whitespace margin (px at 1280x720 analysis size).")
    parser.add_argument("--min-right", type=int, default=40, help="Min right whitespace margin (px at 1280x720 analysis size).")
    parser.add_argument("--min-top", type=int, default=20, help="Min top whitespace margin (px at 1280x720 analysis size).")
    parser.add_argument("--min-bottom", type=int, default=20, help="Min bottom whitespace margin (px at 1280x720 analysis size).")
    args = parser.parse_args()

    md_path: Path = args.md_path
    if not md_path.exists():
        raise SystemExit(f"Markdown not found: {md_path}")

    md_text = md_path.read_text(encoding="utf-8")

    unreplaced = extract_unreplaced_tokens(md_text)
    if unreplaced:
        raise SystemExit(
            "Unreplaced template variables found. Resolve before rendering:\n"
            + "\n".join(f"- {t}" for t in unreplaced)
        )

    emoji_lines = find_emoji_lines(md_text)
    if emoji_lines:
        raise SystemExit(
            "Emoji characters detected in the deck markdown (client decks must be emoji-free). Remove them and re-render:\n"
            + "\n".join(f"- {v}" for v in emoji_lines)
        )

    image_refs = extract_image_refs(md_text)
    missing_images: list[str] = []
    checked_images: list[str] = []
    for ref in image_refs:
        if not ref or is_remote_ref(ref):
            continue
        local_path = resolve_local_ref(md_path, ref)
        checked_images.append(f"{ref} -> {local_path}")
        if not local_path.exists():
            missing_images.append(ref)

    if missing_images:
        raise SystemExit(
            "Missing local images referenced by markdown. Fix paths or generate charts:\n"
            + "\n".join(f"- {p}" for p in sorted(missing_images))
        )

    html_path = md_path.with_suffix(".html")
    pptx_path = md_path.with_suffix(".pptx")

    # Render
    run_marp(args.marp, md_path, html_path, ["--html"])
    run_marp(args.marp, md_path, pptx_path, [])

    if not html_path.exists() or html_path.stat().st_size < 1000:
        raise SystemExit(f"HTML output missing/too small: {html_path}")
    if not pptx_path.exists() or pptx_path.stat().st_size < 1000:
        raise SystemExit(f"PPTX output missing/too small: {pptx_path}")

    normalization = normalize_pptx_for_determinism(pptx_path)

    pptx_slides = pptx_slide_count(pptx_path)
    if pptx_slides <= 0:
        raise SystemExit("PPTX slide count is 0 (unexpected).")

    md_seps = md_slide_separators_count(md_text)
    # Approximate slide count: separators + 1 (post-frontmatter).
    md_slides_est = md_seps + 1
    if pptx_slides != md_slides_est:
        raise SystemExit(
            f"Slide count mismatch (PPTX vs markdown): pptx={pptx_slides}, md_estimate={md_slides_est}. "
            "Check for malformed slide separators ('---') or Marp rendering errors."
        )

    # ------------------------------------------------------------------
    # Slide-by-slide whitespace verification (PPTX slide images)
    # ------------------------------------------------------------------
    slide_images = extract_slide_images(pptx_path)
    if not slide_images:
        raise SystemExit(
            "Could not find per-slide images inside the PPTX (expected Marp-style Slide-<n>-image-1.*).\n"
            "Cannot run automated whitespace QA; open the PPTX and review slide-by-slide."
        )

    margin_requirements = {"left": args.min_left, "right": args.min_right, "top": args.min_top, "bottom": args.min_bottom}
    slide_margin_rows: list[dict[str, object]] = []
    margin_violations: list[dict[str, object]] = []

    for slide_num in range(1, pptx_slides + 1):
        img_bytes = slide_images.get(slide_num)
        if img_bytes is None:
            margin_violations.append(
                {"slide": slide_num, "error": "Missing slide image in PPTX (cannot verify whitespace)."}
            )
            continue

        margins = slide_content_margins(img_bytes)
        slide_margin_rows.append({"slide": slide_num, "margins": margins})

        if margins is None:
            continue

        bad_edges = {k: {"actual": int(margins[k]), "min": int(margin_requirements[k])} for k in margin_requirements if margins[k] < margin_requirements[k]}
        if bad_edges:
            margin_violations.append({"slide": slide_num, "bad_edges": bad_edges, "margins": margins})

    manifest = {
        # Deterministic: keep this stable so repeated renders of the same `.md` produce identical manifests.
        "rendered_at": FIXED_RENDERED_AT,
        "marp": {"bin": args.marp, "version": marp_version(args.marp)},
        "normalization": {"pptx": normalization},
        "source": file_info(md_path).__dict__,
        "checks": {
            "unreplaced_tokens": [],
            "images_checked": checked_images,
            "images_missing": [],
            "md_slide_count_estimate": md_slides_est,
            "pptx_slide_count": pptx_slides,
            "slide_whitespace": {
                "analysis_size": {"width": 1280, "height": 720},
                "min_margins_px": margin_requirements,
                "method": {"blur_radius": 3.0, "diff_threshold": 20, "trim_percentile": 1.0},
                "per_slide": slide_margin_rows,
                "violations": margin_violations,
            },
        },
        "outputs": {
            "html": file_info(html_path).__dict__,
            "pptx": file_info(pptx_path).__dict__,
        },
    }

    manifest_path = md_path.with_suffix(".render_manifest.json")
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    if margin_violations:
        failing = ", ".join(str(v.get("slide")) for v in margin_violations[:12])
        more = "" if len(margin_violations) <= 12 else f" (+{len(margin_violations) - 12} more)"
        raise SystemExit(
            "Slide whitespace QA failed (content too close to slide edges).\n"
            f"Failing slides: {failing}{more}\n"
            f"See: {manifest_path}"
        )

    print("[OK] Render + verification passed")
    print(f"[OK] HTML:  {html_path}")
    print(f"[OK] PPTX:  {pptx_path} ({pptx_slides} slides)")
    print(f"[OK] Manifest: {manifest_path}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nInterrupted.", file=sys.stderr)
        raise SystemExit(130)
