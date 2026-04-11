---
name: sector-peer-finder
description: Use this tool to automatically discover which companies in the dataset are sector peers based on business descriptions. No hardcoded peer lists.
---

# sector-peer-finder

## Overview
Dynamic peer discovery using business description analysis and LLM reasoning.

## Parameters
- `company` (str): Target company name

## Output
Dict with `peers` (scored + rationale), `sector`, and `non_peers`.
