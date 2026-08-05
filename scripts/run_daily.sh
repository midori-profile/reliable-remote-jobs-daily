#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

# Guard against overlapping runs (e.g. if a future /schedule setup ever fires
# two invocations close together, they'd otherwise race on git commit/push).
# flock isn't reliably available on macOS (this is developed on macOS), so we
# use a portable mkdir-based lock instead — mkdir is atomic on every
# filesystem we care about here. Known gap: a hard kill (kill -9) leaves the
# lock dir behind; if run_daily.sh ever refuses to start with a "lock dir
# exists" message and no other run is actually in progress, manually remove
# it with `rmdir "$LOCK_DIR"`.
LOCK_DIR="/tmp/ts-remote-jobs-run-daily.lock"
if ! mkdir "$LOCK_DIR" 2>/dev/null; then
  echo "another run_daily.sh appears to be running (lock dir exists: $LOCK_DIR); exiting" >&2
  exit 1
fi
trap 'rmdir "$LOCK_DIR"' EXIT

source .venv/bin/activate
python scripts/scan.py --region APAC

# Scope the dirty check to exactly what we're about to add/commit, so an
# unrelated uncommitted file elsewhere in the tree can't trigger a
# "nothing to commit" failure here.
if [[ -n "$(git status --porcelain -- reports/ README.md)" ]]; then
  git add reports/
  # README.md doesn't exist until Task 12 lands; guard so this script keeps
  # working before then, and still picks it up once it's present.
  [[ -f README.md ]] && git add README.md
  git commit -m "chore: daily scan $(date +%Y-%m-%d)"
  git push
else
  echo "no changes to commit"
fi
