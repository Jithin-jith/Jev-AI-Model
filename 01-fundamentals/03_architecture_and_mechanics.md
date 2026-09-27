# Module 1.3: Architecture & Mechanics of Jev

Understanding Jev's internal design helps engineers write better criteria, optimize batching, and architect production systems.

---

## 🏗️ Model Architecture: Non-Autoregressive Transformer

Traditional LLMs (Decoder-Only transformers like GPT-4, LLaMA, Claude) predict the next token given all preceding tokens:

$$P(w_1, w_2, \dots, w_N) = \prod_{i=1}^N P(w_i \mid w_1, \dots, w_{i-1})$$

Because each token depends on the previous token, text generation is strictly **serial**. To generate 50 tokens of JSON, the model must make 50 consecutive forward passes through its neural network.

```
AUTOREGRESSIVE LLM (Serial Generation):
Token 1 ──► Token 2 ──► Token 3 ──► ... ──► Token 50
[------------------ 1,200ms - 3,500ms ------------------]
```

### Jev’s Non-Autoregressive Parallel Forward Pass
Jev uses a specialized transformer architecture that pairs an encoder backbone with dedicated decision heads:

```
JEV (Non-Autoregressive Parallel Forward Pass):
               ┌──► Head 1: Choice (Department)    ──► "billing" (0.97)
State Input ───┼──► Head 2: Score  (Frustration)   ──► 4 (0.89)
               └──► Head 3: Noul   (Is Urgent)     ──► True (0.94)
[---------------------- 70ms - 250ms ---------------------]
```

1. **State Embedding:** The input state (text, context, metadata) is encoded once into dense contextual representations.
2. **Multi-Question Cross-Attention:** Each question definition (instructions + criteria) is projected and cross-attends to the state representations in parallel.
3. **Dedicated Output Projections:**
   - **Choice:** Softmax over the candidate criteria embeddings.
   - **Score:** Ordinal regression / distribution head across the rubric embeddings.
   - **Noul:** Sigmoid probability head calibrated for binary veracity.

---

## 🎯 RLCD: Reinforcement Learning for Calibrated Decisions

In standard LLM training (RLHF/DPO), models are optimized for *human preference*—which often encourages models to sound authoritative, persuasive, or verbose even when uncertain. This destroys probability calibration.

TypeSafe AI pioneered **RLCD (Reinforcement Learning for Calibrated Decisions)**:
- **Calibration Objective:** If Jev reports a confidence score of $0.80$ over 1,000 decisions, exactly $800$ of those decisions must be empirically correct.
- **Strict Scoring Rule Penalties:** Training utilizes proper scoring rules (such as Brier score and Negative Log-Likelihood) combined with adversarial calibration loss functions to eliminate overconfidence and underconfidence.

### Expected Calibration Error (ECE) Comparison:
- **Standard Frontier LLM with Softmax:** $\text{ECE} \approx 0.18 - 0.28$ (Severely uncalibrated; tends to be overly confident).
- **Jev with RLCD:** $\text{ECE} < 0.04$ (Highly calibrated; confidence directly correlates to true probability).

This makes Jev uniquely safe for **automated decision thresholds** in enterprise code:
```python
# With Jev, 0.90 confidence genuinely means a ~90% accuracy rate
if response.answers["compliance_check"].confidence >= 0.90:
    auto_approve_transaction(tx)
else:
    route_to_human_review(tx)
```

---

## 💰 Economic Mechanics & Pricing Breakdown

Jev operates on a radically disruptive pricing model designed for high-throughput software pipelines:

### Pricing Schedule (September 2026):
- **Input Tokens:** **$0.042 per 1,000,000 tokens** ($0.000042 / 1K tokens)
- **Output Tokens:** **$0.00 (Completely FREE)**
- **Question Definitions:** Tokenized as part of input context.

### Real-World Cost Comparison: 1,000,000 Events
Imagine processing 1,000,000 customer messages (average 250 input tokens per message) to classify urgency and category:

| Architecture | Cost per 1M Events | Total Latency per Request | Monthly Bill (10M requests) |
| :--- | :--- | :--- | :--- |
| **GPT-4o (Structured Outputs)** | ~$1,125.00 | ~1,200 ms | **$11,250.00** |
| **Claude 3.5 Haiku** | ~$350.00 | ~750 ms | **$3,500.00** |
| **Self-Hosted Fine-Tuned LLaMA** | ~$400.00 (GPU Cloud) | ~400 ms | **$4,000.00 + DevOps** |
| **Jev (TypeSafe AI)** | **$10.50** | **~110 ms** | **$105.00** |

**Cost Reduction:** **Over 99% cost savings** compared to frontier LLMs, with a **10x reduction in latency**.

---

## ⚡ Latency Profile Breakdown

A typical Jev request executes in **70ms to 350ms**:

```
Client Request Sent
  │   ~20ms (Network TLS / Transit)
  ▼
Edge Gateway / API Router
  │   ~10ms (Auth, Rate Limiting, Schema Validation)
  ▼
Jev Inference Engine (Single Forward Pass)
  │   ~40ms - 80ms (State Tokenization + Attention + Parallel Heads)
  ▼
Response Serialization & Return
  │   ~20ms (Network Return)
  ▼
Total Roundtrip: ~90ms - 130ms (US-East / EU-Central)
```

---

## 🎯 Summary Takeaways
1. Non-autoregressive forward passes eliminate token-by-token sequential latency.
2. RLCD ensures that confidence values represent true mathematical probabilities.
3. Pricing ($0.042/1M input, $0 output) makes AI-driven decisions viable for high-volume backend microservices.
4. Next module: [Module 2.1: Python SDK Quickstart](../02-quickstart-and-sdks/01_python_quickstart.md).
