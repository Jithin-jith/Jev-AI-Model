# Jev: Complete Zero-to-Hero Learning Curriculum
### Master TypeSafe AI's "System One" Decision Intelligence Model

Welcome to the definitive guide and hands-on repository for **Jev**, the groundbreaking "System One" model created by **TypeSafe AI** (founded by former OpenAI RLHF co-creator Diogo Almeida, Erik Gafni, and Sasha Sheng; released in early access September 15, 2026).

---

## ⚡ The Paradigm Shift: Why Jev is NOT an LLM

For years, GenAI developers used Large Language Models (LLMs) like GPT-4, Claude, or LLaMA for **everything**—including simple tasks like:
- *"Is this support ticket urgent?"* (Boolean)
- *"Categorize this document into 1 of 5 departments."* (Classification)
- *"Rate the user's frustration on a 1–5 scale."* (Scoring)
- *"Does this prompt contain malicious injection?"* (Guardrails)

### The Problem With Using LLMs for Decisions:
1. **Autoregressive Waste:** LLMs generate text token by token. Asking an LLM for a JSON category takes 1,000–3,000ms and generates tokens you discard.
2. **Parsing & Hallucination Failures:** LLMs hallucinate keys, break JSON formatting, or add conversational preamble ("Sure, here is your JSON: ...").
3. **Prohibitive Cost:** Processing millions of classification events with frontier LLMs costs thousands of dollars monthly.
4. **Poor Probability Calibration:** LLM log-probabilities are notoriously poorly calibrated for confidence gating.

### The Jev Solution: Daniel Kahneman’s "Dual-Process Theory" in AI
In *Thinking, Fast and Slow*, Daniel Kahneman defines two modes of thought:
- **System 1:** Fast, intuitive, automatic, low-effort, immediate pattern recognition.
- **System 2:** Slow, deliberate, analytical, generative, heavy reasoning.

```
┌────────────────────────────────────────────────────────────────────────┐
│                        MODERN DUAL-SYSTEM AI STACK                     │
├────────────────────────────────────────────────────────────────────────┤
│                                                                        │
│   Incoming Request / Event / Text                                      │
│                │                                                       │
│                ▼                                                       │
│   ┌─────────────────────────────┐                                      │
│   │    SYSTEM 1: JEV            │  ◄── 70 - 500 ms Latency             │
│   │    (TypeSafe AI)            │  ◄── $0.042 / 1M Input Tokens        │
│   │    • Parallel Forward Pass  │  ◄── Free Output Tokens              │
│   │    • Non-Autoregressive     │  ◄── Zero JSON Hallucinations        │
│   │    • Calibrated Confidence  │  ◄── Choice, Score, Noul             │
│   └──────────────┬──────────────┘                                      │
│                  │                                                     │
│        Confidence Gating Check                                         │
│       ┌──────────┴──────────┐                                          │
│       ▼                     ▼                                          │
│  [High Confidence]    [Low Confidence / Deep Reasoning]                │
│  Deterministic Route        │                                          │
│  or Instant Cache Hit       ▼                                          │
│  or Instant Action    ┌─────────────────────────────┐                  │
│                       │   SYSTEM 2: FRONTIER LLM    │                  │
│                       │   (GPT-4o, Claude 3.7,      │                  │
│                       │    Gemini 2.5 Pro)          │                  │
│                       │   • Deep generation         │                  │
│                       │   • Multi-step synthesis    │                  │
│                       │   • Complex code writing    │                  │
│                       └─────────────────────────────┘                  │
└────────────────────────────────────────────────────────────────────────┘
```

**Jev is the world's first purpose-built System 1 AI model.** It does not generate free prose. Instead, it takes a state and schema-defined questions, evaluating them simultaneously in a **single non-autoregressive forward pass** with rigorous **Reinforcement Learning for Calibrated Decisions (RLCD)**.

---

## 📊 Jev at a Glance

| Feature | Standard LLM (GPT-4o / Claude 3.5 / Gemini) | Jev (TypeSafe AI) |
| :--- | :--- | :--- |
| **Model Type** | Autoregressive Generative Text Model | Non-Autoregressive System One Decision Model |
| **Output** | Unstructured text / Prose / JSON strings | **Typed native primitives** (`Choice`, `Score`, `Noul`) |
| **Latency** | 800ms – 5,000ms | **70ms – 500ms** (up to 40x–200x faster) |
| **Input Pricing** | ~$2.50 – $15.00 per 1M tokens | **$0.042 per 1M tokens** (~100x–400x cheaper) |
| **Output Pricing** | ~$10.00 – $75.00 per 1M tokens | **$0.00 (FREE)** |
| **JSON Parse Failures**| Common (requires Pydantic/BAML retry loops) | **0% (Native Typed Engine)** |
| **Confidence Scoring** | Poorly calibrated softmax heuristics | **Natively calibrated via RLCD** |
| **Evaluation Mode** | Sequential token prediction | **Massively parallel forward-pass questions** |

