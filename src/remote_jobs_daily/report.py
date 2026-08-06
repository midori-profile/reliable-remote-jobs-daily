import re
from datetime import date

from remote_jobs_daily.fetchers import JobPosting


def _escape_cell(value: str) -> str:
    """Collapse embedded whitespace/newlines and escape pipes for a Markdown table cell."""
    return re.sub(r"\s+", " ", value).strip().replace("|", "\\|")


def render_report(jobs: list[JobPosting], unparsed_companies: list[str], run_date: date) -> str:
    lines = [f"# TypeScript Remote Jobs — {run_date.isoformat()}", ""]

    if not jobs:
        lines.append("No matching roles found today.")
    else:
        lines.append(f"Found **{len(jobs)}** matching role(s) across {len({j.company for j in jobs})} companies.")
        lines.append("")
        lines.append("| Company | Title | Location | Link |")
        lines.append("|---|---|---|---|")
        for job in jobs:
            company = _escape_cell(job.company)
            title = _escape_cell(job.title)
            location = _escape_cell(job.location)
            lines.append(f"| {company} | {title} | {location} | [Apply]({job.url}) |")

    lines.append("")
    lines.append("## 未能解析")
    if unparsed_companies:
        lines.append("")
        for name in unparsed_companies:
            lines.append(f"- {name} — please check their careers page manually.")
    else:
        lines.append("")
        lines.append("(none)")

    return "\n".join(lines) + "\n"
