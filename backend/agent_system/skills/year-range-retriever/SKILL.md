---
name: year-range-retriever
description: Use this tool to search for document chunks related to a query for a single company across a range of years. This is the workhorse tool for temporal retrieval.
---

# year-range-retriever

## Overview
Retrieves and reranks document chunks for a specific company across a year range.

## Parameters
- `company` (str): Exact company name — e.g., `'3M'`, `'ACTIVISIONBLIZZARD'`
- `query` (str): The metric, topic, or question
- `start_year` (int): Beginning of year range (inclusive)
- `end_year` (int): End of year range (inclusive)
- `section` (str, optional): Section filter — e.g., `'MD&A'`, `'Risk Factors'`, `'Business'`

## Output
List of top-10 reranked chunks, each with: id, score, rerank_score, payload (text, company, year, section, type, etc.)

## Usage Examples
```
year_range_retriever(company="3M", query="revenue growth", start_year=2015, end_year=2018)
year_range_retriever(company="3M", query="litigation risk", start_year=2016, end_year=2017, section="Risk Factors")
```
