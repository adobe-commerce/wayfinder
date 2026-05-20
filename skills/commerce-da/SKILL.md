---
name: commerce-da
description: >
  Helps software engineers and content authors work with Document Authoring (DA) on Adobe
  Commerce EDS projects. Use this skill for any question about: creating or editing content
  pages in DA (da.live); adding, placing, or configuring blocks on a page; page metadata and
  section metadata; bulk metadata; navigation (nav.docx); placeholders; the preview and publish
  workflow (Sidekick, aem.page, aem.live); DA organization and site setup; DA access and
  permissions (IMS org switcher, "Not permitted" errors, ACL sheet, user groups); DA
  administration; or any question where the primary concern is content authoring workflow
  rather than storefront code.
---

# Commerce DA Skill

## Source authority

DA documentation is split across three locations. When they conflict, the domain owner wins:

| Domain | Authoritative source | Entry point |
|---|---|---|
| DA platform — authoring interface, DA org/site setup, DA-specific permissions/ACL | **docs.da.live** | `https://da.live/docs` |
| EDS platform — blocks, CDN, publish workflow, Admin API | **aem.live** | `https://www.aem.live/llms.txt` |
| Commerce-specific content authoring (blocks, merchants) | **ExL Storefront** | `https://experienceleague.adobe.com/developer/commerce/storefront/llms.txt` |

Some DA questions span both docs.da.live and aem.live (e.g. "how do I publish from DA to my
EDS site"). Fetching from both is correct in those cases.

---

## Fetch strategy

**docs.da.live** (primary for DA-platform topics)

No `llms.txt`. Fetch `https://da.live/docs` as the discovery hub to find the relevant
DA-specific pages, then fetch those pages. Use for: DA authoring interface, DA org/site
setup, DA permissions/ACL.

**aem.live sections** (for EDS-general topics that overlap with DA)

| Topic | URL |
|---|---|
| DA authoring guide (blocks, sections, publishing) | `https://www.aem.live/docs/authoring-guide.md` |
| Authoring overview | `https://www.aem.live/docs/authoring.md` |
| Bulk metadata | `https://www.aem.live/docs/bulk-metadata.md` |
| Placeholders | `https://www.aem.live/docs/placeholders.md` |
| Sidekick (preview/publish browser extension) | `https://www.aem.live/docs/sidekick.md` |
| Block markup and structure (for understanding block authoring) | `https://www.aem.live/developer/markup-sections-blocks.md` |
| Admin API (content source config, sync) | `https://www.aem.live/docs/admin.html` |

For the full aem.live index: `https://www.aem.live/llms.txt`

**ExL Storefront section** (for Commerce-specific content authoring)

| Topic | URL |
|---|---|
| DA content authoring for Commerce (pages, blocks, section metadata, page metadata) | `https://experienceleague.adobe.com/developer/commerce/storefront/_llms-txt/merchants-authoring.txt` |

---

## Reading the user's repo

DA content lives in the DA system (`da.live`), not in the code repo. But the code repo
defines which blocks are available and how they render.

When filesystem access is available, check:
- `blocks/` — available blocks and their expected DA table structure
- `fstab.yaml` — confirms which DA org/site is the content source

If filesystem access is not available, ask the user which DA org and site they are working with.

---

## Workflow

1. **Identify the source** — DA-platform topics (authoring interface, permissions, org/site setup) → start with `docs.da.live`. EDS-general topics (blocks, publish workflow, Admin API) → start with `aem.live`. Many DA questions need both.
2. **Check the repo** (if available) — read `blocks/` to understand which blocks exist and their DA table structure. Read `fstab.yaml` to confirm the DA org/site.
3. **Fetch** — retrieve the relevant section. For `docs.da.live`, start from `https://da.live/docs` to discover the right page, then fetch it.
4. **If the first fetch doesn't answer** — fetch from the other source; DA knowledge bridges both locations.
5. **Synthesize** — explain the workflow or concept clearly. Cite the doc URL.

Common starting points by scenario:

| Scenario | Start here |
|---|---|
| "Not permitted" / access error | `da.live/docs` (discovery) + `admin.html` (aem.live) |
| Creating or editing a content page | `authoring-guide.md` (aem.live) + `merchants-authoring.txt` (ExL) |
| Preview vs. publish / Sidekick | `sidekick.md` (aem.live) |
| Adding a block to a page | Read `blocks/` in repo, then `markup-sections-blocks.md` (aem.live) |
| Page metadata or section metadata | `authoring-guide.md` + `merchants-authoring.txt` |
| Bulk metadata | `bulk-metadata.md` (aem.live) |
| Adding a team member / permissions | `da.live/docs` (discovery) + `admin.html` (aem.live) |

---

## Terminology

| Use | Not |
|---|---|
| Document Authoring (DA) | just "DA" on first mention without expanding |
| Adobe Commerce | Magento |
