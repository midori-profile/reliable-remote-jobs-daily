import re

from remote_jobs_daily.fetchers import JobPosting
from remote_jobs_daily.roles import RoleCategory


def _build_matcher(category: RoleCategory):
    plain_keywords = tuple(k.lower() for k in category.keywords)
    boundary_patterns = [
        re.compile(rf"\b{re.escape(k)}\b", re.IGNORECASE) for k in category.boundary_keywords
    ]

    def _count_hits(text_lower: str) -> int:
        hits = sum(1 for k in plain_keywords if k in text_lower)
        hits += sum(1 for p in boundary_patterns if p.search(text_lower))
        return hits

    def matches(title: str, description: str) -> bool:
        # Title match is a strong signal: always counts, same as before.
        if _count_hits(title.lower()) > 0:
            return True
        # Description-only match is a weaker signal: a single incidental mention
        # (e.g. "css" in an email-design bullet, or "javascript" in a generic skills
        # list) isn't enough. Require at least 2 distinct keyword/boundary hits so a
        # description genuinely saturated with role-specific terms still counts.
        return _count_hits(description.lower()) >= 2

    return matches


def categorize_jobs(
    jobs: list[JobPosting], roles: dict[str, RoleCategory], selected_keys: list[str]
) -> dict[str, list[JobPosting]]:
    matchers = {key: _build_matcher(roles[key]) for key in selected_keys}
    result: dict[str, list[JobPosting]] = {key: [] for key in selected_keys}

    for job in jobs:
        for key, matcher in matchers.items():
            if matcher(job.title, job.description_text):
                result[key].append(job)

    return result
