import yaml


class SelectedRolesError(ValueError):
    pass


def load_selected_roles(path: str, roles: dict) -> list[str]:
    with open(path, encoding="utf-8") as f:
        raw = yaml.safe_load(f) or {}

    selected = raw.get("selected")
    if not selected:
        raise SelectedRolesError(f"{path}: 'selected' list is empty or missing")

    unknown = [key for key in selected if key not in roles]
    if unknown:
        raise SelectedRolesError(f"{path}: unknown role key(s): {', '.join(unknown)}")

    return list(selected)
