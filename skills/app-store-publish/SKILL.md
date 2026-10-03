---
name: app-store-publish
description: Prepare, complete, verify, and resume app-store publishing workflows, including Google Play Console listings, reviewer access, policy declarations, assets, scoped publisher access, and authorized submissions. Use for app store setup or publishing; not for app implementation or website deployment.
---

# App Store Publishing

Turn an app's verified facts and supplied assets into saved store setup, then carry out review/release steps only within the user's authorized scope. Default to preparation when the request does not authorize submission. A saved listing is not a published app.

## Route by provider

- **Before any console work:** read [prerequisites and off-console work](references/before-the-console.md): package name, developer verification API, signing key continuity, the policy pages and in-app features the forms assume, the reviewer account, and store graphics limits.
- **Google Play:** read [Play Console workflow](references/google-play.md).
- **Computer use:** also read [UI execution and recovery](references/computer-use.md) when working through a browser.
- **Intake and reporting:** use [handoff templates](references/handoff.md) to capture missing facts and leave a reliable resume state.
- **Apple:** no validated Apple procedure is included yet. Obtain current official App Store Connect guidance and inspect the live account/UI before proceeding. Do not reuse Google answers or permissions for Apple. Add a separate provider reference once that workflow is learned; retain the common intake, evidence, scope, and reporting model.

## Start from a concrete app and endpoint

Establish store, developer account/team, app name, package/bundle ID, existing app record, and intended endpoint: draft setup, test distribution, review submission, or production release. Preserve a user-specified order. Reuse existing records; check for duplicates before creating anything.

Inspect existing reports and saved UI state before asking questions. Gather facts from user declarations, current app/build configuration, and supplied assets. Ask for missing information only when it changes a declaration or blocks the task; continue independent work while waiting. Keep confirmations separate from factual questions.

Explicitly distinguish:

- App facts: data collected, sharing, ad ID, login, age targeting, reporting mechanisms, asset provenance.
- Store state: not started, unsaved, saved draft, ready for review, submitted, approved, released.
- Authorization: authorized preparation versus signing, agreements, access grants, review, or release.

An earlier app's answers are never evidence for a future app. “No ads” does not establish “no advertising ID.” A reporting mechanism does not establish blocking or moderation. A target audience is different from a content rating.

## Execute within scope

Verify app identity before mutations. Avoid unrelated apps/account settings. Treat publisher access as its own task, with explicit recipient and permission scope. Do not infer account-wide access from app administration.

Follow current tool/host rules for credentials, security-sensitive grants, agreements, payments, and submission. User instructions to avoid repeated questions do not override action-time confirmation or user handoff requirements enforced by those rules. Prepare concrete results first and explain the exact source of any required stop; do not invent an approval flow for ordinary saves.

Reviewer credentials belong only in the intended store form. Do not place passwords, tokens, or private keys in skills, repo files, reports, screenshots for delivery, or command output. Do not create reviewer identities or bypass verification unless explicitly requested and permitted. Turn off optional additional credential sharing/testing unless authorized.

## Verify and finish

For each section, use the final applicable Save, then verify a success message or persisted status. “Save as draft” may preserve incomplete work without completing the declaration. Reopen or inspect summaries only where that resolves a real uncertainty.

Before finishing, inspect the app's setup dashboard and outstanding declarations. Separate actual blockers from optional testing/launch paths. Record completed sections, evidence, defaults, unanswered fields, required next actions, and authorization boundaries in a local report. Keep incomplete items explicit; do not declare completion because a tool call succeeded.

Use current official provider documentation when policy interpretation, a changed requirement, or a technical claim needs verification. Live UI wording takes precedence over dated observations in the provider reference. Stop only dependent work when login, a new agreement, missing facts, or authorization blocks it; complete unaffected work and leave a precise resume step.
