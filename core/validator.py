"""
Brain Validator - Validates brain configurations for LLM enforcement compliance.

This module provides validation utilities to ensure that brain configurations
include proper guardrails for preventing LLM deviation. It checks that brains
have appropriate stop rules, must_do/must_not constraints, and validation rules.

Based on lessons learned from the Casey Optical Too workflow errors:
- Error 1: Missing template file - generated from scratch instead of stopping
- Error 2: Template version mismatch - wrong HTML structure used
- Error 3: Incomplete data population
- Error 4: Pricing minimum not enforced
- Error 5: FTE minimum hours not enforced
- Error 6: Chart verification skipped
- Error 7: Slide-specific validation issues
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, field
import yaml

from .brain import Brain, BrainManifest, StopRule, Constraint


@dataclass
class ValidationResult:
    """Result of a brain validation check."""
    valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)

    def add_error(self, message: str) -> None:
        self.errors.append(message)
        self.valid = False

    def add_warning(self, message: str) -> None:
        self.warnings.append(message)

    def add_suggestion(self, message: str) -> None:
        self.suggestions.append(message)

    def merge(self, other: "ValidationResult") -> None:
        """Merge another result into this one."""
        if not other.valid:
            self.valid = False
        self.errors.extend(other.errors)
        self.warnings.extend(other.warnings)
        self.suggestions.extend(other.suggestions)


# ═══════════════════════════════════════════════════════════════════
# REQUIRED PATTERNS - Things every brain should have
# ═══════════════════════════════════════════════════════════════════

# Minimum stop rules that should exist in any production brain
RECOMMENDED_STOP_RULE_PATTERNS = [
    "missing",      # Should have rules for missing files
    "minimum",      # Should have rules for minimum values
    "quality",      # Should have rules for data quality thresholds
    "validation",   # Should have rules for validation failures
]

# Constraint patterns that should exist
RECOMMENDED_MUST_DO_PATTERNS = [
    "confirm",      # Should confirm inputs with user
    "validate",     # Should validate outputs
    "verify",       # Should verify files exist
]

RECOMMENDED_MUST_NOT_PATTERNS = [
    "generate",     # Should not generate from scratch when template missing
    "skip",         # Should not skip validation
    "assume",       # Should not assume values
]


def validate_brain_structure(brain_path: Path) -> ValidationResult:
    """
    Validate that a brain directory has the required structure.

    Checks:
    - brain.yaml exists and is valid
    - graph.yaml exists and is valid
    - state.yaml exists (optional but recommended)
    - config/ directory exists with pricing constants
    - references/ directory exists
    - skills/ directory exists

    Args:
        brain_path: Path to the brain directory

    Returns:
        ValidationResult with any errors or warnings
    """
    result = ValidationResult(valid=True)

    # Required files
    required_files = [
        ("brain.yaml", "Brain manifest"),
        ("graph.yaml", "Execution graph"),
    ]

    for filename, description in required_files:
        file_path = brain_path / filename
        if not file_path.exists():
            result.add_error(f"Missing required file: {filename} ({description})")

    # Recommended files
    recommended_files = [
        ("state.yaml", "State template"),
        ("config/pricing_constants.yaml", "Pricing constants"),
    ]

    for filename, description in recommended_files:
        file_path = brain_path / filename
        if not file_path.exists():
            result.add_warning(f"Missing recommended file: {filename} ({description})")

    # Recommended directories
    recommended_dirs = [
        ("references", "Reference specifications"),
        ("skills", "Skill definitions"),
        ("scripts", "Validation scripts"),
    ]

    for dirname, description in recommended_dirs:
        dir_path = brain_path / dirname
        if not dir_path.exists():
            result.add_suggestion(f"Consider adding: {dirname}/ ({description})")

    return result


def validate_stop_rules(manifest: BrainManifest) -> ValidationResult:
    """
    Validate that a brain has appropriate stop rules.

    Stop rules are critical for preventing LLM deviation. A brain without
    stop rules will allow the LLM to improvise when it should ask the user.

    Args:
        manifest: The brain manifest to validate

    Returns:
        ValidationResult with any errors or warnings
    """
    result = ValidationResult(valid=True)

    if not manifest.stop_rules:
        result.add_warning(
            "No stop rules defined - LLM may improvise instead of asking user"
        )
        result.add_suggestion(
            "Add stop_rules in constraints section for: missing files, "
            "minimum values, data quality thresholds"
        )
        return result

    # Check for recommended patterns
    rule_text = " ".join(sr.condition.lower() for sr in manifest.stop_rules)

    for pattern in RECOMMENDED_STOP_RULE_PATTERNS:
        if pattern not in rule_text:
            result.add_suggestion(
                f"Consider adding stop rule for '{pattern}' conditions"
            )

    # Check that stop rules have actions defined
    for i, sr in enumerate(manifest.stop_rules):
        if not sr.action:
            result.add_warning(
                f"Stop rule {i+1} has no action defined - "
                f"condition: '{sr.condition[:50]}...'"
            )

    return result


def validate_constraints(manifest: BrainManifest) -> ValidationResult:
    """
    Validate that a brain has appropriate must_do/must_not constraints.

    Constraints define the guardrails for LLM behavior. Without them,
    the LLM may skip important steps or do things it shouldn't.

    Args:
        manifest: The brain manifest to validate

    Returns:
        ValidationResult with any errors or warnings
    """
    result = ValidationResult(valid=True)

    must_do = [c for c in manifest.constraints if c.type == "must_do"]
    must_not = [c for c in manifest.constraints if c.type == "must_not"]

    if not must_do:
        result.add_warning(
            "No must_do constraints defined - LLM may skip required steps"
        )

    if not must_not:
        result.add_warning(
            "No must_not constraints defined - LLM may do forbidden actions"
        )

    # Check for recommended patterns in must_do
    if must_do:
        must_do_text = " ".join(c.description.lower() for c in must_do)
        for pattern in RECOMMENDED_MUST_DO_PATTERNS:
            if pattern not in must_do_text:
                result.add_suggestion(
                    f"Consider adding must_do constraint for '{pattern}'"
                )

    # Check for recommended patterns in must_not
    if must_not:
        must_not_text = " ".join(c.description.lower() for c in must_not)
        for pattern in RECOMMENDED_MUST_NOT_PATTERNS:
            if pattern not in must_not_text:
                result.add_suggestion(
                    f"Consider adding must_not constraint for '{pattern}'"
                )

    return result


def validate_minimum_enforcements(manifest: BrainManifest) -> ValidationResult:
    """
    Validate minimum enforcement configurations.

    Minimum enforcements ensure that calculated values meet business
    requirements. Without them, the LLM may output invalid values.

    Args:
        manifest: The brain manifest to validate

    Returns:
        ValidationResult with any errors or warnings
    """
    result = ValidationResult(valid=True)

    if not manifest.minimum_enforcements:
        # Check if config has pricing minimums
        pricing_minimums = manifest.config.get("pricing_minimums", {})
        if pricing_minimums:
            result.add_suggestion(
                "pricing_minimums defined in config but no minimum_enforcements - "
                "consider adding enforcement rules"
            )
        return result

    for me in manifest.minimum_enforcements:
        if me.minimum <= 0:
            result.add_warning(
                f"Minimum enforcement for '{me.field}' has minimum <= 0"
            )

        if not me.error_message:
            result.add_warning(
                f"Minimum enforcement for '{me.field}' has no error message"
            )

    return result


def validate_config(manifest: BrainManifest) -> ValidationResult:
    """
    Validate the business configuration in a brain manifest.

    Checks that required configuration sections exist and have
    reasonable values.

    Args:
        manifest: The brain manifest to validate

    Returns:
        ValidationResult with any errors or warnings
    """
    result = ValidationResult(valid=True)

    config = manifest.config

    if not config:
        result.add_warning(
            "No config section defined - business rules may not be enforced"
        )
        return result

    # Check for common config sections
    recommended_sections = [
        ("pricing_minimums", "Minimum pricing values"),
        ("coverage_minimums", "Minimum coverage/hours values"),
        ("thresholds", "Quality and validation thresholds"),
    ]

    for section, description in recommended_sections:
        if section not in config:
            result.add_suggestion(
                f"Consider adding config.{section} ({description})"
            )

    return result


def validate_brain(brain: Brain) -> ValidationResult:
    """
    Comprehensive validation of a brain for LLM enforcement compliance.

    This is the main validation entry point that runs all checks.

    Args:
        brain: The brain to validate

    Returns:
        ValidationResult with all errors, warnings, and suggestions
    """
    result = ValidationResult(valid=True)

    # Load the brain if not already loaded
    if not brain._loaded:
        try:
            brain.load()
        except Exception as e:
            result.add_error(f"Failed to load brain: {e}")
            return result

    manifest = brain.manifest

    # Validate structure
    structure_result = validate_brain_structure(brain.path)
    result.merge(structure_result)

    # Validate stop rules
    stop_rules_result = validate_stop_rules(manifest)
    result.merge(stop_rules_result)

    # Validate constraints
    constraints_result = validate_constraints(manifest)
    result.merge(constraints_result)

    # Validate minimum enforcements
    minimums_result = validate_minimum_enforcements(manifest)
    result.merge(minimums_result)

    # Validate config
    config_result = validate_config(manifest)
    result.merge(config_result)

    return result


def validate_brain_from_path(brain_path: str) -> ValidationResult:
    """
    Validate a brain from a file path.

    Args:
        brain_path: Path to the brain directory

    Returns:
        ValidationResult with all errors, warnings, and suggestions
    """
    path = Path(brain_path)
    brain = Brain(path)
    return validate_brain(brain)


# ═══════════════════════════════════════════════════════════════════
# TEMPLATE VALIDATION
# ═══════════════════════════════════════════════════════════════════

def validate_brain_has_template_rules(manifest: BrainManifest) -> ValidationResult:
    """
    Validate that a brain has proper template handling rules.

    Based on Error 1 from Casey Optical Too: LLM generated presentation
    from scratch when template was missing instead of stopping.

    Args:
        manifest: The brain manifest to validate

    Returns:
        ValidationResult
    """
    result = ValidationResult(valid=True)

    # Check stop rules for template-related conditions
    has_template_stop = False
    for sr in manifest.stop_rules:
        if "template" in sr.condition.lower() and "missing" in sr.condition.lower():
            has_template_stop = True
            break

    if not has_template_stop:
        result.add_warning(
            "No stop rule for missing template - LLM may generate from scratch"
        )
        result.add_suggestion(
            "Add stop_rule: 'templates/presentation_template.md is missing' -> "
            "'STOP and ask user - DO NOT generate from scratch'"
        )

    # Check must_not for template-related constraints
    has_no_generate = False
    for c in manifest.constraints:
        if c.type == "must_not" and "generate" in c.description.lower():
            has_no_generate = True
            break

    if not has_no_generate:
        result.add_suggestion(
            "Add must_not constraint: 'Generate presentation content from scratch "
            "when template is missing - ALWAYS stop and ask'"
        )

    return result


# ═══════════════════════════════════════════════════════════════════
# PRICING VALIDATION
# ═══════════════════════════════════════════════════════════════════

def validate_brain_has_pricing_rules(manifest: BrainManifest) -> ValidationResult:
    """
    Validate that a brain has proper pricing enforcement rules.

    Based on Error 4 from Casey Optical Too: pricing was calculated
    below the minimum without enforcement.

    Args:
        manifest: The brain manifest to validate

    Returns:
        ValidationResult
    """
    result = ValidationResult(valid=True)

    # Check for pricing minimums in config
    pricing_minimums = manifest.config.get("pricing_minimums", {})
    if not pricing_minimums:
        result.add_warning(
            "No pricing_minimums in config - pricing floors may not be enforced"
        )

    # Check for minimum enforcements related to pricing
    has_pricing_enforcement = False
    for me in manifest.minimum_enforcements:
        if "pricing" in me.field.lower() or "weekly" in me.field.lower():
            has_pricing_enforcement = True
            break

    if not has_pricing_enforcement and pricing_minimums:
        result.add_suggestion(
            "pricing_minimums defined but no minimum_enforcements for pricing fields"
        )

    # Check for stop rule about pricing below minimum
    has_pricing_stop = False
    for sr in manifest.stop_rules:
        if "pricing" in sr.condition.lower() and "minimum" in sr.condition.lower():
            has_pricing_stop = True
            break

    if not has_pricing_stop:
        result.add_suggestion(
            "Add stop_rule for calculated pricing below minimums"
        )

    return result


# ═══════════════════════════════════════════════════════════════════
# CLI ENTRY POINT
# ═══════════════════════════════════════════════════════════════════

def main():
    """CLI entry point for brain validation."""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python -m core.validator <brain_path>")
        print("       python -m core.validator brains/phone_to_present_cc")
        sys.exit(1)

    brain_path = sys.argv[1]
    print(f"Validating brain: {brain_path}")
    print("-" * 50)

    result = validate_brain_from_path(brain_path)

    if result.valid:
        print("PASSED - Brain validation successful")
    else:
        print("FAILED - Brain validation found errors")

    if result.errors:
        print()
        print(f"Errors ({len(result.errors)}):")
        for error in result.errors:
            print(f"  ERROR: {error}")

    if result.warnings:
        print()
        print(f"Warnings ({len(result.warnings)}):")
        for warning in result.warnings:
            print(f"  WARN: {warning}")

    if result.suggestions:
        print()
        print(f"Suggestions ({len(result.suggestions)}):")
        for suggestion in result.suggestions:
            print(f"  SUGGEST: {suggestion}")

    print()
    print("Summary:")
    print(f"  Errors: {len(result.errors)}")
    print(f"  Warnings: {len(result.warnings)}")
    print(f"  Suggestions: {len(result.suggestions)}")

    sys.exit(0 if result.valid else 1)


if __name__ == "__main__":
    main()
