# Apple App Store: from zero to "Waiting for Review"

Learned on Someday (`app.someday.capture`, Expo/EAS, October 2026), on an
organization account owned by someone else (the Account Holder is a parent's
company that also holds its own apps). Most of it is API work. Only four steps
need the web UI.

## Split: API versus web UI

| Step | How |
|---|---|
| Accept the updated Program License Agreement | **Web UI, Account Holder only.** Blocks everything else (Certificates, App Store Connect, the API) until accepted. |
| Create the App Store Connect API key | **Web UI**, Users and Access > Integrations > App Store Connect API. Admin role, so EAS can manage certificates. The `.p8` downloads ONCE: put it straight into a secret store with key_id, issuer_id, team_id, then `rm -P` the download. |
| Register the bundle ID, enable capabilities | **API** (`POST /v1/bundleIds`, `POST /v1/bundleIdCapabilities`). Sign in with Apple is `capabilityType: APPLE_ID_AUTH` with `settings: [{"key": "APPLE_ID_AUTH_APP_CONSENT", "options": [{"key": "PRIMARY_APP_CONSENT"}]}]`; `SIGN_IN_WITH_APPLE` is rejected with 409 `ENTITY_ERROR.ATTRIBUTE.TYPE`. |
| App Groups (share extensions) | **Web UI.** The API can enable the `APP_GROUPS` capability but cannot create a group or assign it. Create `group.<bundle id>` and assign it to the app AND the extension ID. |
| Create the app record | **Web UI.** The API cannot create apps. Name, language, bundle ID, SKU. |
| App Privacy ("nutrition label") | **Web UI.** No API. Map from the Play data safety answers; publish it. |
| Sign in with Apple key (token revocation) | **Web UI**, Keys > (+), only "Sign in with Apple", primary App ID = the app. Downloads once. |
| Certificates and provisioning profiles | **EAS**, with the API key (see below) |
| Build upload | `eas submit -p ios` with the API key |
| Listing text, subtitle, categories, URLs, copyright | **API** (`appStoreVersionLocalizations`, `appInfoLocalizations`, `appInfos` categories) |
| Age rating | **API** (`ageRatingDeclarations`). Answer every field; a private group app with UGC and messaging came out 4+. |
| Price and availability | **API** (`appPriceSchedules` USA $0 price point, `appAvailabilities` v2 with all territories) |
| Screenshots | **API** (`appScreenshotSets` + `appScreenshots`: reserve, upload operations, commit with MD5) |
| App Review details (demo account, contact, notes) | **API** (`appStoreReviewDetails`). `contactPhone` is REQUIRED at create time (409 `ENTITY_ERROR.ATTRIBUTE.REQUIRED`) and must be `+<country code> ...`. |
| Attach build, submit | **API** (`PATCH appStoreVersions/{id}/relationships/build`, then `reviewSubmissions` + `reviewSubmissionItems`, then `submitted: true`) |

## Talking to the API

Sign an ES256 JWT with the `.p8` (`kid` = key_id, `iss` = issuer_id,
`aud` = `appstoreconnect-v1`, expiry under 20 minutes). PyJWT plus cryptography
in a throwaway venv is enough; keep a tiny `asc.py METHOD PATH [json]` helper
that reads the key from the secret store at run time. Check access first:
`GET /v1/apps` lists the team's apps (and shows whose account it is).

## EAS with only an API key (no Apple ID, no 2FA)

```sh
EXPO_ASC_API_KEY_PATH=<tmp .p8> EXPO_ASC_KEY_ID=... EXPO_ASC_ISSUER_ID=... \
EXPO_APPLE_TEAM_ID=... EXPO_APPLE_TEAM_TYPE=COMPANY_OR_ORGANIZATION \
EXPO_NO_CAPABILITY_SYNC=1 eas build -p ios --profile <store profile>
```

