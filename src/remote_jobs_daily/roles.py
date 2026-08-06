from dataclasses import dataclass

import yaml


class RoleConfigError(ValueError):
    pass


@dataclass
class RoleCategory:
    key: str
    label: str
    keywords: tuple[str, ...] = ()
    boundary_keywords: tuple[str, ...] = ()


def load_roles(path: str) -> dict[str, RoleCategory]:
    with open(path, encoding="utf-8") as f:
        raw = yaml.safe_load(f) or {}

    roles = {}
    for key, entry in raw.items():
        entry = entry or {}
        label = entry.get("label")
        if not label:
            raise RoleConfigError(f"{key}: missing required field: label")

        keywords = tuple(entry.get("keywords") or ())
        boundary_keywords = tuple(entry.get("boundary_keywords") or ())
        if not keywords and not boundary_keywords:
            raise RoleConfigError(
                f"{key}: must have at least one of keywords/boundary_keywords"
            )

        roles[key] = RoleCategory(
            key=key, label=label, keywords=keywords, boundary_keywords=boundary_keywords
        )
    return roles
