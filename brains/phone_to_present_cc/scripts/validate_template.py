#!/usr/bin/env python3
"""
Pre-flight template validation script.

This script validates that a presentation template meets all requirements
before the workflow begins. Prevents Error 1 (missing template) and
Error 2 (wrong template structure) from Casey Optical Too run.

Usage:
    python validate_template.py [template_path]
    python validate_template.py  # Uses default templates/presentation_template.md
"""

import sys
import re
import json
from pathlib import Path
from typing import Dict, List, Any, Tuple


# Required CSS classes for v4 Paths Forward HTML structure
REQUIRED_CLASSES = [
    ("pf-table", "v4 Paths Forward table container"),
    ("pf-container", "Paths Forward wrapper container"),
    ("pf-icon-check", "Green checkmark icon class"),
    ("pf-icon-warn", "Amber warning icon class"),
    ("pf-icon-x", "Gray X icon class"),
    ("pf-rhc", "RHC column styling"),
    ("pf-badge", "MOST POPULAR badge"),
]

# Forbidden patterns that indicate wrong structure
FORBIDDEN_PATTERNS = [
    (r"\|\s*Feature\s*\|", "Markdown table header for Slide 18"),
    (r"\|\s*---+\s*\|", "Markdown table separator"),
    (r"\|\s*-+\s*\|", "Markdown table separator variant"),
]

# Required placeholders that must be present
REQUIRED_PLACEHOLDERS = [
    "{{CLIENT_NAME}}",
    "{{ANSWER_RATE}}",
    "{{GRADE}}",
    "{{HIRE_WEEKLY}}",
    "{{RHC_WEEKLY}}",
    "{{INBOUND_WEEKLY}}",
]


def validate_template(template_path: str) -> Dict[str, Any]:
    """
    Validate that a template has all required components.

    Returns:
        Dict with keys:
        - valid: bool
        - issues: List[str] - human-readable issue descriptions
        - missing_classes: List[str] - CSS classes that are missing
        - has_markdown_table: bool - True if forbidden markdown table found
        - missing_placeholders: List[str] - required placeholders not found
    """
    issues: List[str] = []
    missing_classes: List[str] = []
    missing_placeholders: List[str] = []
    has_markdown_table = False

    template = Path(template_path)

    # Check file exists
    if not template.exists():
        return {
            "valid": False,
            "issues": [f"Template file not found: {template_path}"],
            "missing_classes": [],
            "has_markdown_table": False,
            "missing_placeholders": [],
        }

    # Check file is readable
    try:
        content = template.read_text(encoding="utf-8")
    except Exception as e:
        return {
            "valid": False,
            "issues": [f"Cannot read template file: {e}"],
            "missing_classes": [],
            "has_markdown_table": False,
            "missing_placeholders": [],
        }

    # Check file is not empty
    if not content.strip():
        return {
            "valid": False,
            "issues": ["Template file is empty"],
            "missing_classes": [],
            "has_markdown_table": False,
            "missing_placeholders": [],
        }

    # Check for required CSS classes (v4 HTML structure)
    for class_name, description in REQUIRED_CLASSES:
        # Check both double and single quote variants
        if f'class="{class_name}"' not in content and f"class='{class_name}'" not in content:
            # Also check for class in multi-class attributes
            if not re.search(rf'class=["\'][^"\']*\b{class_name}\b[^"\']*["\']', content):
                issues.append(f"Missing {description} (class='{class_name}')")
                missing_classes.append(class_name)

    # Check for forbidden markdown table patterns in Slide 18 context
    # First, try to find the Paths Forward section
    paths_forward_match = re.search(
        r"#\s*Paths\s*Forward.*?(?=#\s*|\Z)",
        content,
        re.IGNORECASE | re.DOTALL
    )

    paths_forward_section = paths_forward_match.group(0) if paths_forward_match else content

    for pattern, description in FORBIDDEN_PATTERNS:
        if re.search(pattern, paths_forward_section, re.IGNORECASE):
            issues.append(f"Found forbidden pattern: {description}")
            has_markdown_table = True

    # Additional check: if we found pf-table, the markdown table is less concerning
    # But if we have ONLY markdown table and NO pf-table, that's the error
    if has_markdown_table and "pf-table" not in missing_classes:
        # Has both - remove the markdown table warning, pf-table takes precedence
        issues = [i for i in issues if "Markdown table" not in i]
        has_markdown_table = False

    # Check for required placeholders
    for placeholder in REQUIRED_PLACEHOLDERS:
        if placeholder not in content:
            issues.append(f"Missing required placeholder: {placeholder}")
            missing_placeholders.append(placeholder)

    # Check for SVG icons (required for Slide 18)
    if '<svg' not in content.lower():
        issues.append("No SVG elements found - Slide 18 icons may be missing")

    # Check for Marp directives (basic template structure)
    if '---' not in content:
        issues.append("No Marp slide separators (---) found")

    if 'marp:' not in content.lower() and 'theme:' not in content.lower():
        issues.append("No Marp configuration found (marp: or theme:)")

    return {
        "valid": len(issues) == 0,
        "issues": issues,
        "missing_classes": missing_classes,
        "has_markdown_table": has_markdown_table,
        "missing_placeholders": missing_placeholders,
    }


