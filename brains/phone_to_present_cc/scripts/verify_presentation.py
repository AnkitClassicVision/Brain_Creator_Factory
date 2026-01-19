#!/usr/bin/env python3
"""
Post-generation presentation verification script.

This script verifies that a generated presentation meets all requirements
before delivery. Prevents Error 3 (incomplete data), Error 6 (missing charts),
and Error 7 (slide issues) from Casey Optical Too run.

Usage:
    python verify_presentation.py <md_path> [html_path]
    python verify_presentation.py output/client/presentation.md
"""

import sys
import re
import os
import json
from pathlib import Path
from typing import Dict, List, Any, Tuple, Optional


# Minimum HTML file size (bytes) - a full deck should be at least this size
MIN_HTML_SIZE = 50000

# Required charts that must exist
REQUIRED_CHARTS = [
    "miss_distribution.png",
    "daily_volume.png",
    "hourly_volume.png",
    "heatmap.png",
    "concurrency_cdf.png",
    "grade_badge.png",
]

# Alternative chart names (some workflows use different names)
CHART_ALTERNATIVES = {
    "heatmap.png": ["pain_windows_heatmap.png", "heatmap_matrix.png"],
    "concurrency_cdf.png": ["fte_coverage.png", "cdf_chart.png"],
    "grade_badge.png": ["answer_rate_gauge.png", "grade_badge.svg"],
}

# Critical slides that must be validated
CRITICAL_SLIDES = {
    1: {
        "name": "Title",
        "required_populated": ["CLIENT_NAME"],
        "forbidden_patterns": [r"\{\{CLIENT_NAME\}\}"],
    },
    5: {
        "name": "Primary KPIs",
        "required_populated": ["ANSWER_RATE", "MISS_RATE", "GRADE"],
        "validation": {
            "ANSWER_RATE": r"\d+\.?\d*%?",  # Should be a number/percentage
            "GRADE": r"^[A-F]$",  # Should be a letter grade
        },
    },
    8: {
        "name": "Process vs Capacity",
        "required_images": ["miss_distribution.png"],
        "required_populated": ["PROCESS_MISS_PCT", "CAPACITY_MISS_PCT"],
    },
    18: {
        "name": "Paths Forward",
        "required_classes": ["pf-table"],
        "forbidden_patterns": [r"\|\s*---+\s*\|"],  # No markdown tables
        "required_populated": ["HIRE_WEEKLY", "RHC_WEEKLY", "INBOUND_WEEKLY"],
    },
}


