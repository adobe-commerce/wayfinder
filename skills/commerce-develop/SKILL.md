---
name: commerce-develop
description: >
  Guides software engineers developing features for an Adobe Commerce EDS storefront
  (hlxsites/aem-boilerplate-commerce). Use this skill whenever someone is creating or
  customizing EDS blocks for a Commerce site; extending or overriding a Commerce drop-in
  (storefront-pdp, storefront-cart, storefront-checkout, storefront-account, storefront-order,
  storefront-recommendations, storefront-auth); customizing dropin containers or using the
  DOM fragment pattern; overriding GraphQL operations with overrideGQLOperations; implementing
  aem-commerce-prerender; adding or customizing product recommendation units; working with
  the dropin initializer pattern; or understanding how the EDS block/dropin architecture
  works. Also trigger for questions about import maps, scripts/__dropins__/, the event bus,
  commerce.js, or initializers.
---

# Adobe Commerce EDS Storefront Development Skill

You are helping a software engineer develop features on an EDS storefront built on
`hlxsites/aem-boilerplate-commerce`.

## Terminology

| Use This | Not This |
|---|---|
| **Adobe Commerce** | ~~Magento~~ |
| **Storefront Configuration** | ~~config.json~~ |

> **Always look at the user's codebase first.** Read the relevant block files, initializers,
> and drop-in source in `scripts/__dropins__/` before making recommendations. The boilerplate
> evolves; what you read in the code is more authoritative than static memory or docs.

---

## Source Authority

When sources conflict, the domain owner is authoritative:

| Domain | Authoritative Source | URL |
|---|---|---|
| EDS platform — Code Sync, Admin API, CDN, publishing | **aem.live** | `https://www.aem.live/llms.txt` |
| Storefront drop-ins, blocks, boilerplate, SDK, recommendations | **Storefront ExL** | `https://experienceleague.adobe.com/developer/commerce/storefront/llms.txt` |
| Commerce backend, GraphQL schema, attributes | **Commerce ExL** | `https://experienceleague.adobe.com/en/docs/commerce` |

---

## Fetch Strategy

Fetch current documentation before advising on APIs or specific patterns — the boilerplate
evolves and docs are the authoritative source.

| Topic | Fetch This URL |
|---|---|
| Drop-in APIs, containers, slots | `https://experienceleague.adobe.com/developer/commerce/storefront/_llms-txt/dropins-reference.txt` |
| Block structure, slot configurations | `https://experienceleague.adobe.com/developer/commerce/storefront/_llms-txt/blocks-reference.txt` |
| Task-focused how-tos | `https://experienceleague.adobe.com/developer/commerce/storefront/_llms-txt/how-tos.txt` |
| Step-by-step tutorials (cart, checkout, PDP) | `https://experienceleague.adobe.com/developer/commerce/storefront/_llms-txt/tutorials-reference.txt` |
| SDK components and integration patterns | `https://experienceleague.adobe.com/developer/commerce/storefront/_llms-txt/sdk-reference.txt` |
| Architecture, onboarding | `https://experienceleague.adobe.com/developer/commerce/storefront/_llms-txt/get-started.txt` |
| EDS platform specifics (Code Sync, CDN) | `https://www.aem.live/llms.txt` then fetch linked section pages |

> The `search-commerce-docs` MCP tool can also search storefront docs but requires `aio auth login`.

---

## Architecture Mental Model

```
EDS Page Load
  └── scripts/scripts.js  (page lifecycle: eager → lazy → delayed)
       └── initializeCommerce()  (in scripts/commerce.js)
            └── Sets up CORE_FETCH_GRAPHQL + CS_FETCH_GRAPHQL from Storefront Configuration
            └── Loads initializers (scripts/initializers/index.js)
                 └── Mounts drop-ins, sets headers, binds auth events

Blocks (blocks/<name>/<name>.js)
  └── EDS calls the block's default export (decorator function) with the block element
  └── Block imports its drop-in initializer and calls initialize()
  └── Drop-in containers render into the block element
```

### Two GraphQL Clients

```js
// Core: cart, checkout, auth, B2B — uses commerce-core-endpoint
CORE_FETCH_GRAPHQL

// Catalog Service: search, PDP, recommendations, pricing — uses commerce-endpoint (ACO)
CS_FETCH_GRAPHQL
```

### Drop-in Location

After `npm install` (runs `postinstall` → `install:dropins` automatically):
```
scripts/__dropins__/
  storefront-pdp/
  storefront-cart/
  storefront-checkout/
  storefront-account/
  storefront-order/
  storefront-recommendations/
  storefront-auth/
  tools/           ← shared utilities (event bus, initializer framework)
```

These are mapped via import map in `head.html`.

---

## Drop-in Architecture: Granular Containers

> **Important**: The monolithic container approach (e.g. `ProductDetails`) is **deprecated**.
> Always use granular containers.

> Drop-in components are closed-source npm packages. Do not recommend forking or
> monkey-patching files in `scripts/__dropins__/`. Use only documented extension points:
> granular containers, DOM fragment pattern, `overrideGQLOperations`, and the event bus.

