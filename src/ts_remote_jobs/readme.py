import re
from datetime import date

START = "<!-- LATEST-SCAN:START -->"
END = "<!-- LATEST-SCAN:END -->"


class MarkersNotFoundError(ValueError):
    pass


def update_latest_scan_section(readme_text: str, summary: str, report_path: str, run_date: date) -> str:
    start_idx = readme_text.find(START)
    end_idx = readme_text.find(END)
    if start_idx == -1 or end_idx == -1 or start_idx > end_idx:
        raise MarkersNotFoundError("README.md is missing LATEST-SCAN markers")

    block = (
        f"{START}\n"
        f"**{run_date.isoformat()}** — {summary}\n"
        f"Full report: [{report_path}]({report_path})\n"
        f"{END}"
    )

    pattern = re.compile(re.escape(START) + r".*?" + re.escape(END), re.DOTALL)
    # Use a lambda replacement so arbitrary characters in `block` (e.g. backslashes
    # from a summary/report_path) are never interpreted as regex backreferences.
    return pattern.sub(lambda _match: block, readme_text, count=1)
