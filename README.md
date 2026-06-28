# NexusMind 🧠

Zero-Friction Technical Exploration, Grounded RAG, and Deep Analytics.

NexusMind is an enterprise-grade, high-density AI engineering assistant platform. It leverages a high-performance FastAPI gateway alongside a compiled, single-tiered native LangGraph Orchestration Network to route conversational prompts dynamically based on semantic complexity. By leveraging a centralized, custom-engineered user interface mimicking premium modern workspaces (like Gemini), the interface strips out bloat and wraps messaging rows directly in zero-overhead HTML flex arrays. System controls are compressed into dual top-of-chatbox micro utilities managing the active conversation pipeline mode (🧠 Auto Orchestrate, ✨ Nexa Chat, 🔬 Deep Research) and the compute infrastructure runtime selector (🤖 Auto Model, LOCAL, CLOUD) natively anchored inside a single compact boundary footprint.

------------------------------

## 🏗️ Technical System Architecture
NexusMind is engineered as a decoupled, multi-tier runtime system. The interaction between the responsive, avatar-free Streamlit custom presentation canvas, the FastAPI communication routing layer, the compiled LangGraph execution topologies, and the underlying multi-provider model gateways is structured as a decoupled multi-tier architecture:

```mermaid
graph TD
    %% Styling Configuration Profiles
    classDef ui fill:#1E1B4B,stroke:#6366F1,stroke-width:2px,color:#F8FAFC;
    classDef api fill:#0F172A,stroke:#38BDF8,stroke-width:1.5px,color:#F1F5F9;
    classDef graphCore fill:#312E81,stroke:#818CF8,stroke-width:1px,color:#E2E8F0;
    classDef infra fill:#064E3B,stroke:#34D399,stroke-width:2px,color:#ECFDF5;

    %% Presentation Layer
    subgraph Streamlit_Frontend [Streamlit Presentation Workspace :8501]
        UI[Canvas Overrides: inject_minimal_overrides]
        Bubble[Custom DOM Renderer: render_message_bubble]
        Selectors[Modular Utilities: Mode & Model selectbox]
    end
    class UI,Bubble,Selectors ui;

    %% Communication Gateway Layer
    subgraph FastAPI_Backend [FastAPI Application Gateway :8001]
        Router[API Endpoint Route: /api/chat]
        Schemas[Data Contracts Validation: schemas.py]
    end
    class Router,Schemas api;

    %% Orchestration Graph Layer
    subgraph LangGraph_Engine [Core Graph State Machine Grid]
        CoreGraph[Master Orchestrator: core_graph.py]
        GovNode[Edge Interceptor Node: governance_node]
        RouteNode[Intent Classifier Node: router_node]
        FastNode[Fast Local Path Node: fast_conversational_node]
        
        subgraph SubAgent_Network [Independent Research Subgraph]
            ResearchGraph[Research Topology: research_graph.py]
            GatherNode[Data Discovery Node: gather_sources_node]
            SynthNode[Citation Synthesizer Node: synthesize_research_node]
        end
    end
    class CoreGraph,GovNode,RouteNode,FastNode,ResearchGraph,GatherNode,SynthNode graphCore;

    %% Underpinning Infrastructure Layer
    subgraph Compute_And_Storage [Inference Infrastructure & Context Data Space]
        OllamaCompletions[Local Ollama: qwen2.5-coder:7b :11434]
        ChromaDB[Docker Desktop Sandbox: ChromaDB Vector Space :8000]
        WebScrape[Async Scraper Subsystem: trafilatura engine]
        GeminiCloud[Cloud Edge Cloud API: gemini-2.5-flash]
    end
    class OllamaCompletions,ChromaDB,WebScrape,GeminiCloud infra;

    %% Data Pipeline Interaction Lines
    UI -->|1. Loop Custom Component Matrix| Bubble
    Selectors -->|2. Inject Global Config States| Router
    Router -->|3. Initialize GlobalState & .astream_events| CoreGraph
    
    CoreGraph --> GovNode
    GovNode -->|4. Guardrail & PII Masking Pass| RouteNode
    
    %% Conditional Branching Elements
    RouteNode -->|5a. Heuristic Chat Path Routing| FastNode
    RouteNode -->|5b. Research Subgraph Dynamic Path Trigger| ResearchGraph
    
    %% Compute Integrations
    FastNode -->|6. Unified Gateway Factory Model| OllamaCompletions
    
    ResearchGraph --> GatherNode
    GatherNode -->|7a. Vector Proximity Query| ChromaDB
    GatherNode -->|7b. Multiquery Fallback Scrape| WebScrape
    GatherNode --> SynthNode
    SynthNode -->|8. Grounded Context Model Call| GeminiCloud
    
    %% Response Aggregation and Real-Time SSE Wire Output
    FastNode -->|9a. Append Native HTML Streaming Matrix| Router
    SynthNode -->|9b. Append Native HTML Streaming Matrix| Router
    
    Router -->|10. Stream SSE Event Data Packets| UI

```

