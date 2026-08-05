from dataclasses import dataclass, field

import yaml

VALID_ATS = {"greenhouse", "lever", "ashby", "workable", "other"}


class CompanyConfigError(ValueError):
    pass


@dataclass
class Company:
    name: str
    ats: str
    token: str | None
    careers_url: str
    hires_from: list[str] = field(default_factory=lambda: ["Global"])

    def accepts_region(self, region: str) -> bool:
        return "Global" in self.hires_from or region in self.hires_from


def load_companies(path: str) -> list[Company]:
    with open(path, encoding="utf-8") as f:
        raw = yaml.safe_load(f) or []

    companies = []
    for entry in raw:
        name = entry.get("name")
        ats = entry.get("ats")
        careers_url = entry.get("careers_url")
        missing = [
            field_name
            for field_name, value in (
                ("name", name),
                ("ats", ats),
                ("careers_url", careers_url),
            )
            if not value
        ]
        if missing:
            raise CompanyConfigError(
                f"{name or '<unnamed>'}: missing required field(s): {', '.join(missing)}"
            )
        if ats not in VALID_ATS:
            raise CompanyConfigError(f"{name}: unknown ats '{ats}'")

        companies.append(
            Company(
                name=name,
                ats=ats,
                token=entry.get("token"),
                careers_url=careers_url,
                hires_from=entry.get("hires_from") or ["Global"],
            )
        )
    return companies
