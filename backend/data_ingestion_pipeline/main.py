"""
Data Ingestion Pipeline — Main entry point.

Usage:
    python main.py /path/to/pdf/folder [--output /path/to/extracted]
    python main.py /path/to/single.pdf
"""

import sys
import os
import argparse
import tempfile
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed

from config import MAX_PARALLEL_PDFS
from extractor import extract_pdf
from filename_parser import parse_filename
from chunker import chunk_content_list
from bedrock_client import get_embeddings_batch, caption_image
from vector_store import get_client, ensure_collection, upsert_chunks
from s3_storage import upload_image


def process_single_pdf(pdf_path: str, output_dir: str, max_pages: int = None) -> dict:
    """Process one PDF: extract → chunk → caption figures → embed → store."""
    pdf_path = Path(pdf_path)
    filename = pdf_path.name
    print(f"\n[START] {filename}")

    # 1. Parse filename metadata
    file_meta = parse_filename(filename)
    print(f"  Meta: {file_meta}")

    # 2. Extract with MinerU
    print(f"  Extracting with MinerU...")
    extracted = extract_pdf(str(pdf_path), output_dir)
    content_list = extracted["content_list"]
    images_dir = extracted["images_dir"]
    print(f"  Extracted: {len(content_list)} blocks")

    # Filter by max_pages if set
    if max_pages:
        content_list = [item for item in content_list if item.get("page_idx", 0) < max_pages]
        print(f"  Limited to first {max_pages} pages: {len(content_list)} blocks")

    # 3. Chunk
    chunks = chunk_content_list(content_list, file_meta)
    print(f"  Chunked: {len(chunks)} chunks")

    # 3b. Link chunks (prev/next)
    for i, c in enumerate(chunks):
        c["payload"]["prev_chunk_id"] = chunks[i - 1]["id"] if i > 0 else None
        c["payload"]["next_chunk_id"] = chunks[i + 1]["id"] if i < len(chunks) - 1 else None

    # 4. Caption real images, upload to S3 under pdf name folder
    figure_chunks = [c for c in chunks if c["payload"]["type"] == "figure"]
    if figure_chunks:
        print(f"  Captioning & uploading {len(figure_chunks)} figures...")
        pdf_stem = pdf_path.stem
        for c in figure_chunks:
            img_path = c["payload"].get("img_path", "")
            if img_path:
                full_path = os.path.join(images_dir, img_path) if not os.path.isabs(img_path) else img_path
                caption = caption_image(full_path)
                c["text"] = caption
                c["payload"]["text"] = caption
                s3_url = upload_image(full_path, pdf_stem)
                if s3_url:
                    c["payload"]["raw_content"] = s3_url

    # Filter out empty chunks and clean up internal fields
    chunks = [c for c in chunks if c["text"].strip()]
    for c in chunks:
        c["payload"].pop("img_path", None)
    print(f"  Valid chunks: {len(chunks)}")

    if not chunks:
        print(f"  [SKIP] No valid chunks for {filename}")
        return {"file": filename, "chunks": 0, "inserted": 0, "skipped": 0}

    # 5. Embed
    print(f"  Embedding {len(chunks)} chunks...")
    texts = [c["text"] for c in chunks]
    vectors = get_embeddings_batch(texts)

    # 6. Store in Qdrant
    print(f"  Storing in Qdrant...")
    client = get_client()
    ensure_collection(client)
    inserted, skipped = upsert_chunks(client, chunks, vectors)

    print(f"  [DONE] {filename}: {inserted} inserted, {skipped} duplicates skipped")
    return {"file": filename, "chunks": len(chunks), "inserted": inserted, "skipped": skipped}


def process_folder(folder_path: str, output_dir: str, max_pages: int = None):
    """Process all PDFs in a folder in parallel."""
    folder = Path(folder_path)
    pdfs = sorted(folder.glob("*.pdf"))

    if not pdfs:
        print(f"No PDFs found in {folder}")
        return

    print(f"Found {len(pdfs)} PDFs in {folder}")
    print(f"Output dir: {output_dir}")
    print(f"Parallel workers: {MAX_PARALLEL_PDFS}")
    print("=" * 60)

    # Ensure Qdrant collection exists
    client = get_client()
    ensure_collection(client)

    results = []
    with ProcessPoolExecutor(max_workers=MAX_PARALLEL_PDFS) as pool:
        futures = {pool.submit(process_single_pdf, str(p), output_dir, max_pages): p.name for p in pdfs}
        for future in as_completed(futures):
            name = futures[future]
            try:
                result = future.result()
                results.append(result)
            except Exception as e:
                print(f"\n  [ERROR] {name}: {e}")
                results.append({"file": name, "chunks": 0, "inserted": 0, "skipped": 0, "error": str(e)})

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    total_chunks = sum(r["chunks"] for r in results)
    total_inserted = sum(r["inserted"] for r in results)
    total_skipped = sum(r["skipped"] for r in results)
    errors = [r for r in results if "error" in r]
    print(f"  PDFs processed: {len(results)}")
    print(f"  Total chunks:   {total_chunks}")
    print(f"  Inserted:       {total_inserted}")
    print(f"  Duplicates:     {total_skipped}")
    print(f"  Errors:         {len(errors)}")
    if errors:
        for e in errors:
            print(f"    - {e['file']}: {e['error']}")


def main():
    parser = argparse.ArgumentParser(description="Ingest PDFs into vector store")
    parser.add_argument("path", help="PDF file or folder of PDFs")
    parser.add_argument("--output", "-o", default=None, help="Output dir for MinerU extraction")
    parser.add_argument("--max-pages", type=int, default=None, help="Limit pages for testing")
    args = parser.parse_args()

    path = Path(args.path)
    output_dir = args.output or os.path.join(tempfile.gettempdir(), "mineru_extracted")

    if path.is_file() and path.suffix == ".pdf":
        client = get_client()
        ensure_collection(client)
        process_single_pdf(str(path), output_dir, args.max_pages)
    elif path.is_dir():
        process_folder(str(path), output_dir, args.max_pages)
    else:
        print(f"Error: {path} is not a PDF file or directory")
        sys.exit(1)


if __name__ == "__main__":
    main()
