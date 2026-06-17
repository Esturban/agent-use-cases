# 18-fundraising-agent

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Esturban/agent-use-cases/blob/main/examples/18-fundraising-agent/fundraising_agent_workbook.ipynb)

An agent that takes one company brief and produces three distinct sets of fundraising
materials -- one for VCs, one for PE firms, and one for family offices -- each
framed in the language and priorities that audience actually responds to.

## Harness focus

**Audience-targeted generation -- same data, different typed output per persona**

Three separate LLM calls run sequentially, each with a persona-specific system
prompt. The VC call gets a growth-and-TAM framing; the PE call gets an
EBITDA-and-exit framing; the family office call gets a capital-preservation framing.
Each returns the same `FundraisingMaterials` schema, but the content is shaped
entirely differently. The results are assembled into a single `FundraisingPackage`.

```
Company brief
      |
      +---> [VC drafter]           --> FundraisingMaterials (persona=vc)
      |
      +---> [PE drafter]           --> FundraisingMaterials (persona=pe)
      |
      +---> [Family Office drafter]--> FundraisingMaterials (persona=family_office)
      |
      v
FundraisingPackage
  |-- vc_materials
  |     |-- investor_thesis
  |     |-- headline_metrics   (ARR, NRR, burn multiple ...)
  |     |-- narrative_angle
  |     |-- key_asks
  |     |-- objection_responses
  |     |-- suggested_materials
  |-- pe_materials             (EBITDA framing)
  |-- family_office_materials  (preservation framing)
  |-- universal_value_props
```

**Keys:** `OPENAI_API_KEY`

```bash
python examples/18-fundraising-agent/main.py
```

## Key concepts

| Concept | Where |
|---------|-------|
| Three persona-specific system prompts | `src/workflow.py` -- `PERSONA_PROMPTS` dict |
| Same schema, different content per call | `src/schema.py` -- `FundraisingMaterials` |
| Fan-out assembly into FundraisingPackage | `src/workflow.py` -- `run()` |
| Volt Energy: Series B brief reused from example 17 | `main.py` -- same synthetic company |
| Persona comparison side by side | `fundraising_agent_workbook.ipynb` -- Part 5 |
