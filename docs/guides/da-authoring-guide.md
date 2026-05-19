# Document Authoring (DA) Guide for Adobe Commerce EDS Storefronts

## Overview

Document Authoring (DA) is Adobe's authoring interface for creating and managing Edge Delivery Services content at [da.live](https://da.live). Its document editor intentionally resembles common word processors, while adding DA-specific patterns for blocks, tables, apps, preview, and publish.

Your project's content usually lives under: `https://da.live/#/{org}/{site}/`

To edit a specific page, use: `https://da.live/#/edit/{org}/{site}/{page-name}`

---

## Core Concepts

### Pages

Every content page on your EDS site corresponds to a document in DA. For example:
- Homepage = `index` document
- About page = `about` document

### Sections

Sections are the top-level content divisions on a page. They are separated by **horizontal rules** (section dividers).

To create a section divider, type `---` (three hyphens) on a new line, or insert a horizontal rule from the toolbar.

```
[Section 1 content here]
---
[Section 2 content here]
---
[Section 3 content here]
```

Each section becomes a `<div class="section">` on the rendered page.

### Blocks

Blocks are represented as tables in DA documents. They add structured content and special functionality to your site, such as commerce product lists, carousels, accordions, or project-specific components.

**A block is a table where the first row contains the block name.** For Commerce storefront blocks, use the block name documented by Adobe, usually in `kebab-case`.

---

## Working with the DA Editor

### Text Formatting

Working with text in DA follows standard word-processor conventions:

| Format | How to Apply |
|--------|-------------|
| **Heading 1-6** | Select text and choose heading level from the format dropdown |
| **Bold** | Select text and press `Cmd/Ctrl + B` |
| **Italic** | Select text and press `Cmd/Ctrl + I` |
| **Underline** | Select text and press `Cmd/Ctrl + U` |
| **Lists** | Use the toolbar buttons for ordered/unordered lists |
| **Links** | Select text and press `Cmd/Ctrl + K` or use the link button |

### Navigation

- Use the **breadcrumb** in the title area to move up one level in the content hierarchy
- Use `Cmd/Ctrl + Click` on the breadcrumb to open in a new tab
- Use the browser's back button as an alternative

### Slash Menu

If your DA editor configuration exposes a slash menu, type `/` on a new line to open quick insert options. Treat available options as project- and editor-version-specific.

### Block Library

DA can expose project block libraries and plugins that help authors insert preconfigured blocks. Availability depends on how the project is configured.

---

## Creating Blocks

### Basic Block Structure

Every block follows the same structure:

1. Insert a **table** (use the toolbar table/grid button or the block library)
2. The **first row** must be a single merged cell containing the **block name**
3. Subsequent rows contain the block's **content or configuration**

### Key-Value Block (Configuration Block)

Many Commerce blocks use a key-value configuration format with 2 columns:

| Block Name |  |
|---|---|
| property1 | value1 |
| property2 | value2 |

**Step-by-step:**

1. Click the **block button** (or `+` button) in the toolbar to insert a table
2. Create a table with **2 columns**
3. In the **first row**, type the documented block name (e.g., `product-recommendations`)
4. **Merge the first row cells**: Select both cells in the first row, right-click (or use the table menu) and choose **Merge cells**
5. In each subsequent row, enter a **property name** in the left cell and its **value** in the right cell

### Content Block

Some blocks contain rich content rather than key-value pairs:

| Columns |  |
|---|---|
| Text content for left column | Text content for right column |
| More content | More content |

### Block Variants

Block variants are specified in parentheses after the block name:

| Columns (highlight) |  |
|---|---|
| content | content |

This passes the variant name as a CSS class to the rendered block.

### Edit Table Button

The toolbar is **contextually aware**. When you click into a table, the add block button changes to an **edit table** button, allowing you to modify the table structure (add/remove rows and columns, merge cells).

---

## Section Metadata

**Section metadata** is a special table that applies configuration to the entire section it belongs to. Place it in the section whose styling or layout you want to control.

| section-metadata |  |
|---|---|
| style | style-name |

This adds a CSS class to the section's `<div>`, enabling section-specific styling.

**Example:** Adding `style: hot-sellers` results in `<div class="section hot-sellers">` in the rendered HTML.

