from datetime import date

from ts_remote_jobs.fetchers import JobPosting


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
            lines.append(f"| {job.company} | {job.title} | {job.location} | [Apply]({job.url}) |")

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
