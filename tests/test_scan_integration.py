# tests/test_scan_integration.py
from datetime import date
from unittest.mock import Mock
from remote_jobs_daily.companies import load_companies
from remote_jobs_daily.roles import load_roles
from remote_jobs_daily.fetchers import fetch_for_company, FetchError
from remote_jobs_daily.filters import categorize_jobs
from remote_jobs_daily.report import render_report


def test_full_pipeline_with_categories_and_region_exclusion():
    companies = load_companies("tests/fixtures/companies_sample.yaml")
    roles = load_roles("tests/fixtures/roles_sample.yaml")  # frontend, backend
    selected = ["frontend", "backend"]

    mock_client = Mock()

    def fake_get(url, timeout=15):
        resp = Mock()
        if "boards-api.greenhouse.io" in url:
            resp.status_code = 200
            resp.json.return_value = {
                "jobs": [{
                    "id": 1, "title": "Frontend Engineer",
                    "absolute_url": "https://x.example.com/1",
                    "location": {"name": "Remote - APAC"}, "content": "",
                }]
            }
        else:
            resp.status_code = 500
        return resp

    mock_client.get.side_effect = fake_get

    all_jobs, unparsed = [], []
    for company in companies:
        if not company.accepts_region("APAC"):
            continue
        try:
            all_jobs.extend(fetch_for_company(company, client=mock_client))
        except FetchError:
            unparsed.append(company.name)

    grouped = categorize_jobs(all_jobs, roles, selected)
    categorized = [(roles[key].label, grouped[key]) for key in selected]
    report = render_report(categorized, unparsed, run_date=date(2026, 8, 6))

    assert "Frontend Engineer" in report
    assert "## Backend Engineer" in report
    # Acme is US-only, excluded by region before ever being fetched — not "未能解析"
    assert "Acme Custom Corp" not in report
