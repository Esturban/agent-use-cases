import json
import urllib.request

_OSV_URL = "https://api.osv.dev/v1/query"

_SEVERITY_RANK = {"CRITICAL": 4, "HIGH": 3, "MEDIUM": 2, "LOW": 1, "UNKNOWN": 0}


def query_osv(package: str, version: str, ecosystem: str) -> list[dict]:
    """POST to OSV.dev and return raw vuln dicts. Returns [] on any error."""
    payload = json.dumps({
        "version": version,
        "package": {"name": package, "ecosystem": ecosystem},
    }).encode()
    req = urllib.request.Request(
        _OSV_URL,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
        return data.get("vulns", [])
    except Exception:
        return []


def extract_severity(vuln: dict) -> str:
    """Best-effort severity extraction from an OSV vuln object."""
    for affected in vuln.get("affected", []):
        sev = affected.get("database_specific", {}).get("severity", "").upper()
        if sev in _SEVERITY_RANK:
            return sev
    return "UNKNOWN"


def extract_fixed(vuln: dict) -> list[str]:
    """Extract fixed version strings from affected ranges."""
    fixed = []
    for affected in vuln.get("affected", []):
        for r in affected.get("ranges", []):
            for event in r.get("events", []):
                if "fixed" in event:
                    fixed.append(event["fixed"])
    return list(set(fixed))
