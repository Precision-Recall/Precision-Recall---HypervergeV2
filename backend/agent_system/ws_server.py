"""
WebSocket server — streams agent execution events in real-time.
Run: python ws_server.py
"""

import sys
import os
import json
import time
import asyncio
import queue
import threading

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from agents.orchestrator import create_agent, set_event_queue, _emit, _truncate, set_provider, get_current_provider
from tools.call_limiter import reset_call_counts
from skill_loader import load_skills_for_agent

agent = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global agent
    print("🚀 Initializing agent...")
    agent = create_agent()
    print("✅ Agent ready.")
    yield


app = FastAPI(lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


def _make_event(event_type, **kwargs):
    return {"type": event_type, "timestamp": time.time() * 1000, **kwargs}


def _collect_sources(output) -> list[dict]:
    """Extract source metadata from tool outputs."""
    sources = []
    if isinstance(output, dict):
        for key, val in output.items():
            if isinstance(val, list):
                for item in val:
                    if isinstance(item, dict) and "company" in item:
                        sources.append({
                            "company": item.get("company"),
                            "year": item.get("year"),
                            "section": item.get("section"),
                            "section_item": item.get("section_item"),
                            "page": item.get("page"),
                            "type": item.get("type"),
                            "text": str(item.get("text", ""))[:300],
                            "raw_content": item.get("raw_content") if item.get("type") == "table" else None,
                        })
        if "sources" in output and isinstance(output["sources"], list):
            for s in output["sources"]:
                if isinstance(s, dict):
                    sources.append({
                        **s,
                        "raw_content": s.get("raw_content"),
                        "type": "table" if s.get("raw_content") else "text",
                    })
    elif isinstance(output, list):
        for item in output:
            if isinstance(item, dict) and "company" in item:
                sources.append({
                    "company": item.get("company"),
                    "year": item.get("year"),
                    "section": item.get("section"),
                    "page": item.get("page"),
                    "type": item.get("type"),
                    "text": str(item.get("text", ""))[:300],
                    "raw_content": item.get("raw_content") if item.get("type") == "table" else None,
                })
    return sources


def run_agent_streaming(query: str, event_queue: queue.Queue, session_id: str = "default"):
    """Run agent, push events to queue as they happen."""
    all_sources = []
    try:
        reset_call_counts()
        set_event_queue(event_queue)

        event_queue.put(_make_event("agent_start", agent="Financial Intelligence Agent", data={"type": "orchestrator"}))
        event_queue.put(_make_event("reasoning", data={"type": "intent", "description": f"Analyzing: \"{query[:100]}\""}))

        # Emit skill loading events
        from skill_loader import load_all_skills
        skills = load_all_skills()
        for name in skills:
            event_queue.put(_make_event("reasoning", data={
                "type": "tool_call",
                "description": f"📖 Reading skill: {name}"
            }))
        event_queue.put(_make_event("reasoning", data={
            "type": "planning",
            "description": f"Loaded {len(skills)} skills → Ready to analyze"
        }))
        config = {"configurable": {"thread_id": session_id}}

        for event in agent.stream({"messages": [("user", query)]}, stream_mode="updates", config=config):
            for node_name, node_data in event.items():
                for msg in node_data.get("messages", []):
                    try:
                        msg_type = msg.type if hasattr(msg, "type") else type(msg).__name__

                        # Agent decides to call tool(s)
                        if msg_type == "ai" and hasattr(msg, "tool_calls") and msg.tool_calls:
                            for tc in msg.tool_calls:
                                tool_name = tc.get("name", "")
                                tool_args = tc.get("args", {})
                                event_queue.put(_make_event("reasoning", data={
                                    "type": "tool_call",
                                    "description": f"Calling {tool_name}"
                                }))
                                event_queue.put(_make_event("tool_call", tool=tool_name,
                                                            data={"input": tool_args}))

                        # Tool result
                        elif msg_type == "tool":
                            tool_name = msg.name if hasattr(msg, "name") else ""
                            content = msg.content if hasattr(msg, "content") else str(msg)
                            try:
                                output = json.loads(content) if isinstance(content, str) else content
                            except (json.JSONDecodeError, TypeError):
                                output = {"result": _truncate(content)}

                            all_sources.extend(_collect_sources(output))

                            tool_sources = []
                            if isinstance(output, dict) and "sources" in output:
                                tool_sources = output.get("sources", [])
                                clean_output = {**output}
                                if "sources" in clean_output:
                                    clean_output["sources"] = [
                                        {k: v for k, v in s.items() if k != "raw_content"}
                                        for s in clean_output["sources"]
                                    ]
                                output = clean_output

                            try:
                                if len(json.dumps(output, default=str)) > 3000:
                                    output = {"result": _truncate(json.dumps(output, default=str), 2500), "truncated": True}
                            except Exception:
                                output = {"result": _truncate(str(output), 2500)}

                            event_queue.put(_make_event("tool_complete", tool=tool_name,
                                                        data={"output": output}))

                        # Final answer
                        elif msg_type == "ai" and hasattr(msg, "content") and msg.content:
                            if not (hasattr(msg, "tool_calls") and msg.tool_calls):
                                content = msg.content
                                if isinstance(content, list):
                                    content = " ".join(
                                        item.get("text", "") if isinstance(item, dict) else str(item)
                                        for item in content
                                    ).strip()
                                if not isinstance(content, str):
                                    content = str(content)
                                if content:
                                    for word in content.split(" "):
                                        event_queue.put(_make_event("token_stream", token=word + " "))

                    except Exception as e:
                        event_queue.put(_make_event("reasoning", data={"type": "tool_call", "description": f"⚠️ {str(e)[:100]}"}))

        # Emit sources
        if all_sources:
            seen = set()
            unique = []
            for s in all_sources:
                key = f"{s.get('company')}-{s.get('year')}-{s.get('section')}-{s.get('page')}"
                if key not in seen:
                    seen.add(key)
                    unique.append(s)
            for i in range(0, len(unique), 5):
                batch = unique[i:i+5]
                event_queue.put(_make_event("sources", data={"sources": batch}))

            # Build citation graph
            graph_nodes = [{"id": "query", "type": "query", "label": query[:80]}]
            graph_edges = []
            tool_nodes_seen = set()

            for s in unique:
                # Tool node
                tool_id = f"tool-{s.get('section','unknown')}"
                if tool_id not in tool_nodes_seen:
                    tool_nodes_seen.add(tool_id)
                    graph_nodes.append({"id": tool_id, "type": "tool", "label": s.get("section", "Unknown")})
                    graph_edges.append({"source": "query", "target": tool_id})

                # Source node
                src_id = f"src-{s.get('company','')}-{s.get('year','')}-{s.get('section','')}-{s.get('page','')}"
                graph_nodes.append({
                    "id": src_id,
                    "type": "source",
                    "label": f"{s.get('company','')} {s.get('year','')}",
                    "section": s.get("section", ""),
                    "page": s.get("page"),
                    "text": str(s.get("text", ""))[:100],
                })
                graph_edges.append({"source": tool_id, "target": src_id})

            event_queue.put(_make_event("citation_graph", data={"nodes": graph_nodes, "edges": graph_edges}))

        event_queue.put(_make_event("agent_complete", agent="Financial Intelligence Agent",
                                    data={"output": "Complete"}))

    except Exception as e:
        event_queue.put(_make_event("error", data={"message": str(e)}))
    finally:
        event_queue.put(_make_event("done"))
        event_queue.put(None)


@app.websocket("/chat")
async def websocket_chat(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            msg = json.loads(data)
            query = msg.get("message", "")
            session_id = msg.get("sessionId", "default")
            provider = msg.get("provider")

            # Switch provider if requested
            if provider and provider != get_current_provider():
                global agent
                set_provider(provider)
                agent = create_agent(provider)

            if not query:
                await websocket.send_json(_make_event("error", data={"message": "Empty query"}))
                continue

            eq = queue.Queue()
            thread = threading.Thread(target=run_agent_streaming, args=(query, eq, session_id), daemon=True)
            thread.start()

            while True:
                try:
                    event = eq.get(timeout=0.05)
                except queue.Empty:
                    await asyncio.sleep(0.02)
                    continue

                if event is None:
                    break

                await websocket.send_json(event)

                if event["type"] in ("agent_start", "agent_complete"):
                    await asyncio.sleep(0.15)
                elif event["type"] == "token_stream":
                    await asyncio.sleep(0.02)

    except WebSocketDisconnect:
        print("Client disconnected")


@app.get("/health")
def health():
    return {"status": "ok", "agent": agent is not None, "provider": get_current_provider()}


@app.post("/switch")
async def switch_provider(body: dict):
    """Switch LLM provider. Body: {"provider": "gemini" | "openai"}"""
    global agent
    provider = body.get("provider", "gemini")
    set_provider(provider)
    agent = create_agent(provider)
    return {"status": "ok", "provider": provider}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
