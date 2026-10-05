# UI execution and recovery

Use the host's supported computer-use API. Read its documentation before acting and refresh it after context compaction if required. Prefer provider APIs/connectors for supported operations when available and authorized; do not invent API routes from browser internals. If the user requires UI-only execution, respect it.

## Native Chromium mechanics observed on macOS

- Bind the requested app/window through the supported API. Native app AX element indices are ephemeral; never save them as locators in this skill or a resume report.
- After an action batch, obtain fresh accessibility state before deciding the next action. Batch only deterministic operations against controls known to remain valid. Conditional selections can replace Save buttons, so inspect the new state before clicking Save.
- Navigation may initially show the old page or a loading shell. Confirm title, URL, and target app before proceeding. When an unchanged tree leaves missing context, use an allowed screenshot/full snapshot rather than repeatedly polling unchanged state.
- Prefer named AX controls. When a click fails with elementHasNoFrame, the first action may already have succeeded and replaced a later control. Inspect state before retrying to avoid toggling a selected answer off.
- cannotClickOffscreenElement calls for scrolling and refreshing state. It does not justify blind coordinates. Observe a fresh screenshot before coordinate actions.
- If the tool reports `frontmostApplicationChanged` or “The user changed” the app, rebind the app and observe current state before retrying. Inspect whether the write happened; do not assume failure.
- A text-area click can leave focus on the page; Select All then selects page text instead of the field. Verify the actual field value after entry. A supported setValue operation worked for release notes in the observed workflow.
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

## Running Codex computer use headless (no human relaying messages)

**Start a FRESH session scoped to the projects folder (validated 2026-10-05, scout):**

```sh
codex exec -C ~/Desktop/projects --skip-git-repo-check \
  -c sandbox_mode='"workspace-write"' "<task>" < /dev/null
```

`< /dev/null` matters when the caller runs it in the background: with an open
stdin, `codex exec` prints "Reading additional input from stdin..." and waits
forever without starting the task.

A fresh `codex exec` loads the `cua_repl` MCP server and binds
`org.chromium.Chromium` with no prompt once the user has chosen "always allow"
for Chromium in the desktop app. Resuming the older Someday session
(`codex exec resume <id>`) loaded the stale `node_repl` server instead and failed
with "cua is undefined", even with `SkyComputerUseService` running. Prefer a
fresh session; probe first with a read-only task ("bind Chromium, report the
window title, click nothing"). `-C ~/Desktop/projects` lets the agent read the
skill and write its report into the app repo instead of `/tmp`.

**Computer use in another Codex home** (`CODEX_HOME`, for example a second
account; validated 2026-10-05 on `~/.codex-lenskart`, an Enterprise login).
Enabling the plugin in config is not enough, and `codex plugin marketplace add`
refuses the name `openai-bundled` ("reserved"). What works:

```sh
H=~/.codex-lenskart
mkdir -p $H/.tmp/bundled-marketplaces
cp -R ~/.codex/.tmp/bundled-marketplaces/openai-bundled $H/.tmp/bundled-marketplaces/
# must include the hidden .agents/plugins/marketplace.json; ChatGPT.app's
# Resources/plugins copy lacks it, so copy from a home the desktop app materialized
printf '\n[marketplaces.openai-bundled]\nsource_type = "local"\nsource = "%s/.tmp/bundled-marketplaces/openai-bundled"\n' "$H" >> $H/config.toml
CODEX_HOME=$H codex plugin add computer-use@openai-bundled
```

Then copy the whole `[mcp_servers.node_repl]` and `[mcp_servers.node_repl.env]`
blocks from `~/.codex/config.toml`, changing `CODEX_HOME` and the first entry of
`NODE_REPL_TRUSTED_CODE_PATHS` to the new home. Without `node_repl` the skill
loads but says its tool is absent. No grant file is needed: the "always allow"
for Chromium lives in the Computer Use service, not in a Codex home. Probe with
a read-only task before real work.

The notes below are from the first run (2026-10-03) and explain resume, which is
now the fallback, not the default.

Learned 2026-10-03, Codex CLI 0.160 with the ChatGPT desktop app installed.

- `codex exec` gets the computer-use tool (`mcp__cua_repl.js`) only from a
  Codex home that has the bundled `computer-use` plugin enabled. The desktop
  app uses the default `~/.codex`; a separate `CODEX_HOME` without the plugin
  has no such tool and the agent says so.
- App access is granted PER SESSION, by the user, in the desktop UI. The grant
  lives in `~/.codex/computer-use/sessions/<session-id>.toml`
  (`[apps] allowed = ["org.chromium.Chromium"]`). A fresh `codex exec` session
  has no grant and fails with "Computer Use was not approved to use <app>".
  Do not write grant files for new sessions: that bypasses the user's consent.
- Instead continue the session where the user granted access:
  `codex exec resume <session-id> --skip-git-repo-check -c sandbox_mode='"workspace-write"' "<task>"`.
  The desktop app holds that session open ("already has an active writer"),
  so quit the app first (`osascript -e 'tell application "ChatGPT" to quit'`).
  The chat history stays on disk.
- `exec` defaults to a read-only sandbox, so the agent cannot write its report
  file. Pass `sandbox_mode` workspace-write (it covers `/tmp`).
- An automatic approval reviewer checks consequential clicks against the
  latest instruction's scope. A narrow instruction ("change nothing else")
  blocks Play's "Submit N changes for review", which bundles every pending
  change. For a first release, state explicitly that the user's approval
  covers the release together with the first-time setup (listing, countries,
  declarations), or it stops.
- The Mac must stay awake and unlocked while it works.
