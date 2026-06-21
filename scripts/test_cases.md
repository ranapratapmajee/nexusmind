

---

### 🧪 Test Scenario 1: Standard Utility & Casual Greetings

**Goal:** Verify that standard inputs do not trigger false positives or accidental escalations.

* **Test Prompt to Send:** `"hi, clear the context and let's run a baseline test."`
* **Expected Behavior:** * `governance_node` returns `passed=True`.
* `planner_node` detects no learning or escalation keywords.
* `persona_mode` sets to `"standard_utility"`.
* `next_step` points to `"direct_llm"`.


* **What to check in the UI Trace:** Ensure the performance card shows **`STANDARD STREAM`** and your local Ollama model handles the response cleanly.

---

### 🧪 Test Scenario 2: Socratic Persona Trigger

**Goal:** Verify that educational queries successfully shift the agent's behavior into a teaching assistant mode.

* **Test Prompt to Send:** `"Explain the mathematical difference between L1 and L2 regularization."`
* **Expected Behavior:** * `governance_node` passes (matches `"explain"` and `"math"` domains).
* `planner_node` catches the keyword `"explain"`.
* `persona_mode` sets to `"socratic_professor"`.
* `next_step` points to `"direct_llm"`.


* **What to check in the UI Trace:** Verify that the response tone reads like an encouraging professor trying to guide you, and that the telemetry trace flags `mode: socratic_professor | NATIVE`.

---

### 🧪 Test Scenario 3: Autonomous Deep Research Escalation

**Goal:** Verify that high-complexity prompts automatically upgrade the execution tier without requiring the user to change the UI pill selection.

* **Test Prompt to Send:** `"Provide a full breakdown and compare architecture differences between ChromaDB and a standard SQL database cluster."`
* **Expected Behavior:**
* `planner_node` flags the keywords `"full breakdown"` and `"compare architecture"`.
* `current_intent_route` automatically escalates to `"deep_research"`.
* `next_step` routes to `"research_agent"`.
* The engine dynamically hot-swaps the model tier from Ollama to your Gemini endpoint (`gemini-2.5-flash`).


* **What to check in the UI Trace:** Ensure the response details file chunks retrieved from your local document indexing database and the timing trace showcases a multi-second deep analysis span.

---