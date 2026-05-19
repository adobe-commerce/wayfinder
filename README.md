# Commerce DX Skills

Three Claude skills for Adobe Commerce EDS storefront engineers.

**AI agents and new contributors:** see [`AGENTS.md`](AGENTS.md) for project intent and layout; [`CLAUDE.md`](CLAUDE.md) for Claude-specific packaging and workflow notes.

| Skill | Purpose |
|---|---|
| `commerce-setup` | Environment creation, Storefront Configuration, CORS, DA authoring/permissions |
| `commerce-develop` | Block/dropin development, GraphQL overrides, prerender, recommendations |
| `commerce-troubleshoot` | $0 prices, 418 errors, search, DA access, CDN sync, cart errors |

## Iterating on a skill

**Edit content** — guides are the source of truth:
```
docs/guides/           ← edit here
skills/*/references/   ← symlinks to docs/guides/ (do not edit directly)
skills/*/SKILL.md      ← skill instructions (edit directly)
```

**Run evals** against a skill after changes:
```bash
# Requires skill-creator at ~/.claude/plugins/cache/claude-plugins-official/skill-creator/...
cd /path/to/skill-creator
/opt/homebrew/bin/python3.13 -m scripts.run_evals \
  /path/to/this/repo/skills/commerce-setup \
  --output /path/to/this/repo/commerce-setup-workspace/iteration-N
```

**Review eval output** in the browser:
```bash
/opt/homebrew/bin/python3.13 generate_review.py \
  /path/to/this/repo/commerce-setup-workspace/iteration-N \
  --port 8091
```

Use ports 8091/8092/8093 for setup/develop/troubleshoot to run all three at once.

**Package and install** after evals look good:
```bash
/opt/homebrew/bin/python3.13 -m scripts.package_skill \
  /path/to/this/repo/skills/commerce-setup
claude skill install commerce-setup.skill
```

Repeat for `commerce-develop` and `commerce-troubleshoot`.

## Official docs

LLM-friendly format: `https://experienceleague.adobe.com/developer/commerce/storefront/llms.txt`

Section-specific `.txt` files are referenced directly in each `SKILL.md`.

## Notes

- Use `/opt/homebrew/bin/python3.13`, not system `python3` (system is 3.9, missing `X | Y` union syntax)
- `search-commerce-docs` MCP tool requires `aio auth login` before use
- Storefront Configuration is managed via the AEM Admin API — not DA, not `config.json` in the repo