---

## 🛠️ Virtual Environment Setup & Requirements

A root [requirements.txt](file:///f:/Projects/Jev/requirements.txt) is provided. Set up your virtual environment with:

```bash
# 1. Create a virtual environment
python -m venv .venv

# 2. Activate the virtual environment
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# Linux / macOS:
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt
```

---

## 🧪 Hands-On Test Files in Every Module

Each module includes a dedicated, ready-to-run `.py` test script. All scripts automatically detect your environment—connecting to the live `typesafe-sdk` if installed and authenticated, or seamlessly falling back to the built-in offline simulator so you can learn without an API key!

| Module | Hands-On Test Script | What It Tests |
| :--- | :--- | :--- |
| **01. Fundamentals** | [`01-fundamentals/test_fundamentals.py`](file:///f:/Projects/Jev/01-fundamentals/test_fundamentals.py) | `Choice`, `Score`, `Noul`, candidate distributions, expected values. |
| **02. Quickstart & SDKs** | [`02-quickstart-and-sdks/test_quickstart.py`](file:///f:/Projects/Jev/02-quickstart-and-sdks/test_quickstart.py) | Sync/async execution, SLA timeouts, connection pooling. |
| **03. Intermediate Patterns** | [`03-intermediate-patterns/test_intermediate_patterns.py`](file:///f:/Projects/Jev/03-intermediate-patterns/test_intermediate_patterns.py) | 3-tier confidence gating, sub-100ms security shield, 4-factor contract analysis. |
| **04. Advanced Architectures**| [`04-advanced-architectures/test_advanced_architectures.py`](file:///f:/Projects/Jev/04-advanced-architectures/test_advanced_architectures.py) | Dual-System Jev+LLM routing, agent tool dispatcher, Brier Score & ECE math. |
| **05. Project 1: Triage** | [`05-hands-on-projects/project1-support-triage/triage_engine.py`](file:///f:/Projects/Jev/05-hands-on-projects/project1-support-triage/triage_engine.py) | Automated customer ticket triage with SLA routing. |
| **05. Project 2: Guardrails**| [`05-hands-on-projects/project2-realtime-guardrail/guardrail_proxy.py`](file:///f:/Projects/Jev/05-hands-on-projects/project2-realtime-guardrail/guardrail_proxy.py) | Prompt injection & DAN jailbreak interception proxy. |
| **05. Project 3: Agent Orchestrator**| [`05-hands-on-projects/project3-agent-orchestrator/dual_system_orchestrator.py`](file:///f:/Projects/Jev/05-hands-on-projects/project3-agent-orchestrator/dual_system_orchestrator.py) | Full autonomous agent dispatching & LLM synthesis. |
| **06. Reference & Benchmarks**| [`06-reference-cheatsheet/test_benchmarks.py`](file:///f:/Projects/Jev/06-reference-cheatsheet/test_benchmarks.py) | Latency percentiles (p50/p95) and multi-model cost calculator. |

---

## 🗺️ Curriculum Structure

This repository is organized into progressive learning modules designed for software engineers, GenAI practitioners, and enterprise architects:

### 📁 [Module 1: Fundamentals](./01-fundamentals/)
- **[01. Introduction to System One AI](./01-fundamentals/01_introduction_to_system_one_ai.md)**: Theoretical foundations, Kahneman's cognitive framework, and why generative models fail at software decision boundaries.
- **[02. Core Decision Primitives](./01-fundamentals/02_core_primitives.md)**: Deep dive into `Choice`, `Score`, and `Noul` with criteria structuring and probabilities.
- **[03. Architecture & Mechanics](./01-fundamentals/03_architecture_and_mechanics.md)**: Non-autoregressive forward pass, RLCD calibration, token pricing mechanics, and latency profiling.

### 📁 [Module 2: Quickstart & SDKs](./02-quickstart-and-sdks/)
- **[01. Python SDK Quickstart (`typesafe-sdk`)](./02-quickstart-and-sdks/01_python_quickstart.md)**: Environment setup, parallel queries, strongly-typed responses.
- **[02. TypeScript/JavaScript SDK Quickstart (`@typesafe-ai/sdk`)](./02-quickstart-and-sdks/02_typescript_quickstart.md)**: Compile-time type inference, Node 20+, async handling.
- **[03. REST API Specification](./02-quickstart-and-sdks/03_rest_api_specification.md)**: Direct `POST https://api.typesafe.ai/v1/systemone` raw HTTP schema, curl requests, and payload definitions.

### 📁 [Module 3: Intermediate Patterns](./03-intermediate-patterns/)
- **[01. Confidence Gating & Dynamic Routing](./03-intermediate-patterns/01_confidence_gating_and_routing.md)**: Gating automated business workflows using calibrated confidence thresholds.
- **[02. Guardrails & Real-Time Moderation](./03-intermediate-patterns/02_guardrails_and_moderation.md)**: Sub-100ms prompt injection detection, PII detection, and policy compliance.
- **[03. Batch & Multi-Dimensional Questioning](./03-intermediate-patterns/03_batch_and_parallel_evaluations.md)**: Evaluating 20+ questions across a single state in one sub-second call.

### 📁 [Module 4: Advanced Architectures](./04-advanced-architectures/)
- **[01. Hybrid System 1 + System 2 Pipelines](./04-advanced-architectures/01_hybrid_system1_system2_pipeline.md)**: Constructing enterprise production pipelines combining Jev with frontier reasoning models.
- **[02. Agentic Workflows & Tool Selection](./04-advanced-architectures/02_agentic_workflows_and_tool_selection.md)**: Eliminating LLM tool-calling latency using Jev as a deterministic dispatcher.
- **[03. Calibration Evals, Brier Score & Observability](./04-advanced-architectures/03_calibration_evals_and_monitoring.md)**: Measuring Expected Calibration Error (ECE), reliability diagrams, and tracing with Langfuse/Bifrost.

### 📁 [Module 5: Hands-On Projects](./05-hands-on-projects/)
- **[Project 1: Enterprise Support Ticket Triage Engine](./05-hands-on-projects/project1-support-triage/)**: High-throughput automated categorization, sentiment/frustration scoring, and urgency routing.
- **[Project 2: Real-Time Security Guardrail Proxy](./05-hands-on-projects/project2-realtime-guardrail/)**: Ultra-fast security interceptor for LLM chats to stop jailbreaks and data leaks.
- **[Project 3: Dual-System Agent Orchestrator](./05-hands-on-projects/project3-agent-orchestrator/)**: Autonomous agent workflow with Jev System 1 fast path and LLM System 2 fallback.

### 📁 [Module 6: Reference & Cheatsheets](./06-reference-cheatsheet/)
- **[Jev Syntax & API Cheatsheet](./06-reference-cheatsheet/jev_cheatsheet.md)**
- **[Pricing, Latency & Model Benchmarks](./06-reference-cheatsheet/pricing_and_benchmarks.md)**

### 📁 [Executable Code Examples](./examples/)
- Run code directly using Python:
  - `examples/01_basic_primitives.py`
  - `examples/02_dual_system_pipeline.py`
  - `examples/03_guardrail_moderator.py`
  - All examples run live against TypeSafe AI using your API key configured in `.env`!

---

## 🚀 60-Second Quickstart (Python)

```bash
pip install typesafe-sdk
export TYPESAFE_API_KEY="your-api-key"
```

```python
from typesafe_sdk import TypeSafeClient, Choice, Score, Noul

client = TypeSafeClient()

response = client.system_one(
    state="The database replica in us-east-1 is throwing connection timeouts since 03:00 UTC. Customers are affected.",
    questions={
        "severity": Choice(
            instructions="Determine incident severity level",
            criteria={
                "SEV_1": "Critical outage affecting active customer transactions",
                "SEV_2": "Major degradation with partial workaround",
                "SEV_3": "Minor issue or cosmetic bug"
            }
        ),
        "impact_score": Score(
            instructions="Rate the business impact from 1 (lowest) to 5 (catastrophic)",
            criteria=[
                "No business impact",
                "Isolated customer complaint",
                "Moderate latency or degraded performance",
                "Significant customer-facing errors",
                "Complete service downtime"
            ]
        ),
        "requires_oncall_page": Noul(
            instructions="Does this incident require immediately waking up the on-call engineer?"
        )
    }
)

# Native typed outputs - zero JSON parsing!
print(response.answers["severity"].choice)            # "SEV_1"
print(response.answers["severity"].confidence)        # 0.982
print(response.answers["impact_score"].score)         # 4
print(response.answers["requires_oncall_page"].noul)  # True (prob: 0.96)
```

---

## 🛠️ Repository Navigation
Clone or browse the directories above to start your journey from basic primitives to production dual-system AI architectures.
