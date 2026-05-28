#!/usr/bin/env python3
"""
Score eval results produced by run-evals.py.

Reads each per-run result file (eval-NN-runM.md), sends (expected + actual)
to claude for scoring, and prints a per-eval aggregate summary.

Two independent scores per eval:
  Synthesis — PASS/PARTIAL/FAIL: did the answer address the expected key points?
  Routing   — ROUTED/PARTIAL/UNROUTED: did the response cite the expected source domains?

Usage:
    python3 scripts/score-evals.py [skill_name]
    python3 scripts/score-evals.py commerce-storefront
    python3 scripts/score-evals.py  # scores all
"""

import json
import os
import re
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
RESULTS_DIR = REPO_ROOT / "results"
EVALS_DIR = REPO_ROOT / "evals"
SKILL_NAMES = ["commerce-storefront", "commerce-backend", "commerce-da"]

SCORING_PROMPT = """\
You are scoring a skill response against a rubric. Be strict and concise.

## Expected key points
{expected}

## Actual response
{actual}

## Task
Score this response as one of:
- PASS — all key points from expected are clearly addressed; no clearly fabricated facts
- PARTIAL — most key points addressed but 1-2 are missing or inaccurate
- FAIL — a major key point is missing; or a clearly fabricated fact is present

Important: Do NOT flag URLs as fabricated unless they are obviously made up (e.g. placeholder
text, made-up product names, structurally implausible). Plausible documentation URLs should be
assumed to be legitimate citations.

Respond in exactly this format:
SCORE: <PASS|PARTIAL|FAIL>
HIT: <comma-separated list of expected points that were addressed>
MISS: <comma-separated list of expected points that were missing or wrong>
NOTE: <one sentence explaining the score, or "none">
"""

URL_RE = re.compile(r"https?://[^\s\)\]\"'<>]+")

SYNTH_GRADE = {"PASS": "✅", "PARTIAL": "⚠️", "FAIL": "❌", "ERROR": "?"}
ROUTE_GRADE = {"ROUTED": "🔀", "PARTIAL": "⚡", "UNROUTED": "🚫", "N/A": "—"}


def score_result(expected: str, actual: str) -> dict:
    prompt = SCORING_PROMPT.format(expected=expected, actual=actual)
    result = subprocess.run(
        ["claude", "-p", prompt],
        capture_output=True,
        text=True,
        timeout=60,
    )
    raw = result.stdout.strip()
    parsed = {"score": "ERROR", "hit": "", "miss": "", "note": raw[:120], "raw": raw}
    for line in raw.splitlines():
        if line.startswith("SCORE:"):
            parsed["score"] = line.split(":", 1)[1].strip()
        elif line.startswith("HIT:"):
            parsed["hit"] = line.split(":", 1)[1].strip()
        elif line.startswith("MISS:"):
            parsed["miss"] = line.split(":", 1)[1].strip()
        elif line.startswith("NOTE:"):
            parsed["note"] = line.split(":", 1)[1].strip()
    return parsed


def check_routing(expected_sources: list[str], actual: str) -> dict:
    """Check whether expected source domains appear in URLs cited in the response."""
    if not expected_sources:
        return {"score": "N/A", "found": [], "missing": []}
    urls = URL_RE.findall(actual)
    found = [d for d in expected_sources if any(d in url for url in urls)]
    missing = [d for d in expected_sources if d not in found]
    if not missing:
        score = "ROUTED"
    elif found:
        score = "PARTIAL"
    else:
        score = "UNROUTED"
    return {"score": score, "found": found, "missing": missing}


def extract_sections(content: str) -> tuple[str, str]:
    """Extract expected and actual sections from a result markdown file."""
    expected_match = re.search(r'\n## Expected key points\n\n(.*?)\n## Actual output', content, re.DOTALL)
    actual_match = re.search(r'\n## Actual output\n\n(.*?)$', content, re.DOTALL)
    expected = expected_match.group(1).strip() if expected_match else ""
    actual = actual_match.group(1).strip() if actual_match else ""
    return expected, actual


def parse_eval_filename(name: str) -> tuple[int, int]:
    """Parse eval-NN-runM.md → (eval_id, run). Returns (id, 0) if no run suffix."""
    m = re.match(r"eval-(\d+)-run(\d+)", name)
    if m:
        return int(m.group(1)), int(m.group(2))
    m = re.match(r"eval-(\d+)", name)
    if m:
        return int(m.group(1)), 0
    return -1, 0


def aggregate_synthesis(run_scores: list[str]) -> str:
    """Majority vote; FAIL wins ties that include FAIL."""
    counts = {"PASS": 0, "PARTIAL": 0, "FAIL": 0, "ERROR": 0}
    for s in run_scores:
        counts[s] = counts.get(s, 0) + 1
    n = len(run_scores)
    if counts["PASS"] > n / 2:
        return "PASS"
    if counts["FAIL"] > n / 2:
        return "FAIL"
    if counts["FAIL"] >= 1 and counts["PASS"] == 0:
        return "FAIL"
    return "PARTIAL"


def aggregate_routing(run_scores: list[str]) -> str:
    """Majority vote for routing scores."""
    if not run_scores or all(s == "N/A" for s in run_scores):
        return "N/A"
    counts: dict[str, int] = defaultdict(int)
    for s in run_scores:
        counts[s] += 1
    n = len(run_scores)
    if counts["ROUTED"] > n / 2:
        return "ROUTED"
    if counts["UNROUTED"] > n / 2:
        return "UNROUTED"
    return "PARTIAL"


