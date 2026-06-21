#!/usr/bin/env python3
import json
import sys
import time
from pathlib import Path

import httpx

from app.config.settings import settings

# Force root workspace resolution before executing application initialization calls
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


BACKEND_URL = f"http://{settings.server.host}:{settings.server.port}"
DATASET_PATH = PROJECT_ROOT / "scripts" / "eval_dataset.json"
REPORT_PATH = PROJECT_ROOT / "scripts" / "eval_report.md"


def load_dataset() -> list:
    if not DATASET_PATH.exists():
        print(f"❌ Operational Error: Target file dataset missing at {DATASET_PATH}")
        sys.exit(1)
    with open(DATASET_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def execute_test_case(client: httpx.Client, test_case: dict) -> dict:
    print(
        f"📡 Executing Matrix Target [{test_case['id']}] ({test_case['source_type']}) -> {test_case['name']}"
    )

    # 🎯 Perfectly aligned with ChatRequest schema validation parameters
    payload = {
        "session_id": f"eval-session-{test_case['id']}",
        "message": test_case["query"],
        "model_id": "auto",
        "mode": test_case.get("mode", "chat"),
    }

    result_template = {
        "id": test_case["id"],
        "name": test_case["name"],
        "source_type": test_case["source_type"],
        "passed": False,
        "expected_route": test_case["expected_route"],
        "actual_route": "ERROR",
        "expected_tier": test_case["expected_tier"],
        "actual_tier": "ERROR",
        "backend_ms": 0,
        "wall_time_ms": 0,
        "tokens": 0,
        "reasons": [],
        "status": "FAIL",
    }

    start_wall_time = time.perf_counter()
    try:
        response = client.post("/api/chat", json=payload, timeout=45.0)
        wall_time_ms = int((time.perf_counter() - start_wall_time) * 1000)
        result_template["wall_time_ms"] = wall_time_ms

        if response.status_code != 200:
            result_template["status"] = "FAIL"
            result_template["reasons"] = [
                f"HTTP Server Error: Status {response.status_code}"
            ]
            return result_template

        res_payload = response.json()

        # 🎯 Pulling from verified Pydantic schema keys: "reply" and "trace"
        reply_content = res_payload.get("reply", "")
        trace = res_payload.get("trace", {}) or {}

        meta = trace.get("metadata", {}) or {}
        metrics = trace.get("metrics", {}) or {}
        token_metrics = metrics.get("token_metrics", {}) or {}

        actual_route = meta.get("route", "UNKNOWN").upper()
        actual_tier = meta.get("tier", "Standard Stream")
        actual_tools = meta.get("tools_used", []) or []
        backend_internal_ms = metrics.get("total_ms", 0)
        total_tokens_consumed = token_metrics.get("total_tokens", 0)

        result_template["actual_route"] = actual_route
        result_template["actual_tier"] = actual_tier
        result_template["backend_ms"] = backend_internal_ms
        result_template["tokens"] = total_tokens_consumed

        # Validation checks
        route_ok = actual_route == test_case["expected_route"]
        tier_ok = actual_tier == test_case["expected_tier"]

        missing_tools = [
            t for t in test_case["expected_tools"] if t not in actual_tools
        ]
        tools_ok = len(missing_tools) == 0

        illegal_tools_run = [
            t for t in test_case["forbidden_tools"] if t in actual_tools
        ]
        isolation_ok = len(illegal_tools_run) == 0

        missing_anchors = [
            t
            for t in test_case["anchor_tokens"]
            if t.lower() not in reply_content.lower()
        ]
        anchors_ok = len(missing_anchors) == 0

        if not route_ok:
            result_template["reasons"].append(f"Route Mismatch (Got {actual_route})")
        if not tier_ok:
            result_template["reasons"].append(f"Tier Mismatch (Got '{actual_tier}')")
        if not tools_ok:
            result_template["reasons"].append(f"Missing Tools: {missing_tools}")
        if not isolation_ok:
            result_template["reasons"].append(
                f"Leaked Forbidden Tools: {illegal_tools_run}"
            )
        if not anchors_ok:
            result_template["reasons"].append(
                f"Missing Ground Anchors: {missing_anchors}"
            )

        if route_ok and tier_ok and tools_ok and isolation_ok and anchors_ok:
            result_template["passed"] = True
            result_template["status"] = "PASS"
            result_template["reasons"] = ["None"]

        return result_template

    except Exception as err:
        result_template["status"] = "CRASH"
        result_template["reasons"] = [f"Script Execution Exception: {str(err)}"]
        return result_template


def compile_markdown_report(results: list, run_duration: float):
    pass_count = sum(1 for r in results if r.get("passed", False))
    total_count = len(results)
    rate = (pass_count / total_count) * 100 if total_count > 0 else 0

    report = [
        "# 📉 NexusMind Automated System Testing & Grounding Eval Report",
        f"**Execution Date:** {time.strftime('%Y-%m-%d %H:%M:%S')} UTC",
        f"**Target System Core Version:** v{settings.app.version}",
        f"**Global Reliability Pass Rate:** `{pass_count}/{total_count} ({rate:.1f}%)`",
        f"**Complete Matrix Evaluation Sequence Clock:** {run_duration:.2f}s",
        "\n## 📊 Test Case Performance Matrix\n",
        "| ID | Test Target Name | Profile | Status | Route Validation | Tier Validation | App Latency | Wall Time | Failure Analysis Trace |",
        "|---|---|---|---|---|---|---|---|---|",
    ]

    for r in results:
        if "error" in r:
            report.append(
                f"| {r['id']} | {r['name']} | `{r['source_type']}` | 💥 **CRASH** | `ERROR` | - | - | - | `{r['error']}` |"
            )
        else:
            icon = "✅ PASS" if r["passed"] else "❌ FAIL"
            reasons_str = ", ".join(r["reasons"])
            report.append(
                f"| {r['id']} | {r['name']} | `{r['source_type']}` | {icon} | `{r['actual_route']}` / `{r['expected_route']}` | `{r['actual_tier']}` | {r['backend_ms']}ms | {r['wall_time_ms']}ms | {reasons_str} |"
            )

    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(report))
    print(f"📝 Comprehensive Markdown matrix summary compiled to: {REPORT_PATH}")


def main():
    print("🧠 Initializing Unified NexusMind Multi-Route Integration Tester...")
    dataset = load_dataset()
    test_results = []

    start_timer = time.perf_counter()
    with httpx.Client(base_url=BACKEND_URL) as client:
        try:
            client.get("/health")
        except Exception:
            print(
                f"❌ Error: Backend API is offline at {BACKEND_URL}. Fire up ./run_nexusmind.sh first."
            )
            sys.exit(1)

        for case in dataset:
            outcome = execute_test_case(client, case)
            test_results.append(outcome)
            print(f"Result Status Target Matrix: [{outcome['status']}]\n" + "=" * 70)

    run_duration = time.perf_counter() - start_timer
    compile_markdown_report(test_results, run_duration)

    if any(not r.get("passed", False) for r in test_results):
        print(
            "⚠️ Matrix complete: System variations found outside standard validation thresholds."
        )
        sys.exit(2)
    print(
        "✨ Matrix complete: Core execution tracks verified across all routes smoothly!"
    )


if __name__ == "__main__":
    main()
