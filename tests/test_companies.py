import pytest

from ts_remote_jobs.companies import Company, CompanyConfigError, load_companies

FIXTURE = "tests/fixtures/companies_sample.yaml"
INVALID_FIXTURE = "tests/fixtures/companies_invalid.yaml"


def test_loads_valid_entries():
    companies = load_companies(FIXTURE)
    assert companies[0] == Company(
        name="GitLab",
        ats="greenhouse",
        token="gitlab",
        careers_url="https://about.gitlab.com/jobs/",
        hires_from=["Global"],
    )


def test_other_ats_allows_null_token():
    companies = load_companies(FIXTURE)
    acme = next(c for c in companies if c.name == "Acme Custom Corp")
    assert acme.ats == "other"
    assert acme.token is None
    assert acme.hires_from == ["US"]


def test_missing_required_field_raises():
    with pytest.raises(CompanyConfigError, match="Missing Fields Co.*careers_url"):
        load_companies(INVALID_FIXTURE)


def test_accepts_global_hires_from():
    companies = load_companies(FIXTURE)
    assert companies[0].accepts_region("APAC") is True


def test_rejects_region_not_listed():
    companies = load_companies(FIXTURE)
    acme = next(c for c in companies if c.name == "Acme Custom Corp")
    assert acme.accepts_region("APAC") is False
    assert acme.accepts_region("US") is True
