"""System prompts and chart of accounts."""

from langchain_core.messages import SystemMessage

CHART_OF_ACCOUNTS = {
    "1000": "Cash and Cash Equivalents",
    "1100": "Accounts Receivable",
    "1200": "Inventory",
    "1300": "Prepaid Expenses",
    "1600": "Property, Plant & Equipment",
    "1700": "Accumulated Depreciation",
    "2000": "Accounts Payable",
    "2100": "Accrued Liabilities",
    "2200": "VAT/Tax Payable",
    "2300": "Deferred Revenue",
    "3000": "Retained Earnings",
    "4000": "Revenue",
    "4100": "Service Revenue",
    "5000": "Cost of Goods Sold",
    "6000": "Salaries & Wages",
    "6100": "Rent Expense",
    "6200": "Depreciation Expense",
    "6300": "Interest Expense",
    "6400": "G&A Expenses",
    "7000": "Marketing Expense",
}

POSTING_PROMPT = SystemMessage(
    "You are a senior GAAP accountant. Prepare the double-entry journal posting "
    "for the given business event.\n"
    "Rules:\n"
    "- Every posting MUST have at least one debit and one credit line\n"
    "- Total debits MUST equal total credits\n"
    "- Use the most specific account available\n"
    "- Include cost_centre on all P&L accounts (4xxx-8xxx) when provided\n"
    "Chart of accounts:\n"
    + "\n".join(f"  {k}: {v}" for k, v in CHART_OF_ACCOUNTS.items())
)
