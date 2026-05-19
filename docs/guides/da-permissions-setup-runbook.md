# DA Permissions Setup Runbook

**Document Authoring (DA) — Access Control Troubleshooting & Setup Guide**  
Use this when a user can sign in to DA but cannot browse or edit an org/site.

---

## Symptom

You navigate to `da.live/#/{org}/{site}` and see:

- **"Not permitted"** in the DA browser UI
- A `403 Forbidden` on `GET https://admin.da.live/config/{org}/` in DevTools Network tab

### What the 403 means

Per the DA access control docs:

- `401` = user is **anonymous** (not logged in)
- `403` = user is **logged in** but does not have access

So if you see a 403, authentication succeeded but authorization failed. The most common cause is that your email, IMS org, or IMS group does not match the org's DA `permissions` sheet.

### Before investigating permissions

**Check the IMS organization switcher first** (top right in the DA UI). You may be logged into the wrong IMS org. Switching to the correct org may resolve the issue immediately.

> **Note on authentication**: DA supports any IDP connected to Adobe IMS — not just Adobe ID. Users may authenticate via Google or other IDPs. The permissions sheet grants access by email address or IMS user group, regardless of which IDP was used to authenticate.

---

## Understanding DA's Permission Model

DA uses a **sheet-based ACL system**. Permissions are declared in a `permissions` sheet inside the org-level config at:

```
https://da.live/config#/{org-name}/
```

The sheet has four columns:


| path   | groups                                  | actions | comments (optional) |
| ------ | --------------------------------------- | ------- | ------------------- |
| CONFIG | [your@email.com](mailto:your@email.com) | write   |                     |
| /+**   | [your@email.com](mailto:your@email.com) | write   |                     |


### Key path syntax


| Path              | What it matches                                          |
| ----------------- | -------------------------------------------------------- |
| `CONFIG`          | The org config itself — **required** to edit permissions |
| `/+**`            | All content in the org, including the root folder        |
| `/**`             | All content *under* root, but not the root folder itself |
| `/{site}/+**`     | All content under a specific site, including that folder |


### Key actions


| Action    | What it grants                    |
| --------- | --------------------------------- |
| `write`   | Full read + write + delete access |
| `read`    | Read-only access                  |
| *(empty)* | Explicit deny                     |


> **Critical:** Always include a `CONFIG write` row for at least one administrator. If you omit it, you can lock yourself and others out of editing the permissions sheet.

---

## Diagnosing the Problem

### Step 1 — Check the failing request

Open DevTools → Network tab → look for a request to:

```
https://admin.da.live/config/{org}/
```

If it returns `403`, your identity is not authorized by the permissions sheet, or the sheet has not been created yet.

### Step 2 — Try to open the org config directly

Navigate to:

```
https://da.live/config#/{org-name}/
```

**What you might see:**


| What you see                                         | What it means                        |
| ---------------------------------------------------- | ------------------------------------ |
| Empty spreadsheet (no tabs, no data)                 | Permissions sheet was never created  |
| A `permissions` tab exists but your email is missing | You need to be added                 |
| You get a 403 just loading this page                 | You have no access at all — escalate |


---

## Fix: Setting Up the Permissions Sheet

### If the config is empty

You won't be able to create the permissions sheet yourself — DA requires existing `CONFIG write` access to modify the config.

**You must reach out to someone who can create it for you.**

### Who to contact

**Contact Adobe Support** via your official support channel (Slack, Teams, Discord, or
the Adobe Support portal). Ask them to create an initial permissions sheet for your org.

> **Note:** The DA team's internal Slack channel is not accessible to external users.
> All escalation should go through your official Adobe support channel.

### What to ask them to create

Request a `permissions` sheet in `da.live/config#/{your-org}/` with the following rows:

#### For email-only access (simplest, no IMS org needed):


