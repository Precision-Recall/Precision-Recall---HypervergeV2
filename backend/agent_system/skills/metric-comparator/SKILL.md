---
name: metric-comparator
description: "Use this tool to compare a specific financial metric across multiple companies for the same year. Recommended - normalize terminology first."
---

# metric-comparator

## Overview
Cross-company metric extraction and comparison using LLM-powered normalization.

## Parameters
- `companies` (list[str]): Company names
- `metric` (str): Financial metric to compare
- `year` (int): Year to compare

## Output
Structured comparison dict with normalized values, units, and analysis.

## Critical
Recommended: call terminology_normalizer first for accurate cross-company comparison.
