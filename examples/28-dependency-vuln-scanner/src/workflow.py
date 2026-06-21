"""
Dependency vulnerability scanner -- real CVE data, no API key required.

Step 1: Parse requirements.txt content into (package, version) pairs.
Step 2: Query OSV.dev (Google's open source vulnerability DB) for each package -- no auth.
Step 3: LLM synthesises raw CVE data into a typed VulnerabilityReport with severity ranking and risk summary.
"""
import json
import os

from openai import OpenAI

from .osv_client import extract_fixed, extract_severity, query_osv
from .schema import VulnerabilityReport

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

    raw_findings: list[dict] = []
    for name, version in packages:
        vulns = query_osv(name, version, ecosystem)
        if vulns:
            raw_findings.append({
                "package": name,
                "version": version,
                "ecosystem": ecosystem,
                "vulns": [
                    {
                        "id": v.get("id", ""),
                        "summary": v.get("summary", "No summary available."),
                        "severity": extract_severity(v),
                        "fixed_in": extract_fixed(v),
                    }
                    for v in vulns
                ],
            })

    user_content = (
        f"Packages scanned: {len(packages)}\n\n"
        f"Raw vulnerability data from OSV.dev:\n{json.dumps(raw_findings, indent=2)}"
    )

    completion = client.beta.chat.completions.parse(
        model="gpt-4.1-nano",
        messages=[
            {"role": "system", "content": _SYNTHESIS_SYSTEM},
            {"role": "user", "content": user_content},
        ],
        response_format=VulnerabilityReport,
    )
    report: VulnerabilityReport = completion.choices[0].message.parsed
    report.packages_scanned = len(packages)
    return report
