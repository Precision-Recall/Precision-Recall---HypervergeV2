---
name: promise-vs-reality
description: Use this skill when the user wants to check if a company kept a promise or commitment made in an earlier year's 10-K filing.
---

# Promise vs. Reality Detection

## When to use
- "Did TSLA deliver on their 2018 renewable energy promise by 2023?"
- "Check if 3M hit their cost reduction target from 2016"
- "Was the CEO's 2019 growth commitment met by 2022?"

## Approach
1. Use `search_promise_evidence` for the PROMISE YEAR to find the original commitment in Item 1 (Business), Item 7 (MD&A), or Item 1A (Risk Factors)
2. Use `search_promise_evidence` for the VERIFICATION YEAR to find acknowledgment/update
3. Compare evidence and determine: DELIVERED, PARTIALLY DELIVERED, NOT DELIVERED, or SILENTLY DROPPED
4. If no mention in verification year, that itself is a red flag (silent walkback)

## Key sections
- Item 7 (MD&A): Forward-looking statements — "we expect", "by 2025", "our target is"
- Item 1 (Business): Long-term strategic goals, product roadmap promises
- Item 1A (Risk Factors): Risks acknowledged as caveats to promises
