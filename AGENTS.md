# Agent context: Commerce DX Skills

This document is for **AI coding agents** and **human contributors** who land in this repository. It explains what the project is for, how it is organized, and how to change it safely.

## Purpose

This repository holds **Claude Agent Skills** (and supporting material) that help **software engineers working on Adobe Commerce** projects — especially **Edge Delivery Services (EDS)** storefronts built from [`hlxsites/aem-boilerplate-commerce`](https://github.com/hlxsites/aem-boilerplate-commerce) — with repeatable, accurate guidance.

Intended coverage includes (non-exhaustive):

- Creating and configuring **Adobe Commerce Cloud Service (ACCS)**, **Adobe Commerce Optimizer (ACO)**, or related **PaaS / B2B** backend environments.
- Creating and configuring an **EDS Commerce storefront** from the boilerplate (content source, Code Sync, drop-ins, local dev).
- **Document Authoring (DA)**: content pages, blocks, publishing, and **permissions / access** issues.
- **Storefront code**: customizing blocks, drop-ins, GraphQL overrides (`overrideGQLOperations`), slots / DOM patterns, **aem-commerce-prerender**, **product recommendations** units and UI.
- **Troubleshooting**: catalog/search/PDP behavior, configuration errors (for example 418-style flows), CORS, CDN sync, cart/checkout, and **where to look** (browser DevTools, endpoints, config).
- **Operational orientation**: how authoring, admin, and cloud consoles relate to **EDS org/site**, **tenant IDs**, and Adobe surfaces.

Skills are **advisory**: they do not replace official Adobe documentation, tenant-specific runbooks, or reading the user's actual repo.

## What ships here

| Deliverable | Location | Role |
|-------------|----------|------|
| **Three skills** | `skills/commerce-setup/`, `skills/commerce-develop/`, `skills/commerce-troubleshoot/` | Runtime instructions (`SKILL.md`) |
| **Evals** | `skills/*/evals/evals.json` | Regression prompts for skill-creator |
| **Eval workspaces** | `commerce-*-workspace/iteration-*` | Outputs and grading from eval runs |

### Skill split (mental model)

| Skill | Use when the user is… |
|-------|------------------------|
| `commerce-setup` | Standing up backends, EDS + boilerplate, Storefront Configuration, CORS, DA setup and first authoring steps. |
| `commerce-develop` | Changing blocks/drop-ins, prerender, recommendations, GraphQL extension patterns, storefront architecture. |
| `commerce-troubleshoot` | Debugging runtime/config: prices, search, errors, DA access, sync, cart, headers/endpoints. |

## Source authority

Official public documentation is the source of truth. Each `SKILL.md` documents which source to trust when they conflict:

| Domain | Authoritative Source | Root URL |
|---|---|---|
| EDS platform — Code Sync, Admin API, CDN, fstab, DA platform | **aem.live** | `https://www.aem.live/llms.txt` |
| Storefront drop-ins, blocks, boilerplate, recommendations, SDK | **Storefront ExL** | `https://experienceleague.adobe.com/developer/commerce/storefront/llms.txt` |
| Commerce backend, B2B, admin, catalog, data export | **Commerce ExL** | `https://experienceleague.adobe.com/en/docs/commerce` |

When a topic spans domains, trust the component-specific authority for component behavior, and the platform authority for platform behavior. For example: DA content formatting → Storefront ExL. DA permissions system → aem.live.

Skills use **WebFetch** to pull current content from these sources rather than maintaining static copies. The `search-commerce-docs` MCP can also search storefront docs after `aio auth login`.

## How to edit content

1. **Skill behavior, triggers, official doc tables, architecture notes, inline facts** → `skills/<name>/SKILL.md`.
2. **Fetch strategy** — if a new doc section becomes available at an official source, add it to the "Fetch Strategy" table in the relevant `SKILL.md`.
3. **Evals** — after material behavior changes to a skill, update or add eval cases in `skills/*/evals/evals.json`.

Do not maintain static copies of official documentation in this repo. If you find information in a `SKILL.md` that conflicts with current official docs, update the `SKILL.md` to reflect reality or remove the stale content and add a fetch pointer instead.

## Trust and accuracy

- Inline facts in `SKILL.md` reflect real project experience. When something looks off, verify against official docs and the user's environment.
- **Terminology** is enforced across skills: say **Adobe Commerce** (not "Magento"); say **Storefront Configuration** (not "config.json" as the primary term).
- **Boilerplate and product behavior change over time.** Prefer the **user's checked-in code** and current Adobe docs over static memory.

See `README.md` for **eval**, **review UI**, and **packaging** commands.

## Repo hygiene for agents

- **Scope**: Changes should usually touch `SKILL.md` files and/or evals — avoid unrelated refactors.
- **No static doc copies**: Do not add or restore reference files that duplicate official documentation. Add a fetch pointer instead.
- **Evals**: After material behavior changes, run evals as described in `README.md` when possible.

## Human-oriented readme

Project overview and commands for humans: `README.md`.
