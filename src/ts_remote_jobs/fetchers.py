from dataclasses import dataclass

import requests
from bs4 import BeautifulSoup


DEFAULT_TIMEOUT = 15


class FetchError(Exception):
    pass


@dataclass
class JobPosting:
    company: str
    title: str
    location: str
    url: str
    source: str
    description_text: str


def _strip_html(html: str) -> str:
    return BeautifulSoup(html or "", "html.parser").get_text(" ", strip=True)


def fetch_greenhouse(token: str, company_name: str, client=requests) -> list[JobPosting]:
    url = f"https://boards-api.greenhouse.io/v1/boards/{token}/jobs?content=true"
    try:
        resp = client.get(url, timeout=DEFAULT_TIMEOUT)
        if resp.status_code != 200:
            raise FetchError(
                f"greenhouse fetch failed for {company_name}: HTTP {resp.status_code}"
            )

        data = resp.json()
        return [
            JobPosting(
                company=company_name,
                title=job["title"],
                location=(job.get("location") or {}).get("name", "Unknown"),
                url=job["absolute_url"],
                source="greenhouse",
                description_text=_strip_html(job.get("content", "")),
            )
            for job in data.get("jobs", [])
        ]
    except FetchError:
        raise
    except (requests.RequestException, ValueError, KeyError) as e:
        raise FetchError(f"greenhouse fetch failed for {company_name}: {e}") from e
