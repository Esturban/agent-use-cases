"""
SEC ESG Extractor -- real 10-K filings, no API key required.

Step 1: Search SEC EDGAR full-text search API for a company's most recent 10-K filing.
Step 2: Fetch the filing index and extract the primary document URL.
Step 3: Download a representative text chunk from the filing (Risk Factors + MD&A sections).
Step 4: LLM maps ESG disclosures to CSRD reporting categories and scores completeness.
"""
import os

from openai import OpenAI

from .schema import ESGReport
from .sec_client import (
    extract_esg_sections,
    fetch_filing_text,
    get_company_name,
    latest_10k,
    search_cik,
)

_ANALYSIS_SYSTEM = (
    "You are an ESG analyst specialising in CSRD (Corporate Sustainability Reporting Directive) compliance. "
    "Given text extracted from a company's 10-K filing:\n"
    "1. Identify all ESG-related disclosures and map each to a CSRD reporting category\n"
    "2. Quote or closely paraphrase the relevant text and note which section it came from\n"
    "3. Assess completeness (FULL / PARTIAL / MINIMAL) and list specific CSRD gaps\n"
    "4. Score overall CSRD coverage (0-100), name strongest areas, and identify critical gaps\n"
    "5. Write a 2-3 sentence analyst note on ESG disclosure maturity\n"
    "Be specific. Cite section names. Do not invent disclosures not present in the text."
)

_CSRD_PROMPT = (
    "Analyse the following 10-K excerpts for ESG disclosures. "
    "Map each finding to a CSRD reporting category and assess completeness.\n\n"
    "Company: {company} ({ticker})\n"
    "Filing year: {year}\n\n"
    "--- FILING EXCERPTS ---\n{text}"
)


def analyse(ticker: str, company_name: str | None = None) -> ESGReport:
    """
    Fetch a company's latest 10-K from SEC EDGAR and extract ESG disclosures.

    Args:
        ticker: Stock ticker, e.g. 'MSFT'.
        company_name: Override display name. If None, fetched from EDGAR metadata.

    Returns:
        ESGReport with CSRD-mapped disclosures and coverage scoring.
    """
    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

    cik = search_cik(ticker)
    accession, filing_year = latest_10k(cik)

    raw_text = fetch_filing_text(cik, accession)
    esg_text = (
        extract_esg_sections(raw_text)
        if raw_text
        else "(Filing text unavailable -- using ticker metadata only)"
    )

    if company_name is None:
        company_name = get_company_name(cik, fallback=ticker)

    prompt = _CSRD_PROMPT.format(
        company=company_name,
        ticker=ticker.upper(),
        year=filing_year,
        text=esg_text,
    )

    completion = client.beta.chat.completions.parse(
        model="gpt-4.1-nano",
        messages=[
            {"role": "system", "content": _ANALYSIS_SYSTEM},
            {"role": "user", "content": prompt},
        ],
        response_format=ESGReport,
    )
    report: ESGReport = completion.choices[0].message.parsed
    report.company = company_name
    report.ticker = ticker.upper()
    report.filing_year = filing_year
    return report
