import json
from unittest.mock import Mock

import requests

from ts_remote_jobs.companies import Company
from ts_remote_jobs.fetchers import (
    FetchError,
    JobPosting,
    _strip_html,
    fetch_ashby,
    fetch_for_company,
    fetch_generic,
    fetch_greenhouse,
    fetch_lever,
    fetch_workable,
)


def load_fixture(name):
    with open(f"tests/fixtures/{name}", encoding="utf-8") as f:
        return json.load(f)


def test_strip_html_handles_single_encoded_html():
    assert _strip_html("<p>We use TypeScript and React.</p>") == "We use TypeScript and React."


def test_strip_html_handles_double_encoded_html():
    double_encoded = (
        "&lt;div&gt;&lt;p&gt;Hello &lt;b&gt;World&lt;/b&gt;&lt;/p&gt;&lt;/div&gt;"
    )
    result = _strip_html(double_encoded)
    assert result == "Hello World"
    for tag_char in ("<div>", "<p>", "<b>", "</b>", "</p>", "</div>"):
        assert tag_char not in result


def test_strip_html_preserves_typescript_generics_syntax():
    # A description that legitimately mentions generics like Array<string> or
    # Promise<T> (itself escaped once, since it's inside HTML text content)
    # must not be mistaken for double-encoded structural markup and stripped
    # away — only real escaped tags (div/p/etc.) should trigger unescaping.
    content = (
        "&lt;p&gt;Experience with generics like Array&amp;lt;string&amp;gt; "
        "or Promise&amp;lt;T&amp;gt;.&lt;/p&gt;"
    )
    result = _strip_html(content)
    assert result == "Experience with generics like Array<string> or Promise<T>."


def test_fetch_greenhouse_parses_jobs():
    mock_client = Mock()
    mock_client.get.return_value.status_code = 200
    mock_client.get.return_value.json.return_value = load_fixture("greenhouse_response.json")

    jobs = fetch_greenhouse("gitlab", "GitLab", client=mock_client)

    mock_client.get.assert_called_once_with(
        "https://boards-api.greenhouse.io/v1/boards/gitlab/jobs?content=true",
        timeout=15,
    )
    assert jobs == [
        JobPosting(
            company="GitLab",
            title="Senior Frontend Engineer (TypeScript)",
            location="Remote - APAC",
            url="https://boards.greenhouse.io/gitlab/jobs/111",
            source="greenhouse",
            description_text="We use TypeScript and React.",
        ),
        JobPosting(
            company="GitLab",
            title="Site Reliability Engineer",
            location="Remote - US",
            url="https://boards.greenhouse.io/gitlab/jobs/222",
            source="greenhouse",
            description_text="Kubernetes, Go.",
        ),
    ]


def test_fetch_greenhouse_raises_on_non_200():
    mock_client = Mock()
    mock_client.get.return_value.status_code = 404
    try:
        fetch_greenhouse("nonexistent", "Nonexistent", client=mock_client)
        assert False, "expected FetchError"
    except FetchError as e:
        assert "404" in str(e)


def test_fetch_greenhouse_wraps_network_error():
    mock_client = Mock()
    mock_client.get.side_effect = requests.exceptions.ConnectionError("boom: no route to host")

    try:
        fetch_greenhouse("gitlab", "GitLab", client=mock_client)
        assert False, "expected FetchError"
    except FetchError as e:
        assert "GitLab" in str(e)
        assert "boom: no route to host" in str(e)
        assert isinstance(e.__cause__, requests.exceptions.ConnectionError)


def test_fetch_greenhouse_raises_fetch_error_on_malformed_shape():
    mock_client = Mock()
    mock_client.get.return_value.status_code = 200
    mock_client.get.return_value.json.return_value = ["unexpected", "list", "shape"]

    try:
        fetch_greenhouse("gitlab", "GitLab", client=mock_client)
        assert False, "expected FetchError"
    except FetchError as e:
        assert "GitLab" in str(e)


def test_fetch_lever_parses_jobs():
    mock_client = Mock()
    mock_client.get.return_value.status_code = 200
    mock_client.get.return_value.json.return_value = load_fixture("lever_response.json")

    jobs = fetch_lever("doist", "Doist", client=mock_client)

    mock_client.get.assert_called_once_with(
        "https://api.lever.co/v0/postings/doist?mode=json", timeout=15
    )
    assert jobs[0].title == "Frontend Engineer, TypeScript"
    assert jobs[0].location == "Remote - APAC"
    assert jobs[0].url == "https://jobs.lever.co/doist/abc-123"
    assert jobs[0].source == "lever"


