# Fixtures

Example codebases showing how to reference the hosted AGENTS.md from a user's project.

## Pattern

User projects (storefront boilerplate forks, App Builder starters, backend modules) add a minimal local `AGENTS.md` that tells the AI agent where to fetch the real guidance:

```
AGENTS.md          ← stub: one fetch instruction + project type hint
```

The stub is intentionally small. All routing logic, operating principles, disambiguation examples, and per-source guides live in the hosted files and are fetched at query time.

## Stub template

```markdown
# AGENTS.md

This is an Adobe Commerce [project type] repository.

Before answering any question, fetch and follow the agent guidance at:
https://raw.githubusercontent.com/adobe-commerce/wayfinder/main/skills/AGENTS.md

Read that file completely before routing to a per-source guide or fetching documentation.
```

## Fixtures in this folder

| Directory | Represents |
| --- | --- |
| `storefront-boilerplate/` | EDS storefront fork (hlxsites/aem-boilerplate-commerce pattern) |
| `app-builder/` | App Builder starter project |

## Updating the base URL

If the hosted files move to a custom domain, update the URL in:
1. Each project's local `AGENTS.md` stub
2. The `> Remote base URL:` header in `skills/AGENTS.md`

The sub-doc links in `skills/AGENTS.md` stay relative and resolve automatically once the base URL is correct.
