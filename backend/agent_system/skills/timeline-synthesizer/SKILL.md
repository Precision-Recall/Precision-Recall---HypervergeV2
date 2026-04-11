---
name: timeline-synthesizer
description: Use this tool to build a coherent chronological narrative from multi-year data about a specific topic for one company.
---

# timeline-synthesizer

## Overview
Synthesizes a chronological story from chunks spanning multiple years using LLM narrative generation.

## Parameters
- `company` (str): Company name
- `topic` (str): Topic to trace — e.g., `'revenue growth'`, `'risk factors'`, `'M&A strategy'`
- `start_year` (int): Beginning of range
- `end_year` (int): End of range

## Output
Dict with `narrative` (synthesized text), `years_covered`, `chunk_count`.
