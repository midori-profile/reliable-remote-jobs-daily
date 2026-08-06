import html as html_module
import re
from dataclasses import dataclass
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup


DEFAULT_TIMEOUT = 15

JOB_LINK_KEYWORDS = ("engineer", "developer", "typescript", "frontend", "software")

# Matches an HTML-entity-escaped opening/closing structural tag (e.g.
# "&lt;div&gt;", "&lt;/p&gt;"). Only unescape-before-strip when this is
# present, so we don't blindly unescape legitimate escaped text that merely
# *resembles* a tag — e.g. a job description mentioning TypeScript generics
# like "Array&lt;string&gt;" or "Promise&lt;T&gt;", which would otherwise be
# silently swallowed by BeautifulSoup as an unknown structural tag once
# unescaped.
_DOUBLE_ENCODED_TAG = re.compile(
    r"&lt;(?:/)?(?:div|p|span|br|ul|ol|li|strong|em|b|i|u|a|h[1-6]"
    r"|table|tr|td|th|blockquote|pre|code)\b",
    re.IGNORECASE,
)


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
    # Greenhouse (and possibly others) can return content that is itself
    # HTML-entity-escaped (e.g. "&lt;div&gt;...&lt;/div&gt;" instead of real
    # "<div>...</div>" tags). Only unescape first when we detect real
    # double-encoded structural markup — otherwise unescaping would also
    # turn legitimate escaped-but-not-HTML text (e.g. TypeScript generics
    # like "Array&lt;string&gt;") into what looks like a real tag, which
    # BeautifulSoup would then silently strip as unknown markup.
    html = html or ""
    if _DOUBLE_ENCODED_TAG.search(html):
        html = html_module.unescape(html)
    return BeautifulSoup(html, "html.parser").get_text(" ", strip=True)


def _get(client, url: str, source: str, company_name: str):
    try:
        resp = client.get(url, timeout=DEFAULT_TIMEOUT)
        if resp.status_code != 200:
            raise FetchError(f"{source} fetch failed for {company_name}: HTTP {resp.status_code}")
        return resp
    except FetchError:
        raise
    except requests.RequestException as e:
        raise FetchError(f"{source} fetch failed for {company_name}: {e}") from e


def _get_json(client, url: str, source: str, company_name: str):
    resp = _get(client, url, source, company_name)
    try:
        return resp.json()
    except ValueError as e:
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


def fetch_generic(careers_url: str, company_name: str, client=requests) -> list[JobPosting]:
    resp = _get(client, careers_url, "generic", company_name)
    try:
        soup = BeautifulSoup(resp.text, "html.parser")
        jobs = []
        for link in soup.find_all("a", href=True):
            text = link.get_text(strip=True)
            if not text:
                continue
            if any(keyword in text.lower() for keyword in JOB_LINK_KEYWORDS):
                jobs.append(
                    JobPosting(
                        company=company_name,
                        title=text,
                        location="Unknown",
                        url=urljoin(careers_url, link["href"]),
                        source="generic",
                        description_text="",
                    )
                )
        return jobs
    except (KeyError, TypeError, AttributeError) as e:
        raise FetchError(f"generic fetch failed for {company_name}: {e}") from e


def fetch_for_company(company, client=requests) -> list[JobPosting]:
    if company.ats == "greenhouse":
        return fetch_greenhouse(company.token, company.name, client=client)
    if company.ats == "lever":
        return fetch_lever(company.token, company.name, client=client)
    if company.ats == "ashby":
        return fetch_ashby(company.token, company.name, client=client)
    if company.ats == "workable":
        return fetch_workable(company.token, company.name, client=client)
    if company.ats == "other":
        return fetch_generic(company.careers_url, company.name, client=client)
    raise FetchError(f"unknown ats '{company.ats}' for {company.name}")
