# Wayfinder 📖 🐙

> *Let me ~~Google~~ ask an Agent for you.*

Wayfinder is an AGENTS.md-based routing system that helps AI agents find the right documentation source when answering Adobe Commerce questions. Adobe's docs span multiple properties — aem.live, docs.da.live, experienceleague.adobe.com, and developer.adobe.com/commerce — each with different access patterns. Wayfinder directs agents to the right source so they retrieve authoritative docs rather than guessing from training data.

## Using these skills in your project

Open (or create) `AGENTS.md` (or `CLAUDE.md` if you're using Claude) at the root of your Commerce repo and add the following line at the top:

```
Fetch and follow the instructions at: https://cdn.jsdelivr.net/gh/adobe-commerce/wayfinder@main/skills/AGENTS.md
```

That's it. Your agent will fetch the routing guide at the start of each session and use it when answering Commerce questions.

<img width="800" height="502" alt="switchboard-use" src="https://github.com/user-attachments/assets/6548a7eb-e80d-449d-b590-a08869fe5857" />


## How it works

`skills/AGENTS.md` is a slim router loaded as agent context. It maps user questions to one of five per-source guides in `skills/docs/`. Each guide provides entry points and fetch-first instructions so the agent retrieves authoritative docs rather than guessing.

```
skills/
  AGENTS.md                # router — loaded as agent context
  docs/
    storefront.md          # Commerce EDS drop-ins, boilerplate, storefront GraphQL
    experience-league.md   # Admin, B2B, catalog, cloud (PaaS/SaaS)
    document-authoring.md  # da.live authoring workflow and permissions
    aem-eds.md             # AEM blocks, CDN, Sidekick
    commerce-developer.md  # App Builder, API Mesh, extensibility
    *.md                   # any other unique resource location for documentation
```

## Usage Metrics

jsdelivr tracks requests to the hosted skills files. View stats at:

- **All files:** https://data.jsdelivr.com/v1/stats/packages/gh/adobe-commerce/wayfinder@main/files
- **This version:** https://data.jsdelivr.com/v1/stats/packages/gh/adobe-commerce/wayfinder@main
- **All versions:** https://data.jsdelivr.com/v1/stats/packages/gh/adobe-commerce/wayfinder

## Running evals

Evals exercise the full routing chain via an isolated Claude config (`claude-ext`) that loads only `AGENTS.md` and the per-source guides.

**1. Set up the external Claude alias:**
```sh
alias claude-ext 'CLAUDE_CONFIG_DIR=~/.claude-external claude'
```

**2. Configure `~/.claude-external/settings.json` with the required permissions:**
```json
{
  "permissions": {
    "allow": [
      "WebSearch",
      "WebFetch(domain:experienceleague.adobe.com)",
      "WebFetch(domain:www.aem.live)",
      "WebFetch(domain:aem.live)",
      "WebFetch(domain:da.live)",
      "WebFetch(domain:docs.da.live)",
      "WebFetch(domain:cdn.jsdelivr.net)",
      "WebFetch(domain:github.com)",
      "WebFetch(domain:raw.githubusercontent.com)",
      "WebFetch(domain:developer.adobe.com)"
    ]
  },
  "skipAutoPermissionPrompt": true
}
```
Without these, the agent falls back to training data instead of fetching live docs.

**3. Run evals:**

```sh
python3 scripts/run-evals.py                    # full routing suite (default)
python3 scripts/run-evals.py routing            # same; full routing suite
python3 scripts/run-evals.py synthesis          # full synthesis suite
python3 scripts/run-evals.py routing 4          # single eval by type/id
python3 scripts/run-evals.py --runs 3 routing   # 3 runs per eval (variance testing)
```

Results are written to `results/<domain>/eval-NN-runN.md` — each file has the prompt, expected key points, actual output, and elapsed time.
