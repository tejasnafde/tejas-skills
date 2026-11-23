# Pre-submission checks

Run these before every first submission and before each update that changes
native code, permissions, SDKs, login, payments or store text. The other
references record how to do the console work. This file catches the rejection
before it happens.

Each item names the rule it comes from and links the official source. Dates
were checked against those sources on 2026-11-23. Requirements move every year:
when a date here has passed or a source says something else, trust the source
and fix this file.

The idea for this list came from the community repo `mjmirza/app-store-compliance`
(124 rejection patterns, 112 dated deadlines). Its license is not open source,
so nothing is copied from it. Use it as a second opinion, not as a source.

## 1. Run a scanner first

[`RevylAI/greenlight`](https://github.com/RevylAI/greenlight) (MIT, Go) scans
source, `PrivacyInfo.xcprivacy`, Info.plist, Gradle, the merged Android manifest
inside an APK or AAB, and an IPA. It runs offline and needs no account.

```sh
brew install revylai/tap/greenlight
greenlight preflight . --exit-code                     # source tree
greenlight preflight . --aab app-release.aab --exit-code
greenlight preflight . --ipa build.ipa --exit-code
greenlight preflight . --format json --output greenlight.json
```

- `--exit-code` fails on CRITICAL and HIGH findings, and on a scanner that
  crashed. Fix or explain every CRITICAL and HIGH finding before you submit.
- Scan the built artifact as well as the source. Only the artifact shows the
  merged manifest (permissions that SDKs add) and the 16 KB alignment of native
  libraries.
- It is a pattern scanner. A clean result does not prove that a flow works: a
  "Delete account" button wired to nothing passes. The manual checks below
  still apply.
- `--verify` runs flows on Revyl's cloud devices. It needs a Revyl account and
  uploads the build. Do not use it unless the user asks.
- **Its rules can be stale.** v0.2.0 (2026-07-28) knows Play target API 36 from
  2026-08-31 and Play Billing 8. It does not know Apple changes after August
  2026, for example the age rating descriptors below. Check its latest release
  date before you trust a "pass" on a dated rule.
- Record the greenlight version and its CRITICAL and HIGH findings in the
  setup report.

## 2. Both stores

- [ ] **Reviewer access works.** A dedicated account, no 2FA or OTP the reviewer
  cannot receive, real-looking data, and notes that say how to reach every gated
  feature. Apple 2.1, [Play App access](https://support.google.com/googleplay/android-developer/answer/9859455).
  See `before-the-console.md` section 6.
- [ ] **Release build is clean.** No staging or localhost backend, no debug menu,
  no placeholder text, no "coming soon" screens. Apple 2.1 and 2.3.
- [ ] **Account deletion** is in the app, deletes (not only deactivates) the
  account, and is not a mailto link. Play also needs a web URL.
  Apple 5.1.1(v), [Play account deletion](https://support.google.com/googleplay/android-developer/answer/13327111).
- [ ] **Privacy disclosures match the build, including every SDK.** Apple App
  Privacy and Play Data safety. Read the code and the built manifest, not memory
  (see `before-the-console.md` sections 4 and 5).
  [Apple](https://developer.apple.com/app-store/user-privacy-and-data-use/),
  [Play User Data](https://support.google.com/googleplay/android-developer/answer/10144311).
- [ ] **Third-party AI is disclosed and consented.** Name the provider, list the
  data sent, and ask before the first send. Apple 5.1.2(i). See
  `apple-app-store.md`, "Third-party AI disclosure".
- [ ] **Generative AI features** have a way to report offensive output and
  safeguards against harmful content.
  [Play AI-Generated Content](https://support.google.com/googleplay/android-developer/answer/14094294).
- [ ] **Store text** promises no future features, names no other platform
  ("also on Android"), and matches what the app does. Apple 2.3.

## 3. Apple

Sources: [App Review Guidelines](https://developer.apple.com/app-store/review/guidelines/),
[Upcoming requirements](https://developer.apple.com/news/upcoming-requirements/).

- [ ] **Build tools.** Since 2026-04-28, uploads need Xcode 26 and the 26 SDKs.
  Since 2026-09-09, iOS apps must target iOS 13 or later. With EAS, check the
  image of the build profile.
- [ ] **Privacy manifest.** `PrivacyInfo.xcprivacy` is present and valid, every
  required-reason API the app or its SDKs call is declared, and third-party SDKs
  ship their own manifests.
  [Privacy manifest files](https://developer.apple.com/documentation/bundleresources/privacy-manifest-files),
  [Required reason APIs](https://developer.apple.com/documentation/bundleresources/describing-use-of-required-reason-api),
  [TN3181](https://developer.apple.com/documentation/technotes/tn3181-debugging-invalid-privacy-manifest).
- [ ] **Purpose strings** for every capability the app or its WebView can reach,
  each saying what the app does with it. A pre-permission screen must not have a
  button titled "Allow". Apple 5.1.1(ii). See `apple-app-store.md`.
- [ ] **Age rating questionnaire is current.** The new age rating system applies
  since 2026-01-31. From 2026-11-16 it adds two descriptors, Shared Location and
  Dating and Relationships; every app must answer them by **2027-01-12**, and
  Dating and Relationships means 18+. An app where users share their location
  with a circle or group has Shared Location.
  [Apple news](https://developer.apple.com/news/?id=yxkh08us),
  [Set an age rating](https://developer.apple.com/help/app-store-connect/manage-app-information/set-an-app-age-rating).
- [ ] **4.2 Minimum functionality.** A WebView shell must do more than show the
  website: native sign-in, push, share extension, offline state or device
  features. Write in the review notes what the app does that the website cannot.
- [ ] **4.3 Spam.** No second app that is the same app with new branding.
- [ ] **4.0 Design on iPad.** An iPhone-only app is still reviewed on an iPad, in
  a window as small as 320 x 480 points. See `apple-app-store.md`.
- [ ] **4.8 Login services.** If the app offers Google or another social login,
  it also offers Sign in with Apple, and the backend accepts
  `privaterelay.appleid.com` addresses.
- [ ] **3.1.1 / 3.1.2 Payments.** Digital goods use In-App Purchase. Non-consumables
  and subscriptions have a Restore Purchases control. The billed price is the most
  prominent price, and the Terms and Privacy links work. No external tip or
  donation link.
- [ ] **5.1.2 Tracking.** An SDK that tracks across apps needs the App Tracking
  Transparency prompt and `NSUserTrackingUsageDescription`.
- [ ] **2.5.5 IPv6.** The app works on an IPv6-only network. Hard-coded IPv4
  addresses fail review.
- [ ] **Export compliance.** `ITSAppUsesNonExemptEncryption` is set.
- [ ] **EU trader status** is declared before the app is offered in the EU (Digital
  Services Act). [Apple DSA trader requirements](https://developer.apple.com/help/app-store-connect/manage-compliance-information/manage-european-union-digital-services-act-trader-requirements).

## 4. Google Play

- [ ] **Target API.** Since 2026-08-31, new apps and updates must target API 36
  (Wear OS and Automotive 35, TV and XR 34). An extension to 2026-11-01 was
  available on request. Existing apps below API 35 stop reaching new users on
  newer devices. [Target API level](https://support.google.com/googleplay/android-developer/answer/11926878).
- [ ] **Play Billing Library 8 or later** if the app sells anything.
  [Deprecation FAQ](https://developer.android.com/google/play/billing/deprecation-faq).
- [ ] **16 KB page size.** Native libraries for apps that target Android 15 or
  later must support 16 KB pages. Check the AAB with greenlight.
  [Page sizes](https://developer.android.com/guide/practices/page-sizes).
- [ ] **Restricted permissions.** Photos and videos use the Photo Picker unless
  media access is the core feature; no `QUERY_ALL_PACKAGES`,
  `MANAGE_EXTERNAL_STORAGE`, background location, SMS or Call Log without a
  declared core use. Check the merged manifest of the built AAB.
  [Restricted permissions](https://support.google.com/googleplay/android-developer/answer/14115180),
  [Sensitive permissions](https://support.google.com/googleplay/android-developer/answer/9888170).
- [ ] **Exact alarms.** `SCHEDULE_EXACT_ALARM` is denied by default from Android 14;
  `USE_EXACT_ALARM` is only for alarm and calendar apps.
  [Exact alarms](https://developer.android.com/about/versions/14/changes/schedule-exact-alarms).
- [ ] **Foreground services** each declare a type and the matching
  `FOREGROUND_SERVICE_*` permission; `specialUse` needs a subtype. Play Console
  asks for a declaration per type.
  [Service types](https://developer.android.com/develop/background-work/services/fgs/service-types).
- [ ] **Advertising ID** answered from the built manifest (`AD_ID` permission),
  not from "we have no ads". See `before-the-console.md` section 5.
- [ ] **No self-updater** and no `REQUEST_INSTALL_PACKAGES` in the Play build.
  See `before-the-console.md` section 5.
- [ ] **Release build** is not debuggable, ships 64-bit native libraries, and
  has a rising versionCode.
- [ ] **Developer verification.** Every package name, including sideloaded ones,
  is registered to the verified developer.
  [Developer verification](https://developer.android.com/developer-verification).
  See `before-the-console.md` section 2.
- [ ] **Personal accounts only:** a personal developer account created after
  2023-11-13 must run a closed test with at least 12 testers opted in for 14
  days in a row before it can apply for production. An organization account is
  exempt. Plan this two weeks ahead.
  [Testing requirements](https://support.google.com/googleplay/android-developer/answer/14151465).

## 5. Record the result

Add a "Pre-submission" section to the setup report: the date, the greenlight
version and its findings, each checklist item as pass, fail, or not applicable
with one line of evidence, and every item you could not check.
