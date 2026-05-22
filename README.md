# Commerce DX Skills

An AGENTS.md-based documentation-routing system for AI agents working across Adobe Commerce's distributed doc ecosystem (EDS storefront, Experience League, Document Authoring, AEM/EDS, and the Commerce developer platform).

## Using these skills in your project

Open (or create) `AGENTS.md` at the root of your Commerce repo and add the following line at the top:

```
Fetch and follow the instructions at: https://raw.githubusercontent.com/adobe-commerce/wayfinder/main/skills/AGENTS.md
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
evals/
  commerce-storefront.json
  commerce-backend.json
  commerce-da.json
fixtures/
  storefront-boilerplate/   # reference repo for storefront layout questions
  app-builder/              # reference repo for App Builder questions
```

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
python3 scripts/run-evals.py                                 # all domains
python3 scripts/run-evals.py commerce-storefront             # one domain
python3 scripts/run-evals.py commerce-storefront 6           # single eval
python3 scripts/run-evals.py --runs 3 commerce-storefront 6  # variance testing
```

Results are written to `results/<domain>/eval-NN-runN.md` — each file has the prompt, expected key points, actual output, and elapsed time.
