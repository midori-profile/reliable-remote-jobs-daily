from remote_jobs_daily.fetchers import JobPosting
from remote_jobs_daily.roles import RoleCategory
from remote_jobs_daily.filters import categorize_jobs


def make_job(title, description=""):
    return JobPosting(
        company="X", title=title, location="Remote", url="https://x.example.com/1",
        source="greenhouse", description_text=description,
    )


FRONTEND = RoleCategory(
    key="frontend", label="Frontend Engineer",
    keywords=("frontend", "typescript"), boundary_keywords=("react",),
)
BACKEND = RoleCategory(
    key="backend", label="Backend Engineer",
    keywords=("backend", "microservice"), boundary_keywords=("api",),
)
ROLES = {"frontend": FRONTEND, "backend": BACKEND}


def test_matches_on_plain_keyword():
    jobs = [make_job("Senior TypeScript Engineer")]
    result = categorize_jobs(jobs, ROLES, ["frontend"])
    assert result["frontend"] == jobs


def test_matches_on_boundary_keyword_but_not_substring_false_positive():
    reactive = make_job("Federal Sales Rep", "balance the reactive work of responding to users")
    real_react = make_job("Frontend Engineer", "we use React daily")
    result = categorize_jobs([reactive, real_react], ROLES, ["frontend"])
    assert result["frontend"] == [real_react]


def test_job_can_match_multiple_categories():
    job = make_job("Frontend + Backend Hybrid Role", "some frontend work and a backend microservice")
    result = categorize_jobs([job], ROLES, ["frontend", "backend"])
    assert result["frontend"] == [job]
    assert result["backend"] == [job]


def test_unmatched_categories_return_empty_list():
    job = make_job("Site Reliability Engineer", "Kubernetes and Go")
    result = categorize_jobs([job], ROLES, ["frontend", "backend"])
    assert result["frontend"] == []
    assert result["backend"] == []


def test_only_selected_categories_are_checked():
    job = make_job("Frontend Engineer")
    result = categorize_jobs([job], ROLES, ["backend"])
    assert "frontend" not in result
    assert result["backend"] == []


def test_single_incidental_keyword_hit_in_description_does_not_match():
    # Title doesn't match FRONTEND (keywords: frontend, typescript; boundary: react).
    # Description has exactly ONE keyword hit (typescript, mentioned once, incidentally).
    # A single incidental mention should not be enough to count as a match.
    job = make_job(
        "Manager, People Analytics",
        "Familiarity with scripting languages such as Python, R, or TypeScript is a plus.",
    )
    result = categorize_jobs([job], ROLES, ["frontend"])
    assert result["frontend"] == []


def test_two_or_more_distinct_keyword_hits_in_description_matches():
    # Title doesn't match; description is saturated with 2+ distinct keyword/boundary hits
    # (typescript + react) — a much stronger signal the posting is actually about the role.
    job = make_job(
        "Manager, People Analytics",
        "We build our tooling with TypeScript and React on a daily basis.",
    )
    result = categorize_jobs([job], ROLES, ["frontend"])
    assert result["frontend"] == [job]


def test_gitlab_lifecycle_marketing_manager_false_positive_regression():
    # Real discovered false positive: GitLab "Senior Lifecycle Marketing Manager" matched
    # frontend's css boundary_keyword via a single incidental mention of css in an
    # email-design context. This is a marketing role, not a frontend engineering job.
    marketing_frontend = RoleCategory(
        key="frontend", label="Frontend Engineer",
        keywords=("frontend", "front-end", "front end", "javascript", "typescript"),
        boundary_keywords=("react", "vue", "angular", "css"),
    )
    job = make_job(
        "Senior Lifecycle Marketing Manager",
        "You should have working knowledge of html and css for email design "
        "or troubleshooting, as well as experience with marketing automation tools.",
    )
    result = categorize_jobs([job], {"frontend": marketing_frontend}, ["frontend"])
    assert result["frontend"] == []
