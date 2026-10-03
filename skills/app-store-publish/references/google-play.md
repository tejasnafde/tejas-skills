# Google Play Console workflow

These mechanics were observed in October 2026. Labels and dependencies can change. Use the live UI and current official documentation, not remembered routes or checkbox indices. This is operational guidance, not a reusable set of policy answers.

Official entry points when interpretation is needed:
- [App access / reviewer instructions](https://support.google.com/googleplay/android-developer/answer/9859455)
- [Target audience](https://support.google.com/googleplay/android-developer/answer/9867159)
- [Data safety](https://support.google.com/googleplay/android-developer/answer/10787469)
- [Account deletion](https://support.google.com/googleplay/android-developer/answer/13327111)
- [Advertising ID](https://support.google.com/googleplay/android-developer/answer/6048248)
- [Store listing assets](https://support.google.com/googleplay/android-developer/answer/9866151)

## Identify or create the record

Confirm the developer account and exact package/app record. Search the app list before creating a draft; similarly named apps and multiple packages may coexist in one account. Package availability/registration and draft creation are distinct checks; verify the actual identity displayed by Console.

For creation, obtain name, default language, App/Game, and Free/Paid. Handle developer policy and export agreements under current confirmation rules. Do not treat draft creation as authorization to configure signing or create a release. Preserve automatic installer protection when requested or left at its default; describe its current build/distribution scope only using verified facts.

## Dependency-aware setup

Unless the user specifies another order, start with reviewer access, then target audience, then the remaining declarations/listing and final Data safety Save. Observed dependencies:

1. **Sign in details** (formerly App access) must be saved before starting Target audience and content.
2. **Target audience and content** must be completed before final Data safety Save.
3. Data safety can be filled and saved as draft while target audience is blocked.
4. A store listing draft can preserve text/assets while its final asset declaration remains incomplete.

Console's App content → Need attention is the source for required declarations. Do not invent News/COVID or other forms if they are absent. Inspect Actioned to find an already-completed declaration that needs correction.

## Reviewer access

For restricted apps, select Yes and add a named credential set. Supply username/email, password if required, and exact English access instructions. Use the intended login method; do not substitute email OTP instructions for a Google reviewer account or vice versa. Instructions should explain meaningful seeded content and how reviewers reach restricted features.

Ensure the supplied account actually covers the app's features before affirming full access. Identify reusable access for OTP, two-factor, location, or paid restrictions; do not invent bypasses. Save both the credential-set dialog and the parent declaration. Inspect optional “testing on Google and trusted partner devices” separately from necessary review access. Verify parent Save success.

## Target audience and rating

Select only the app's supplied age groups. An 18+ selection was observed to skip App details, Ads, and Store presence and go straight to Summary; child design/appeal questions did not appear. Record that exact path instead of claiming nonexistent answers were entered. Younger audiences may expose different obligations; inspect and answer them using app facts.

For content rating, use the actual category and subtype. Small invited friend circles may fit a different subtype from public social networks. Inspect conditional questions about reporting, blocking, moderation, purchases, location, and invite-only interactions independently. Preserve prior answers when retaking a questionnaire unless the user changes them or verified facts contradict them. Review the generated summary and save the final rating; accepting rating terms is distinct from submitting the app for review.

City-level display is not necessarily precise location sharing. Determine both what is collected and what other users see; don't use a rating answer as a substitute for Data safety disclosure.

## Other declarations

Privacy URL, ads, government, financial features, health, child safety, advertising ID, and any newly surfaced forms should be answered from supplied/verified facts. Some “no features” paths have a second documentation/regional step showing no documents required; finish that step and verify Save.

- Advertising ID includes SDK behavior, not just ads. Verify a build manifest and SDK inventory or use the user's explicit verified declaration. No ads alone is insufficient.
- Child safety standards may request a published standards URL, an in-app reporting mechanism, contact email, and compliance/reporting attestations. Use actual facts and authorized attestations; distinguish factual declarations from new agreements. If the UI only accepts email, record the contact's name/mechanism in the report rather than inventing fields.
- Category, tags, email, website, and optional phone are separate listing settings. Use available relevant tags; don't replace missing exact tags with unrelated ones.

## Store listing and graphics

Preserve exact supplied name/short/full description and paragraph breaks. Check live limits. Observed asset guidance: icon 512×512, up to 1 MB; feature graphic 1024×500, up to 15 MB; phone screenshots 2–8, 320–3840 px per side, up to 8 MB, with the UI's stated aspect requirements. Recheck current limits before preparing/uploading future assets.

Upload only the app's requested assets. Verify filename, dimensions, thumbnail, slot, and count. Concurrent uploads can finish in arbitrary order. The asset library selection sequence was observed to determine insertion order: deselect automatic selections and select screenshots in the intended order before Add. Verify the final listing sequence by filenames; don't assume lexical order or upload order was retained. Use visible reordering controls if needed.

The Assets → Review step may include an AI asset declaration. Select based on provenance, not appearance. Code rendering an existing brand SVG/fonts and real app captures were user-confirmed non-AI in the source workflow; this is not evidence for future assets. Ask for provenance if unknown, save a draft while pending, then use final Save once answered. This internal listing Review step and Save are not “Send for review” to Google.

## Data safety

Build a table for every collected/shared type with: collected, shared, ephemeral, required/optional, and exact collection/sharing purposes. The definition of shared has exemptions; interpret them with current official guidance when necessary. Do not infer third-party sharing solely from using a processor, or infer no sharing solely from having no ads.

Account creation options include username/password, username with other authentication, OAuth, and others. Inspect actual implementation where unclear: email OTP and Google OAuth can require two selections. Do not select a password login merely because the Google reviewer account has a password.

Enter encryption and account deletion facts plus the deletion URL. An optional question about deleting data *without deleting the account* is different from account deletion; leave it unanswered or obtain the relevant fact. In-app Settings → Delete account does not imply a separate selective-deletion capability.

Select data types, then complete each handling dialog. For every type, explicitly verify collection/sharing, ephemeral status, optional/required status, and purposes. Save each dialog, confirm Completed, then proceed to Preview. Expand preview details to check purposes, optional markers, sharing, encryption, and deletion URL. The preview can suppress ephemeral collection from the public view, so also check the source handling answer when needed.

Use Save as draft only when blocked or intentionally staging. Once prerequisites are satisfied, perform final Save and verify success. Review submission remains a separate action.

### Example facts from the source app (not defaults)

The source app was a free private-circle bucket list with no ads, Google OAuth/email OTP, city-level posts, photos, shared picks/memories, reporting in Settings, deletion in Settings, and optional push notifications. Its user supplied these disclosures:

| Data | Requirement | Collection purposes |
|---|---|---|
| Name, email, user IDs | Required | App functionality; Account management |
| Approximate location, photos | Optional | App functionality |
| Other user-generated content | Required | App functionality |
| App interactions | Required | Analytics |
| Crash logs | Required | App functionality |
| Device or other IDs | Optional | App functionality |

All were collected, not ephemeral, not shared with third parties, and not used for ads. This example illustrates the mapping; obtain a new app's facts before using any answer.

## Publisher/service-account access

Only when expressly authorized: invite the exact recipient once. Inspect the current list first; if already present, do not silently edit it or send a duplicate. Clarify changed scope only if necessary.

For an app-only Admin request:
1. Add exactly the target app. Avoid Select all and permission groups that widen access.
2. Select Admin (all permissions) within that app's permission dialog.
3. Verify every Account permissions checkbox remains unchecked.
4. Verify app summary lists exactly one row/package and the recipient is exact.
5. Obtain any action-time confirmation required by the current tool policy immediately before sending.
6. Send once, inspect the resulting status, then verify saved scope read-only.

App Admin includes permissions to manage access for users of that app, releases, signing, store presence, and financial information for the app; it is broader than store-listing editing. Do not downscope an explicit Admin request without discussion, or broaden a narrower request to Admin for convenience. Creating access does not authorize exercising release/signing permissions.

## Dashboard and handoff

After saves, check App content → Need attention and the Dashboard. “You're all caught up” verifies no declarations currently need attention, not that the app is approved or released.

The observed completed setup dashboard retained alternative launch paths:
- Internal testing: testers, create release, preview/confirm.
- Closed testing: countries, testers, create release, preview/confirm, send for review.
- Open testing: countries, create release, preview/confirm, send for review.
- Pre-registration: bundle/APK upload, countries, optional reward, send for review.
- Production: countries, create release, preview/confirm, send for review, publish.

Expand task lists read-only; do not click Create release, Upload, Send for review, or Publish just to inspect status. Record actual current counters and locked tasks. These paths are alternatives, not a mandate to complete every one. Report outstanding signing/build/release work only to the extent verified, and distinguish it from policy setup.