| path   | groups                                                                                     | actions | comments |
| ------ | ------------------------------------------------------------------------------------------ | ------- | -------- |
| CONFIG | [your@adobe.com](mailto:your@adobe.com), [colleague@adobe.com](mailto:colleague@adobe.com) | write   | Admins   |
| /+**   | [your@adobe.com](mailto:your@adobe.com), [colleague@adobe.com](mailto:colleague@adobe.com) | write   |          |


#### For IMS Org-based access (recommended for teams):


| path        | groups                                  | actions | comments      |
| ----------- | --------------------------------------- | ------- | ------------- |
| CONFIG      | `{IMS_ORG_ID}`                          | read    |               |
| CONFIG      | `{IMS_ORG_ID}/admins`                   | write   | Adobe Support |
| /+**        | `{IMS_ORG_ID}`                          | read    |               |
| /+**        | `{IMS_ORG_ID}/authors`                  | write   |               |
| /{site}/+** | [your@adobe.com](mailto:your@adobe.com) | write   | Site-specific |


> **Finding your IMS Org ID:** Go to [Adobe Admin Console](https://adminconsole.adobe.com/). The IMS Org ID is the alphanumeric string before the `@` in the URL (e.g., `77C920686809469C0A495FE5`).

---

## Example Permission Sheet

This anonymized example shows the shape of a completed permissions sheet:


| path        | groups                                                                                     | actions | comments      |
| ----------- | ------------------------------------------------------------------------------------------ | ------- | ------------- |
| CONFIG      | `{IMS_ORG_ID}, {SUPPORT_IMS_ORG_ID}`                                                        | write   | Adobe Support |
| CONFIG      | [owner@example.com](mailto:owner@example.com), [admin@example.com](mailto:admin@example.com) | write   |               |
| /+**        | [owner@example.com](mailto:owner@example.com), [admin@example.com](mailto:admin@example.com) | write   |               |
| /{site}/+** | [author@example.com](mailto:author@example.com)                                             | write   | Site-specific |


**Notes:**

- Row 2 uses IMS Org IDs for administrator or support access.
- Rows 3–4 use individual emails for project owners.
- A site-specific path like `/{site}/+**` can be added when a user should only have access to one site folder.

---

## After Permissions Are Set

1. **Log out and back in** to DA — this refreshes the IMS group/permission cache
2. Navigate back to `da.live/#/{org}/{site}`
3. The "Not permitted" message should be gone

---

## Quick Reference: DA Config URLs


| Purpose                            | URL                                                  |
| ---------------------------------- | ---------------------------------------------------- |
| View/edit org config & permissions | `https://da.live/config#/{org}/`                     |
| Browse org content                 | `https://da.live/#/{org}/`                           |
| Browse specific site               | `https://da.live/#/{org}/{site}`                     |
| DA admin API config endpoint       | `https://admin.da.live/config/{org}/`                |
| Edge Delivery user admin           | `https://tools.aem.live/tools/user-admin/index.html` |


---

## Related Resources

- [DA Access Control Reference](https://docs.da.live/developers/reference/access-control)
- [DA Permissions & Security Guide](https://docs.da.live/administrators/guides/permissions)
- [AEM Edge Delivery Auth Setup](https://www.aem.live/docs/authentication-setup-authoring)

## Official references & attribution

- [DA Access Control Reference](https://docs.da.live/developers/reference/access-control) (retrieved 2026-05-14). Used to verify the `permissions` sheet location, `read`/`write`/empty actions, group formats, `CONFIG`, `ACLTRACE`, path wildcard syntax, longest-path evaluation, and `401`/`403` developer semantics.
- [DA Permissions and Security Guide](https://docs.da.live/administrators/guides/permissions) (retrieved 2026-05-14). Used to verify IMS identity support, recommended IMS-org and email-only permission sheet patterns, Admin Console IMS org ID guidance, support escalation guidance, and the note that `write` implies read and delete.
- [AEM Configuring Authentication for Authors](https://www.aem.live/docs/authentication-setup-authoring) (retrieved 2026-05-14). Used to distinguish DA authoring permissions from Edge Delivery preview, publish, and origin access.

