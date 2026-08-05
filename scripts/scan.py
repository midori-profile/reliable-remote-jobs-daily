#!/usr/bin/env python3
"""Scan companies.yaml for TypeScript-relevant remote roles and write a dated report."""
import argparse
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from ts_remote_jobs.companies import load_companies, CompanyConfigError
from ts_remote_jobs.fetchers import fetch_for_company, FetchError
from ts_remote_jobs.filters import filter_jobs
from ts_remote_jobs.report import render_report
from ts_remote_jobs.readme import update_latest_scan_section, MarkersNotFoundError


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--companies-file", default="companies.yaml")
    parser.add_argument("--output-dir", default="reports")
    parser.add_argument("--readme", default="README.md")
    parser.add_argument("--region", default="APAC")
    args = parser.parse_args()

    try:
        companies = load_companies(args.companies_file)
    except CompanyConfigError as e:
        print(f"companies.yaml error: {e}", file=sys.stderr)
        return 1

    all_jobs, unparsed = [], []
    for company in companies:
        if not company.accepts_region(args.region):
            continue
        try:
            all_jobs.extend(fetch_for_company(company))
        except FetchError as e:
            print(f"warning: {e}", file=sys.stderr)
            unparsed.append(company.name)

    relevant = filter_jobs(all_jobs)
    run_date = date.today()
    report_md = render_report(relevant, unparsed, run_date=run_date)

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    report_path = output_dir / f"{run_date.isoformat()}.md"
    report_path.write_text(report_md, encoding="utf-8")
    print(f"wrote {report_path}")

    readme_path = Path(args.readme)
    if readme_path.exists():
        summary = (
            f"Found {len(relevant)} matching role(s)."
            if relevant else "No matching roles found."
        )
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
