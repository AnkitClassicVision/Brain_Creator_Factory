#!/usr/bin/env python3
"""
Verify key numeric outputs (FTE + pricing + missed-calls math) from a JSON manifest.

This is intended as a deterministic "checks & balances" layer:
- recompute FTE shrinkage rule
- recompute weekly costs for Inbound / RHC / In-house (internal formulas)
- validate weekly→monthly→annual conversions

Expected input: a JSON file with at least the keys you want verified.
Missing keys are skipped (script reports what's not checked).
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


@dataclass(frozen=True)
class Issue:
    level: str  # "CRITICAL" | "WARNING"
    message: str


def _get(d: dict[str, Any], key: str) -> Any:
    return d.get(key, None)


def _as_float(v: Any) -> float | None:
    if v is None:
        return None
    if isinstance(v, (int, float)):
        return float(v)
    try:
        return float(str(v).replace(",", "").replace("$", ""))
    except Exception:
        return None


def _as_bool(v: Any) -> bool | None:
    if v is None:
        return None
    if isinstance(v, bool):
        return v
    if isinstance(v, (int, float)):
        return bool(v)
    s = str(v).strip().lower()
    if s in {"true", "t", "yes", "y", "1"}:
        return True
    if s in {"false", "f", "no", "n", "0"}:
        return False
    return None


def approx_equal(a: float, b: float, *, tol: float) -> bool:
    return abs(a - b) <= tol


def verify_shrinkage(d: dict[str, Any]) -> tuple[list[Issue], list[str]]:
    issues: list[Issue] = []
    checked: list[str] = []

    base = _as_float(_get(d, "BASE_FTE"))
    shrink = _as_float(_get(d, "SHRINKAGE_FTE"))
    if base is None or shrink is None:
        return issues, checked

    expected = max(base / 0.80, 1.25)
    checked.append("SHRINKAGE_FTE rule (max(BASE/0.80, 1.25))")
    if not approx_equal(shrink, expected, tol=0.05):
        issues.append(Issue("WARNING", f"SHRINKAGE_FTE mismatch: expected ~{expected:.2f}, got {shrink:.2f}"))

    if base < 1.0:
        issues.append(Issue("WARNING", f"BASE_FTE is < 1.0 ({base:.2f}); expected floor at 1.0"))

    return issues, checked


def verify_pricing(d: dict[str, Any]) -> tuple[list[Issue], list[str]]:
    issues: list[Issue] = []
    checked: list[str] = []

    base = _as_float(_get(d, "BASE_FTE"))
    shrink = _as_float(_get(d, "SHRINKAGE_FTE"))
    ot_hours = _as_float(_get(d, "OT_HOURS")) or 0.0
    has_sat = _as_bool(_get(d, "HAS_SATURDAY")) or False
    has_sun = _as_bool(_get(d, "HAS_SUNDAY")) or False

    inbound_weekly = _as_float(_get(d, "INBOUND_WEEKLY"))
    rhc_weekly = _as_float(_get(d, "RHC_WEEKLY"))
    hire_weekly = _as_float(_get(d, "HIRE_WEEKLY"))

    if base is None or shrink is None:
        return issues, checked

    # Internal constants (overrideable via manifest if desired)
    mybcat_weekly_rate = _as_float(_get(d, "MYBCAT_WEEKLY_RATE")) or 480.0
    mybcat_ot_hourly = _as_float(_get(d, "MYBCAT_OT_HOURLY")) or 18.0
    inhouse_weekly_rate = _as_float(_get(d, "INHOUSE_WEEKLY_RATE")) or 960.0
    inhouse_ot_hourly = _as_float(_get(d, "INHOUSE_OT_HOURLY")) or 36.0
    weekend_premium = _as_float(_get(d, "WEEKEND_PREMIUM_PER_DAY")) or 25.0

    weekend_days = int(has_sat) + int(has_sun)

    # v2 headcount basis:
    # - Inbound (phones-only) uses BASE_FTE.
    # - RHC + In-house use SHRINKAGE_FTE.
    expected_inbound_weekly = mybcat_weekly_rate * base + mybcat_ot_hourly * base * ot_hours + weekend_premium * base * weekend_days
    expected_rhc_weekly = mybcat_weekly_rate * shrink + mybcat_ot_hourly * base * ot_hours + weekend_premium * base * weekend_days
    expected_hire_weekly = inhouse_weekly_rate * shrink + inhouse_ot_hourly * base * ot_hours + weekend_premium * base * weekend_days

    rhc_growth_addon_weekly = _as_float(_get(d, "RHC_GROWTH_ADDON_WEEKLY")) or 500.0
    rhc_growth_weekly = _as_float(_get(d, "RHC_GROWTH_WEEKLY"))
    expected_rhc_growth_weekly = expected_rhc_weekly + rhc_growth_addon_weekly

    # Compare if the fields exist
    if inbound_weekly is not None:
        checked.append("INBOUND_WEEKLY formula")
        if not approx_equal(inbound_weekly, expected_inbound_weekly, tol=5.0):
            issues.append(
                Issue(
                    "WARNING",
                    f"INBOUND_WEEKLY mismatch: expected ~{expected_inbound_weekly:.2f}, got {inbound_weekly:.2f}",
                )
            )

    if rhc_weekly is not None:
        checked.append("RHC_WEEKLY formula")
        if not approx_equal(rhc_weekly, expected_rhc_weekly, tol=5.0):
            issues.append(
                Issue("WARNING", f"RHC_WEEKLY mismatch: expected ~{expected_rhc_weekly:.2f}, got {rhc_weekly:.2f}")
            )

    if rhc_growth_weekly is not None:
        checked.append("RHC_GROWTH_WEEKLY formula")
        if not approx_equal(rhc_growth_weekly, expected_rhc_growth_weekly, tol=5.0):
            issues.append(
                Issue(
                    "WARNING",
                    f"RHC_GROWTH_WEEKLY mismatch: expected ~{expected_rhc_growth_weekly:.2f}, got {rhc_growth_weekly:.2f}",
                )
            )

    if hire_weekly is not None:
        checked.append("HIRE_WEEKLY formula")
        if not approx_equal(hire_weekly, expected_hire_weekly, tol=5.0):
            issues.append(
                Issue(
                    "WARNING",
                    f"HIRE_WEEKLY mismatch: expected ~{expected_hire_weekly:.2f}, got {hire_weekly:.2f}",
                )
            )

    # Sanity relationships (only if the values exist)
    if inbound_weekly is not None and rhc_weekly is not None and rhc_weekly < inbound_weekly:
        issues.append(Issue("WARNING", "RHC_WEEKLY < INBOUND_WEEKLY (unexpected). Verify inputs and rounding."))
    if rhc_weekly is not None and rhc_growth_weekly is not None and rhc_growth_weekly < rhc_weekly:
        issues.append(Issue("WARNING", "RHC_GROWTH_WEEKLY < RHC_WEEKLY (unexpected). Verify addon amount."))
    if inbound_weekly is not None and hire_weekly is not None and hire_weekly < inbound_weekly:
        issues.append(Issue("WARNING", "HIRE_WEEKLY < INBOUND_WEEKLY (unexpected). Verify rates and hours."))

    # Weekly → monthly → annual conversions (best-effort)
    weekly_to_monthly = 4.33
    for prefix in ("INBOUND", "RHC", "RHC_GROWTH", "HIRE"):
        w = _as_float(_get(d, f"{prefix}_WEEKLY"))
        m = _as_float(_get(d, f"{prefix}_MONTHLY"))
        a = _as_float(_get(d, f"{prefix}_ANNUAL"))
        if w is not None and m is not None:
            checked.append(f"{prefix}_MONTHLY ~= {prefix}_WEEKLY * 4.33")
            if not approx_equal(m, w * weekly_to_monthly, tol=10.0):
                issues.append(Issue("WARNING", f"{prefix}_MONTHLY mismatch (expected ~{w * weekly_to_monthly:.2f}, got {m:.2f})"))
        if m is not None and a is not None:
            checked.append(f"{prefix}_ANNUAL ~= {prefix}_MONTHLY * 12")
            if not approx_equal(a, m * 12.0, tol=25.0):
                issues.append(Issue("WARNING", f"{prefix}_ANNUAL mismatch (expected ~{m * 12.0:.2f}, got {a:.2f})"))

    return issues, checked


def verify_missed_calls(d: dict[str, Any]) -> tuple[list[Issue], list[str]]:
    issues: list[Issue] = []
    checked: list[str] = []

    # Prefer top-level keys, but fall back to nested manifest structures when present.
    open_missed = _as_float(_get(d, "OPEN_MISSED")) or _as_float(((d.get("deck_variables") or {}).get("MISSED_OPEN_HOURS")))
    weeks = _as_float(_get(d, "WEEKS_IN_RANGE")) or _as_float(((d.get("metrics") or {}).get("weeks_in_range")))
    missed_per_week = (
        _as_float(_get(d, "MISSED_CALLS_WEEK"))
        or _as_float(_get(d, "MISSED_PER_WEEK"))
        or _as_float(((d.get("deck_variables") or {}).get("MISSED_PER_WEEK")))
    )

    if open_missed is None or weeks is None or missed_per_week is None:
        return issues, checked

    checked.append("MISSED_CALLS_WEEK ~= OPEN_MISSED / WEEKS_IN_RANGE")
    expected = open_missed / weeks if weeks else math.inf
    if weeks <= 0:
        issues.append(Issue("CRITICAL", f"WEEKS_IN_RANGE must be > 0 (got {weeks})"))
        return issues, checked

    if not approx_equal(missed_per_week, expected, tol=1.0):
        issues.append(Issue("WARNING", f"Missed/week mismatch: expected ~{expected:.2f}, got {missed_per_week:.2f}"))

    return issues, checked


def verify_fte_reconciliation(d: dict[str, Any]) -> tuple[list[Issue], list[str]]:
    issues: list[Issue] = []
    checked: list[str] = []

    base = _as_float(_get(d, "BASE_FTE")) or _as_float(((d.get("fte") or {}).get("base_fte")))
    mc_fte_90 = _as_float(_get(d, "MC_FTE_90")) or _as_float(((d.get("fte") or {}).get("mc_fte_90")))
    if base is None or mc_fte_90 is None:
        return issues, checked

    diff = abs(mc_fte_90 - base)
    tol = (
        _as_float(((d.get("fte") or {}).get("fte_reconcile_tolerance")))
        or _as_float((((d.get("config") or {}).get("analysis") or {}).get("fte_reconcile_tolerance")))
        or 1.0
    )
    checked.append(f"FTE reconciliation (abs(MC_FTE_90 - BASE_FTE) <= {tol:.2f})")
    if diff > tol:
        issues.append(
            Issue(
                "WARNING",
                f"FTE reconciliation delta is large: BASE_FTE={base:.2f}, MC_FTE_90={mc_fte_90:.2f}, diff={diff:.2f} > tol={tol:.2f}",
            )
        )
    elif abs(diff - tol) < 1e-9 and mc_fte_90 > base:
        issues.append(
            Issue(
                "WARNING",
                f"FTE reconciliation is borderline (understaffing risk): BASE_FTE={base:.2f}, MC_FTE_90={mc_fte_90:.2f}, diff={diff:.2f} at tol={tol:.2f}",
            )
        )

    declared_pass = (d.get("fte") or {}).get("fte_verify_pass")
    if declared_pass is False:
        issues.append(Issue("WARNING", "Manifest flagged fte_verify_pass=false; verify timezone/business hours/AHT assumptions."))

    return issues, checked


def verify_monte_carlo(d: dict[str, Any]) -> tuple[list[Issue], list[str]]:
    issues: list[Issue] = []
    checked: list[str] = []

    mc = (d.get("fte") or {}).get("mc")
    if not isinstance(mc, dict):
        return issues, checked

    seed = mc.get("seed")
    num = _as_float(mc.get("num_simulations"))
    counts = mc.get("fte_counts")
    duration_model = mc.get("duration_model")
    pool_size = _as_float(mc.get("duration_pool_size"))

    checked.append("Monte Carlo manifest fields (seed/num_sims/counts/model)")

    if seed is None:
        issues.append(Issue("WARNING", "Monte Carlo seed missing (determinism risk)."))
    if num is None or num <= 0:
        issues.append(Issue("WARNING", f"Monte Carlo num_simulations invalid ({mc.get('num_simulations')})."))

    if not duration_model:
        issues.append(Issue("WARNING", "Monte Carlo duration_model missing (cannot audit duration assumptions)."))
    elif str(duration_model).startswith("bootstrap") and (pool_size is None or pool_size <= 0):
        issues.append(Issue("WARNING", f"Monte Carlo duration_model={duration_model} but duration_pool_size is {mc.get('duration_pool_size')}."))

    if isinstance(counts, dict) and num is not None:
        try:
            total = sum(int(v) for v in counts.values())
            if total != int(num):
                issues.append(Issue("WARNING", f"Monte Carlo fte_counts sum {total} != num_simulations {int(num)}."))
        except Exception:
            issues.append(Issue("WARNING", "Monte Carlo fte_counts is not a dict of integers."))

    return issues, checked


def verify_revenue_leak(d: dict[str, Any]) -> tuple[list[Issue], list[str]]:
    issues: list[Issue] = []
    checked: list[str] = []

    cfg = d.get("config") if isinstance(d.get("config"), dict) else {}
    assumptions = (cfg.get("assumptions") if isinstance(cfg, dict) else {}) or {}

    conversion_pct = _as_float(assumptions.get("conversion_pct"))
    appt_seeking_pct = _as_float(assumptions.get("appt_seeking_pct"))
    new_patient_pct = _as_float(assumptions.get("new_patient_pct"))
    avg_appt_value = _as_float(assumptions.get("avg_appt_value"))

    missed_per_week = _as_float(_get(d, "MISSED_CALLS_WEEK")) or _as_float(((d.get("deck_variables") or {}).get("MISSED_PER_WEEK")))
    if (
        missed_per_week is None
        or conversion_pct is None
        or appt_seeking_pct is None
        or new_patient_pct is None
        or avg_appt_value is None
    ):
        return issues, checked

    expected_weekly = (
        missed_per_week
        * (appt_seeking_pct / 100.0)
        * (new_patient_pct / 100.0)
        * (conversion_pct / 100.0)
        * avg_appt_value
    )
    expected_monthly = expected_weekly * 4.33
    expected_annual = expected_monthly * 12.0

    deck = d.get("deck_variables") if isinstance(d.get("deck_variables"), dict) else {}
    weekly = _as_float(deck.get("WEEKLY_LEAK"))
    monthly = _as_float(deck.get("MONTHLY_LEAK"))
    annual = _as_float(deck.get("ANNUAL_LEAK"))

    # Only compare if the deck variables exist.
    if weekly is None and monthly is None and annual is None:
        return issues, checked

    checked.append("Revenue leak arithmetic (weekly/monthly/annual)")

    # Deck values are commonly rounded for presentation; keep tolerances lenient.
    if weekly is not None and not approx_equal(weekly, expected_weekly, tol=50.0):
        issues.append(Issue("WARNING", f"WEEKLY_LEAK mismatch: expected ~{expected_weekly:.2f}, got {weekly:.2f}"))
    if monthly is not None and not approx_equal(monthly, expected_monthly, tol=200.0):
        issues.append(Issue("WARNING", f"MONTHLY_LEAK mismatch: expected ~{expected_monthly:.2f}, got {monthly:.2f}"))
    if annual is not None and not approx_equal(annual, expected_annual, tol=1000.0):
        issues.append(Issue("WARNING", f"ANNUAL_LEAK mismatch: expected ~{expected_annual:.2f}, got {annual:.2f}"))

    return issues, checked


def verify_pricing_breakdown(d: dict[str, Any]) -> tuple[list[Issue], list[str]]:
    issues: list[Issue] = []
    checked: list[str] = []

    pricing = d.get("pricing")
    if not isinstance(pricing, dict):
        return issues, checked

    weeks_per_month = _as_float(pricing.get("weeks_per_month")) or 4.33

    def _verify_option(name: str, key: str) -> None:
        opt = pricing.get(key)
        if not isinstance(opt, dict):
            return

        base = _as_float(opt.get("base"))
        ot = _as_float(opt.get("ot")) or 0.0
        weekend = _as_float(opt.get("weekend")) or 0.0
        growth_addon_weekly = _as_float(opt.get("growth_addon_weekly")) or 0.0
        weekly = _as_float(opt.get("weekly"))
        monthly = _as_float(opt.get("monthly"))
        annual = _as_float(opt.get("annual"))

        if base is None or weekly is None:
            return

        checked.append(f"{name} pricing breakdown sums")
        expected_weekly = base + ot + weekend + growth_addon_weekly
        if not approx_equal(weekly, expected_weekly, tol=0.05):
            issues.append(
                Issue(
                    "WARNING",
                    f"{name} weekly mismatch vs breakdown: expected ~{expected_weekly:.2f}, got {weekly:.2f}",
                )
            )

        if monthly is not None:
            checked.append(f"{name} monthly ~= weekly * {weeks_per_month:.2f}")
            if not approx_equal(monthly, weekly * weeks_per_month, tol=10.0):
                issues.append(
                    Issue(
                        "WARNING",
                        f"{name} monthly mismatch: expected ~{weekly * weeks_per_month:.2f}, got {monthly:.2f}",
                    )
                )
        if monthly is not None and annual is not None:
            checked.append(f"{name} annual ~= monthly * 12")
            if not approx_equal(annual, monthly * 12.0, tol=25.0):
                issues.append(Issue("WARNING", f"{name} annual mismatch: expected ~{monthly * 12.0:.2f}, got {annual:.2f}"))

    _verify_option("Inbound", "inbound")
    _verify_option("RHC", "rhc")
    _verify_option("RHC+ Growth", "rhc_growth")
    _verify_option("In-house", "in_house")

    return issues, checked


def main() -> None:
    parser = argparse.ArgumentParser(description="Verify FTE + pricing + missed-calls math from a JSON manifest.")
    parser.add_argument("manifest", type=Path, help="Path to JSON manifest with computed variables.")
    args = parser.parse_args()

    if not args.manifest.exists():
        raise SystemExit(f"Manifest not found: {args.manifest}")

    d = json.loads(args.manifest.read_text(encoding="utf-8"))
    if not isinstance(d, dict):
        raise SystemExit("Manifest must be a JSON object (dict).")

    all_issues: list[Issue] = []
    all_checked: list[str] = []

    for verifier in (
        verify_shrinkage,
        verify_pricing,
        verify_pricing_breakdown,
        verify_missed_calls,
        verify_fte_reconciliation,
        verify_monte_carlo,
        verify_revenue_leak,
    ):
        issues, checked = verifier(d)
        all_issues.extend(issues)
        all_checked.extend(checked)

    if all_checked:
        print("Checks performed:")
        for c in all_checked:
            print(f"- {c}")
    else:
        print("No checks performed (missing required keys in manifest).")

    if all_issues:
        print("\nIssues:")
        for issue in all_issues:
            print(f"- [{issue.level}] {issue.message}")

    has_critical = any(i.level == "CRITICAL" for i in all_issues)
    if has_critical:
        raise SystemExit(1)

    print("\n[OK] Verification completed (no CRITICAL issues).")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nInterrupted.", file=sys.stderr)
        raise SystemExit(130)
