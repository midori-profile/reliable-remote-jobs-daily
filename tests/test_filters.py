from remote_jobs_daily.filters import is_typescript_relevant, filter_jobs
from remote_jobs_daily.fetchers import JobPosting


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


def test_rejects_sre_posting_with_ts_substring_false_positives():
    description = (
        "You will own our production infrastructure. Requirements: 5+ years "
        "experience with Kubernetes and Go. Benefits include equity grants, "
        "unlimited PTO, and a home office stipend. You'll work closely with "
        "clients and stakeholders across multiple projects and markets, "
        "manage cloud accounts, review contracts, and keep documents and "
        "assets organized. We host guests at quarterly summits and track "
        "costs across all posts."
    )
    assert not is_typescript_relevant(make_job("Site Reliability Engineer", description))


def test_rejects_reactive_as_false_positive_for_react_keyword():
    description = (
        "You will need to balance the reactive work of responding to interested "
        "users with proactive outreach and pipeline management."
    )
    assert not is_typescript_relevant(make_job("Federal Sales Development Representative", description))


def test_matches_react_framework_as_standalone_word():
    assert is_typescript_relevant(make_job("Software Engineer", "We build our UI in React."))


def test_filter_jobs_combines_keyword_and_region():
    jobs = [
        make_job("TypeScript Engineer"),          # relevant, APAC location string but region comes from Company
        make_job("Site Reliability Engineer"),     # not relevant
    ]
    result = filter_jobs(jobs)
    assert [j.title for j in result] == ["TypeScript Engineer"]
