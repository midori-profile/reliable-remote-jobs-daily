from datetime import date

from remote_jobs_daily.report import render_report
from remote_jobs_daily.fetchers import JobPosting


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


def test_render_report_escapes_pipe_and_newline_in_scraped_fields():
    jobs = [
        JobPosting("Acme", "Senior Engineer | Remote", "Remote\n- APAC",
                   "https://x.example.com/1", "generic", ""),
    ]
    md = render_report(jobs, [], run_date=date(2026, 8, 5))
    assert "| Acme | Senior Engineer \\| Remote | Remote - APAC | [Apply](https://x.example.com/1) |" in md
