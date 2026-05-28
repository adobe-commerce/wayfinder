#!/usr/bin/env python3
"""
Score eval results produced by run-evals.py.

Reads each per-run result file (eval-NN-runM.md), sends (expected + actual)
to claude for scoring, and prints a per-eval aggregate summary.

Three independent scores per eval:
  Synthesis — PASS/PARTIAL/FAIL/ERROR: did the answer address the expected key points?
  Citation  — ROUTED/PARTIAL/UNROUTED: did the response cite the expected source domains?
  Fetch     — FETCHED/PARTIAL/UNFETCHED: did the agent actually call WebFetch for those domains?
              (N/A when result file predates fetch tracking, or no expected_sources defined)

Usage:
    python3 scripts/score-evals.py [skill_name]
    python3 scripts/score-evals.py commerce-storefront
    python3 scripts/score-evals.py  # scores all
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from collections import defaultdict
from pathlib import Path
from urllib.parse import urlparse

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

SYNTH_GRADE = {"PASS": "✅", "PARTIAL": "⚠️", "FAIL": "❌", "ERROR": "💥"}
ROUTE_GRADE = {"ROUTED": "🔀", "PARTIAL": "⚡", "UNROUTED": "🚫", "N/A": "—"}
FETCH_GRADE = {"FETCHED": "🌐", "PARTIAL": "⚡", "UNFETCHED": "💭", "N/A": "—"}


def _domain_matches(domain: str, url: str) -> bool:
    """Return True if url's hostname equals or is a subdomain of domain."""
    try:
        netloc = urlparse(url).netloc.lower().split(":")[0]  # strip port
        d = domain.lower()
        return netloc == d or netloc.endswith("." + d)
    except Exception:
        return False


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
    if not actual:
        # Empty actual (malformed file) — score as N/A, not UNROUTED
        return {"score": "N/A", "found": [], "missing": []}
    urls = URL_RE.findall(actual)
    found = [d for d in expected_sources if any(_domain_matches(d, url) for url in urls)]
    missing = [d for d in expected_sources if d not in found]
    if not missing:
        score = "ROUTED"
    elif found:
        score = "PARTIAL"
    else:
        score = "UNROUTED"
    return {"score": score, "found": found, "missing": missing}


def check_fetch_routing(expected_sources: list[str], fetched_urls: list[str] | None) -> dict:
    """Check whether expected source domains were actually fetched via WebFetch."""
    if not expected_sources or fetched_urls is None:
        # None means no fetch data in this result file (old format)
        return {"score": "N/A", "found": [], "missing": []}
    found = [d for d in expected_sources if any(_domain_matches(d, url) for url in fetched_urls)]
    missing = [d for d in expected_sources if d not in found]
    if not missing:
        score = "FETCHED"
    elif found:
        score = "PARTIAL"
    else:
        score = "UNFETCHED"
    return {"score": score, "found": found, "missing": missing}


def extract_sections(content: str) -> tuple[str, str]:
    """Extract expected and actual sections from a result markdown file."""
    expected_match = re.search(r'\n## Expected key points\n\n(.*?)\n## Actual output', content, re.DOTALL)
    actual_match = re.search(r'\n## Actual output\n\n(.*?)(?:\n## Fetched URLs\n|\Z)', content, re.DOTALL)
    expected = expected_match.group(1).strip() if expected_match else ""
    actual = actual_match.group(1).strip() if actual_match else ""
    return expected, actual


def extract_fetched_urls(content: str) -> list[str] | None:
    """Return fetched URLs from the result file, or None if the section is absent (old format)."""
    m = re.search(r'\n## Fetched URLs\n\n(.*?)$', content, re.DOTALL)
    if m is None:
        return None
    return URL_RE.findall(m.group(1))


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
    """Majority vote; FAIL wins ties that include FAIL. All-ERROR surfaces as ERROR."""
    counts = {"PASS": 0, "PARTIAL": 0, "FAIL": 0, "ERROR": 0}
    for s in run_scores:
        counts[s] = counts.get(s, 0) + 1
    # Exclude ERROR runs from the vote; surface ERROR only when all runs failed
    valid = [s for s in run_scores if s != "ERROR"]
    if not valid:
        return "ERROR"
    n = len(valid)
    if counts["PASS"] > n / 2:
        return "PASS"
    if counts["FAIL"] > n / 2:
        return "FAIL"
    if counts["FAIL"] >= 1 and counts["PASS"] == 0:
        return "FAIL"
    return "PARTIAL"


def aggregate_routing(run_scores: list[str]) -> str:
    """Majority vote for routing scores; N/A runs are excluded from the denominator."""
    if not run_scores or all(s == "N/A" for s in run_scores):
        return "N/A"
    valid = [s for s in run_scores if s != "N/A"]
    n = len(valid)
    counts: dict[str, int] = defaultdict(int)
    for s in valid:
        counts[s] += 1
    if counts["ROUTED"] > n / 2:
        return "ROUTED"
    if counts["UNROUTED"] > n / 2:
        return "UNROUTED"
    return "PARTIAL"


