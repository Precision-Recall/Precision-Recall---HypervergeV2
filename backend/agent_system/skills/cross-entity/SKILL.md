---
name: cross-entity
description: Use this skill when the user asks to COMPARE or BENCHMARK multiple companies. This agent analyzes cross-company metrics, discovers peers, normalizes terminology differences, and builds comparison tables.
---

# Cross-Entity Agent

## Overview
Specialized agent for multi-company comparison and benchmarking across financial filings.

## When to use
- "Compare 3M and Activision Blizzard revenue in 2017"
- "Which company had higher operating income in 2016?"
- "Find sector peers for 3M"
- "Benchmark revenue growth across all companies from 2015-2018"
- "How do these companies' risk profiles compare?"

## Tool Selection Guide

### For retrieving multi-company data
- `multi_company_retriever` — parallel retrieval across N companies

### For metric comparison
1. `terminology_normalizer` — recommended first to normalize term differences
2. `metric_comparator` — then extract and compare the normalized metric

### For peer analysis
- `sector_peer_finder` — discovers peer companies automatically from the dataset

### For hybrid temporal + cross-entity
- `cross_temporal_benchmarker` — compares metrics across companies AND years

### For expanding context
- `chunk_bundler` — get neighboring chunks
- `section_full_fetcher` — get entire section content
- `list_available_data` — discover what companies/years exist

## Critical Workflow
When comparing metrics across companies, normalize terminology first:
1. Call `terminology_normalizer` with the metric terms from each company
2. Use the canonical term in `metric_comparator`
3. Present results with notes on how terms were normalized