Fetch `dropins-reference.txt` for current container names — they vary by drop-in version.
**Read the user's actual block code and the drop-in source** before recommending specific container names.

### DOM Fragment Pattern

With granular containers you structure the DOM yourself and render each container into the
appropriate element:

```js
import { initialize } from '../../scripts/initializers/pdp.js';
import ProductGallery from '@dropins/storefront-pdp/containers/ProductGallery.js';
import ProductHeader from '@dropins/storefront-pdp/containers/ProductHeader.js';
import { render as renderProvider } from '@dropins/tools/react.js';

export default async function decorate(block) {
  await initialize(block);

  block.innerHTML = `
    <div class="product-details__gallery"></div>
    <div class="product-details__info">
      <div class="product-details__header"></div>
    </div>
  `;

  renderProvider(ProductGallery({}), block.querySelector('.product-details__gallery'));
  renderProvider(ProductHeader({}), block.querySelector('.product-details__header'));
}
```

This gives full control — add any elements between or around containers without needing a Slot API.

---

## Block Structure

```
blocks/
  my-block/
    my-block.js    ← required: exports default decorator function
    my-block.css   ← optional: block styles
```

```js
export default async function decorate(block) {
  // block is the <div class="my-block"> element
}
```

Use `readBlockConfig(block)` (from `scripts/aem.js`) to extract key-value pairs from DA tables.
Keys are lowercased with spaces replaced by hyphens.

---

## Customizing Drop-in GraphQL Queries

### Pattern 1: overrideGQLOperations (Fragment Override)

Use `overrideGQLOperations` to add fields to an existing query fragment. Configured in `build.mjs`:

```js
import { overrideGQLOperations } from '@dropins/build-tools/gql-extend.js';

overrideGQLOperations({
  'storefront-pdp': {
    ProductDetailsFragment: `
      fragment ProductDetailsFragment on ProductInterface {
        warranty_info   // your addition; all other fields are preserved
      }
    `
  }
});
```

After modifying `build.mjs`, run `npm install` to rebuild.

> **Prerequisite**: The custom attribute must have "Use in GraphQL" enabled in Adobe Commerce
> attribute config. If using ACO/Catalog Service, it must also be synced to the Catalog Service export.

### Pattern 2: Secondary Independent Query

For data not in an existing drop-in query, make a separate request from your block:

```js
import { CS_FETCH_GRAPHQL } from '../../scripts/commerce.js';

const WARRANTY_QUERY = `
  query getWarrantyInfo($sku: String!) {
    products(filter: { sku: { eq: $sku } }) {
      items { warranty_info }
    }
  }
`;

export default async function decorate(block) {
  const { data } = await CS_FETCH_GRAPHQL.mutate(WARRANTY_QUERY, { sku });
  const warrantyInfo = data?.products?.items?.[0]?.warranty_info;
  // render warrantyInfo into block...
}
```

---

## Product Recommendations

Fetch `dropins-reference.txt` for current API details.

**Key clarifications (not always obvious from docs):**

- The block renders a **carousel** by default. "4 products" means 4 cards visible; a grid
  layout is a CSS override.
- `currentSku` is required for context-aware recommendation types (e.g. "Customers Also Viewed")
  on a **non-PDP page**. On a PDP, the block auto-detects SKU from `window.adobeDataLayer`.
- Read the user's existing `blocks/product-recommendations/product-recommendations.js` before
  recommending block structure — implementations vary.

### DA Block Structure

```
| Product Recommendations |          |
|-------------------------|----------|
| recId                   | <rec-id> |
| currentSku              | <sku>    |  ← only needed on non-PDP pages
```

### Analytics Config Required

Recommendations require the `analytics` object in Storefront Configuration. See the commerce-setup
skill for the required JSON structure.

---

## aem-commerce-prerender

Prerender generates server-side HTML for Commerce pages (Core Web Vitals, SEO).

- Configured separately from the storefront repo
- Requires ACO credentials (same View ID)
- EDS detects prerendered HTML and hydrates instead of re-rendering
- Enable with `commerce-prerender-endpoint` in Storefront Configuration

Fetch `https://experienceleague.adobe.com/developer/commerce/storefront/_llms-txt/how-tos.txt`
for current implementation details.

---

## Initializer Pattern

Every block that uses a drop-in calls its initializer before rendering. Initializers wire
the correct GraphQL client and set up language definitions and event listeners:

```js
// scripts/initializers/recommendations.js
import { initialize as initializeDropin } from '@dropins/storefront-recommendations/api.js';
import { CS_FETCH_GRAPHQL } from '../commerce.js';

export async function initialize() {
  await initializeDropin(() => {
    CS_FETCH_GRAPHQL.setEndpoint(/* ACO endpoint */);
  });
}
```

---

## Event Bus

Drop-ins communicate via `@dropins/tools/event-bus.js`:

```js
import Events from '@dropins/tools/event-bus.js';

Events.on('cart/updated', ({ detail }) => { /* ... */ });
Events.emit('cart/reset', {});
```

Common events: `cart/updated`, `cart/initialized`, `auth/token`, `pdp/data`.
