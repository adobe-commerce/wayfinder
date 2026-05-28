# AGENTS.md

> **Remote base URL:** `https://raw.githubusercontent.com/adobe-commerce/wayfinder/main/skills/`
> Sub-doc paths in this file (e.g. `./docs/storefront.md`) are relative to that base. If you fetched this file remotely, construct absolute URLs by replacing `./docs/` with `https://raw.githubusercontent.com/adobe-commerce/wayfinder/main/skills/docs/`.

Guidance for AI agents working in Adobe Commerce repositories. Use this file to route to the right documentation source, then read the per-source guide for that source before answering.

## Architecture layers

Understanding the stack prevents mis-routing:

```
┌─────────────────────────────────────────────────────┐
│  Commerce Storefront  (experienceleague.adobe.com)  │  drop-ins, commerce blocks, ACO/ACCS wiring
├─────────────────────────────────────────────────────┤
│  EDS / AEM  (aem.live)                              │  delivery infra: CDN, code sync, Sidekick,
│                                                     │  blocks, spreadsheets, local dev — applies
│                                                     │  to ALL EDS sites, including storefront
├──────────────────────┬──────────────────────────────┤
│  Document Authoring  │  Adobe Commerce backend      │
│  (docs.da.live)      │  (experienceleague.adobe.com)│
│  content authoring   │  Admin, catalog, B2B, cloud  │
│  tool and DA-specific│                              │
│  setup/permissions   │                              │
└──────────────────────┴──────────────────────────────┘
```

**Key implication:** When a question is about EDS mechanics — code sync, Sidekick publish, local dev (`aem up`), block authoring pattern, CDN caching, spreadsheets, navigation documents, section metadata, placeholders — use **aem.live** even if the repo is a Commerce storefront. The storefront docs cover only the commerce-specific layer on top.

**DA vs aem.live:** DA is the authoring tool (where content is written and managed). aem.live is the delivery layer (how that content reaches the live site). "My page isn't showing on my live URL" is an aem.live/Sidekick question, not a DA question — the publish workflow is part of the EDS delivery infrastructure.

## Operating principles

1. **Fetch first, name names second.** Do not guess specific names — container names, slot names, config keys, header names, CLI commands, GraphQL fields, Admin paths, URLs, module names, block names, or DA URL patterns. If your answer names any of these, you must have fetched it from the official docs, read it from the user's repo, or read it from a boilerplate reference repo in this session.
2. **Read local code first.** If filesystem access is available, read relevant files before answering. Local code reflects current state and takes precedence over docs — but confirm it's up to date before treating it as authoritative. For storefront layout/DOM questions with no local code, fall back to the boilerplate reference repos.
3. **Public sources only, no invented URLs.** Only cite URLs you retrieved in this session or that appear in this file or the per-source guide you loaded.
4. **Cite sources.** Attribute claims to the doc URL used. If the answer isn't in the docs, say so and direct to official Adobe support — do not speculate.
5. **Verify relevance after fetching.** After fetching each per-source guide or documentation page (not this file), confirm it contains what you need before citing it. If sub-agent spawning is available, spawn one with: "Does this document contain the information needed to answer this question: [insert the user's actual question here]? If yes, respond 'yes' and quote the specific strings that answer it, clearly delimited. If no, respond 'no'. Do not spawn further sub-agents." If the sub-agent responds 'no', skip that source and continue to the next. If sub-agent spawning is unavailable, perform this relevance check inline before citing.

## Documentation routing

Use this table to pick the right source(s), then read the linked per-source guide before fetching docs.

