---
name: ts-remote-jobs
description: Scan a curated list of remote-friendly companies for TypeScript/frontend roles via their public ATS APIs, filtered by hiring region, and publish a daily Markdown report.
user-invocable: true
argument-hint: '[region, default APAC]'
---

# ts-remote-jobs

When the user invokes `/ts-remote-jobs [region]`:

1. Run `./scripts/run_daily.sh` from the repo root (it activates the venv, runs `scripts/scan.py --region APAC`, and — if there were changes — commits and pushes them).

   **Note on the `[region]` argument:** `run_daily.sh` currently always scans `APAC` — it does not yet accept a region argument. If the user passes a region other than APAC (or the default), tell them region customization isn't wired through to the daily-run wrapper yet, and don't try to work around it by calling `scripts/scan.py --region <region>` directly — `run_daily.sh`'s lock file and commit/push logic exist specifically to make automated runs safe, and bypassing it would skip that hardening for no real benefit (a bespoke-region run isn't part of the tracked daily report anyway). Just run `./scripts/run_daily.sh` as-is and note the limitation.

2. If the script reports "no changes to commit," tell the user today's report is identical to what's already published (this is expected since scans aren't deduplicated day-to-day — re-running the same day produces the same snapshot).
3. Read back the freshly written `reports/<today>.md` and summarize the top few matches in chat.
4. If the script's stderr contains `warning:` lines, mention which companies failed to parse today, so the user knows to check those manually if they care.

This skill assumes it's being run from within a clone of the `ts-remote-jobs` repo with `.venv` already set up (`pip install -r requirements.txt`). For daily automation, register this skill with Claude Code's `/schedule` skill to run once a day.
