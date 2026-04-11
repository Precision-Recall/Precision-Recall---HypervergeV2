"""
Cross-Entity Agent — subagent definition.
Reasons across MANY companies, fixed or varying years. Every tool varies company.
"""

from tools.cross_entity.multi_company_retriever import multi_company_retriever
from tools.cross_entity.metric_comparator import metric_comparator
from tools.cross_entity.terminology_normalizer import terminology_normalizer
from tools.cross_entity.sector_peer_finder import sector_peer_finder
from tools.cross_entity.cross_temporal_benchmarker import cross_temporal_benchmarker
from tools.shared.chunk_bundler import chunk_bundler
from tools.shared.section_full_fetcher import section_full_fetcher
from tools.shared.list_available_data import list_available_data
from skill_loader import load_skills_for_agent, skills_to_prompt


CROSS_ENTITY_BASE_PROMPT = """You are the Cross-Entity Agent — a specialized financial analyst 
that reasons across MANY companies, for a fixed year or across varying years.

Your job is to answer questions that compare, benchmark, or contrast multiple companies.

## Critical Workflow
When comparing metrics across companies, normalize terminology first:
1. Call terminology_normalizer with the metric + companies list
2. Use the exact aliases in metric_comparator
3. Present results with notes on how terms were normalized

## Rules
1. Each tool can be called at most 5 times per request.
2. For metric comparisons, call terminology_normalizer before metric_comparator to ensure accuracy.
3. Use sector_peer_finder if the user asks "compare with peers" without specifying companies.
4. For multi-year comparisons across companies, use cross_temporal_benchmarker.
5. Present comparisons in clear tabular format with normalized metrics.
6. Explicitly note when companies report differently and how you normalized.
7. CRITICAL: If a tool returns NO_DATA or 0 results, STOP. Do not retry with same params.
8. NEVER generate answers from your own knowledge. Only use retrieved data.

## Skills & Tool Guide
{skills}
"""

_skills = load_skills_for_agent("cross-entity")
CROSS_ENTITY_SYSTEM_PROMPT = CROSS_ENTITY_BASE_PROMPT.format(skills=skills_to_prompt(_skills))

cross_entity_subagent = {
    "name": "cross-entity-agent",
    "description": (
        "Compares and benchmarks MULTIPLE companies for a fixed year or across "
        "varying years. Use for questions like: 'Compare 3M and Activision revenue in "
        "2017', 'Which company had higher operating income?', 'Find peers for 3M', "
        "'Benchmark revenue growth across all companies from 2015-2018.'  "
        "Varies company, fixes or ranges year."
    ),
    "system_prompt": CROSS_ENTITY_SYSTEM_PROMPT,
    "tools": [
        multi_company_retriever,
        metric_comparator,
        terminology_normalizer,
        sector_peer_finder,
        cross_temporal_benchmarker,
        chunk_bundler,
        list_available_data,
        section_full_fetcher,
    ],
}
