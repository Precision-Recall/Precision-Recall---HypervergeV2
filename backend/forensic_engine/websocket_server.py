"""
WebSocket server for the Forensic Engine.
Streams real agent execution events.

Compatible with the frontend's ForensicWebSocketClient:
- Connects to ws://localhost:6060 (root path)
- Receives: {type: "promise_vs_reality", params: {company, promise_year, ...}}
- Sends: {type: "agent_start"|"tool_call"|"token_stream"|..., data: {...}, timestamp: "..."}
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

from config import WS_PORT
from agent import create_forensic_agent

agent = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global agent
    print("🚀 Initializing Forensic Agent...")
    agent = create_forensic_agent()
    print("✅ Forensic Agent ready.")
    yield


app = FastAPI(lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


def _event(event_type: str, **kwargs) -> dict:
    return {"type": event_type, "timestamp": time.time() * 1000, **kwargs}


def _truncate(text, n=300):
    s = str(text)
    return s[:n] + ("..." if len(s) > n else "")


def _params_to_query(msg_type: str, params: dict) -> str:
    """Convert frontend's structured params into a natural language query."""
    company = params.get("company", "unknown")
    lens = params.get("lens", "finance")

    if msg_type == "promise_vs_reality":
        return (
            f"Promise vs Reality: In {params.get('promise_year', 2018)}, did {company} make commitments "
            f"related to '{params.get('promise_query', '')}'? Check the {params.get('verification_year', 2023)} "
            f"filing to see if they delivered. Focus lens: {lens}."
        )
    elif msg_type == "anomaly_detection":
        return (
            f"Anomaly Detection: Compare {company}'s risk factor language between "
            f"{params.get('start_year', 2022)} and {params.get('end_year', 2023)}. "
            f"Flag significant changes in legal risk disclosures, internal controls, "
            f"or related party transactions. Focus lens: {lens}."
        )
    elif msg_type == "sentiment_divergence":
        return (
            f"Sentiment Divergence: Analyze {company}'s {params.get('year', 2023)} 10-K. "
            f"Is the CEO's tone in MD&A optimistic while the financial footnotes and "
            f"market risk sections show concerning signals? Focus lens: {lens}."
        )
    else:
        return str(params.get("query", params.get("message", str(params))))


def _collect_sources(output) -> list[dict]:
    """Extract source metadata from tool outputs — mirrors agent_system pattern."""
    sources = []
    if isinstance(output, dict):
        # Handle evidence lists (search_promise_evidence, search_sentiment_signals)
        for key, val in output.items():
            if isinstance(val, list):
                for item in val:
                    if isinstance(item, dict) and ("section" in item or "company" in item):
                        sources.append({
                            "company": output.get("company") or item.get("company"),
                            "year": output.get("year") or output.get("year_a") or item.get("year"),
                            "section": item.get("section"),
                            "section_item": item.get("section_item"),
                            "page": item.get("page"),
                            "text": str(item.get("text", ""))[:300],
                        })
        # Handle explicit sources key
        if "sources" in output and isinstance(output["sources"], list):
            for s in output["sources"]:
                if isinstance(s, dict):
                    sources.append(s)
    elif isinstance(output, list):
        for item in output:
            if isinstance(item, dict) and "company" in item:
                sources.append({
                    "company": item.get("company"),
                    "year": item.get("year"),
                    "section": item.get("section"),
                    "page": item.get("page"),
                    "text": str(item.get("text", ""))[:300],
                })
    return sources


def _build_citation_graph(query: str, sources: list[dict]) -> dict:
    """Build citation graph from collected sources — same as agent_system."""
    nodes = [{"id": "query", "type": "query", "label": query[:80]}]
    edges = []
    tool_nodes_seen = set()

    for s in sources:
        tool_id = f"tool-{s.get('section', 'unknown')}"
        if tool_id not in tool_nodes_seen:
            tool_nodes_seen.add(tool_id)
            nodes.append({"id": tool_id, "type": "tool", "label": s.get("section", "Unknown")})
            edges.append({"source": "query", "target": tool_id})

        src_id = f"src-{s.get('company', '')}-{s.get('year', '')}-{s.get('section', '')}-{s.get('page', '')}"
        nodes.append({
            "id": src_id, "type": "source",
            "label": f"{s.get('company', '')} {s.get('year', '')}",
            "section": s.get("section", ""),
            "page": s.get("page"),
            "text": str(s.get("text", ""))[:100],
        })
        edges.append({"source": tool_id, "target": src_id})

    return {"nodes": nodes, "edges": edges}


