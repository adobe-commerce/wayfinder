# Experience League (Commerce) — Agent Reference

> Load this file when the question involves product and operations documentation for Adobe Commerce: Admin user guides, merchant workflows, B2B (companies, shared catalogs, purchase orders), catalog and inventory in Admin, promotions, cloud offerings (Commerce on Cloud, Commerce as a Cloud Service, Commerce Optimizer), SaaS data export, Live Search / Product Recommendations / Catalog Service product docs, Payment Services, operations (install, upgrade, configuration CLI, release schedule), implementation playbook, Knowledge Base, or Commerce-learn tutorials.

## Entry points

- Human-readable: [Adobe Commerce Documentation](https://experienceleague.adobe.com/en/docs/commerce)
- Agent index: [commerce.md](https://experienceleague.adobe.com/en/docs/commerce.md)

## Navigate deeper

ExL Commerce has no `llms.txt`. Fetch the hub or `commerce.md` to discover sections, then fetch the relevant section page(s). The hub returns navigable content with direct links. The ExL search page is JavaScript-rendered and not useful for WebFetch — use a site-scoped search instead.

## Known starting points

Verify current URL via the hub if any fail:

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

## Site-scoped fallback search

```
site:experienceleague.adobe.com/en/docs/commerce <topic>
```

## Also check

- **[Adobe Commerce Storefront](./storefront.md)** for headless/EDS storefront implementation details.
- **[Adobe Commerce Developer docs](./commerce-developer.md)** for web APIs and extensibility (REST, GraphQL, App Builder, API Mesh).
- **[AEM / EDS](./aem-eds.md)** for non-commerce EDS behavior on a headless storefront project.
