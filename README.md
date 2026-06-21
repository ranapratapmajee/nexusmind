# NexusMind 🧠
> **Ask anything. Research deeply.**

NexusMind is a research-first AI assistant platform powered by a single frontend chatbot — **Nexa** — backed by a backend execution graph that routes each query to the most appropriate mode and model. It supports offline RAG over local PDFs, web search, direct LLM chat, and deep research workflows, with answer tracing so you can see how each response was produced. It leverages a high-performance **FastAPI** gateway alongside a modular **LangGraph Orchestration Engine**.

Instead of forcing developers to manually manage multiple granular settings, NexusMind simplifies cognitive friction down to just two macro front-end selections (**✨ Nexa Chat** and **🔬 Deep Research**) managed by an autonomous backend traffic broker. The architecture features sub-millisecond local guardrail interceptors, automated escalation paths, vectorized batch local RAG, and an **extensible Global Telemetry Framework** designed to monitor distributed AI lifecycles.

![Python](https://img.shields.io/badge/Python-3.12-blue?style=flat-square)
![FastAPI](https://img.shields.io/badge/FastAPI-1.0.0-green?style=flat-square)
![Streamlit](https://img.shields.io/badge/Streamlit-0.2.1-red?style=flat-square)
![LangGraph](https://img.shields.io/badge/Orchestration-LangGraph-blueviolet?style=flat-square)
![ChromaDB](https://img.shields.io/badge/VectorDB-ChromaDB-orange?style=flat-square)
![Status](https://img.shields.io/badge/Status-Active-success?style=flat-square)

---

## 🚀 Advanced Features

* **Dual Macro UI Framework** — Limits user friction down to just two core modes (*Nexa Chat* and *Deep Research*) directly within an elegant, theme-aware Streamlit interface featuring a floating input composer panel.
* **Autonomous Escalation Engine** — The core backend router automatically upgrades standard execution streams to deep research graphs if the semantic intent classifier detects that the query requires multi-step synthesis, structural code validation, or external documentation search.
* **Heuristic Input Governance** — Sub-millisecond pre-compiled regex filters and semantic domain-bounding checks catch prompt injection loops, system prompt disclosure attempts, or out-of-domain queries before touching expensive cloud or local model context layers.
* **Token-Masking Compliance Layer** — Automatically scans raw buffer streams and redacts sensitive PII/PHI strings (including Social Security Numbers, Credit Cards, IPv4 addresses, and Medical Record Numbers) on the local hardware edge.
* **Socratic Professor Persona Addendum** — Automatically triggers when educational or analysis intents are discovered via keywords like `"teach me"`, `"explain how"`, `"study"`, or `"learn"`. It swaps standard assistant utility prompts out for academic scaffolding, source citations, and active-recall verification checks.
* **High-Performance Batched RAG** — Overhauls slow synchronous RAG setups by executing parallel vectorized block transformations using a concurrency file-system reader and automated chunk hashing over local document datasets.
* **Zero-Cost Live Web Synthesis** — Scrapes and cleans public search metrics natively via DuckDuckGo HTML pipelines and `trafilatura` extraction libraries without requiring paid third-party search engine tokens or API keys.
* **Pluggable Global Telemetry Engine** — Implements a schema-agnostic, decentralized ledger manager (`TraceTracker`) that aggregates metadata configurations, precision performance benchmarks, and hierarchical chronological flow charts natively across parent and subgraphs without triggering memory reducer collisions.

---

## 🏗️ System Architecture Flow

```text
┌──────────────────────────────────────────────────────────────────────────────────┐
│                             NEXA FRONTEND WORKSPACE                              │
│                            Streamlit · localhost:8501                            │
│                                                                                  │
│    ┌────────────────────────────────────────────────────────────────────────┐    │
│    │    Floating Composer Input Panel  [✨ Nexa Chat  vs  🔬 Deep Research]  │    │
│    └───────────────────────────────────┬────────────────────────────────────┘    │
│                                        │                                         │
│                                        │ HTTP POST /api/chat                     │
└────────────────────────────────────────┼─────────────────────────────────────────┘
                                         │
┌────────────────────────────────────────▼─────────────────────────────────────────┐
│                            NEXUSMIND BACKEND GATEWAY                             │
│                             FastAPI · localhost:8001                             │
│                                                                                  │
│  ┌────────────────────────────────────────────────────────────────────────────┐  │
│  │ 1. INPUT HEURISTIC GOVERNANCE INTERCEPTOR (guardrails.py)                  │  │
│  │    ├── Pre-compiled Regex Filters (Catches prompt injection loops)         │  │
│  │    └── Token-Masking PII Compliance (Sub-millisecond local redaction)      │  │
│  └─────────────────────────────────────┬──────────────────────────────────────┘  │
│                                        │ Passed Safely                           │
│                                        ▼                                         │
│  ┌────────────────────────────────────────────────────────────────────────────┐  │
│  │ 2. INTENT PLANNER ROUTER NODE (core/graph.py)                              │  │
│  │    └── [Heuristic Fast-Path]  Checks length (< 4 words) & jargon keywords  │  │
│  └─────────────┬─────────────────────────────────────────────────┬────────────┘  │
│                │                                                 │               │
│                │ (Heuristic Bypass Triggered)                    │ (Closed /     │
│                │ LOW Compute / Simple Prompt                     │ Technical)    │
│                ▼                                                 ▼               │
│  ┌───────────────────────────┐                 ┌──────────────────────────────┐  │
│  │ 3. DIRECT CONVERSATIONAL  │                 │ 4. AUTONOMOUS ESCALATION     │  │
│  │    NODE (direct_llm_node) │                 │    ENGINE (DEEP_RESEARCH)    │  │
│  │                           │                 │    └── semantic_classifier   │  │
│  └─────────────┬─────────────┘                 └───────────────┬──────────────┘  │
│                │                                               │                 │
│                │                                               │ Routes Intent   │
│                │                                               ▼                 │
│                │                          ┌───────────────────────────────────┐  │
│                │                          │ 5. QUERY EXPANSION ENGINE         │  │
│                │                          │    └── Generates 3 Search Vectors │  │
│                │                          └────────────────────┬──────────────┘  │
│                │                                               │                 │
│                │                                               │ Parallel Exec   │
│                │                        ┌──────────────────────┴──────────────┐  │
│                │                        │ SANDBOX INFRASTRUCTURE              │  │
│                │                        │ (Colima VM / Managed Loops)         │  │
│                │                        │                                     │  │
│                │                        │ ┌─────────────────────────────────┐ │  │
│                │                        │ │ 6a. BATCH LOCAL RAG PIPELINE    │ │  │
│                │                        │ │     └── ChromaDB Cluster Port   │ │  │
│                │                        │ └────────────────┬────────────────┘ │  │
│                │                        │                  │                  │  │
│                │                        │                  ▼ Synthesis        │  │
│                │                        │ ┌─────────────────────────────────┐ │  │
│                │                        │ │ 6b. ZERO-COST WEB EXTRACTOR     │ │  │
│                │                        │ │     └── DuckDuckGo/Trafilatura  │ │  │
│                │                        │ └────────────────┬────────────────┘ │  │
│                │                        └──────────────────┼──────────────────┘  │
│                │                                           │                     │
│                │                                           ▼ Context Bound       │
│                │                          ┌───────────────────────────────────┐  │
│                │                          │ 7. SOCRATIC PROFESSOR PERSONA     │  │
│                │                          │    └── Dynamic System Prompt Mod  │  │
│                │                          └────────────────────┬──────────────┘  │
│                │                                               │                 │
│                └───────────────────────┬───────────────────────┘                 │
│                                        │                                         │
│                                        ▼ Unified Ingest                          │
│  ┌────────────────────────────────────────────────────────────────────────────┐  │
│  │ 8. UNIFIED LLM GATEWAY (llm/gateway.py)                                    │  │
│  │    └── Monitors token volume limits, records latency, manages cloud tiers  │  │
│  └─────────────────────────────────────┬──────────────────────────────────────┘  │
│                                        │                                         │
│  ┌─────────────────────────────────────▼──────────────────────────────────────┐  │
│  │ 9. EXTENSIBLE GLOBAL TELEMETRY FRAMEWORK (core/state.py)                   │  │
│  │    └── Isolates trace memory buffers natively via `copy.deepcopy()`        │  │
│  └─────────────────────────────────────┬──────────────────────────────────────┘  │
│                                        │                                         │
│                                        │ Returns Clean JSON-200 Response Payload │
└────────────────────────────────────────┼─────────────────────────────────────────┘
                                         ▼
┌──────────────────────────────────────────────────────────────────────────────────┐
│                             NEXA FRONTEND WORKSPACE                              │
│  Maps TraceTracker to native `st.code(..., language="text")` mono density panel  │
└──────────────────────────────────────────────────────────────────────────────────┘

```

---

## 📂 Project Directory Structure

```text
nexusmind/
├── app/                            # 🧠 UNIFIED BACKEND GRAPH CORES
│   ├── main.py                     # App bootstrap: sets up CORS and global logging channels
│   ├── api/
│   │   └── chat_routes.py          # Network ingress: receives payloads, pipes to runtime orchestrator
│   ├── chat/
│   │   └── chat_app.py             # Context normalizer: binds incoming HTTP sessions to LangGraph
│   ├── config/
│   │   ├── config.yaml             # Absolute environment configuration source-of-truth
│   │   └── settings.py             # Type-safe object mapping using Pydantic Settings
│   ├── core/                       # 🎛️ DOCKER / ORCHESTRATION HUB
│   │   ├── state.py                # Telemetry Core: holds memory-isolated `TraceTracker` & deepcopy reducers
│   │   ├── guardrails.py           # Ingress Shield: executes fast regex tracking & local token masking
│   │   ├── graph.py                # State Engine: houses the Heuristic Fast-Path and compiles nodes
│   │   └── engine.py               # Invoker Interface: instantiates thread workers for incoming streams
│   ├── agents/
│   │   └── research/               # 🔬 SYSTEM RESEARCH SUBGRAPHS
│   │       ├── research_state.py   # Isolated context matrices specific to search tasks
│   │       └── research_subgraph.py# Parallel multi-query generator and vector synthesis nodes
│   ├── llm/                        # 📡 RESOURCE ROUTING MUX
│   │   ├── gateway.py              # LLM Dispatcher: tracks prompt tokens and executes cloud fallbacks
│   │   ├── prompt_builder.py       # Prompt Layer: dynamically switches between Utility and Socratic modes
│   │   └── provider_clients.py     # Network Connectors: handles non-streaming local Ollama and Cloud clients
│   ├── rag/
│   │   ├── chunker.py              # Text Processing: recursive character string separators
│   │   ├── chroma_store.py         # DB Interactions: executes batch uploads and low-latency collections
│   │   └── ingest.py               # File Pipeline: high-performance local directory data parser
│   └── utils/
│       ├── fetch_url.py            # Extraction Engine: zero-cost text scraping with trafilatura
│       └── web_search.py           # Web Scanner: zero-cost live querying via DuckDuckGo HTML
│
├── frontend/                       # 🎨 DENSITY PRESENTATION LAYER
│   ├── streamlit_app.py            # Window Frame: aggregates sidebar configuration parameters and message streams
│   └── ui/
│       ├── api_client.py           # Network Client: async HTTPX communications mapping to backend port
│       ├── chat_ui.py              # Message Loop: handles layout grid frames for chat bubbles
│       ├── composer_ui.py          # Input Bar: handles active input selections and mode toggles
│       ├── formatters.py           # Visual Transformers: status indicators and clock metric conversions
│       ├── sidebar_ui.py           # Host Inspector: displays session diagnostics and data upload arrays
│       ├── state.py                # Cache Registry: initializes and persists browser runtime states
│       ├── styles.py               # Injection Matrix: runs theme-aware custom application CSS overrides
│       └── trace_ui.py             # Diagnostics Console: clean, high-density monospaced tree rendering
│
├── chroma-data/                    # Persistent storage volumes for vector search indices
├── data/                           # Ingestion target folder for reference manuals, docs, and PDFs
├── docker-compose.yaml             # ChromaDB server container initialization file
├── run_nexusmind.sh                # Unified background script: automatically handles infrastructure and service setup
├── run_backend.sh                  # Separated standalone api runner script
├── run_frontend.sh                 # Separated standalone dashboard interface runner
├── pyproject.toml                  # Project manifest: pinned package specifications managed via uv
├── scripts/                        # Management maintenance tools
│   ├── run_ingest.py               # Local execution parsing pipeline CLI tool
│   ├── architechture.md            # Structural code design documentation records
│   └── test_cases.md               # Pipeline verification boundary data models
├── PLANNING.md
├── README.md
└── uv.lock                         # Pinned explicit package tracking index manifest

```

---

## 🏗️ Detailed System Architecture & Control Flow

The entire lifecycle of a query relies on the **Compute Budget Principle**. Computationally expensive agentic workflows are held in reserve, only spinning up if the request demands heavy reasoning.

Here is the step-by-step technical journey a message takes through NexusMind:

### 1. Ingress & Edge Interception (FastAPI ⟶ Guardrails)

* The user enters a prompt into the Streamlit composer panel. The frontend converts this to a structured payload and fires a `POST` request to `/api/chat` on the FastAPI gateway (`localhost:8001`).
* Before hitting LangGraph, the payload passes through `guardrails.py`.
* Sub-millisecond pre-compiled regex arrays inspect the string for systemic injection indicators.
* Concurrently, a local token-masking compliance layer scans the input stream buffer, automatically swapping out any exposed PII data (IP addresses, credit card matches, SSN strings) before allocation occurs.

### 2. Telemetry Seeding & Core State Ingestion

* If the validation passes, a fresh telemetry packet is initialized. The application states pass to the `TraceTracker` module inside `app/core/state.py`.
* **The Memory Loop Isolation Patch:** To prevent multi-threaded lockups where internal logs mutate mid-flight, the tracker forces a hard `copy.deepcopy()` operation on the state parameters. This severs memory references to the live state dictionary channels and isolates lists safely inside their own RAM registers.

### 3. Heuristic Filtering & The Fast-Path Decision (The Planner Node)

* The state passes into the unified LangGraph compilation layer in `app/core/graph.py`. The execution stream encounters the **Intent Planner Node** first.
* **The Heuristic Optimization Bypass:** The query length and formatting are checked against low-complexity triggers. If the input is a standard greeting (e.g., *"hi"*, *"hello"*) or an extremely short sentence devoid of technical jargon terms, the system activates a fast-path heuristic bypass.
* The router bypasses the semantic LLM evaluator completely, registers the classification as `LOW`, logs a trace event (`Heuristic fast-path engaged. LLM bypass successful.`), and shifts the state target parameter to `direct_llm`.

### 4. Semantic Escalation & Parallel Search Generation (The Deep Research Path)

* If the input contains complex parameters or engineering jargon (e.g., *"What are the use cases of LangGraph?"*), the heuristic bypass stays closed, and the system runs semantic classification.
* The planner passes the text to the `semantic_intent_classifier` through the local provider client. If classified as `HIGH`, it routes execution to `DEEP_RESEARCH`.
* The state changes its target tracking value to `query_expansion`. Here, the system splits the primary user objective into **three distinct search queries**.
* These expanded queries are handed off in parallel to the `research_subgraph` system:
* **Local Ingest Point:** The sub-nodes query your containerized ChromaDB database cluster (managed on the local machine via Colima) to retrieve matched technical snippets.
* **External Extraction Point:** Simultaneously, if cloud tracking is enabled, the system drops zero-cost search hooks into the web lookup utility, parsing live web documents.



### 5. Resolution & Monospaced Diagnostics Presentation

* The collected context data blocks are concatenated, deduped, and structured into an advanced reference layout.
* The system checks the query context for instructional or educational goals. If keywords match, the `prompt_builder.py` appends a **Socratic Professor Persona Addendum**, forcing the model to wrap its final output in structured academic scaffolding and citation tracking.
* The consolidated payload hits the unified LLM gateway (`llm/gateway.py`), logs the total runtime latency metrics, and returns the response array to the UI as a JSON-200.
* On the frontend, `trace_ui.py` picks up the data payload. Instead of processing slow HTML frames or messy paragraphs, it feeds the raw strings directly into a native `st.code(..., language="text")` code block wrapper. This guarantees a clean, compact, and monospaced console tree display that loads instantly.

---

## 📈 Execution Profiles Matrix

| Mode | Trigger Keyword Signatures | Internal Action Path | Selected Compute Target |
| --- | --- | --- | --- |
| **✨ Nexa Chat** | *Standard conversational input, greetings, or very short requests.* | Direct language inference bypassing heavy graph computation. | Local `Ollama` primary node instances. |
| **🎓 Socratic Professor** | `"teach me"`, `"explain how"`, `"study"`, `"learn"` | Appends instructional addendums + drops an active-recall evaluation check. | Upgraded Local/Cloud depending on task layer weights. |
| **🔬 Deep Research** | Explicitly clicked, or triggered by high complexity parameters. | Triggers multi-step background loops, fetches local vector points, scrapes web variables. | Advanced Cloud `Gemini` compute with local fallback. |

---

## 💻 Streamlit Interface & Control Panels

The Streamlit user interface (`frontend/ui/sidebar_ui.py`) features an interactive high-density engineering dashboard to manage local workspace loops.

### ⚡ Session Controls & Commands

* **✨ New Session** — Flushes runtime buffers and clears mid-flight variables to spin up an isolated core environment instance.
* **🗑️ Reset** — Completely drops the cached session message history layer across the application.
* **🔌 Ping Host** — Issues an HTTP lifecycle health check ping directly to the local FastAPI port configuration cluster to assess connection limits.
* **🔄 Sync Models** — Forces a backend refresh operation to flush local model catalogs and dynamically populate available model drops.
* **📋 Session Identity** — Displays and allows copying of the unique uuid session identifier directly to copyboards for log auditing.

### 📖 Operations Glossary & Indicators

* `CONNECTED` / `OFFLINE` **Status Dot** — Displays active socket health using an illuminated neon indicator (`dot-online` vs `dot-warning`).
* **🤖 Standard Assistant** — Low-latency, fast localized text generation handled completely on local silicon.
* **🔷 Deep Analysis** — Multi-query parallel vector scans executing cross-tier cloud synthesis cascades.
* **📱 User Selected** — Overridden execution tracks locked by the manual composer pill selections.
* **⚡ Dynamic Route** — Automated backend scalability activated dynamically based on query accuracy heuristics.

---

## 🛠️ Getting Started

### Prerequisites

* Python 3.12+ managed by **`uv`**
* Ollama local model server active (`ollama run qwen2.5-coder:3b-instruct`)
* Colima Virtual Machine or Docker Desktop running on the host layer

### 🚀 Zero-Configuration Unified Boot Script

NexusMind includes an intelligent shell orchestrator script that automatically syncs dependencies, boots virtualization runtimes, verifies model ports, mounts background processes, and displays a unified operations dashboard.

To launch the full stack, simply make the script executable and run it from your project root directory:

```bash
chmod +x run_nexusmind.sh
./run_nexusmind.sh

```

The terminal interface will clear and display your service routing matrix:

```text
NexusMind Platform Online (Colima Engine)
--------------------------------------
UI Dashboard : http://localhost:8501
Backend API  : http://localhost:8001
--------------------------------------
Press [CTRL+C] to exit and stop Colima completely.

```

---

## ⚙️ APM Telemetry Trace Logs

Every response card generated by NexusMind includes an expandable high-density text console trace panel mapping the structural schema registers:

```text
📡 PLATFORM ENGINE  ::  [ROUTE: DEEP_RESEARCH]  [MODE: 🔷 Deep Analysis | ⚡ Dynamic Route]
🐳 INFRASTRUCTURE   ::  [VIRTUALIZATION: Colima (Apple vz/virtiofs)]
🗄️ VECTOR STORE     ::  [ENGINE: ChromaDB Container Cluster]
🧠 LOGICAL COMPUTE  ::  [TIER: Advanced Reasoning]  [MODEL: gemini-2.5-flash]

⛓️ PIPELINE CHRONOLOGICAL FLOW DIAGRAM
 ├── 🟢 [1] User Request Entry ──> [Payload Ingested]
 ├── 🟢 [2] Security Check Engine ──> [Nexus Guardrails V2 Active]
 ├── 🟢 [3] governance_node ──> [Input governance verification clear.]
 ├── 🟢 [4] Intent Classifier (⚡ Dynamic Route) ──> [Allocated Tier: 🔷 Deep Analysis]
 ├── 🟢 [5] Query Expansion Engine ──> [Generated 3 search vectors for RAG optimization]
 ├── 🟢 [6] Colima Virtual Machine Context Handshake ──> [Docker/Chroma DB Ready, Link Stable]
 ├── 🟢 [7] ChromaDB Unified Retrieval ──> [Match Confirmed across vectors (Dist: 0.32)]
 ├── 🟢 [8] LLM Compute Core ──> [Dispatching instructions to network gateway (gemini-2.5-flash)]
 └── 🏁 Terminal Exit Handshake (4250ms)

📚 VECTOR COLLECTION INFORMATION
 ├── [INDEX: nexus_knowledgebase]  [RETRIEVED_TOP_K: 6]
 ├── [1] api_client.py // HTTP Adapter ── "class APIClient: def post(self, url, json_payload)..."
 ├── [2] state.py // Telemetry Register ── "class TraceTracker: def compiled_trace(self)..."
 └── ✅ data grounding verification clear

⚡ TRIGGERED ACTIVE TOOLS :: [token_masker, regex_guardrails, semantic_intent_classifier, query_expansion_engine, chroma_retriever]

```

---

## 📥 Ingestion & Document Management

NexusMind supports dual-path ingestion pipelines for engineering reference manuals, textbooks, or research papers.

### Path A: Frontend Web Workspace Upload

1. Navigate to the left dashboard control panel on the frontend app (`http://localhost:8501`).
2. Open the **DATA SOURCE MANAGEMENT** expander card.
3. Drop in your technical document `.pdf`. The file is securely written as a multipart stream payload straight to the backend context RAG pipeline where background vector workers chunk, embed, and index it asynchronously.

### Path B: Local Directory Command Line Core Ingester

Drop your research file vectors directly inside the root folder named `./data/`, and run our custom, absolute-pathed execution command line script module:

```bash
python scripts/run_ingest.py

```

---

## 👥 Developer & Maintenance Framework

Developed by **Ranapratap Majee** — Elite Engineering Workspace.

Licensed under the `MIT License` schemas guidelines.