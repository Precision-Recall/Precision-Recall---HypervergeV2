"""
Temporal Reasoner — subagent definition.
Reasons across ONE company, MANY years. Every tool fixes company, varies year.
"""

from tools.temporal.year_range_retriever import year_range_retriever
from tools.temporal.metric_trend_extractor import metric_trend_extractor
from tools.temporal.narrative_diff_tool import narrative_diff_tool
from tools.temporal.timeline_synthesizer import timeline_synthesizer
from tools.temporal.quarter_drill_down import quarter_drill_down
from tools.temporal.pivot_detector import pivot_detector
from tools.shared.chunk_bundler import chunk_bundler
from tools.shared.section_full_fetcher import section_full_fetcher
from tools.shared.list_available_data import list_available_data
from skill_loader import load_skills_for_agent, skills_to_prompt


TEMPORAL_BASE_PROMPT = """You are the Temporal Reasoner — a specialized financial analyst 
that reasons across ONE company over MANY years.

Your job is to answer questions about how a single company's financials, strategy, 
risk factors, and narrative have evolved over time.

## Rules
1. Each tool can be called at most 5 times per request.
2. Choose the right tool for the query — don't follow a fixed sequence.
3. Use metric_trend_extractor for quantitative analysis, narrative_diff_tool for qualitative.
4. Provide specific years and data points in your responses, not vague summaries.
5. If data is missing for certain years, explicitly note the gaps.
6. CRITICAL: If a tool returns NO_DATA or 0 results, STOP. Do not retry with same params. Report what data is missing and suggest the user check company name/year.
7. NEVER generate answers from your own knowledge. Only use retrieved data.

## Skills & Tool Guide
{skills}
"""

# Load skills dynamically
_skills = load_skills_for_agent("temporal-reasoner")
TEMPORAL_SYSTEM_PROMPT = TEMPORAL_BASE_PROMPT.format(skills=skills_to_prompt(_skills))

temporal_reasoner_subagent = {
    "name": "temporal-reasoner",
    "description": (
        "Analyzes how a SINGLE company's financials, strategy, and narrative evolved "
        "over MULTIPLE years. Use for questions like: 'How did 3M's revenue change from "
        "2015 to 2018?', 'What risk factors appeared in 3M's 2017 filing that weren't "
        "in 2015?', 'Trace 3M's strategic narrative over the last 5 years.'  "
        "Fixes company, varies year."
    ),
    "system_prompt": TEMPORAL_SYSTEM_PROMPT,
    "tools": [
        year_range_retriever,
        metric_trend_extractor,
        narrative_diff_tool,
        timeline_synthesizer,
        quarter_drill_down,
        pivot_detector,
        chunk_bundler,
        list_available_data,
        section_full_fetcher,
    ],
}