## 1. Unified Sequence Flow

```mermaid
sequenceDiagram
    autonumber
    actor Dev as Engineer (UI Layout)
    participant ST as Streamlit Frontend (:8501)
    participant API as FastAPI Gateway (:8001)
    participant CG as LangGraph Core Engine
    participant SG as LangGraph Research Subgraph
    participant DB as ChromaDB Container (:8000)
    participant OL as Local Ollama Serve (:11434)
    participant GEM as Cloud Gemini Cloud API

    %% Conversational Loop
    Dev->>ST: Submits Query (Capsule Chat Input)
    ST->>API: HTTP POST /api/chat (ChatRequest SSE Stream)
    API->>CG: astream_events(GlobalState)
    
    critical Edge Governance
        CG->>CG: LLM Structured Output Guardrail Check
        CG->>CG: Mask PII into forward_query string variable
    end

    alt Chat Path Triggered
        CG->>OL: Stream Chat completions chunk token loop
        OL-->>CG: Yields Text Token Delta Chunks
    end
    
    alt Research Path Triggered
        CG->>SG: Cascades State down to Subgraph Node
        
        par Parallel Retrieval Matrix
            SG->>DB: Query Collection Vector Space (Top-K)
            DB-->>SG: Array Text Chunks & Proximity Scores
        and Fallback Web Lookup
            SG->>SG: Run trafilatura Live Page Extraction
        end
        
        SG->>GEM: Dispatches Enriched Grounded Context Prompt
        GEM-->>SG: Yields Citation-Tracked Token Delta Chunks
        SG-->>CG: Merges Subgraph Results into State Array
    end

    CG->>CG: Calculates performance_metrics_ms values
    CG-->>API: Emits trace, metrics, and token SSE frames
    API-->>ST: Streams data packets over event-stream
    ST->>Dev: Appends to native .chat-row without layout shifting

```

## 2. Context Ingestion & Real-Time Background RAG Pipeline

When a technical reference manual or PDF is uploaded via the custom Streamlit sidebar expander console, it immediately triggers a non-blocking asynchronous multi-threaded ingestion workflow:

