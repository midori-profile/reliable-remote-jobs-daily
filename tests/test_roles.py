import pytest

from remote_jobs_daily.roles import RoleCategory, RoleConfigError, load_roles

FIXTURE = "tests/fixtures/roles_sample.yaml"
INVALID_FIXTURE = "tests/fixtures/roles_missing_keywords.yaml"
KEYWORDS_NOT_LIST_FIXTURE = "tests/fixtures/roles_keywords_not_list.yaml"
BOUNDARY_KEYWORDS_NOT_LIST_FIXTURE = "tests/fixtures/roles_boundary_keywords_not_list.yaml"


def test_loads_valid_categories():
    roles = load_roles(FIXTURE)
    assert roles["frontend"] == RoleCategory(
        key="frontend",
        label="Frontend Engineer",
        keywords=("frontend", "front-end"),
        boundary_keywords=("react",),
    )


def test_category_missing_keywords_and_boundary_keywords_raises():
    with pytest.raises(RoleConfigError, match="no_keywords_at_all.*keywords"):
        load_roles(INVALID_FIXTURE)


def test_category_missing_label_raises(tmp_path):
    bad_file = tmp_path / "bad.yaml"
    bad_file.write_text('some_key:\n  keywords: ["x"]\n')
    with pytest.raises(RoleConfigError, match="some_key.*label"):
        load_roles(str(bad_file))


def test_category_keywords_not_a_list_raises():
    with pytest.raises(RoleConfigError, match="frontend.*keywords"):
        load_roles(KEYWORDS_NOT_LIST_FIXTURE)


def test_category_boundary_keywords_not_a_list_raises():
    with pytest.raises(RoleConfigError, match="frontend.*boundary_keywords"):
        load_roles(BOUNDARY_KEYWORDS_NOT_LIST_FIXTURE)
