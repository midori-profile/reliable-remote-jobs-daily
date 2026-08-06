"""Exercises scripts/scan.py's actual main() entrypoint (exit-code contract),
since scripts/scan.py is a standalone script (not part of the remote_jobs_daily
package) it is loaded here via importlib by file path.
"""
import importlib.util
from pathlib import Path
from unittest.mock import Mock

from remote_jobs_daily.fetchers import FetchError, JobPosting

SCAN_PATH = Path(__file__).resolve().parent.parent / "scripts" / "scan.py"
FIXTURES = Path(__file__).resolve().parent / "fixtures"


def _load_scan_module():
    spec = importlib.util.spec_from_file_location("scan_cli_under_test", SCAN_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_main_exits_0_on_normal_successful_run(tmp_path, monkeypatch):
    scan = _load_scan_module()

    def fake_fetch_for_company(company):
        if company.name == "GitLab":
            return [
                JobPosting(
                    company="GitLab",
                    title="Senior Frontend Developer",
                    location="Remote - APAC",
                    url="https://x.example.com/1",
                    source="greenhouse",
                    description_text="",
                )
            ]
        raise AssertionError(f"unexpected fetch attempt for {company.name}")

    monkeypatch.setattr(scan, "fetch_for_company", fake_fetch_for_company)

    output_dir = tmp_path / "reports"
    readme_path = tmp_path / "nonexistent-readme.md"

    exit_code = scan.main(
        [
            "--companies-file", str(FIXTURES / "companies_sample.yaml"),
            "--roles-file", str(FIXTURES / "roles_sample.yaml"),
            "--selected-roles-file", str(FIXTURES / "selected_roles_sample.yaml"),
            "--output-dir", str(output_dir),
            "--readme", str(readme_path),
            "--region", "APAC",
        ]
    )

    assert exit_code == 0
    report_files = list(output_dir.glob("*.md"))
    assert len(report_files) == 1
    assert "Senior Frontend Developer" in report_files[0].read_text(encoding="utf-8")


def test_main_exits_1_on_company_config_error(tmp_path):
    scan = _load_scan_module()

    output_dir = tmp_path / "reports"
    readme_path = tmp_path / "nonexistent-readme.md"

    exit_code = scan.main(
        [
            "--companies-file", str(FIXTURES / "companies_invalid.yaml"),
            "--roles-file", str(FIXTURES / "roles_sample.yaml"),
            "--selected-roles-file", str(FIXTURES / "selected_roles_sample.yaml"),
            "--output-dir", str(output_dir),
            "--readme", str(readme_path),
            "--region", "APAC",
        ]
    )

    assert exit_code == 1
    assert not output_dir.exists()


def test_main_exits_1_when_all_attempted_companies_fail(tmp_path, monkeypatch):
    scan = _load_scan_module()

    def fake_fetch_for_company(company):
        raise FetchError(f"simulated network failure for {company.name}")

    monkeypatch.setattr(scan, "fetch_for_company", fake_fetch_for_company)

    output_dir = tmp_path / "reports"
    readme_path = tmp_path / "nonexistent-readme.md"

    exit_code = scan.main(
        [
            "--companies-file", str(FIXTURES / "companies_sample.yaml"),
            "--roles-file", str(FIXTURES / "roles_sample.yaml"),
            "--selected-roles-file", str(FIXTURES / "selected_roles_sample.yaml"),
            "--output-dir", str(output_dir),
            "--readme", str(readme_path),
            "--region", "APAC",
        ]
    )

    assert exit_code == 1
    # No report should be written when every attempted company failed to fetch.
    assert not output_dir.exists()


def test_main_respects_roles_override_argument(tmp_path, monkeypatch):
    # Using --roles should work even without a selected-roles file existing at all —
    # --roles takes precedence and load_selected_roles is never called.
    scan = _load_scan_module()

    def fake_fetch_for_company(company):
        if company.name == "GitLab":
            return [
                JobPosting(
                    company="GitLab",
                    title="Senior Frontend Developer",
                    location="Remote - APAC",
                    url="https://x.example.com/1",
                    source="greenhouse",
                    description_text="",
                )
            ]
        raise AssertionError(f"unexpected fetch attempt for {company.name}")

    monkeypatch.setattr(scan, "fetch_for_company", fake_fetch_for_company)

    output_dir = tmp_path / "reports"
    readme_path = tmp_path / "nonexistent-readme.md"
    nonexistent_selected_roles = tmp_path / "nonexistent-selected-roles.yaml"

    exit_code = scan.main(
        [
            "--companies-file", str(FIXTURES / "companies_sample.yaml"),
            "--roles-file", str(FIXTURES / "roles_sample.yaml"),
            "--selected-roles-file", str(nonexistent_selected_roles),
            "--roles", "frontend",
            "--output-dir", str(output_dir),
            "--readme", str(readme_path),
            "--region", "APAC",
        ]
    )

    assert exit_code == 0
    report_files = list(output_dir.glob("*.md"))
    assert len(report_files) == 1
    report_text = report_files[0].read_text(encoding="utf-8")
    assert "## Frontend Engineer" in report_text
    assert "Senior Frontend Developer" in report_text
    # Only the frontend category was selected via --roles, backend should not appear.
    assert "## Backend Engineer" not in report_text


def test_main_dedupes_duplicate_roles_in_roles_argument(tmp_path, monkeypatch):
    # --roles frontend,frontend,backend should behave like --roles frontend,backend:
    # the frontend section must appear exactly once, not once per duplicate key.
    scan = _load_scan_module()

    def fake_fetch_for_company(company):
        if company.name == "GitLab":
            return [
                JobPosting(
                    company="GitLab",
                    title="Senior Frontend Developer",
                    location="Remote - APAC",
                    url="https://x.example.com/1",
                    source="greenhouse",
                    description_text="",
                )
            ]
        raise AssertionError(f"unexpected fetch attempt for {company.name}")

    monkeypatch.setattr(scan, "fetch_for_company", fake_fetch_for_company)

    output_dir = tmp_path / "reports"
    readme_path = tmp_path / "nonexistent-readme.md"
    nonexistent_selected_roles = tmp_path / "nonexistent-selected-roles.yaml"

    exit_code = scan.main(
        [
            "--companies-file", str(FIXTURES / "companies_sample.yaml"),
            "--roles-file", str(FIXTURES / "roles_sample.yaml"),
            "--selected-roles-file", str(nonexistent_selected_roles),
            "--roles", "frontend,frontend,backend",
            "--output-dir", str(output_dir),
            "--readme", str(readme_path),
            "--region", "APAC",
        ]
    )

    assert exit_code == 0
    report_files = list(output_dir.glob("*.md"))
    assert len(report_files) == 1
    report_text = report_files[0].read_text(encoding="utf-8")
    assert report_text.count("## Frontend Engineer") == 1


def test_main_exits_1_on_whitespace_comma_only_roles_argument(tmp_path, capsys):
    # --roles ",,," is truthy (skips the selected-roles-file path) but strips down
    # to an empty list of role keys, which must be a hard error, not a silent
    # "no matching roles" success.
    scan = _load_scan_module()

    output_dir = tmp_path / "reports"
    readme_path = tmp_path / "nonexistent-readme.md"
    nonexistent_selected_roles = tmp_path / "nonexistent-selected-roles.yaml"

    exit_code = scan.main(
        [
            "--companies-file", str(FIXTURES / "companies_sample.yaml"),
            "--roles-file", str(FIXTURES / "roles_sample.yaml"),
            "--selected-roles-file", str(nonexistent_selected_roles),
            "--roles", ",,,",
            "--output-dir", str(output_dir),
            "--readme", str(readme_path),
            "--region", "APAC",
        ]
    )

    assert exit_code == 1
    assert not output_dir.exists()
    captured = capsys.readouterr()
    assert "error" in captured.err.lower()
    assert "--roles" in captured.err
