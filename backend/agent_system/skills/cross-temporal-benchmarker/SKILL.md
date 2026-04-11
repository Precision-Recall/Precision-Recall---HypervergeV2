---
name: cross-temporal-benchmarker
description: Use this hybrid tool for questions that are BOTH cross-entity AND temporal. Benchmarks a metric across multiple companies over multiple years.
---

# cross-temporal-benchmarker

## Overview
Hybrid tool combining cross-company and temporal comparison into a benchmark matrix.

## Parameters
- `companies` (list[str]): Company names
- `metric` (str): Financial metric to benchmark
- `start_year` (int): Beginning of range
- `end_year` (int): End of range

## Output
Multi-dimensional comparison matrix with rankings (best/worst performer, highest growth) and analysis.
