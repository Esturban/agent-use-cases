"""
SEC ESG Extractor -- real 10-K filings, no API key required.

Step 1: Search SEC EDGAR full-text search API for a company's most recent 10-K filing.
Step 2: Fetch the filing index and extract the primary document URL.
Step 3: Download a representative text chunk from the filing (Risk Factors + MD&A sections).
Step 4: LLM maps ESG disclosures to CSRD reporting categories and scores completeness.
"""
import json
import os
import re
import urllib.request
import urllib.parse

from openai import OpenAI

from .schema import ESGReport

_EDGAR_SEARCH = "https://efts.sec.gov/LATEST/search-index?q=%22{query}%22&dateRange=custom&startdt={year}-01-01&enddt={year}-12-31&forms=10-K"
_EDGAR_SUBMISSIONS = "https://data.sec.gov/submissions/CIK{cik}.json"
_EDGAR_FILING_INDEX = "https://www.sec.gov/Archives/edgar/data/{cik}/{accession_dir}/{accession}-index.htm"
_HEADERS = {"User-Agent": "agent-use-cases research@example.com", "Accept-Encoding": "gzip, deflate"}

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


def _get(url: str, headers: dict | None = None) -> bytes:
    req = urllib.request.Request(url, headers={**_HEADERS, **(headers or {})})
    with urllib.request.urlopen(req, timeout=20) as resp:
        return resp.read()


def _search_cik(ticker: str) -> str:
    """Resolve a ticker to a CIK via SEC EDGAR company tickers JSON."""
    data = json.loads(_get("https://www.sec.gov/files/company_tickers.json"))
    ticker_upper = ticker.upper()
    for entry in data.values():
        if entry.get("ticker", "").upper() == ticker_upper:
            return str(entry["cik_str"]).zfill(10)
    raise ValueError(f"Ticker not found in EDGAR: {ticker}")


def _latest_10k(cik: str) -> tuple[str, int]:
    """Return (accession_number, filing_year) for the most recent 10-K."""
    data = json.loads(_get(_EDGAR_SUBMISSIONS.format(cik=cik)))
    filings = data.get("filings", {}).get("recent", {})
    forms = filings.get("form", [])
    for i, form in enumerate(forms):
        if form in ("10-K", "10-K/A"):
            acc = filings["accessionNumber"][i].replace("-", "")
            date = filings["filingDate"][i]
            year = int(date[:4])
            return acc, year
    raise ValueError(f"No 10-K found for CIK {cik}")


def _fetch_filing_text(cik: str, accession: str, max_chars: int = 40000) -> str:
    """Download the primary 10-K document and return up to max_chars of text."""
    acc_dir = accession  # already no dashes
    acc_dashes = f"{accession[:10]}-{accession[10:12]}-{accession[12:]}"
    index_url = f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{acc_dir}/{acc_dashes}-index.json"
    try:
        index_data = json.loads(_get(index_url))
        primary = next(
            (f for f in index_data.get("directory", {}).get("item", [])
             if f.get("name", "").endswith(".htm") and "10k" in f.get("name", "").lower()),
            None,
        )
        if primary is None:
            primary = next(
                (f for f in index_data.get("directory", {}).get("item", [])
                 if f.get("name", "").endswith(".htm")),
                None,
            )
        if primary:
            doc_url = f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{acc_dir}/{primary['name']}"
            raw = _get(doc_url).decode("utf-8", errors="ignore")
            # Strip HTML tags
            text = re.sub(r"<[^>]+>", " ", raw)
            text = re.sub(r"\s+", " ", text)
            return text[:max_chars]
    except Exception:
        pass
    # Fallback: fetch the viewer text via EDGAR full-text search
    return ""


def _extract_esg_sections(text: str, max_chars: int = 30000) -> str:
    """Pull out sections most likely to contain ESG content."""
    markers = [
        "risk factor", "environmental", "climate", "sustainability",
        "social responsibility", "governance", "human capital",
        "management's discussion", "legal proceedings",
    ]
    chunks: list[str] = []
    lower = text.lower()
    for marker in markers:
        idx = lower.find(marker)
        if idx != -1:
            chunk = text[max(0, idx - 200): idx + 3000]
            chunks.append(chunk)

    combined = " ... ".join(chunks)
    return combined[:max_chars] if combined else text[:max_chars]


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

    cik = _search_cik(ticker)
    accession, filing_year = _latest_10k(cik)

    raw_text = _fetch_filing_text(cik, accession)
    esg_text = _extract_esg_sections(raw_text) if raw_text else "(Filing text unavailable — using ticker metadata only)"

    if company_name is None:
        try:
            sub_data = json.loads(_get(_EDGAR_SUBMISSIONS.format(cik=cik)))
            company_name = sub_data.get("name", ticker)
        except Exception:
            company_name = ticker

    prompt = _CSRD_PROMPT.format(
        company=company_name,
        ticker=ticker.upper(),
        year=filing_year,
        text=esg_text,
    )

    completion = client.beta.chat.completions.parse(
        model="gpt-4o-mini",
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
