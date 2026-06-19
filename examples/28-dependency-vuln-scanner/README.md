# 28 — Dependency Vulnerability Scanner

Paste in a requirements.txt and get back a ranked CVE report with immediate action items. No API key needed for the vulnerability data — it calls OSV.dev (Google's open source vulnerability database) directly.

---

## What it does

You pass in a list of Python packages with pinned versions and get back:

- Every known CVE per package, with severity and summary
- A ranked list of packages ordered CRITICAL → HIGH → MEDIUM → LOW
- Fix versions for each vulnerability (what to upgrade to)
- A plain-English risk summary: which packages to upgrade first and why

---

## How it works

`parse_requirements()` extracts package names and pinned versions from requirements.txt text. For each package, it calls the OSV.dev `/v1/query` endpoint over standard HTTP (no API key, no rate limits on typical usage). Raw CVE records are passed to `gpt-4o-mini` via structured output, which classifies severity, ranks findings, and writes the risk summary as a typed `VulnerabilityReport`.

The vulnerability data is live and real — OSV.dev is updated continuously from NVD, GitHub Advisory, and ecosystem-specific databases.

---

## What you'll see

```
============================================================
Scanning: Legacy data science stack
Packages: ['pillow==9.0.1', 'pyyaml==5.3.1', 'cryptography==36.0.0', ...]
============================================================

Packages scanned: 5
Packages with CVEs: 4
Critical: 2  |  High: 5

Findings (sorted by severity):
  [CRITICAL] pillow==9.0.1
    GHSA-4fx9-vc88-q2xc (CRITICAL): Heap buffer overflow in TIFF decoding -> fix: 9.3.0
    GHSA-j7hp-h8jx-5ppr (HIGH): Integer overflow in path handling -> fix: 9.1.0

  [HIGH] pyyaml==5.3.1
    CVE-2020-14343 (HIGH): Arbitrary code execution via unsafe YAML load -> fix: 5.4

  [HIGH] cryptography==36.0.0
    GHSA-x4qr-2fvf-3mr5 (HIGH): OpenSSL X.509 certificate verification bypass -> fix: 38.0.3

Risk summary:
  Upgrade pillow immediately — the CRITICAL heap overflow in 9.0.1 is remotely exploitable
  via crafted image uploads. PyYAML 5.3.1 allows arbitrary code execution through unsafe
  load(); pin to 5.4+ or use safe_load(). Address cryptography next as the OpenSSL
  verification bypass affects TLS certificate validation.
```

---

## How to run

```bash
# Only requires OPENAI_API_KEY in .env -- OSV.dev needs no key
python examples/28-dependency-vuln-scanner/main.py
```

---

## Files

```
28-dependency-vuln-scanner/
  src/schema.py      # Vulnerability, PackageRisk, VulnerabilityReport
  src/workflow.py    # OSV.dev HTTP calls + LLM synthesis pass
  main.py            # Legacy stack and mixed stack sample inputs
  README.md
```
