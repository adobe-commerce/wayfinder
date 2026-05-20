---
name: commerce-backend
description: >
  Helps software engineers or admins set up, configure, and troubleshoot Adobe Commerce backend
  environments. Use this skill for any question about: Adobe Commerce Cloud Service (ACCS)
  setup and configuration; Adobe Commerce Optimizer (ACO) setup, catalog views, price books,
  and data export; Adobe Commerce on Cloud (PaaS) infrastructure and deployment; B2B features
  and configuration (company accounts, shared catalogs, purchase orders, negotiable quotes);
  SaaS data export and catalog sync (Live Search, Product Recommendations, Catalog Service);
  Commerce GraphQL API; CORS configuration on Adobe Commerce; Admin UI access (stores, catalog,
  customers, marketing, system configuration); understanding tenant IDs, instance URLs, and how
  backend environments relate to the EDS storefront; or troubleshooting backend issues (data
  not syncing, catalog not appearing, B2B features not working, API errors).
---

# Commerce Backend Skill

## Source authority

| Authoritative source | Entry point |
|---|---|
| **ExL Commerce** | `https://experienceleague.adobe.com/en/docs/commerce` |

ExL Commerce has no `llms.txt`. Fetch the hub page to discover sections, then fetch the
relevant section page(s). The hub page returns navigable content with direct links.
The ExL search page is JavaScript-rendered and not useful for WebFetch.

---

## Fetch strategy

Fetch the most relevant section for the question. Start with the hub if you need to discover
the right section:

**Hub (discovery)**

| Purpose | URL |
|---|---|
| Full section index | `https://experienceleague.adobe.com/en/docs/commerce` |

**Specific sections — fetch directly when the topic is clear**

| Topic | URL |
|---|---|
| Adobe Commerce Cloud Service (ACCS) | `https://experienceleague.adobe.com/en/docs/commerce/cloud-service/overview` |
| Adobe Commerce Optimizer (ACO) | `https://experienceleague.adobe.com/en/docs/commerce/optimizer/overview` |
| Adobe Commerce on Cloud / PaaS infrastructure | `https://experienceleague.adobe.com/en/docs/commerce-on-cloud/user-guide/overview` |
| B2B features and configuration | `https://experienceleague.adobe.com/en/docs/commerce-admin/b2b/introduction` |
| Catalog administration | `https://experienceleague.adobe.com/en/docs/commerce-admin/catalog/guide-overview` |
| SaaS data export (catalog sync to ACO, Live Search, Recs) | `https://experienceleague.adobe.com/en/docs/commerce/saas-data-export/overview` |
| Catalog Service | `https://experienceleague.adobe.com/en/docs/commerce/catalog-service/guide-overview` |
| Live Search | `https://experienceleague.adobe.com/en/docs/commerce/live-search/overview` |
| Product Recommendations (backend/data side) | `https://experienceleague.adobe.com/en/docs/commerce/product-recommendations/guide-overview` |
| ACO Optimizer Connector | `https://experienceleague.adobe.com/en/docs/commerce/aco-optimizer-connector/overview` |
| Admin start guide (general admin UI) | `https://experienceleague.adobe.com/en/docs/commerce-admin/start/guide-overview` |
| Stores and sales configuration | `https://experienceleague.adobe.com/en/docs/commerce-admin/stores-sales/guide-overview` |
| System configuration | `https://experienceleague.adobe.com/en/docs/commerce-admin/systems/guide-overview` |
| Troubleshooting knowledge base | `https://experienceleague.adobe.com/en/docs/commerce-knowledge-base/kb/troubleshooting/overview` |
| Commerce GraphQL / Web API | `https://developer.adobe.com/commerce/webapi/` |
| App Builder / extensibility | `https://developer.adobe.com/commerce/extensibility/` |

---

## Reading the user's repo

When filesystem access is available, check for a backend repo — a PaaS Adobe Commerce (Magento)
PHP codebase. Read it before making assumptions.

Key things to check:
- `composer.json` — Commerce version, installed extensions
- `.magento/routes.yaml`, `.magento.app.yaml` — cloud config (PaaS)
- `app/etc/env.php` — environment config (if accessible)
- Any custom modules in `app/code/`

If filesystem access is not available, ask the user to share relevant config or describe
their environment (e.g., ACCS vs ACO vs PaaS, instance URL, tenant ID).

---

## Workflow

1. **Identify the topic** — use the fetch strategy table to pick the right section. If uncertain, fetch the hub first.
2. **Check the repo** (if available) — read `composer.json` and relevant config before assuming the user's environment.
3. **Fetch** — retrieve the relevant section. ExL Commerce has no `llms.txt`; use the direct section URLs above or start from the hub.
4. **If the first fetch doesn't answer** — try the troubleshooting knowledge base, or fetch a related section (e.g., if ACO overview doesn't cover a catalog question, try `saas-data-export` or `catalog-service`).
5. **Synthesize** — cite the doc URL. If the answer is not in the docs, say so and direct to Adobe support.

Common starting points by scenario:

| Scenario | Start here |
|---|---|
| Products not appearing in storefront or search | `saas-data-export/overview` |
| ACO provisioning, catalog views, price books | `optimizer/overview` |
| Live Search setup or configuration | `live-search/overview` |
| B2B features (companies, shared catalogs, purchase orders) | `b2b/introduction` |
| CORS on Adobe Commerce | `cloud-service/overview` (ACCS) or `commerce-on-cloud/user-guide/overview` (PaaS) |
| Tenant IDs, instance URLs, endpoint format | `optimizer/overview` |
| Data sync between Commerce and ACO / Live Search | `saas-data-export/overview` + `aco-optimizer-connector/overview` |

---

## Terminology

| Use | Not |
|---|---|
| Adobe Commerce | Magento (except when referring specifically to the PaaS PHP codebase) |
| Adobe Commerce Optimizer (ACO) | just "ACO" on first mention |
| Adobe Commerce Cloud Service (ACCS) | just "ACCS" on first mention |
| Adobe Commerce on Cloud | "PaaS" or "Magento Commerce Cloud" |