```mermaid
graph TD
    %% Styling Profile Configurations
    classDef fileStyle fill:#1E293B,stroke:#6366F1,stroke-width:2px,color:#F8FAFC;
    classDef processStyle fill:#312E81,stroke:#4F46E5,stroke-width:1px,color:#E2E8F0;
    classDef infraStyle fill:#064E3B,stroke:#10B981,stroke-width:2px,color:#ECFDF5;

    %% Workflow Structures
    Upload[📁 User Drops Reference PDF in Sidebar UI] -->|HTTP Multipart Binary Stream| Route[⚡ FastAPI Endpoint: /api/rag/upload]
    
    subgraph Local Disk Operations [Host Environment OS]
        Route --> Write[💾 Write Binary Chunk stream to disk]
        Write --> StorageDir[./data/ File Cluster Vault]
        class StorageDir fileStyle;
    end

    Route --> IngestWorker[⚙️ Background Process Thread: run_ingest]
    class IngestWorker processStyle;
    StorageDir --> IngestWorker

    subgraph RAG Compilation Sequence [Atomic Chunker Engine]
        IngestWorker --> HashCheck[🔒 Evict Duplicate Collision doc_hash IDs]
        HashCheck --> TextStream[📝 Extract Raw Text via pdfminer]
        TextStream --> Chunking[✂️ Generate Split text via RecursiveCharacterTextSplitter]
    end
    class HashCheck,TextStream,Chunking processStyle;

    subgraph Asynchronous Vector Pipeline [Ollama Compute Cluster]
        Chunking --> EmbedAPI[🚀 Local LangChain OllamaEmbeddings Client]
        EmbedAPI --> EmbedMerge[🧬 Bind document chunks & metadata maps]
    end
    class EmbedAPI,EmbedMerge processStyle;
    
    subgraph Persistent Storage Database [Docker Desktop Sandbox]
        EmbedMerge --> Chroma[🗄️ ChromaDB Collection Server Container :8000]
        class Chroma infraStyle;
    end

    Chroma --> Log[✅ Log standard terminal confirmation metrics]

```

---

## 🚀 Key Architectural Pillars

* **Avatar-Free Clean HTML Messaging DOM** — Circumvents the structural alignment constraints, ghost margins, and wide layout component stretching seen in typical Streamlit deployments by shifting rendering tasks into a lightweight component wrapper (`render_message_bubble`) using raw HTML flex vectors (`.chat-row`).
* **Centralized Capsule Input Workspace** — Configures your application's focus area into a centered, $720\text{px}$ track capsule. Features subtle border shadows, text wrapping, and an integrated Inter typography stack to align perfectly with high-end, responsive system layout principles.
* **Modular Single-Line Utility Track** — Isolates configuration dropdown models cleanly inside `st.bottom`. Uses a side-by-side flex block configuration that sits tightly aligned above the prompt capsule, with individual selectbox components handling their own layout sizing rules.
* **Direct Graph Compilation Grid** — Replaces fragile external dynamic string loaders with hard-compiled explicit imports (`from app.graphs.research_graph import compiled_research_graph`). Subgraphs run natively inside parent nodes via direct activations.
* **Token-Masking & Local Guardrail Interceptors** — Inspects string payloads at the application boundary through pre-compiled high-performance regular expressions to stop code injection variations while automatically scrubbing PII elements (SSN, credit card strings, IPv4 masks) into secure `[..._REDACTED]` blocks.

---

## 📂 Project Directory Structure

```text
nexusmind/
├── .env                       # Environment context configuration definitions
├── docker-compose.yaml        # Docker Desktop configuration file for ChromaDB services
├── pyproject.toml             # Python system build profiles managed via uv
├── run_ingest.py              # CLI utility hook to run directory-level data scans
├── run_nexusmind.sh           # Master local deployment boot environment shell script
├── tests/                     # Validation suite matrix layer
│   ├── eval_dataset.json      # RAG ground-truth assertion validation metrics
│   ├── run_eval.py            # Automated system scoring computation engine
│   └── test_backend.py        # PyTest integration boundary endpoints assertions
│
├── data/                      # Local PDF data cluster vault configuration mount
│   └── [REFERENCE_MANUALS].pdf
│
├── chroma-data/               # Persistent volume database mount registry
│   └── chroma.sqlite3
│
├── app/                       # FASTAPI LOGICAL ENGINE SERVICES CORE
│   ├── main.py                # System bootstrapper, CORS rules, and root logger
│   ├── settings.py            # Configuration bindings via Pydantic BaseSettings
│   ├── state_models.py        # Shared Pydantic LangGraph state definition models
│   ├── core_graph.py          # Master topology graph, intent routers, and guardrails
│   ├── llm_gateway.py         # Client adapters w/ automated cloud failover fallbacks
│   ├── rag_storage.py         # Text split processing, hashing, and parallel embeddings
│   │
│   ├── api/                   # CONSOLIDATED WEB APPS ENDPOINT REGISTRY
│   │   ├── routes.py          # Pathway handlers, background tasks hooks, uploads
│   │   └── schemas.py         # Request/Response validation models
│   │
│   ├── tools/                 # DATA DISCOVERY ISOLATED OPERATIONS Retrieval Tools
│   │   ├── chroma_search.py   # Vector collection index query utility retriever
│   │   └── web_search.py      # Async live search scraper tool
│   │
│   └── graphs/                # INDEPENDENT COMPILATION AGENT SUBGRAPHS
│       └── research_graph.py  # Source parsing, node loops, deep query synthesis
│
└── frontend/                  # STREAMLIT UI DEVELOPMENT WORKSPACE
    └── streamlit_app.py       # Main presentation interface canvas utilizing the Inter sans font-stack

```

