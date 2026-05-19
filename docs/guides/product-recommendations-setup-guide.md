# Product Recommendations Setup Guide

Guide for adding product recommendations to your EDS storefront using Adobe Commerce Optimizer (ACO).

> **Prerequisite**: Complete the [EDS Storefront + ACO Setup Guide](aco-storefront-setup-guide.md) first. Your storefront must be connected to ACO with working catalog, search, and pricing before adding recommendations.

---

## Table of Contents

1. [How Recommendations Work](#1-how-recommendations-work)
2. [Create a Recommendation Unit in ACO](#2-create-a-recommendation-unit-in-aco)
3. [Add the Block in DA](#3-add-the-block-in-da)
4. [Grid Layout CSS (Optional)](#4-grid-layout-css-optional)
5. [Recommendation Types](#5-recommendation-types)
6. [Block Internals](#6-block-internals)
7. [Troubleshooting](#7-troubleshooting)

---

## 1. How Recommendations Work

The `product-recommendations` block (`blocks/product-recommendations/product-recommendations.js`):

1. Reads `recid` and `currentsku` from the block config (DA table)
2. Initializes the `@dropins/storefront-recommendations` drop-in via `scripts/initializers/recommendations.js`
3. The drop-in uses `CS_FETCH_GRAPHQL` (the ACO endpoint) with ACO headers (`AC-View-ID`, `AC-Price-Book-ID`)
4. Renders a `ProductList` component with slots for:
   - **Footer**: Add to Cart button (simple products) or Select Options link (configurable products), plus Wishlist toggle
   - **Thumbnail**: Product image with link to PDP, supports AEM Assets
5. On mobile, uses `IntersectionObserver` for lazy loading — the recommendation only fetches data when the section scrolls into view
6. Listens to `adobeDataLayer` changes (product context, category, page type, cart) and reloads when significant context changes

### Initialization Chain

```
blocks/product-recommendations/product-recommendations.js
  └── imports scripts/initializers/recommendations.js
        └── sets CS_FETCH_GRAPHQL as the endpoint
        └── calls initializers.mountImmediately(initialize, { langDefinitions })
```

### Key Files

| File | Purpose |
|---|---|
| `blocks/product-recommendations/product-recommendations.js` | Block decorator — renders ProductList with slots |
| `blocks/product-recommendations/product-recommendations.css` | Block styles |
| `scripts/initializers/recommendations.js` | Drop-in initialization, binds to `CS_FETCH_GRAPHQL` |
| `scripts/__dropins__/storefront-recommendations/` | Drop-in source (installed via npm) |

---

## 2. Create a Recommendation Unit in ACO

1. In the ACO application, go to **Merchandising > Recommendations**
2. Select the **Catalog View** where the recommendation should be available
3. Click **Create recommendation**
4. Configure:
   - **Name**: Internal identifier (e.g., "Homepage Hot Sellers")
   - **Recommendation Type**: Choose based on your use case (see [Section 5](#5-recommendation-types))
   - **Storefront Display Label**: Label visible to shoppers above the recommended products
   - **Number of Products**: e.g., 8 for a 4x2 grid
   - **Filters**: Optional product filters
5. Click **Activate**
6. Select the recommendation, click the **info icon**, and **copy the Recommendation ID** (`recId`)

> **Reference**: [Create and Manage Recommendations](https://experienceleague.adobe.com/en/docs/commerce/optimizer/merchandising/recommendations/create)

---

## 3. Add the Block in DA

Edit your page in DA (`https://da.live/#/edit/<org>/<repo>/<page>`).

### Basic Setup

Insert a table with a merged header row containing the block name, and a data row with the `recId`:

| product-recommendations |  |
|---|---|
| **recId** | `<paste-your-rec-id>` |

### On a PDP (Product Detail Page)

On PDP template pages, Adobe's Commerce authoring docs say only `recId` is required. The boilerplate block listens for product context changes in `adobeDataLayer` and uses the current product SKU when it is available.

### On a Non-PDP Page (Homepage, Category Page, etc.)

On non-PDP pages, Adobe's Commerce authoring docs say to provide both `recId` and `currentSku` because there is no current PDP product context:

| product-recommendations |  |
|---|---|
| **recId** | `<your-rec-id>` |
| **currentSku** | `<product-sku>` |

For broad, non-product-specific units such as popularity-based recommendations, the SKU may not materially change the result, but keep the table shape aligned with Adobe's documented block configuration.

### Full Section Example (Homepage)

```
---
## Hot Sellers
Here is what's trending right now

| product-recommendations |          |
|-------------------------|----------|
| recId                   | <rec-id> |

| section-metadata |             |
|------------------|-------------|
| style            | hot-sellers |
---
```

The `section-metadata` table with `style: hot-sellers` adds the CSS class `hot-sellers` to the section wrapper, enabling custom grid styling.

---

## 4. Grid Layout CSS (Optional)

The boilerplate block's default CSS renders recommendations as a horizontal scrollable row. To display products in a grid layout, add CSS targeting a section style class and verify the selectors against the version of `blocks/product-recommendations/product-recommendations.css` in your storefront.

Add to `blocks/product-recommendations/product-recommendations.css`:

```css
/* Grid layout for hot-sellers section */
.section.hot-sellers .product-recommendations .scrollable {
  overflow-x: visible;
}

.section.hot-sellers .product-recommendations .product-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 2rem;
}

.section.hot-sellers .product-recommendations .product-grid picture {
  width: 100%;
}

@media (max-width: 900px) {
  .section.hot-sellers .product-recommendations .product-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
```

Then in DA, add section metadata after the product recommendations block:

| section-metadata |  |
|---|---|
| **style** | `hot-sellers` |

You can create different section styles for different recommendation placements (e.g., `you-may-also-like`, `recently-viewed`).

---

## 5. Recommendation Types

| Type | Description | Requires Context |
|---|---|---|
| **Viewed this, viewed that** | Products often viewed by shoppers who viewed the current product | Yes (`currentSku`) |
| **Viewed this, bought that** | Products often bought by shoppers who viewed the current product | Yes (`currentSku`) |
| **Bought this, bought that** | Products often bought with the current product | Yes (`currentSku`) |
| **Recommended for you** | Personalized recommendations for the shopper | User history |
| **Most Viewed** | Popular products by views | No product SKU context |
| **Most Purchased** | Popular products by purchases | No product SKU context |
| **Most Added to Cart** | Products frequently added to cart | No product SKU context |
| **Trending** | Products with recent engagement momentum | No product SKU context |
| **View to Purchase Conversion** | Products with strong view-to-purchase conversion | No product SKU context |
| **View to Cart Conversion** | Products with strong view-to-cart conversion | No product SKU context |
| **Recently Viewed** | Products the current user has recently viewed | User view history |

The block automatically reads view history and purchase history from `localStorage` (keyed by store view code) and passes them to the drop-in:

```js
context.userViewHistory = getProductViewHistory(storeViewCode);
context.userPurchaseHistory = getPurchaseHistory(storeViewCode);
```

---

## 6. Block Internals

### Configuration Reading

The block uses `readBlockConfig(block)` to extract key-value pairs from the DA table:

```js
const { currentsku, recid } = readBlockConfig(block);
```

The boilerplate `readBlockConfig(block)` helper normalizes keys; in the current product recommendations block, `recId` is read as `recid` and `currentSku` is read as `currentsku`.

### Slots

The block customizes two slots in the `ProductList` component:

**Footer slot** — renders per product:
- **Simple products**: "Add to Cart" button that calls `cartApi.addProductsToCart()`
- **Configurable products**: "Select Options" link to the PDP
- **Wishlist toggle**: heart icon for adding/removing from wishlist

**Thumbnail slot** — renders per product:
- Product image wrapped in an `<a>` link to the PDP
- Supports AEM Assets via `tryRenderAemAssetsImage()`

### Reload Behavior

The block listens for changes to the Adobe Client Data Layer and reloads recommendations when:
- `productContext.sku` changes (navigating between PDPs)
- `categoryContext.name` changes
- `pageContext.pageType` changes
- `shoppingCartContext` changes

A 300ms debounce prevents excessive API calls during rapid changes.

### Mobile Lazy Loading

On mobile (`max-width: 900px`), the block uses `IntersectionObserver` on the section element. Recommendations are only fetched when the section scrolls into the viewport.

---

## 7. Troubleshooting

### Recommendations Not Rendering

**Check**:
1. Verify the `recId` is correct — copy it directly from ACO
2. Verify the recommendation unit is **Activated** in ACO (not Draft)
3. Check DevTools Network for the recommendations GraphQL request and inspect the response
4. Ensure the `@dropins/storefront-recommendations` package is installed — `npm install` should have run `install:dropins` via postinstall automatically; if `scripts/__dropins__/storefront-recommendations/` is missing, run `npm run install:dropins` manually

### Recommendations Show but No Prices

This is the same issue as catalog pricing. See the [ACO Setup Guide - Troubleshooting](aco-storefront-setup-guide.md#12-troubleshooting) section on "$0.00 prices".

### "Recently Viewed" Shows No Products

The "Recently Viewed" type relies on `localStorage` data stored by the PDP page. The user must have visited at least one product detail page for view history to exist.

Check localStorage:
```js
// In DevTools Console
localStorage.getItem('default:productViewHistory')
```

### Recommendations Not Updating After Context Change

The block debounces reload requests by 300ms. If recommendations still don't update:
1. Check that `window.adobeDataLayer` is initialized (the block registers listeners on it)
2. Verify the data layer events are firing: DevTools Console > filter for `adobeDataLayer`

### Slot Customization Limitations

The default block renders **image, name, price, Add to Cart, and Wishlist**. The following require custom slot implementations:
- Star ratings / reviews
- Size swatches (XS, S, M, L, XL)
- Color swatches
- Custom badges (e.g., "New", "Sale")

These would require modifying the `ProductList` slots in `product-recommendations.js` to fetch and render additional product attributes.

## Official references & attribution

- [Commerce Storefront Product Recommendations setup](https://experienceleague.adobe.com/developer/commerce/storefront/_llms-txt/merchants-authoring.txt) (retrieved 2026-05-14). Used to verify the `product-recommendations` block table, `recId`, `currentSku`, PDP versus non-PDP guidance, and DA authoring workflow.
- [Adobe Commerce Optimizer Create and Manage Recommendations](https://experienceleague.adobe.com/en/docs/commerce/optimizer/merchandising/recommendations/create) (retrieved 2026-05-14). Used to verify ACO recommendation creation steps, catalog view selection, recommendation ID lookup, activation, and recommendation type names.
- [Recommendations Quick Start](https://experienceleague.adobe.com/developer/commerce/storefront/dropins/recommendations/quick-start/) (retrieved 2026-05-14). Used to verify the package name, initializer import, `ProductList` container, and provider-render pattern.
- [ProductList container](https://experienceleague.adobe.com/developer/commerce/storefront/dropins/recommendations/containers/product-list/) (retrieved 2026-05-14). Used to verify `recId`, `currentSku`, `cartSkus`, user history props, `routeProduct`, and supported slots.
- [Recommendations Slots](https://experienceleague.adobe.com/developer/commerce/storefront/dropins/recommendations/slots/) (retrieved 2026-05-14). Used to verify `ProductList` slots, including `Heading`, `Footer`, `Title`, `Sku`, `Price`, and `Thumbnail`.
- [Recommendations Functions](https://experienceleague.adobe.com/developer/commerce/storefront/dropins/recommendations/functions/) (retrieved 2026-05-14). Used to verify recommendation fetch parameters and `publishRecsItemAddToCartClick`.
- [aem-boilerplate-commerce `product-recommendations.js`](https://raw.githubusercontent.com/hlxsites/aem-boilerplate-commerce/main/blocks/product-recommendations/product-recommendations.js) and [`recommendations.js`](https://raw.githubusercontent.com/hlxsites/aem-boilerplate-commerce/main/scripts/initializers/recommendations.js) (retrieved 2026-05-14). Used to verify current boilerplate implementation details including `readBlockConfig`, local storage history, `adobeDataLayer` listeners, lazy loading, debounce behavior, custom slots, and use of `CS_FETCH_GRAPHQL`.
