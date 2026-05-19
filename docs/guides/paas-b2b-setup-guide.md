# Adobe Commerce Cloud B2B Starter with Edge Delivery Services and Commerce Optimizer

Use this guide for an Adobe Commerce on Cloud infrastructure (PaaS) project template that provisions a **B2B-capable backend** for an **Edge Delivery Services (EDS) storefront** and, when licensed, **Adobe Commerce Optimizer (ACO)** for catalog merchandising. The version numbers and package names below are template-specific; verify them against the actual `composer.json`, `.magento.app.yaml`, `.magento/services.yaml`, and current Adobe release notes before using them in a production rollout.

You must have an active Adobe Commerce Cloud license to use this template.

**Setup Guide** (do these in order):

-  [Architecture Overview](#architecture-overview)
-  [Glossary](#glossary)
-  [Tech Stack](#tech-stack)
-  [Prerequisites](#prerequisites)
-  [Setup Progress Checklist](#setup-progress-checklist)
-  [Phase 1: Commerce Cloud Backend](#phase-1-commerce-cloud-backend)
-  [Phase 2: B2B Configuration](#phase-2-b2b-configuration)
-  [Phase 3: EDS Storefront and CORS](#phase-3-eds-storefront-and-cors)
-  [Phase 4: Adobe Commerce Optimizer (ACO)](#phase-4-adobe-commerce-optimizer-aco)

**Reference** (look up when needed):

-  [Repository Structure](#repository-structure)
-  [Sample Data](#sample-data)
-  [Disable a Module on Cloud](#disable-a-module-on-cloud)
-  [Cron Configuration](#cron-configuration)
-  [Useful Commands](#useful-commands)
-  [Troubleshooting](#troubleshooting)
-  [Developer Documentation](#developer-documentation)

## Architecture Overview

This project implements a three-layer architecture:

```
┌─────────────────────────┐
│   EDS Storefront        │  Decoupled frontend (Edge Delivery Services)
│   (Drop-in Components)  │  Renders product pages, category pages, cart, checkout
└───────────┬─────────────┘
            │ GraphQL / REST API
            ▼
┌─────────────────────────┐
│  Commerce Cloud (PaaS)  │  Adobe Commerce backend
│  B2B + Catalog + Orders │  Companies, shared catalogs, purchase orders,
│                         │  negotiable quotes, requisition lists
└───────────┬─────────────┘
            │ SaaS Data Export Pipeline
            ▼
┌─────────────────────────┐
│  Adobe Commerce         │  Catalog merchandising and optimization
│  Optimizer (ACO)        │  Consumes exported catalog/pricing/inventory data
│  + Live Search          │  SaaS-based search and merchandising for EDS
└─────────────────────────┘
```

## Glossary

If you're new to the Adobe Commerce ecosystem, here are the acronyms used throughout this document:

| Acronym | Full Name | What It Means |
|---|---|---|
| **EDS** | Edge Delivery Services | Adobe's decoupled storefront framework — the frontend your customers see |
| **ACO** | Adobe Commerce Optimizer | A SaaS layer for catalog merchandising and optimization |
| **PaaS** | Platform as a Service | Adobe-managed cloud hosting where your Commerce backend runs |
| **SaaS** | Software as a Service | Adobe-hosted services (search, data export, recommendations) that Commerce connects to |
| **Live Search** | Adobe Commerce Live Search | SaaS-based search and merchandising for storefront search experiences. It does not remove every backend need for a search service in Adobe Commerce. |
| **ECE-Tools** | Experience Cloud Edition Tools | CLI toolkit that handles building and deploying your app on Commerce Cloud |
| **SCD** | Static Content Deployment | The process of pre-compiling CSS, JS, and HTML for the storefront |
| **DI** | Dependency Injection | Adobe Commerce's object-wiring system — "DI compilation" generates optimized class maps |
| **CORS** | Cross-Origin Resource Sharing | Browser security mechanism — must be configured when frontend and backend are on different domains |

## Tech Stack

| Component | Template Value | Source / Verification Note |
|---|---|---|
| Adobe Commerce | 2.4.8 | `composer.json`; Storefront PaaS docs require Adobe Commerce v2.4.7 or later |
| B2B Extension | ^1.5 | `magento/extension-b2b`; verify against B2B release notes and product availability for your Commerce version |
| PHP | 8.4 | `.magento.app.yaml`; **verify before deployment** because Adobe's B2B install docs list PHP 8.1, 8.2, and 8.3 for B2B 1.5.0 |
| Composer | 2.9.3 | `.magento.app.yaml` |
| MySQL (MariaDB) | 11.4 | `.magento/services.yaml` |
| Valkey (cache) | 8.0 | `.magento/services.yaml` |
| OpenSearch | 3 | `.magento/services.yaml` |
| Live Search | SaaS service | Search and merchandising service; configure only if your rollout uses it |
| ACO Adapter | ^1.0 | `adobe-commerce/commerce-data-export-aco-adapter` |
| EDS Compatibility | ^4.8 | `adobe-commerce/storefront-compatibility` |
| EDS B2B Compatibility | ^1.0 | `adobe-commerce/storefront-compatibility-b2b` |
| CORS | ^2.1 | `graycore/magento2-cors` |

## Prerequisites

Before starting, ensure you have:

- An active **Adobe Commerce Cloud (PaaS) license**
- The **Adobe Commerce Cloud CLI** (`magento-cloud`) installed
- **Composer authentication keys** for `repo.magento.com` (public and private key pair)
- Access to an **Adobe Commerce Optimizer tenant** (for ACO integration)
- An **EDS storefront project**, created with Site Creator when available or with the manual GitHub/Code Sync path
- **Git** client installed

## Setup Progress Checklist

> **Returning to this project?** Start here. This checklist tracks the entire end-to-end setup. Each phase has a verification step — **do not move on until it passes.**

- [ ] **Phase 1: Backend** — Clone, authenticate, create `.magento.env.yaml`, deploy to Cloud
  - **Verify:** Admin login works at `https://<your-domain>/admin`
- [ ] **Phase 2: B2B** — Enable Company first, then the B2B features your rollout needs, assign products to shared catalogs if shared catalogs are enabled
  - **Verify:** Enabled B2B settings show the expected values, products are assigned to the intended shared catalog, and SaaS data export counts match the expected storefront-visible catalog
- [ ] **Phase 3: Storefront** — Connect EDS project, configure CORS for cross-domain API access
  - **Verify:** EDS storefront loads a product page with data from Commerce GraphQL
- [ ] **Phase 4: ACO** — Configure Commerce Services Connector / ACO connector as required by your license and trigger initial data sync
  - **Verify:** `bin/magento saas:status` shows feeds syncing

---

# Setup Guide

Follow these phases in order. Each phase builds on the previous one.

---

## Phase 1: Commerce Cloud Backend

This phase gets your Commerce Cloud instance running with the correct services (database, cache, search).

### 1.1 Clone and Authenticate

1.  **Clone** this repository:

    ```bash
    git clone <your-cloud-git-remote> && cd <project-directory>
    ```

2.  **Set up Composer authentication.** You need authentication keys to download Adobe Commerce packages from `repo.magento.com`.

    **Option A — Environment variable (recommended for Cloud):**

    1.  In the _Project Web UI_, click the configuration icon in the upper left corner.
    2.  In the _Configure Project_ view, click the **Variables** tab.
    3.  Click **Add Variable**.
    4.  In the _Name_ field, enter `env:COMPOSER_AUTH`.
    5.  In the _Value_ field, add the following and replace `<public-key>` and `<private-key>` with your Adobe Commerce Cloud authentication credentials:

        ```json
        {
           "http-basic": {
              "repo.magento.com": {
              "username": "<public-key>",
              "password": "<private-key>"
            }
          }
        }
        ```

    6.  Select **Visible during build** and deselect **Visible at run**.
    7.  Click **Add Variable**.

    See [Adding Adobe Commerce authentication keys](https://experienceleague.adobe.com/docs/commerce-cloud-service/user-guide/develop/authentication-keys.html).

    **Option B — `auth.json` file (for Docker / local development):**

    1.  Create an `auth.json` file in your project root directory:

        ```json
        {
          "http-basic": {
            "repo.magento.com": {
              "username": "<public-key>",
              "password": "<private-key>"
            }
          }
        }
        ```

    2.  **Do not commit this file.** It is already in `.gitignore`.

    See [Launching a Docker configuration](https://experienceleague.adobe.com/docs/commerce-cloud-service/user-guide/dev-tools/cloud-docker.html).

### 1.2 Create `.magento.env.yaml`

This file tells ECE-Tools how to configure services during deployment. **It does not exist yet — you must create it.**

Create `.magento.env.yaml` in the project root:

```yaml
stage:
  global:
    SCD_ON_DEMAND: true
  build:
    SCD_STRATEGY: compact
  deploy:
    SEARCH_CONFIGURATION:
      engine: live-search
    CACHE_CONFIGURATION:
      frontend:
        default:
          backend: Magento\Framework\Cache\Backend\RemoteSynchronizedCache
          backend_options:
            remote_backend: Cm_Cache_Backend_Valkey
    SESSION_CONFIGURATION:
      save: valkey
```

**What this does:**
- `SCD_ON_DEMAND: true` — generates static content (CSS/JS) on first request instead of during build, speeding up deployments
- `SCD_STRATEGY: compact` — only deploys changed themes/locales
- `SEARCH_CONFIGURATION` — template-specific search configuration. Confirm the supported search engine value for your Commerce version and installed services before deploying.
- `CACHE_CONFIGURATION` — uses Valkey 8.0 for page and block caching
- `SESSION_CONFIGURATION` — stores user sessions in Valkey instead of the database

### 1.3 Deploy to Cloud

```bash
git add -A && git commit -m "Initial configuration"
git push origin <branch-name>
```

The Cloud platform automatically executes three hooks (defined in `.magento.app.yaml`):

1. **Build hook**: Runs `composer install --no-dev`, then ECE-Tools generates static content and compiles DI
2. **Deploy hook**: Runs database migrations and imports configuration
3. **Post-deploy hook**: Warms caches for faster first-page loads

> **Tip:** Watch the deployment in real-time with `magento-cloud activity:log`

### 1.4 Phase 1 Verification

**Before moving to Phase 2, confirm all of the following:**

1. Run `magento-cloud url` — you should see your store URLs listed
2. Open `https://<your-domain>/admin` in a browser — the Admin login page should load
3. SSH in and run `bin/magento module:status` — it should list modules with no errors

> **Stuck?** See [Troubleshooting > Phase 1](#phase-1-backend-issues).

---

## Phase 2: B2B Configuration

This phase enables B2B-specific features on your Commerce backend. The B2B extension (`magento/extension-b2b: ^1.5`) is already installed — you just need to turn on the features.

### 2.1 Enable B2B Features

In the Admin, navigate to **Stores > Configuration > General > B2B Features**.

> **Important:** You must set **Enable Company** to **Yes** first. The other B2B settings auto-populate immediately — no need to save before continuing. All B2B features depend on company accounts.

Once Company is enabled, the full set of B2B features appears. Enable them in this order:

**Step 1 — Core features:**

| Setting | Set To | What It Does |
|---|---|---|
| **Enable Company** | Yes | Lets business customers create organizational accounts with hierarchical user roles and permissions. **Must be enabled first — all other B2B features depend on this.** |
| **Enable Shared Catalog** | Yes | Assigns different product assortments and pricing to different customer segments. Enables category permissions for all stores. |
| **Enable Shared Catalog direct products price assigning** | Yes | Stores only products assigned to a shared catalog in the price index, which can affect storefront services that depend on indexed product and pricing data. |

**Step 2 — Ordering and quoting features:**

| Setting | Set To | What It Does |
|---|---|---|
| **Enable B2B Quote** | Yes | Enables negotiable quote workflows between buyers and sellers |
| **Enable Quick Order** | Yes | Lets buyers enter SKUs directly to add items to cart without browsing |
| **Enable Requisition List** | Yes | Lets buyers save product lists for repeat orders (like a favorites list) |

**Step 3 — Approval and payment (scroll down to find these):**

| Setting | Set To | What It Does |
|---|---|---|
| **Order Approval Configuration** | Configure as needed | Adds purchase order approval rules (e.g., "orders over $5k need manager approval") |
| **Default B2B Payment Methods** | Configure as needed | Controls which payment methods are available for B2B company accounts |
| **Default B2B Shipping Methods** | Configure as needed | Controls which shipping methods are available for B2B company accounts |

Click **Save Config**.

### 2.2 Assign Products to the Shared Catalog

> **Why this matters:** With Shared Catalogs enabled and "direct products price assigning" set to Yes, product assignment affects which products are price-indexed and available to storefront discovery flows. If search or recommendations show fewer products than expected, shared catalog assignment is one of the first things to check.

1. Navigate to **Catalog > Shared Catalogs** in the Admin sidebar.
2. You should see a **Default (General)** catalog (Type: Public). This is the public catalog that applies to all customers not assigned to a specific company.
3. Click **Select** on the Default (General) row, then choose **Set Pricing and Structure**.
4. On the "Catalog Structure" page, click **Configure**.
5. **Step 1 — Select Products:** In the "Products in Catalog" panel, check the **Root Catalog** checkbox on the left (it will show "0 of N included"). This selects all products at once. Do not select categories individually — select the root to include everything.
6. Click **Next** to proceed to Step 2 (Pricing). Adjust custom pricing if needed, or leave defaults.
7. Click **Generate Catalog** to save.

> **Note:** After generating, Commerce schedules a background task ("Assign Categories to Shared Catalog") that processes asynchronously. This task can lock indexers (Product Feed, Product Prices Feed, Category Products) for several minutes. Wait for it to complete before reindexing.

### 2.3 Reindex and Flush Cache

After enabling features and assigning products, SSH into your Cloud environment and run:

```bash
bin/magento setup:upgrade
bin/magento indexer:reindex
bin/magento cache:flush
```

**If indexers are locked** (you see "index is locked by another reindex process. Skipping."), the shared catalog background task is still running. Wait a few minutes and try again. If indexers stay stuck in "Processing" / "Suspended" state for more than 10 minutes, force-reset them:

```bash
bin/magento indexer:reset catalog_data_exporter_products catalog_data_exporter_product_prices catalog_product_attribute
bin/magento indexer:reindex
```

Repeat `bin/magento indexer:status` until all relevant indexers show **Ready**.

See [Enable B2B Features](https://experienceleague.adobe.com/docs/commerce-admin/b2b/enable-basic-features.html).

### 2.4 Phase 2 Verification

**Before moving to Phase 3, confirm:**

1. In Admin, go to **Stores > Configuration > General > B2B Features** — the features you enabled should show the expected values
2. In Admin, go to **Customers > Companies** — the menu item should be visible (it only appears when Company is enabled)
3. In Admin, go to **Catalog > Shared Catalogs** — the Default (General) catalog should exist and have products assigned
4. Run `bin/magento indexer:status` — relevant indexers should show **Ready** with **Idle** schedule status. If any show "Processing" or "Suspended", see the reset instructions in [2.3](#23-reindex-and-flush-cache)
5. Check **System > Data Sync** (Data Management section). You should see three cards:

   | Card | Expected Count | What It Means |
   |---|---|---|
   | **Catalog Service** | All SKUs (e.g., 2048) | Syncs every product regardless of visibility or shared catalog assignment |
   | **Product Discovery** | Visible products (e.g., 189) | Only products with "Catalog, Search" visibility **and** assigned to a shared catalog |
   | **Recommendations** | Same as Product Discovery | Uses the same filtering criteria as Product Discovery |

   > **The numbers will differ** and that's expected. Catalog Service is always larger because it includes "Not Visible Individually" variants (simple products behind configurables/bundles). Product Discovery and Recommendations should match each other and should equal the number of "Catalog, Search" visible products assigned to the shared catalog.

> **Stuck?** See [Troubleshooting > Phase 2](#phase-2-b2b-issues).

---

## Phase 3: EDS Storefront and CORS

This phase connects your Commerce backend to an Edge Delivery Services (EDS) storefront. Since the storefront and backend run on **different domains**, you also need to configure CORS so the browser allows cross-domain API calls.

### 3.1 Understand the Compatibility Packages

This project includes two packages that make the Commerce backend APIs work with EDS drop-in components:

- **`adobe-commerce/storefront-compatibility`** — Ensures GraphQL and REST API compatibility with EDS drop-in components for catalog browsing, cart, and checkout.
- **`adobe-commerce/storefront-compatibility-b2b`** — Extends API compatibility to B2B-specific flows (company accounts, shared catalogs, purchase orders, requisition lists).

These are already installed via `composer.json`. No action needed — just be aware they exist.

### 3.2 Connect the EDS Project

The EDS storefront is a **separate repository** from this Commerce Cloud project. You will clone it, configure it to talk to your Commerce backend, and run it locally.

#### Step 1 — Create or Clone the EDS Storefront

1. **Create the storefront** with [Site Creator](https://da.live/app/adobe-commerce/storefront-tools/tools/site-creator/site-creator) when your organization allows it, or manually create a repository from the [Commerce boilerplate](https://github.com/hlxsites/aem-boilerplate-commerce) and install the [AEM Code Sync GitHub App](https://github.com/apps/aem-code-sync).

2. **Clone the EDS storefront repo** into a separate directory (not inside this Commerce Cloud repo):

    ```bash
    git clone https://github.com/<your-org>/aem-boilerplate-commerce.git
    cd aem-boilerplate-commerce
    ```

    > **Note:** This is a completely separate codebase from the Commerce Cloud backend. You'll work in two repos going forward — one for the backend (this project) and one for the storefront.

3. **Find your storefront URL.** Your EDS storefront URL is derived from your GitHub org and repo name:

    | Environment | URL Pattern | Purpose |
    |---|---|---|
    | **Preview** | `https://main--<repo-name>--<github-org>.aem.page` | Only visible to you — use for testing before publishing |
    | **Live** | `https://main--<repo-name>--<github-org>.aem.live` | Public-facing production URL |

    For example, if your GitHub org is `acme-corp` and your repo is `acme-store`, your live URL is `https://main--acme-store--acme-corp.aem.live`.

    > **Forgot your URL?** You can also check the admin status page at `https://admin.hlx.page/status/<github-org>/<repo-name>/main` — the JSON response includes both your preview and live URLs.

#### Step 2 — Configure Storefront Configuration

For production, prefer AEM Configuration Service public config at
`https://admin.hlx.page/config/{org}/sites/{site}/public.json`. For local development and
branch testing, a repository-root `config.json` can override Configuration Service values.
Do not commit `config.json` to `main` if production should resolve from Configuration
Service. See [AEM Admin API docs](https://www.aem.live/docs/admin.html) for authentication
and API reference.

The JSON structure to set under `public.default`:

```json
{
  "public": {
    "default": {
      "commerce-endpoint": "https://<your-commerce-domain>/graphql",
      "headers": {
        "all": {
          "Store": "default"
        },
        "cs": {
          "Magento-Store-Code": "main_website_store",
          "Magento-Store-View-Code": "default",
          "Magento-Website-Code": "base"
        }
      },
      "commerce-b2b-enabled": true,
      "commerce-companies-enabled": true,
      "commerce-assets-enabled": true,
      "analytics": {
        "base-currency-code": "USD",
        "environment": "Testing",
        "environment-id": "{{ENVIRONMENT_ID}}",
        "store-code": "main_website_store",
        "store-id": "main_website_store",
        "store-name": "Default Store View",
        "store-url": "http://<your-commerce-domain>/",
        "store-view-code": "default",
        "store-view-id": "default",
        "store-view-name": "Default Store View",
        "website-code": "base",
        "website-id": "base",
        "website-name": "Main Website"
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

**Key fields to update:**

| Field | What to Set | How to Find It |
|---|---|---|
| `commerce-endpoint` | Your Commerce Cloud GraphQL URL (e.g., `https://master-7rqtwti-xxx.us-a1.magentosite.cloud/graphql`) | Run `magento-cloud url` in your Commerce Cloud project |
| `headers.all.Store` | Your store view code (e.g., `default`) | Admin > **Stores > All Stores** — check the **Code** column |
| `headers.cs.Magento-Store-Code` | Your store code (e.g., `main_website_store`) | Admin > **Stores > All Stores** — the store-level code |
| `headers.cs.Magento-Website-Code` | Your website code (e.g., `base`) | Admin > **Stores > All Stores** — the website-level code |
| `analytics.environment-id` | Your Commerce Cloud environment ID | Commerce Cloud Project Web UI or `magento-cloud environment:info id` |
| `analytics.store-url` | Your Commerce Cloud store URL | Same as the domain in `commerce-endpoint`, with trailing slash |
| `commerce-b2b-enabled` | `true` (since this project uses B2B) | Already set — leave as `true` |
| `commerce-companies-enabled` | `true` (since Company accounts are enabled) | Already set — leave as `true` |
| `plugins.picker.rootCategory` | Your root category ID (usually `"2"`) | Admin > **Catalog > Categories** — the ID of the root category |

> **Why the `Store` header matters:** Every GraphQL request includes this header to tell Commerce which store view to use. If it's missing or wrong, requests may return 403 errors or data from the wrong store view.

> **What are the `cs` headers?** These are additional headers used by Commerce Services (Live Search, Product Recommendations) to identify the correct store context. They are separate from the `all` headers which apply to all API calls.

#### Step 3 — Install Dependencies and Drop-in Components

The EDS storefront uses drop-in components — pre-built UI blocks for product pages, cart, checkout, etc.

1. **Install dependencies:**

    ```bash
    npm install
    ```

2. The boilerplate includes drop-in components for:
   - **Product Details** — PDP with images, pricing, options, add-to-cart
   - **Product List / Search** — category pages and search results (powered by the configured catalog/search services)
   - **Cart** — mini-cart and full cart page
   - **Checkout** — multi-step checkout flow
   - **Authentication** — customer login and account pages

   These are pre-configured in the boilerplate. You can customize them by editing the block code in the `blocks/` directory.

#### Step 4 — Run the EDS Storefront Locally

1. **Start the local development server:**

    ```bash
    npm start
    ```

    This typically starts a local server at `http://localhost:3000`.

2. **Open the storefront** in your browser and navigate to a product page. You should see product data (name, price, images) fetched from your Commerce backend via GraphQL.

3. **If you see CORS errors** in the browser console, proceed to [3.3 Configure CORS](#33-configure-cors) — this is expected when running locally on `localhost`.

> **Tip:** During local development, you may need to add `http://localhost:3000` to the CORS "Allowed Origins" in the Commerce Admin (see [3.3](#33-configure-cors)). Remember to also add your production EDS domain (`https://your-storefront.aem.live`).

See [Create a storefront](https://experienceleague.adobe.com/developer/commerce/storefront/get-started/create-storefront/) and [Storefront configuration](https://experienceleague.adobe.com/developer/commerce/storefront/setup/configuration/commerce-configuration/).

### 3.3 Configure CORS

The EDS storefront runs on a domain like `https://your-storefront.aem.live`, but your Commerce APIs are on `https://your-commerce-domain.com`. Browsers block these cross-domain requests by default. You must configure CORS to allow them.

This template may include [`graycore/magento2-cors`](https://github.com/graycoreio/magento2-cors) for this purpose. If your project does not use that module, configure equivalent CORS headers at the web server, edge, or custom-module layer.

If using `graycore/magento2-cors`, configure it via **Stores > Configuration > General > Web > CORS** in the Admin. Adobe's storefront CORS setup guide lists `GET`, `POST`, and `OPTIONS` plus `Content-Type`, `Authorization`, and `X-Requested-With` as the minimum requirements for PaaS GraphQL requests; include additional request headers, such as `Store`, when your storefront sends them.

| Setting | What to Enter |
|---|---|
| **Allowed Origins** | Your EDS storefront domain (e.g., `https://your-storefront.aem.live`) |
| **Allowed Headers** | `Content-Type, Authorization, X-Requested-With, Store` |
| **Allowed Methods** | `GET, POST, OPTIONS` |
| **Allow Credentials** | `true` |
| **Max Age** | `86400` |

> **Important:** The "Allowed Origins" must be the **exact** EDS domain, including the protocol (`https://`). No trailing slash.

See [graycore/magento2-cors documentation](https://github.com/graycoreio/magento2-cors).

### 3.4 Phase 3 Verification

**Before moving to Phase 4, confirm:**

1. Open your EDS storefront URL in a browser — it should load without errors
2. Navigate to a product detail page — product data (name, price, image) should appear (fetched from Commerce GraphQL)
3. Open browser DevTools > Console — there should be **no** CORS errors (red messages mentioning "Access-Control-Allow-Origin")
4. Open browser DevTools > Network — filter for GraphQL requests and confirm they return `200 OK`, not `403` or `0`

> **Stuck?** See [Troubleshooting > Phase 3](#phase-3-storefront-and-cors-issues).

---

## Phase 4: Adobe Commerce Optimizer (ACO)

This phase connects your Commerce backend to Adobe Commerce Optimizer, which consumes catalog, pricing, and category data for merchandising and storefront discovery.

This template expects the Adobe Commerce Optimizer Connector package (`adobe-commerce/commerce-data-export-aco-adapter`) to be installed. If it is not already in `composer.json`, install it with Composer and deploy it before configuring synchronization.

### 4.1 Configure the Commerce Services Connector

In the Admin, navigate to **Stores > Configuration > Services > Commerce Services Connector** and configure:

- **API Keys**: Add your production and sandbox API key pair
- **Environment ID**: Your Commerce Cloud environment identifier
- **SaaS Data Space**: Select the data space for your environment (production or sandbox)

> **Where do I get these?** Your Adobe account team provides the API keys. The Environment ID is in the Commerce Cloud Project Web UI.

See [Commerce Services Connector](https://experienceleague.adobe.com/docs/commerce/services/connector/overview.html).

### 4.2 Trigger Initial Data Sync

After configuring the connector, trigger the first full sync of your catalog data:

```bash
bin/magento saas:resync --feed=products
bin/magento saas:resync --feed=categories
bin/magento saas:resync --feed=prices
```

After this initial sync, ongoing partial synchronization is handled by cron jobs. This template schedules Commerce cron every minute; verify your own `.magento.app.yaml` before relying on that cadence.

### 4.3 Phase 4 Verification

**Setup is complete when all of the following pass:**

1. Run `bin/magento saas:status` — feeds should show "Syncing" or "Synced" (not "Error" or "Not Configured")
2. Check cron is running: `bin/magento cron:run` should complete without errors
3. Wait a few minutes, then run `bin/magento saas:status` again — feed counts should be increasing

> **Stuck?** See [Troubleshooting > Phase 4](#phase-4-aco-issues).

See:
- [Adobe Commerce Optimizer](https://experienceleague.adobe.com/docs/commerce/optimizer/overview.html)
- [SaaS Data Export](https://experienceleague.adobe.com/docs/commerce/data-export/overview.html)

---

# Reference

The sections below are not part of the setup sequence. Use them as reference when needed.

---

## Repository Structure

```bash
.magento/
        /routes.yaml        # URL routing to the Commerce application
        /services.yaml      # Service definitions (template-specific database, cache, and search services)
.magento.app.yaml           # Application config (PHP runtime, build/deploy hooks, cron)
.magento.env.yaml           # Environment-specific build/deploy variables (create this — see Phase 1)
app/etc/config.php          # Module enable/disable state
auth.json                   # Composer auth (do not commit; use env variable on Cloud)
composer.json               # Dependencies: B2B, ACO adapter, EDS compatibility, CORS
magento-vars.php            # Multi-store routing configuration
php.ini                     # PHP settings (memory limit, opcache, session GC)
m2-hotfixes/                # Quality patches and custom hotfixes
```

-  `.magento/routes.yaml` — redirects `www` to the naked domain and routes HTTP to the `php` application.
-  `.magento/services.yaml` — sets up MySQL 11.4, Valkey 8.0 (cache/session), and OpenSearch 3 (search).
-  `.magento.app.yaml` — defines the application runtime, build/deploy hooks via ECE-Tools, and cron jobs.
-  `composer.json` — fetches Adobe Commerce Enterprise Edition, B2B extension, ACO adapter, EDS compatibility layers, CORS module, and sample data.

## Sample Data

This project includes a full suite of Adobe Commerce sample data modules for development and demo purposes:

- **Catalog**: products, categories, configurable products, bundle products, downloadable products, grouped products
- **CMS**: pages and blocks
- **Customers**: customer accounts and segments
- **Sales**: orders, sales rules, cart price rules
- **B2B**: gift cards, gift registry, MSRP, target rules
- **Theme**: sample theme assets, widgets, swatches

Sample data is installed automatically during `composer install` and deployed via `bin/magento setup:upgrade`.

## Disable a Module on Cloud

In Adobe Commerce Cloud, disable modules through versioned code and deployment rather than making ad hoc changes over SSH in a running container.

If you see this error:

`Command line user does not have read and write permissions on generated directory`

run the workflow in a local or integration environment and deploy the change:

1.  Disable the module:

    ```bash
    php bin/magento module:disable <module-name>
    ```

1.  Refresh Cloud module configuration:

    ```bash
    ./vendor/bin/ece-tools module:refresh
    ```

1.  If `app/etc/config.php` is missing, generate shared config:

    ```bash
    ./vendor/bin/ece-tools config:dump
    ```

1.  Verify module state in `app/etc/config.php` (`'<module-name>' => 0`), then commit and push:

    ```bash
    git add app/etc/config.php
    git commit -m "Disable <module-name>"
    git push origin <branch-name>
    ```

1.  After deployment, verify:

    ```bash
    bin/magento module:status <module-name>
    ```

## Cron Configuration

The default Adobe Commerce cron is configured in this template's `.magento.app.yaml` to run every minute:

```yaml
crons:
    cronrun:
        spec: "* * * * *"
        cmd: "php bin/magento cron:run"
```

This is essential for:
- **B2B features**: purchase order processing, quote expiration, company credit updates
- **SaaS data export**: incremental data synchronization to ACO
- **Indexers**: scheduled index updates
- **Email queue**: transactional email processing

## Useful Commands

```bash
# Check module status
bin/magento module:status

# Reindex all indexers
bin/magento indexer:reindex

# Check indexer status (all should show "Ready")
bin/magento indexer:status

# Reset stuck/suspended indexers (use when indexers are locked for >10 min)
bin/magento indexer:reset catalog_data_exporter_products catalog_data_exporter_product_prices catalog_product_attribute

# Trigger SaaS data export resync
bin/magento saas:resync --feed=products

# Check SaaS export status
bin/magento saas:status

# Flush all caches
bin/magento cache:flush

# ECE-Tools module refresh
./vendor/bin/ece-tools module:refresh

# Run static content deploy (for a specific locale)
bin/magento setup:static-content:deploy en_US

# Compile DI
bin/magento setup:di:compile

# Watch Cloud deployment logs in real-time
magento-cloud activity:log

# SSH into your Cloud environment
magento-cloud ssh
```

## Troubleshooting

### Phase 1: Backend Issues

| Symptom | Cause | Fix |
|---|---|---|
| `composer install` fails with 401 | Auth keys not configured | See [1.1 Clone and Authenticate](#11-clone-and-authenticate) — set `env:COMPOSER_AUTH` or create `auth.json` |
| Deploy fails with "service not found" | `.magento.env.yaml` missing or misconfigured | See [1.2 Create .magento.env.yaml](#12-create-magentoenvyaml) — ensure the file exists in the project root |
| Deploy fails with "unknown service type valkey" | Cloud platform version doesn't support Valkey 8.0 | Check your Cloud project's infrastructure version; Valkey requires a recent platform update |
| Admin page shows 500 error | DI compilation or config issue | SSH in and run `bin/magento setup:upgrade && bin/magento cache:flush` |

### Phase 2: B2B Issues

| Symptom | Cause | Fix |
|---|---|---|
| Only "Enable Company", "Enable Quick Order", and "Enable Requisition List" visible in B2B Features | Company not enabled yet | Set **Enable Company** to **Yes** — the remaining B2B settings (Shared Catalog, B2B Quote, etc.) auto-populate immediately without saving |
| B2B Features menu not visible in Admin at all | B2B module not enabled | Run `bin/magento module:status Magento_B2b` — if disabled, run `bin/magento module:enable Magento_B2b && bin/magento setup:upgrade` |
| "Reindex required" after enabling features | Expected — indexers need to rebuild | Run `bin/magento indexer:reindex` |
| Shared catalog prices not appearing | Shared catalog indexer not run | Run `bin/magento indexer:reindex catalog_product_price` |
| Live Search / Product Discovery shows far fewer products than expected | Products may not be assigned to the expected shared catalog, or associated products/options are missing from the shared catalog | Check **Catalog > Shared Catalogs > Default (General) > Set Pricing and Structure** and confirm the relevant products and associated products/options are assigned |
| "Shared Catalogs" not visible under Catalog menu | Shared Catalog feature not enabled | Go to **Stores > Configuration > General > B2B Features** and set **Enable Shared Catalog** to **Yes** (requires Enable Company = Yes first) |
| Indexers show "locked by another reindex process. Skipping." | Shared catalog background task is still processing | Wait a few minutes and reindex again — the background "Assign Categories to Shared Catalog" task locks Product Feed, Product Prices Feed, and Category Products indexers while it runs |
| Indexers stuck in "Processing" / "Suspended" for >10 minutes | Stale lock from a crashed or timed-out process | Reset the stuck indexers: `bin/magento indexer:reset catalog_data_exporter_products catalog_data_exporter_product_prices catalog_product_attribute` then `bin/magento indexer:reindex` |
| Product Discovery count didn't increase after assigning products to shared catalog | Indexers not yet rebuilt after assignment | Ensure all indexers show "Ready" (especially Product Feed and Product Prices Feed), then wait 1-2 minutes for SaaS sync. Refresh the Data Sync page |

### Phase 3: Storefront and CORS Issues

| Symptom | Cause | Fix |
|---|---|---|
| Browser console shows "Access-Control-Allow-Origin" errors | CORS not configured or wrong origin | In Admin, go to **Stores > Config > General > Web > CORS** and verify the Allowed Origins matches your exact EDS domain (include `https://`, no trailing slash) |
| GraphQL requests return 403 | Missing `Store` header in requests | Ensure your EDS project sends the `Store` header with the correct store view code |
| EDS page loads but no product data | Wrong Commerce backend URL in EDS config | Verify the backend URL in your EDS project points to this Commerce Cloud instance |
| CORS works on GET but fails on POST | `OPTIONS` method not allowed | Ensure "Allowed Methods" includes `OPTIONS` (preflight requests use this) |

### Phase 4: ACO Issues

| Symptom | Cause | Fix |
|---|---|---|
| `saas:resync` fails with "not configured" | Commerce Services Connector not set up | In Admin, go to **Stores > Config > Services > Commerce Services Connector** and add your API keys, environment ID, and SaaS data space |
| Feed status shows "Error" | API key mismatch or network issue | Verify API keys are correct; check if your Cloud environment can reach Adobe SaaS endpoints |
| Feeds stuck at 0 items | Cron not running | Run `bin/magento cron:run` manually, then check `bin/magento saas:status` again. If cron keeps failing, check `var/log/cron.log` |
| Feeds syncing but counts aren't increasing | No products in catalog | Import or create products first, then resync with `bin/magento saas:resync --feed=products` |

## Developer Documentation

- [Adobe Commerce on Cloud infrastructure guide](https://experienceleague.adobe.com/en/docs/commerce-cloud-service/user-guide/overview)
- [B2B for Adobe Commerce](https://experienceleague.adobe.com/en/docs/commerce-admin/b2b/introduction)
- [Commerce Storefront backend options](https://experienceleague.adobe.com/developer/commerce/storefront/get-started/backends/)
- [Storefront Compatibility package installation](https://experienceleague.adobe.com/developer/commerce/storefront/setup/configuration/storefront-compatibility/install/)
- [Adobe Commerce Optimizer Connector](https://experienceleague.adobe.com/en/docs/commerce/aco-optimizer-connector/overview)
- [SaaS Data Export](https://experienceleague.adobe.com/en/docs/commerce/saas-data-export/overview)
- [Commerce Services Connector](https://experienceleague.adobe.com/en/docs/commerce-merchant-services/user-guides/integration-services/saas)
- [CORS Module (graycore)](https://github.com/graycoreio/magento2-cors)

## Official references & attribution

- [Commerce Storefront backend options](https://experienceleague.adobe.com/developer/commerce/storefront/get-started/backends/) (retrieved 2026-05-14). Used to verify PaaS prerequisites, Adobe Commerce v2.4.7+ requirement, ACO licensing for PaaS drop-in usage, and required storefront packages/services.
- [Storefront Compatibility Package Installation](https://experienceleague.adobe.com/developer/commerce/storefront/setup/configuration/storefront-compatibility/install/) (retrieved 2026-05-14). Used to verify PaaS installation flow and current 2.4.7/2.4.8 package examples.
- [Adobe Commerce on Cloud infrastructure overview](https://experienceleague.adobe.com/en/docs/commerce-cloud-service/user-guide/overview) (retrieved 2026-05-14). Used to verify Cloud infrastructure framing.
- [Install the Adobe Commerce B2B extension](https://experienceleague.adobe.com/en/docs/commerce-admin/b2b/install) (retrieved 2026-05-14). Used to verify `magento/extension-b2b`, cloud installation flow, B2B message consumers, and PHP compatibility warnings.
- [Enable B2B features](https://experienceleague.adobe.com/en/docs/commerce-admin/b2b/enable-basic-features) (retrieved 2026-05-14). Used to verify Company, Shared Catalog, B2B Quote, Quick Order, Requisition List, purchase orders, payment, and shipping feature settings.
- [Add products to a shared catalog](https://experienceleague.adobe.com/en/docs/commerce-admin/b2b/shared-catalogs/define/catalog-shared-product-add) and [Set shared catalog pricing and structure](https://experienceleague.adobe.com/en/docs/commerce-admin/b2b/shared-catalogs/define/catalog-shared-pricing-structure) (retrieved 2026-05-14). Used to verify shared catalog product assignment flow and associated-product requirements.
- [Create a storefront](https://experienceleague.adobe.com/developer/commerce/storefront/get-started/create-storefront/) and [Storefront configuration](https://experienceleague.adobe.com/developer/commerce/storefront/setup/configuration/commerce-configuration/) (retrieved 2026-05-14). Used to verify Site Creator, manual GitHub/Code Sync flow, Configuration Service, `config.json` precedence, and storefront config fields.
- [CORS Setup](https://experienceleague.adobe.com/developer/commerce/storefront/setup/configuration/cors-setup/) (retrieved 2026-05-14). Used to verify PaaS CORS requirements for storefront GraphQL requests.
- [Adobe Commerce Optimizer Connector](https://experienceleague.adobe.com/en/docs/commerce/aco-optimizer-connector/overview) (retrieved 2026-05-14). Used to verify the `adobe-commerce/commerce-data-export-aco-adapter` package, connector architecture, and targeted resync commands.
- [SaaS Data Export Guide](https://experienceleague.adobe.com/en/docs/commerce/saas-data-export/overview) and [Data Management Dashboard](https://experienceleague.adobe.com/en/docs/commerce-admin/systems/data-transfer/data-sync/data-dashboard) (retrieved 2026-05-14). Used to verify SaaS data export feed concepts, manual/cron synchronization, and sync status surfaces.
- [Commerce Services Connector](https://experienceleague.adobe.com/en/docs/commerce-merchant-services/user-guides/integration-services/saas) (retrieved 2026-05-14). Used to verify connector configuration concepts for Commerce services.
- [Cloud cron property](https://experienceleague.adobe.com/en/docs/commerce-cloud-service/user-guide/configure/app/properties/crons-property) and [global deployment variables](https://experienceleague.adobe.com/en/docs/commerce-cloud-service/user-guide/configure/env/stage/variables-global) (retrieved 2026-05-14). Used to verify Cloud cron and `.magento.env.yaml` configuration concepts.

## License

Each Adobe Commerce source file included in this distribution is licensed under the OSL-3.0 license.

Please see [LICENSE.txt](https://github.com/magento/magento-cloud/blob/master/LICENSE.txt) for the full text of the [Open Software License v. 3.0 (OSL-3.0)](http://opensource.org/licenses/osl-3.0.php).