def verify_presentation(
    md_path: str,
    html_path: Optional[str] = None
) -> Dict[str, Any]:
    """
    Verify a generated presentation meets all requirements.

    Args:
        md_path: Path to the markdown source file
        html_path: Path to the rendered HTML (optional, derived from md_path if not given)

    Returns:
        Dict with keys:
        - valid: bool
        - issues: List[str]
        - unreplaced_placeholders: List[str]
        - missing_images: List[str]
        - slide_issues: Dict[int, List[str]]
        - html_size: int
    """
    issues: List[str] = []
    unreplaced: List[str] = []
    missing_images: List[str] = []
    slide_issues: Dict[int, List[str]] = {}

    md_file = Path(md_path)
    html_size = 0

    # Derive HTML path if not provided
    if html_path is None:
        html_path = str(md_file.with_suffix(".html"))
    html_file = Path(html_path)

    # Check markdown source exists
    if not md_file.exists():
        return {
            "valid": False,
            "issues": [f"Markdown source not found: {md_path}"],
            "unreplaced_placeholders": [],
            "missing_images": [],
            "slide_issues": {},
            "html_size": 0,
        }

    try:
        md_content = md_file.read_text(encoding="utf-8")
    except Exception as e:
        return {
            "valid": False,
            "issues": [f"Cannot read markdown source: {e}"],
            "unreplaced_placeholders": [],
            "missing_images": [],
            "slide_issues": {},
            "html_size": 0,
        }

    # Check for unreplaced placeholders
    placeholders = re.findall(r"\{\{([^}]+)\}\}", md_content)
    if placeholders:
        unique_placeholders = sorted(set(placeholders))
        unreplaced = unique_placeholders
        issues.append(f"Found {len(unique_placeholders)} unreplaced placeholders")

    # Check for emoji characters (forbidden in client-facing materials)
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F300-\U0001F5FF"  # symbols & pictographs
        "\U0001F680-\U0001F6FF"  # transport & map symbols
        "\U0001F700-\U0001F77F"  # alchemical symbols
        "\U0001F780-\U0001F7FF"  # geometric shapes extended
        "\U0001F800-\U0001F8FF"  # supplemental arrows-c
        "\U0001F900-\U0001F9FF"  # supplemental symbols and pictographs
        "\U0001FA00-\U0001FA6F"  # chess symbols
        "\U0001FA70-\U0001FAFF"  # symbols and pictographs extended-a
        "\U00002702-\U000027B0"  # dingbats
        "]+",
        flags=re.UNICODE
    )
    emojis = emoji_pattern.findall(md_content)
    if emojis:
        issues.append(f"Found emoji characters in content (forbidden): {emojis[:5]}")

    # Check Slide 18 structure (v4 HTML requirement)
    if 'class="pf-table"' not in md_content and "class='pf-table'" not in md_content:
        issues.append("Slide 18 missing v4 HTML structure (no pf-table class)")
        slide_issues[18] = slide_issues.get(18, []) + ["Missing pf-table class"]

    # Check for markdown table in Paths Forward section
    paths_section = extract_slide_content(md_content, 18)
    if paths_section and re.search(r"\|\s*---+\s*\|", paths_section):
        issues.append("Slide 18 uses markdown table instead of v4 HTML")
        slide_issues[18] = slide_issues.get(18, []) + ["Uses markdown table instead of HTML"]

    # Check image references
    img_refs = re.findall(r"!\[.*?\]\(([^)]+)\)", md_content)
    parent_dir = md_file.parent

    for img_ref in img_refs:
        # Handle relative paths
        if img_ref.startswith("http"):
            continue  # Skip external URLs

        img_path = parent_dir / img_ref
        if not img_path.exists():
            missing_images.append(img_ref)

    if missing_images:
        issues.append(f"Found {len(missing_images)} missing image references")

    # Check required charts exist
    charts_dir = parent_dir / "charts"
    if charts_dir.exists():
        existing_charts = set(os.listdir(charts_dir))

        for required_chart in REQUIRED_CHARTS:
            found = False

            # Check primary name
            if required_chart in existing_charts:
                # Verify file size > 0
                chart_path = charts_dir / required_chart
                if chart_path.stat().st_size == 0:
                    issues.append(f"Chart file is empty (0 bytes): {required_chart}")
                else:
                    found = True

            # Check alternatives
            if not found and required_chart in CHART_ALTERNATIVES:
                for alt in CHART_ALTERNATIVES[required_chart]:
                    if alt in existing_charts:
                        alt_path = charts_dir / alt
                        if alt_path.stat().st_size > 0:
                            found = True
                            break

            if not found:
                issues.append(f"Required chart missing or empty: {required_chart}")
    else:
        issues.append("Charts directory not found")

    # Check HTML output if it exists
    if html_file.exists():
        try:
            html_content = html_file.read_text(encoding="utf-8")
            html_size = len(html_content)

            if html_size < MIN_HTML_SIZE:
                issues.append(
                    f"HTML file suspiciously small: {html_size} bytes "
                    f"(expected >= {MIN_HTML_SIZE})"
                )

            # Count slides in HTML
            slide_count = html_content.count("<section")
            if slide_count < 15:
                issues.append(f"HTML has only {slide_count} slides (expected ~20)")

            # Check for broken images in HTML
            broken_imgs = re.findall(r'<img[^>]+src="([^"]+)"[^>]*>', html_content)
            for img_src in broken_imgs:
                if not img_src.startswith("data:") and not img_src.startswith("http"):
                    img_path = parent_dir / img_src
                    if not img_path.exists():
                        if img_src not in missing_images:
                            missing_images.append(img_src)

        except Exception as e:
            issues.append(f"Error reading HTML file: {e}")
    else:
        issues.append(f"HTML output not found: {html_path}")

    # Validate critical slides content
    for slide_num, config in CRITICAL_SLIDES.items():
        slide_content = extract_slide_content(md_content, slide_num)
        if slide_content is None:
            slide_issues[slide_num] = [f"Slide {slide_num} ({config['name']}) not found"]
            continue

        slide_problems = []

        # Check forbidden patterns
        for pattern in config.get("forbidden_patterns", []):
            if re.search(pattern, slide_content):
                slide_problems.append(f"Contains forbidden pattern: {pattern}")

        # Check required classes
        for cls in config.get("required_classes", []):
            if f'class="{cls}"' not in slide_content and f"class='{cls}'" not in slide_content:
                slide_problems.append(f"Missing required class: {cls}")

        # Check required images
        for img in config.get("required_images", []):
            if img not in slide_content:
                slide_problems.append(f"Missing required image: {img}")

        if slide_problems:
            slide_issues[slide_num] = slide_problems

    return {
        "valid": len(issues) == 0,
        "issues": issues,
        "unreplaced_placeholders": unreplaced,
        "missing_images": missing_images,
        "slide_issues": slide_issues,
        "html_size": html_size,
    }


