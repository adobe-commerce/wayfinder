# EDS Storefront + Adobe Commerce Optimizer (ACO) Setup Guide

End-to-end guide for setting up an Edge Delivery Services (EDS) storefront connected to Adobe Commerce Optimizer (ACO), with an Adobe Commerce core endpoint when the storefront needs cart, checkout, authentication, account, or B2B functionality.

---

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [Prerequisites](#2-prerequisites)
3. [Create the Storefront Repository](#3-create-the-storefront-repository)
4. [Configure Content Source (DA)](#4-configure-content-source-da)
5. [Install Drop-in Dependencies](#5-install-drop-in-dependencies)
6. [Gather ACO Instance Details](#6-gather-aco-instance-details)
7. [Configure Storefront Configuration](#7-configure-storefront-configuration)
8. [Configure CORS on Adobe Commerce](#8-configure-cors-on-adobe-commerce)
9. [Local Development](#9-local-development)
10. [Verify the Integration](#10-verify-the-integration)
11. [Author Content in DA](#11-author-content-in-da)
12. [Troubleshooting](#12-troubleshooting)

---

## 1. Architecture Overview

For an ACO storefront that also uses Commerce transactional features, configure two GraphQL endpoints:

| Endpoint | Config Key | Used For | Backed By |
|---|---|---|---|
| **Core** | `commerce-core-endpoint` | Cart, checkout, auth, account, B2B | Adobe Commerce |
| **Catalog Service** | `commerce-endpoint` | Product catalog, search, recommendations, pricing | Adobe Commerce Optimizer (ACO) |

```
Browser
  |
  +-- Core requests (cart, auth, checkout) --> Adobe Commerce GraphQL
  |
  +-- Catalog requests (search, PDP, recs)  --> ACO GraphQL
```

**How it works in the current boilerplate** (`scripts/commerce.js`):

```js
// Core endpoint: uses commerce-core-endpoint, falls back to commerce-endpoint
CORE_FETCH_GRAPHQL.setEndpoint(
  getConfigValue('commerce-core-endpoint') || getConfigValue('commerce-endpoint')
);

// Catalog Service endpoint: always uses commerce-endpoint
CS_FETCH_GRAPHQL.setEndpoint(await commerceEndpointWithQueryParams());
```

**Key flag**: Setting `"adobe-commerce-optimizer": true` in Storefront Configuration enables ACO-specific code paths:
- The auth drop-in queries Adobe Commerce for `commerceOptimizer { priceBookId }` and dynamically sets the `AC-Price-Book-ID` header based on the user's customer group
- ACO-specific headers (`AC-View-ID`, `AC-Price-Book-ID`) are sent with Catalog Service requests

---

## 2. Prerequisites

- **Adobe Commerce instance** with:
  - GraphQL API accessible
  - CORS configured for your EDS domain (see [Section 8](#8-configure-cors-on-adobe-commerce))
  - Catalog data synced to ACO

- **Adobe Commerce Optimizer instance** with:
  - Access via [Adobe Experience Cloud](https://experience.adobe.com/)
  - At least one Catalog View configured
  - Price Book assigned (if using custom pricing)

- **GitHub repository** with AEM Code Sync GitHub App installed

- **DA (Document Authoring)** access at [da.live](https://da.live)

- **Node.js** (v18+) and npm

- **AEM CLI** for local development:
  ```bash
  npm install -g @adobe/aem-cli
  ```

---

## 3. Create the Storefront Repository

### Option A: Site Creator Tool (Recommended)

1. Go to [DA Site Creator](https://da.live/app/adobe-commerce/storefront-tools/tools/site-creator/site-creator)
2. Follow the guided setup to create your repository and content source

### Option B: Manual Setup

1. Create a new repository from the [EDS Commerce Boilerplate](https://github.com/hlxsites/aem-boilerplate-commerce) template
2. Install the [AEM Code Sync GitHub App](https://github.com/apps/aem-code-sync) on your repository
3. Clone the repository locally:
   ```bash
   git clone https://github.com/<org>/<repo>.git
   cd <repo>
   ```

---

## 4. Configure Content Source (DA)

If you use Site Creator, it creates or attaches the DA content folder as part of the guided flow. Use the manual `fstab.yaml` path only when your setup process requires it.

> **Important**: `fstab.yaml` is read during initial site provisioning. After Code Sync has provisioned the site, update content source and folder mappings through the AEM Admin API / Configuration Service instead of editing `fstab.yaml` in the repository.

Configure `fstab.yaml` **before** installing the AEM Code Sync GitHub App:

```yaml
mountpoints:
  /:
    url: https://content.da.live/<org>/<repo>/
    type: markup

folders:
  /products/: /products/default
```

- Replace `<org>` and `<repo>` with your DA organization and site name
- The `folders` mapping provides a default template for product detail pages

Your site will be available at:
- **Preview**: `https://main--<repo>--<org>.aem.page/`
- **Live**: `https://main--<repo>--<org>.aem.live/`

---

## 5. Install Drop-in Dependencies

```bash
npm install
```

`npm install` automatically runs `install:dropins` via the `postinstall` script. This copies drop-in component files from `node_modules` into `scripts/__dropins__/`, which is the local serving path referenced by the import map in `head.html`.

If `scripts/__dropins__/` is missing after install, run `npm run install:dropins` manually to re-run the copy step.

The import map in `head.html` maps package names to local paths:
```html
<script type="importmap">
{
  "imports": {
    "@dropins/storefront-pdp/": "/scripts/__dropins__/storefront-pdp/",
    "@dropins/storefront-cart/": "/scripts/__dropins__/storefront-cart/",
    "@dropins/tools/": "/scripts/__dropins__/tools/",
    ...
  }
}
</script>
```

---

## 6. Gather ACO Instance Details

### Access ACO

1. Log in to [Adobe Experience Cloud](https://experience.adobe.com/)
2. Open **Commerce** > **Commerce Cloud Manager**
3. Click your instance name to open the ACO application
4. Click the **info icon** next to the instance name for Instance Details

### Values to collect

| Value | Where to Find | Example |
|---|---|---|
| **GraphQL Endpoint** | Instance Details panel | `https://na1.api.commerce.adobe.com/<tenantId>/graphql` |
| **Catalog View ID** | Catalog > Views in ACO UI | `c793c282-70b5-4328-9440-068b4c7522c3` |
| **Price Book ID** | Catalog View configuration | `base::b6589fc6ab0dc82cf12099d1c2d40ab994e8410c` |
| **Tenant ID** | Instance Details (also in the endpoint URL) | `N5raScCffY2MjWSEEyALCV` |
| **Adobe Commerce GraphQL URL** | Your Adobe Commerce Admin | `https://<instance>.commercecloud.adobe.com/graphql` |

---

## 7. Configure Storefront Configuration

Storefront configuration is the central configuration for Commerce endpoints, headers, feature flags, and analytics values. For production, prefer AEM Configuration Service public config. For local development and branch testing, a repository-root `config.json` can be useful, but any `config.json` present on `main` takes precedence over Configuration Service values and can silently override production config.

**Recommended production location:**
```
https://admin.hlx.page/config/{org}/sites/{site}/public.json
```

Authentication is required to update the site config. See [AEM Admin API docs](https://www.aem.live/docs/admin.html) for authentication and API reference.

The config is cached: the CDN caches it with `max-age=7200` (2 hours), and the browser
caches it in `sessionStorage` with the same 2-hour expiry. After changing the config, open
an incognito window or clear sessionStorage to bypass the browser cache.

> **Local development:** A `config.json` file in the repo root overrides Configuration Service values. Use it for local development or branch-based testing, and keep it off `main` for production sites that rely on Configuration Service.

### Full ACO + Adobe Commerce Configuration

```json
{
  "public": {
    "default": {
      "commerce-endpoint": "https://na1.api.commerce.adobe.com/<TENANT_ID>/graphql",
      "commerce-core-endpoint": "https://<MAGENTO_INSTANCE>.commercecloud.adobe.com/graphql",
      "adobe-commerce-optimizer": true,
      "headers": {
        "all": {
          "Store": "default"
        },
        "cs": {
          "AC-View-ID": "<CATALOG_VIEW_ID>",
          "AC-Price-Book-ID": "<PRICE_BOOK_ID>"
        }
      },
      "commerce-b2b-enabled": true,
      "commerce-companies-enabled": true,
      "commerce-assets-enabled": true,
      "analytics": {
        "base-currency-code": "USD",
        "environment": "Testing",
        "environment-id": "<TENANT_ID>",
        "store-url": "https://main--<repo>--<org>.aem.live/",
        "store-view-currency-code": "USD",
        "storefront-template": "Other",
        "view-id": "<CATALOG_VIEW_ID>",
        "locale": "en-US"
      },
      "plugins": {
        "picker": {
          "rootCategory": "2"
        }
      }
    }
  }
}
```

### Config Keys Explained

| Key | Purpose |
|---|---|
| `commerce-endpoint` | ACO GraphQL endpoint. Used by Catalog Service (`CS_FETCH_GRAPHQL`) for search, PDP, recommendations |
| `commerce-core-endpoint` | Adobe Commerce core GraphQL endpoint. Used by Core (`CORE_FETCH_GRAPHQL`) for write operations and some reads, including cart, checkout, and auth. Falls back to `commerce-endpoint` if omitted |
| `adobe-commerce-optimizer` | Enables ACO code paths: dynamic price book header, ACO flag passed to auth drop-in |
| `headers.all` | Headers sent with **all** GraphQL requests (both Core and Catalog Service) |
| `headers.cs` | Headers sent only with **Catalog Service** requests (ACO) |
| `AC-View-ID` | Identifies which ACO Catalog View to query |
| `AC-Price-Book-ID` | Identifies which Price Book to use for pricing. **Optional** — the auth drop-in automatically determines this from the user's customer group when `adobe-commerce-optimizer` is `true`. Set it here only as a fallback or override. |

### How Headers Are Applied

In `scripts/commerce.js`:
```js
// Core endpoint gets "all" headers
CORE_FETCH_GRAPHQL.setFetchGraphQlHeaders((prev) => ({ ...prev, ...getHeaders('all') }));

// Catalog Service gets "cs" headers
CS_FETCH_GRAPHQL.setFetchGraphQlHeaders((prev) => ({ ...prev, ...getHeaders('cs') }));
```

### Dynamic Price Book Header

When `adobe-commerce-optimizer` is `true`, the auth drop-in queries the **Core endpoint** (Adobe Commerce) for the price book ID based on the user's customer group:

```graphql
query GET_ADOBE_COMMERCE_OPTIMIZER_DATA {
  commerceOptimizer {
    priceBookId
  }
}
```

If the query succeeds, the returned `priceBookId` overrides the static `AC-Price-Book-ID` header from config. This allows per-user pricing (e.g., B2B customer-specific price books). The handler in `scripts/initializers/index.js`:

```js
const setAdobeCommerceOptimizerHeader = (adobeCommerceOptimizer) => {
  if (adobeCommerceOptimizer?.priceBookId) {
    CS_FETCH_GRAPHQL.setFetchGraphQlHeader('AC-Price-Book-ID', adobeCommerceOptimizer.priceBookId);
  } else {
    CS_FETCH_GRAPHQL.removeFetchGraphQlHeader('AC-Price-Book-ID');
  }
};
```

> **Important**: If the Core endpoint is unreachable (e.g., CORS not configured), this query fails, and the `else` branch removes the `AC-Price-Book-ID` header — even if it was set statically — causing all prices to show as $0.00. This is why CORS configuration on Adobe Commerce is critical.
>
> **Custom solutions**: Since the storefront code is yours, you can also resolve `AC-Price-Book-ID` any way you want — fetch it from your own API, hardcode it, or remove the `setAdobeCommerceOptimizerHeader` function entirely and set the header directly.

---

## 8. Configure CORS on Adobe Commerce

The EDS storefront makes cross-origin requests from `*.aem.live` / `*.aem.page` to your Adobe Commerce instance. Without CORS headers, browser security blocks these requests.

### Required CORS Headers on Adobe Commerce

The Adobe Commerce GraphQL endpoint must return CORS headers that allow your storefront origin. Adobe's storefront CORS setup guide lists these minimum requirements:

```
Access-Control-Allow-Origin: https://main--<repo>--<org>.aem.live
Access-Control-Allow-Methods: GET, POST, OPTIONS
Access-Control-Allow-Headers: Content-Type, Authorization, X-Requested-With
```

If your storefront sends additional Commerce headers such as `Store` or `X-Adobe-Company`, include those in your CORS implementation's allowed headers as well.

### Configuration Options

**Option A: Server or edge configuration**
- Configure CORS headers at the web server or edge layer used by your Commerce deployment.

**Option B: Custom module or middleware**
- Add CORS headers via a custom Adobe Commerce module or server configuration

### Verify CORS

```bash
curl -I -X OPTIONS \
  -H "Origin: https://main--<repo>--<org>.aem.live" \
  -H "Access-Control-Request-Method: POST" \
  https://<INSTANCE>.commercecloud.adobe.com/graphql
```

You should see `Access-Control-Allow-Origin` in the response headers.

### What Happens Without CORS

Without CORS, browser requests from the EDS storefront to the Adobe Commerce core endpoint fail. In ACO storefronts, that can also prevent the auth drop-in from resolving a dynamic `AC-Price-Book-ID`, causing:
- All product prices show as **$0.00**
- Other core requests, such as cart or checkout, may fail

---

## 9. Local Development

Start the local dev server:

```bash
npm start
```

This runs `aem up`, which:
- Serves the site locally at `http://localhost:3000`
- Proxies content from your DA content source
- Hot-reloads code changes

### Useful Commands

| Command | Purpose |
|---|---|
| `npm start` | Start local dev server (`aem up`) |
| `npm run lint` | Run ESLint + Stylelint |
| `npm run install:dropins` | Rebuild and copy drop-in files |

---

## 10. Verify the Integration

### Step 1: Check Config Loading

Open DevTools > Console. You should see event bus logger output. No `418` error page should appear.

### Step 2: Verify GraphQL Endpoints

Open DevTools > Network tab. Filter by `graphql`:

- **Catalog requests** (search, PDP) should go to the ACO endpoint (`na1.api.commerce.adobe.com`)
- **Core requests** (cart, auth) should go to the Adobe Commerce endpoint

### Step 3: Verify ACO Headers

Click on a Catalog Service request and check Request Headers:

```
AC-View-ID: <your-view-id>
AC-Price-Book-ID: <your-price-book-id>
```

### Step 4: Test Search

Use the search bar to query for a product. Verify:
- Products are returned
- Prices are **not** $0.00
- Product images load

### Step 5: Test Cart

Add a product to cart and verify the cart drawer opens with the correct item and price.

### Config Caching Note

Storefront Configuration is cached in `sessionStorage`, and `/config.json` is cached by the Edge CDN with a 2-hour cache control header. After updating via the AEM Admin API:
- Check `/config.json` directly to see which configuration the CDN is serving
- Open an **incognito window** (or clear sessionStorage) to bypass the browser cache

---

## 11. Author Content in DA

### Access DA

- **Editor**: `https://da.live/#/edit/<org>/<repo>/<page>`
- **File browser**: `https://da.live/#/<org>/<repo>/`

### EDS Content Model

Content in DA maps to the EDS block structure:

- **Sections** are separated by horizontal rules (`---`)
- **Blocks** are tables where the first row (merged cells) is the block name
- **Section metadata** is a special table that applies styles/layout to its containing section

### Example: Section Metadata

To apply a custom style to a section:

| section-metadata |  |
|---|---|
| **style** | `custom-style` |

This adds the class `custom-style` to the section's wrapper `<div>`, which you can target with CSS.

---

## Next Steps

- **Product Recommendations Setup Guide** — Add product recommendation units to your storefront pages

---

## 12. Troubleshooting

### Prices Show as $0.00

**Cause**: The `AC-Price-Book-ID` header is missing from Catalog Service requests.

**Check**:
1. Verify CORS is configured on Adobe Commerce. Without it, the auth drop-in's query fails and the dynamic handler removes the header — even if `AC-Price-Book-ID` was set in Storefront Configuration
2. In DevTools Network, find a catalog GraphQL request and check if `AC-Price-Book-ID` is in the request headers
3. If you want to bypass the auth dropin mechanism entirely, you can set `AC-Price-Book-ID` in Storefront Configuration under `headers.cs`, fetch it from your own API, or remove `setAdobeCommerceOptimizerHeader` and set the header directly

**Test with curl**:
```bash
curl -X POST https://na1.api.commerce.adobe.com/<TENANT_ID>/graphql \
  -H "Content-Type: application/json" \
  -H "AC-View-ID: <VIEW_ID>" \
  -H "AC-Price-Book-ID: <PRICE_BOOK_ID>" \
  -d '{"query":"{ products(search: \"bag\") { items { name price { regular { amount { value currency } } } } } }"}'
```

### 418 Configuration Error

**Cause**: `initializeCommerce()` in `scripts/scripts.js` threw an error during config initialization.

**Check**:
1. Ensure Storefront Configuration JSON is valid
2. Ensure `commerce-endpoint` is set and reachable
3. If `commerce-core-endpoint` is set, ensure the Adobe Commerce instance is reachable and CORS is configured
4. Clear sessionStorage and refresh: DevTools > Application > Session Storage > delete the `config` entry

### Search Returns No Results

**Cause**: Possible locale mismatch or missing catalog data.

**Check**:
1. Remove `AC-Source-Locale` from headers if your catalog was not ingested with a specific locale
2. Verify products exist in the ACO Catalog View by querying directly:
   ```bash
   curl -X POST https://na1.api.commerce.adobe.com/<TENANT_ID>/graphql \
     -H "Content-Type: application/json" \
     -H "AC-View-ID: <VIEW_ID>" \
     -d '{"query":"{ products(search: \"*\") { total_count items { name sku } } }"}'
   ```

### CDN Not Serving Updated Files

**Cause**: AEM Code Sync may not have processed the file.

**Check**:
1. Verify the AEM Code Sync GitHub App is installed on your repository
2. Check sync status (authentication required — see [AEM Admin API docs](https://www.aem.live/docs/admin.html)):
   ```bash
   curl -H "Authorization: token <your-token>" \
     https://admin.hlx.page/status/<org>/<repo>/main/<file-path>
   ```
3. File paths on the CDN are **case-sensitive** (e.g., `SearchResults.js` is not the same as `searchresults.js`)
4. Force re-sync — choose one:
   - **Admin API** (requires auth): `POST https://admin.hlx.page/live/<org>/<repo>/main/<path>`
   - **Trivial commit**: add/remove a comment and push to trigger the webhook
   - **PR checkbox**: open a pull request — each PR gets a Code Sync comment with a checkbox that triggers re-sync when checked

### Config Changes Not Taking Effect

**Cause**: Storefront Configuration is cached in sessionStorage for 2 hours.

**Fix**:
1. Open an incognito/private window
2. Or clear sessionStorage manually: DevTools > Application > Session Storage > delete the `config` entry
3. Check `/config.json` directly; the Edge CDN may serve cached config for up to 2 hours

---

## Key Files Reference

| File | Purpose |
|---|---|
| Storefront Configuration | Central configuration: endpoints, headers, feature flags. Prefer Configuration Service for production; use repository `config.json` for local or branch testing. |
| `fstab.yaml` | Legacy/manual content source mapping (DA) used during initial provisioning; after provisioning, update content source through Configuration Service. |
| `head.html` | Import map, CSP policy, modulepreload hints |
| `scripts/commerce.js` | Dual-endpoint setup, config caching, commerce initialization |
| `scripts/scripts.js` | Page lifecycle: eager/lazy/delayed loading phases |
| `scripts/initializers/index.js` | Drop-in initialization, auth headers, ACO header management |
| `scripts/initializers/auth.js` | Auth drop-in setup, passes `adobeCommerceOptimizer` flag |
| `demo-config-aco.json` | Reference ACO-only configuration template |

## Official references & attribution

- [Create a Storefront](https://experienceleague.adobe.com/developer/commerce/storefront/get-started/create-storefront/) (retrieved 2026-05-14). Used to verify Site Creator, manual repository setup, Code Sync, config generator, DA content creation, and local setup flow.
- [Storefront Configuration](https://experienceleague.adobe.com/developer/commerce/storefront/setup/configuration/commerce-configuration/) (retrieved 2026-05-14). Used to verify `commerce-core-endpoint`, `commerce-endpoint`, ACO configuration, Configuration Service versus repository `config.json`, caching, and `headers.cs` values.
- [Price Book ID Setup](https://experienceleague.adobe.com/developer/commerce/storefront/setup/configuration/price-book-setup/) (retrieved 2026-05-14). Used to verify the ACO auth drop-in event, `adobeCommerceOptimizer` option, and dynamic `AC-Price-Book-ID` handling.
- [CORS Setup](https://experienceleague.adobe.com/developer/commerce/storefront/setup/configuration/cors-setup/) (retrieved 2026-05-14). Used to verify CORS requirements, minimum allowed methods, and minimum allowed headers for Adobe Commerce PaaS GraphQL requests.
- [AEM Configuration Service Setup](https://www.aem.live/docs/config-service-setup) (retrieved 2026-05-14). Used to verify `public.json`, content source configuration, and Configuration Service API paths.
- [AEM Admin API](https://www.aem.live/docs/admin.html) (retrieved 2026-05-14). Used to verify Admin API authentication and status/config endpoint patterns.
- [Adobe Commerce Optimizer storefront setup](https://experienceleague.adobe.com/en/docs/commerce/optimizer/storefront) (retrieved 2026-05-14). Used to verify ACO values to collect, including tenant ID, GraphQL endpoint, catalog view ID, source locale, and price book headers.
- [aem-boilerplate-commerce `scripts/commerce.js`](https://raw.githubusercontent.com/hlxsites/aem-boilerplate-commerce/main/scripts/commerce.js), [`scripts/initializers/index.js`](https://raw.githubusercontent.com/hlxsites/aem-boilerplate-commerce/main/scripts/initializers/index.js), and [`scripts/initializers/auth.js`](https://raw.githubusercontent.com/hlxsites/aem-boilerplate-commerce/main/scripts/initializers/auth.js) (retrieved 2026-05-14). Used to verify current boilerplate endpoint selection, header application, session-storage config caching, and ACO auth initialization code snippets.
