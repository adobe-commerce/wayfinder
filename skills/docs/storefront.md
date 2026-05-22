# Adobe Commerce Storefront — Agent Reference

> Load this file when the question involves the Commerce storefront stack on Edge Delivery Services: drop-in components, commerce blocks, storefront boilerplate, `fstab.yaml` / Code Sync for storefront repos, Storefront Configuration, storefront GraphQL customization, cart/checkout/account/order flows, storefront troubleshooting (CORS, drop-ins not loading, $0 prices), or Storefront SDK usage in the storefront repo.

## Entry points

- Human-readable: [Adobe Commerce Storefront](https://experienceleague.adobe.com/developer/commerce/storefront/)
- Agent index: [llms.txt](https://experienceleague.adobe.com/developer/commerce/storefront/llms.txt)
  - Full bundle (large): [llms-full.txt](https://experienceleague.adobe.com/developer/commerce/storefront/llms-full.txt)
  - Abridged bundle (large): [llms-small.txt](https://experienceleague.adobe.com/developer/commerce/storefront/llms-small.txt)

## Navigate deeper

Fetch the `llms.txt` index to discover available topic bundles and their descriptions, then fetch every bundle relevant to the question — do not stop after one bundle if the question spans multiple topics. Do not guess bundle URLs — the index is the source of truth for the current chunking.

Common bundle topics include: initial setup and boilerplate configuration, drop-in installation, drop-in customization (containers/slots/event bus), GraphQL customization (`overrideGQLOperations` in `build.mjs`), Storefront Configuration reference, and troubleshooting ($0 prices, 418 errors, CORS, drop-ins not loading).

## Site-scoped fallback search

```
site:experienceleague.adobe.com/developer/commerce/storefront <topic>
```

## Also check

- **[Experience League](./experience-league.md)** for backend/catalog data behind the storefront (Admin config, SaaS data export, ACO catalog views, B2B module setup).
- **[Adobe Commerce Developer docs](./commerce-developer.md)** for shared APIs (storefront events SDK, App Builder integrations, API Mesh).
- **[Document Authoring](./document-authoring.md)** when authors work in da.live on the same site (block authoring, content publishing).
- **[AEM / EDS](./aem-eds.md)** for generic EDS block mechanics, CDN, Sidekick, or go-live topics with no Commerce-specific angle.
