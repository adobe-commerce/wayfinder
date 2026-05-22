# Document Authoring (DA) — Agent Reference

> Load this file when the question involves Document Authoring or da.live: creating or editing content in DA, DA organization and site setup, permissions ("Not permitted", ACL sheet, user groups), blocks and pages in DA, DA administration, preview/publish workflow with DA, or author-facing guides that explicitly reference Document Authoring rather than Universal Editor-only AEM authoring.

## Entry points

- [Document Authoring documentation](https://docs.da.live/)

## Navigate deeper

No `llms.txt`. Fetch `https://docs.da.live/sitemap.xml` to discover all available DA pages, then fetch the relevant ones. Many DA questions also need [AEM / EDS](./aem-eds.md) content (blocks, publish workflow, Admin API) — fetch from both when the question bridges them.

## Known starting points

Verify via sitemap if any fail:

| Topic | URL |
| --- | --- |
| Permissions and ACL sheet (email, user groups) | `https://docs.da.live/administrators/guides/permissions` |
| Access control reference (developer perspective) | `https://docs.da.live/developers/reference/access-control` |
| Site configuration (org-level and site-level configs) | `https://docs.da.live/administrators/guides/configs` |
| Content editing guide for authors | `https://docs.da.live/authors/guides/editing-docs` |
| Administrator guides hub | `https://docs.da.live/administrators/guides` |
| Live preview reference | `https://docs.da.live/authors/reference/live-preview` |

## Site-scoped fallback search

```
site:docs.da.live <topic>
site:www.aem.live <topic>
```

## Also check

- **[AEM / EDS](./aem-eds.md)** for Sidekick (preview/publish browser extension), EDS block markup, CDN, and Admin API topics — these are EDS-level features DA relies on but doesn't document itself.
- **[Adobe Commerce Storefront](./storefront.md)** for commerce-specific blocks, drop-in authoring, and storefront content patterns.
