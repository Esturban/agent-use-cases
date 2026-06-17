import os

from dotenv import load_dotenv

from src.workflow import run

load_dotenv()

if not os.getenv("OPENAI_API_KEY"):
    raise EnvironmentError("Set OPENAI_API_KEY in .env")

SAMPLE_RFP = """
REQUEST FOR PROPOSAL
Digital Transformation Office Maturity Assessment and Roadmap
Issued by: Meridian Financial Services Group
RFP Reference: MFSG-2025-DT-011
Submission Deadline: 30 March 2025

1. BACKGROUND
Meridian Financial Services Group (MFSG) is a mid-market financial services firm with
1,400 employees across retail banking, wealth management, and insurance divisions.
Our Digital Transformation Office (DTO) was established in 2022 but has struggled
to demonstrate measurable ROI. Executive leadership requires an independent assessment
of the DTO's current maturity, operating model, and a prioritised 18-month roadmap
before budget allocation for FY2026 is finalised.

2. SCOPE OF WORK
The selected firm must deliver:
a) Maturity Assessment: Benchmark the DTO against industry frameworks (e.g. CMMI,
   Gartner Digital Maturity Model) across five dimensions: strategy, governance,
   talent, technology, and delivery.
b) Stakeholder Interviews: Conduct structured interviews with a minimum of 20
   stakeholders including C-suite sponsors, DTO leadership, and business unit heads.
c) Root Cause Analysis: Identify the primary drivers of underperformance with
   supporting evidence from data, interviews, and benchmarks.
d) Prioritised Roadmap: Deliver an 18-month roadmap with initiatives ranked by
   effort vs. impact, quick wins (0-90 days) clearly identified.
e) Executive Presentation: Present findings and roadmap to the MFSG Executive
   Committee within 10 weeks of engagement commencement.

3. MANDATORY REQUIREMENTS (PASS/FAIL)
M1. Firm must have completed at least three digital maturity assessments for
    regulated financial services clients in the past five years.
M2. Lead partner must have a minimum of 15 years' experience in financial services
    transformation.
M3. All data handling must comply with UK GDPR and FCA data governance requirements.
M4. Proposal must include a fixed-fee commercial structure; time-and-materials bids
    will be disqualified.
M5. Draft deliverables must be provided within six weeks of contract signature.

4. EVALUATION CRITERIA (scored out of 100)
- Relevant sector experience and case studies: 35 points
- Quality and specificity of proposed methodology: 30 points
- Team credentials and named personnel: 20 points
- Commercial value and fixed-fee clarity: 15 points

5. COMMERCIAL
Proposals should be submitted as a single fixed fee. Budget envelope is GBP 180,000
exclusive of VAT. MFSG reserves the right to negotiate scope adjustments.

6. SUBMISSION REQUIREMENTS
- Maximum 20 pages excluding appendices
- Structured response following the sections in this RFP
- Submit electronically to procurement@mfsg.co.uk by 30 March 2025 17:00 GMT
"""

if __name__ == "__main__":
    result = run(SAMPLE_RFP)
    outline = result["outline"]
    proposal = result["proposal"]

    print("=" * 60)
    print("STAGE 1 — RFP OUTLINE (Supervisor)")
    print("=" * 60)
    print(f"Title:    {outline.rfp_title}")
    print(f"Client:   {outline.client_name or 'Unknown'}")
    print(f"Deadline: {outline.submission_deadline or 'Not specified'}")

    mandatory = [r for r in outline.requirements if r.mandatory]
    optional = [r for r in outline.requirements if not r.mandatory]
    print(f"\nRequirements: {len(mandatory)} mandatory, {len(optional)} optional")
    print("\nMandatory pass/fail:")
    for r in mandatory:
        print(f"  [{r.section}] {r.requirement}")

    print(f"\nWin themes ({len(outline.win_themes)}):")
    for t in outline.win_themes:
        print(f"  * {t}")

    print("\nEvaluation criteria (ranked):")
    for i, c in enumerate(outline.evaluation_criteria, 1):
        print(f"  {i}. {c}")

    print(f"\nSections to write: {', '.join(outline.sections_to_write)}")

    print()
    print("=" * 60)
    print("STAGE 2 — PROPOSAL DRAFT (Writer)")
    print("=" * 60)
    print("\n--- EXECUTIVE SUMMARY ---")
    print(proposal.executive_summary)

    print("\n--- OUR APPROACH ---")
    print(proposal.our_approach)

    print("\n--- TEAM & CREDENTIALS ---")
    print(proposal.team_and_credentials)

    print("\n--- TIMELINE ---")
    print(proposal.timeline)

    print("\n--- COMMERCIAL ---")
    print(proposal.commercial)

    print("\n--- WHY US ---")
    print(proposal.why_us)

    print("\n--- KEY DIFFERENTIATORS ---")
    for d in proposal.key_differentiators:
        print(f"  * {d}")

    print("\n--- COMPLIANCE STATEMENT ---")
    print(proposal.compliance_statement)
