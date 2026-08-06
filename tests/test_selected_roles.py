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


def test_non_list_selection_raises():
    with pytest.raises(SelectedRolesError, match="must be a list"):
        load_selected_roles("tests/fixtures/selected_roles_not_a_list.yaml", ROLES)


def test_non_string_entry_raises_selected_roles_error():
    with pytest.raises(SelectedRolesError):
        load_selected_roles("tests/fixtures/selected_roles_non_string_entry.yaml", ROLES)


def test_duplicate_key_is_deduped_preserving_order():
    selected = load_selected_roles("tests/fixtures/selected_roles_duplicate_key.yaml", ROLES)
    assert selected == ["frontend", "backend"]
