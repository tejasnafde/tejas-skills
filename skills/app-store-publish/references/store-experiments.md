# Store screenshots and A/B tests

Validated 2026-11-23 on one app in both stores. Read this before you make store
screenshots or start a listing test.

## Screenshot checklist

Check every frame before upload:

- No `localhost`, `127.0.0.1`, port number, `example.com` email or test name. A
  shown URL reads like production (`app.example.com/join/<short token>`). Use
  first names and hide emails.
- No grey scrim behind a sheet. Show the sheet over the plain page.
- One feature for each frame. The phone or the cropped UI fills at least 75% of
  the frame width. A partial phone (top or bottom cropped) makes the UI larger.
- A "panorama" set: an object that crosses the edge between two frames must not
  cut text. Use a picture, an icon, a heart or an avatar stack across the edge.
  Look at a crop of each edge.
- No gradient, glow or emoji unless the app itself has them. Text on a colour
  passes WCAG AA.
- Check each frame at 25% size, as the store thumbnail. The headline must read.
- Sizes: iOS 6.9" display `1320x2868` (display type `APP_IPHONE_67`); Play phone
  `1080x1920` (ratio at most 2:1).
- Render with Playwright, not `chromium --headless --screenshot`. One browser at
  a time; stop the dev server when done.

## App Store: product page optimization (API only)

All of it works through the App Store Connect API. No web UI step.

1. `POST /v2/appStoreVersionExperiments` with `name`, `platform`,
   `trafficProportion` and the `app` relationship.
2. For each variant: `POST /v1/appStoreVersionExperimentTreatments` (relationship
   `appStoreVersionExperimentV2`), then
   `POST /v1/appStoreVersionExperimentTreatmentLocalizations` for each locale.
3. Trap: the new treatment localization COPIES the live screenshot set. A second
   `POST /v1/appScreenshotSets` for the same display type returns 409. Read the
   existing set, delete its screenshots, and upload yours into it
   (`POST /v1/appScreenshots` with fileName and fileSize, PUT the
   `uploadOperations`, then PATCH `uploaded: true` with the MD5
   `sourceFileChecksum`). Wait until each `assetDeliveryState` is `COMPLETE`.
4. Trap: `trafficProportion` is at most 66. The control may not get less traffic
   than a treatment. 66 with two treatments is 34/33/33.
5. The test needs review: add it as a `reviewSubmissionItems` entry
   (`appStoreVersionExperimentV2`) to a review submission, then PATCH the
   submission `submitted: true`. Only one open submission is allowed for each
   platform; reuse an unsubmitted one.
6. After approval the state reads `APPROVED` with a start date. It ends by itself
   after 90 days.

Results: App Store Connect > App Analytics > Product Page Optimization
(impressions, conversion rate, improvement, confidence for each variant).

## Google Play: store listing experiments (Play Console only)

The Play Developer API has NO endpoint for store listing experiments. Use Play
Console: Grow users > Store presence > Store listing experiments. The direct URL
`.../store-listing-experiments` redirects to Home; open the app dashboard and
follow the menu.

- Drive Play Console with Playwright over CDP on the signed-in Chromium profile
  (see [computer use](computer-use.md)). Upload with `setInputFiles`. One Codex
  run did the whole setup this way, with no screen clicks.
- Type "Default graphics" changes only the graphics. Replace ALL phone
  screenshots in each variant and check the order after upload.
- Trap: the target metric is now only "Unique user install clicks" or "Unique
  user open clicks". "Retained first-time installers" is gone (2026-11).
- Trap: the variants' audience also caps at 66%. 66% gives 34/33/33.
- Starting the experiment also sends it to Play's quick checks.

Results: the experiment page shows each variant's metric with a range.

## Reading a test

- Wait for 90% confidence AND the same result for a week. With low traffic
  (tens of store visits a day) expect 3 to 6 weeks.
- Do not change the store listing while a test runs; a change resets it.
- Keep a control arm. Without it you learn which new set wins, not whether
  either beats the current one.
- Apply the winner in the store, then stop the test.
