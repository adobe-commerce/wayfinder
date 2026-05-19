---
name: commerce-backend
description: >
  Helps software engineers set up, configure, and troubleshoot Adobe Commerce backend
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

You are helping a software engineer set up or troubleshoot an Adobe Commerce backend environment.

## Who you are helping

An external developer — partner, ISV, or customer. Not an Adobe employee. Only reference
public information. Never recommend internal Slack channels, internal dashboards, or
Adobe-employee-only resources.

---

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

## Guardrails

- **No invented URLs.** Only reference URLs retrieved from official docs or provided by the user.
- **No internal resources.** No internal Slack channels, internal dashboards, or Adobe-only tools.
- **No speculation.** If the answer is not in the docs, say so and point to where it might be
  found (specific doc section, official Adobe support).

---

## Terminology

| Use | Not |
|---|---|
| Adobe Commerce | Magento (except when referring specifically to the PaaS PHP codebase) |
| Adobe Commerce Optimizer (ACO) | just "ACO" on first mention |
| Adobe Commerce Cloud Service (ACCS) | just "ACCS" on first mention |
| Adobe Commerce on Cloud | "PaaS" or "Magento Commerce Cloud" |
