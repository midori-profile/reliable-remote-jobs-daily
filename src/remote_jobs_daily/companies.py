from dataclasses import dataclass, field

import yaml

VALID_ATS = {"greenhouse", "lever", "ashby", "workable", "other"}
VALID_REGIONS = {"Global", "US", "EU", "APAC", "LATAM", "UK"}


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
        hires_from_folded = {r.casefold() for r in self.hires_from}
        return "global" in hires_from_folded or region.casefold() in hires_from_folded


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
        if ats != "other" and not entry.get("token"):
            raise CompanyConfigError(f"{name}: ats '{ats}' requires a token")

        hires_from = entry.get("hires_from") or ["Global"]
        for region in hires_from:
            if region not in VALID_REGIONS:
                raise CompanyConfigError(f"{name}: unknown region '{region}' in hires_from")

        companies.append(
            Company(
                name=name,
                ats=ats,
                token=entry.get("token"),
                careers_url=careers_url,
                hires_from=hires_from,
            )
        )
    return companies
