# Intake and handoff templates

These are working structures, not forms to force on every user. Fill from existing context first. Store the app-specific report in the user's workspace or requested artifact location, not inside the reusable skill. Never include passwords, tokens, or private keys.

## Intake

```text
Provider and developer account/team:
App name and package/bundle ID:
Existing app record or create new:
Requested endpoint and explicit order:
Authorization already supplied (and actions excluded):
Report location:

Store: language, App/Game, Free/Paid, category, tags, contact, website
Listing: exact name, short/full copy, localization scope
Assets: folder, filenames, dimensions, screenshot order, provenance
Reviewer access: restriction, credential source, reusable login method,
                 exact instructions, seeded content, feature coverage
Audience/rating: age groups, child design/appeal, app category/subtype,
                 UGC/report/block/moderation/location/purchases facts
Privacy: policy and deletion URLs, deletion mechanisms, encryption,
         account creation methods, data handling table
Other declarations: ads, ad ID/build evidence, government, health,
                    financial, child safety, surfaced provider forms
Publisher access (only if requested): exact recipient, app scope,
                                       permissions, expiry
Release (only if requested): build/version, track, countries, testers,
                            signing status, review/publish authorization
```

Data-handling worksheet:

| Type | Collected | Shared | Ephemeral | Required/optional | Purposes | Evidence/unknowns |
|---|---|---|---|---|---|---|
| Fill per type | | | | | | |

Ask a bundled factual question only for remaining consequential unknowns. Do not ask the user to reconfirm facts already provided. A blank field may be optional; record it rather than making up an answer.

## Report

```markdown
# App store setup report
Date / provider:
Developer account/team:
App name / package or bundle ID / store record ID:
Requested endpoint:

## Saved and verified
- Section: exact non-secret answers; observed saved state or success message.
- Assets: filenames, order, dimensions; declaration and save status.
- Reviewer access: account identifier, instruction summary, password entered
  (value omitted), optional sharing choice. Do not claim login was tested
  unless it actually was.

## Incomplete or blocked
- Task, concrete blocker, current stored state, action needed to unblock.
- Distinguish draft-only from final saved, ready for review from submitted.

## Dashboard / outstanding declarations
- Current observations, counters, locked tasks, optional paths.
- Do not present stale dashboard information as current.

## Scope and consequential actions
- Agreements accepted, access granted and verified scope, builds uploaded,
  signing/review/release actions performed or outstanding.
- Record authorization/confirmation in prose; no credentials.

## Resume
- Exact next page/section/action and dependencies; last confirmed save.
```

Update prior statuses when completed; don't leave “pending” claims contradicted by a later success. Keep historical crash notes clearly dated and identify what recovery resolved. A useful final response states outcome, real remaining work, and a report link.

## Future Apple extension

Add a provider-specific reference and route it from SKILL.md. Reuse identity, endpoint, credential hygiene, evidence, and report structure. Learn Apple-specific review access, privacy disclosures, age-rating questions, assets/localizations, signing/build upload, testing, and release states from current official guidance and actual execution. Record observed dependencies and scope differences rather than porting Google checkbox answers. Do not mark Apple supported merely because this extension point exists.
