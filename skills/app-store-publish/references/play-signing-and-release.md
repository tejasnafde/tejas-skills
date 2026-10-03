# Play signing and internal releases

Observed in October 2026. Reuse the checks and boundaries, not app-specific paths, IDs, fingerprints, tester addresses, or policy answers. Inspect current UI labels each time. This procedure does not authorize signing changes or distribution by itself.

## Signing preparation versus enrollment

App integrity may redirect to **Protected with Play**. In the observed UI: expand **Play Store protection**, then **Protect app signing key / Releases signed by Play → Manage Play app signing**. Verify the target app/package before changing anything.

A draft app can already show a Google-generated signing key **In use**, even before a bundle upload. Do not assume that opening a draft means signing is unset. **Change key** opens a warning that existing internal/closed users must reinstall and previously uploaded versions become unusable. Obtain authorization for that consequential change under the current host rules. A request merely to download export instructions does not authorize committing a key change. Zero install base is evidence about current impact, not a general permission to change keys.

Choose **Export and upload a key from Java keystore** when the user wants that source. The preferences dialog exposes:
- Download encryption public key (`encryption_public_key.pem` in the observed run).
- Download PEPK tool (`pepk.jar`).
- A command with keystore, alias, output ZIP, and encryption-key-path placeholders.
- Upload generated ZIP; optional separate upload certificate instructions; final Save.

Record the exact command from the live page; do not substitute this example as an app's live command:

```sh
$ java -jar pepk.jar --keystore=foo.keystore --alias=foo --output=output.zip --include-cert --rsa-aes-encryption --encryption-key-path=/path/to/encryption_public_key.pem
```

The `$` is a shell prompt marker. The tool and public encryption key are preparation downloads; neither is the signing upload. Downloading them or selecting the radio button does not complete enrollment. Verify actual saved filenames/locations because repeat downloads can add suffixes. For a download-only request, stop before export, upload, or final Save.

## Upload and verify an existing key

The required upload is the PEPK-generated encrypted ZIP from the intended existing signing key. If the user supplies it, use that ZIP without accessing the raw keystore or requesting its password. If it is absent, ask for its path or the information needed to prepare it; continue independent tester/draft setup where possible. Do not generate a replacement key to resolve a missing export.

With explicit upload/save authorization, use **Upload generated ZIP**, verify the chosen filename, and Save. The observed success message was **App signing key changed**. An optional separate upload key is a distinct choice; don't create one without scope.

Verify the resulting app signing certificate against the certificate in the supplied ZIP or the intended existing APK. The observed PEPK ZIP contained `encryptedPrivateKey` and `certificate.pem`; inspect only the public certificate for comparison. Compare SHA-256 with the current **app signing** certificate (also exposed in Digital Asset Links JSON). Checking only **Upload key certificate** is insufficient: upload keys and distribution signing keys can differ. Record the matching public fingerprint and evidence, without private key contents or passwords.

## Internal testers

On the target app's **Internal testing → Testers**, inspect existing lists before creating one. Create the requested list with exactly the supplied addresses, commit the addresses to the list, and verify its count. Console may explain that email lists are reusable across all apps in the developer account; this does not select the list for other apps.

Save the list dialog and any Create confirmation, then inspect track selection. New lists can become selected automatically. Select only the requested list(s), leave unrelated lists unchanged, and use the parent **Save**. Verify persisted checkbox state and **Changes updated** or the completed Select testers task. List creation and track selection are separate saves.

## Bundle and release draft

Reuse an existing matching draft instead of creating duplicates. Upload the exact authorized AAB to the specified track. Wait for both transfer and distribution optimization to finish: 100% uploaded is not validation completion. The UI warns that leaving during transfer cancels the upload; after transfer it may permit leaving while optimization runs.

Verify the artifact row's versionCode/versionName, and record SDK or validation details where relevant. Preserve the user’s release name. Enter localized notes inside the Console's language tags, for example `<en-US>…</en-US>`, and verify the actual field and language count. Then **Save as draft**; the observed confirmation was **Changes saved. You can now preview your release before publishing it.**

The observed review action was **Next → Preview and confirm**, rather than a button literally named Review release. This preview is distinct from submitting the app for Google review or distributing it. Expand **Errors, warnings and messages** and report all displayed issues word for word with their version codes. Do not treat warnings as errors or silently modify the supplied build to remove them.

One observed warning concerned a missing deobfuscation file despite native debug symbols being attached. These are separate artifacts. Report the actual warning and whether the current page permits proceeding; do not infer it is safe or blocking solely from this historical example.