---

## Page Metadata

**Metadata** is a special table that defines page-level properties like title, description, social sharing, SEO, and caching settings.

| metadata |  |
|---|---|
| title | Page Title |
| description | Page description for SEO |
| image | /path/to/image.png |
| json-ld | { "type": "Product", "name": "Product Name", ... } |

---

## Commerce Block Examples

### Product Recommendations Block

Displays product recommendation units configured in Adobe Commerce Optimizer.

| product-recommendations |  |
|---|---|
| recId | your-recommendation-unit-id |

**Properties:**
- `recId` (required) — The Recommendation ID for the unit to display
- `currentSku` — Current product SKU for recommendation context. Adobe's Commerce storefront docs say PDP pages only require `recId`; other pages require both `recId` and `currentSku`.

### Product List Page Block

Displays a searchable, filterable product listing.

| product-list-page |  |
|---|---|
| categoryPath | category/url/path |

### Hero Block

| hero |  |
|---|---|
| ![Hero image](/path/to/image.png) | **Hero Title** Hero description text [Call to Action](https://link) |

### Carousel Block

| carousel |  |
|---|---|
| ![Slide 1](/path/to/slide1.png) |
| ![Slide 2](/path/to/slide2.png) |

---

## Publishing Workflow

### Preview

After editing a document, use the **Preview** function to see how it will look on the EDS site. The preview URL follows the pattern:

`https://main--{site}--{org}.aem.page/{path}`

### Publish

Once you're satisfied with the preview, **Publish** the document to make it live:

`https://main--{site}--{org}.aem.live/{path}`

### Bulk Operations

For bulk workflows, use [DA's bulk app](https://da.live/apps/bulk). The [Traverse app](https://da.live/apps/traverse) can crawl a content tree and copy page URLs for use in bulk operations.

---

## Complete Page Example

Below is an example of a full homepage document structure:

```
## Welcome to Our Store
Discover amazing products at great prices.

[Shop Now](/products)
---
## Hot Sellers
Here is what's trending on Luma right now

| product-recommendations   |                              |
|-------------------------|------------------------------|
| recId                   | abc123-def456-ghi789         |

| section-metadata         |                              |
|-------------------------|------------------------------|
| style                   | hot-sellers                  |
---
| metadata                 |                              |
|-------------------------|------------------------------|
| title                   | Home - My Store              |
| description             | Shop the best products here  |
```

---

## Additional Resources

- [DA Editor Documentation](https://docs.da.live/)
- [EDS Authoring Guide](https://www.aem.live/docs/authoring)
- [DA Editing Documents](https://docs.da.live/authors/guides/editing-docs)
- [Blocks and Autoblocks](https://experienceleague.adobe.com/en/docs/experience-manager-learn/sites/document-authoring/blocks-and-autoblocks)
- [Commerce Content & Commerce Blocks](https://experienceleague.adobe.com/developer/commerce/storefront/merchants/quick-start/content-commerce-blocks/)

## Official references & attribution

- [DA Editing Documents](https://docs.da.live/authors/guides/editing-docs) (retrieved 2026-05-14). Used to verify DA editor navigation, contextual menus, text editing guidance, and the statement that blocks are represented as tables with a title row.
- [AEM Authoring and Publishing Content](https://www.aem.live/docs/authoring) (retrieved 2026-05-14). Used to verify section dividers, block table structure, block variants, metadata, and preview/publish workflow.
- [Commerce Storefront Merchants and Authoring](https://experienceleague.adobe.com/developer/commerce/storefront/_llms-txt/merchants-authoring.txt) (retrieved 2026-05-14). Used to verify Commerce block table naming, `product-recommendations` properties, section metadata, page metadata, and authoring links.
- [Commerce Storefront Blocks Reference](https://experienceleague.adobe.com/developer/commerce/storefront/_llms-txt/blocks-reference.txt) (retrieved 2026-05-14). Used to verify Product List Page and Product Recommendations block purposes.
- [DA Traverse App Guide](https://docs.da.live/authors/guides/apps/content-tree) (retrieved 2026-05-14). Used to verify content-tree traversal and bulk-operation support wording.
