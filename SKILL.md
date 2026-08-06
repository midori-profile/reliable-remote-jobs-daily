---
name: reliable-remote-jobs-daily
description: Scan a curated list of remote-friendly companies for engineering roles (Frontend, Backend, Fullstack, AI Agent Engineer, AI Infra Engineer, Mobile, DevOps/SRE, Data Engineer, Security Engineer) via their public ATS APIs, filtered by hiring region and role category, and publish a daily Markdown report.
user-invocable: true
argument-hint: '[region]'
---

# reliable-remote-jobs-daily

When the user invokes `/reliable-remote-jobs-daily [region]`:

1. Run `./scripts/run_daily.sh` from the repo root (it activates the venv, runs `scripts/scan.py --region APAC`, and — if there were changes — commits and pushes them).

   **Note on the `[region]` argument:** `run_daily.sh` currently always scans `APAC` (the default) — it does not yet accept a region argument. If the user passes a region other than APAC, tell them region customization isn't wired through to the daily-run wrapper yet, and don't try to work around it by calling `scripts/scan.py --region <region>` directly — `run_daily.sh`'s lock file and commit/push logic exist specifically to make automated runs safe, and bypassing it would skip that hardening for no real benefit (a bespoke-region run isn't part of the tracked daily report anyway). Just run `./scripts/run_daily.sh` as-is and note the limitation.

   **Note on role selection:** similarly, `run_daily.sh` always scans whichever categories are listed in `selected-roles.yaml` — it does not accept a `--roles` argument any more than it accepts `--region`. If the user wants a different role mix, prefer editing `selected-roles.yaml` for anything meant to be part of the tracked daily flow (that's the file that governs what `run_daily.sh` scans for by default), and only reach for `scripts/scan.py --roles <roles>` directly for a genuinely one-off manual check run outside `run_daily.sh` — not as a way to bypass the daily wrapper's locking and commit/push safety for a routine role change.

2. **Check the exit code of step 1 first, before anything else.** `run_daily.sh` uses `set -euo pipefail`, so it aborts before writing anything on any of these:
   - The lock directory already exists (another run is in progress) — tell the user a scan is already running and to try again shortly. No report was written.
   - `scan.py` itself failed (bad `companies.yaml`, every company failed to fetch, or zero companies matched the region) — in these cases **no `reports/<today>.md` file exists yet**, so don't attempt step 4 below. Show the user the actual error output from the script (it prints a specific `error: ...` line explaining which case it was) rather than guessing.
   - `git push` failed (e.g. no remote configured yet, or a credential/network issue) — a commit was created locally but not pushed; tell the user this happened so they can push manually once the issue is resolved.

   Only proceed to steps 3-5 if the script exited 0.

3. If the script reports "no changes to commit," tell the user today's report is identical to what's already published (this is expected since scans aren't deduplicated day-to-day — re-running the same day produces the same snapshot).
4. Read back the freshly written `reports/<today>.md` and summarize the top few matches in chat.
5. If the script's stderr contains `warning:` lines, mention which companies failed to parse today, so the user knows to check those manually if they care.

This skill assumes it's being run from within a clone of the `reliable-remote-jobs-daily` repo with `.venv` already set up (`pip install -r requirements.txt`). For daily automation, register this skill with Claude Code's `/schedule` skill to run once a day.
