---
name: sentiment-divergence
description: Use this skill when the user wants to detect mismatch between CEO optimism in MD&A and actual financial risk signals in footnotes and market risk sections.
---

# Sentiment Divergence Detection

## When to use
- "Is the CEO optimistic while footnotes show liquidity risk?"
- "Detect tone mismatch in 3M's 2022 filing"
- "Compare management narrative vs actual financial risk signals"

## Approach
1. Use `search_sentiment_signals` with signal_type='optimism' to get MD&A tone from Item 7
2. Use `search_sentiment_signals` with signal_type='risk' to get counter-signals from Item 7A and Item 8
3. Analyze the DIVERGENCE: is the CEO painting a rosy picture while footnotes show trouble?
4. Flag CRITICAL divergence when both strong optimism and strong risk signals are present

## Key sections
- Item 7 (MD&A): CEO/management optimism tone — "strong growth", "record performance"
- Item 7A (Market Risk): Actual liquidity & debt exposure — the counter-signal to CEO tone
- Item 8 (Financial Statements & Notes): Going concern warnings, contingent liabilities hidden in footnotes
