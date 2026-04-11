---
name: pivot-detector
description: Use this tool to identify when a company shifted its primary business focus by cross-correlating revenue mix changes with executive language shifts across years.
---

# pivot-detector

## Overview
Composite tool that uses metric_trend_extractor + narrative_diff_tool internally to detect strategic business pivots.

## Parameters
- `company` (str): Company name
- `start_year` (int): Beginning of analysis range
- `end_year` (int): End of analysis range

## Output
Dict with `pivot_detected`, `pivot_year`, `confidence`, `evidence`, `summary`.

## Important
- This tool makes internal calls to metric_trend_extractor and narrative_diff_tool
- The internal calls count toward the per-tool call limits
