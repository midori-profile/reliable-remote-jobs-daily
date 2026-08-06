# reliable-remote-jobs-daily

A daily-refreshed, machine-readable list of remote-friendly companies, scanned directly against their hiring systems for engineering roles across Frontend, Backend, Fullstack, AI Agent Engineer, AI Infra Engineer, Mobile, DevOps/SRE, Data Engineer, and Security Engineer — no stale job-board aggregators involved.

<!-- LATEST-SCAN:START -->
**2026-08-06** — Found 110 matching role(s).
Full report: [reports/2026-08-06.md](reports/2026-08-06.md)
<!-- LATEST-SCAN:END -->

## Why this exists

Most "remote jobs" lists are aggregator scrapes that lag days or weeks behind reality, and they're often full of scam postings and disreputable companies with no real vetting. This project takes a different approach: a curated list of real, vetted companies, each with its actual ATS (Greenhouse/Lever/Ashby/Workable) recorded, scanned directly via their public job-board APIs every day. It's also not locked to one job title — the role taxonomy covers nine engineering categories (see above), so you can point it at whichever mix of categories matches what you're actually looking for, instead of re-filtering a generic firehose yourself.

## Usage

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python scripts/scan.py --region APAC --roles frontend,backend   # or your own region/roles
```

Output lands in `reports/<date>.md`, and the "latest scan" block above this section gets updated automatically.

## Automating it daily

If you're using [Claude Code](https://claude.com/claude-code), clone this repo and use the bundled `/reliable-remote-jobs-daily` skill (see `SKILL.md`) to run a scan and summarize the results in chat, or register `scripts/run_daily.sh` with the `/schedule` skill to run once a day unattended — it activates the venv, runs the scan, and commits/pushes any new report automatically.

Note: `scripts/scan.py` accepts `--region` and `--roles` flags directly (see Usage above), but `scripts/run_daily.sh` — and therefore the `/schedule`-driven automation — currently always scans the `APAC` default region against whichever categories are listed in `selected-roles.yaml`. Neither region nor role customization is wired through to the daily wrapper; if you need a different region or role mix on a schedule, edit `selected-roles.yaml` (for roles) so it becomes part of the tracked daily flow, or run `scripts/scan.py --region <region> --roles <roles>` yourself for a one-off manual check outside `run_daily.sh`.

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

## Contributing a role category

Add an entry to `roles.yaml`:

```yaml
data_engineer:
  label: "Data Engineer"
  keywords: ["data engineer", "data pipeline", "data warehouse", "apache spark", "airflow"]
  boundary_keywords: ["etl", "sql"]
```

- `label` — the human-readable name shown in reports.
- `keywords` — plain substring matches. Safe for long/specific terms, where a false-positive substring collision is essentially impossible.
- `boundary_keywords` — word-boundary (`\b...\b`) matches. Use this for anything short or ambiguous: 2-4 letter terms, acronyms, or terms that are also common English words/word-fragments.

Put a term in `boundary_keywords` rather than `keywords` whenever it's short or ambiguous. This isn't a style preference — v0.1.0 shipped a real production bug where `"react"` was matched as a bare substring and silently matched "reactive" in a live job posting (a company describing "the **reactive** nature of the on-call rotation," nothing to do with React). Switching short/ambiguous terms to word-boundary matching fixed it. When in doubt, default to `boundary_keywords`: the cost of guessing wrong there is low (it still matches the real word, just also guards against substring false positives), while guessing wrong the other way reintroduces the exact bug above.

Word-boundary matching isn't a complete fix, either — it stops substring collisions but not whole-word ones. `"swift"` is in `boundary_keywords` for exactly this reason (it prevents substring collisions like "Swiftype" or "swiftly"), but `"swift"` (the mobile language) and `"SWIFT"` (the bank code) are both valid whole words, so a posting mentioning SWIFT payments could still match the `mobile` category. This is a known, accepted limitation of the current matcher, not something a new role entry needs to work around.

Also add the new category's key to `selected-roles.yaml`'s `selected` list if you want it included in the default daily scan — `roles.yaml` just defines what categories exist; `selected-roles.yaml` controls which of them actually get scanned for by default.

## License

MIT
