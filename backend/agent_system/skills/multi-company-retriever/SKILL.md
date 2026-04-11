---
name: multi-company-retriever
description: Use this tool for parallel retrieval of document chunks across multiple companies simultaneously for the same query.
---

# multi-company-retriever

## Overview
Concurrent retrieval across N companies using ThreadPoolExecutor for parallel Qdrant queries.

## Parameters
- `companies` (list[str]): Company names — e.g., `['3M', 'ACTIVISIONBLIZZARD']`
- `query` (str): Topic to search
- `year` (int, optional): Exact year filter
- `start_year` (int, optional): Range start
- `end_year` (int, optional): Range end

## Output
Dict keyed by company name, each value is a list of top-10 reranked chunks.
