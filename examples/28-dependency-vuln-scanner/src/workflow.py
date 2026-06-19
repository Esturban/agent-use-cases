"""
Dependency vulnerability scanner -- real CVE data, no API key required.

Step 1: Parse requirements.txt content into (package, version) pairs.
Step 2: Query OSV.dev (Google's open source vulnerability DB) for each package -- no auth.
Step 3: LLM synthesises raw CVE data into a typed VulnerabilityReport with severity ranking and risk summary.
"""
import json
import os
import urllib.request

from openai import OpenAI

from .schema import VulnerabilityReport

_OSV_URL = "https://api.osv.dev/v1/query"

_SEVERITY_RANK = {"CRITICAL": 4, "HIGH": 3, "MEDIUM": 2, "LOW": 1, "UNKNOWN": 0}

_SYNTHESIS_SYSTEM = (
    "You are a security analyst reviewing dependency vulnerabilities fetched from OSV.dev. "
    "Given raw CVE data for a set of Python packages:\n"
    "- For each package with findings, list all CVEs with their severity, a one-sentence summary, and fix versions\n"
    "- Assign the highest severity level across all its CVEs as highest_severity\n"
    "- Sort packages CRITICAL first, then HIGH, MEDIUM, LOW\n"
    "- Count packages_with_findings, critical_count, high_count accurately\n"
    "- Write a 2-3 sentence risk_summary naming the most urgent packages to upgrade and why\n"
    "Use only the CVE data provided. Do not invent vulnerabilities."
)


def _query_osv(package: str, version: str, ecosystem: str) -> list[dict]:
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


def _extract_severity(vuln: dict) -> str:
    """Best-effort severity extraction from an OSV vuln object."""
    # GitHub Advisory and PyPI advisories store severity in database_specific
    for affected in vuln.get("affected", []):
        sev = affected.get("database_specific", {}).get("severity", "").upper()
        if sev in _SEVERITY_RANK:
            return sev
    return "UNKNOWN"


def _extract_fixed(vuln: dict) -> list[str]:
    """Extract fixed version strings from affected ranges."""
    fixed = []
    for affected in vuln.get("affected", []):
        for r in affected.get("ranges", []):
            for event in r.get("events", []):
                if "fixed" in event:
                    fixed.append(event["fixed"])
    return list(set(fixed))


def parse_requirements(requirements_txt: str, ecosystem: str = "PyPI") -> list[tuple[str, str]]:
    """Parse requirements.txt text into [(package, version)] pairs. Skips unpinned packages."""
    packages = []
    for line in requirements_txt.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        for sep in ("==", ">=", "~="):
            if sep in line:
                name, rest = line.split(sep, 1)
                version = rest.strip().split(",")[0].strip()
                packages.append((name.strip(), version))
                break
    return packages


def scan(packages: list[tuple[str, str]], ecosystem: str = "PyPI") -> VulnerabilityReport:
    """
    Query OSV.dev for each (package, version) pair and return a VulnerabilityReport.

    Args:
        packages: List of (package_name, version) tuples.
        ecosystem: Package ecosystem for OSV lookup (default: PyPI).

    Returns:
        VulnerabilityReport with ranked findings and risk summary.
    """
    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

    # Fetch raw vulnerability data from OSV.dev
    raw_findings: list[dict] = []
    for name, version in packages:
        vulns = _query_osv(name, version, ecosystem)
        if vulns:
            raw_findings.append({
                "package": name,
                "version": version,
                "ecosystem": ecosystem,
                "vulns": [
                    {
                        "id": v.get("id", ""),
                        "summary": v.get("summary", "No summary available."),
                        "severity": _extract_severity(v),
                        "fixed_in": _extract_fixed(v),
                    }
                    for v in vulns
                ],
            })

    user_content = (
        f"Packages scanned: {len(packages)}\n\n"
        f"Raw vulnerability data from OSV.dev:\n{json.dumps(raw_findings, indent=2)}"
    )

    completion = client.beta.chat.completions.parse(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": _SYNTHESIS_SYSTEM},
            {"role": "user", "content": user_content},
        ],
        response_format=VulnerabilityReport,
    )
    report: VulnerabilityReport = completion.choices[0].message.parsed
    report.packages_scanned = len(packages)
    return report
