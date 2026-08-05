from ts_remote_jobs.filters import is_typescript_relevant, filter_jobs
from ts_remote_jobs.fetchers import JobPosting


def make_job(title, description=""):
    return JobPosting(
        company="X", title=title, location="Remote - APAC",
        url="https://x.example.com/1", source="greenhouse", description_text=description,
    )


def test_matches_on_title_keyword():
    assert is_typescript_relevant(make_job("Senior TypeScript Engineer"))


def test_matches_on_description_keyword():
    assert is_typescript_relevant(make_job("Software Engineer", "We write TypeScript daily"))


def test_matches_frontend_without_explicit_typescript():
    assert is_typescript_relevant(make_job("Frontend Engineer"))


def test_rejects_unrelated_role():
    assert not is_typescript_relevant(make_job("Site Reliability Engineer", "Kubernetes and Go"))


def test_filter_jobs_combines_keyword_and_region():
    jobs = [
        make_job("TypeScript Engineer"),          # relevant, APAC location string but region comes from Company
        make_job("Site Reliability Engineer"),     # not relevant
    ]
    result = filter_jobs(jobs)
    assert [j.title for j in result] == ["TypeScript Engineer"]
