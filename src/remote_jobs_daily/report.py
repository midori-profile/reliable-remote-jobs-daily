import re
from datetime import date

from remote_jobs_daily.fetchers import JobPosting


def _escape_cell(value: str) -> str:
    """Collapse embedded whitespace/newlines and escape pipes for a Markdown table cell."""
    return re.sub(r"\s+", " ", value).strip().replace("|", "\\|")


def render_report(
    categorized: list[tuple[str, list[JobPosting]]],
    unparsed_companies: list[str],
    run_date: date,
) -> str:
    lines = [f"# Reliable Remote Jobs Daily — {run_date.isoformat()}", ""]

    total_jobs = sum(len(jobs) for _, jobs in categorized)
    all_companies = {job.company for _, jobs in categorized for job in jobs}

    if total_jobs == 0:
        lines.append("No matching roles found today.")
    else:
        category_word = "category" if len(categorized) == 1 else "categories"
        lines.append(
            f"Found **{total_jobs}** matching role(s) across {len(categorized)} "
            f"{category_word} and {len(all_companies)} companies."
        )

    for label, jobs in categorized:
        lines.append("")
        lines.append(f"## {label}")
        lines.append("")
        if not jobs:
            lines.append("No matching roles in this category today.")
            continue
        lines.append("| Company | Title | Location | Link |")
        lines.append("|---|---|---|---|")
        for job in jobs:
            company = _escape_cell(job.company)
            title = _escape_cell(job.title)
            location = _escape_cell(job.location)
            lines.append(f"| {company} | {title} | {location} | [Apply]({job.url}) |")

    lines.append("")
    lines.append("## Unparsed Companies")
    if unparsed_companies:
        lines.append("")
        for name in unparsed_companies:
            lines.append(f"- {name} — please check their careers page manually.")
    else:
        lines.append("")
        lines.append("(none)")

    return "\n".join(lines) + "\n"
