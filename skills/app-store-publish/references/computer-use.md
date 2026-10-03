# UI execution and recovery

Use the host's supported computer-use API. Read its documentation before acting and refresh it after context compaction if required. Prefer provider APIs/connectors for supported operations when available and authorized; do not invent API routes from browser internals. If the user requires UI-only execution, respect it.

## Native Chromium mechanics observed on macOS

- Bind the requested app/window through the supported API. Native app AX element indices are ephemeral; never save them as locators in this skill or a resume report.
- After an action batch, obtain fresh accessibility state before deciding the next action. Batch only deterministic operations against controls known to remain valid. Conditional selections can replace Save buttons, so inspect the new state before clicking Save.
- Navigation may initially show the old page or a loading shell. Confirm title, URL, and target app before proceeding. When an unchanged tree leaves missing context, use an allowed screenshot/full snapshot rather than repeatedly polling unchanged state.
- Prefer named AX controls. When a click fails with elementHasNoFrame, the first action may already have succeeded and replaced a later control. Inspect state before retrying to avoid toggling a selected answer off.
- cannotClickOffscreenElement calls for scrolling and refreshing state. It does not justify blind coordinates. Observe a fresh screenshot before coordinate actions.
- A native menu can trap keyboard navigation. Use its documented Cancel accessibility action if Escape does not dismiss it, then refresh state.

## Upload dialogs

The browser's asset library and macOS file picker are separate layers. Observe each after opening. Go to Folder can be reached with the normal system shortcut; set the visible path field with the supported API. In the source workflow, paste did not populate that native field but setValue did. Do not assume that workaround is necessary in every host.

Observe actual filenames, select only intended files, and confirm upload completion before choosing assets for a slot. The native picker can select multiple screenshot files, but the browser's asynchronous upload order may differ. Recheck ordered selection in the asset library and final listing.

## Crash/session recovery

An observed Chromium 150 macOS crash aborted on the browser main thread during NSAccessibility attribute reads; the crash report attributed the incoming request to SkyComputerUseService. That supports an accessibility-query-triggered browser bug, but unsymbolicated frames do not reveal the exact assertion. Do not diagnose memory exhaustion, profile corruption, cookie loss, or a universal Chromium bug from that report alone.

On a crash or unexpected window change:
1. Preserve the last confirmed save and the exact outstanding step in the report.
2. Reconnect through the supported app API and inspect window title, URL, account, and app. A newly launched Chromium window may have a different profile/session from the crashed process.
3. Use observed window/profile menus to find the intended session. Avoid interacting with unrelated windows.
4. If login is required, ask the user to restore the developer account when credentials or verification are unavailable or require handoff. Reviewer credentials are not developer-account credentials.
5. After recovery, inspect persisted state and resume the pending step. Do not recreate the app, invite another user, re-accept agreements, or repeat release submissions.

For an ambiguous write (no success indication before crash), read resulting state before any retry. A failed observation is not evidence a save failed. If the same native AX path crashes repeatedly, stop repeating it; use another permitted supported surface or hand off the affected step. Do not disable security protections, wipe profiles, install browsers, or change authentication to recover a form.
