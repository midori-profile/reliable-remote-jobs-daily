import re

from remote_jobs_daily.fetchers import JobPosting

# "react" is handled separately as a word-boundary regex (see _REACT_PATTERN)
# below, since a plain substring match on "react" false-positives on words
# like "reactive"/"reaction" that have nothing to do with the React
# framework. The other keywords are long/specific enough not to have this
# problem, so they stay as plain substring checks.
TS_KEYWORDS = (
    "typescript",
    "frontend",
    "front-end",
    "front end",
    "node.js",
    "nodejs",
    "javascript",
    "full stack",
    "fullstack",
    "full-stack",
)

_REACT_PATTERN = re.compile(r"\breact\b", re.IGNORECASE)


def is_typescript_relevant(job: JobPosting) -> bool:
    haystack = f"{job.title} {job.description_text}".lower()
    if any(keyword in haystack for keyword in TS_KEYWORDS):
        return True
    return bool(_REACT_PATTERN.search(haystack))


def filter_jobs(jobs: list[JobPosting]) -> list[JobPosting]:
    return [job for job in jobs if is_typescript_relevant(job)]
