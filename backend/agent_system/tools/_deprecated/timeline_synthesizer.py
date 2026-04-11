"""
Timeline synthesizer — takes multi-year retrieved chunks and builds a coherent
chronological narrative.

KEY FIX: Now ACCEPTS year_chunks as input (output of year_range_retriever),
instead of doing its own retrieval. Tools compose: retriever → synthesizer.

Single responsibility: year_chunks dict → chronological narrative.
"""

from langchain.tools import tool

from llm.bedrock_client import llm_generate
from tools.call_limiter import max_calls


@tool
@max_calls(5)
def timeline_synthesizer(
    company: str,
    topic: str,
    year_chunks: dict,
) -> str:
    """Synthesize multi-year chunks into a single coherent timeline narrative.

    Prevents LLM from jumbling year ordering when generating final answers.
    Uses the RAMAS (2026) synthesis-after-retrieval pattern.

    IMPORTANT: This tool takes the output of year_range_retriever directly.
    Do NOT call this without first calling year_range_retriever.

    Args:
        company: company name (e.g., '3M').
        topic: the topic to trace (e.g., 'revenue growth', 'risk factors').
        year_chunks: dict from year_range_retriever — {year: [chunk_payloads]}.
                     Each chunk payload has 'text', 'section', etc.

    Returns:
        A chronological narrative string citing specific years.
    """
    if not year_chunks:
        return f"No data found for {company} on '{topic}'."

    # Build year-ordered context
    timeline_context = ""
    for year in sorted(year_chunks.keys()):
        chunks = year_chunks[year]
        # Take top 3 chunks per year to stay within context limits
        chunks_text = " ".join(
            c.get("text", "") for c in chunks[:3] if c.get("text")
        )
        timeline_context += f"\n\n=== {year} ===\n{chunks_text}"

    narrative = llm_generate(
        f"Create a chronological narrative for '{topic}' at {company}.\n"
        f"Use ONLY the provided yearly context. Cite the year for each claim.\n"
        f"Be concise but insightful (300-500 words).\n\n"
        f"Context:\n{timeline_context}",
        max_gen_len=2048,
    )

    return narrative
