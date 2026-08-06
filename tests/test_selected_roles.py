import pytest

from remote_jobs_daily.roles import load_roles
from remote_jobs_daily.selected_roles import SelectedRolesError, load_selected_roles

ROLES = load_roles("tests/fixtures/roles_sample.yaml")  # has "frontend" and "backend"


def test_loads_valid_selection():
    selected = load_selected_roles("tests/fixtures/selected_roles_sample.yaml", ROLES)
    assert selected == ["frontend", "backend"]


def test_unknown_role_key_raises():
    with pytest.raises(SelectedRolesError, match="not_a_real_category"):
        load_selected_roles("tests/fixtures/selected_roles_unknown_key.yaml", ROLES)


def test_empty_selection_raises():
    with pytest.raises(SelectedRolesError, match="empty"):
        load_selected_roles("tests/fixtures/selected_roles_empty.yaml", ROLES)