def load_expected_sources(skill_name: str) -> dict[int, list[str]]:
    """Return {eval_id: [domain, ...]} from the eval JSON for this skill."""
    evals_path = EVALS_DIR / f"{skill_name}.json"
    if not evals_path.exists():
        return {}
    data = json.loads(evals_path.read_text())
    return {ev["id"]: ev.get("expected_sources", []) for ev in data.get("evals", [])}


def score_skill(skill_name: str) -> dict:
    skill_results = RESULTS_DIR / skill_name
    if not skill_results.exists():
        print(f"  [skip] no results for {skill_name} — run run-evals.py first")
        return {}

    result_files = sorted(skill_results.glob("eval-*.md"))
    if not result_files:
        print(f"  [skip] no eval-*.md files in {skill_results}")
        return {}

    expected_sources_map = load_expected_sources(skill_name)

    print(f"\n{'='*60}")
    print(f"Scoring: {skill_name}  ({len(result_files)} result files)")
    print(f"{'='*60}")

    # Group result files by eval_id
    by_eval: dict[int, list] = defaultdict(list)
    for path in result_files:
        eval_id, run = parse_eval_filename(path.stem)
        by_eval[eval_id].append((run, path))

    eval_results = {}
    for eval_id in sorted(by_eval.keys()):
        runs = sorted(by_eval[eval_id])
        expected_sources = expected_sources_map.get(eval_id, [])
        run_synth_scores = []
        run_route_scores = []

        for run, path in runs:
            content = path.read_text()
            expected, actual = extract_sections(content)
            label = f"eval-{eval_id:02d}" + (f"-run{run}" if run else "")
            print(f"  {label}...", end=" ", flush=True)
            scored = score_result(expected, actual)
            routed = check_routing(expected_sources, actual)
            synth_emoji = SYNTH_GRADE.get(scored["score"], "?")
            route_emoji = ROUTE_GRADE.get(routed["score"], "?")
            print(f"{synth_emoji} {scored['score']}  {route_emoji} {routed['score']}")
            if scored["miss"] and scored["miss"].lower() != "none":
                miss = scored["miss"]
                if len(miss) > 200:
                    miss = miss[:200] + "..."
                print(f"    miss: {miss}")
            if routed["missing"]:
                print(f"    not routed to: {', '.join(routed['missing'])}")
            run_synth_scores.append(scored["score"])
            run_route_scores.append(routed["score"])

        eval_results[eval_id] = {
            "synthesis": run_synth_scores,
            "routing": run_route_scores,
        }

    return eval_results


def print_summary(all_results: dict[str, dict[int, dict]]):
    if not all_results:
        return
    print(f"\n{'='*60}")
    print("SUMMARY (per-eval, with run-by-run consistency)")
    print(f"{'='*60}")
    synth_totals: dict[str, int] = {"PASS": 0, "PARTIAL": 0, "FAIL": 0}
    route_totals: dict[str, int] = {"ROUTED": 0, "PARTIAL": 0, "UNROUTED": 0, "N/A": 0}
    for skill, eval_results in all_results.items():
        for eval_id, scores in sorted(eval_results.items()):
            synth_runs = scores["synthesis"]
            route_runs = scores["routing"]
            grades_str = "".join(SYNTH_GRADE.get(s, "?") for s in synth_runs)
            synth_agg = aggregate_synthesis(synth_runs)
            route_agg = aggregate_routing(route_runs)
            synth_emoji = SYNTH_GRADE.get(synth_agg, "?")
            route_emoji = ROUTE_GRADE.get(route_agg, "?")
            synth_totals[synth_agg] = synth_totals.get(synth_agg, 0) + 1
            route_totals[route_agg] = route_totals.get(route_agg, 0) + 1
            print(f"  {grades_str}  →  {synth_emoji} {synth_agg:<7}  {route_emoji} {route_agg:<10}  {skill}/eval-{eval_id:02d}")
    total = sum(synth_totals.values())
    print(f"\n  Synthesis ({total} evals): ✅ {synth_totals.get('PASS', 0)}  ⚠️ {synth_totals.get('PARTIAL', 0)}  ❌ {synth_totals.get('FAIL', 0)}")
    routed = route_totals.get("ROUTED", 0)
    partial = route_totals.get("PARTIAL", 0)
    unrouted = route_totals.get("UNROUTED", 0)
    na = route_totals.get("N/A", 0)
    route_total = routed + partial + unrouted
    na_note = f"  (+ {na} N/A)" if na else ""
    print(f"  Routing   ({route_total} evals): 🔀 {routed} routed  ⚡ {partial} partial  🚫 {unrouted} unrouted{na_note}")


def main():
    target = sys.argv[1] if len(sys.argv) > 1 else None
    skills = [target] if target else SKILL_NAMES

    all_results = {}
    for skill in skills:
        if skill not in SKILL_NAMES:
            print(f"Unknown skill: {skill}. Choose from: {', '.join(SKILL_NAMES)}")
            sys.exit(1)
        result = score_skill(skill)
        if result:
            all_results[skill] = result

    print_summary(all_results)


if __name__ == "__main__":
    main()
