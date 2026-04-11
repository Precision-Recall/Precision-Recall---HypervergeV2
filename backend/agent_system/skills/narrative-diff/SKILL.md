---
name: narrative-diff
description: Use this tool to compare the language and narrative of a specific filing section between two years. Detects additions, removals, and tone shifts.
---

# narrative-diff

## Overview
Computes structured diffs between two years' filings for the same section using LLM analysis.

## Parameters
- `company` (str): Company name
- `section` (str): Section to compare — e.g., `'Risk Factors'`, `'MD&A'`, `'Business'`
- `year1` (int): Earlier year
- `year2` (int): Later year

## Output
Dict with `additions`, `removals`, `tone_shifts`, `key_changes_summary`, `risk_flag`.
