---
name: commerce-troubleshoot
description: >
  Helps software engineers debug and troubleshoot Adobe Commerce EDS storefront issues.
  Use this skill whenever someone reports a problem with their Commerce storefront, such as:
  products showing $0.00 prices; search returning no results; a 418 Configuration Error page;
  DA content authoring access denied or "Not permitted" in da.live; CDN sync not updating
  files; config changes not taking effect; cart or checkout errors; CORS errors in browser
  DevTools; GraphQL requests failing or going to the wrong endpoint; drop-ins not loading;
  or any other runtime or configuration error on an EDS Commerce storefront. Also use when
  the user asks "why isn't X working" or "how do I debug Y" for any Commerce storefront
  component.
---

# Adobe Commerce Storefront Troubleshooting Skill

You are helping a software engineer debug an issue with an EDS Commerce storefront.

## Terminology

| Use This | Not This |
|---|---|
| **Adobe Commerce** | ~~Magento~~ |
| **Storefront Configuration** | ~~config.json~~ |

---

## Source Authority

When sources conflict, the domain owner is authoritative:

| Domain | Authoritative Source | URL |
|---|---|---|
| EDS platform — Code Sync, Admin API, CDN, publishing | **aem.live** | `https://www.aem.live/llms.txt` |
| Document Authoring (DA) — platform, access, features | **aem.live** | `https://www.aem.live/llms.txt` |
| Storefront drop-ins, blocks, configuration | **Storefront ExL** | `https://experienceleague.adobe.com/developer/commerce/storefront/llms.txt` |
| Commerce backend, B2B, GraphQL schema | **Commerce ExL** | `https://experienceleague.adobe.com/en/docs/commerce` |

---

## Fetch Strategy

| Topic | Fetch This URL |
|---|---|
| Known storefront issues and FAQs | `https://experienceleague.adobe.com/developer/commerce/storefront/_llms-txt/troubleshooting.txt` |
| Storefront Configuration keys, header details | `https://experienceleague.adobe.com/developer/commerce/storefront/_llms-txt/setup-reference.txt` |
| Drop-in APIs and container behavior | `https://experienceleague.adobe.com/developer/commerce/storefront/_llms-txt/dropins-reference.txt` |
| EDS platform (Code Sync, Admin API, CDN) | `https://www.aem.live/llms.txt` then follow section links |

---

## Diagnostic Approach

Identify the symptom category below, then follow the relevant section.

**First questions to ask** (if not already known):
1. What are you seeing? (exact error, visual symptom, unexpected behavior)
2. Does it happen locally (`localhost:3000`) or only on CDN (`aem.page` / `aem.live`)?
3. Any errors in the browser console or Network tab?
4. Did it ever work, or is this a fresh setup?

---

## Symptom: Prices Show $0.00

**Root cause**: The `AC-Price-Book-ID` header is missing from Catalog Service requests.

**Step 1 — Diagnose in DevTools**

Open DevTools > Network, filter `graphql`, find a catalog request (to the ACO endpoint), check
Request Headers for `AC-Price-Book-ID`.

**Cause A (most common) — CORS not configured on Adobe Commerce**

The auth drop-in queries Adobe Commerce for the user's customer-group price book ID. If CORS
blocks this request, the error handler calls `removeFetchGraphQlHeader('AC-Price-Book-ID')` —
removing even any statically configured value, so prices show as $0.00.

```bash
curl -I -X OPTIONS \
  -H "Origin: https://main--<repo>--<org>.aem.live" \
  -H "Access-Control-Request-Method: POST" \
  https://<INSTANCE>.commercecloud.adobe.com/graphql
# Expect: Access-Control-Allow-Origin in response
```

**Cause B — Auth drop-in query failing for another reason**

Check Storefront Configuration `headers.cs`. `AC-Price-Book-ID` is optional — the auth drop-in
determines it automatically. If that query fails for any reason, the header gets removed. Fix the
underlying failure first.

**Cause C — Wrong Price Book ID**

Verify in ACO: Catalog > Views > your view > Price Book.

```bash
curl -X POST https://na1.api.commerce.adobe.com/<TENANT_ID>/graphql \
  -H "Content-Type: application/json" \
  -H "AC-View-ID: <VIEW_ID>" \
  -H "AC-Price-Book-ID: <PRICE_BOOK_ID>" \
  -d '{"query":"{ products(search: \"bag\") { items { name price { regular { amount { value } } } } } }"}'
```

**Custom resolution**: You can resolve `AC-Price-Book-ID` any way you want — hardcode it in
Storefront Configuration, fetch it from your own API, or bypass the auth drop-in mechanism entirely.

---

