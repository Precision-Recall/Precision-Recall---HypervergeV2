"""
Parse PDF filename to extract company, year, quarter, form_type.
Expected format: COMPANY_YEAR_FORMTYPE.pdf or COMPANY_YEARQN_FORMTYPE.pdf
"""

import re


def parse_filename(filename: str) -> dict:
    """Extract metadata from filename like '3M_2018_10K.pdf'."""
    stem = filename.replace(".pdf", "")
    parts = stem.split("_")

    meta = {"company": None, "year": None, "quarter": None, "form_type": None, "document_type": None}

    # Find year (4-digit number between 2000-2099)
    year_idx = None
    for i, p in enumerate(parts):
        m = re.match(r"^(20\d{2})(Q(\d))?$", p)
        if m:
            meta["year"] = int(m.group(1))
            if m.group(3):
                meta["quarter"] = int(m.group(3))
            year_idx = i
            break

    if year_idx is not None:
        meta["company"] = "_".join(parts[:year_idx])
        remaining = "_".join(parts[year_idx + 1:])
        if remaining:
            meta["form_type"] = remaining.split("_")[0]  # e.g. 10K, 10Q, 8K

    # Derive document_type
    ft = (meta["form_type"] or "").upper()
    if "10K" in ft:
        meta["document_type"] = "annual_report"
    elif "10Q" in ft:
        meta["document_type"] = "quarterly_report"
    elif "8K" in ft:
        meta["document_type"] = "current_report"
    elif "EARNINGS" in ft:
        meta["document_type"] = "earnings"
    elif "ANNUAL" in ft.upper():
        meta["document_type"] = "annual_report"
    else:
        meta["document_type"] = "other"

    return meta
