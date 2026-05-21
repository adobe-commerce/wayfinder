#!/usr/bin/env python3
"""
Score eval results produced by run-evals.py.

Reads each per-run result file (eval-NN-runM.md), sends (expected + actual)
to claude for scoring, and prints a per-eval aggregate summary.

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


GRADE = {"PASS": "✅", "PARTIAL": "⚠️", "FAIL": "❌", "ERROR": "?"}


def score_skill(skill_name: str) -> dict:
    skill_results = RESULTS_DIR / skill_name
    if not skill_results.exists():
        print(f"  [skip] no results for {skill_name} — run run-evals.py first")
        return {}

    result_files = sorted(skill_results.glob("eval-*.md"))
    if not result_files:
        print(f"  [skip] no eval-*.md files in {skill_results}")
        return {}

    print(f"\n{'='*60}")
    print(f"Scoring: {skill_name}  ({len(result_files)} result files)")
    print(f"{'='*60}")

    # Group result files by eval_id
    by_eval = defaultdict(list)
    for path in result_files:
        eval_id, run = parse_eval_filename(path.stem)
        by_eval[eval_id].append((run, path))

    eval_results = {}
    for eval_id in sorted(by_eval.keys()):
        runs = sorted(by_eval[eval_id])
        run_scores = []
        for run, path in runs:
            content = path.read_text()
            expected, actual = extract_sections(content)
            label = f"eval-{eval_id:02d}" + (f"-run{run}" if run else "")
            print(f"  {label}...", end=" ", flush=True)
            scored = score_result(expected, actual)
            print(f"{GRADE.get(scored['score'], '?')} {scored['score']}")
            if scored["miss"] and scored["miss"].lower() != "none":
                # Indent miss for readability; truncate if very long
                miss = scored["miss"]
                if len(miss) > 200:
                    miss = miss[:200] + "..."
                print(f"    miss: {miss}")
            run_scores.append(scored["score"])
        eval_results[eval_id] = run_scores

    return eval_results


def aggregate(run_scores: list[str]) -> str:
    """Majority vote; FAIL wins if there's a tie that includes FAIL."""
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


def print_summary(all_results: dict[str, dict[int, list[str]]]):
    if not all_results:
        return
    print(f"\n{'='*60}")
    print("SUMMARY (per-eval, with run-by-run consistency)")
    print(f"{'='*60}")
    totals = {"PASS": 0, "PARTIAL": 0, "FAIL": 0}
    for skill, eval_results in all_results.items():
        for eval_id, runs in sorted(eval_results.items()):
            grades_str = "".join(GRADE.get(s, "?") for s in runs)
            agg = aggregate(runs)
            agg_emoji = GRADE.get(agg, "?")
            totals[agg] = totals.get(agg, 0) + 1
            print(f"  {grades_str}  →  {agg_emoji} {skill}/eval-{eval_id:02d}")
    total = sum(totals.values())
    print(f"\n  Total evals: {total}  ✅ {totals.get('PASS', 0)}  ⚠️ {totals.get('PARTIAL', 0)}  ❌ {totals.get('FAIL', 0)}")


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