## Publication boundary and verification

The final internal rollout action may be **Save and publish**, with **Changes made will be published to Google Play immediately**, rather than Start rollout to Internal testing. Treat the consequence as the boundary regardless of the label. If the user asked to stop before rollout, stop here and request approval for the concrete release. Approval to preview does not authorize publishing. After publication approval, complete the matching confirmation dialog; in the observed run it repeated **Save and publish** and warned that visibility usually takes an hour but can take longer.

Verify on Internal testing Releases:
- Exact release name/version code.
- Track **Active** and release **Available to internal testers**.
- Displayed release time and review status.

Do not claim success from the button click alone. If the result is ambiguous, read the track before retrying. **Not reviewed** and a temporary package-based app name can coexist with internal availability; internal distribution is not production publication or completed app review.

Open **Testers**, use **Copy link**, verify **Web link copied**, and record the exact opt-in URL in the report. Preserve tester selection. Console availability is not evidence of an installation tested on a device; distinguish these. Do not promote the release or touch Closed testing, Open testing, or Production unless separately authorized.

## Off-console steps around signing and release

The Console steps above assume these are already true. Learned on the same run.

**Timing of the key change.** Enroll your own signing key before the first
bundle upload. At that point the install base is 0% and nothing has been
uploaded, so the reinstall warning has no real effect. After the first upload
it does. Still get explicit authorization for the change.

**Getting the keystore out of EAS (Expo).**
- `eas credentials -p android`, then the profile, then Keystore, then Download
  existing keystore. Answer yes to "display the sensitive information", or the
  passwords are not shown. The command has no non-interactive download, so the
  user runs it.
- It writes `@<owner>__<slug>.jks` into the current directory, and a repeat run
  renames the old file to `..._OLD_1.jks`. Move every copy out of the repo at
  once (`~/Documents/keys/`, mode 600), compare copies with `cmp`, and add
  `*.jks`, `*.keystore` and the service-account key file to `.gitignore`.
- Ask the user to store the keystore file and both passwords in a password
  manager. Losing the key means the app can never be updated.
- PEPK needs a JDK. On a Mac without `java` on PATH, call it by full path
  (`/opt/homebrew/opt/openjdk@21/libexec/openjdk.jdk/Contents/Home/bin/java`).
  Run it in the user's own terminal, so the passwords go only into PEPK. Write
  the zip next to the keystore, outside any repo.

**Check the signer before upload, not only after enrollment.**
`keytool -printcert -jarfile app.aab` must show the same SHA-256 as the key
registered for Android developer verification and as the PEPK certificate.

**Build setup (Expo/EAS).**
- Play needs an AAB and a strictly rising versionCode. Add a separate build
  profile (for example `play`, `extends` the APK profile, `buildType:
  app-bundle`) and set `cli.appVersionSource: remote` with `autoIncrement`, or
  every build reuses versionCode 1.
- If anything publishes finished builds automatically (an EAS webhook that
  creates GitHub releases for an in-app updater), make it publish only the APK
  profile and only `.apk` artifacts, BEFORE the first AAB build. Otherwise the
  AAB reaches every installed app as a broken "APK".

**Tester device troubleshooting.**
- "Item not found" on the store page right after the first internal release is
  normal propagation. It can take minutes to hours. Confirm the opt-in page
  says "You're a tester", that the Play Store app's active account is on the
  list, and wait.
- A tester who taps "Leave test program" re-joins from the same opt-in link.
  No Console change is needed while their address stays on the list.
- The test that matters: the Play build installs as an **Update** over the
  sideloaded APK, without uninstalling, and the user stays signed in. That
  proves key continuity.

**Later releases from CI.**
- Prove the service account first: open an edit with the Play Developer API
  (`POST .../applications/<pkg>/edits`), read the internal track, then delete
  the edit. Delete returns an empty body.
- A manual workflow (`workflow_dispatch`) is enough: `eas build --profile play
  --wait`, write the key from a GitHub secret to a file, `eas submit --profile
  play --latest` to the internal track as a draft, delete the file. Manual,
  because every run spends an EAS build.
- Store the key once in Secret Manager and pipe it into `gh secret set`; it
  never needs to touch the disk.

**Plan the human checkpoints.** Computer-use agents stop for confirmation at
legal agreements (Developer Program Policies, IARC), new admin grants, signing
key changes and publishing, even with prior authority. Expect about five stops
in a first release, and give the user exact messages to paste, so that each
stop takes seconds.