def aggregate_fetch(run_scores: list[str]) -> str:
    """Majority vote for fetch scores; N/A runs are excluded from the denominator."""
    if not run_scores or all(s == "N/A" for s in run_scores):
        return "N/A"
    valid = [s for s in run_scores if s != "N/A"]
    n = len(valid)
    counts: dict[str, int] = defaultdict(int)
    for s in valid:
        counts[s] += 1
    if counts["FETCHED"] > n / 2:
        return "FETCHED"
    if counts["UNFETCHED"] > n / 2:
        return "UNFETCHED"
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
        run_fetch_scores = []

        for run, path in runs:
            content = path.read_text()
            expected, actual = extract_sections(content)
            fetched_urls = extract_fetched_urls(content)
            label = f"eval-{eval_id:02d}" + (f"-run{run}" if run else "")
            print(f"  {label}...", end=" ", flush=True)
            scored = score_result(expected, actual)
            routed = check_routing(expected_sources, actual)
            fetched = check_fetch_routing(expected_sources, fetched_urls)
            synth_emoji = SYNTH_GRADE.get(scored["score"], "?")
            route_emoji = ROUTE_GRADE.get(routed["score"], "?")
            fetch_emoji = FETCH_GRADE.get(fetched["score"], "?")
            print(f"{synth_emoji} {scored['score']}  {route_emoji} {routed['score']}  {fetch_emoji} {fetched['score']}")
            if scored["miss"] and scored["miss"].lower() != "none":
                miss = scored["miss"]
                if len(miss) > 200:
                    miss = miss[:200] + "..."
                print(f"    miss: {miss}")
            if routed["missing"]:
                print(f"    not cited: {', '.join(routed['missing'])}")
            if fetched["missing"]:
                print(f"    not fetched: {', '.join(fetched['missing'])}")
            run_synth_scores.append(scored["score"])
            run_route_scores.append(routed["score"])
            run_fetch_scores.append(fetched["score"])

        eval_results[eval_id] = {
            "synthesis": run_synth_scores,
            "routing": run_route_scores,
            "fetch": run_fetch_scores,
        }

    return eval_results


def print_summary(all_results: dict[str, dict[int, dict]]):
    if not all_results:
        return
    print(f"\n{'='*60}")
    print("SUMMARY (per-eval, with run-by-run consistency)")
    print(f"{'='*60}")
    synth_totals: dict[str, int] = {"PASS": 0, "PARTIAL": 0, "FAIL": 0, "ERROR": 0}
    route_totals: dict[str, int] = {"ROUTED": 0, "PARTIAL": 0, "UNROUTED": 0, "N/A": 0}
    fetch_totals: dict[str, int] = {"FETCHED": 0, "PARTIAL": 0, "UNFETCHED": 0, "N/A": 0}
    for skill, eval_results in all_results.items():
        for eval_id, scores in sorted(eval_results.items()):
            synth_runs = scores["synthesis"]
            route_runs = scores["routing"]
            fetch_runs = scores["fetch"]
            grades_str = "".join(SYNTH_GRADE.get(s, "?") for s in synth_runs)
            synth_agg = aggregate_synthesis(synth_runs)
            route_agg = aggregate_routing(route_runs)
            fetch_agg = aggregate_fetch(fetch_runs)
            synth_emoji = SYNTH_GRADE.get(synth_agg, "?")
            route_emoji = ROUTE_GRADE.get(route_agg, "?")
            fetch_emoji = FETCH_GRADE.get(fetch_agg, "?")
            synth_totals[synth_agg] = synth_totals.get(synth_agg, 0) + 1
            route_totals[route_agg] = route_totals.get(route_agg, 0) + 1
            fetch_totals[fetch_agg] = fetch_totals.get(fetch_agg, 0) + 1
            print(f"  {grades_str}  →  {synth_emoji} {synth_agg:<7}  {route_emoji} {route_agg:<10}  {fetch_emoji} {fetch_agg:<10}  {skill}/eval-{eval_id:02d}")

    total = sum(synth_totals.values())
    error_note = f"  💥 {synth_totals['ERROR']} errors" if synth_totals["ERROR"] else ""
    print(f"\n  Synthesis ({total} evals): ✅ {synth_totals['PASS']}  ⚠️ {synth_totals['PARTIAL']}  ❌ {synth_totals['FAIL']}{error_note}")

    route_n = route_totals["ROUTED"] + route_totals["PARTIAL"] + route_totals["UNROUTED"]
    route_na = route_totals["N/A"]
    route_na_note = f"  (+ {route_na} N/A)" if route_na else ""
    print(f"  Citation  ({route_n} evals): 🔀 {route_totals['ROUTED']} routed  ⚡ {route_totals['PARTIAL']} partial  🚫 {route_totals['UNROUTED']} unrouted{route_na_note}")

    fetch_n = fetch_totals["FETCHED"] + fetch_totals["PARTIAL"] + fetch_totals["UNFETCHED"]
    fetch_na = fetch_totals["N/A"]
    fetch_na_note = f"  (+ {fetch_na} N/A)" if fetch_na else ""
    print(f"  Fetched   ({fetch_n} evals): 🌐 {fetch_totals['FETCHED']} fetched  ⚡ {fetch_totals['PARTIAL']} partial  💭 {fetch_totals['UNFETCHED']} unfetched{fetch_na_note}")


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
