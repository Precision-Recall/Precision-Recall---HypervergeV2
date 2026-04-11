"""
PDF extraction using MinerU CLI.
"""

import subprocess
import json
import os
from pathlib import Path


def extract_pdf(pdf_path: str, output_dir: str) -> dict:
    """Run MinerU on a PDF and return parsed content_list + images dir."""
    pdf_path = Path(pdf_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    subprocess.run(
        ["mineru", "-p", str(pdf_path), "-o", str(output_dir), "-m", "auto", "-b", "pipeline", "-l", "en"],
        check=True
    )

    stem = pdf_path.stem
    base = output_dir / stem / "auto"
    content_list_path = base / f"{stem}_content_list.json"

    if not content_list_path.exists():
        raise FileNotFoundError(f"MinerU output not found: {content_list_path}")

    with open(content_list_path) as f:
        content_list = json.load(f)

    return {
        "content_list": content_list,
        "images_dir": str(base / "images"),
        "stem": stem,
    }
