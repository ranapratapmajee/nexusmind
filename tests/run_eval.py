# path: tests/run_eval.py

import os
import json
import asyncio
import httpx
import time

# Target your local API service endpoint port
BACKEND_URL = "http://127.0.0.1:8001/api/chat"
DATASET_PATH = os.path.join(os.path.dirname(__file__), "eval_dataset.json")

async def evaluate_case(client: httpx.AsyncClient, tc: dict) -> dict:
    """Fires a single transaction payload with explicit exception string trapping."""
    payload = {
        "session_id": f"eval_session_{tc['id']}",
        "message": tc["query"],
        "model_id": "auto",
        "mode": tc["mode"]
    }
    
    start_time = time.perf_counter()
    try:
        # Give deep research ample room to scrape and synthesize over local hardware
        resp = await client.post(BACKEND_URL, json=payload, timeout=60.0)
        elapsed_ms = int((time.perf_counter() - start_time) * 1000)
        
        if resp.status_code != 200:
            return {
                "id": tc["id"], 
                "name": tc["name"], 
                "passed": False, 
                "error": f"HTTP Gateway Error Status Code: {resp.status_code} - {resp.text}"
            }
            
        data = resp.json()
        reply = data.get("reply", "")
        logs = data.get("trace_logs", [])
        
        # 1. Evaluate Routing & Tier Assertions
        logs_str = "".join([l.get("node_identifier", "").lower() + l.get("telemetry_message", "").lower() for l in logs])
        
        # Locate if research sub-tracks or fast paths were cleanly engaged
        actual_route = "research" if "research" in logs_str or "gather_sources" in logs_str else "direct_llm"
        route_match = actual_route == tc["expected_route"]
        
        # 2. Evaluate Anchors with fuzzy lookups (matches substrings/stems)
        found_anchors = [anchor for anchor in tc["anchor_tokens"] if anchor.lower() in reply.lower()]
        anchors_match = len(found_anchors) == len(tc["anchor_tokens"])
        
        passed = route_match and anchors_match
        
        return {
            "id": tc["id"],
            "name": tc["name"],
            "passed": passed,
            "latency_ms": elapsed_ms,
            "route_match": route_match,
            "actual_route": actual_route,
            "expected_route": tc["expected_route"],
            "found_anchors": found_anchors,
            "total_anchors": len(tc["anchor_tokens"])
        }
        
    except httpx.TimeoutException:
        return {"id": tc["id"], "name": tc["name"], "passed": False, "error": "Network Timeout: Server exceeded execution budget limit."}
    except Exception as e:
        err_msg = str(e) if str(e).strip() else f"Direct Connection Drop Refused (Type: {type(e).__name__})"
        return {"id": tc["id"], "name": tc["name"], "passed": False, "error": err_msg}


async def main():
    print("🚀 INITIALIZING NEXA MIND AUTOMATED APM EVALUATION SUITE")
    print(f"Loading benchmark test dataset from: '{DATASET_PATH}'...")
    print("-----------------------------------------------------------------")
    
    try:
        with open(DATASET_PATH, "r") as f:
            cases = json.load(f)
    except Exception as e:
        print(f"❌ Failed to load dataset file artifact: {e}")
        return

    limits = httpx.Limits(max_keepalive_connections=5, max_connections=10)
    async with httpx.AsyncClient(limits=limits) as client:
        # Process metrics sequentially to prevent local port starvation
        results = []
        for tc in cases:
            print(f"⚙️ Running evaluation matrix tier case [{tc['id']}]...")
            res = await evaluate_case(client, tc)
            results.append(res)

    passed_count = 0
    print(f"\n📊 EXECUTION RESULTS ACROSS {len(results)} CASE MATRIX RUNS:")
    print("=" * 80)
    
    for r in results:
        status_icon = "🟢 PASSED" if r.get("passed") else "🔴 FAILED"
        if r.get("passed"):
            passed_count += 1
            
        print(f"[{r['id']}] {r['name']} -> {status_icon}")
        if "error" in r:
            print(f"   ❌ Fatal Exception Handshake: {r['error']}")
            print("-" * 80)
            continue
            
        print(f"   ├── Latency: {r['latency_ms']}ms | Engine Route Match: {r['route_match']} (Got: '{r['actual_route']}', Expected: '{r['expected_route']}')")
        if r['total_anchors'] > 0:
            print(f"   └── Grounding Anchors: {len(r['found_anchors'])}/{r['total_anchors']} verified matches {r['found_anchors']}")
        print("-" * 80)

    print(f"\n🏁 SUITE VERIFICATION REPORT SUMMARY: {passed_count}/{len(results)} MATCHES CLEAR")

if __name__ == "__main__":
    asyncio.run(main())