def extract_slide_content(content: str, slide_num: int) -> Optional[str]:
    """
    Extract content for a specific slide number.

    Assumes Marp format with --- separators.
    """
    slides = content.split("---")

    # Account for front matter (first --- is before it)
    # Actual slides start after front matter
    actual_slides = []
    in_frontmatter = True

    for i, slide in enumerate(slides):
        if in_frontmatter:
            # Front matter ends after first non-empty slide with content
            if slide.strip() and not slide.strip().startswith("marp:"):
                in_frontmatter = False
            continue
        actual_slides.append(slide)

    # slide_num is 1-indexed
    if 0 < slide_num <= len(actual_slides):
        return actual_slides[slide_num - 1]

    return None


def verify_charts_directory(charts_dir: str) -> Tuple[bool, List[str]]:
    """
    Verify all required charts exist and are valid.

    Returns:
        Tuple of (all_valid, list_of_issues)
    """
    issues = []
    charts_path = Path(charts_dir)

    if not charts_path.exists():
        return False, ["Charts directory does not exist"]

    for required_chart in REQUIRED_CHARTS:
        chart_path = charts_path / required_chart

        if not chart_path.exists():
            # Check alternatives
            found = False
            if required_chart in CHART_ALTERNATIVES:
                for alt in CHART_ALTERNATIVES[required_chart]:
                    alt_path = charts_path / alt
                    if alt_path.exists() and alt_path.stat().st_size > 0:
                        found = True
                        break

            if not found:
                issues.append(f"Missing chart: {required_chart}")
                continue

        # Check file size
        if chart_path.exists() and chart_path.stat().st_size == 0:
            issues.append(f"Empty chart file (0 bytes): {required_chart}")
            continue

        # Check file is valid PNG (magic bytes)
        if chart_path.exists():
            try:
                with open(chart_path, "rb") as f:
                    header = f.read(8)
                    png_magic = b"\x89PNG\r\n\x1a\n"
                    if header != png_magic:
                        issues.append(f"Invalid PNG file: {required_chart}")
            except Exception as e:
                issues.append(f"Cannot read chart file {required_chart}: {e}")

    return len(issues) == 0, issues


def main():
    """Main entry point for CLI usage."""
    if len(sys.argv) < 2:
        print("Usage: python verify_presentation.py <md_path> [html_path]")
        print("       python verify_presentation.py output/client/presentation.md")
        sys.exit(1)

    md_path = sys.argv[1]
    html_path = sys.argv[2] if len(sys.argv) > 2 else None

    print(f"Verifying presentation: {md_path}")
    if html_path:
        print(f"HTML output: {html_path}")
    print("-" * 50)

    # Run verification
    result = verify_presentation(md_path, html_path)

    # Output results
    if result["valid"]:
        print("PASSED - Presentation verification successful")
        print()
        print("Summary:")
        print(f"  - No unreplaced placeholders")
        print(f"  - All required images present")
        print(f"  - HTML size: {result['html_size']} bytes")
        print(f"  - All critical slides validated")
        sys.exit(0)
    else:
        print("FAILED - Presentation verification failed")
        print()
        print("Issues found:")
        for issue in result["issues"]:
            print(f"  - {issue}")
        print()

        if result["unreplaced_placeholders"]:
            print(f"Unreplaced placeholders ({len(result['unreplaced_placeholders'])}):")
            for placeholder in result["unreplaced_placeholders"][:10]:
                print(f"  - {{{{{placeholder}}}}}")
            if len(result["unreplaced_placeholders"]) > 10:
                print(f"  ... and {len(result['unreplaced_placeholders']) - 10} more")
            print()

        if result["missing_images"]:
            print(f"Missing images ({len(result['missing_images'])}):")
            for img in result["missing_images"]:
                print(f"  - {img}")
            print()

        if result["slide_issues"]:
            print("Critical slide issues:")
            for slide_num, problems in result["slide_issues"].items():
                slide_name = CRITICAL_SLIDES.get(slide_num, {}).get("name", "Unknown")
                print(f"  Slide {slide_num} ({slide_name}):")
                for problem in problems:
                    print(f"    - {problem}")
            print()

        print("Resolution:")
        print("  1. Fix unreplaced placeholders by re-running template population")
        print("  2. Regenerate missing charts")
        print("  3. Ensure Slide 18 uses v4 HTML (not markdown table)")
        print("  4. Re-render HTML and re-verify")

        sys.exit(1)


if __name__ == "__main__":
    main()
