---
name: commerce-storefront
description: >
  Helps software engineers build, configure, and troubleshoot Adobe Commerce EDS storefronts.
  Use for questions about: EDS storefront setup (boilerplate, Code Sync, fstab.yaml, npm
  install, local dev); Storefront Configuration (AEM Admin API, config keys, headers, CORS);
  Commerce drop-ins (storefront-pdp, storefront-cart, storefront-checkout, storefront-auth,
  storefront-account, storefront-order, storefront-recommendations — installation,
  customization, containers, slots, event bus, initializers); EDS blocks (JS/CSS,
  readBlockConfig); GraphQL customization (overrideGQLOperations, CS_FETCH_GRAPHQL,
  CORE_FETCH_GRAPHQL); product recommendations; aem-commerce-prerender; troubleshooting
  ($0.00 prices, 418 errors, no search results, drop-ins not loading, CDN sync, CORS errors);
  storefront architecture (two-endpoint pattern, import maps, scripts/__dropins__/, commerce.js).
---

# Commerce Storefront Skill

## Source authority

Two sources cover this skill. When they conflict, the domain owner wins:

| Domain | Authoritative source | Entry point |
|---|---|---|
| EDS platform — Code Sync, Admin API, CDN, fstab, block patterns | **aem.live** | `https://www.aem.live/llms.txt` |
| Storefront — drop-ins, boilerplate, Storefront Configuration, recommendations, prerender | **ExL Storefront** | `https://experienceleague.adobe.com/developer/commerce/storefront/llms.txt` |

---

## Fetch strategy

Fetch documentation before answering — do not rely on static knowledge for specifics.
Use the section most relevant to the question:

**ExL Storefront sections**

| Topic | URL |
|---|---|
| Architecture, getting started, onboarding | `https://experienceleague.adobe.com/developer/commerce/storefront/_llms-txt/get-started.txt` |
| Boilerplate structure, fstab.yaml, head.html, import maps | `https://experienceleague.adobe.com/developer/commerce/storefront/_llms-txt/boilerplate.txt` |
| Storefront Configuration keys, CORS, environment setup | `https://experienceleague.adobe.com/developer/commerce/storefront/_llms-txt/setup-reference.txt` |
| Drop-in APIs, containers, slots, event bus, initializers | `https://experienceleague.adobe.com/developer/commerce/storefront/_llms-txt/dropins-reference.txt` |
| Block structure and patterns | `https://experienceleague.adobe.com/developer/commerce/storefront/_llms-txt/blocks-reference.txt` |
| Task-focused how-tos | `https://experienceleague.adobe.com/developer/commerce/storefront/_llms-txt/how-tos.txt` |
| Step-by-step tutorials (cart, checkout, PDP, etc.) | `https://experienceleague.adobe.com/developer/commerce/storefront/_llms-txt/tutorials-reference.txt` |
| SDK components and integration patterns | `https://experienceleague.adobe.com/developer/commerce/storefront/_llms-txt/sdk-reference.txt` |
| Troubleshooting known issues | `https://experienceleague.adobe.com/developer/commerce/storefront/_llms-txt/troubleshooting.txt` |
| Release notes | `https://experienceleague.adobe.com/developer/commerce/storefront/_llms-txt/releases.txt` |

**aem.live sections** (for EDS platform topics)

| Topic | URL |
|---|---|
| EDS project structure, Code Sync, CDN | `https://www.aem.live/developer/anatomy-of-a-project.md` |
| Block markup, sections, and block patterns | `https://www.aem.live/developer/markup-sections-blocks.md` |
| Admin API (Storefront Configuration, content source, sync) | `https://www.aem.live/docs/admin.html` |
| Custom headers | `https://www.aem.live/docs/custom-headers.md` |
| Sidekick (preview/publish browser extension) | `https://www.aem.live/docs/sidekick.md` |
| Go-live checklist, CDN setup | `https://www.aem.live/docs/go-live-checklist.md` |
| AI coding agents guide | `https://www.aem.live/developer/ai-coding-agents.md` |

For the full index of available sections, start at:
`https://experienceleague.adobe.com/developer/commerce/storefront/llms.txt`

---

## Reading the user's repo

When filesystem access is available, read relevant files before answering. The storefront repo
may be a starter kit fork or a custom EDS project — read it before assuming any structure.

Key files to check depending on the question:

| File / path | Relevant for |
|---|---|
| `package.json` | Drop-in versions, scripts, build setup |
| `fstab.yaml` | Content source (DA org/site), folder mappings |
| `head.html` | Import map — drop-in module aliases |
| `scripts/commerce.js` | GraphQL client setup, endpoint wiring |
| `scripts/initializers/` | Per-drop-in initialization (headers, auth, events) |
| `blocks/<name>/<name>.js` | Block implementation for the feature in question |
| `scripts/__dropins__/<name>/` | Installed drop-in source — read to understand available containers and APIs |
| `build.mjs` | GraphQL override configuration (`overrideGQLOperations`) |

If filesystem access is not available, ask the user to share the relevant files or paste
the relevant code.

---

## Workflow

1. **Check the repo** (if available) — read the files most relevant to the question before fetching docs.
2. **Pick the right section** — use the fetch strategy table above.
3. **Fetch** — retrieve that section before answering. Do not rely on static knowledge for specifics.
4. **If the first fetch doesn't answer** — try `troubleshooting.txt`, or fetch the full index at the ExL Storefront `llms.txt` for a more specific section.
5. **Synthesize** — combine repo findings and fetched docs. Cite the doc URL.

Common starting points by scenario:

| Scenario | Start here |
|---|---|
| $0.00 prices / CORS errors | `setup-reference.txt` + `troubleshooting.txt` |
| 418 Configuration Error | `troubleshooting.txt` |
| Drop-in customization (containers, slots, events) | Read `scripts/__dropins__/<name>/`, then `dropins-reference.txt` |
| CDN not syncing / Code Sync issues | `anatomy-of-a-project.md` (aem.live) |
| New storefront setup | `get-started.txt`, then `boilerplate.txt` |
| GraphQL field customization | `build.mjs` in the repo, then `how-tos.txt` |
| Product recommendations | `dropins-reference.txt` + `sdk-reference.txt` |

---

## Terminology

| Use | Not |
|---|---|
| Adobe Commerce | Magento |
| Storefront Configuration | config.json (as primary term) |
| Document Authoring (DA) | just "DA" on first mention without expanding |
| Adobe Commerce Optimizer (ACO) | just "ACO" on first mention |
| Adobe Commerce Cloud Service (ACCS) | just "ACCS" on first mention |
