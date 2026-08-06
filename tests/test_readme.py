from datetime import date

from remote_jobs_daily.readme import update_latest_scan_section

TEMPLATE = """# ts-remote-jobs

Some intro text.

<!-- LATEST-SCAN:START -->
(no scan yet)
<!-- LATEST-SCAN:END -->

## Contributing
"""


def test_replaces_content_between_markers():
    result = update_latest_scan_section(
        TEMPLATE, summary="Found 3 roles across 3 companies.",
        report_path="reports/2026-08-05.md", run_date=date(2026, 8, 5),
    )
    assert "(no scan yet)" not in result
    assert "Found 3 roles across 3 companies." in result
    assert "[reports/2026-08-05.md](reports/2026-08-05.md)" in result
    assert result.startswith("# ts-remote-jobs")
    assert result.strip().endswith("## Contributing")


def test_raises_if_markers_missing():
    from remote_jobs_daily.readme import MarkersNotFoundError
    try:
        update_latest_scan_section("no markers here", "x", "y", date(2026, 8, 5))
        assert False, "expected MarkersNotFoundError"
    except MarkersNotFoundError:
        pass


def test_raises_if_markers_reversed():
    from remote_jobs_daily.readme import MarkersNotFoundError

    reversed_template = """# ts-remote-jobs

<!-- LATEST-SCAN:END -->
(no scan yet)
<!-- LATEST-SCAN:START -->
"""
    try:
        update_latest_scan_section(reversed_template, "x", "y", date(2026, 8, 5))
        assert False, "expected MarkersNotFoundError"
    except MarkersNotFoundError:
        pass
