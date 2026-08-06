import yaml


class SelectedRolesError(ValueError):
    pass


def load_selected_roles(path: str, roles: dict) -> list[str]:
    with open(path, encoding="utf-8") as f:
        raw = yaml.safe_load(f) or {}

    selected = raw.get("selected")
    if not selected:
        raise SelectedRolesError(f"{path}: 'selected' list is empty or missing")
    if not isinstance(selected, list):
        raise SelectedRolesError(f"{path}: 'selected' must be a list")

    unknown = [key for key in selected if not isinstance(key, str) or key not in roles]
    if unknown:
        raise SelectedRolesError(f"{path}: unknown role key(s): {', '.join(map(str, unknown))}")

    return list(dict.fromkeys(selected))  # dedupe, preserve order
