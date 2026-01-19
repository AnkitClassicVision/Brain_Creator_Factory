#!/usr/bin/env python3
"""
Run the phone_to_present workflow end-to-end on a CSV/XLSX file and produce:
- gold table (normalized data)
- analysis manifest (inputs, mappings, metrics, FTE, pricing, assumptions)
- charts (PNG) referenced by the Marp template
- populated markdown deck (source of truth)
- rendered HTML + PPTX via Marp (verified)

This script is intentionally deterministic:
- Monte Carlo seed is derived from the input file hash + key parameters
- outputs include a manifest suitable for audit and reruns
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import subprocess
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns


ROOT = Path(__file__).resolve().parent.parent  # phone_to_present/
TEMPLATE_PATH = ROOT / "templates" / "presentation_template.md"
RENDER_VERIFY = ROOT / "scripts" / "render_verify.py"
VERIFY_FINANCIALS = ROOT / "scripts" / "verify_financials.py"

PLACEHOLDER_RE = re.compile(r"\{\{([A-Z0-9_]+)\}\}")
DAY_ORDER = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def stable_seed(*parts: Any) -> int:
    fp = "|".join(str(p) for p in parts)
    digest = hashlib.sha256(fp.encode("utf-8")).hexdigest()
    return int(digest[:8], 16)


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def normalize_col(s: str) -> str:
    return re.sub(r"\s+", " ", s.strip().lower())


def normalize_key(s: Any) -> str:
    return re.sub(r"\s+", " ", str(s).strip().lower())


def parse_iso_date(s: str) -> date:
    return date.fromisoformat(str(s).strip())


def status_is_confirmed(v: Any) -> bool:
    if isinstance(v, bool):
        return v
    s = str(v or "").strip().lower()
    return s in {"confirmed", "confirm", "true", "yes", "y", "1"}


def status_label(v: Any, *, default: str = "Unconfirmed") -> str:
    if status_is_confirmed(v):
        return "Client-confirmed"
    s = str(v or "").strip()
    if not s:
        return default
    if s.lower() in {"assumed", "assumption", "test"}:
        return "Assumed for analysis"
    return s


def slugify(s: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9]+", "-", str(s).strip().lower()).strip("-")
    return cleaned or "default"


def load_location_overrides(cfg: dict[str, Any]) -> dict[str, dict[str, Any]]:
    raw = cfg.get("location_overrides") or {}
    if raw is None:
        return {}
    if not isinstance(raw, dict):
        raise ValueError("location_overrides must be an object mapping location_name -> override settings")
    out: dict[str, dict[str, Any]] = {}
    for k, v in raw.items():
        if not isinstance(v, dict):
            raise ValueError(f"location_overrides[{k!r}] must be an object")
        out[normalize_key(k)] = v
    return out



def find_column(df: pd.DataFrame, candidates: list[str]) -> str | None:
    lookup = {normalize_col(c): c for c in df.columns}
    for cand in candidates:
        c = lookup.get(normalize_col(cand))
        if c:
            return c
    return None


def parse_hhmm(s: str) -> int:
    hh, mm = str(s).strip().split(":")
    return int(hh) * 60 + int(mm)


def fmt_int(x: float | int) -> str:
    return f"{int(round(float(x))):,}"


def fmt_money(x: float | int) -> str:
    return f"{int(round(float(x))):,}"


def fmt_pct(x: float, digits: int = 1) -> str:
    return f"{x:.{digits}f}"


def clamp_text(s: str, max_chars: int) -> str:
    compact = " ".join(str(s).split())
    if max_chars <= 1:
        return "…"
    if len(compact) <= max_chars:
        return compact
    return compact[: max_chars - 1].rstrip() + "…"


def extract_placeholders(text: str) -> list[str]:
    return sorted(set(PLACEHOLDER_RE.findall(text)))


def apply_template(template_text: str, variables: dict[str, str]) -> str:
    placeholders = extract_placeholders(template_text)
    missing = [p for p in placeholders if p not in variables]
    if missing:
        raise ValueError("Missing template variables:\n" + "\n".join(f"- {m}" for m in missing))
    out = template_text
    for k, v in variables.items():
        out = out.replace(f"{{{{{k}}}}}", v)
    leftover = extract_placeholders(out)
    if leftover:
        raise ValueError("Unreplaced template variables remain:\n" + "\n".join(f"- {m}" for m in leftover))
    return out


def run_cmd(cmd: list[str], *, cwd: Path) -> None:
    proc = subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError((proc.stderr or proc.stdout or "").strip() or f"Command failed: {cmd}")


def disposition_normalize(raw: Any) -> tuple[str, float]:
    if raw is None:
        return "unknown", 0.0
    s = str(raw).strip().lower()
    if not s:
        return "unknown", 0.0
    mapping = {
        "answered": "answered",
        "completed": "answered",
        "connected": "answered",
        "missed": "missed",
        "no answer": "missed",
        "unanswered": "missed",
        "abandoned": "abandoned",
        "hang up": "abandoned",
        "hungup": "abandoned",
        "voicemail": "voicemail",
        "vm": "voicemail",
        "left message": "voicemail",
        "forwarded": "redirected",
        "redirected": "redirected",
        "transferred": "redirected",
        "transfer": "redirected",
    }
    if s in mapping:
        return mapping[s], 1.0
    for k, v in mapping.items():
        if k in s:
            return v, 0.8
    return "unknown", 0.0


def direction_normalize(raw: Any) -> tuple[str, float]:
    if raw is None:
        return "unknown", 0.0
    s = str(raw).strip().lower()
    if not s:
        return "unknown", 0.0
    mapping = {
        "inbound": "inbound",
        "incoming": "inbound",
        "in": "inbound",
        "outbound": "outbound",
        "outgoing": "outbound",
        "out": "outbound",
        "internal": "internal",
        "transfer": "internal",
    }
    if s in mapping:
        return mapping[s], 1.0
    for k, v in mapping.items():
        if k in s:
            return v, 0.8
    return "unknown", 0.0


def grade_from_answer_rate(answer_rate: float) -> tuple[str, str, str, str]:
    if answer_rate >= 95:
        return "A", "Excellent", "#10B981", "#ffffff"
    if answer_rate >= 90:
        return "B", "Good", "#EAB308", "#27343C"
    if answer_rate >= 80:
        return "C", "Needs Improvement", "#EAB308", "#27343C"
    if answer_rate >= 70:
        return "D", "Poor", "#E63946", "#ffffff"
    return "F", "Critical", "#E63946", "#ffffff"


@dataclass(frozen=True)
class BusinessHours:
    # day -> (open_minutes, close_minutes) or None if closed
    windows: dict[str, tuple[int, int] | None]

    def describe(self) -> str:
        weekday = [self.windows.get(d) for d in DAY_ORDER[:5]]
        if all(w == weekday[0] and w is not None for w in weekday):
            o, c = weekday[0]  # type: ignore[misc]
            base = f"Mon-Fri {o//60:02d}:{o%60:02d}-{c//60:02d}:{c%60:02d}"
            weekend = []
            for d in ["Sat", "Sun"]:
                w = self.windows.get(d)
                if w:
                    o2, c2 = w
                    weekend.append(f"{d} {o2//60:02d}:{o2%60:02d}-{c2//60:02d}:{c2%60:02d}")
            return ", ".join([base, *weekend]) if weekend else base

        parts: list[str] = []
        for d in DAY_ORDER:
            w = self.windows.get(d)
            if not w:
                continue
            o, c = w
            parts.append(f"{d} {o//60:02d}:{o%60:02d}-{c//60:02d}:{c%60:02d}")
        return ", ".join(parts) if parts else "Unknown"

    def weekly_summary(self) -> dict[str, Any]:
        hours_by_day: dict[str, float] = {}
        for d in DAY_ORDER:
            w = self.windows.get(d)
            if not w:
                hours_by_day[d] = 0.0
                continue
            o, c = w
            hours_by_day[d] = max((c - o) / 60.0, 0.0)
        total = sum(hours_by_day.values())
        regular = min(total, 40.0)
        ot = max(total - 40.0, 0.0)
        return {
            "hours_by_day": hours_by_day,
            "total_weekly_hours": round(total, 2),
            "regular_hours": round(regular, 2),
            "ot_hours": round(ot, 2),
            "has_saturday": hours_by_day["Sat"] > 0,
            "has_sunday": hours_by_day["Sun"] > 0,
            "saturday_hours": round(hours_by_day["Sat"], 2),
            "sunday_hours": round(hours_by_day["Sun"], 2),
        }


def load_business_hours_dict(raw: dict[str, Any]) -> BusinessHours:
    windows: dict[str, tuple[int, int] | None] = {}
    for d in DAY_ORDER:
        v = raw.get(d)
        if v is None:
            windows[d] = None
            continue
        if not isinstance(v, list) or len(v) != 2:
            raise ValueError(f"business_hours[{d}] must be [\"HH:MM\",\"HH:MM\"] or null")
        o = parse_hhmm(v[0])
        c = parse_hhmm(v[1])
        if c <= o:
            raise ValueError(f"business_hours[{d}] close must be > open (got {v})")
        windows[d] = (o, c)
    return BusinessHours(windows=windows)


def load_business_hours(cfg: dict[str, Any]) -> BusinessHours:
    raw = cfg.get("business_hours") or {}
    if not isinstance(raw, dict):
        raise ValueError("business_hours must be an object mapping day->['HH:MM','HH:MM'] or null")
    return load_business_hours_dict(raw)


def compute_open_flag(ts_local: pd.Timestamp, bh: BusinessHours, closures: set[date] | None = None) -> tuple[bool, str, int]:
    day = ts_local.strftime("%a")[:3]
    if closures and ts_local.date() in closures:
        return False, day, ts_local.hour
    mins = ts_local.hour * 60 + ts_local.minute
    w = bh.windows.get(day)
    if not w:
        return False, day, ts_local.hour
    o, c = w
    return (o <= mins < c), day, ts_local.hour


def build_time_weighted_concurrency(start_s: np.ndarray, end_s: np.ndarray) -> dict[int, float]:
    start_s = np.sort(np.asarray(start_s, dtype=float))
    end_s = np.sort(np.asarray(end_s, dtype=float))
    n = start_s.shape[0]
    if n == 0:
        return {0: 0.0}

    i = 0
    j = 0
    level = 0
    time_at: dict[int, float] = {}
    last = min(start_s[0], end_s[0])

    while i < n or j < n:
        next_start = start_s[i] if i < n else math.inf
        next_end = end_s[j] if j < n else math.inf

        # End before start on ties
        if next_end <= next_start:
            t = next_end
            if t > last:
                time_at[level] = time_at.get(level, 0.0) + (t - last)
            level -= 1
            j += 1
            last = t
        else:
            t = next_start
            if t > last:
                time_at[level] = time_at.get(level, 0.0) + (t - last)
            level += 1
            i += 1
            last = t

    return time_at


def concurrency_at_arrival(start_s: np.ndarray, end_s: np.ndarray) -> np.ndarray:
    start_s = np.asarray(start_s, dtype=float)
    end_s = np.asarray(end_s, dtype=float)
    order = np.argsort(start_s, kind="mergesort")
    start_sorted = start_s[order]
    end_sorted = np.sort(end_s)

    conc_sorted = np.zeros_like(start_sorted, dtype=int)
    j = 0
    for i, st in enumerate(start_sorted):
        while j < len(end_sorted) and end_sorted[j] <= st:
            j += 1
        conc_sorted[i] = (i - j) + 1

    out = np.zeros_like(conc_sorted)
    out[order] = conc_sorted
    return out


def calculate_base_fte(time_weighted: dict[int, float], target_coverage: float) -> int:
    levels = sorted([k for k in time_weighted.keys() if k > 0])
    if not levels:
        return 1
    total = sum(time_weighted[k] for k in levels)
    if total <= 0:
        return 1
    cum = 0.0
    for level in levels:
        cum += time_weighted[level]
        if (cum / total) >= target_coverage:
            return int(level)
    return int(max(levels))


def build_staffing_ladder(
    conc_counts: pd.Series,
    *,
    shrink_factor: float,
    min_shrinkage_fte: float = 1.25,
) -> list[dict[str, Any]]:
    conc_counts = conc_counts.copy()
    conc_counts.index = conc_counts.index.astype(int)
    conc_counts = conc_counts.sort_index()

    if conc_counts.empty:
        return []

    total_arrivals = int(conc_counts.sum())
    max_level = int(conc_counts.index.max())

    cum = 0
    rows: list[dict[str, Any]] = []
    for level in range(1, max_level + 1):
        cnt = int(conc_counts.get(level, 0))
        cum += cnt
        answer_rate = (cum / total_arrivals * 100.0) if total_arrivals else 0.0
        shrinkage_fte = max(level / float(shrink_factor), float(min_shrinkage_fte))
        rows.append(
            {
                "base_hc": int(level),
                "shrinkage_hc": float(shrinkage_fte),
                "answer_rate": float(answer_rate),
            }
        )

    return rows


def print_staffing_ladder(rows: list[dict[str, Any]], *, highlight_levels: set[int] | None = None) -> None:
    if not rows:
        print("[INFO] Staffing ladder unavailable (no arrival data).")
        return

    highlight_levels = highlight_levels or set()

    base_w = max(len("Base HC"), max(len(str(r["base_hc"])) for r in rows))
    shrink_w = max(len("Shrinkage HC"), 10)
    ar_w = max(len("Answer Rate"), 10)

    header = f"{'Base HC':<{base_w}}  {'Shrinkage HC':<{shrink_w}}  {'Answer Rate':<{ar_w}}"
    print(header)
    print("-" * len(header))

    for r in rows:
        level = int(r["base_hc"])
        star = " *" if level in highlight_levels else ""
        shrink = f"{float(r['shrinkage_hc']):.2f}"
        ar = f"{float(r['answer_rate']):.1f}%"
        print(f"{level:<{base_w}}  {shrink:<{shrink_w}}  {ar:<{ar_w}}{star}")


def prompt_yes_no(question: str, *, default: bool | None = None) -> bool:
    if default is True:
        suffix = "[Y/n]"
    elif default is False:
        suffix = "[y/N]"
    else:
        suffix = "[y/n]"

    while True:
        try:
            ans = input(f"{question} {suffix} ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            raise SystemExit("\n[ABORTED] No interactive input available.")
        if not ans and default is not None:
            return bool(default)
        if ans in {"y", "yes"}:
            return True
        if ans in {"n", "no"}:
            return False
        print("Please answer y or n.")


def prompt_int(question: str, *, default: int | None = None, min_value: int | None = None, max_value: int | None = None) -> int:
    default_hint = f" [{default}]" if default is not None else ""
    while True:
        try:
            raw = input(f"{question}{default_hint}: ").strip()
        except (EOFError, KeyboardInterrupt):
            raise SystemExit("\n[ABORTED] No interactive input available.")
        if not raw and default is not None:
            v = int(default)
        else:
            try:
                v = int(raw)
            except Exception:
                print("Enter a whole number.")
                continue
        if min_value is not None and v < int(min_value):
            print(f"Must be >= {min_value}.")
            continue
        if max_value is not None and v > int(max_value):
            print(f"Must be <= {max_value}.")
            continue
        return v


def prompt_pilot_calc(*, default: str = "base") -> str:
    default_norm = default.strip().lower()
    default_choice = "1" if default_norm == "base" else "2" if default_norm == "shrinkage" else "1"
    while True:
        try:
            raw = input(
                "Pilot calculation: (1) Base HC (call-time)  (2) Shrinkage HC (with buffer) "
                f"[{default_choice}]: "
            ).strip()
        except (EOFError, KeyboardInterrupt):
            raise SystemExit("\n[ABORTED] No interactive input available.")
        if not raw:
            raw = default_choice
        if raw in {"1", "base"}:
            return "base"
        if raw in {"2", "shrinkage"}:
            return "shrinkage"
        print("Choose 1 (base) or 2 (shrinkage).")


def run_monte_carlo_fte(
    *,
    start_s_sorted: np.ndarray,
    num_sims: int,
    target_coverage: float,
    seed: int,
    duration_model: str,
    duration_pool_s: np.ndarray | None = None,
    aht_lambda: float | None = None,
    duration_floor_s: float = 1.0,
    duration_cap_s: float | None = None,
) -> dict[str, Any]:
    rng = np.random.default_rng(seed)
    start_s_sorted = np.asarray(start_s_sorted, dtype=float)

    model = str(duration_model or "exponential").strip().lower()
    used_model = model

    pool: np.ndarray | None = None
    if model.startswith("bootstrap"):
        if duration_pool_s is not None:
            pool = np.asarray(duration_pool_s, dtype=float)
            pool = pool[np.isfinite(pool)]
            pool = pool[pool >= float(duration_floor_s)]
            if duration_cap_s is not None:
                pool = np.minimum(pool, float(duration_cap_s))
        if pool is None or pool.size < 50:
            used_model = "exponential"

    if used_model == "exponential" and aht_lambda is None:
        raise ValueError("aht_lambda is required when duration_model is exponential (or when bootstrap falls back).")

    fte: list[int] = []
    for _ in range(int(num_sims)):
        if used_model == "exponential":
            u = rng.random(start_s_sorted.shape[0])
            u = np.clip(u, 1e-12, 1 - 1e-12)
            durations = (-np.log(u) / float(aht_lambda)).astype(float)
        else:
            assert pool is not None
            durations = rng.choice(pool, size=start_s_sorted.shape[0], replace=True).astype(float)

        if duration_cap_s is not None:
            durations = np.minimum(durations, float(duration_cap_s))
        durations = np.maximum(durations, float(duration_floor_s))

        end_s = start_s_sorted + durations
        tw = build_time_weighted_concurrency(start_s_sorted, end_s)
        fte.append(calculate_base_fte(tw, target_coverage))

    arr = np.asarray(fte, dtype=float)
    counts = {str(int(k)): int(v) for k, v in pd.Series(fte).value_counts().sort_index().items()}
    return {
        "seed": int(seed),
        "num_simulations": int(num_sims),
        "target_coverage": float(target_coverage),
        "duration_model": str(used_model),
        "duration_floor_s": float(duration_floor_s),
        "duration_cap_s": float(duration_cap_s) if duration_cap_s is not None else None,
        "duration_pool_size": int(pool.size) if pool is not None else 0,
        "fte_mean": float(np.mean(arr)),
        "fte_median": float(np.median(arr)),
        "fte_90th": float(np.percentile(arr, 90)),
        "fte_max": int(np.max(arr)),
        "fte_counts": counts,
    }


def make_answer_rate_gauge(path: Path, answer_rate: float, grade: str) -> None:
    fig, ax = plt.subplots(figsize=(6.7, 4.6), dpi=150)
    ax.axis("off")

    zones = [
        (0, 70, "#FEE2E2"),
        (70, 80, "#FED7AA"),
        (80, 90, "#FEF3C7"),
        (90, 95, "#D1FAE5"),
        (95, 100, "#10B981"),
    ]
    for a, b, color in zones:
        theta1 = 180 * (1 - b / 100)
        theta2 = 180 * (1 - a / 100)
        wedge = matplotlib.patches.Wedge((0, 0), 1.0, theta1, theta2, width=0.25, facecolor=color, edgecolor="white")
        ax.add_patch(wedge)

    angle = math.radians(180 * (1 - answer_rate / 100))
    ax.plot([0, 0.85 * math.cos(angle)], [0, 0.85 * math.sin(angle)], color="#27343C", linewidth=3)
    ax.add_patch(matplotlib.patches.Circle((0, 0), 0.05, color="#27343C"))
    ax.text(0, -0.25, f"{answer_rate:.1f}%", ha="center", va="center", fontsize=20, fontweight="bold", color="#27343C")
    ax.text(0, -0.38, f"Grade: {grade}", ha="center", va="center", fontsize=14, color="#27343C")
    ax.text(0, 0.95, "Answer Rate Performance", ha="center", va="center", fontsize=14, fontweight="bold")

    ax.set_xlim(-1.1, 1.1)
    ax.set_ylim(-0.5, 1.1)
    fig.tight_layout()
    fig.savefig(path, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def make_process_capacity_pie(path: Path, process_pct: float, capacity_pct: float) -> None:
    fig, ax = plt.subplots(figsize=(5.2, 5.2), dpi=150)
    labels = ["Process", "Capacity"]
    sizes = [max(process_pct, 0.0), max(capacity_pct, 0.0)]
    colors = ["#E63946", "#EAB308"]
    ax.pie(sizes, labels=labels, autopct="%1.1f%%", startangle=90, colors=colors, textprops={"fontsize": 11})
    ax.set_title("Why Calls Are Missed (Open Hours)", fontsize=14, fontweight="bold")
    fig.tight_layout()
    fig.savefig(path, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def make_heatmap(path: Path, miss_rate_matrix: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=(8.0, 5.0), dpi=150)
    sns.heatmap(
        miss_rate_matrix,
        ax=ax,
        cmap=sns.color_palette(["#D1FAE5", "#FEF3C7", "#FEE2E2", "#E63946"], as_cmap=True),
        annot=True,
        fmt=".0f",
        linewidths=0.3,
        linecolor="#E5E7EB",
        cbar_kws={"label": "Miss Rate %"},
    )
    ax.set_title("Pain Windows (Miss Rate % by Hour × Day)", fontsize=14, fontweight="bold")
    ax.set_xlabel("")
    ax.set_ylabel("Hour (Local)")
    fig.tight_layout()
    fig.savefig(path, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def make_hourly_volume(path: Path, hourly: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=(10.0, 4.8), dpi=150)
    ax.bar(hourly.index, hourly["answered"], label="Answered", color="#10B981")
    ax.bar(hourly.index, hourly["missed"], bottom=hourly["answered"], label="Missed", color="#E63946")
    ax.set_title("Hourly Call Distribution (Open Hours)", fontsize=14, fontweight="bold")
    ax.set_xlabel("Hour (Local)")
    ax.set_ylabel("Calls")
    ax.legend()
    fig.tight_layout()
    fig.savefig(path, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def make_daily_pattern(path: Path, daily: pd.DataFrame) -> None:
    fig, ax1 = plt.subplots(figsize=(10.0, 4.8), dpi=150)
    ax1.bar(daily.index, daily["total"], color="#006064", label="Total Calls")
    ax1.set_ylabel("Calls")
    ax1.set_title("Daily Call Pattern (Open Hours)", fontsize=14, fontweight="bold")

    ax2 = ax1.twinx()
    ax2.plot(daily.index, daily["miss_rate"], color="#E63946", marker="o", label="Miss Rate %")
    ax2.set_ylabel("Miss Rate %")

    ax1.legend(loc="upper left")
    ax2.legend(loc="upper right")
    fig.tight_layout()
    fig.savefig(path, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def make_fte_coverage(path: Path, time_weighted: dict[int, float], base_fte: int, target_coverage: float) -> None:
    levels = sorted(time_weighted.keys())
    values = np.array([time_weighted[l] for l in levels], dtype=float)
    total = values.sum()
    pct = values / total * 100 if total > 0 else values

    fig, ax1 = plt.subplots(figsize=(7.2, 4.6), dpi=150)
    ax1.bar(levels, pct, color="#6B7280")
    ax1.set_xlabel("Concurrency Level")
    ax1.set_ylabel("% of Time")
    ax1.set_title("Time-Weighted Concurrency (Open Hours)", fontsize=12, fontweight="bold")

    levels_pos = [l for l in levels if l > 0]
    values_pos = np.array([time_weighted[l] for l in levels_pos], dtype=float)
    total_pos = values_pos.sum()
    cdf = (np.cumsum(values_pos) / total_pos * 100) if total_pos > 0 else np.zeros_like(values_pos)

    ax2 = ax1.twinx()
    ax2.plot(levels_pos, cdf, color="#10B981", marker="o")
    ax2.axhline(target_coverage * 100, color="#EAB308", linestyle="--", linewidth=1)
    ax2.axvline(base_fte, color="#E63946", linestyle="--", linewidth=1)
    ax2.set_ylabel("CDF % (excluding level 0)")
    ax2.set_ylim(0, 100)

    fig.tight_layout()
    fig.savefig(path, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def count_weekdays(start: date, end: date) -> int:
    # inclusive
    n = 0
    for d in pd.date_range(start, end):
        if d.strftime("%a")[:3] in DAY_ORDER[:5]:
            n += 1
    return n


def main() -> None:
    parser = argparse.ArgumentParser(description="Run phone_to_present pipeline and render Marp outputs.")
    parser.add_argument("--input", required=True, type=Path, help="Path to input CSV/XLSX file.")
    parser.add_argument("--config", required=True, type=Path, help="Path to config JSON (timezone, hours, assumptions).")
    parser.add_argument("--out", required=True, type=Path, help="Output directory.")
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Enable interactive prompts after analysis (e.g., pilot pricing selection).",
    )
    parser.add_argument(
        "--allow-unconfirmed",
        action="store_true",
        help="Allow running with unconfirmed metadata/mapping (marks confidence low and adds caveats).",
    )
    parser.add_argument(
        "--location",
        default=None,
        help="Optional location_name filter (exact match, case-insensitive). Useful for multi-location exports.",
    )
    args = parser.parse_args()

    input_path: Path = args.input
    cfg = read_json(args.config)
    client = cfg.get("client") or {}
    assumptions = cfg.get("assumptions") or {}
    analysis_cfg = cfg.get("analysis") or {}
    confirmations = cfg.get("confirmations") or {}
    pilot_cfg = cfg.get("pilot") or {}
    if not isinstance(pilot_cfg, dict):
        raise SystemExit("`pilot` must be an object (or omitted).")

    default_tz = str(client.get("timezone") or "America/New_York")
    default_bh = load_business_hours(cfg)

    require_confirmed_metadata = bool(analysis_cfg.get("require_confirmed_metadata", True))
    if require_confirmed_metadata and not args.allow_unconfirmed:
        if not status_is_confirmed(confirmations.get("timezone")):
            raise SystemExit(
                "Timezone is not marked confirmed in config. Set `confirmations.timezone=confirmed` "
                "or rerun with `--allow-unconfirmed` for testing."
            )
        if not status_is_confirmed(confirmations.get("business_hours")):
            raise SystemExit(
                "Business hours are not marked confirmed in config. Set `confirmations.business_hours=confirmed` "
                "or rerun with `--allow-unconfirmed` for testing."
            )

    has_closure_field = "closures" in cfg
    raw_closures = cfg.get("closures") or []
    if not isinstance(raw_closures, list):
        raise SystemExit("`closures` must be a list of ISO dates like ['2025-12-25'] (or omitted).")
    global_closure_dates: list[date] = []
    for item in raw_closures:
        try:
            global_closure_dates.append(parse_iso_date(str(item)))
        except Exception as e:
            raise SystemExit(f"Invalid closure date '{item}'. Expected YYYY-MM-DD. ({e})")
    global_closure_rationale = (
        status_label(confirmations.get("closures"), default="Unconfirmed")
        if has_closure_field
        else "No closure calendar provided"
    )

    out_dir: Path = args.out
    ensure_dir(out_dir)
    charts_dir = out_dir / "charts"
    ensure_dir(charts_dir)

    # Load data
    if input_path.suffix.lower() == ".csv":
        raw = pd.read_csv(input_path, encoding="utf-8-sig")
    elif input_path.suffix.lower() in {".xlsx", ".xls"}:
        raw = pd.read_excel(input_path)
    else:
        raise SystemExit(f"Unsupported input format: {input_path.suffix}")

    # Column mapping (heuristics; this is one of the things to red-team)
    col_location = find_column(raw, ["location_name", "location", "office", "site", "branch"])
    col_start = find_column(raw, ["call_start_time (UTC)", "call_start_time", "start_time", "start", "timestamp"])
    col_end = find_column(raw, ["call_end_time (UTC)", "call_end_time", "end_time", "end"])
    col_dur = find_column(raw, ["duration_secs", "duration_seconds", "duration", "talk_time", "seconds"])
    col_dir = find_column(raw, ["call_direction", "direction", "call_type", "type"])
    col_status = find_column(raw, ["call_status", "disposition", "status", "result", "outcome"])

    required = {
        "start_time_utc": col_start,
        "end_time_utc": col_end,
        "duration_seconds": col_dur,
        "direction": col_dir,
        "status": col_status,
    }
    missing = [k for k, v in required.items() if v is None]
    if missing:
        raise SystemExit(f"Missing required columns (mapping failed): {missing}")

    df = raw.copy()
    df["start_time_utc"] = pd.to_datetime(df[col_start], utc=True, errors="raise")  # type: ignore[arg-type]
    df["end_time_utc"] = pd.to_datetime(df[col_end], utc=True, errors="raise")  # type: ignore[arg-type]
    df["duration_seconds"] = pd.to_numeric(df[col_dur], errors="raise").astype(int)  # type: ignore[arg-type]
    df["location_name"] = df[col_location].astype(str) if col_location else ""  # type: ignore[index]

    # Normalize direction + disposition
    dir_norm = df[col_dir].apply(direction_normalize)  # type: ignore[index]
    df["direction"] = dir_norm.apply(lambda x: x[0])
    df["direction_confidence"] = dir_norm.apply(lambda x: float(x[1]))

    disp_norm = df[col_status].apply(disposition_normalize)  # type: ignore[index]
    df["disposition_normalized"] = disp_norm.apply(lambda x: x[0])
    df["disposition_confidence"] = disp_norm.apply(lambda x: float(x[1]))
    df["disposition_raw"] = df[col_status].astype(str)  # type: ignore[index]

    # ------------------------------------------------------------------
    # Mapping confidence gates (deterministic checks before analysis)
    # ------------------------------------------------------------------
    mapping_report = {
        "direction_unknown_pct": float((df["direction"] == "unknown").mean() * 100.0),
        "direction_low_conf_pct": float((df["direction_confidence"] < 1.0).mean() * 100.0),
        "disposition_unknown_pct": float((df["disposition_normalized"] == "unknown").mean() * 100.0),
        "disposition_low_conf_pct": float((df["disposition_confidence"] < 1.0).mean() * 100.0),
        "redirected_pct": float((df["disposition_normalized"] == "redirected").mean() * 100.0),
        "raw_status_unique": int(df["disposition_raw"].nunique(dropna=False)),
    }

    require_disposition_mapping_confirmation = bool(analysis_cfg.get("require_disposition_mapping_confirmation", True))
    if require_disposition_mapping_confirmation and not args.allow_unconfirmed:
        if not status_is_confirmed(confirmations.get("disposition_mapping")):
            raise SystemExit(
                "Disposition mapping is not marked confirmed in config. Set `confirmations.disposition_mapping=confirmed` "
                "after reviewing raw call status values → normalized categories, or rerun with `--allow-unconfirmed` for testing."
            )

    max_unknown_disposition_pct = float(analysis_cfg.get("max_unknown_disposition_pct", 1.0))
    max_unknown_direction_pct = float(analysis_cfg.get("max_unknown_direction_pct", 1.0))
    max_low_conf_disposition_pct = float(analysis_cfg.get("max_low_conf_disposition_pct", 10.0))
    max_redirected_pct = float(analysis_cfg.get("max_redirected_pct", 20.0))
    stop_on_low_confidence = bool(analysis_cfg.get("stop_on_low_confidence", True))

    mapping_issues: list[str] = []
    if mapping_report["disposition_unknown_pct"] > max_unknown_disposition_pct:
        mapping_issues.append(
            f"Unknown disposition {mapping_report['disposition_unknown_pct']:.1f}% > {max_unknown_disposition_pct:.1f}%"
        )
    if mapping_report["direction_unknown_pct"] > max_unknown_direction_pct:
        mapping_issues.append(
            f"Unknown direction {mapping_report['direction_unknown_pct']:.1f}% > {max_unknown_direction_pct:.1f}%"
        )
    if mapping_report["disposition_low_conf_pct"] > max_low_conf_disposition_pct:
        mapping_issues.append(
            f"Low-confidence disposition mapping {mapping_report['disposition_low_conf_pct']:.1f}% > {max_low_conf_disposition_pct:.1f}%"
        )
    if mapping_report["redirected_pct"] > max_redirected_pct:
        mapping_issues.append(
            f"Redirected/forwarded dispositions {mapping_report['redirected_pct']:.1f}% > {max_redirected_pct:.1f}% (system semantics may treat these as answered)"
        )
    if mapping_issues and stop_on_low_confidence and not args.allow_unconfirmed:
        raise SystemExit("Mapping quality gate failed:\n" + "\n".join(f"- {m}" for m in mapping_issues))

    # ------------------------------------------------------------------
    # Location-aware configuration (optional)
    # ------------------------------------------------------------------
    location_overrides = load_location_overrides(cfg)
    location_mode = str(analysis_cfg.get("location_mode") or "single").strip().lower()

    location_values = sorted(
        set(str(x).strip() for x in df["location_name"].dropna().unique() if str(x).strip())
    )

    if args.location:
        wanted = normalize_key(args.location)
        mask = df["location_name"].apply(normalize_key) == wanted
        if not bool(mask.any()):
            avail = ", ".join(location_values) if location_values else "(none)"
            raise SystemExit(f"No rows matched --location={args.location!r}. Available location_name values: {avail}")
        df = df[mask].copy()
        location_values = sorted(
            set(str(x).strip() for x in df["location_name"].dropna().unique() if str(x).strip())
        )

    if location_mode == "by_location" and not args.location and len(location_values) > 1:
        locations_dir = out_dir / "locations"
        ensure_dir(locations_dir)

        rollup: dict[str, Any] = {
            "mode": "by_location",
            "input": {"path": str(input_path), "sha256": sha256_file(input_path)},
            "locations": [],
        }

        script_path = (ROOT / "scripts" / "run_pipeline.py").resolve()
        for loc in location_values:
            slug = slugify(loc)
            sub_out = (locations_dir / slug).resolve()
            ensure_dir(sub_out)

            cmd = [
                "python",
                str(script_path),
                "--input",
                str(input_path.resolve()),
                "--config",
                str(args.config.resolve()),
                "--out",
                str(sub_out),
                "--location",
                loc,
            ]
            if args.allow_unconfirmed:
                cmd.append("--allow-unconfirmed")

            run_cmd(cmd, cwd=ROOT)

            manifest_path = sub_out / "analysis_manifest.json"
            entry: dict[str, Any] = {"location_name": loc, "out_dir": str(sub_out), "manifest": str(manifest_path)}
            if manifest_path.exists():
                try:
                    m = read_json(manifest_path)
                    entry["open_answer_rate"] = (m.get("metrics") or {}).get("open_answer_rate")
                    entry["grade"] = (m.get("metrics") or {}).get("grade")
                except Exception:
                    entry["manifest_read_error"] = True
            rollup["locations"].append(entry)

        rollup_path = out_dir / "rollup_manifest.json"
        write_json(rollup_path, rollup)
        print("[OK] Multi-location run complete")
        print(f"[OK] Rollup: {rollup_path}")
        return

    location_context = location_values[0] if len(location_values) == 1 else (args.location or None)
    override = location_overrides.get(normalize_key(location_context)) if location_context else None

    confirmations_effective = dict(confirmations) if isinstance(confirmations, dict) else {}
    if override and isinstance(override.get("confirmations"), dict):
        confirmations_effective.update(override["confirmations"])
    confirmations = confirmations_effective

    tz = str((override or {}).get("timezone") or default_tz)

    bh = default_bh
    if override and "business_hours" in override and override["business_hours"] is not None:
        raw_hours = override["business_hours"]
        if not isinstance(raw_hours, dict):
            raise SystemExit("location_overrides[...].business_hours must be an object mapping day->['HH:MM','HH:MM'] or null")
        bh = load_business_hours_dict(raw_hours)

    # Merge global + per-location closures
    closure_candidates: list[date] = list(global_closure_dates)
    if override and override.get("closures"):
        raw_loc_closures = override["closures"]
        if not isinstance(raw_loc_closures, list):
            raise SystemExit("location_overrides[...].closures must be a list of ISO dates like ['2025-12-25']")
        for item in raw_loc_closures:
            try:
                closure_candidates.append(parse_iso_date(str(item)))
            except Exception as e:
                raise SystemExit(f"Invalid per-location closure date '{item}'. Expected YYYY-MM-DD. ({e})")
    closure_set = set(closure_candidates)
    closure_desc = "None" if not closure_set else ", ".join(sorted(d.isoformat() for d in closure_set))
    closure_rationale = (
        status_label(confirmations.get("closures"), default=global_closure_rationale)
        if closure_set
        else global_closure_rationale
    )

    # Re-check confirmations after applying per-location overrides
    if require_confirmed_metadata and not args.allow_unconfirmed:
        if not status_is_confirmed(confirmations.get("timezone")):
            raise SystemExit(
                "Timezone is not marked confirmed in config for this run. Set `confirmations.timezone=confirmed` "
                "(or per-location override confirmations) or rerun with `--allow-unconfirmed` for testing."
            )
        if not status_is_confirmed(confirmations.get("business_hours")):
            raise SystemExit(
                "Business hours are not marked confirmed in config for this run. Set `confirmations.business_hours=confirmed` "
                "(or per-location override confirmations) or rerun with `--allow-unconfirmed` for testing."
            )

    hours_summary = bh.weekly_summary()

    df["start_time_local"] = df["start_time_utc"].dt.tz_convert(tz)
    df["end_time_local"] = df["end_time_utc"].dt.tz_convert(tz)

    open_flags = df["start_time_local"].apply(lambda ts: compute_open_flag(ts, bh, closure_set))
    df["is_open_hours"] = open_flags.apply(lambda x: bool(x[0]))
    df["day_of_week"] = open_flags.apply(lambda x: x[1])
    df["hour_local"] = open_flags.apply(lambda x: int(x[2]))

    df["is_closure_day"] = df["start_time_local"].apply(lambda ts: ts.date() in closure_set)
    df["is_weekend"] = df["day_of_week"].isin(["Sat", "Sun"])
    df["is_after_hours"] = (~df["is_open_hours"]) & (~df["is_weekend"]) & (~df["is_closure_day"])
    df["is_lunch_window"] = False

    # Gold export
    gold_cols = [
        "location_name",
        "start_time_utc",
        "end_time_utc",
        "start_time_local",
        "end_time_local",
        "duration_seconds",
        "direction",
        "direction_confidence",
        "disposition_raw",
        "disposition_normalized",
        "disposition_confidence",
        "is_open_hours",
        "is_after_hours",
        "is_closure_day",
        "is_weekend",
        "day_of_week",
        "hour_local",
    ]
    gold_path = out_dir / "gold_calls.csv"
    df[gold_cols].to_csv(gold_path, index=False)

    # ------------------------------------------------------------------
    # Metrics (open-hours primary)
    # ------------------------------------------------------------------
    total_records = int(len(df))
    inbound_df = df[df["direction"] == "inbound"].copy()
    outbound_df = df[df["direction"] == "outbound"].copy()
    total_inbound = int(len(inbound_df))
    total_outbound = int(len(outbound_df))

    min_local = df["start_time_local"].min()
    max_local = df["start_time_local"].max()
    min_date = min_local.date()
    max_date = max_local.date()
    days_analyzed = int((max_date - min_date).days) + 1
    weeks_in_range = days_analyzed / 7.0

    open_hours_df = inbound_df[inbound_df["is_open_hours"]].copy()
    closed_hours_df = inbound_df[~inbound_df["is_open_hours"]].copy()

    open_answered = int((open_hours_df["disposition_normalized"] == "answered").sum())
    open_missed = int(open_hours_df["disposition_normalized"].isin(["missed", "abandoned"]).sum())
    open_unknown = int((open_hours_df["disposition_normalized"] == "unknown").sum())
    open_known = int(len(open_hours_df) - open_unknown)

    answer_rate = (open_answered / open_known * 100.0) if open_known > 0 else 0.0
    miss_rate = (open_missed / open_known * 100.0) if open_known > 0 else 0.0

    grade, grade_desc, grade_bg, grade_text = grade_from_answer_rate(answer_rate)
    answer_rate_color = "#10B981" if grade == "A" else "#EAB308" if grade in {"B", "C"} else "#E63946"
    miss_ratio = "N/A" if miss_rate <= 0 else str(int(round(100.0 / miss_rate)))

    missed_per_week = (open_missed / weeks_in_range) if weeks_in_range > 0 else 0.0
    weekday_count = count_weekdays(min_date, max_date)
    missed_per_day = (open_missed / weekday_count) if weekday_count > 0 else 0.0

    # Pain windows + worst hours
    min_calls_for_worst = int(analysis_cfg.get("min_calls_for_worst_window", 5))
    hour_start, hour_end = analysis_cfg.get("business_hours_range_display", [8, 18])
    hour_start = int(hour_start)
    hour_end = int(hour_end)

    open_hours_df["is_missed"] = open_hours_df["disposition_normalized"].isin(["missed", "abandoned"])
    total_matrix = open_hours_df.pivot_table(index="hour_local", columns="day_of_week", values="is_missed", aggfunc="size", fill_value=0)
    missed_matrix = open_hours_df[open_hours_df["is_missed"]].pivot_table(index="hour_local", columns="day_of_week", values="is_missed", aggfunc="size", fill_value=0)
    miss_rate_matrix = (missed_matrix / total_matrix * 100.0).fillna(0.0)

    existing_days = [d for d in DAY_ORDER if d in miss_rate_matrix.columns]
    miss_rate_matrix = miss_rate_matrix[existing_days]
    miss_rate_matrix = miss_rate_matrix.loc[miss_rate_matrix.index.isin(range(hour_start, hour_end))]

    worst: list[dict[str, Any]] = []
    for hour in miss_rate_matrix.index:
        for day in miss_rate_matrix.columns:
            total = int(total_matrix.loc[hour, day]) if (hour in total_matrix.index and day in total_matrix.columns) else 0
            missed = int(missed_matrix.loc[hour, day]) if (hour in missed_matrix.index and day in missed_matrix.columns) else 0
            rate = float(miss_rate_matrix.loc[hour, day])
            if total >= min_calls_for_worst and missed > 0:
                worst.append({"day": day, "hour": int(hour), "rate": rate, "missed": missed, "total": total})
    worst.sort(key=lambda x: (x["rate"], x["missed"], x["total"]), reverse=True)

    def worst_label(item: dict[str, Any]) -> str:
        h = int(item["hour"])
        return f"{item['day']} {h}:00-{h+1}:00"

    worst_1 = worst[0] if len(worst) > 0 else None
    worst_2 = worst[1] if len(worst) > 1 else None
    worst_3 = worst[2] if len(worst) > 2 else None

    # Daily pattern (open hours)
    daily = open_hours_df.groupby("day_of_week").agg(
        total=("disposition_normalized", "size"),
        answered=("disposition_normalized", lambda s: int((s == "answered").sum())),
        missed=("disposition_normalized", lambda s: int(s.isin(["missed", "abandoned"]).sum())),
    )
    daily["miss_rate"] = (daily["missed"] / daily["total"] * 100.0).fillna(0.0)
    daily = daily.reindex([d for d in DAY_ORDER if d in daily.index])
    peak_day = str(daily["total"].idxmax()) if len(daily) else "N/A"

    # Hourly distribution (open hours)
    hourly = open_hours_df.groupby("hour_local").agg(
        answered=("disposition_normalized", lambda s: int((s == "answered").sum())),
        missed=("disposition_normalized", lambda s: int(s.isin(["missed", "abandoned"]).sum())),
    )
    hourly["total"] = hourly["answered"] + hourly["missed"]
    hourly = hourly.sort_index()

    # ------------------------------------------------------------------
    # Concurrency + FTE (open-hours inbound only)
    # ------------------------------------------------------------------
    start_epoch = (open_hours_df["start_time_local"].astype("int64") / 1e9).to_numpy(dtype=float)
    end_epoch = (open_hours_df["end_time_local"].astype("int64") / 1e9).to_numpy(dtype=float)
    start_sorted = np.sort(start_epoch)

    time_weighted = build_time_weighted_concurrency(start_epoch, end_epoch)
    target_coverage = float(analysis_cfg.get("target_coverage", 0.90))
    base_fte = max(calculate_base_fte(time_weighted, target_coverage), 1)

    shrinkage_pct = float(assumptions.get("shrinkage_pct", 20))
    shrink_factor = 1.0 - (shrinkage_pct / 100.0)
    shrinkage_fte = max(base_fte / shrink_factor, 1.25)

    # Triggered concurrency (arrivals)
    # NOTE: Some exports contain 0-second calls (end == start). For "arrivals" analysis,
    # treat every arrival as at least 1 line ringing to avoid confusing 0-concurrency rows.
    conc_arr = concurrency_at_arrival(start_epoch, end_epoch)
    conc_arr = np.maximum(conc_arr, 1)
    open_hours_df["concurrency_at_arrival"] = conc_arr
    conc_counts = pd.Series(conc_arr).value_counts().sort_index()
    total_arrivals = int(conc_counts.sum())

    staffing_ladder = build_staffing_ladder(conc_counts, shrink_factor=shrink_factor)
    answer_rate_by_level = {int(r["base_hc"]): float(r["answer_rate"]) for r in staffing_ladder}
    max_staff_level = int(staffing_ladder[-1]["base_hc"]) if staffing_ladder else int(base_fte)

    pilot_enabled_default = bool(pilot_cfg.get("enabled", False))
    pilot_level_default_raw = pilot_cfg.get("level", None)
    pilot_level_default = int(pilot_level_default_raw) if pilot_level_default_raw is not None else int(base_fte)
    pilot_calc_default = str(pilot_cfg.get("calculation", "base")).strip().lower()
    if pilot_calc_default not in {"base", "shrinkage"}:
        pilot_calc_default = "base"

    pilot_enabled = pilot_enabled_default
    pilot_level = pilot_level_default
    pilot_calc = pilot_calc_default

    if args.interactive:
        print("\n[STAFFING LADDER] Base HC vs Shrinkage HC vs Answer Rate (Open Hours, Arrival Coverage)")
        print_staffing_ladder(
            staffing_ladder,
            highlight_levels={int(base_fte)},
        )
        print("  * marks current BASE_FTE (deck target coverage)")
        print("")

        if staffing_ladder:
            pilot_enabled = prompt_yes_no("Include pilot program pricing in the presentation?", default=pilot_enabled_default)
            if pilot_enabled:
                pilot_level = prompt_int(
                    "Pilot staffing level (Base HC)",
                    default=pilot_level_default,
                    min_value=1,
                    max_value=max_staff_level,
                )
                pilot_calc = prompt_pilot_calc(default=pilot_calc_default)
        else:
            print("[INFO] Pilot selection skipped (no staffing ladder available).")
            pilot_enabled = False

    if pilot_enabled:
        if pilot_level < 1 or pilot_level > max_staff_level:
            raise SystemExit(f"pilot.level must be between 1 and {max_staff_level} (got {pilot_level}).")
        if pilot_calc not in {"base", "shrinkage"}:
            raise SystemExit("pilot.calculation must be 'base' or 'shrinkage'.")

    pilot_answer_rate = float(answer_rate_by_level.get(int(pilot_level), 0.0)) if staffing_ladder else 0.0

    conc_0 = int(conc_counts.get(0, 0))
    conc_1 = int(conc_counts.get(1, 0))
    conc_2 = int(conc_counts.get(2, 0))
    conc_3 = int(conc_counts.get(3, 0))
    conc_4plus = int(conc_counts[conc_counts.index >= 4].sum())

    def pct(x: int) -> float:
        return (x / total_arrivals * 100.0) if total_arrivals else 0.0

    # Process vs capacity misses (open hours)
    missed_open = open_hours_df[open_hours_df["disposition_normalized"].isin(["missed", "abandoned"])].copy()
    process_misses = int((missed_open["concurrency_at_arrival"] <= 1).sum())
    capacity_misses = int((missed_open["concurrency_at_arrival"] > 1).sum())
    total_misses = process_misses + capacity_misses
    process_pct = (process_misses / total_misses * 100.0) if total_misses else 0.0
    capacity_pct = (capacity_misses / total_misses * 100.0) if total_misses else 0.0

    # AHT used (answered open-hours calls) + Monte Carlo
    aht_min = float(analysis_cfg.get("aht_min_minutes", 3.5))
    answered_open = open_hours_df[open_hours_df["disposition_normalized"] == "answered"]
    avg_duration_minutes = float(answered_open["duration_seconds"].mean() / 60.0) if len(answered_open) else aht_min
    aht_used = max(avg_duration_minutes, aht_min)
    aht_lambda = 1.0 / (aht_used * 60.0)

    file_hash = sha256_file(input_path)
    num_sims = int(analysis_cfg.get("num_simulations", 300))

    mc_model = str(analysis_cfg.get("mc_duration_model") or "bootstrap_answered").strip().lower()
    mc_floor_s = float(analysis_cfg.get("mc_duration_floor_seconds", 1.0))
    mc_cap_raw = analysis_cfg.get("mc_duration_cap_seconds", None)
    mc_cap_s = float(mc_cap_raw) if mc_cap_raw is not None else None

    if mc_model not in {"bootstrap_answered", "bootstrap_all_open", "exponential"}:
        raise SystemExit(
            f"Unsupported mc_duration_model: {mc_model!r}. Use one of: bootstrap_answered, bootstrap_all_open, exponential."
        )

    duration_pool_s: np.ndarray | None = None
    if mc_model == "bootstrap_answered":
        duration_pool_s = answered_open["duration_seconds"].to_numpy(dtype=float)
    elif mc_model == "bootstrap_all_open":
        duration_pool_s = open_hours_df["duration_seconds"].to_numpy(dtype=float)

    mc_seed = stable_seed(
        file_hash,
        total_records,
        str(min_local),
        str(max_local),
        tz,
        aht_used,
        target_coverage,
        mc_model,
        mc_floor_s,
        mc_cap_s,
        num_sims,
    )
    mc = run_monte_carlo_fte(
        start_s_sorted=start_sorted,
        num_sims=num_sims,
        target_coverage=target_coverage,
        seed=mc_seed,
        duration_model=mc_model,
        duration_pool_s=duration_pool_s,
        aht_lambda=aht_lambda,
        duration_floor_s=mc_floor_s,
        duration_cap_s=mc_cap_s,
    )
    mc_fte_90 = float(mc["fte_90th"])
    fte_diff = float(abs(mc_fte_90 - float(base_fte)))
    fte_reconcile_tolerance = float(analysis_cfg.get("fte_reconcile_tolerance", 1.0))
    fte_verify_pass = fte_diff <= fte_reconcile_tolerance
    fte_verify_borderline = fte_verify_pass and (abs(fte_diff - fte_reconcile_tolerance) < 1e-9) and (fte_diff > 0)

    # ------------------------------------------------------------------
    # Pricing (internal model; deck shows totals only)
    # ------------------------------------------------------------------
    mybcat_weekly_rate = 480.0
    mybcat_ot_hourly = 18.0
    inhouse_weekly_rate = 960.0
    inhouse_ot_hourly = 36.0
    weekend_premium = 25.0

    ot_hours = float(hours_summary["ot_hours"])
    weekend_days = int(hours_summary["has_saturday"]) + int(hours_summary["has_sunday"])

    # v2 headcount basis:
    # - Phones-only (Inbound) uses BASE_FTE (call-time coverage).
    # - RHC + In-house use SHRINKAGE_FTE (accounts for shrinkage).
    inbound_base = mybcat_weekly_rate * base_fte
    inbound_ot = mybcat_ot_hourly * base_fte * ot_hours
    inbound_weekend = weekend_premium * base_fte * weekend_days
    inbound_weekly = inbound_base + inbound_ot + inbound_weekend

    rhc_fte_total = shrinkage_fte
    rhc_base = mybcat_weekly_rate * rhc_fte_total
    rhc_ot = mybcat_ot_hourly * base_fte * ot_hours
    rhc_weekend = weekend_premium * base_fte * weekend_days
    rhc_weekly = rhc_base + rhc_ot + rhc_weekend

    rhc_growth_addon_weekly = float(assumptions.get("rhc_growth_addon_weekly", 500))
    rhc_growth_weekly = rhc_weekly + rhc_growth_addon_weekly

    hire_base = inhouse_weekly_rate * shrinkage_fte
    hire_ot = inhouse_ot_hourly * base_fte * ot_hours
    hire_weekend = weekend_premium * base_fte * weekend_days
    hire_weekly = hire_base + hire_ot + hire_weekend

    pilot_fte_total: float | None = None
    pilot_base: float | None = None
    pilot_ot: float | None = None
    pilot_weekend: float | None = None
    pilot_weekly: float | None = None
    pilot_monthly: float | None = None
    pilot_annual: float | None = None
    if pilot_enabled:
        pilot_fte_total = float(pilot_level) if pilot_calc == "base" else float(max(pilot_level / shrink_factor, 1.25))
        pilot_base = mybcat_weekly_rate * pilot_fte_total
        pilot_ot = mybcat_ot_hourly * float(pilot_level) * ot_hours
        pilot_weekend = weekend_premium * float(pilot_level) * weekend_days
        pilot_weekly = pilot_base + pilot_ot + pilot_weekend
        pilot_monthly = pilot_weekly * 4.33
        pilot_annual = pilot_monthly * 12

    inbound_monthly = inbound_weekly * 4.33
    rhc_monthly = rhc_weekly * 4.33
    rhc_growth_monthly = rhc_growth_weekly * 4.33
    hire_monthly = hire_weekly * 4.33

    inbound_annual = inbound_monthly * 12
    rhc_annual = rhc_monthly * 12
    rhc_growth_annual = rhc_growth_monthly * 12
    hire_annual = hire_monthly * 12

    conversion_pct = float(assumptions.get("conversion_pct", 15))
    appt_seeking_pct = float(assumptions.get("appt_seeking_pct", 60))
    new_patient_pct = float(assumptions.get("new_patient_pct", 35))
    avg_appt_value = float(assumptions.get("avg_appt_value", 500))
    weekly_leak = (
        missed_per_week
        * (appt_seeking_pct / 100.0)
        * (new_patient_pct / 100.0)
        * (conversion_pct / 100.0)
        * avg_appt_value
    )
    monthly_leak = weekly_leak * 4.33
    annual_leak = monthly_leak * 12

    raw_status_counts = df["disposition_raw"].value_counts(dropna=False).head(6)
    raw_status_bits = ", ".join(f"{k} ({int(v):,})" for k, v in raw_status_counts.items())
    more_raw = int(df["disposition_raw"].nunique(dropna=False) - len(raw_status_counts))
    if more_raw > 0:
        raw_status_bits = f"{raw_status_bits} (+{more_raw} more)"
    metadata_confirmed = status_is_confirmed(confirmations.get("timezone")) and status_is_confirmed(confirmations.get("business_hours"))
    disposition_confirmed = status_is_confirmed(confirmations.get("disposition_mapping"))

    disposition_method_full = (
        f"Disposition from `{col_status}` mapped deterministically to answered/missed/abandoned/redirected. "
        f"Top raw values: {raw_status_bits}."
    )
    disposition_method_deck = f"Disposition from `{col_status}` mapped deterministically to answered/missed/abandoned/redirected."
    if not disposition_confirmed:
        disposition_method_deck += " (Not client-confirmed.)"

    caveat_bits: list[str] = []
    if str(assumptions.get("notes") or "").strip():
        caveat_bits.append(str(assumptions["notes"]))
    caveat_bits.append("Primary KPIs (answer rate, missed/week/day, FTE) use inbound calls during business hours only.")
    if not args.location and len(location_values) > 1 and location_mode != "by_location":
        caveat_bits.append(
            f"Multiple locations detected ({len(location_values)}). This run analyzed them together under a single schedule/timezone; "
            "use `analysis.location_mode=by_location` (or rerun with `--location`) for per-location hours/timezone accuracy."
        )
    if not status_is_confirmed(confirmations.get("timezone")) or not status_is_confirmed(confirmations.get("business_hours")):
        caveat_bits.append("Timezone/business hours are not client-confirmed; treat results as directional until confirmed.")
    if not status_is_confirmed(confirmations.get("disposition_mapping")):
        caveat_bits.append("Disposition mapping was not explicitly confirmed; review raw status values for this phone system.")
    if mapping_issues:
        caveat_bits.append("Mapping quality flags: " + "; ".join(mapping_issues) + ".")
    if not fte_verify_pass:
        caveat_bits.append(
            "FTE reconciliation failed: "
            f"MC_FTE_90 ({mc_fte_90:.2f}) vs BASE_FTE ({base_fte}) diff={fte_diff:.2f} > tol={fte_reconcile_tolerance:.2f}. "
            "Verify timezone/business hours and duration model assumptions."
        )
    elif fte_verify_borderline and mc_fte_90 > float(base_fte):
        caveat_bits.append(
            "FTE reconciliation is borderline (understaffing risk): "
            f"MC_FTE_90 ({mc_fte_90:.2f}) vs BASE_FTE ({base_fte}) diff={fte_diff:.2f} at tol={fte_reconcile_tolerance:.2f}. "
            "Recommend reviewing hours/timezone and considering the higher FTE for planning."
        )
    methodology_caveat_full = " ".join(caveat_bits)

    deck_caveats: list[str] = []
    if str(assumptions.get("notes") or "").strip():
        deck_caveats.append("Some inputs were assumed for analysis.")
    deck_caveats.append("Primary KPIs use inbound calls during business hours only.")
    if not metadata_confirmed:
        deck_caveats.append("Timezone/business hours not client-confirmed.")
    if not disposition_confirmed:
        deck_caveats.append("Disposition mapping not client-confirmed.")
    if mapping_issues:
        deck_caveats.append("Data mapping has quality flags.")
    if not fte_verify_pass:
        deck_caveats.append("FTE reconciliation failed; verify hours/timezone and duration assumptions.")
    elif fte_verify_borderline and mc_fte_90 > float(base_fte):
        deck_caveats.append("FTE reconciliation borderline; consider higher coverage for planning.")
    if not args.location and len(location_values) > 1 and location_mode != "by_location":
        deck_caveats.append("Multiple locations analyzed together; per-location rerun recommended.")

    methodology_caveat_deck = clamp_text(" ".join(deck_caveats), 220)

    if not metadata_confirmed:
        confidence = "Low"
    elif not disposition_confirmed:
        confidence = "Medium"
    elif mapping_issues:
        confidence = "Low"
    elif str(assumptions.get("notes") or "").strip():
        confidence = "Medium"
    else:
        confidence = "High"

    if confidence == "High" and not args.location and len(location_values) > 1 and location_mode != "by_location":
        confidence = "Medium"

    # ------------------------------------------------------------------
    # Charts (these filenames are referenced in the Marp template)
    # ------------------------------------------------------------------
    make_answer_rate_gauge(charts_dir / "answer_rate_gauge.png", answer_rate, grade)
    make_process_capacity_pie(charts_dir / "miss_distribution.png", process_pct, capacity_pct)
    make_heatmap(charts_dir / "pain_windows_heatmap.png", miss_rate_matrix)
    make_hourly_volume(charts_dir / "hourly_volume.png", hourly)
    make_daily_pattern(charts_dir / "daily_pattern.png", daily)
    make_fte_coverage(charts_dir / "fte_coverage.png", time_weighted, base_fte, target_coverage)

    # ------------------------------------------------------------------
    # Deck variables (strings; template already includes $/% around placeholders)
    # ------------------------------------------------------------------
    location_values = sorted(set(str(x) for x in df["location_name"].dropna().unique() if str(x).strip()))
    location_count = len(location_values) if location_values else 1
    location_list = ", ".join(location_values) if location_values else ""

    date_range = f"{min_date.strftime('%b %d, %Y')} - {max_date.strftime('%b %d, %Y')}"

    pilot_investment_row = ""
    world_class_answer_rate_line = ""
    if pilot_enabled:
        if pilot_weekly is None or pilot_monthly is None:
            raise RuntimeError("pilot_weekly/pilot_monthly were not computed despite pilot_enabled=True")
        pilot_investment_row = (
            "\n"
            f"| **Pilot Program (Inbound Answering)** | **${fmt_money(pilot_weekly)}** | **${fmt_money(pilot_monthly)}** | "
            f"**{fmt_pct(pilot_answer_rate, 1)}%** | Pilot: validate capturing ${fmt_money(monthly_leak)}/mo |"
        )
        world_class_answer_rate_line = '<br><span style="color:#666; font-size:0.8em;">World Class Answer Rate</span>'

    vars_for_deck: dict[str, str] = {
        "CLIENT_NAME": str(client.get("client_name") or "Client"),
        "CLIENT_TAGLINE": str(client.get("client_tagline") or ""),
        "SPECIALTY": str(client.get("specialty") or ""),
        "DATE_RANGE": date_range,
        "DAYS_ANALYZED": str(days_analyzed),
        "TOTAL_RECORDS": fmt_int(total_records),
        "LOCATION_COUNT": str(location_count),
        "LOCATION_LIST": location_list,
        "DATA_SOURCE": input_path.name,
        "BUSINESS_HOURS_DESC": bh.describe(),
        "TIMEZONE_DESC": tz,
        "TIMEZONE_RATIONALE": status_label(confirmations.get("timezone"), default="Assumed for analysis"),
        "BUSINESS_HOURS_RATIONALE": status_label(confirmations.get("business_hours"), default="Assumed for analysis"),
        "CLOSURES_DESC": closure_desc,
        "CLOSURES_RATIONALE": closure_rationale,
        "CONFIDENCE_LEVEL": confidence,
        "DISPOSITION_METHOD": disposition_method_deck,
        "METHODOLOGY_CAVEAT": methodology_caveat_deck,

        "TOTAL_INBOUND": fmt_int(total_inbound),
        "TOTAL_OUTBOUND": fmt_int(total_outbound),
        "INBOUND_PCT": fmt_pct((total_inbound / total_records * 100.0) if total_records else 0.0, 1),
        "OUTBOUND_PCT": fmt_pct((total_outbound / total_records * 100.0) if total_records else 0.0, 1),

        "ANSWER_RATE": fmt_pct(answer_rate, 1),
        "ANSWER_RATE_COLOR": answer_rate_color,
        "MISS_RATE": fmt_pct(miss_rate, 1),
        "MISS_RATIO": miss_ratio,
        "MISSED_OPEN_HOURS": fmt_int(open_missed),
        "MISSED_PER_WEEK": fmt_int(missed_per_week),
        "MISSED_PER_DAY": fmt_int(missed_per_day),

        "GRADE": grade,
        "GRADE_BG_COLOR": grade_bg,
        "GRADE_TEXT_COLOR": grade_text,

        "PROCESS_MISS_PCT": fmt_pct(process_pct, 1),
        "CAPACITY_MISS_PCT": fmt_pct(capacity_pct, 1),

        "WORST_HOUR_1": worst_label(worst_1) if worst_1 else "N/A",
        "WORST_HOUR_1_RATE": fmt_pct(float(worst_1["rate"]), 0) if worst_1 else "0",
        "WORST_HOUR_1_COUNT": fmt_int(int(worst_1["missed"])) if worst_1 else "0",
        "WORST_HOUR_2": worst_label(worst_2) if worst_2 else "N/A",
        "WORST_HOUR_2_RATE": fmt_pct(float(worst_2["rate"]), 0) if worst_2 else "0",
        "WORST_HOUR_2_COUNT": fmt_int(int(worst_2["missed"])) if worst_2 else "0",
        "WORST_HOUR_3": worst_label(worst_3) if worst_3 else "N/A",
        "WORST_HOUR_3_RATE": fmt_pct(float(worst_3["rate"]), 0) if worst_3 else "0",
        "WORST_HOUR_3_COUNT": fmt_int(int(worst_3["missed"])) if worst_3 else "0",

        "WEEKLY_LEAK": fmt_money(weekly_leak),
        "MONTHLY_LEAK": fmt_money(monthly_leak),
        "ANNUAL_LEAK": fmt_money(annual_leak),
        "APPT_SEEKING_PCT": str(int(appt_seeking_pct)),
        "NEW_PATIENT_PCT": str(int(new_patient_pct)),
        "CONVERSION_PCT": str(int(conversion_pct)),
        "AVG_APPT_VALUE": fmt_money(avg_appt_value),

        "INBOUND_WEEKLY": fmt_money(inbound_weekly),
        "INBOUND_MONTHLY": fmt_money(inbound_monthly),
        "RHC_WEEKLY": fmt_money(rhc_weekly),
        "RHC_MONTHLY": fmt_money(rhc_monthly),
        "RHC_GROWTH_WEEKLY": fmt_money(rhc_growth_weekly),
        "RHC_GROWTH_MONTHLY": fmt_money(rhc_growth_monthly),
        "RHC_GROWTH_ADDON_WEEKLY": fmt_money(rhc_growth_addon_weekly),
        "HIRE_WEEKLY": fmt_money(hire_weekly),
        "HIRE_MONTHLY": fmt_money(hire_monthly),
        "HIRE_COST_ANNUAL": fmt_money(hire_annual),

        "PILOT_INVESTMENT_ROW": pilot_investment_row,
        "WORLD_CLASS_ANSWER_RATE_LINE": world_class_answer_rate_line,

        "ANSWERED_COUNT": fmt_int(int((inbound_df["disposition_normalized"] == "answered").sum())),
        "MISSED_COUNT": fmt_int(int(inbound_df["disposition_normalized"].isin(["missed", "abandoned"]).sum())),
        "ANSWERED_PCT": fmt_pct(((inbound_df["disposition_normalized"] == "answered").sum() / total_records * 100.0) if total_records else 0.0, 1),
        "MISSED_PCT": fmt_pct((inbound_df["disposition_normalized"].isin(["missed", "abandoned"]).sum() / total_records * 100.0) if total_records else 0.0, 1),

        "AVG_CALLS_DAY": fmt_pct((total_records / days_analyzed) if days_analyzed else 0.0, 1),
        "AVG_INBOUND_DAY": fmt_pct((total_inbound / days_analyzed) if days_analyzed else 0.0, 1),
        "AVG_ANSWERED_DAY": fmt_pct((open_answered / days_analyzed) if days_analyzed else 0.0, 1),
        "PEAK_DAY": peak_day,

        "BASE_FTE": fmt_pct(float(base_fte), 2),
        "SHRINKAGE_FTE": fmt_pct(float(shrinkage_fte), 2),
        "SHRINKAGE_PCT": str(int(shrinkage_pct)),

        "CONC_0_COUNT": str(conc_0),
        "CONC_0_PCT": fmt_pct(pct(conc_0), 1),
        "CONC_1_COUNT": fmt_int(conc_1),
        "CONC_1_PCT": fmt_pct(pct(conc_1), 1),
        "CONC_2_COUNT": fmt_int(conc_2),
        "CONC_2_PCT": fmt_pct(pct(conc_2), 1),
        "CONC_3_COUNT": fmt_int(conc_3),
        "CONC_3_PCT": fmt_pct(pct(conc_3), 1),
        "CONC_4PLUS_COUNT": fmt_int(conc_4plus),
        "CONC_4PLUS_PCT": fmt_pct(pct(conc_4plus), 1),
    }

    # Populate deck
    template_text = TEMPLATE_PATH.read_text(encoding="utf-8")
    populated = apply_template(template_text, vars_for_deck)
    md_out = out_dir / "presentation.md"
    md_out.write_text(populated, encoding="utf-8")

    # ------------------------------------------------------------------
    # Manifest for auditing + deterministic verification
    # ------------------------------------------------------------------
    analysis_manifest = {
        # top-level keys for verify_financials.py
        "BASE_FTE": float(base_fte),
        "SHRINKAGE_FTE": float(shrinkage_fte),
        "PILOT_ENABLED": bool(pilot_enabled),
        "PILOT_LEVEL": int(pilot_level) if pilot_enabled else None,
        "PILOT_CALCULATION": str(pilot_calc) if pilot_enabled else None,
        "PILOT_ANSWER_RATE": float(pilot_answer_rate) if pilot_enabled else None,
        "OT_HOURS": float(ot_hours),
        "HAS_SATURDAY": bool(hours_summary["has_saturday"]),
        "HAS_SUNDAY": bool(hours_summary["has_sunday"]),
        "MYBCAT_WEEKLY_RATE": float(mybcat_weekly_rate),
        "MYBCAT_OT_HOURLY": float(mybcat_ot_hourly),
        "INHOUSE_WEEKLY_RATE": float(inhouse_weekly_rate),
        "INHOUSE_OT_HOURLY": float(inhouse_ot_hourly),
        "WEEKEND_PREMIUM_PER_DAY": float(weekend_premium),
        "OPEN_MISSED": float(open_missed),
        "WEEKS_IN_RANGE": float(weeks_in_range),
        "MISSED_CALLS_WEEK": float(missed_per_week),
        "INBOUND_WEEKLY": float(inbound_weekly),
        "RHC_WEEKLY": float(rhc_weekly),
        "RHC_GROWTH_ADDON_WEEKLY": float(rhc_growth_addon_weekly),
        "RHC_GROWTH_WEEKLY": float(rhc_growth_weekly),
        "HIRE_WEEKLY": float(hire_weekly),
        "INBOUND_MONTHLY": float(inbound_monthly),
        "INBOUND_ANNUAL": float(inbound_annual),
        "RHC_MONTHLY": float(rhc_monthly),
        "RHC_ANNUAL": float(rhc_annual),
        "RHC_GROWTH_MONTHLY": float(rhc_growth_monthly),
        "RHC_GROWTH_ANNUAL": float(rhc_growth_annual),
        "HIRE_MONTHLY": float(hire_monthly),
        "HIRE_ANNUAL": float(hire_annual),
        "PILOT_WEEKLY": float(pilot_weekly) if pilot_weekly is not None else None,
        "PILOT_MONTHLY": float(pilot_monthly) if pilot_monthly is not None else None,
        "PILOT_ANNUAL": float(pilot_annual) if pilot_annual is not None else None,
        "pricing": {
            "weeks_per_month": 4.33,
            "weekend_days": int(weekend_days),
            "inbound": {
                "base": float(inbound_base),
                "ot": float(inbound_ot),
                "weekend": float(inbound_weekend),
                "weekly": float(inbound_weekly),
                "monthly": float(inbound_monthly),
                "annual": float(inbound_annual),
            },
            "rhc": {
                "fte_total": float(rhc_fte_total),
                "base": float(rhc_base),
                "ot": float(rhc_ot),
                "weekend": float(rhc_weekend),
                "weekly": float(rhc_weekly),
                "monthly": float(rhc_monthly),
                "annual": float(rhc_annual),
            },
            "rhc_growth": {
                "fte_total": float(rhc_fte_total),
                "base": float(rhc_base),
                "ot": float(rhc_ot),
                "weekend": float(rhc_weekend),
                "growth_addon_weekly": float(rhc_growth_addon_weekly),
                "weekly": float(rhc_growth_weekly),
                "monthly": float(rhc_growth_monthly),
                "annual": float(rhc_growth_annual),
            },
            "in_house": {
                "base": float(hire_base),
                "ot": float(hire_ot),
                "weekend": float(hire_weekend),
                "weekly": float(hire_weekly),
                "monthly": float(hire_monthly),
                "annual": float(hire_annual),
            },
            "pilot": (
                {
                    "base_hc": int(pilot_level),
                    "calculation": str(pilot_calc),
                    "answer_rate": float(pilot_answer_rate),
                    "fte_total": float(pilot_fte_total) if pilot_fte_total is not None else None,
                    "base": float(pilot_base) if pilot_base is not None else None,
                    "ot": float(pilot_ot) if pilot_ot is not None else None,
                    "weekend": float(pilot_weekend) if pilot_weekend is not None else None,
                    "weekly": float(pilot_weekly) if pilot_weekly is not None else None,
                    "monthly": float(pilot_monthly) if pilot_monthly is not None else None,
                    "annual": float(pilot_annual) if pilot_annual is not None else None,
                }
                if pilot_enabled
                else None
            ),
        },
        "input": {"path": str(input_path), "sha256": file_hash, "rows": total_records},
        "config": cfg,
        "quality": {
            "allow_unconfirmed": bool(args.allow_unconfirmed),
            "confirmations": confirmations,
            "location": {
                "mode": location_mode,
                "filter": args.location,
                "detected": location_values,
                "context": location_context,
                "timezone": tz,
                "business_hours_desc": bh.describe(),
            },
            "require_confirmed_metadata": require_confirmed_metadata,
            "require_disposition_mapping_confirmation": require_disposition_mapping_confirmation,
            "thresholds": {
                "max_unknown_disposition_pct": max_unknown_disposition_pct,
                "max_unknown_direction_pct": max_unknown_direction_pct,
                "max_low_conf_disposition_pct": max_low_conf_disposition_pct,
                "max_redirected_pct": max_redirected_pct,
                "stop_on_low_confidence": stop_on_low_confidence,
            },
            "closures": sorted(d.isoformat() for d in closure_set),
            "deck_text": {
                "disposition_method_full": disposition_method_full,
                "methodology_caveat_full": methodology_caveat_full,
            },
            "mapping_report": mapping_report,
            "mapping_issues": mapping_issues,
        },
        "mapping": {
            "location": col_location,
            "start_time": col_start,
            "end_time": col_end,
            "duration": col_dur,
            "direction": col_dir,
            "status": col_status,
        },
        "metrics": {
            "days_analyzed": days_analyzed,
            "weeks_in_range": weeks_in_range,
            "total_inbound": total_inbound,
            "total_outbound": total_outbound,
            "open_inbound": int(len(open_hours_df)),
            "closed_inbound": int(len(closed_hours_df)),
            "open_answer_rate": answer_rate,
            "open_miss_rate": miss_rate,
            "grade": grade,
        },
        "fte": {
            "time_weighted": {str(k): float(v) for k, v in sorted(time_weighted.items())},
            "base_fte": base_fte,
            "shrinkage_fte": shrinkage_fte,
            "staffing_ladder": staffing_ladder,
            "aht_used_minutes": aht_used,
            "mc": mc,
            "mc_fte_90": mc_fte_90,
            "fte_diff": fte_diff,
            "fte_verify_pass": fte_verify_pass,
            "fte_reconcile_tolerance": fte_reconcile_tolerance,
            "fte_verify_borderline": fte_verify_borderline,
        },
        "deck_variables": vars_for_deck,
    }

    manifest_path = out_dir / "analysis_manifest.json"
    write_json(manifest_path, analysis_manifest)

    # ------------------------------------------------------------------
    # Checks & balances: financial verification + Marp render verification
    # ------------------------------------------------------------------
    run_cmd(["python", str(VERIFY_FINANCIALS), str(manifest_path.resolve())], cwd=ROOT)
    run_cmd(["python", str(RENDER_VERIFY), str(md_out.resolve())], cwd=ROOT)

    print("[OK] Pipeline run complete")
    print(f"[OK] Gold: {gold_path}")
    print(f"[OK] Manifest: {manifest_path}")
    print(f"[OK] Deck: {md_out}")


if __name__ == "__main__":
    main()
