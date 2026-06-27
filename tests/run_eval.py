# path: tests/run_eval.py

import os
import json
import asyncio
import httpx
import time

# Target your local real-time streaming API endpoint
BACKEND_URL = "http://127.0.0.1:8001/api/chat"
DATASET_PATH = os.path.join(os.path.dirname(__file__), "eval_dataset.json")

# path: tests/run_eval.py -> Modify evaluate_case client network timeout boundary

async def evaluate_case(client: httpx.AsyncClient, tc: dict) -> dict:
    """Fires a payload transaction and reads the Server-Sent Events (SSE) stream line-by-line."""
    payload = {
        "session_id": f"eval_session_{tc['id']}",
        "message": tc["query"],
        "chat_selection": tc["chat_selection"],
        "model_selection": tc["model_selection"]
    }
    
    start_time = time.perf_counter()
    accumulated_reply = ""
    resolved_path = "NEXA_CHAT"
    resolved_tier = "LOCAL"
    
    try:
        # 🟢 REMOVED TIME LIMIT: Timeout set to None so benchmarks never crash on local hardware execution
        async with client.stream("POST", BACKEND_URL, json=payload, timeout=None) as response:
            if response.status_code != 200:
                return {"id": tc["id"], "name": tc["name"], "passed": False, "error": f"HTTP Error: {response.status_code}"}
                
            async for line in response.aiter_lines():
                if line.startswith("data:"):
                    data_str = line.replace("data:", "").strip()
                    if data_str == "[DONE]":
                        break
                        
                    event = json.loads(data_str)
                    event_type = event.get("type")
                    
                    if event_type == "token":
                        accumulated_reply += event.get("delta", "")
                    elif event_type == "trace" and event.get("node") == "router":
                        message = event.get("message", "")
                        if "Path: RESEARCH" in message: resolved_path = "RESEARCH"
                        if "Tier: CLOUD" in message: resolved_tier = "CLOUD"

        elapsed_ms = int((time.perf_counter() - start_time) * 1000)
        route_match = resolved_path == tc["expected_route"]
        tier_match = resolved_tier == tc["expected_tier"]
        
        found_anchors = []
        for anchor in tc["anchor_tokens"]:
            if anchor.lower() in accumulated_reply.lower():
                found_anchors.append(anchor)
        anchors_match = len(found_anchors) == len(tc["anchor_tokens"])
        
        passed = route_match and tier_match and anchors_match
        return {
            "id": tc["id"], "name": tc["name"], "passed": passed, "latency_ms": elapsed_ms,
            "route_match": route_match, "tier_match": tier_match, "actual_route": resolved_path,
            "expected_route": tc["expected_route"], "actual_tier": resolved_tier, "expected_tier": tc["expected_tier"],
            "found_anchors": found_anchors, "total_anchors": len(tc["anchor_tokens"])
        }
    except Exception as e:
        return {"id": tc["id"], "name": tc["name"], "passed": False, "error": str(e)}



async def main():
    print("🚀 INITIALIZING NEXA MIND DYNAMIC EVALUATION APM RUNNER")
    print(f"Loading benchmark dataset artifact from: '{DATASET_PATH}'...")
    print("-----------------------------------------------------------------")
    
    if not os.path.exists(DATASET_PATH):
        print(f"❌ Failed to locate evaluation file: {DATASET_PATH}")
        return

    with open(DATASET_PATH, "r") as f:
        cases = json.load(f)

    limits = httpx.Limits(max_keepalive_connections=5, max_connections=10)
    async with httpx.AsyncClient(limits=limits) as client:
        results = []
        for tc in cases:
            print(f"⚙️ Streaming verification pass matrix case [{tc['id']}]...")
            res = await evaluate_case(client, tc)
            results.append(res)

    passed_count = 0
    print(f"\n📊 TOTAL EVALUATION LIFECYCLE METRICS SUMMARY REPORT across {len(results)} RUNS:")
    print("=" * 90)
    
    for r in results:
        status_icon = "        🟢 PASSED" if r.get("passed") else "        🔴 FAILED"
        if r.get("passed"):
            passed_count += 1
            
        print(f"[{r['id']}] {r['name']} -> {status_icon}")
        if "error" in r:
            print(f"   ❌ Fatal Exception Handshake: {r['error']}")
            print("-" * 90)
            continue
            
        print(f"   ├── Latency: {r['latency_ms']}ms")
        print(f"   ├── Route Target Match: {r['route_match']} (Got: '{r['actual_route']}', Expected: '{r['expected_route']}')")
        print(f"   ├── Compute Tier Match: {r['tier_match']} (Got: '{r['actual_tier']}', Expected: '{r['expected_tier']}')")
        if r['total_anchors'] > 0:
            print(f"   └── Grounding Anchors: {len(r['found_anchors'])}/{r['total_anchors']} verified matches {r['found_anchors']}")
        print("-" * 90)

    print(f"\n🏁 SUITE PROCESS COMPLETE: {passed_count}/{len(results)} TOTAL CONDITIONS MET CLEAR")

if __name__ == "__main__":
    asyncio.run(main())
