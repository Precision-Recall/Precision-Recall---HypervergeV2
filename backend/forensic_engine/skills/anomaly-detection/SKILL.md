---
name: anomaly-detection
description: Use this skill when the user wants to detect significant changes in risk factor language, internal controls, or related party disclosures between two years.
---

# Anomaly Detection (Risk Language Shift)

## When to use
- "Flag changes in risk factors between 2022 and 2023"
- "What new legal risks appeared in 3M's latest filing?"
- "Detect any silent additions to related party transactions"

## Approach
1. Use `compare_risk_factors` to get a structured diff of Item 1A (Risk Factors) between two years
2. The tool uses an inner LLM to identify new risks, dropped risks, and severity changes
3. It also checks Item 9A (Controls) and Item 13 (Related Party) for supplementary signals
4. Highlight NEW risks that silently appeared, DROPPED risks, and CHANGED severity

## Key sections
- Item 1A (Risk Factors): PRIMARY target — new legal/financial risks that silently appeared
- Item 9A (Controls & Procedures): Internal audit failures, control weaknesses added quietly
- Item 13 (Related Party Transactions): New conflict-of-interest disclosures
