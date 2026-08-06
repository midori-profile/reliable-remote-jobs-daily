from datetime import date

from remote_jobs_daily.report import render_report
from remote_jobs_daily.fetchers import JobPosting


def test_render_report_groups_by_category_and_lists_unparsed():
    fe_job = JobPosting("GitLab", "Frontend Engineer", "Remote - APAC",
                         "https://x.example.com/1", "greenhouse", "")
    categorized = [("Frontend Engineer", [fe_job]), ("Backend Engineer", [])]
    unparsed = ["Acme Custom Corp"]

    md = render_report(categorized, unparsed, run_date=date(2026, 8, 6))

    assert "# Reliable Remote Jobs Daily — 2026-08-06" in md
    assert "## Frontend Engineer" in md
    assert "| GitLab | Frontend Engineer | Remote - APAC |" in md
    assert "[Apply](https://x.example.com/1)" in md
    assert "## Backend Engineer" in md
    assert "No matching roles in this category today." in md
    assert "## Unparsed Companies" in md
    assert "Acme Custom Corp" in md


def test_render_report_handles_zero_jobs_across_all_categories():
    categorized = [("Frontend Engineer", []), ("Backend Engineer", [])]
    md = render_report(categorized, [], run_date=date(2026, 8, 6))
    assert "No matching roles found today." in md


def test_render_report_escapes_pipe_and_newline_in_scraped_fields():
    job = JobPosting("Acme", "Senior Engineer | Remote", "Remote\n- APAC",
                      "https://x.example.com/1", "generic", "")
    categorized = [("Frontend Engineer", [job])]
    md = render_report(categorized, [], run_date=date(2026, 8, 6))
    assert "| Acme | Senior Engineer \\| Remote | Remote - APAC | [Apply](https://x.example.com/1) |" in md
