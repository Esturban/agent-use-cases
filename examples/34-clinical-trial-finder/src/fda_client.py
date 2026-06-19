import requests

_BASE = "https://clinicaltrials.gov/api/v2/studies"


def search_trials(condition: str, max_results: int = 10) -> list[dict]:
    resp = requests.get(
        _BASE,
        params={
            "query.cond": condition,
            "filter.overallStatus": "RECRUITING",
            "pageSize": max_results,
            "format": "json",
        },
        timeout=15,
    )
    resp.raise_for_status()
    studies = resp.json().get("studies", [])
    results = []
    for study in studies:
        proto = study.get("protocolSection", {})
        id_mod = proto.get("identificationModule", {})
        status_mod = proto.get("statusModule", {})
        design_mod = proto.get("designModule", {})
        elig_mod = proto.get("eligibilityModule", {})
        phases = design_mod.get("phases", [])
        results.append({
            "nct_id": id_mod.get("nctId", ""),
            "title": id_mod.get("briefTitle", ""),
            "status": status_mod.get("overallStatus", ""),
            "phase": ", ".join(phases) if phases else "N/A",
            "eligibility_criteria": elig_mod.get("eligibilityCriteria", "")[:2000],
        })
    return results
