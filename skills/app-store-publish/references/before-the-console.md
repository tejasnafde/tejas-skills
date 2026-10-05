# Before the console: prerequisites and off-console work

The console forms are the easy half. Most of the time on the first app (Someday,
`app.someday.capture`, October 2026) went into things the forms *assume* are
already true. Do these first, or the forms either block you or make you state
something false.

## 1. Decide the package name once

- A Play package name can never change after the app is created. Changing it
  means a new app: existing users get no updates.
- Pick it before the first APK ships anywhere, including sideloaded APKs. The
  name is also baked into Firebase (`google-services.json`), deep links and the
  developer-verification registration.
- Convention for new apps: **`app.tn07.<app>`**, the SAME ID on Android and iOS,
  set in `app.json` before the first build of ANY kind (decided 2026-10-05, after
  scout shipped sideloaded APKs as `com.tejas.jobfinder` and had to move). Users
  never see it, except in the Play URL. Older apps predate this:
  `app.someday.capture`, `app.switchboard.mobile`, `dev.tn07.brief`; leave
  published ones alone.

  Every other identifier derives from it, so nothing is invented per app:

  | Identifier | Value |
  |---|---|
  | Android package, iOS bundle ID | `app.tn07.<app>` |
  | iOS share extension | `app.tn07.<app>.share-extension` (what `expo-share-intent` derives) |
  | App Group | `group.app.tn07.<app>` |
  | App Store Connect SKU | `<app>-ios` |
  | Expo slug, EAS project, URL scheme | `<app>` (not a legacy codename) |
  | Firebase Android app | `app.tn07.<app>`, `google-services.json` trimmed to it |
  | Store name | `<app>` plus a short tagline, max 30 characters |
  | Secrets, GCP labels | `<APP>_*`, label `app=<app>` |

- Changing it after a store record exists: Apple never lets an app record change
  its bundle ID. Rename the abandoned record (`appInfoLocalizations` name, max 30
  characters) so it stops holding the store name, and use a new SKU.
- Play Console now asks for the package name on the Create app form and checks
  that the developer account owns it.

## 2. Android developer verification (applies to sideloaded APKs too)

Google requires every Android package to be registered to a verified developer
(enforced from 2026-09-30 in a few countries, worldwide in 2027). Apps published
on Play are registered automatically. APKs sideloaded from GitHub or GCS are not.

It is fully scriptable through the **Android Developer Console API**
(`androiddeveloperconsole.googleapis.com`, v1):

- Auth: OAuth user flow ONLY, scope
  `https://www.googleapis.com/auth/androiddeveloperconsole`. Service accounts and
  gcloud tokens are refused. Use any Desktop OAuth client in a project where the
  API is enabled, with a loopback redirect. Delete the refresh token when done.
- The discovery document needs an API key (`$discovery/rest?version=v1&key=`).
  Create a key restricted to this API, read the doc, delete the key.
- Paths (all under `https://androiddeveloperconsole.googleapis.com/v1/`):
  - `GET developerAccounts`
  - `GET developerAccounts/{id}/androidPackages/{pkg}/registrationPolicy`
    (`USE_ANY_KEY` means nobody holds the name yet)
  - `POST developerAccounts/{id}/androidPackages?androidPackageId={pkg}` with
    body `{"packageName": "{pkg}"}`. The query parameter is required; without it
    you get a bare INVALID_ARGUMENT.
  - `POST developerAccounts/{id}/androidPackages/{pkg}/keys` with
    `{"certificateFingerprintSha256": "<64 hex>"}`. The response carries a
    `verificationToken` (one token per developer account).
  - Ownership proof: media upload of a signed APK to
    `/upload/v1/{keyName}:verify?uploadType=media`
    (`Content-Type: application/vnd.android.package-archive`).
- **The APK must contain `assets/adi-registration.properties` holding ONLY the
  raw token and a newline.** Not `verificationToken=...`: that prefix fails the
  upload with a bare INVALID_ARGUMENT. Google's own sample
  (`android/security-samples`, `AndroidDeveloperVerificationAPKSigningExample`)
  is the reference.
- Expo/managed apps: `android/` is generated, so copy the file in with a small
  config plugin (`withDangerousMod`, platform `android`) at prebuild.
- Read the signing fingerprint with
  `apksigner verify --print-certs <apk>` (needs a JDK on PATH; `keytool
  -printcert -jarfile` fails on v2-only APKs).
- States: DRAFT -> IN_REVIEW (after the upload) -> REGISTERED (under 24 h).

## 3. Signing key continuity

- When you create the first Play release, choose **use my own key** and upload
  the existing keystore (EAS: `eas credentials -p android`, download keystore)
  as an encrypted export produced by Google's PEPK tool, rather than uploading
  the raw keystore. See [signing and internal releases](play-signing-and-release.md)
  for the validated Console procedure. If Google generates a new key, users of the
  sideloaded APK cannot update to the Play build without uninstalling.
