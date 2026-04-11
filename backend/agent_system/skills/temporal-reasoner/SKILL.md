---
name: temporal-reasoner
description: Use this skill when the user asks about how a SINGLE company changed over time. This agent analyzes temporal evolution of financials, strategy, risks, and narrative across multiple years for one company.
---

# Temporal Reasoner

## Overview
Specialized agent for single-company temporal analysis across annual (10-K) and quarterly (10-Q) filings.

## When to use
- "How did 3M's revenue change from 2015 to 2018?"
- "What new risk factors appeared in 3M's latest filing?"
- "Trace the strategic narrative for Activision over the last 3 years"
- "When did 3M pivot its business focus?"
- "Compare 3M's MD&A section between 2016 and 2017"

## Tool Selection Guide

### For retrieving raw data
- `year_range_retriever` — start here, retrieves chunks across a year span
- `quarter_drill_down` — for quarterly data specifically

### For quantitative analysis
- `metric_trend_extractor` — extracts exact numbers from financial tables

### For qualitative analysis
- `narrative_diff_tool` — compares language changes between two years
- `timeline_synthesizer` — builds chronological narrative from multi-year data

### For strategic analysis
- `pivot_detector` — detects business focus shifts (uses metric + narrative internally)

### For expanding context
- `chunk_bundler` — get neighboring chunks
- `section_full_fetcher` — get entire section content
- `list_available_data` — discover what companies/years exist
