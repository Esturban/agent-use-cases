from dotenv import load_dotenv

from src.workflow import parse_requirements, scan

load_dotenv()

# Legacy data science stack with known vulnerabilities
LEGACY_REQS = """
pillow==9.0.1
pyyaml==5.3.1
cryptography==36.0.0
urllib3==1.26.5
setuptools==65.5.0
"""

# Mostly current stack with one outdated package
MIXED_REQS = """
requests==2.31.0
pydantic==2.5.0
pillow==9.4.0
openai==1.12.0
"""


def main() -> None:
    for label, reqs in [("Legacy data science stack", LEGACY_REQS), ("Mixed stack", MIXED_REQS)]:
        packages = parse_requirements(reqs)
        print(f"\n{'=' * 60}")
        print(f"Scanning: {label}")
        print(f"Packages: {[f'{n}=={v}' for n, v in packages]}")
        print("=" * 60)

        report = scan(packages)

        print(f"\nPackages scanned: {report.packages_scanned}")
        print(f"Packages with CVEs: {report.packages_with_findings}")
        print(f"Critical: {report.critical_count}  |  High: {report.high_count}")

        if report.findings:
            print("\nFindings (sorted by severity):")
            for pkg in report.findings:
                print(f"\n  [{pkg.highest_severity}] {pkg.package}=={pkg.version}")
                for vuln in pkg.vulnerabilities:
                    fixed = f" -> fix: {', '.join(vuln.fixed_in)}" if vuln.fixed_in else ""
                    print(f"    {vuln.vuln_id} ({vuln.severity}): {vuln.summary}{fixed}")
        else:
            print("\nNo vulnerabilities found.")

        print(f"\nRisk summary:\n  {report.risk_summary}")


if __name__ == "__main__":
    main()
