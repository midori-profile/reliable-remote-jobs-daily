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


def _get_json(client, url: str, source: str, company_name: str):
    try:
        resp = client.get(url, timeout=DEFAULT_TIMEOUT)
        if resp.status_code != 200:
            raise FetchError(f"{source} fetch failed for {company_name}: HTTP {resp.status_code}")
        return resp.json()
    except FetchError:
        raise
    except (requests.RequestException, ValueError) as e:
        raise FetchError(f"{source} fetch failed for {company_name}: {e}") from e


def fetch_greenhouse(token: str, company_name: str, client=requests) -> list[JobPosting]:
    url = f"https://boards-api.greenhouse.io/v1/boards/{token}/jobs?content=true"
    data = _get_json(client, url, "greenhouse", company_name)
    try:
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
    except (KeyError, TypeError, AttributeError) as e:
        raise FetchError(f"greenhouse fetch failed for {company_name}: {e}") from e


def fetch_lever(token: str, company_name: str, client=requests) -> list[JobPosting]:
    url = f"https://api.lever.co/v0/postings/{token}?mode=json"
    data = _get_json(client, url, "lever", company_name)
    try:
        return [
            JobPosting(
                company=company_name,
                title=posting["text"],
                location=posting.get("categories", {}).get("location", "Unknown"),
                url=posting["hostedUrl"],
                source="lever",
                description_text=posting.get("descriptionPlain", ""),
            )
            for posting in data
        ]
    except (KeyError, TypeError, AttributeError) as e:
        raise FetchError(f"lever fetch failed for {company_name}: {e}") from e


def fetch_ashby(token: str, company_name: str, client=requests) -> list[JobPosting]:
    url = f"https://api.ashbyhq.com/posting-api/job-board/{token}"
    data = _get_json(client, url, "ashby", company_name)
    try:
        return [
            JobPosting(
                company=company_name,
                title=job["title"],
                location=job.get("location", "Unknown"),
                url=job["jobUrl"],
                source="ashby",
                description_text=job.get("descriptionPlain", ""),
            )
            for job in data.get("jobs", [])
        ]
    except (KeyError, TypeError, AttributeError) as e:
        raise FetchError(f"ashby fetch failed for {company_name}: {e}") from e


def fetch_workable(token: str, company_name: str, client=requests) -> list[JobPosting]:
    url = f"https://apply.workable.com/api/v1/widget/accounts/{token}?details=true"
    data = _get_json(client, url, "workable", company_name)
    try:
        return [
            JobPosting(
                company=company_name,
                title=job["title"],
                location=(job.get("location") or {}).get("location_str", "Unknown"),
                url=job["url"],
                source="workable",
                description_text="",
            )
            for job in data.get("jobs", [])
        ]
    except (KeyError, TypeError, AttributeError) as e:
        raise FetchError(f"workable fetch failed for {company_name}: {e}") from e
