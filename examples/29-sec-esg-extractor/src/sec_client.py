import json
import re
import urllib.request

_EDGAR_SUBMISSIONS = "https://data.sec.gov/submissions/CIK{cik}.json"
_HEADERS = {"User-Agent": "agent-use-cases research@example.com", "Accept-Encoding": "gzip, deflate"}


def get(url: str, headers: dict | None = None) -> bytes:
    req = urllib.request.Request(url, headers={**_HEADERS, **(headers or {})})
    with urllib.request.urlopen(req, timeout=20) as resp:
        return resp.read()


def search_cik(ticker: str) -> str:
    """Resolve a ticker to a CIK via SEC EDGAR company tickers JSON."""
    data = json.loads(get("https://www.sec.gov/files/company_tickers.json"))
    ticker_upper = ticker.upper()
    for entry in data.values():
        if entry.get("ticker", "").upper() == ticker_upper:
            return str(entry["cik_str"]).zfill(10)
    raise ValueError(f"Ticker not found in EDGAR: {ticker}")


def latest_10k(cik: str) -> tuple[str, int]:
    """Return (accession_number, filing_year) for the most recent 10-K."""
    data = json.loads(get(_EDGAR_SUBMISSIONS.format(cik=cik)))
    filings = data.get("filings", {}).get("recent", {})
    forms = filings.get("form", [])
    for i, form in enumerate(forms):
        if form in ("10-K", "10-K/A"):
            acc = filings["accessionNumber"][i].replace("-", "")
            date = filings["filingDate"][i]
            year = int(date[:4])
            return acc, year
    raise ValueError(f"No 10-K found for CIK {cik}")


def fetch_filing_text(cik: str, accession: str, max_chars: int = 40000) -> str:
    """Download the primary 10-K document and return up to max_chars of text."""
    acc_dir = accession
    acc_dashes = f"{accession[:10]}-{accession[10:12]}-{accession[12:]}"
    index_url = (
        f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{acc_dir}/{acc_dashes}-index.json"
    )
    try:
        index_data = json.loads(get(index_url))
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
            doc_url = (
                f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{acc_dir}/{primary['name']}"
            )
            raw = get(doc_url).decode("utf-8", errors="ignore")
            text = re.sub(r"<[^>]+>", " ", raw)
            text = re.sub(r"\s+", " ", text)
            return text[:max_chars]
    except Exception:
        pass
    return ""


def extract_esg_sections(text: str, max_chars: int = 30000) -> str:
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


def get_company_name(cik: str, fallback: str) -> str:
    """Fetch company name from EDGAR submissions metadata."""
    try:
        sub_data = json.loads(get(_EDGAR_SUBMISSIONS.format(cik=cik)))
        return sub_data.get("name", fallback)
    except Exception:
        return fallback
