from ts_remote_jobs.fetchers import JobPosting

TS_KEYWORDS = (
    "typescript",
    "ts ",
    "frontend",
    "front-end",
    "front end",
    "react",
    "node.js",
    "nodejs",
    "javascript",
    "full stack",
    "fullstack",
    "full-stack",
)


def is_typescript_relevant(job: JobPosting) -> bool:
    haystack = f"{job.title} {job.description_text}".lower()
    return any(keyword in haystack for keyword in TS_KEYWORDS)


def filter_jobs(jobs: list[JobPosting]) -> list[JobPosting]:
    return [job for job in jobs if is_typescript_relevant(job)]
