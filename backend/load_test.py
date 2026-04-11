"""
Load test — sends questions from CSV to the agent WebSocket in parallel.
Traces land in LangSmith automatically (already configured in agent_system).

Usage:
    python load_test.py                          # 5 workers (default)
    python load_test.py --workers 10             # 10 workers
    python load_test.py --workers 3 --limit 10   # 3 workers, first 10 questions
"""

import asyncio
import csv
import json
import time
import argparse
import websockets

WS_URL = "ws://localhost:8000/chat"
CSV_PATH = "Questions Dataset.csv"


async def run_question(sem: asyncio.Semaphore, idx: int, question: str, session_prefix: str):
    """Send one question to the agent WS and wait for completion."""
    async with sem:
        start = time.time()
        session_id = f"{session_prefix}-{idx}"
        try:
            async with websockets.connect(WS_URL) as ws:
                await ws.send(json.dumps({
                    "message": question,
                    "sessionId": session_id,
                }))

                # Drain events until done
                while True:
                    msg = await asyncio.wait_for(ws.recv(), timeout=120)
                    data = json.loads(msg)
                    if data.get("type") in ("done", "error"):
                        break

            elapsed = round(time.time() - start, 1)
            print(f"  ✓ Q{idx:02d} ({elapsed}s): {question[:80]}")
            return {"idx": idx, "status": "ok", "elapsed": elapsed}

        except Exception as e:
            elapsed = round(time.time() - start, 1)
            print(f"  ✗ Q{idx:02d} ({elapsed}s): {str(e)[:80]}")
            return {"idx": idx, "status": "error", "error": str(e), "elapsed": elapsed}


async def main(workers: int, limit: int | None):
    # Load questions
    with open(CSV_PATH, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        questions = [(int(row["id"].replace("Q", "")), row["question"]) for row in reader]

    if limit:
        questions = questions[:limit]

    print(f"{'=' * 60}")
    print(f"Load Test — {len(questions)} questions, {workers} workers")
    print(f"Target: {WS_URL}")
    print(f"Traces → LangSmith (Hyp-fin project)")
    print(f"{'=' * 60}\n")

    sem = asyncio.Semaphore(workers)
    session_prefix = f"loadtest-{int(time.time())}"
    start = time.time()

    tasks = [run_question(sem, idx, q, session_prefix) for idx, q in questions]
    results = await asyncio.gather(*tasks)

    elapsed = round(time.time() - start, 1)
    ok = sum(1 for r in results if r["status"] == "ok")
    err = sum(1 for r in results if r["status"] == "error")
    avg_time = round(sum(r["elapsed"] for r in results) / len(results), 1) if results else 0

    print(f"\n{'=' * 60}")
    print(f"Done in {elapsed}s — {ok} ok, {err} errors, avg {avg_time}s/question")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--workers", type=int, default=5)
    parser.add_argument("--limit", type=int, default=None)
    args = parser.parse_args()
    asyncio.run(main(args.workers, args.limit))
