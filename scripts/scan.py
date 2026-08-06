#!/usr/bin/env python3
"""Scan companies.yaml for roles matching the selected categories and write a dated report."""
import argparse
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from remote_jobs_daily.companies import load_companies, CompanyConfigError
from remote_jobs_daily.roles import load_roles, RoleConfigError
from remote_jobs_daily.selected_roles import load_selected_roles, SelectedRolesError
from remote_jobs_daily.fetchers import fetch_for_company, FetchError
from remote_jobs_daily.filters import categorize_jobs
from remote_jobs_daily.report import render_report
from remote_jobs_daily.readme import update_latest_scan_section, MarkersNotFoundError


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--companies-file", default="companies.yaml")
    parser.add_argument("--roles-file", default="roles.yaml")
    parser.add_argument("--selected-roles-file", default="selected-roles.yaml")
    parser.add_argument("--roles", default=None, help="comma-separated category keys, overrides --selected-roles-file")
    parser.add_argument("--output-dir", default="reports")
    parser.add_argument("--readme", default="README.md")
    parser.add_argument("--region", default="APAC")
    args = parser.parse_args(argv)

    try:
        companies = load_companies(args.companies_file)
    except CompanyConfigError as e:
        print(f"companies.yaml error: {e}", file=sys.stderr)
        return 1

    try:
        roles = load_roles(args.roles_file)
    except RoleConfigError as e:
        print(f"roles.yaml error: {e}", file=sys.stderr)
        return 1

    if args.roles:
        selected = [key.strip() for key in args.roles.split(",") if key.strip()]
        unknown = [key for key in selected if key not in roles]
        if unknown:
            print(f"error: unknown role key(s) in --roles: {', '.join(unknown)}", file=sys.stderr)
            return 1
    else:
        try:
            selected = load_selected_roles(args.selected_roles_file, roles)
        except SelectedRolesError as e:
            print(f"selected-roles.yaml error: {e}", file=sys.stderr)
            return 1

    attempted = 0
    all_jobs, unparsed = [], []
    for company in companies:
        if not company.accepts_region(args.region):
            continue
        attempted += 1
        try:
            all_jobs.extend(fetch_for_company(company))
        except FetchError as e:
            print(f"warning: {e}", file=sys.stderr)
            unparsed.append(company.name)

    if attempted == 0:
        print(
            f"error: no companies were attempted for region '{args.region}' "
            "(every company was filtered out — check for a --region typo) — "
            "aborting without writing a report",
            file=sys.stderr,
        )
        return 1
    if unparsed and len(unparsed) == attempted:
        print(
            f"error: all {len(unparsed)} attempted companies failed to fetch — "
            "aborting without writing a report",
            file=sys.stderr,
        )
        return 1

    grouped = categorize_jobs(all_jobs, roles, selected)
    categorized = [(roles[key].label, grouped[key]) for key in selected]
    total_relevant = sum(len(jobs) for _, jobs in categorized)

    run_date = date.today()
    report_md = render_report(categorized, unparsed, run_date=run_date)

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    report_path = output_dir / f"{run_date.isoformat()}.md"
    report_path.write_text(report_md, encoding="utf-8")
    print(f"wrote {report_path}")

    readme_path = Path(args.readme)
    if readme_path.exists():
        if unparsed:
            summary = (
                f"Found {total_relevant} matching role(s). "
                f"({len(unparsed)} of {attempted} companies could not be parsed.)"
            )
        elif total_relevant:
            summary = f"Found {total_relevant} matching role(s)."
        else:
            summary = "No matching roles found."
        try:
            updated = update_latest_scan_section(
                readme_path.read_text(encoding="utf-8"),
                summary=summary,
                report_path=str(report_path),
                run_date=run_date,
            )
            readme_path.write_text(updated, encoding="utf-8")
            print(f"updated {readme_path}")
        except MarkersNotFoundError as e:
            print(f"warning: {e}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
