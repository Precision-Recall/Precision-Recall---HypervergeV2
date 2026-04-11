"""
Chunking logic: section detection + recursive text chunking + table/image as whole chunks.
"""

import re
import uuid
import tiktoken

from config import MAX_CHUNK_TOKENS, CHUNK_OVERLAP_TOKENS

enc = tiktoken.get_encoding("cl100k_base")

SECTION_PATTERN = re.compile(r"^(Item\s+(\d+[A-Za-z]?)\.\s+.+)", re.IGNORECASE)

SECTION_LABELS = {
    "1": "Business", "1a": "Risk Factors", "1b": "Unresolved Staff Comments",
    "2": "Properties", "3": "Legal Proceedings", "4": "Mine Safety",
    "5": "Market & Equity", "6": "Selected Financial Data",
    "7": "MD&A", "7a": "Market Risk",
    "8": "Financial Statements", "9": "Accounting Changes",
    "9a": "Controls & Procedures", "9b": "Other Information",
    "10": "Directors & Officers", "11": "Executive Compensation",
    "12": "Security Ownership", "13": "Related Transactions",
    "14": "Accounting Fees", "15": "Exhibits", "16": "Form 10-K Summary",
}

SKIP_TYPES = {"page_number", "footer", "page_footnote"}


def token_count(text: str) -> int:
    return len(enc.encode(text))


def split_text_recursive(text: str, max_tokens: int, overlap_tokens: int) -> list[str]:
    """Split text into chunks at paragraph boundaries with overlap."""
    if token_count(text) <= max_tokens:
        return [text]

    paragraphs = text.split("\n\n")
    chunks, current, current_tokens = [], "", 0

    for para in paragraphs:
        pt = token_count(para)
        if current_tokens + pt > max_tokens and current:
            chunks.append(current.strip())
            # Overlap: keep last portion
            overlap_text = enc.decode(enc.encode(current)[-overlap_tokens:]) if overlap_tokens else ""
            current, current_tokens = overlap_text + "\n\n" + para, token_count(overlap_text) + pt
        else:
            current += ("\n\n" if current else "") + para
            current_tokens += pt

    if current.strip():
        chunks.append(current.strip())

    return chunks


def chunk_content_list(content_list: list, file_meta: dict) -> list[dict]:
    """Process MinerU content_list into chunks with metadata."""
    current_section = "Preamble"
    current_section_item = None

    # Group consecutive text blocks by section
    groups = []  # list of (section, section_item, type, content, page, raw_content, img_path)
    text_buffer, text_pages = "", []

    def flush_text():
        nonlocal text_buffer, text_pages
        if text_buffer.strip():
            groups.append((current_section, current_section_item, "text",
                           text_buffer.strip(), text_pages[0] if text_pages else 0, None, None))
        text_buffer, text_pages = "", []

    for item in content_list:
        item_type = item.get("type", "")
        if item_type in SKIP_TYPES:
            continue

        text = (item.get("text", "") or "").strip()
        page = item.get("page_idx", 0)

        # Detect section changes
        if text:
            match = SECTION_PATTERN.match(text)
            if match:
                flush_text()
                sid = match.group(2).lower()
                current_section = SECTION_LABELS.get(sid, match.group(1)[:80])
                current_section_item = f"Item {match.group(2)}"

        if item_type == "table":
            flush_text()
            table_body = item.get("table_body", "") or ""
            img_path = item.get("img_path", "")
            narrative = table_to_narrative(table_body)
            groups.append((current_section, current_section_item, "table",
                           narrative, page, table_body, img_path))

        elif item_type == "image":
            flush_text()
            img_path = item.get("img_path", "")
            groups.append((current_section, current_section_item, "figure",
                           None, page, img_path, img_path))  # text filled later by captioning

        elif item_type in ("text", "header", "list"):
            if text:
                text_buffer += ("\n\n" if text_buffer else "") + text
                text_pages.append(page)

    flush_text()

    # Now split text groups into sized chunks
    chunks = []
    for section, section_item, ctype, content, page, raw_content, img_path in groups:
        if ctype == "text" and content:
            for part in split_text_recursive(content, MAX_CHUNK_TOKENS, CHUNK_OVERLAP_TOKENS):
                chunks.append(_make_chunk(part, section, section_item, ctype, page, None, None, file_meta))
        elif ctype == "table" and content:
            chunks.append(_make_chunk(content, section, section_item, ctype, page, raw_content, img_path, file_meta))
        elif ctype == "figure":
            chunks.append(_make_chunk("", section, section_item, ctype, page, raw_content, img_path, file_meta))

    return chunks


def table_to_narrative(html_table: str) -> str:
    """Convert HTML table to flat text for embedding."""
    text = re.sub(r"</?table>", "", html_table)
    text = re.sub(r"<tr>", "\n", text)
    text = re.sub(r"</?t[dh][^>]*>", " | ", text)
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"\|\s*\|", "|", text)
    text = re.sub(r"\n\s*\n", "\n", text)
    return text.strip()


def _make_chunk(text, section, section_item, ctype, page, raw_content, img_path, file_meta):
    renderable = ctype in ("table", "figure") and raw_content is not None
    return {
        "id": str(uuid.uuid5(uuid.NAMESPACE_URL,
                              f"{file_meta.get('company','')}-{file_meta.get('year','')}-{section_item}-{page}-{text[:100]}")),
        "text": text,
        "payload": {
            "text": text,
            "raw_content": raw_content,
            "img_path": img_path,
            "type": ctype,
            "renderable": renderable,
            "company": file_meta.get("company"),
            "year": file_meta.get("year"),
            "quarter": file_meta.get("quarter"),
            "form_type": file_meta.get("form_type"),
            "document_type": file_meta.get("document_type"),
            "section": section,
            "section_item": section_item,
            "page": page,
        },
    }
