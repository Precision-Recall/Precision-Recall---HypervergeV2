---
name: terminology-normalizer
description: Use this tool to map synonymous financial terms across companies before comparing metrics. Critical for accurate cross-company comparisons.
---

# terminology-normalizer

## Overview
Maps equivalent financial terminology across companies using a static synonym table + LLM fallback.

## Parameters
- `terms` (list[str]): Financial terms to normalize — e.g., `['Operating income', 'Income from operations', 'Net Sales']`

## Output
Dict with `mappings` (canonical → [synonyms]) and `unmapped` terms.

## Example
Input: `['Operating income', 'Income from operations']`
Output: `{"mappings": {"Operating Income": ["Operating income", "Income from operations"]}, "unmapped": []}`