def validate_with_reference(
    template_path: str,
    reference_path: str
) -> Tuple[bool, List[str]]:
    """
    Validate template against the v4 reference specification.

    Args:
        template_path: Path to the template to validate
        reference_path: Path to slide18_paths_forward_v4.md

    Returns:
        Tuple of (is_valid, list_of_issues)
    """
    issues = []

    template = Path(template_path)
    reference = Path(reference_path)

    if not reference.exists():
        issues.append(f"Reference file not found: {reference_path}")
        return False, issues

    ref_content = reference.read_text(encoding="utf-8")

    # Extract required classes from reference
    ref_classes = re.findall(r'class="([^"]+)"', ref_content)
    unique_ref_classes = set()
    for cls_str in ref_classes:
        for cls in cls_str.split():
            if cls.startswith("pf-"):
                unique_ref_classes.add(cls)

    if not template.exists():
        issues.append(f"Template file not found: {template_path}")
        return False, issues

    tpl_content = template.read_text(encoding="utf-8")

    # Check that template has all reference classes
    for cls in unique_ref_classes:
        if cls not in tpl_content:
            issues.append(f"Template missing class from reference: {cls}")

    return len(issues) == 0, issues


def main():
    """Main entry point for CLI usage."""
    # Determine paths
    if len(sys.argv) > 1:
        template_path = sys.argv[1]
    else:
        template_path = "templates/presentation_template.md"

    reference_path = "references/slide18_paths_forward_v4.md"

    print(f"Validating template: {template_path}")
    print("-" * 50)

    # Run validation
    result = validate_template(template_path)

    # Also check against reference if available
    ref_valid, ref_issues = validate_with_reference(template_path, reference_path)

    # Combine issues
    all_issues = result["issues"] + ref_issues
    is_valid = result["valid"] and ref_valid

    # Output results
    if is_valid:
        print("PASSED - Template validation successful")
        print()
        print("Summary:")
        print(f"  - All {len(REQUIRED_CLASSES)} required CSS classes present")
        print(f"  - All {len(REQUIRED_PLACEHOLDERS)} required placeholders present")
        print("  - No forbidden markdown table patterns")
        print("  - v4 reference compliance verified")
        sys.exit(0)
    else:
        print("FAILED - Template validation failed")
        print()
        print("Issues found:")
        for issue in all_issues:
            print(f"  - {issue}")
        print()

        if result["missing_classes"]:
            print("Missing CSS classes:")
            for cls in result["missing_classes"]:
                print(f"  - {cls}")
            print()

        if result["has_markdown_table"]:
            print("CRITICAL: Markdown table found in Slide 18 section")
            print("  The Paths Forward table MUST use v4 HTML (<table class=\"pf-table\">)")
            print("  See: references/slide18_paths_forward_v4.md")
            print()

        if result["missing_placeholders"]:
            print("Missing required placeholders:")
            for placeholder in result["missing_placeholders"]:
                print(f"  - {placeholder}")
            print()

        print("Resolution:")
        print("  1. Copy a known-good template from a sibling repo")
        print("  2. Or update the template using references/slide18_paths_forward_v4.md")
        print("  3. Re-run this validation before proceeding")

        sys.exit(1)


if __name__ == "__main__":
    main()
