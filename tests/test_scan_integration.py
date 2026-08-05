import json
from datetime import date
from unittest.mock import Mock

from ts_remote_jobs.companies import load_companies
from ts_remote_jobs.fetchers import fetch_for_company, FetchError
from ts_remote_jobs.filters import filter_jobs
from ts_remote_jobs.report import render_report


def test_full_pipeline_with_mixed_success_and_failure():
    # Note: Task 1 split the original single fixture into companies_sample.yaml
    # (valid entries only: GitLab, Acme Custom Corp) and companies_invalid.yaml
    # (the entry missing careers_url), because load_companies() is fail-fast and
    # can't return a normal list AND raise from the same file/call. This test
    # only needs valid entries, so it uses companies_sample.yaml directly.
    companies = load_companies("tests/fixtures/companies_sample.yaml")

    mock_client = Mock()

    def fake_get(url, timeout=15):
        resp = Mock()
        if "boards-api.greenhouse.io" in url:
            resp.status_code = 200
            resp.json.return_value = {
                "jobs": [{
                    "id": 1, "title": "TypeScript Engineer",
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

    relevant = filter_jobs(all_jobs)
    report = render_report(relevant, unparsed, run_date=date(2026, 8, 5))

    assert "TypeScript Engineer" in report
    # Acme is US-only, so it's excluded by region before it ever gets fetched —
    # it must NOT show up in "未能解析" (that section is for fetch failures, not region exclusions)
    assert "Acme Custom Corp" not in report
