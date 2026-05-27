# Unit 1 — Practice Quiz 1 (Agents, LLMs, Messages, Tools)

> Self-graded practice for the first ungraded checks in Unit 1.
> Covers: agents/agency spectrum, LLMs + tokenization + chat templates, base vs instruct, tools (definition, description, decorator), MCP.
> Format: 15 multiple-choice questions. Answers + explanations at the bottom.

---

### Q1. Which definition best captures the **HF agents-course** definition of an AI Agent?

A. Any LLM that can answer a user's prompt fluently in natural language.
B. A system that leverages an AI model to interact with its environment to achieve a user-defined objective, combining reasoning, planning, and action.
C. A workflow that calls a single tool deterministically.
D. A neural network with more than 1 billion parameters.

---

### Q2. In the smolagents "agency spectrum", which level corresponds to **`run_function(llm_chosen_tool, llm_chosen_args)`**?

A. Simple processor (☆☆☆)
B. Router (★☆☆)
C. Tool caller (★★☆)
D. Multi-agent (★★★)

---

### Q3. Why are tools necessary for an LLM to "take actions"?

A. They give the LLM access to GPU memory.
B. LLMs natively produce only text; tools are external functions that the agent runtime calls on the LLM's behalf based on what the LLM emits.
C. Tools are required to run the transformer attention mechanism.
D. They are the same thing as the LLM's training data.

---

### Q4. Which statement about LLM tokens is most accurate?

A. One token always equals one English word.
B. LLMs vocabularies typically have hundreds of millions of tokens.
C. LLM tokens are usually sub-word units; e.g. Llama-2 has ~32k tokens vs ~600k English words, and "interest" + "ing" can compose "interesting".
D. Tokens are randomly assigned to words each training run.

---

### Q5. What does an LLM being **autoregressive** mean?

A. It always re-reads the user's first message before answering.
B. The output of one decoding pass is fed back as input for the next, looping until the model emits an EOS token.
C. It auto-corrects its own grammar.
D. It runs simultaneously on multiple GPUs.

---

### Q6. Which is the **EOS token** for SmolLM2?

A. `<|endoftext|>`
B. `<|eot_id|>`
C. `<|im_end|>`
D. `<end_of_turn>`

---

### Q7. Which type of transformer is typically used as the "brain" of an LLM-powered agent?

A. Encoder-only (e.g. BERT)
B. Decoder-only (e.g. Llama, GPT-style)
C. Seq2seq encoder-decoder (e.g. T5)
D. Vision transformer (ViT)

---

### Q8. What is the difference between a **base** model and an **instruct** model?

A. The base model is bigger; the instruct model is smaller.
B. The base model predicts the next token from raw text; the instruct model is fine-tuned to follow instructions/chat — requires the right chat template to behave conversationally.
C. They are the same; "instruct" is just a marketing label.
D. The instruct model has no tokenizer.

---

### Q9. In Hugging Face `transformers`, which function converts a list of `{"role", "content"}` messages into the prompt string the model expects?

A. `model.generate(messages)`
B. `tokenizer.encode(messages)`
C. `tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)`
D. `pipeline("chat", messages)`

---

### Q10. What is a **system message** used for in an agent prompt?

A. Logging telemetry to the server.
B. A persistent role-prefixed instruction that defines how the model should behave; for agents it also typically lists available tools and the action format.
C. The user's first request.
D. Internal Python exceptions.

---

### Q11. A well-designed Tool description for an LLM should minimally include:

A. The Python bytecode of the function.
B. A clear name, a human-readable description of what it does, the input arguments with their types, and the output type.
C. The Git commit hash where the tool was added.
D. Only the function name.

---

### Q12. In the smolagents-style `@tool` decorator pattern, where does the **description text** of the tool come from?

A. From a hand-written XML file.
B. From a JSON schema you must register globally.
C. From the function's name (becomes `name`), the docstring (becomes `description`), and the type hints (become input/output types).
D. From environment variables.

---

### Q13. Which of the following is the **best** rule of thumb for when to add a tool to your agent?

