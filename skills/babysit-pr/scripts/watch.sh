#!/usr/bin/env bash
# Block until the PR's state changes, print the new fingerprint, exit 0.
# Burns zero agent tokens while waiting: run it in the background.
#
#   watch.sh <pr-number-or-url> [baseline]    # baseline = fingerprint you last acted on
#   watch.sh <pr-number-or-url> --once        # print current fingerprint and exit
#   EVERY=300 (seconds between polls)
set -u
pr=${1:?usage: watch.sh <pr> [baseline|--once]}
every=${EVERY:-300}

if [[ $pr == *github.com* ]] || { [[ $pr != *bitbucket.org* ]] && git remote get-url origin 2>/dev/null | grep -q github.com; }; then
  fp() {
    gh pr view "$pr" --json state,headRefOid,mergeable,reviewDecision,statusCheckRollup,comments,reviews --jq '
      ["state=\(.state)", "head=\(.headRefOid[0:12])", "mergeable=\(.mergeable)", "review=\(.reviewDecision)",
       "checks=" + ([.statusCheckRollup[] | if (.conclusion // "") != "" then .conclusion else (.status // .state) end]
                    | group_by(.) | map("\(.[0]):\(length)") | join(",")),
       "comments=\(.comments | length)", "reviews=\(.reviews | length)"] | join(" ")'
  }
else
  fp() { bbpr "$pr" status; }
fi

last=${2:-}
if [[ -z $last || $last == --once ]]; then
  cur=$(fp) || exit 2
  [[ $last == --once ]] && { echo "$cur"; exit 0; }
  last=$cur
fi

while sleep "$every"; do
  now=$(fp 2>/dev/null) || continue  # ponytail: API blips just retry next tick
  [[ $now != "$last" ]] && { echo "$now"; exit 0; }
done