- Keep "automatic installer protection" on. It affects only Play-delivered
  builds, not your own sideloaded APKs.

## 4. Things the policy and forms assume exist

Build these before the forms, or the forms make you state something false:

| Requirement | Why | What we built |
|---|---|---|
| In-app account deletion | Play and Apple both require it; Play also wants a web URL | Settings > Delete account, and `tn07.dev/privacy#deletion` |
| A privacy policy section per app | The consent screen and the listing both point at it; reviewers read it against the app | Per-product anchors on `tn07.dev/privacy` |
| Child safety standards page | Required for Social and Dating categories | `tn07.dev/child-safety/` |
| In-app "report a concern" | Required by the child safety standards; mailto links do NOT work inside an Android WebView shell, so it must be a form | Settings > Report a concern, stored in a table, alerted to Discord |
| Location disclosure | Any device location use, even reverse-geocoded to a city, must be in the policy and in Data safety (Approximate location) | Policy paragraph naming OpenStreetMap Nominatim |

Grep the app before answering the forms. Every one of these was found by
reading code, not by remembering it: `navigator.geolocation`, reverse geocoding,
uploads, push tokens, analytics, third-party webhooks.

## 5. Facts to verify from the built APK, not from memory

- **Advertising ID:** `aapt2 dump permissions <apk> | grep AD_ID`. No
  `com.google.android.gms.permission.AD_ID` and no ad SDK means "No".
- **Package and version:** `aapt2 dump badging <apk> | head -1`.
- **Signer:** `apksigner verify --print-certs <apk>`.

**Self-updaters must not ship to Play.** An app that updates itself from
GitHub or a bucket needs `REQUEST_INSTALL_PACKAGES`. Play blocks the release
("This release includes permissions that haven't been declared in Play
Console") and its policy forbids updating outside Play, so a declaration will
not pass review. Build a Play variant instead: an `APP_VARIANT=play` env on the
Play EAS profile, an `app.config.js` that removes the permission and adds it to
`android.blockedPermissions`, and an `extra.distribution` flag that hides the
update UI. Check `aapt2 dump permissions` on the sideloaded APK first for other
sensitive permissions (`SYSTEM_ALERT_WINDOW`, `QUERY_ALL_PACKAGES`,
`MANAGE_EXTERNAL_STORAGE`, background location) and drop unused ones from the
Play build too. Verify with `APP_VARIANT=play npx expo config --type public`.

## 6. The reviewer account

Play needs working login credentials when sign-in is required, and Target
audience is blocked until Sign in details are saved.

- Make a dedicated Google account on your own domain, not a Gmail: route
  `review@tn07.dev` with Cloudflare Email Routing (destination address verified,
  rule active, then "Add missing records" for MX, SPF and DKIM), then create the
  Google account with "Use your existing email". No phone number is needed.
- **Gmail trap:** if the app's own mail goes out through the same Gmail account
  that the alias forwards to, Gmail keeps the forwarded copy only in **Sent**.
  Look there for the sign-in code.
- Give the account real-looking data through the app itself: a human display
  name, a circle with a few items, and a second member so that shared features
  (shortlist, picks) are not empty. Do not seed through the database.
- Never reuse the reviewer password, and add no personal recovery details.

## 7. Store graphics

- Icon 512 x 512 PNG (32-bit). Feature graphic 1024 x 500.
- **Phone screenshots: the long side may be at most twice the short side.**
  A modern 412 x 915 viewport (2.22:1) is rejected; capture at 412 x 824 and
  scale to 1080 x 2160.
- Capture over CDP from a Chromium started with
  `--remote-debugging-port=9222` on a non-default profile (Chrome refuses the
  flag on the default profile). Emulate the device with
  `Emulation.setDeviceMetricsOverride`. Set the app theme through its own
  storage key to get light and dark sets, then restore the user's value.
- Put the strongest screen first: Play search shows it first. Real links (Maps,
  YouTube) beat placeholder items.
- AI-generated asset question: answer from fact. Code-rendered brand art and
  real captures are "No".

## 8. API access for later steps

- Create one service account per app (`<app>-play-publisher`), enable
  `androidpublisher.googleapis.com`, and store its JSON key straight into Secret
  Manager (`<APP>_PLAY_SA_KEY`, label `app=<app>`) without leaving it on disk.
- Invite it in Users and permissions with **no account permissions** and Admin
  on **that one app only**. On a shared developer account (another owner's
  business apps), this scoping is the whole point.
- The API covers: listing text, images, data safety (CSV), track uploads,
  rollout. It cannot create the app, upload the signing key, or answer content
  rating, target audience, ads, app access or other declarations.

## 9. Apple

See [Apple App Store](apple-app-store.md) for the full, validated procedure.