A. Always add as many tools as possible; more tools = better agent.
B. Add a tool when it complements what an LLM cannot do natively or reliably (real-time data, precise math, side effects on a system).
C. Only add tools written in TypeScript.
D. Tools are only useful if the LLM is fine-tuned for them.

---

### Q14. What is the **Model Context Protocol (MCP)**, in one sentence?

A. A protocol for fine-tuning models on your own hardware.
B. An open protocol that standardizes how applications expose tools (and other context) to LLMs, so the same tool definition works across frameworks and providers.
C. A new file format for storing model weights.
D. A licensing agreement for closed-source models.

---

### Q15. Which is true about how a tool is **physically presented** to the LLM at runtime?

A. The agent silently passes the tool's Python source code to the model.
B. The agent injects a **textual description** of each tool (name + description + arguments + output) into the system prompt, and parses the LLM's structured output (JSON or code) when it asks to invoke a tool.
C. The LLM reads the tool's binary directly.
D. Tools are mounted as virtual files in the LLM's file system.

---

## Answer Key + Explanations

| Q | Ans | Why |
|---|-----|-----|
| 1 | **B** | The course defines an Agent as a system that uses an AI model to **reason, plan, and act on its environment** to achieve a user goal. |
| 2 | **C** | The "Tool caller" row in the smolagents agency-spectrum table is exactly `run_function(llm_chosen_tool, llm_chosen_args)`. ☆☆☆ is just text processing; ★☆☆ is yes/no routing; ★★★ is the iterating loop (multi-step or multi-agent). |
| 3 | **B** | LLMs only produce text. The agent runtime parses that text, calls the actual Python (or remote) function, and appends the result as an Observation. |
| 4 | **C** | The course explicitly contrasts Llama-2's ~32k token vocab with ~600k English words and uses the "interest" + "ing" → "interesting" example. |
| 5 | **B** | Autoregressive decoding: each generated token is appended and the whole sequence is re-fed; the loop terminates on the EOS token. |
| 6 | **C** | From the EOS table in the LLMs section: SmolLM2 uses `<|im_end|>`. (`<|endoftext|>` is GPT-4, `<|eot_id|>` is Llama 3, `<end_of_turn>` is Gemma.) |
| 7 | **B** | Decoder-only transformers (Llama, GPT, Gemma, DeepSeek, SmolLM, Mistral, Qwen) are the dominant LLM family used as agent brains. Encoder-only is for embeddings/classification; seq2seq is for translation/summarization. |
| 8 | **B** | Base models are pre-trained on raw text for next-token prediction. Instruct models are fine-tuned on chat/instruction data and need their **specific chat template** to behave correctly. |
| 9 | **C** | `tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)` is the documented way; it bakes in the model's special tokens and the trailing `assistant` opener. |
| 10 | **B** | The system message is persistent role-level guidance; for agents it also typically encodes tool listings, action format, and the Think→Act→Observe contract. |
| 11 | **B** | The 4 ingredients the unit lists: name, description, arguments (with typings), and (optional) outputs (with typings). |
| 12 | **C** | The `@tool` decorator uses Python `inspect` to read the function's name, docstring, signature, and return annotation — that's why type hints + good docstrings matter. |
| 13 | **B** | Tools complement the LLM. Calculators beat LLM arithmetic; web search beats stale training data; an SQL tool beats hallucinated SQL. Adding random tools just bloats the prompt. |
| 14 | **B** | MCP is the open protocol from Anthropic that standardizes tool exposure to LLMs — write the tool once, plug into any MCP-aware framework or client. |
| 15 | **B** | Tool descriptions are injected as text into the system prompt; the LLM emits a structured action (JSON or code), the agent **parses** it, executes, and appends the result. |

**Pass mark:** ≥ 12 / 15. If you missed Q4/Q6 (token trivia) it's fine; if you missed Q1/Q3/Q15 (core agent mechanics), re-read sections "What is an Agent?", "What are Tools?", and "How do we give tools to an LLM?" before moving on.
