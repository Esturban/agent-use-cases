from pydantic import BaseModel, Field


class Vulnerability(BaseModel):
    vuln_id: str = Field(description="Vulnerability identifier, e.g. CVE-2023-1234 or GHSA-xxxx-yyyy-zzzz.")
    severity: str = Field(description="Severity level: CRITICAL, HIGH, MEDIUM, LOW, or UNKNOWN.")
    summary: str = Field(description="One-sentence description of what the vulnerability allows.")
    fixed_in: list[str] = Field(description="Package versions where this vulnerability is fixed, if known.")


class PackageRisk(BaseModel):
    package: str = Field(description="Package name as it appears in requirements.txt.")
    version: str = Field(description="Version that was scanned.")
    ecosystem: str = Field(description="Package ecosystem, e.g. PyPI or npm.")
    vulnerabilities: list[Vulnerability] = Field(description="All CVEs found for this package at this version.")
    highest_severity: str = Field(
        description="Highest severity across all CVEs for this package: CRITICAL, HIGH, MEDIUM, LOW, or NONE."
    )


class VulnerabilityReport(BaseModel):
    packages_scanned: int = Field(description="Total number of packages checked against OSV.dev.")
    packages_with_findings: int = Field(description="Number of packages with at least one known CVE.")
    critical_count: int = Field(description="Total CRITICAL severity CVEs across all packages.")
    high_count: int = Field(description="Total HIGH severity CVEs across all packages.")
    findings: list[PackageRisk] = Field(
        description="Packages with vulnerabilities, sorted by severity (CRITICAL first, then HIGH, MEDIUM, LOW)."
    )
    risk_summary: str = Field(
        description=(
            "2-3 sentence plain-English summary of the most urgent risks and the immediate actions "
            "a developer should take — which packages to upgrade first and why."
        )
    )