- The FIRST build cannot be `--non-interactive`: creating the distribution
  certificate and profiles needs prompts ("Distribution Certificate is not
  validated for non-interactive builds"). Drive it with `expect`: answer
  `(Y/n)` with `y`, stop on any Apple ID / password / 2FA prompt. Match on
  `(Y/n)`, not on the question text: colour codes break text matches.
- A share extension is a second target: it needs its own bundle ID and
  provisioning profile. EAS lists the targets at the start.
- EAS capability sync fails on `PUSH_NOTIFICATIONS` and `APP_GROUPS` with an
  invalid-document error. Enable them yourself (API + App Group in the web
  UI), then build with `EXPO_NO_CAPABILITY_SYNC=1`.
- The "set up Push Notifications?" prompt needs an APNs key, which the API
  cannot create (it would ask for an Apple login). Answer No to get the build
  going; create the APNs key in the web UI later and give it to EAS.
- After the first interactive run, later builds work with `--non-interactive`.
- `eas submit` reads the key from `submit.<profile>.ios.ascApiKeyPath`; write
  it from the secret store just before and `rm -P` it after (gitignore it).
- Expo GraphQL can fail mid-setup on a network blip; rerun, it reuses what
  was created.

## App config that review and policy need

- `ios.infoPlist.ITSAppUsesNonExemptEncryption: false` (no export compliance
  question per build).
- `ios.supportsTablet: false` unless you want iPad screenshots and iPad review.
- `ios.usesAppleSignIn: true` when the app offers Google sign-in (guideline
  4.8). Native ID-token flow (`expo-apple-authentication` + Supabase
  `signInWithIdToken` with a hashed nonce) needs no Services ID and no client
  secret, so nothing expires every 6 months. Supabase: Apple provider enabled
  with client ID = the bundle ID, no secret.
- **A second app on the same Supabase project** (scout shares Someday's, 2026-10-05):
  set `external_apple_client_id` to a comma-separated list that KEEPS the existing
  ID (`app.someday.capture,com.tejas.jobfinder`). Do not PATCH
  `external_apple_additional_client_ids`: the Management API moved that value into
  `external_apple_client_id` and dropped the existing ID, which broke the other
  app's Apple sign-in until it was restored. Read the config back after every PATCH.
- **Adding a native module to an app that ships OTA updates:** binaries already in
  the field lack it, and an OTA bundle that imports it at the top of a file crashes
  them on launch (same runtime version). Require it lazily, only on the platform
  that has it (`Platform.OS === 'ios' ? require('expo-apple-authentication') : null`),
  or bump the runtime version.
- Account deletion must REVOKE Apple tokens: the Sign in with Apple key signs a
  client_secret JWT; the app re-authenticates with Apple at delete time to get
  a fresh authorizationCode; the API exchanges it and calls
  `appleid.apple.com/auth/revoke`. Revoke failure must not block deletion.
- Anything Android-only (an APK self-updater) must be off on iOS: gate on
  `Platform.OS` and a build-variant flag, or the iOS app offers an APK.
- No external tip or donation link inside the app (3.1.1). A user-agent mark
  from the native shell lets the web app hide it.
- The Cloud Run service that uses a new secret needs `secretAccessor` for its
  runtime service account BEFORE the deploy that references it, or the new
  revision fails `SecretsAccessCheckFailed` (the old one keeps serving).

## Screenshots

- iPhone 6.9-inch: 1320 x 2868. In the API the display type is still
  `APP_IPHONE_67` (`APP_IPHONE_69` is rejected); that slot accepts 1320 x 2868.
- Playwright's `page.screenshot` caps at 2x. Use raw CDP
  `Page.captureScreenshot` with `Emulation.setDeviceMetricsOverride`
  (440 x 956, deviceScaleFactor 3) to get true 3x. Verify the PNG size before
  upload.

## Testing without an iPhone or a local simulator

- An iOS simulator runtime is about 8 GB. Instead build an EAS simulator
  profile (`ios.simulator: true`) and run it on Appetize.io in the browser.
- Real-device checks: TestFlight internal testers (the Account Holder is one
  by default; add a friend's Apple ID through the API). Internal testers need
  no review.
- Most fixes to a WebView-shell app ship through the web with no review at
  all; only native shell changes need a new build and App Review.

## Computer-use checkpoints (Codex)

Codex computer use asks for confirmation AT THE MOMENT of a legal or
consequential click, even with authority given earlier: the Program License
Agreement, creating an Admin API key. Plan for it: relay the user's own words
("approve", "sure") as the action-time confirmation, resuming the same session.
A fresh headless session works once the user has chosen "always allow" for the
browser in the desktop app.