def test_fetch_lever_raises_on_non_200():
    mock_client = Mock()
    mock_client.get.return_value.status_code = 500
    try:
        fetch_lever("doist", "Doist", client=mock_client)
        assert False, "expected FetchError"
    except FetchError as e:
        assert "500" in str(e)


def test_fetch_lever_wraps_network_error():
    mock_client = Mock()
    mock_client.get.side_effect = requests.exceptions.ConnectionError("boom: no route to host")

    try:
        fetch_lever("doist", "Doist", client=mock_client)
        assert False, "expected FetchError"
    except FetchError as e:
        assert "Doist" in str(e)
        assert "boom: no route to host" in str(e)
        assert isinstance(e.__cause__, requests.exceptions.ConnectionError)


def test_fetch_lever_raises_fetch_error_on_malformed_shape():
    mock_client = Mock()
    mock_client.get.return_value.status_code = 200
    mock_client.get.return_value.json.return_value = {"unexpected": "dict shape"}

    try:
        fetch_lever("doist", "Doist", client=mock_client)
        assert False, "expected FetchError"
    except FetchError as e:
        assert "Doist" in str(e)


def test_fetch_ashby_parses_jobs():
    mock_client = Mock()
    mock_client.get.return_value.status_code = 200
    mock_client.get.return_value.json.return_value = load_fixture("ashby_response.json")

    jobs = fetch_ashby("buffer", "Buffer", client=mock_client)

    mock_client.get.assert_called_once_with(
        "https://api.ashbyhq.com/posting-api/job-board/buffer", timeout=15
    )
    assert jobs[0].title == "Full Stack Engineer"
    assert jobs[0].source == "ashby"


def test_fetch_ashby_raises_on_non_200():
    mock_client = Mock()
    mock_client.get.return_value.status_code = 404
    try:
        fetch_ashby("buffer", "Buffer", client=mock_client)
        assert False, "expected FetchError"
    except FetchError as e:
        assert "404" in str(e)


def test_fetch_ashby_wraps_network_error():
    mock_client = Mock()
    mock_client.get.side_effect = requests.exceptions.ConnectionError("boom: no route to host")

    try:
        fetch_ashby("buffer", "Buffer", client=mock_client)
        assert False, "expected FetchError"
    except FetchError as e:
        assert "Buffer" in str(e)
        assert "boom: no route to host" in str(e)
        assert isinstance(e.__cause__, requests.exceptions.ConnectionError)


def test_fetch_ashby_raises_fetch_error_on_malformed_shape():
    mock_client = Mock()
    mock_client.get.return_value.status_code = 200
    mock_client.get.return_value.json.return_value = {"jobs": ["not-a-dict"]}

    try:
        fetch_ashby("buffer", "Buffer", client=mock_client)
        assert False, "expected FetchError"
    except FetchError as e:
        assert "Buffer" in str(e)


def test_fetch_workable_parses_jobs():
    mock_client = Mock()
    mock_client.get.return_value.status_code = 200
    mock_client.get.return_value.json.return_value = load_fixture("workable_response.json")

    jobs = fetch_workable("zapier", "Zapier", client=mock_client)

    mock_client.get.assert_called_once_with(
        "https://apply.workable.com/api/v1/widget/accounts/zapier?details=true", timeout=15
    )
    assert jobs[0].title == "Backend Engineer"
    assert jobs[0].url == "https://apply.workable.com/zapier/j/ABCDEF/"
    assert jobs[0].source == "workable"


def test_fetch_workable_raises_on_non_200():
    mock_client = Mock()
    mock_client.get.return_value.status_code = 503
    try:
        fetch_workable("zapier", "Zapier", client=mock_client)
        assert False, "expected FetchError"
    except FetchError as e:
        assert "503" in str(e)


def test_fetch_workable_wraps_network_error():
    mock_client = Mock()
    mock_client.get.side_effect = requests.exceptions.ConnectionError("boom: no route to host")

    try:
        fetch_workable("zapier", "Zapier", client=mock_client)
        assert False, "expected FetchError"
    except FetchError as e:
        assert "Zapier" in str(e)
        assert "boom: no route to host" in str(e)
        assert isinstance(e.__cause__, requests.exceptions.ConnectionError)


