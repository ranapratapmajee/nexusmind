# NexusMind — Vision & Engineering Roadmap

> Living strategic planning, alignment, and Architectural Decision Record (ADR) manifest tracking current implementation achievements and future development horizons.

---

## 🎯 Product Vision & Core Pillars

NexusMind is an elite, high-density AI research and engineering development workspace built around a single, clean chatbot interface—**Nexa**. 

Designed as a specialized tool for intensive AI/ML study, source-grounded exploration, and deep academic reasoning, the platform operates on five foundational principles:

1. **Cognitive Simplicity (One Assistant UI)**
   * Nexa is the sole user-facing interface. Frontend workflows collapse messy backend complexities down into a focused, distraction-free reading canvas.
2. **Autonomous Server-Side Routing**
   * The backend dynamically handles execution paths, heuristic validation, and model selection. Orchestration stays server-side to enable zero-downtime path updates without frontend structural modifications.
3. **Local-First, Cost-Aware Infrastructure**
   * Prioritize local hardware execution paths using Ollama (`qwen2.5-coder:3b-instruct`). Scale selectively up to advanced cloud-reasoning layers only when task complexity or autonomous escalation demands it.
4. **Source-Grounded Traceability**
   * Transparency is a product feature, not an afterthought. Every response exposes internal system states, providing full wall-clock metrics and context provenance down to individual text snippets.
5. **Hyper-Focused Verticals**
   * Prioritize high-signal research tools, fast document ingestion, and deeply analytical personas over feature sprawl.

---

## 🏗️ Consolidated Core Architecture (Flat Project Workspace Layout)

Following a thorough modular cleanup and layout refactoring, all codebase paths have been flattened to the root workspace layer. This eliminates nested folder complexities, structural sync drift, and Python relative path evaluation exceptions (`ModuleNotFoundError`):

### Unified Architecture Layout (`nexusmind/`)
* `app/config/` — Type-safe validation engine using Pydantic Settings singletons (`settings.py`) driven by a central, unified `config.yaml` file with dynamic system placeholder interpolation.
* `app/core/` — Primary orchestration loop (`graph.py`, `engine.py`, `state.py`) running LangGraph state machines, Pydantic type-safe routing, and conditional workflow edges.
* `app/core/guardrails.py` — High-performance governance layer running pre-compiled sub-millisecond regex threat mapping, prompt injection defense, and heuristic domain semantic checking.
* `app/api/` — Web-routing layer (`chat_routes.py`) exposing FastAPI gateway endpoints and streaming options maps.
* `app/chat/` — App coordinator (`chat_app.py`) managing conversational options broadcasting and raw JSON telemetry log normalization.
* `app/agents/research/` — Context workspace matrices and parallelized hybrid retrieval-scraping loops (`research_subgraph.py`).
* `app/llm/` — Unified LLM provider access interface gateway (`gateway.py`) abstracting local Ollama endpoints and Google cloud endpoints (`gemini-2.5-flash`).
* `app/rag/` — Consolidated vector data pipeline (`chroma_store.py`, `ingest.py`) handling asynchronous chunk tracking, local token embeddings generation, and batch upserts.
* `frontend/` — High-cohesive frontend UI modules (`streamlit_app.py`, `ui/trace_ui.py`) presenting center-canvas grids, terminal-style monospaced diagnostic expanders, and asynchronous pipeline components.
* `scripts/` — Independent operational utility scripts (`run_ingest.py`) designed for manual ingestion via explicit native package calls (`python -m scripts.run_ingest`).

---

## 🚀 Engineering Registry (Completed Sprint)

### Routing & Orchestration Optimizations
- [x] **Heuristic Fast-Path Bypass:** Engineered a pre-LLM routing filter in `planner_node` that detects simple (<4 words) greetings and test commands, bypassing the 1.4s semantic LLM classification entirely and routing directly to local chat.
- [x] **Memory-Safe Telemetry Framework:** Identified and resolved a silent thread-locking Ouroboros (infinite loop) in `TraceTracker` caused by LangGraph's shallow state copies. Implemented `copy.deepcopy()` to sever memory references during telemetry logging.
- [x] **Unified Foreground/Background Booting:** Patched the `run_nexusmind.sh` shell orchestrator to properly background `&` both FastAPI and Streamlit, utilizing a `wait` block to trap `SIGINT` (CTRL+C) for graceful cross-container teardowns.

