# Unit 2.2 — Practice Quiz 1 (LlamaIndex Components + RAG Pipeline)

> Self-graded practice for the first half of the LlamaIndex unit.
> Covers: LlamaHub, install pattern, `SimpleDirectoryReader`, `IngestionPipeline`, `SentenceSplitter`, HF embeddings, `ChromaVectorStore`, `VectorStoreIndex`, query engines, response synthesizers, evaluators, observability.
> Format: 15 multiple-choice questions. Answers + explanations at the bottom.

---

### Q1. The four pillars of LlamaIndex emphasized in the course are:

A. Models, Prompts, Pipelines, Spaces.
B. Components, Tools, Agents, Workflows.
C. Loaders, Retrievers, Rerankers, Generators.
D. Chains, Memories, Agents, Tools.

---

### Q2. The canonical LlamaHub install pattern is:

A. `pip install llamahub`
B. `pip install llama-index-{component-type}-{framework-name}` (e.g. `pip install llama-index-llms-huggingface-api llama-index-embeddings-huggingface`).
C. `conda install -c llamaindex`
D. Single-package `pip install llama-index` covers everything.

---

### Q3. Within LlamaIndex's 5-stage RAG model, **indexing** specifically means:

A. Tokenizing the input.
B. Creating a data structure (usually vector embeddings, sometimes metadata) over your loaded data so it can be queried efficiently.
C. Calling the LLM.
D. Storing chat history.

---

### Q4. `SimpleDirectoryReader(input_dir="...")` returns:

A. Raw bytes.
B. A list of `Document` objects (one per file or per logical unit), ready to feed into an `IngestionPipeline`.
C. A pandas DataFrame.
D. A `Node` tree.

---

### Q5. An `IngestionPipeline(transformations=[SentenceSplitter(...), HuggingFaceEmbedding(...)])` produces:

A. Tokenized text only.
B. A list of `Node` objects — chunks of text + their vector embeddings, with back-references to source `Document`s.
C. A vector store on disk.
D. An LLM response.

---

### Q6. Why does the course recommend keeping the **same embedding model** for both ingestion and query?

A. Cost.
B. Embeddings live in a vector space tied to the model; mixing models means query vectors and document vectors are in different spaces and similarity scores stop meaning anything.
C. Licensing.
D. Speed.

---

### Q7. To go from `vector_store` + `embed_model` to a queryable index, you call:

A. `VectorStoreIndex(vector_store)`
B. `VectorStoreIndex.from_vector_store(vector_store, embed_model=embed_model)`
C. `index = vector_store.index()`
D. `LlamaIndex.build(vector_store)`

---

### Q8. The three common interfaces produced from an index are:

A. `as_loader`, `as_indexer`, `as_storer`
B. `as_retriever` (raw `NodeWithScore`s), `as_query_engine` (one-shot Q&A returning a response), `as_chat_engine` (multi-turn conversation with memory).
C. `as_pipeline`, `as_workflow`, `as_agent`
D. `as_streamer`, `as_async`, `as_batch`

---

### Q9. The default `response_mode` on `as_query_engine(...)` and what it does:

A. `refine` — one LLM call per chunk, sequentially refining.
B. `compact` — concatenate retrieved chunks before sending (default), minimizing LLM calls.
C. `tree_summarize` — recursive tree of LLM calls over chunks.
D. `extract` — only return spans.

---

### Q10. `FaithfulnessEvaluator` checks:

A. The relevance of the answer to the question.
B. Whether the generated answer is **supported by the retrieved context** (a hallucination check).
C. The latency of the response.
D. Whether the LLM was used at all.

---

### Q11. Which evaluator pair specifically targets the **relevance** and **correctness** axes (separately from faithfulness)?

A. `LatencyEvaluator`, `CostEvaluator`.
B. `AnswerRelevancyEvaluator` (relevance to the question), `CorrectnessEvaluator` (correctness vs ground truth).
C. `EmbeddingDriftEvaluator`, `RetrievalEvaluator`.
D. There's only one evaluator.

---

### Q12. The observability path the unit demonstrates uses:

A. Prometheus.
B. LlamaTrace / Arize Phoenix via `set_global_handler("arize_phoenix", endpoint="...")` and the `OTEL_EXPORTER_OTLP_HEADERS` env var.
C. Splunk.
D. CloudWatch.

---

### Q13. The course says LlamaIndex agents are **`async` by default**. What does that mean in practice?

A. They can't run on CPU.
B. You call them with `await agent.run(...)` (and Python's `asyncio`). In notebooks Jupyter handles the event loop; otherwise you need `asyncio.run(...)`.
C. They can't be tested.
D. They only work in Rust.

---

### Q14. Which is the **easiest** way to add memory across calls to an agent in LlamaIndex?

A. Store transcripts manually in a database.
B. Construct a `Context(agent)` once and pass it in: `await agent.run(msg, ctx=ctx)` — the context carries state and chat history across calls.
C. Re-instantiate the agent each time with full transcript.
D. Memory isn't supported.

---

### Q15. Which is the **best** one-liner contrast between a smolagents `CodeAgent` and a LlamaIndex agent?

A. They're identical.
B. smolagents' CodeAgent emits Python code as actions and runs inside a sandboxed Python executor; LlamaIndex agents emit function/tool calls (via either the LLM's native function-calling API or a ReAct text loop) and run inside an `AgentWorkflow` event-driven runtime.
C. LlamaIndex doesn't have agents.
D. smolagents requires LangChain.

---

## Answer Key + Explanations

| Q | Ans | Why |
|---|-----|-----|
| 1 | **B** | Verbatim from "Introduction to LlamaIndex": Components, Tools, Agents, Workflows. |
| 2 | **B** | `pip install llama-index-{component-type}-{framework-name}` is the canonical pattern; e.g. `llama-index-llms-huggingface-api`. |
| 3 | **B** | Indexing = building a queryable data structure (usually vectors, sometimes metadata-only) over loaded data. |
| 4 | **B** | `SimpleDirectoryReader.load_data()` → list of `Document`. |
| 5 | **B** | The pipeline emits chunked, embedded `Node`s with back-refs. If you attach a `vector_store=...` it also persists them. |
| 6 | **B** | Mixing embeddings is the #1 silent-failure mode in RAG; the unit highlights this explicitly. |
| 7 | **B** | `VectorStoreIndex.from_vector_store(vector_store, embed_model=embed_model)` is the recommended factory. |
| 8 | **B** | `as_retriever` / `as_query_engine` / `as_chat_engine` are the three interfaces enumerated in the unit. |
| 9 | **B** | `compact` is the default; concatenates chunks → minimal LLM calls. (`refine` and `tree_summarize` are the alternatives.) |
| 10 | **B** | Faithfulness = answer grounded in retrieved context, the standard hallucination check. |
| 11 | **B** | The unit lists `AnswerRelevancyEvaluator` and `CorrectnessEvaluator` separately from `FaithfulnessEvaluator`. |
| 12 | **B** | LlamaTrace (a hosted Arize Phoenix) is what the unit wires up. Bonus 2 generalizes this. |
| 13 | **B** | `await agent.run(...)` is the API. Jupyter handles the loop automatically. |
| 14 | **B** | `Context(agent)` is the documented memory mechanism — re-use it across calls. |
| 15 | **B** | smolagents code-first + sandbox; LlamaIndex workflow / function-calling-first + async event-driven runtime. |

**Pass mark:** ≥ 12 / 15. If you missed Q5, Q6, or Q9, re-read "Creating a RAG pipeline using components".