---

## 📈 Execution Profiles Routing Matrix

The orchestrator's router node maps pipeline execution pathways based on the layout configuration parameter context and input intent classification weights:

| Selected Chat Mode | Component Selection Target | Execution Target Pipeline | Active LLM Allocation Model | Dynamic System Prompt Persona |
| --- | --- | --- | --- | --- |
| **🧠 Auto Orchestrate** | Modular `st.selectbox` left-rail utility | Automated router path classification pass | Evaluated dynamically based on query profile | Unified, semantic context system controller prompt |
| **✨ Nexa Chat** | Modular `st.selectbox` left-rail utility | `fast_conversational` node pass | Local Ollama instance via `qwen2.5-coder:7b` | `standard_utility` utility interface prompt |
| **🔬 Deep Research** | Modular `st.selectbox` left-rail utility | Native sub-network `execute_research_subgraph` node | Cloud Google GenAI `gemini-2.5-flash` *(Ollama Fallback)* | Academically anchored `socratic_professor` layout prompt |

---

## 🛠️ Installation & Getting Started

### Prerequisites

* **Python Runtime:** Python 3.12+ managed through **`uv`** package manager tool.
* **Local Inference Engine:** Ollama running locally with the requisite computational models active:

```bash
ollama pull qwen2.5-coder:7b
ollama pull nomic-embed-text

```

* **Virtualization Cluster Container Runtime:** Docker Desktop running locally on the host hardware machine.

### Deployment Operations Boot Sequence

1. **Configure Local Variables Configuration Environment** Generate an active configuration `.env` file directly inside the target project root folder path directory:

```env
# path: .env
APP_ENV=development
LOG_LEVEL=INFO
API_HOST=0.0.0.0
API_PORT=8001
CHROMA_HOST=localhost
CHROMA_PORT=8000
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen2.5-coder:7b
GEMINI_MODEL=gemini-2.5-flash
GEMINI_API_KEY=AIzaSyYourActualCloudGoogleAPIKeyHere
OFFLINE_PDF_DIR=./data

```

2. **Launch the Single-Harness Control Shell Runner Script** The system includes an enterprise shell deployment harness that verifies package locks via `uv`, runs validations against local Docker Desktop infrastructure, builds database mount registers, mounts the background model daemons, launches services, and binds graceful cleanup triggers:

```bash
# Add execution parameters permissions to the script file
chmod +x run_nexusmind.sh

# Fire the active runtime sequence orchestration shell script
./run_nexusmind.sh

```

3. **Verify Host Port Mapping Handshakes**

* **Streamlit UI Layout Platform Display Canvas:** `http://localhost:8501`
* **FastAPI Backend Core Engine REST APIs Swagger docs:** `http://localhost:8001/docs`
* **ChromaDB Docker Sandbox Endpoint:** `http://localhost:8000`

---

## 👥 Maintenance Frame

* **Workspace Owner:** Ranapratap Majee — AI Framework Architecture Specialist.
* **License:** Managed and distributed under standard `MIT License` code parameters.
