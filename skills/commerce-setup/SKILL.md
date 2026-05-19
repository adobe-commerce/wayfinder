---
name: commerce-setup
description: >
  Guides software engineers through setting up and configuring Adobe Commerce environments
  and EDS storefronts. Use this skill whenever someone is creating a new Adobe Commerce
  Cloud Service (ACCS), Adobe Commerce Optimizer (ACO), or PaaS backend environment;
  creating or configuring an EDS (Edge Delivery Services) storefront using the
  hlxsites/aem-boilerplate-commerce template; setting up Storefront Configuration;
  configuring CORS on Adobe Commerce; setting up DA (Document Authoring) content sources
  or permissions; or doing initial DA content authoring (pages, blocks, publishing). Also
  use when the user asks about fstab.yaml, import maps, dropin installation, or getting
  a storefront running locally for the first time.
---

# Adobe Commerce Setup Skill

You are helping a software engineer set up an Adobe Commerce environment and/or EDS storefront.

## Terminology — Always Use These Terms

| Use This | Not This | Notes |
|---|---|---|
| **Adobe Commerce** | ~~Magento~~ | The user may say "Magento", "PaaS", or "ACCS" — translate internally |
| **Storefront Configuration** | ~~config.json~~ | Uses EDS `publicConfig` feature via AEM Admin API |
| **Adobe Commerce Optimizer (ACO)** | ~~ACO~~ alone on first mention | Spell out on first use |

---

## Source Authority

When sources conflict, the domain owner is authoritative:

| Domain | Authoritative Source | URL |
|---|---|---|
| EDS platform — Code Sync, Admin API, CDN, publishing, fstab | **aem.live** | `https://www.aem.live/llms.txt` |
| Document Authoring (DA) — platform, access, features | **aem.live** | `https://www.aem.live/llms.txt` |
| Storefront drop-ins, blocks, boilerplate, recommendations | **Storefront ExL** | `https://experienceleague.adobe.com/developer/commerce/storefront/llms.txt` |
| Commerce backend, B2B, admin, catalog, data export | **Commerce ExL** | `https://experienceleague.adobe.com/en/docs/commerce` |

---

## Fetch Strategy

Fetch current documentation before answering — do not rely on static knowledge for specifics.

| Topic | Fetch This URL |
|---|---|
| Architecture overview, onboarding | `https://experienceleague.adobe.com/developer/commerce/storefront/_llms-txt/get-started.txt` |
| Boilerplate repo structure, fstab.yaml, head.html, import maps | `https://experienceleague.adobe.com/developer/commerce/storefront/_llms-txt/boilerplate.txt` |
| Storefront Configuration keys, CORS, environment setup | `https://experienceleague.adobe.com/developer/commerce/storefront/_llms-txt/setup-reference.txt` |
| DA content authoring — pages, blocks, publishing | `https://experienceleague.adobe.com/developer/commerce/storefront/_llms-txt/merchants-authoring.txt` |
| EDS platform — Code Sync, Admin API, CDN, DA platform | `https://www.aem.live/llms.txt` then fetch linked section pages |
| B2B backend, Commerce admin, catalog | `https://experienceleague.adobe.com/en/docs/commerce` (browse/fetch specific pages) |

> The `search-commerce-docs` MCP tool can also search storefront docs but requires `aio auth login`.

---

## System Architecture

```
Browser
  |
  +-- Core requests (cart, checkout, auth, B2B)    --> Adobe Commerce GraphQL (commerce-core-endpoint)
  +-- Catalog requests (search, PDP, recs, prices) --> ACO GraphQL (commerce-endpoint)

EDS Storefront (hlxsites/aem-boilerplate-commerce)
  |
  +-- Content   <-- Document Authoring (DA) at da.live
  +-- Code      <-- GitHub repo (synced via AEM Code Sync app)
  +-- Drop-ins  <-- npm packages, installed to scripts/__dropins__/
  +-- Config    <-- Storefront Configuration (EDS publicConfig, cached 2h sessionStorage + CDN)
```

**Key insight**: Two distinct GraphQL endpoints. `commerce-endpoint` is always ACO (catalog).
`commerce-core-endpoint` is Adobe Commerce (transactions). If `commerce-core-endpoint` is
omitted, both fall back to `commerce-endpoint`.

---

## Storefront Configuration

The Storefront Configuration is the central configuration for the storefront. It uses the
EDS `publicConfig` feature and is managed via the AEM Admin API at
`https://admin.hlx.page/config/<orgname>/sites/<sitename>.json`. It is **not** managed in DA
or as a file in the code repository. (A `config.json` in the repo root can override it for
local development, but this is not recommended for production.)

Config is cached for 2 hours in `sessionStorage` and on the CDN. After changes:
- Wait 1–2 minutes for CDN propagation
- Use an incognito window or clear sessionStorage to bypass the browser cache

### Minimum Required Configuration (ACO)

