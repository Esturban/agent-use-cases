"""AP invoice 3-way match workflow."""

import json
from typing import Any

from langchain_openai import ChatOpenAI

from .prompts import EXTRACTOR_PROMPT, MATCHER_PROMPT
from .schema import ExtractedInvoice, MatchResult
from .tools import lookup_gr, lookup_po


def create_extractor():
    """Return a chain that extracts structured invoice data from free text."""
    llm = ChatOpenAI(model="gpt-4.1-nano", temperature=0)
    return EXTRACTOR_PROMPT | llm.with_structured_output(ExtractedInvoice)


def create_matcher():
    """Return a chain that classifies discrepancies and determines approval tier."""
    llm = ChatOpenAI(model="gpt-4.1-nano", temperature=0)
    return MATCHER_PROMPT | llm.with_structured_output(MatchResult)


def run(invoice_text: str) -> dict[str, Any]:
    """Run the 3-way match pipeline on a plain-text vendor invoice.

    Stage 1 (LLM): Extract structured invoice data from free text.
    Stage 2 (deterministic): Look up PO and GR records from mock data.
    Stage 3 (LLM): Classify discrepancies and determine approval tier.

    Returns a dict with keys: invoice, po_data, gr_data, match_result.
    """
    # Stage 1 — LLM extraction
    extractor = create_extractor()
    invoice: ExtractedInvoice = extractor.invoke(invoice_text)

    # Stage 2 — deterministic PO and GR lookup
    po_data = lookup_po(invoice.po_reference)
    gr_data = lookup_gr(invoice.po_reference)

    # Stage 3 — LLM 3-way match classification
    matcher = create_matcher()
    context = (
        f"Invoice:\n{json.dumps(invoice.model_dump(), indent=2)}\n\n"
        f"Purchase Order:\n{json.dumps(po_data, indent=2) if po_data else 'NOT FOUND'}\n\n"
        f"Goods Receipt:\n{json.dumps(gr_data, indent=2) if gr_data else 'NOT FOUND'}"
    )
    match_result: MatchResult = matcher.invoke(context)

    return {
        "invoice": invoice,
        "po_data": po_data,
        "gr_data": gr_data,
        "match_result": match_result,
    }
