# AGENTS.md Pattern — Architecture

A documentation-routing pattern for AI agents working across Adobe Commerce's distributed doc ecosystem. Simply, the user prompting the agent provides our entry-file (AGENTS.md) to be read when answering their question. They then provide their question, and the agent will follow the routing logic in AGENTS.md to determine the correct documentation to fetch before synthesizing an answer.

---

## 1. System Overview

How a user question travels through the system to a sourced, attributed answer.

```mermaid
flowchart TD
    User([User])
    Agent["AI Agent\n(chat interface)"]
    AGENTS["AGENTS.md\n(slim base router)"]
    Guides["Per-source guide\nskills/docs/*.md"]

    User -->|"question or task"| Agent
    Agent -->|"loads as system context"| AGENTS

    AGENTS --> Routing{Route by topic}

    Routing -->|"storefront / drop-ins / boilerplate"| SFG["storefront.md"]
    Routing -->|"Admin / B2B / catalog / cloud"| ELG["experience-league.md"]
    Routing -->|"da.live / authoring / permissions"| DAG["document-authoring.md"]
    Routing -->|"EDS blocks / CDN / Sidekick"| AEMG["aem-eds.md"]
    Routing -->|"App Builder / APIs / extensibility"| DEVG["commerce-developer.md"]

    SFG & ELG & DAG & AEMG & DEVG --> Guides

    Guides -->|"entry points + known starting points"| SF["Adobe Commerce Storefront\nexperienceleague.adobe.com/developer/commerce/storefront"]
    Guides -->|"entry points + known starting points"| EL["Experience League Commerce\nexperienceleague.adobe.com/en/docs/commerce"]
    Guides -->|"entry points + known starting points"| DA["Document Authoring\ndocs.da.live"]
    Guides -->|"entry points + known starting points"| AEM["AEM / Edge Delivery Services\naem.live"]
    Guides -->|"entry points + known starting points"| DEV["Adobe Commerce Developer\ndeveloper.adobe.com/commerce"]

    SF & EL & DA & AEM & DEV -->|"fetched content"| Synthesis["Agent synthesizes answer"]
    Synthesis -->|"answer + source URLs"| User
```

---

## 2. Key Design Principles

| Principle | What it means in practice |
|---|---|
| **Fetch first, name names second** | Specific names (classes, fields, config keys, URLs) are only stated after fetching — never from training data |
| **Modular per-source guides** | Each doc source's navigation details live in its own file, loaded only when needed. Consistent template across all guides makes them easy to maintain and selectively import. |
| **Code can beat docs — but confirm first** | Local code (storefront, App Builder, API Mesh, PHP module) may reflect the user's actual state; confirm it's current before treating it as authoritative over docs |
| **Public sources only** | No internal Slack, dashboards, or Adobe-employee-only resources are cited |
| **Attribution required** | Every answer cites the doc URL(s) used; if the answer isn't in the docs, say so and point to Adobe support |
| **No invented URLs** | Only URLs retrieved in-session or listed in AGENTS.md / the loaded per-source guide are cited |

---