### Security & Input Governance
- [x] **Token-Masking PII Compliance:** Implemented local redaction capabilities to strip IPv4 addresses, SSNs, and credit card patterns before payload allocation.
- [x] **Pre-compiled Interceptors:** Integrated sub-millisecond regex threat mapping and query semantic verification blocks inside `guardrails.py`.

### Frontend & Diagnostic Enhancements
- [x] **Terminal-Style Execution Traces:** Rebuilt `trace_ui.py` to strip out heavy HTML/CSS logic, replacing it with pure native Streamlit Markdown and `st.code(..., language="text")` for perfect, micro-density monospaced alignment.
- [x] Eliminated paragraph squashing artifacts caused by Streamlit's native markdown rendering of nested telemetry arrays.

### Foundational Layout & Data Pipelines
- [x] Eliminated nested `backend/` directory artifacts, flattening the application codebase directly to the workspace root.
- [x] Switched to type-safe Pydantic `settings.py` schema singletons (`NexusSettings`).
- [x] Fixed Python's relative import lookup errors within `scripts/` utilities through standard module flag execution rules.
- [x] Introduced high-throughput file chunk batching by grouping slices to process parallel vectorized matrices into ChromaDB.

---

## 📈 Active Pipeline Overhauls (In Progress)

### RAG & Retrieval Tuning
- [ ] Benchmark retrieval quality on specialized technical manuals and datasets.
- [ ] Adjust chunk size and character overlap settings to ensure dense formulas and code loops do not get truncated across adjacent context blocks.
- [ ] Evaluate performance gains from adding semantic rerankers (like FlashRank or cross-encoders) to the post-retrieval pipeline.

### Execution Completeness
- [ ] Refine the Socratic persona trigger rules to accurately catch complex technical queries without generating false positives during standard conversations.

---

## 🗺️ Next Milestones & Future Scope

### Milestone 1 — Stable, Production-Grade Systems Core
* **Goal:** Turn the refined, single-session core into an absolute rock-solid foundation.
* [ ] Integrate explicit Request ID injection tracking across the entire LangGraph call matrix to make log-tracing seamless.
* [ ] Standardize logging outputs across all modules to emit structured JSON streams matching standard cloud deployment parameters.
* [ ] Add comprehensive integration test hooks to validate endpoint performance using mock query profiles.

### Milestone 2 — Advanced User Experience Refinements
* **Goal:** Elevate Nexa from a static click-and-wait app to a highly responsive developer environment.
* [ ] Implement token-by-token streaming responses across both the FastAPI gateway and the custom Streamlit chat message components.
* [ ] Build interactive, inline document preview cards within the main chat feed to view source context fragments instantly.
* [ ] Design an expandable, interactive side drawer specifically for inspecting complex code files and data outputs.

### Milestone 3 — Evaluation Frameworks (Eval Layer)
* **Goal:** Quantify retrieval and reasoning accuracy through automated benchmarking.
* [ ] Assemble a permanent regression-testing set of 50 multi-step questions with known source material groundings.
* [ ] Create an automated evaluation worker script that runs on backend modifications to score retrieval accuracy.
* [ ] Monitor and profile context-window usage to balance cost, performance, and memory retention when using cloud models.

### Milestone 4 — Enterprise Extensions (Multi-User & Storage)
* **Goal:** Transition the platform from a localized single-user tool to a shared work group environment.
* [ ] Update session management to support permanent relational data storage (PostgreSQL/SQLite) for user conversations.
* [ ] Build a complete document management UI layout allowing users to review, tag, search, and delete individual indexed items.
* [ ] Implement secure user authentication layers and role-based workspace partitioning.

---

## 📝 Architectural Decision Records (ADRs)

### ADR 001 — Single Frontend Assistant Canvas
* **Decision:** Nexa remains the single frontend chat assistant interface. Granular settings are hidden behind a clean dual-pill option bar.
* **Rationale:** Minimizes user fatigue. Complexity is shifted entirely onto the backend orchestration layer.