Only `AC-View-ID` is strictly required in the headers. The Price Book ID is auto-determined
by the auth drop-in based on the user's customer group — do not hardcode it unless you want
to override that behavior.

```json
{
  "public": {
    "default": {
      "commerce-endpoint": "https://na1.api.commerce.adobe.com/<TENANT_ID>/graphql",
      "commerce-core-endpoint": "https://<INSTANCE>.commercecloud.adobe.com/graphql",
      "adobe-commerce-optimizer": true,
      "headers": {
        "all": { "Store": "default" },
        "cs": {
          "AC-View-ID": "<CATALOG_VIEW_ID>"
        }
      }
    }
  }
}
```

### Analytics — Required for Recommendations

Analytics-based features (product recommendations, personalization) require the analytics
object. Without it, recommendations will not function:

```json
"analytics": {
  "base-currency-code": "USD",
  "environment": "Testing",
  "environment-id": "<TENANT_ID>",
  "store-url": "https://main--<repo>--<org>.aem.live/",
  "store-view-currency-code": "USD",
  "storefront-template": "Other",
  "view-id": "<CATALOG_VIEW_ID>",
  "locale": "en-US"
}
```

### Key Config Reference

| Key | Purpose |
|---|---|
| `commerce-endpoint` | ACO GraphQL — Catalog Service (search, PDP, recs, pricing) |
| `commerce-core-endpoint` | Adobe Commerce GraphQL — Core (cart, checkout, auth, B2B) |
| `adobe-commerce-optimizer` | Enables ACO code paths and dynamic price book header |
| `headers.all` | Headers sent with all GraphQL requests |
| `headers.cs` | Headers sent only with Catalog Service (ACO) requests |
| `AC-View-ID` | Which ACO Catalog View to query (required) |
| `AC-Price-Book-ID` | Override price book (optional — auth drop-in auto-determines this) |

---

## Repository Setup

### fstab.yaml — One-Time Initialization

`fstab.yaml` defines the content source and is read **only once** when AEM Code Sync first
installs. After Code Sync is configured, changes to the content source must be made via the
AEM Admin API — editing `fstab.yaml` after installation has no effect.

Verify this is correct **before** installing the AEM Code Sync GitHub App:

```yaml
mountpoints:
  /:
    url: https://content.da.live/<org>/<repo>/
    type: markup

folders:
  /products/: /products/default
```

### Installation Steps

1. Confirm `fstab.yaml` is correct (see above)
2. Install the [AEM Code Sync GitHub App](https://github.com/apps/aem-code-sync) on the repo
3. Clone the repo locally
4. Run `npm install` — runs `postinstall` → `install:dropins` automatically
5. Preview and publish content in DA to confirm it appears at `*.aem.page` / `*.aem.live`
6. Configure Storefront Configuration via AEM Admin API
7. Run `npm start` to serve locally at `http://localhost:3000`

If Code Sync is already installed and `fstab.yaml` needs changing, use the AEM Admin API.
Fetch `https://www.aem.live/llms.txt` to find the Admin API docs section, then fetch that page for authentication and endpoint details.

---

## DA Permissions

When a user sees "Not permitted" or a 403 on `admin.da.live`, they are authenticated but
not authorized.

Key points:
- DA uses a **sheet-based ACL** at `da.live/config#/{org}/` — not a file in the GitHub repo
- The permissions sheet grants access via **individual email addresses or IMS user groups**
- If the org config is empty or inaccessible, someone with existing `CONFIG write` access
  must create or update the sheet
- Check the **IMS organization switcher** (top right in DA UI) first — the user may be in the wrong org
- Users can authenticate via any IDP supported by Adobe IMS (not necessarily Adobe ID)
- If escalation is needed, direct external users to contact **Adobe support through their official support channel** (never reference internal Slack channels)

For full DA platform docs: fetch from `https://www.aem.live/llms.txt` and follow the DA section links.

---

## CORS on Adobe Commerce

The EDS storefront makes cross-origin requests from `*.aem.live` / `*.aem.page` to Adobe
Commerce. Without CORS headers, the auth drop-in's request to fetch the price book ID fails
silently, and `AC-Price-Book-ID` is removed from all Catalog Service requests — causing
prices to show as $0.00.

```bash
curl -I -X OPTIONS \
  -H "Origin: https://main--<repo>--<org>.aem.live" \
  -H "Access-Control-Request-Method: POST" \
  https://<INSTANCE>.commercecloud.adobe.com/graphql
# Expect: Access-Control-Allow-Origin in response
```

---

## Common Setup Mistakes

1. **CORS not configured on Adobe Commerce** → auth drop-in price book query fails → prices $0.00
2. **fstab.yaml edited after Code Sync installed** → has no effect; use AEM Admin API instead
3. **Drop-ins missing from `scripts/__dropins__/`** → run `npm run install:dropins` manually
4. **AEM Code Sync app not installed** → code changes won't sync to CDN
5. **DA permissions not set** → "Not permitted" on da.live; check IMS org switcher first
6. **Analytics config missing** → product recommendations won't work