def run_agent_streaming(query: str, eq: queue.Queue, session_id: str = "default"):
    """Run the forensic agent, pushing real events to the queue."""
    all_sources = []
    try:
        eq.put(_event("agent_start", agent="Forensic Accountability Agent",
                       data={"type": "forensic"}))
        eq.put(_event("reasoning", data={
            "type": "intent",
            "description": f'Analyzing: "{query[:120]}"',
        }))

        config = {"configurable": {"thread_id": session_id}}

        for event in agent.stream(
            {"messages": [("user", query)]},
            stream_mode="updates",
            config=config,
        ):
            for node_name, node_data in event.items():
                for msg in node_data.get("messages", []):
                    try:
                        msg_type = msg.type if hasattr(msg, "type") else type(msg).__name__

                        # Agent decides to call tool(s)
                        if msg_type == "ai" and hasattr(msg, "tool_calls") and msg.tool_calls:
                            for tc in msg.tool_calls:
                                tool_name = tc.get("name", "")
                                tool_args = tc.get("args", {})
                                eq.put(_event("reasoning", data={
                                    "type": "tool_call",
                                    "description": f"Calling {tool_name}",
                                }))
                                eq.put(_event("tool_call", tool=tool_name,
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

                            # Strip raw_content from sources before sending to frontend
                            if isinstance(output, dict) and "sources" in output:
                                output = {**output, "sources": [
                                    {k: v for k, v in s.items() if k != "raw_content"}
                                    for s in output["sources"]
                                ]}

                            try:
                                if len(json.dumps(output, default=str)) > 3000:
                                    output = {"result": _truncate(json.dumps(output, default=str), 2500),
                                              "truncated": True}
                            except Exception:
                                output = {"result": _truncate(str(output), 2500)}

                            eq.put(_event("tool_complete", tool=tool_name,
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
                                        eq.put(_event("token_stream", token=word + " "))

                    except Exception as e:
                        eq.put(_event("reasoning", data={
                            "type": "tool_call",
                            "description": f"⚠️ {str(e)[:100]}",
                        }))

        # Emit sources + citation graph
        if all_sources:
            seen = set()
            unique = []
            for s in all_sources:
                key = f"{s.get('company')}-{s.get('year')}-{s.get('section')}-{s.get('page')}"
                if key not in seen:
                    seen.add(key)
                    unique.append(s)
            for i in range(0, len(unique), 5):
                eq.put(_event("sources", data={"sources": unique[i:i + 5]}))

            eq.put(_event("citation_graph", data=_build_citation_graph(query, unique)))

        eq.put(_event("agent_complete", agent="Forensic Accountability Agent",
                       data={"output": "Complete"}))

    except Exception as e:
        eq.put(_event("error", data={"message": str(e)}))
    finally:
        eq.put(_event("done"))
        eq.put(None)


async def _drain_queue(websocket: WebSocket, eq: queue.Queue):
    """Drain the event queue and send events to the WebSocket client."""
    while True:
        try:
            evt = eq.get(timeout=0.05)
        except queue.Empty:
            await asyncio.sleep(0.02)
            continue
        if evt is None:
            break
        await websocket.send_json(evt)
        if evt["type"] in ("agent_start", "agent_complete"):
            await asyncio.sleep(0.15)
        elif evt["type"] == "token_stream":
            await asyncio.sleep(0.02)


@app.websocket("/")
async def websocket_root(websocket: WebSocket):
    """Root WebSocket — frontend ForensicWebSocketClient connects here."""
    await websocket.accept()
    try:
        await websocket.send_json(_event("connected", data={
            "message": "Connected to Forensic Engine",
            "modes": ["promise_vs_reality", "anomaly_detection", "sentiment_divergence"],
        }))

        while True:
            data = await websocket.receive_text()
            msg = json.loads(data)
            msg_type = msg.get("type", "")
            params = msg.get("params", {})

            if msg_type == "ping":
                await websocket.send_json(_event("pong", data={"status": "healthy"}))
                continue

            query = _params_to_query(msg_type, params)

            eq = queue.Queue()
            thread = threading.Thread(
                target=run_agent_streaming,
                args=(query, eq, f"forensic-{id(websocket)}"),
                daemon=True,
            )
            thread.start()
            await _drain_queue(websocket, eq)

    except WebSocketDisconnect:
        print("Client disconnected")
    except Exception as e:
        print(f"WebSocket error: {e}")


@app.get("/health")
def health():
    return {"status": "ok", "agent": agent is not None}


if __name__ == "__main__":
    print("=" * 60)
    print("Forensic Accountability & Anomaly Detector")
    print(f"WebSocket: ws://localhost:{WS_PORT}")
    print("=" * 60)
    uvicorn.run(app, host="0.0.0.0", port=WS_PORT)