### ADR 002 — Fully Centralized Server-Side Orchestration
* **Decision:** All intent analysis, safety verification, and model routing parameters live natively on the backend.
* **Rationale:** Allows development teams to alter routing paths or adjust prompting frameworks without requiring frontend client updates.

### ADR 003 — Local Compute Priority & Compute Budgets
* **Decision:** Route standard conversational text to local Ollama nodes by default. Bypass LangGraph evaluation for basic greetings.
* **Rationale:** Keeps operating costs lean and ensures the workspace remains highly performant during standard coding tasks (saving ~1.4s per basic query).

### ADR 004 — Non-Rigid Type-Safe Schema Definition
* **Decision:** Models, capabilities, and options are loaded from a type-safe `settings` instance powered by `config.yaml` and broadcast down via the API.
* **Rationale:** Eliminates front-end/back-end configuration sync errors and makes it easy to add or upgrade model configurations.

### ADR 005 — Unified Flat Project Structure
* **Decision:** Consolidate application folders directly under the workspace root, abandoning nested directories.
* **Rationale:** Enforces uniform look-up boundaries for python dependencies, simplifies the script orchestrator (`run_nexusmind.sh`), and aligns perfectly with modern package management toolsets like `uv`.

### ADR 006 — Memory-Isolated Telemetry Ledger
* **Decision:** `TraceTracker` must apply `copy.deepcopy()` to all incoming state parameters to sever Python memory references.
* **Rationale:** LangGraph passes state channels as shallow references. Allowing internal logging loops to iterate over and mutate these arrays simultaneously causes catastrophic silent thread-locking loops.

---

## 4. Technical Interview Q&A Deep-Dive

### Q1: Why did you choose LangGraph instead of traditional sequential agent orchestration frameworks?
**Answer:** Sequential chains follow a rigid, linear path that breaks down when handling real-world user interactions. LangGraph models the system as a stateful agent network using a directed graph layout. This design lets us build cyclical execution flows, error-correction loops, and conditional state routing paths (like our Heuristic Fast-Path bypass).

### Q2: Detail how your input guardrails engine prevents performance degradation.
**Answer:** To keep the validation boundary highly responsive, the `NexusGuardrails` engine relies on a dual-tier heuristic design:
1. **Sub-millisecond Pre-compiled Regex:** Adversarial attacks, prompt injections, and PII extractions (Token Masking) are caught immediately using pre-compiled regular expressions.
2. **Deterministic Keyword Matching:** Instead of processing incoming text through high-overhead semantic similarity classifiers, domain alignment checks use a fast keyword lookup array.

### Q3: How did you fix the silent infinite loop/deadlock inside the LangGraph `governance_node`?
**Answer:** The deadlock was caused by a memory-reference loop in our `TraceTracker` class. LangGraph inherently passes a shallow copy of the state dictionary between nodes. Inside the tracker, when `log_external_sequence` iterated over the sequence logs while simultaneously appending to them in the same memory space, it created an instantaneous Ouroboros `for`-loop that locked the Uvicorn thread. We resolved this by casting the target iteration sequence to a static list and applying `copy.deepcopy()` to the initial state construction, completely severing the shared memory link.

### Q4: Explain the `AttributeError: 'ProviderConfig' object has no attribute 'get'` error you encountered.
**Answer:** This error was caused by treating Pydantic v2 validated objects as raw dictionaries. In our settings architecture, configurations map into strongly typed objects. Attempting to chain `.get()` methods failed because Pydantic objects require dot-notation attribute access (e.g., `gemini_provider.model`). We resolved this by updating the routing logic to query the Pydantic properties directly.

### Q5: What is the significance of the `HNSW` indexing algorithm used inside your ChromaDB vector store?
**Answer:** Traditional relational databases index data by sorting records linearly, which scales poorly for high-dimensional semantic vectors. ChromaDB uses **Hierarchical Navigable Small World (HNSW)** multi-layered proximity graphs. The top layers feature wide, sparse connections for fast data navigation, and the bottom layers contain dense clusters for precision tracking. This allows retrieval loops to operate at logarithmic time scaling ($O(\log N)$), delivering instant semantic retrieval across heavy PDF collections.