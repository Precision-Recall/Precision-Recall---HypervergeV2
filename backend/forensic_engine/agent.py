"""
Forensic ReAct agent — uses LangGraph create_react_agent.

Skills are loaded into the system prompt at startup (same pattern as agent_system).
The LLM has all forensic instructions upfront and autonomously decides which tools to call.
"""

from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver

from config import OPENAI_API_KEY, OPENAI_MODEL
from tools import ALL_FORENSIC_TOOLS
from skill_loader import load_all_skills, skills_to_prompt

# Load all skills into the system prompt at startup
_all_skills = load_all_skills()
_skills_prompt = skills_to_prompt(list(_all_skills.values()))

FORENSIC_SYSTEM_PROMPT = f"""You are a Forensic Accountability Agent — an expert at auditing company integrity through SEC 10-K filings.

You have tools to search specific sections of 10-K filings stored in a vector database, filtered by company, year, and section.

## Autonomous Execution
- You have a ReAct loop. Chain multiple tools until you have enough evidence to answer.
- Do NOT stop after one tool call if you need more data.
- If a tool returns NO_DATA, try different parameters ONCE (e.g., different company name). If still empty, report the gap.
- Do NOT retry the same tool with the same parameters.

## Response Rules
- Answer ONLY from retrieved evidence. Never fabricate financial data.
- Quote specific text from the evidence to support your findings.
- Assign a risk level: LOW, MEDIUM, HIGH, or CRITICAL.
- State your confidence level and what would increase it.
- If data is missing, say so. Use list_companies if unsure about available data.
- Keep responses focused and under 400 words.
- Structure your response with: Findings → Evidence → Risk Assessment.

## Available Skills & Tools
{_skills_prompt}
"""


def create_forensic_agent():
    """Create the forensic ReAct agent."""
    llm = ChatOpenAI(
        model=OPENAI_MODEL,
        api_key=OPENAI_API_KEY,
        temperature=0.0,
    )
    memory = MemorySaver()

    return create_react_agent(
        model=llm,
        tools=ALL_FORENSIC_TOOLS,
        prompt=FORENSIC_SYSTEM_PROMPT,
        checkpointer=memory,
    )