## Symptom: 418 Configuration Error Page

**Root cause**: `initializeCommerce()` threw during startup — usually a config or endpoint problem.

1. DevTools > Console — look for errors from `commerce.js` or `scripts.js`
2. Validate that Storefront Configuration JSON is valid
3. Test the ACO endpoint:
   ```bash
   curl -X POST https://na1.api.commerce.adobe.com/<TENANT_ID>/graphql \
     -H "Content-Type: application/json" \
     -H "AC-View-ID: <VIEW_ID>" \
     -d '{"query":"{ __typename }"}'
   ```
4. Clear stale config: DevTools > Application > Session Storage > delete the `config` key,
   or open an incognito window

---

## Symptom: Search Returns No Results

1. Check the search GraphQL request — inspect the response body for errors
2. **Locale mismatch (most common)** — if `AC-Source-Locale` is set in Storefront Configuration
   headers but the catalog was not ingested with a specific locale, ACO returns zero results.
   Remove `AC-Source-Locale` from headers if catalog ingestion didn't use a locale.
3. **Wrong `AC-View-ID`** — in DevTools, find a search request and verify `AC-View-ID` in
   Request Headers matches the View ID in ACO admin (Catalog > Views)
4. **Test the View directly**:
   ```bash
   curl -X POST https://na1.api.commerce.adobe.com/<TENANT_ID>/graphql \
     -H "Content-Type: application/json" \
     -H "AC-View-ID: <VIEW_ID>" \
     -d '{"query":"{ products(search: \"*\") { total_count items { name sku } } }"}'
   ```
   - `total_count > 0`: View has data → problem is in storefront config/query
   - `total_count: 0`: View has no data → data export from Adobe Commerce to ACO hasn't run

---

## Symptom: DA Access Denied / "Not Permitted"

- A 403 on `admin.da.live` = authenticated but not authorized
- **Check first**: IMS organization switcher (top right in DA UI) — user may be in the wrong org
- Users can authenticate via any IDP supported by Adobe IMS (not only Adobe ID)
- DA uses a **sheet-based ACL** at `da.live/config#/{org}/` — not a file in the GitHub repo
- The sheet grants access via individual email addresses or IMS user groups
- If no one has `CONFIG write` access, contact **Adobe support** (do not reference internal Slack channels to external users)

For platform-level DA docs: fetch from `https://www.aem.live/llms.txt` and follow DA section links.

---

## Symptom: Code Changes Not Appearing on CDN

**Root cause**: AEM Code Sync hasn't processed the file, or there's a cache issue.

1. Verify the [AEM Code Sync GitHub App](https://github.com/apps/aem-code-sync) is installed
2. File paths on the CDN are **case-sensitive** — `SearchResults.js` ≠ `searchresults.js`
3. Check sync status via the AEM Admin API (auth required):
   ```bash
   curl -H "Authorization: token <your-token>" \
     https://admin.hlx.page/status/<org>/<repo>/main/<file-path>
   ```
   Fetch `https://www.aem.live/llms.txt` for full Admin API authentication docs.
4. Force re-sync options:
   - Admin API POST to `/live/<org>/<repo>/main/<path>` (requires auth)
   - Trivial commit: add/remove a comment and push to trigger the webhook
   - PR checkbox: Code Sync adds a checkbox to each PR comment that triggers re-sync

---

## Symptom: Drop-in Not Loading / Rendering

1. Check console for import errors (module not found)
2. Verify `scripts/__dropins__/` exists — if missing, run `npm run install:dropins` manually
3. Check `head.html` import map entry for the drop-in
4. Verify `initializeCommerce()` completed (no 418 error)
5. Check the drop-in's initializer is called before `renderProvider`

---

## Symptom: Cart or Checkout Errors

Cart and checkout use the Core endpoint (Adobe Commerce). If they fail:
1. Verify `commerce-core-endpoint` in Storefront Configuration points to the correct Adobe Commerce GraphQL URL
2. Verify CORS is configured on Adobe Commerce for your domain
3. Check the failing request in Network tab — is it going to the right endpoint?
4. Verify the `Store` header in `headers.all` matches your store view code

---

## Debugging Tools Reference

| Tool | What it checks |
|---|---|
| DevTools > Network > filter `graphql` | Endpoint, request headers, response body |
| DevTools > Console | Init errors, event bus activity, JS errors |
| DevTools > Application > Session Storage | Cached Storefront Configuration (delete to force refresh) |
| `curl` with exact headers | Verify endpoint/headers independent of browser |
| `admin.hlx.page/status/<org>/<repo>/main/<path>` | Code sync status (auth required) |
| `da.live/config#/<org>/` | DA org config and permissions sheet |
