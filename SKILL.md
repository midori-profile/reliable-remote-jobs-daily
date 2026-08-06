---
name: ts-remote-jobs
description: Scan a curated list of remote-friendly companies for TypeScript/frontend roles via their public ATS APIs, filtered by hiring region, and publish a daily Markdown report.
user-invocable: true
argument-hint: '[region]'
---

# ts-remote-jobs

When the user invokes `/ts-remote-jobs [region]`:

1. Run `./scripts/run_daily.sh` from the repo root (it activates the venv, runs `scripts/scan.py --region APAC`, and — if there were changes — commits and pushes them).

   **Note on the `[region]` argument:** `run_daily.sh` currently always scans `APAC` (the default) — it does not yet accept a region argument. If the user passes a region other than APAC, tell them region customization isn't wired through to the daily-run wrapper yet, and don't try to work around it by calling `scripts/scan.py --region <region>` directly — `run_daily.sh`'s lock file and commit/push logic exist specifically to make automated runs safe, and bypassing it would skip that hardening for no real benefit (a bespoke-region run isn't part of the tracked daily report anyway). Just run `./scripts/run_daily.sh` as-is and note the limitation.

2. **Check the exit code of step 1 first, before anything else.** `run_daily.sh` uses `set -euo pipefail`, so it aborts before writing anything on any of these:
   - The lock directory already exists (another run is in progress) — tell the user a scan is already running and to try again shortly. No report was written.
   - `scan.py` itself failed (bad `companies.yaml`, every company failed to fetch, or zero companies matched the region) — in these cases **no `reports/<today>.md` file exists yet**, so don't attempt step 4 below. Show the user the actual error output from the script (it prints a specific `error: ...` line explaining which case it was) rather than guessing.
   - `git push` failed (e.g. no remote configured yet, or a credential/network issue) — a commit was created locally but not pushed; tell the user this happened so they can push manually once the issue is resolved.

   Only proceed to steps 3-5 if the script exited 0.

3. If the script reports "no changes to commit," tell the user today's report is identical to what's already published (this is expected since scans aren't deduplicated day-to-day — re-running the same day produces the same snapshot).
4. Read back the freshly written `reports/<today>.md` and summarize the top few matches in chat.
5. If the script's stderr contains `warning:` lines, mention which companies failed to parse today, so the user knows to check those manually if they care.

This skill assumes it's being run from within a clone of the `ts-remote-jobs` repo with `.venv` already set up (`pip install -r requirements.txt`). For daily automation, register this skill with Claude Code's `/schedule` skill to run once a day.
