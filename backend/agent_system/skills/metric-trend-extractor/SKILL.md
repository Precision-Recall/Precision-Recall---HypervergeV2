---
name: metric-trend-extractor
description: Use this tool to extract specific numeric financial metrics from TABLE chunks across multiple years. Contains an inner LLM agent that parses HTML tables to find exact values.
---

# metric-trend-extractor

## Overview
Extracts specific financial metric values from table chunks across years using LLM-powered HTML parsing.

## Parameters
- `company` (str): Company name
- `metric` (str): Financial metric — e.g., `'Total Revenue'`, `'Net Income'`, `'Operating Income'`
- `years` (list[int]): Years to extract — e.g., `[2015, 2016, 2017, 2018]`

## Output
Dict with `trend` (year → {value, unit, context}) and `sources` (chunk IDs used).

## Important
- Only searches TABLE-type chunks (where raw_content contains HTML tables)
- Uses Llama 4 Scout as inner agent for extraction
- Returns "N/A" for years where the metric isn't found