| User or repo context | Documentation | Entry point | Per-source guide |
| --- | --- | --- | --- |
| EDS / AEM Sites — foundational delivery layer for all EDS sites: project setup, code sync (GitHub App), local dev (`aem up`, AEM CLI), block authoring pattern, Sidekick install and publish workflow, CDN/caching, spreadsheets (metadata, nav, redirects, placeholders, fragments), section metadata, generic CSS/JS patterns | **AEM / EDS (aem.live)** | [llms.txt](https://www.aem.live/llms.txt) | [aem-eds.md](./docs/aem-eds.md) |
| Commerce storefront — the commerce layer on top of EDS: drop-in components (cart, checkout, auth, product list, PDP), commerce-specific blocks, `scripts/__dropins__/`, `scripts/initializers/`, `build.mjs`, Storefront Configuration (endpoints, feature flags), drop-in containers/slots API, ACO/ACCS wiring from the front end | **Adobe Commerce Storefront** | [llms.txt](https://experienceleague.adobe.com/developer/commerce/storefront/llms.txt) | [storefront.md](./docs/storefront.md) |
| Product, merchant, and operations docs: Admin, catalog, orders, B2B, cloud (PaaS/SaaS), upgrades, Live Search/Catalog Service, ACO catalog views and price books, knowledge base | **Experience League (Commerce)** | [commerce.md](https://experienceleague.adobe.com/en/docs/commerce.md) | [experience-league.md](./docs/experience-league.md) |
| Document Authoring (DA) — the authoring tool and its setup: DA org/site creation, DA permissions and access control, authoring workflow inside da.live, DA-specific features (variables, reusable content, DA library) | **Document Authoring** | [docs.da.live](https://docs.da.live/) | [document-authoring.md](./docs/document-authoring.md) |
| Developer platform: extensibility, App Builder, web APIs, API Mesh, integration patterns | **Adobe Commerce Developer** | [developer.adobe.com/commerce](https://developer.adobe.com/commerce) | [commerce-developer.md](./docs/commerce-developer.md) |

Many questions span multiple sources. Identify every relevant source first, load each per-source guide, then fetch docs.

---

## Boilerplate reference repos

The storefront boilerplate repositories are the authoritative reference for actual code, scripts, blocks, DOM structure, CSS class names. Use them when the user has no local storefront repo, is on a vanilla boilerplate fork, or you need to verify a specific class name or DOM element before recommending changes.

| Repo | When to use |
| --- | --- |
| [hlxsites/aem-boilerplate-commerce](https://github.com/hlxsites/aem-boilerplate-commerce) | Standard EDS Commerce storefront — default drop-in installations, blocks, `scripts/commerce.js` |
| [adobe-rnd/aem-boilerplate-xcom](https://github.com/adobe-rnd/aem-boilerplate-xcom) | XCOM (AEM Sites) variant of the storefront boilerplate |

Fetch specific files via the raw GitHub URL, e.g.:

```
https://raw.githubusercontent.com/hlxsites/aem-boilerplate-commerce/main/blocks/commerce-cart/commerce-cart.js
```

**Always fetch the boilerplate** when a question is about storefront layout, DOM structure, CSS class names, block JS internals, or any code-level specific the docs alone won't fully resolve.

---

## Reading the user's code

When filesystem access is available, read relevant files before answering. The user's code reflects their actual current state and takes precedence over general documentation.

### Storefront repo (EDS site with Commerce integrations)

| File / path | Relevant for |
| --- | --- |
| `package.json` | Drop-in versions, scripts, build setup |
| `fstab.yaml` | Content source (DA org/site), folder mappings. Deprecated in favor of EDS Configuration Service|
| `head.html` | Import map — drop-in module aliases |
| `scripts/commerce.js` | GraphQL client setup, endpoint wiring |
| `scripts/initializers/` | Per-drop-in initialization (headers, auth, events) |
| `blocks/<name>/<name>.js` and `<name>.css` | Block implementation for the feature in question |
| `scripts/__dropins__/<name>/` | Installed drop-in source — read to understand available containers and APIs (read-only; do not modify) |
| `build.mjs` | GraphQL override configuration (`overrideGQLOperations`) |
| `config.json` (if present in repo) | Local Storefront Configuration (takes precedence over the served config from EDS Configuration Service) |

### App Builder app

| File / path | Relevant for |
| --- | --- |
| `app.config.yaml` | Action and event registration |
| `package.json` | Adobe I/O dependencies, scripts |
| `actions/` | Action implementations |

### Backend repo (PaaS Adobe Commerce / Magento)

| File / path | Relevant for |
| --- | --- |
| `composer.json` | Commerce version, installed extensions |
| `.magento/routes.yaml`, `.magento.app.yaml` | Cloud config (PaaS) |
| `app/etc/env.php` | Environment config (if accessible) |
| `app/code/<Vendor>/<Module>/` | Custom modules |

If filesystem access is not available, ask the user to share relevant files. For storefront layout/DOM questions specifically, prefer fetching from a boilerplate reference repo over asking.

---

## Disambiguation examples

| If the user asks about… | Start here |
| --- | --- |
| content scheduling | [AEM / EDS](./docs/aem-eds.md) — content scheduling is an AEM feature, not a storefront feature, though historically it was managed by PaaS |
| Code change pushed to repo but not showing on aem.live / hlx.live URL | [AEM / EDS](./docs/aem-eds.md) — this is an AEM Code Sync / CDN question, not a storefront question |
| Local dev setup: npm install, how to start the dev server, AEM CLI, `aem up` | [AEM / EDS](./docs/aem-eds.md) — AEM CLI applies to all EDS sites including storefront |
| Page edited in DA or repo not appearing on live site after publish | [AEM / EDS](./docs/aem-eds.md) — the publish/sync pipeline is EDS infrastructure; DA covers only DA-specific authoring steps |
| Navigation, header, or footer in an EDS or storefront site | [AEM / EDS](./docs/aem-eds.md) — nav/header/footer are document-driven EDS patterns; [Document Authoring](./docs/document-authoring.md) if the question is specifically about editing the nav document in DA |
| Add a non-commerce block or spreadsheet-driven content in a storefront repo | [AEM / EDS](./docs/aem-eds.md) — block authoring pattern is EDS, not storefront-specific |
| Placeholders, fragments, metadata sheets, section metadata, redirects | [AEM / EDS](./docs/aem-eds.md) — these are core EDS content patterns |
| Customize checkout drop-in or slot | [Storefront](./docs/storefront.md) |
| Configure Live Search in Admin or sync issues | [Experience League](./docs/experience-league.md) |
| "Not permitted" in da.live or DA site ACL | [Document Authoring](./docs/document-authoring.md) |
| Create a new DA org, DA site, or connect DA to an EDS repo | [Document Authoring](./docs/document-authoring.md) for DA org/site setup + [AEM / EDS](./docs/aem-eds.md) for fstab.yaml / EDS Configuration Service wiring |
| GraphQL mesh or App Builder webhook | [Commerce Developer docs](./docs/commerce-developer.md) |
| B2B company accounts in Admin | [Experience League](./docs/experience-league.md) |
| `scripts/__dropins__/` or `commerce.js` in repo | [Storefront](./docs/storefront.md) |
| $0 prices, 418 Configuration Error, drop-ins not loading | [Storefront](./docs/storefront.md) + check repo / boilerplate |
| ACO catalog views, price books, tenant IDs | [Experience League](./docs/experience-league.md) |
| Sidekick install or publish workflow | [AEM / EDS](./docs/aem-eds.md) |
| CORS errors on storefront requests to backend | [Storefront](./docs/storefront.md) for front-end symptoms + [Experience League](./docs/experience-league.md) for backend CORS config |
| Custom product attribute on PDP (e.g. `warranty_info`) | [Storefront](./docs/storefront.md) for `overrideGQLOperations` in `build.mjs` + [Experience League](./docs/experience-league.md) for enabling "Use in GraphQL" on the attribute in Admin |

When the repository itself indicates the stack (e.g. `blocks/commerce-*`, drop-in imports, `da.live` links in README), treat that as a strong signal for the matching row above.

---

## Terminology

Use the column on the left consistently; avoid the column on the right.

| Use | Not |
| --- | --- |
| Adobe Commerce | Magento (except when referring specifically to the legacy PaaS PHP codebase) |
| Adobe Commerce Optimizer (ACO) | just "ACO" on first mention |
| Adobe Commerce Cloud Service (ACCS) | just "ACCS" on first mention |
| Adobe Commerce on Cloud | "PaaS" or "Magento Commerce Cloud" |
| Storefront Configuration | "config.json" as the primary term (the file is the *artifact*, the configuration is the concept) |
| Document Authoring (DA) | just "DA" on first mention without expansion |
| Edge Delivery Services (EDS) | just "EDS" on first mention; not "Helix" or "Franklin" |
