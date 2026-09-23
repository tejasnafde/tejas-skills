---
name: babysit-pr
description: >-
  Watch an open pull request until it is merged or closed: fix CI failures caused
  by the branch, address actionable review comments (CodeRabbit, bots, humans),
  resolve conflicts, and wake up only when the PR actually changes. Works with
  GitHub (gh) and Bitbucket (bbpr). Use when the user says "babysit this PR",
  "watch my PR", "keep an eye on CI", "handle the review comments", or pastes a
  PR URL and asks you to see it through.
user-invocable: true
argument-hint: "[pr-number-or-url]"
---

# Babysit PR

See a PR through to merged/closed. Waiting is done by a shell script, not by you,
so a quiet PR costs zero tokens.

## Setup

1. **Target**: the argument, or the current branch's PR
   (`gh pr view --json number` / ask the user for the Bitbucket PR number).
2. **Platform**: `github.com` in the URL or `git remote get-url origin` means GitHub
   (`gh`), `bitbucket.org` means Bitbucket (`bbpr`).
3. **Branch**: be on the PR's head branch. If there are unrelated uncommitted
   changes, stop and ask.

## Loop

1. **Snapshot**: `scripts/watch.sh <pr> --once` prints the fingerprint
   (state, head, CI counts, comment counts). Take it *before* acting so nothing
   that lands while you work gets missed.
2. **Act** on the current state (see Handling below).
3. **Wait**: run `scripts/watch.sh <pr> "<fingerprint>"` **in the background**
   (Claude Code: Bash with `run_in_background: true`). It polls every 5 min
   (`EVERY=` to change), prints the new fingerprint, and exits when anything
   changes. Your own push counts as a change. That's fine.
4. **When it exits**, diff the fingerprints, fetch only what changed, handle it,
   and go back to step 3 with the new fingerprint as the baseline. Don't poll by
   hand, don't sleep, and don't
   re-read the whole PR every time you wake.

Stop when `state` is MERGED/CLOSED/DECLINED, or when you're blocked and need the
user. Green, mergeable and review-clean is **not** a stop. Say so once
("🚀 green + clean, still watching for reviews") and keep watching.

## Handling

Order: review comments → conflicts → CI. A pushed fix re-triggers CI, so don't
re-run flaky checks on a SHA you're about to replace.

### Review comments

GitHub:

```bash
# unresolved threads (id = thread id for resolving)
gh api graphql -F o=OWNER -F r=REPO -F n=N -f query='query($o:String!,$r:String!,$n:Int!){repository(owner:$o,name:$r){pullRequest(number:$n){reviewThreads(first:100){nodes{id isResolved path line comments(first:10){nodes{databaseId author{login} body}}}}}}}' \
  --jq '.data.repository.pullRequest.reviewThreads.nodes[] | select(.isResolved | not)'
# latest review bodies (CodeRabbit nitpicks live here)
gh pr view N --json reviews --jq '.reviews[-3:][] | {author: .author.login, state, body}'
# resolve / reply
gh api graphql -F id=THREAD_ID -f query='mutation($id:ID!){resolveReviewThread(input:{threadId:$id}){thread{isResolved}}}'
gh api repos/OWNER/REPO/pulls/N/comments/COMMENT_DATABASE_ID/replies -f body='...'
```

Bitbucket:

```bash
bbpr N comments                      # skip [resolved]; #id is the thread id
bbpr N resolve <id>
bbpr N comment --reply-to <id> -m '...'
```

- **CodeRabbit** (`coderabbitai`): its inline threads are the actionable ones. Fix
  them if they're correct, push, then resolve the thread. Nitpicks live in the
  review body under "Nitpick comments". **Don't fix those.** List them for the
  user in one line each. If a CodeRabbit comment is wrong, reply with a one-line
  reason and resolve it.
- **Other bots**: treat like CodeRabbit.
- **Humans**: fix a request if it's clear and correct. Never reply to or resolve a
  human's thread without the user approving the exact text. For disagreements,
  questions, or anything ambiguous, show it to the user with a suggested reply.

### Conflicts

- GitHub: `mergeable=CONFLICTING`.
- Bitbucket: `git fetch origin <target> && git merge-tree --write-tree HEAD origin/<target> >/dev/null || echo conflict`.

Fix by **merging** the target into the branch (never rebase, never force-push).
Resolve trivial conflicts. For anything touching logic you didn't write, ask.

### CI

- GitHub: `gh pr checks N`, then `gh run view <run-id> --log-failed | tail -80`.
- Bitbucket: `bbpr N builds` gives each build's state and link (usually Google
  Cloud Build). Don't dig for logs or reproduce locally. Hand the user the failing
  build's link and stop on CI until they say what to do.

Classify from the log:
- **Branch-caused** (compile, test, lint or typecheck failing in touched code):
  fix, commit, push.
- **Flaky or infra** (timeouts, runner or network errors, failures in untouched
  code): GitHub gets one `gh run rerun <run-id> --failed` per SHA. Never edit tests, CI config or pins to make an unrelated failure go
  away.
- Same failure after a retry, or you can't tell: stop and ask.

## Rules

- Commit messages say what was fixed (`Fix null check flagged in review`). Push
  normally.
- Don't close, reopen, merge, draft/undraft, or approve the PR.
- Keep updates to what changed. Say nothing on quiet wakes that needed no action.
- **Final summary** (only at stop): final SHA, CI state, fixes pushed, reruns
  used, and anything still open for the user.
