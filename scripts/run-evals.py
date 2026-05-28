#!/usr/bin/env python3
"""
Run evals against AGENTS.md via claude-ext and save outputs to results/.

Each eval set is grouped by domain (one JSON file per domain in evals/), but they
all exercise the single AGENTS.md routing document — there is no per-domain skill
file anymore.

Usage:
    python3 scripts/run-evals.py [domain] [eval_id]
    python3 scripts/run-evals.py commerce-storefront        # all evals in that domain
    python3 scripts/run-evals.py commerce-storefront 6      # only eval 6
    python3 scripts/run-evals.py                            # all domains, all evals
    python3 scripts/run-evals.py --runs 3 commerce-storefront 6
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
EVALS_DIR = REPO_ROOT / "evals"
RESULTS_DIR = REPO_ROOT / "results"
AGENTS_MD = REPO_ROOT / "skills" / "AGENTS.md"
CLAUDE_CONFIG_DIR = Path.home() / ".claude-external"
CLAUDE_MD = CLAUDE_CONFIG_DIR / "CLAUDE.md"

DOMAIN_NAMES = ["commerce-storefront", "commerce-backend", "commerce-da"]
DEFAULT_NUM_RUNS = 1


def write_claude_md():
    """Load only AGENTS.md into the external Claude config.

    Per-source guides are intentionally excluded so the agent must follow
    AGENTS.md's routing table to navigate to the correct guide for each question.
    Pre-loading all guides would bypass that routing decision and make routing
    evals meaningless.
    """
    CLAUDE_MD.write_text(f"@{AGENTS_MD}\n")


def run_eval(prompt: str, cwd: Path, timeout: int = 300) -> tuple[str, list[str], float]:
    """Run one eval and return (text_output, fetched_urls, elapsed_seconds)."""
    env = {**os.environ, "CLAUDE_CONFIG_DIR": str(CLAUDE_CONFIG_DIR)}
    start = time.time()
    result = subprocess.run(
        ["claude", "-p", prompt, "--output-format", "stream-json", "--verbose"],
        env=env,
        cwd=cwd,
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    elapsed = time.time() - start

    if result.returncode != 0:
        return f"[ERROR exit={result.returncode}]\n{result.stderr}", [], elapsed

    text_output = ""
    fetched_urls: list[str] = []

    for line in result.stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue

        event_type = event.get("type")
        if event_type == "result":
            text_output = event.get("result", "")
        elif event_type == "assistant":
            for block in event.get("message", {}).get("content", []):
                if block.get("type") == "tool_use" and block.get("name") == "WebFetch":
                    url = block.get("input", {}).get("url", "")
                    if url:
                        fetched_urls.append(url)

    return text_output, fetched_urls, elapsed


def save_result(domain, eval_id, run, prompt, expected, actual, elapsed, fetched_urls=None):
    domain_results = RESULTS_DIR / domain
    domain_results.mkdir(parents=True, exist_ok=True)
    path = domain_results / f"eval-{eval_id:02d}-run{run}.md"

    fetched_section = ""
    if fetched_urls:
        fetched_section = "\n## Fetched URLs\n\n" + "\n".join(f"- {u}" for u in fetched_urls) + "\n"

    path.write_text(
        f"# {domain} — eval {eval_id} run {run}\n\n"
        f"**Time:** {elapsed:.1f}s\n\n"
        f"## Prompt\n\n{prompt}\n\n"
        f"## Expected key points\n\n{expected}\n\n"
        f"## Actual output\n\n{actual}\n"
        + fetched_section
    )
    return path


def run_domain(domain, cwd: Path, only_eval_id=None, num_runs=DEFAULT_NUM_RUNS):
    evals_path = EVALS_DIR / f"{domain}.json"
    if not evals_path.exists():
        print(f"  [skip] no evals at {evals_path}")
        return

    domain_results = RESULTS_DIR / domain
    domain_results.mkdir(parents=True, exist_ok=True)

    evals = json.loads(evals_path.read_text())["evals"]
    if only_eval_id is not None:
        evals = [e for e in evals if e["id"] == only_eval_id]
        if not evals:
            print(f"  [skip] no eval with id={only_eval_id} in {domain}")
            return
        # When running a single eval, only clear that eval's result files
        for f in domain_results.glob(f"eval-{only_eval_id:02d}-run*.md"):
            f.unlink()
    else:
        # Full run — clear all stale results
        for f in domain_results.glob("eval-*.md"):
            f.unlink()

    total = len(evals) * num_runs
    print(f"\n{'='*60}")
    print(f"Domain: {domain}  ({len(evals)} evals × {num_runs} runs = {total} calls)")
    print(f"{'='*60}")

    write_claude_md()

    for ev in evals:
        eval_id = ev["id"]
        prompt = ev["prompt"]
        expected = ev["expected_output"]

        for run in range(1, num_runs + 1):
            print(f"  eval {eval_id:02d} run {run}: {prompt[:55]}...")
            try:
                actual, fetched_urls, elapsed = run_eval(prompt, cwd)
                path = save_result(domain, eval_id, run, prompt, expected, actual, elapsed, fetched_urls)
                fetch_note = f"  [{len(fetched_urls)} fetched]" if fetched_urls else ""
                print(f"    → {path.relative_to(REPO_ROOT)}  ({elapsed:.1f}s){fetch_note}")
            except subprocess.TimeoutExpired:
                print(f"    → TIMEOUT after 300s")
            except Exception as e:
                print(f"    → ERROR: {e}")


def main():
    parser = argparse.ArgumentParser(description="Run evals against AGENTS.md via claude-ext")
    parser.add_argument(
        "domain",
        nargs="?",
        help="Domain name (default: all domains)",
    )
    parser.add_argument(
        "eval_id",
        nargs="?",
        type=int,
        help="Run only this eval id",
    )
    parser.add_argument(
        "--runs",
        type=int,
        default=DEFAULT_NUM_RUNS,
        metavar="N",
        help=f"Runs per eval (default: {DEFAULT_NUM_RUNS}; use 3 when debugging variance)",
    )
    args = parser.parse_args()

    if args.runs < 1:
        parser.error("--runs must be at least 1")

    domains = [args.domain] if args.domain else DOMAIN_NAMES

    scratch = Path(tempfile.mkdtemp(prefix="claude-eval-"))
    try:
        for domain in domains:
            if domain not in DOMAIN_NAMES:
                print(f"Unknown domain: {domain}. Choose from: {', '.join(DOMAIN_NAMES)}")
                sys.exit(1)
            run_domain(domain, scratch, args.eval_id, num_runs=args.runs)
    finally:
        shutil.rmtree(scratch, ignore_errors=True)

    print(f"\nDone. Results in {RESULTS_DIR.relative_to(REPO_ROOT)}/")


if __name__ == "__main__":
    main()
