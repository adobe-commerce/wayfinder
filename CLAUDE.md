Always read @skills/AGENTS.md.

## Eval system

The eval system tests whether AGENTS.md routes questions to the right documentation source and whether the agent actually fetches from those sources before answering.

### Two eval sets

| File | Purpose | Count | When to run |
|---|---|---|---|
| `evals/routing.json` | Tests non-obvious routing decisions — questions where the agent could plausibly mis-route or answer from training data | 12 | Default; run whenever AGENTS.md or a linked per-source guide changes |
| `evals/synthesis.json` | Tests answer depth and coverage within an already-routed source | 24 | Pre-merge / milestone validation |

Each eval has an `expected_sources` field listing the domain(s) the agent must fetch and cite. The scoring system measures three independent dimensions: Synthesis (answer quality), Citation (did cited URLs match expected domains?), and Fetched (did tool-call traces show actual WebFetch calls to those domains?).

### Running evals

```bash
# Routing evals — default, fast (~3 min)
python3 scripts/run-evals.py

# Synthesis evals — full suite (~15 min)
python3 scripts/run-evals.py synthesis

# Single eval by id
python3 scripts/run-evals.py routing 4

# 3 runs per eval (variance testing)
python3 scripts/run-evals.py --runs 3 routing
```

### Scoring results

```bash
python3 scripts/score-evals.py           # scores routing results (default)
python3 scripts/score-evals.py synthesis
```

### Archiving results

Results are gitignored. Before a new run, copy results to a timestamped archive folder that names the eval type:

```bash
cp -r results/routing results-archive/$(date +%Y-%m-%d)-routing
cp -r results/synthesis results-archive/$(date +%Y-%m-%d)-synthesis
```

`results-archive/` is also gitignored.

### Adding or changing evals

- **Routing eval** (`routing.json`): add when a new routing table row is added to AGENTS.md, or when a question type is known to mis-route. Each entry needs `expected_sources` (the domain(s) the agent must fetch). Aim to keep the routing set to ~3-4 per major source row.
- **Synthesis eval** (`synthesis.json`): add when you want to track answer depth for a specific topic. `expected_sources` is still required.
- Each eval must have a unique `id` within its file and a `domain` field (e.g. `commerce-storefront`) for result labeling.