def test_fetch_workable_raises_fetch_error_on_malformed_shape():
    mock_client = Mock()
    mock_client.get.return_value.status_code = 200
    mock_client.get.return_value.json.return_value = ["unexpected", "list", "shape"]

    try:
        fetch_workable("zapier", "Zapier", client=mock_client)
        assert False, "expected FetchError"
    except FetchError as e:
        assert "Zapier" in str(e)


def test_fetch_generic_parses_job_links_and_ignores_others():
    html = """
    <html>
      <body>
        <a href="/about">About us</a>
        <a href="/jobs/1">Senior TypeScript Engineer</a>
        <a href="https://example.com/jobs/2">Frontend Developer</a>
        <a href="/jobs/3">Office Manager</a>
        <a href="/jobs/4">Software Engineer, Backend</a>
      </body>
    </html>
    """
    mock_client = Mock()
    mock_client.get.return_value.status_code = 200
    mock_client.get.return_value.text = html

    jobs = fetch_generic("https://example.com/careers", "Example Co", client=mock_client)

    mock_client.get.assert_called_once_with("https://example.com/careers", timeout=15)
    titles = [job.title for job in jobs]
    assert "Senior TypeScript Engineer" in titles
    assert "Frontend Developer" in titles
    assert "Software Engineer, Backend" in titles
    assert "About us" not in titles
    assert "Office Manager" not in titles

    ts_job = next(job for job in jobs if job.title == "Senior TypeScript Engineer")
    assert ts_job.company == "Example Co"
    assert ts_job.location == "Unknown"
    assert ts_job.url == "https://example.com/jobs/1"
    assert ts_job.source == "generic"
    assert ts_job.description_text == ""

    external_job = next(job for job in jobs if job.title == "Frontend Developer")
    assert external_job.url == "https://example.com/jobs/2"


def test_fetch_generic_raises_on_non_200():
    mock_client = Mock()
    mock_client.get.return_value.status_code = 404
    try:
        fetch_generic("https://example.com/careers", "Example Co", client=mock_client)
        assert False, "expected FetchError"
    except FetchError as e:
        assert "404" in str(e)


def test_fetch_generic_wraps_network_error():
    mock_client = Mock()
    mock_client.get.side_effect = requests.exceptions.ConnectionError("boom: no route to host")

    try:
        fetch_generic("https://example.com/careers", "Example Co", client=mock_client)
        assert False, "expected FetchError"
    except FetchError as e:
        assert "Example Co" in str(e)
        assert "boom: no route to host" in str(e)
        assert isinstance(e.__cause__, requests.exceptions.ConnectionError)


def test_fetch_for_company_dispatches_to_greenhouse():
    mock_client = Mock()
    mock_client.get.return_value.status_code = 200
    mock_client.get.return_value.json.return_value = load_fixture("greenhouse_response.json")

    company = Company(
        name="GitLab",
        ats="greenhouse",
        token="gitlab",
        careers_url="https://gitlab.com/careers",
    )

    jobs = fetch_for_company(company, client=mock_client)

    mock_client.get.assert_called_once_with(
        "https://boards-api.greenhouse.io/v1/boards/gitlab/jobs?content=true",
        timeout=15,
    )
    assert jobs[0].source == "greenhouse"


def test_fetch_for_company_dispatches_to_generic():
    mock_client = Mock()
    mock_client.get.return_value.status_code = 200
    mock_client.get.return_value.text = '<a href="/jobs/1">Software Engineer</a>'

    company = Company(
        name="Example Co",
        ats="other",
        token=None,
        careers_url="https://example.com/careers",
    )

    jobs = fetch_for_company(company, client=mock_client)

    mock_client.get.assert_called_once_with("https://example.com/careers", timeout=15)
    assert jobs[0].source == "generic"


def test_fetch_for_company_raises_fetch_error_for_unknown_ats():
    company = Company(
        name="Mystery Co",
        ats="bogus",
        token=None,
        careers_url="https://mystery.example.com/careers",
    )

    try:
        fetch_for_company(company, client=Mock())
        assert False, "expected FetchError"
    except FetchError as e:
        assert "Mystery Co" in str(e)
        assert "bogus" in str(e)
