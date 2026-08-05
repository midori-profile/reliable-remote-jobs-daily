from datetime import date

from ts_remote_jobs.report import render_report
from ts_remote_jobs.fetchers import JobPosting


def test_render_report_lists_jobs_and_unparsed():
    jobs = [
        JobPosting("GitLab", "TypeScript Engineer", "Remote - APAC",
                   "https://x.example.com/1", "greenhouse", ""),
    ]
    unparsed = ["Acme Custom Corp"]

    md = render_report(jobs, unparsed, run_date=date(2026, 8, 5))

    assert "# TypeScript Remote Jobs — 2026-08-05" in md
    assert "| GitLab | TypeScript Engineer | Remote - APAC |" in md
    assert "[Apply](https://x.example.com/1)" in md
    assert "## 未能解析" in md
    assert "Acme Custom Corp" in md


def test_render_report_handles_zero_jobs():
    md = render_report([], [], run_date=date(2026, 8, 5))
    assert "No matching roles found today." in md
