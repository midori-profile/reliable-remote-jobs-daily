import pytest

from remote_jobs_daily.companies import Company, CompanyConfigError, load_companies

FIXTURE = "tests/fixtures/companies_sample.yaml"
INVALID_FIXTURE = "tests/fixtures/companies_invalid.yaml"
MISSING_TOKEN_FIXTURE = "tests/fixtures/companies_missing_token.yaml"
INVALID_REGION_FIXTURE = "tests/fixtures/companies_invalid_region.yaml"
APAC_LOWER_FIXTURE = "tests/fixtures/companies_apac_lower.yaml"


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


def test_missing_token_for_ats_requiring_token_raises():
    with pytest.raises(CompanyConfigError, match="No Token Co.*token"):
        load_companies(MISSING_TOKEN_FIXTURE)


def test_invalid_hires_from_region_raises():
    with pytest.raises(CompanyConfigError, match="Bad Region Co.*Mars"):
        load_companies(INVALID_REGION_FIXTURE)


def test_accepts_region_is_case_insensitive():
    companies = load_companies(APAC_LOWER_FIXTURE)
    apac_co = companies[0]
    assert apac_co.accepts_region("apac") is True
