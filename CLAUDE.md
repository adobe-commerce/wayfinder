# Claude / Claude Code context

This repository defines **Claude Agent Skills** for Adobe Commerce + EDS storefront engineering. For full intent, layout, accuracy expectations, and editing rules, read **`AGENTS.md`** first.

## Claude-specific notes

- **Skills root**: `skills/commerce-setup`, `skills/commerce-develop`, `skills/commerce-troubleshoot`. Each contains `SKILL.md` (YAML frontmatter + body) and `evals/`.
- **Source of truth**: Official public documentation — fetched via WebFetch from the URLs in each `SKILL.md`. Do not maintain static copies of doc content in this repo.
- **Packaging**: Use the **skill-creator** plugin's `scripts.package_skill` then `claude skill install` as documented in `README.md`. Paths on a given machine may differ.
- **Python**: Prefer the **Homebrew Python 3.13** called out in `README.md` for eval scripts (system Python may be too old for union syntax used in tooling).
- **Triggers**: The `description:` block in each `SKILL.md` frontmatter controls discovery; after large edits, consider **description optimization** via skill-creator's loop scripts.

## When helping a user

1. Pick the skill that matches **setup vs develop vs troubleshoot** (see table in `AGENTS.md`).
2. Pull facts from **official doc URLs** listed in the skill's "Fetch Strategy" table — use WebFetch. Inline content in `SKILL.md` is supplementary (cross-cutting facts, known quirks).
3. If guidance conflicts with **Experience League**, the **user's repo**, or **runtime behavior**, trust the latter and propose a `SKILL.md` correction.

## Docs for other agents

- Canonical multi-tool agent brief: **`AGENTS.md`**
