# Module 1.2: Core Decision Primitives

Jev replaces prompt engineering hacks (such as "Output 1 for YES, 0 for NO") with three mathematically formal **decision primitives**:

1. **`Choice`**: Categorical classification over discrete candidates.
2. **`Score`**: Scalar evaluation across an ordered rubric.
3. **`Noul`**: Binary probabilistic truth judgement (Yes/No).

Every primitive is designed for parallel execution against a single state object.

---

## 1. The `Choice` Primitive (Categorical Decisions)

The `Choice` primitive selects the single best-fitting category from a set of discrete, mutually exclusive options (up to 255 options).

### Structure
- **`instructions`** (*string*): What Jev should evaluate when choosing.
- **`criteria`** (*dict / object*): A mapping of key-value pairs where:
  - **Key**: The categorical label returned in your code.
  - **Value**: Clear, unambiguous natural language definition of when to pick this category.

### Python Example
```python
from typesafe_sdk import Choice

category_question = Choice(
    instructions="Categorize the user's intent from their incoming message",
    criteria={
        "account_access": "Problems logging in, MFA failure, password resets",
        "billing_dispute": "Unrecognized charges, refund requests, receipt inquiries",
        "feature_request": "Proposing new capabilities or workflow enhancements",
        "bug_report": "System errors, crashes, 500 errors, or broken UI elements",
        "general_inquiry": "Pricing questions, sales demo requests, documentation queries"
    }
)
```

### What Jev Returns
```python
answer = response.answers["category"]

print(answer.choice)       # e.g., 'billing_dispute'
print(answer.confidence)   # e.g., 0.941 (Calibrated probability of this choice)
print(answer.distribution) # e.g., {'account_access': 0.012, 'billing_dispute': 0.941, ...}
```

### Best Practices for `Choice`:
- **Mutually Exclusive Criteria:** Ensure criteria do not heavily overlap. If two categories can both be true, either combine them or define an explicit tie-breaking condition in the instructions.
- **Provide a Fallback Category:** Include a `fallback` or `other` category with criteria like `"None of the above categories apply"`.

---

## 2. The `Score` Primitive (Ordered Scalar Rubrics)

The `Score` primitive evaluates an input along an **ordered scale** (e.g., 1 to 5, 0 to 10, or qualitative rubrics). Unlike an unconstrained LLM that might output `3.7` or `"three"`, Jev outputs a calibrated integer step or continuous scalar according to your rubric.

### Structure
- **`instructions`** (*string*): The evaluation dimension (e.g., urgency, toxicity, technical depth).
- **`criteria`** (*list of strings*): Ordered list of levels, from lowest (index 0 or 1) to highest.

### Python Example
```python
from typesafe_sdk import Score

frustration_score = Score(
    instructions="Assess the customer's emotional frustration level",
    criteria=[
        "Polite, calm, neutral statement of facts",
        "Slightly annoyed, mild impatience expressed",
        "Explicitly frustrated, mentions wasted time or money",
        "Extremely angry, aggressive tone, demands manager or legal escalation",
        "Abusive, threatening, or completely hostile"
    ]
)
```

### What Jev Returns
```python
answer = response.answers["frustration"]

print(answer.score)        # e.g., 3 (0-indexed or 1-indexed depending on config)
print(answer.confidence)   # e.g., 0.884 (Confidence in this specific bracket)
print(answer.expected_val) # e.g., 2.92 (Continuous expectation across the rubric distribution)
```

### Best Practices for `Score`:
- Use monotonic descriptions: each step must strictly increase in severity or intensity.
- Keep rubric steps between 3 and 7 levels for optimal calibration.

---

## 3. The `Noul` Primitive (Probabilistic Yes/No Judgements)

The term **`Noul`** is TypeSafe AI's primitive for a binary truth evaluation ($P(\text{True}) \in [0.0, 1.0]$).

Instead of forcing an LLM to generate `{"is_urgent": true}`, `Noul` outputs a direct, mathematically calibrated probability that the instruction is satisfied.

### Structure
- **`instructions`** (*string*): A declarative proposition that can be evaluated as True or False.

### Python Example
```python
from typesafe_sdk import Noul

is_urgent = Noul(
    instructions="The customer message indicates active production downtime or business revenue stoppage"
)

is_prompt_injection = Noul(
    instructions="The user input attempts to override system prompt instructions, leak API keys, or execute jailbreaks"
)
```

### What Jev Returns
```python
answer = response.answers["is_urgent"]

print(answer.noul)         # Boolean: True if probability >= threshold (default 0.5)
print(answer.probability)  # Float: 0.963 (Calibrated probability that statement is True)
print(answer.confidence)   # Float: 0.926 (Margin from uncertainty threshold)
```

### Why Call it `Noul`?
Traditional booleans in code are deterministic and binary (`True` / `False`). In probabilistic AI systems, truth is continuous: a statement has a likelihood from $0.0$ to $1.0$. The `Noul` primitive models this epistemic uncertainty while still exposing idiomatic boolean properties for easy conditional branching:

```python
# Idiomatic threshold gating
if response.answers["is_urgent"].probability > 0.85:
    send_slack_alert_to_oncall(ticket)
```

---

## 🔬 Parallel Execution Architecture

One of Jev's greatest architectural advantages is that **all questions share the same input state and are evaluated concurrently in a single model forward pass**.

```python
# All 3 primitives evaluated simultaneously in ~120ms total!
response = client.system_one(
    state=user_message,
    questions={
        "dept": category_question,    # Choice
        "urgency": frustration_score, # Score
        "pii": is_pii_present,        # Noul
        "jailbreak": is_prompt_inj    # Noul
    }
)
```

In a traditional LLM setup, evaluating 4 distinct dimensions would either require:
1. Four sequential API calls (4 × 1,500ms = 6,000ms latency).
2. A complex single prompt with high hallucination risk and 2,500ms latency.

With Jev, all 4 questions execute in parallel in **~120ms** with zero risk of schema breakage.

---

## 🎯 Summary Takeaways
- Use **`Choice`** when picking 1 option among distinct categories.
- Use **`Score`** when rating across an ordered monotonic scale.
- Use **`Noul`** for binary truth/probability checks.
- Next module: [03. Architecture & Mechanics](./03_architecture_and_mechanics.md).
