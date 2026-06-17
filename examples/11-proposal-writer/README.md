# 11-proposal-writer

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Esturban/agent-use-cases/blob/main/examples/11-proposal-writer/proposal_writer_workbook.ipynb)

A two-agent pipeline that reads an RFP and returns a complete, structured proposal
response -- supervisor decomposes the brief, writer drafts every section using the
outline as a grounding contract.

## Harness focus

**Multi-agent document generation**

The supervisor agent reads the RFP once and produces a typed `ProposalOutline` --
win themes, mandatory requirements, evaluation criteria, and section order.
The writer agent receives both the raw RFP and the structured outline, then drafts
a full `Proposal` object with every section populated.

```
RFP text
   |
   v
[Supervisor] --> ProposalOutline
                  win_themes
                  requirements (mandatory flagged)
                  evaluation_criteria         --> [Writer] --> Proposal
                  sections_to_write                           executive_summary
                                                              our_approach
                                                              team_and_credentials
                                                              timeline
                                                              commercial
                                                              why_us
                                                              compliance_statement
```

The outline is the handoff contract. The writer cannot drift from requirements
it cannot see -- the supervisor has already extracted them.

**Keys:** `OPENAI_API_KEY`

```bash
python examples/11-proposal-writer/main.py
```

## Key concepts

| Concept | Where |
|---------|-------|
| Supervisor -> Writer handoff via typed schema | `src/workflow.py` -- `_outline()` + `_draft()` |
| Mandatory requirement flagging | `src/schema.py` -- `RFPRequirement.mandatory` |
| Win theme threading across sections | `WRITER_SYSTEM` prompt in `src/workflow.py` |
| Compliance gate in structured output | `src/schema.py` -- `Proposal.compliance_statement` |
| Sample financial services RFP | `main.py` -- MFSG Digital Transformation RFP |
