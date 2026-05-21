# AGENTS.md

Guidance for AI agents working in Adobe Commerce repositories. Use this file to choose the right **official documentation** for the user's question or task, then follow links and indexes inside that doc set — do not rely on training data alone for product-specific behavior, URLs, or configuration.

## Operating principles

1. **Specifics come from the docs or the code, not from training data.** You do not know specific container names, slot names, CSS class names, GraphQL field names, API endpoints, header names, configuration keys, admin paths, module names, feature flags, CLI commands, block names, table column names, metadata keys, or DA URL patterns. If your answer names any of these, you must have fetched it from the official docs, read it from the user's repo, or fetched it from a boilerplate reference repo in this session. Plausible-sounding guesses are wrong — fetch first, name names second.
2. **Read the user's code when available.** The user's repo reflects their actual current state and takes precedence over general documentation when the two conflict. If the user has no local repo, fall back to the [boilerplate reference repos](#boilerplate-reference-repos) for code-level specifics.
3. **Public sources only.** Only reference public documentation, public repos, and official Adobe channels. Do not recommend internal Slack channels, internal dashboards, or Adobe-employee-only resources.
4. **No invented URLs.** Only cite URLs you retrieved in this session or that appear in this file. Do not construct documentation URLs by pattern.
5. **Cite sources.** When you use one of the doc sources listed below, attribute the relevant claim to its source URL.

## Workflow

For every question:

1. **Infer intent** from the latest user message, open files, repo layout, and conversation history (not only keywords).
2. **Check the code** — read the user's repo if filesystem access is available; otherwise fall back to a [boilerplate reference repo](#boilerplate-reference-repos) for layout/DOM/code questions. Code is the source of truth for what specific elements, classes, containers, and config keys actually exist.
3. **Pick the primary doc set(s)** using the [quick reference](#quick-reference) below. When topics span sets, start with the set that matches the *immediate* task (e.g. fixing a drop-in → Storefront; fixing Admin config → Experience League). Many questions span multiple sets — list every relevant set before fetching.
4. **Open the entry point** (site home or `llms.txt` / `.md` index). Prefer machine-readable indexes when you can fetch URLs.
5. **Navigate deeper and fetch** every relevant section or bundle. Do not stop at one fetch if the question spans multiple topics.
6. **If the docs don't fully answer**, use web search with a `site:` operator scoped to the relevant source (examples in each source section), then fetch the pages returned.
7. **Cross-reference only when needed.** Each source below notes common hand-offs to other sets.
8. **Respond with attribution.** Cite the doc URL(s) you used. If the answer is genuinely not in the docs, say so and direct to official Adobe support — do not speculate.

## Documentation routing

### Quick reference

| User or repo context | Primary documentation | Entry point |
| --- | --- | --- |
| Commerce storefront on Edge Delivery Services (EDS): drop-ins, commerce blocks, boilerplate, storefront GraphQL, cart/checkout, storefront config | **Adobe Commerce Storefront** | [Storefront docs](https://experienceleague.adobe.com/developer/commerce/storefront/) · [llms.txt index](https://experienceleague.adobe.com/developer/commerce/storefront/llms.txt) |
| Product, merchant, and operations docs: Admin, catalog, orders, B2B, cloud (PaaS/SaaS), upgrades, Live Search/Catalog Service *as product guides*, knowledge base | **Experience League (Commerce)** | [Commerce docs home](https://experienceleague.adobe.com/en/docs/commerce) · [commerce.md index](https://experienceleague.adobe.com/en/docs/commerce.md) |
| Document Authoring (DA), da.live, DA org/sites, DA permissions, authoring workflow separate from classic AEM authoring | **Document Authoring** | [docs.da.live](https://docs.da.live/) |
| Edge Delivery Services / AEM Sites in general: project anatomy, blocks, spreadsheets, CDN, Sidekick, publish/launch — not Commerce-specific | **AEM / EDS (aem.live)** | [Documentation](https://www.aem.live/docs/) · [llms.txt index](https://www.aem.live/llms.txt) |
| Developer platform: extensibility, App Builder, Commerce web APIs, API Mesh, integration patterns, developer playground | **Adobe Commerce Developer** | [developer.adobe.com/commerce](https://developer.adobe.com/commerce) |

---

### 1. Adobe Commerce Storefront

**Use when** the work involves the **Commerce storefront** stack: Edge Delivery Services project for commerce, **drop-in components**, **commerce blocks**, storefront **boilerplate**, `fstab.yaml` / Code Sync for storefront repos, **Storefront Configuration**, storefront **GraphQL** customization, cart/checkout/account/order flows, storefront troubleshooting (CORS, drop-ins not loading, $0 prices), or **Storefront SDK** usage in the storefront repo.

**Do not use as the only source** for generic EDS block mechanics with no commerce angle (see [AEM / EDS](#4-aem--edge-delivery-services-eds)) or for backend Admin/PHP extension work (see [Experience League](#2-experience-league-commerce) and [Developer docs](#5-adobe-commerce-developer-documentation)).

**Entry points**

- Human-readable: [Adobe Commerce Storefront](https://experienceleague.adobe.com/developer/commerce/storefront/)
- Agent index: [llms.txt](https://experienceleague.adobe.com/developer/commerce/storefront/llms.txt)
  - Full bundle (large): [llms-full.txt](https://experienceleague.adobe.com/developer/commerce/storefront/llms-full.txt)
  - Abridged bundle (large): [llms-small.txt](https://experienceleague.adobe.com/developer/commerce/storefront/llms-small.txt)

**Navigate deeper**

Fetch the `llms.txt` index to discover available topic bundles and their descriptions, then fetch every bundle relevant to the question. Do not guess bundle URLs — the index is the source of truth for the current chunking.

**Site-scoped fallback search** when the indexed bundles don't fully answer:

```
site:experienceleague.adobe.com/developer/commerce/storefront <topic>
```

**Often also relevant:** [Experience League](#2-experience-league-commerce) for backend/catalog data behind the storefront; [Developer docs](#5-adobe-commerce-developer-documentation) for shared APIs and events; [DA](#3-document-authoring-da) when authors work in da.live on the same site.

---

### 2. Experience League (Commerce)

**Use when** the work is **product and operations documentation** for Adobe Commerce: **Admin** user guides, merchant workflows, **B2B** (companies, shared catalogs, purchase orders), **catalog and inventory** in Admin, **promotions**, cloud offerings (**Commerce on Cloud**, **Commerce as a Cloud Service**, **Commerce Optimizer**), **SaaS data export**, **Live Search** / **Product Recommendations** / **Catalog Service** product docs, **Payment Services**, **operations** (install, upgrade, configuration CLI, release schedule), **implementation playbook**, **Knowledge Base**, and **Commerce-learn** tutorials listed under Experience League.

**Do not use as the only source** for storefront drop-in/block implementation (see [Storefront](#1-adobe-commerce-storefront)) or for API-first extensibility landing pages on developer.adobe.com (see [Developer docs](#5-adobe-commerce-developer-documentation) — though Experience League may link there).

**Entry points**

- Human-readable: [Adobe Commerce Documentation](https://experienceleague.adobe.com/en/docs/commerce)
- Agent index: [commerce.md](https://experienceleague.adobe.com/en/docs/commerce.md)

**Navigate deeper**

ExL Commerce has no `llms.txt`. Fetch the hub or `commerce.md` to discover sections, then fetch the relevant section page(s). The hub returns navigable content with direct links. The ExL search page is JavaScript-rendered and not useful for WebFetch — use a site-scoped search instead.

Known starting points (verify current URL via the hub if any fail):

| Topic | URL |
| --- | --- |
| Adobe Commerce Cloud Service (ACCS) | `https://experienceleague.adobe.com/en/docs/commerce/cloud-service/overview` |
| Adobe Commerce Optimizer (ACO) | `https://experienceleague.adobe.com/en/docs/commerce/optimizer/overview` |
| Adobe Commerce on Cloud / PaaS infrastructure | `https://experienceleague.adobe.com/en/docs/commerce-on-cloud/user-guide/overview` |
| B2B features and configuration | `https://experienceleague.adobe.com/en/docs/commerce-admin/b2b/introduction` |
| Catalog administration | `https://experienceleague.adobe.com/en/docs/commerce-admin/catalog/guide-overview` |
| SaaS data export | `https://experienceleague.adobe.com/en/docs/commerce/saas-data-export/overview` |
| Catalog Service | `https://experienceleague.adobe.com/en/docs/commerce/catalog-service/guide-overview` |
| Live Search | `https://experienceleague.adobe.com/en/docs/commerce/live-search/overview` |
| Product Recommendations (backend/data side) | `https://experienceleague.adobe.com/en/docs/commerce/product-recommendations/guide-overview` |
| ACO Optimizer Connector | `https://experienceleague.adobe.com/en/docs/commerce/aco-optimizer-connector/overview` |
| Admin start guide | `https://experienceleague.adobe.com/en/docs/commerce-admin/start/guide-overview` |
| Stores and sales configuration | `https://experienceleague.adobe.com/en/docs/commerce-admin/stores-sales/guide-overview` |
| System configuration | `https://experienceleague.adobe.com/en/docs/commerce-admin/systems/guide-overview` |
| Troubleshooting knowledge base | `https://experienceleague.adobe.com/en/docs/commerce-knowledge-base/kb/troubleshooting/overview` |

**Site-scoped fallback search:**

```
site:experienceleague.adobe.com/en/docs/commerce <topic>
```

**Often also relevant:** [Storefront](#1-adobe-commerce-storefront) for headless/storefront implementation; [Developer docs](#5-adobe-commerce-developer-documentation) for web APIs and extensibility; [AEM / EDS](#4-aem--edge-delivery-services-eds) for non-commerce EDS behavior.

---

### 3. Document Authoring (DA)

**Use when** the work involves **Document Authoring** or **da.live**: creating or editing content in DA, **DA organization and site setup**, **permissions** ("Not permitted", ACL sheet, user groups), **blocks and pages in DA**, DA **administration**, preview/publish workflow with DA, or author-facing guides that explicitly reference Document Authoring rather than Universal Editor-only AEM authoring.

**Do not use as the only source** for Commerce storefront **code** (blocks JS/CSS, drop-ins) — use [Storefront](#1-adobe-commerce-storefront). For general AEM authoring concepts shared across EDS, cross-check [AEM / EDS](#4-aem--edge-delivery-services-eds).

**Entry points**

- [Document Authoring documentation](https://docs.da.live/)

**Navigate deeper**

No `llms.txt`. Fetch `https://docs.da.live/` as the discovery hub to find the relevant DA-specific pages, then fetch those pages. Use for: DA authoring interface, DA org/site setup, DA permissions/ACL. Many DA questions also need [AEM / EDS](#4-aem--edge-delivery-services-eds) content (blocks, publish workflow, Admin API) — fetch from both when the question bridges them.

**Site-scoped fallback search:**

```
site:docs.da.live <topic>
site:www.aem.live <topic>
```

**Often also relevant:** [AEM / EDS](#4-aem--edge-delivery-services-eds) for Sidekick, publishing, and EDS mechanics; [Storefront](#1-adobe-commerce-storefront) for commerce-specific authoring and blocks.

---

### 4. AEM / Edge Delivery Services (EDS)

**Use when** the work is **general Edge Delivery Services** or **AEM Sites** documentation: developer tutorial, **anatomy of a project**, **block collection**, **spreadsheets**, **indexing**, performance ("keeping it 100"), **sections/markup**, **placeholders**, **bulk metadata**, **sitemap**, **redirects**, **CDN** setup (Fastly, Cloudflare, Akamai, etc.), **go-live checklist**, **push invalidation**, **Sidekick** (install, security, library), **Admin API** for AEM, **aem CLI**, staging/environments, security overview — not specific to the Commerce storefront product line.

**Do not use as the only source** for Commerce drop-ins, commerce blocks, or storefront boilerplate (see [Storefront](#1-adobe-commerce-storefront)).

**Entry points**

- Human-readable: [AEM Documentation](https://www.aem.live/docs/)
- Agent index: [llms.txt](https://www.aem.live/llms.txt)

**Navigate deeper**

Fetch the `llms.txt` index to discover available `.md` paths and bundles, then fetch every section relevant to the question.

Known starting points (verify current URL via the index if any fail):

| Topic | URL |
| --- | --- |
| EDS project structure, Code Sync, CDN | `https://www.aem.live/developer/anatomy-of-a-project.md` |
| Block markup, sections, and block patterns | `https://www.aem.live/developer/markup-sections-blocks.md` |
| Admin API (Storefront Configuration, content source, sync) | `https://www.aem.live/docs/admin.html` |
| Custom headers | `https://www.aem.live/docs/custom-headers.md` |
| Sidekick (preview/publish browser extension) | `https://www.aem.live/docs/sidekick.md` |
| Go-live checklist, CDN setup | `https://www.aem.live/docs/go-live-checklist.md` |
| AI coding agents guide | `https://www.aem.live/developer/ai-coding-agents.md` |

**Site-scoped fallback search:**

```
site:www.aem.live <topic>
```

**Often also relevant:** [Storefront](#1-adobe-commerce-storefront) for commerce projects; [DA](#3-document-authoring-da) for da.live authoring.

---

### 5. Adobe Commerce Developer documentation

**Use when** the work is **developer.adobe.com** scope: **API-first development**, **App Builder**, **event-driven integrations** and webhooks, **Commerce web APIs** (REST/GraphQL), **API Mesh**, **Admin UI SDK**, **extensibility** overview, **integration starter kit**, **Merchandising Services APIs**, **product recommendations** APIs, **storefront events** SDK, code samples, and the **developer playground**.

**Do not use as the only source** for step-by-step storefront drop-in tutorials and block references (see [Storefront](#1-adobe-commerce-storefront)) or for long-form Admin user guide prose (see [Experience League](#2-experience-league-commerce)).

**Entry points**

- [Adobe Commerce for developers](https://developer.adobe.com/commerce)

**Navigate deeper**

Follow the site IA: Extensibility, Web API, Services, and linked reference pages. When Experience League or Storefront pages link here for APIs, prefer the developer site for request/response details and samples.

**Site-scoped fallback search:**

```
site:developer.adobe.com/commerce <topic>
```

**Often also relevant:** [Storefront](#1-adobe-commerce-storefront) for drop-in SDK and storefront integration; [Experience League](#2-experience-league-commerce) for operational context and Admin configuration that backs APIs.

---

## Boilerplate reference repos

The storefront boilerplate implementations are the authoritative reference for actual code, DOM structure, CSS class names, default block layouts, and default `scripts/` wiring. Use them when:

- The user has no local storefront repo to read.
- The user is on a vanilla boilerplate fork that hasn't been customized.
- You need to verify a specific class name, container, or DOM element before recommending changes to it.

| Repo | When to use |
| --- | --- |
| [hlxsites/aem-boilerplate-commerce](https://github.com/hlxsites/aem-boilerplate-commerce) | Standard EDS Commerce storefront — default drop-in installations, blocks, `scripts/commerce.js` |
| [adobe-rnd/aem-boilerplate-xcom](https://github.com/adobe-rnd/aem-boilerplate-xcom) | XCOM (AEM Sites) variant of the storefront boilerplate |

Fetch specific files via the raw GitHub URL, e.g.:

```
https://raw.githubusercontent.com/hlxsites/aem-boilerplate-commerce/main/blocks/commerce-cart/commerce-cart.js
```

**Always fetch the boilerplate** when a question is about layout, DOM structure, CSS class names, block JS internals, or any code-level specific the docs alone won't fully resolve. The boilerplate is the source of truth for "what containers / classes / elements / files exist by default."

---

## Reading the user's code

When filesystem access is available, read relevant files before answering. The user's code reflects their actual current state and takes precedence over general documentation. There may be more than one repo:

### Storefront repo (EDS site with Commerce integrations)

May be built on a starter kit such as `hlxsites/aem-boilerplate-commerce` or `adobe-rnd/aem-boilerplate-xcom`, or built custom. Read the actual repo before assuming any structure.

| File / path | Relevant for |
| --- | --- |
| `package.json` | Drop-in versions, scripts, build setup |
| `fstab.yaml` | Content source (DA org/site), folder mappings |
| `head.html` | Import map — drop-in module aliases |
| `scripts/commerce.js` | GraphQL client setup, endpoint wiring |
| `scripts/initializers/` | Per-drop-in initialization (headers, auth, events) |
| `blocks/<name>/<name>.js` and `<name>.css` | Block implementation for the feature in question |
| `scripts/__dropins__/<name>/` | Installed drop-in source — read to understand available containers and APIs (read-only; do not modify) |
| `build.mjs` | GraphQL override configuration (`overrideGQLOperations`) |
| `config.json` (if present in repo) | Local Storefront Configuration (takes precedence over the served config) |

### App Builder app

Adobe I/O Runtime applications such as `aem-commerce-prerender`.

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

If filesystem access is not available, ask the user to share the relevant files or paste the relevant code. For storefront layout/DOM questions specifically, prefer fetching from a [boilerplate reference repo](#boilerplate-reference-repos) over asking.

---

## Disambiguation examples

| If the user asks about… | Start here |
| --- | --- |
| Customize checkout drop-in or slot | [Storefront](#1-adobe-commerce-storefront) |
| Configure Live Search in Admin or sync issues | [Experience League](#2-experience-league-commerce) |
| "Not permitted" in da.live or DA site ACL | [DA](#3-document-authoring-da) |
| Add a generic EDS block or spreadsheet-driven content | [AEM / EDS](#4-aem--edge-delivery-services-eds) |
| GraphQL mesh or App Builder webhook | [Developer docs](#5-adobe-commerce-developer-documentation) |
| B2B company accounts in Admin | [Experience League](#2-experience-league-commerce) |
| `scripts/__dropins__/` or `commerce.js` in repo | [Storefront](#1-adobe-commerce-storefront) |
| $0 prices, 418 Configuration Error, drop-ins not loading | [Storefront](#1-adobe-commerce-storefront) + check repo / boilerplate |
| ACO catalog views, price books, tenant IDs | [Experience League](#2-experience-league-commerce) |
| Sidekick or publish workflow on an EDS site | [AEM / EDS](#4-aem--edge-delivery-services-eds), [DA](#3-document-authoring-da) if authoring in da.live |

When the repository itself indicates the stack (e.g. `blocks/commerce-*`, drop-in imports, `da.live` links in README), treat that as a strong signal for the matching row in the [quick reference](#quick-reference) table.

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
