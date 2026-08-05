import json
from unittest.mock import Mock

import requests

from ts_remote_jobs.fetchers import FetchError, JobPosting, fetch_greenhouse


def load_fixture(name):
    with open(f"tests/fixtures/{name}", encoding="utf-8") as f:
        return json.load(f)


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
