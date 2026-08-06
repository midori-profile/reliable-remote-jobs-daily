# ts-remote-jobs

A daily-refreshed, machine-readable list of remote-friendly (but not big-tech) companies, scanned directly against their hiring systems for TypeScript/frontend roles — no stale job-board aggregators involved.

<!-- LATEST-SCAN:START -->
(no scan yet — run `scripts/run_daily.sh`)
<!-- LATEST-SCAN:END -->

## Why this exists

Most "remote jobs" lists are aggregator scrapes that lag days or weeks behind reality, and most searches for "Hong Kong Remote" / "APAC Remote" miss postings from companies that just say "Remote" or "Distributed." This project takes a different approach: a curated list of real companies (`companies.yaml`, currently 34 of them — GitLab, Automattic, Zapier, Vercel, Supabase, 1Password, and more), each with its actual ATS (Greenhouse/Lever/Ashby/Workable) recorded, scanned directly via their public job-board APIs every day.

## Usage

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python scripts/scan.py --region APAC   # or your own region
```

Output lands in `reports/<date>.md`, and the "latest scan" block above this section gets updated automatically.

## Automating it daily

If you're using [Claude Code](https://claude.com/claude-code), clone this repo and use the bundled `/ts-remote-jobs` skill (see `SKILL.md`) to run a scan and summarize the results in chat, or register `scripts/run_daily.sh` with the `/schedule` skill to run once a day unattended — it activates the venv, runs the scan, and commits/pushes any new report automatically.

Note: `scripts/scan.py` accepts a `--region` flag directly (see Usage above), but `scripts/run_daily.sh` — and therefore the `/schedule`-driven automation — currently always scans the `APAC` default. Region customization isn't wired through to the daily wrapper yet; if you need a different region on a schedule, run `scripts/scan.py --region <region>` yourself rather than through `run_daily.sh`.

## Contributing a company

Add an entry to `companies.yaml`:

```yaml
- name: Your Favorite Company
  ats: greenhouse   # greenhouse | lever | ashby | workable | other
  token: their-board-token
  careers_url: https://example.com/careers
  hires_from: [Global]   # or e.g. [US, EU] if they don't hire everywhere
```

Before opening a PR, verify the token actually resolves to a real jobs payload with a live curl check against the ATS's public API, e.g.:

```bash
curl -s -o /dev/null -w "%{http_code}\n" "https://boards-api.greenhouse.io/v1/boards/<token>/jobs"
curl -s -o /dev/null -w "%{http_code}\n" "https://api.lever.co/v0/postings/<token>?mode=json"
curl -s -o /dev/null -w "%{http_code}\n" "https://api.ashbyhq.com/posting-api/job-board/<token>"
curl -s -o /dev/null -w "%{http_code}\n" "https://apply.workable.com/api/v1/widget/accounts/<token>?details=true"
```

If none of these return `200` with a real jobs payload, find the correct token from the company's actual `/careers` page (the embedded board URL usually reveals it), or fall back to `ats: other` with `careers_url` pointing at their real careers page. See `docs/plans/2026-08-05-ts-remote-jobs-implementation-plan.md` (Task 10) for the full methodology used to build the current seed list.

## License

MIT
