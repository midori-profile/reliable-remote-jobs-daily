import re

from remote_jobs_daily.fetchers import JobPosting
from remote_jobs_daily.roles import RoleCategory


def _build_matcher(category: RoleCategory):
    plain_keywords = tuple(k.lower() for k in category.keywords)
    boundary_patterns = [
        re.compile(rf"\b{re.escape(k)}\b", re.IGNORECASE) for k in category.boundary_keywords
    ]

    def matches(haystack_lower: str) -> bool:
        if any(k in haystack_lower for k in plain_keywords):
            return True
        return any(p.search(haystack_lower) for p in boundary_patterns)

    return matches


def categorize_jobs(
    jobs: list[JobPosting], roles: dict[str, RoleCategory], selected_keys: list[str]
) -> dict[str, list[JobPosting]]:
    matchers = {key: _build_matcher(roles[key]) for key in selected_keys}
    result: dict[str, list[JobPosting]] = {key: [] for key in selected_keys}

    for job in jobs:
        haystack = f"{job.title} {job.description_text}".lower()
        for key, matcher in matchers.items():
            if matcher(haystack):
                result[key].append(job)

    return result
