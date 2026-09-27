# Jev Syntax & API Reference Cheatsheet

A quick-reference lookup for developers building with Jev (TypeSafe AI System One).

---

## 🔑 Authentication

```bash
export TYPESAFE_API_KEY="ts_live_..."
```

---

## 🐍 Python SDK (`typesafe-sdk`)

```python
from typesafe_sdk import TypeSafeClient, AsyncTypeSafeClient, Choice, Score, Noul

client = TypeSafeClient(api_key="...", timeout_ms=800)

response = client.system_one(
    state="Input text, markdown, or JSON string to evaluate",
    questions={
        "category": Choice(
            instructions="Select primary category",
            criteria={"cat_a": "Description A", "cat_b": "Description B"}
        ),
        "severity": Score(
            instructions="Assess severity level",
            criteria=["Low", "Medium", "High", "Critical"]
        ),
        "is_actionable": Noul(
            instructions="The user statement requires immediate automated action"
        )
    }
)

# Accessing Typed Answers
print(response.answers["category"].choice)         # str
print(response.answers["category"].confidence)     # float (0.0 to 1.0)
print(response.answers["category"].distribution)   # dict[str, float]

print(response.answers["severity"].score)          # int (1-indexed or 0-indexed)
print(response.answers["severity"].expected_val)   # float

print(response.answers["is_actionable"].noul)      # bool
print(response.answers["is_actionable"].probability) # float (0.0 to 1.0)
```

---

## 🟦 TypeScript / JavaScript SDK (`@typesafe-ai/sdk`)

```typescript
import { TypeSafeClient, choice, score, noul } from "@typesafe-ai/sdk";

const client = new TypeSafeClient();

const response = await client.systemOne({
  state: "Context string or object",
  questions: {
    dept: choice({
      instructions: "Route to department",
      criteria: { billing: "Payment issues", support: "Technical help" }
    }),
    urgency: score({
      instructions: "Rate urgency",
      criteria: ["Routine", "Elevated", "Critical"]
    }),
    alert_manager: noul({
      instructions: "Alert the on-duty manager immediately"
    })
  }
});

// TypeScript statically types response.answers.dept.choice as 'billing' | 'support'
console.log(response.answers.dept.choice);
console.log(response.answers.urgency.score);
console.log(response.answers.alert_manager.noul);
```

---

## 🌐 Raw HTTP REST API (`POST https://api.typesafe.ai/v1/systemone`)

```bash
curl -X POST https://api.typesafe.ai/v1/systemone \
  -H "Authorization: Bearer $TYPESAFE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "state": "The user entered invalid credentials 5 times in 2 minutes.",
    "questions": {
      "risk": {
        "type": "choice",
        "instructions": "Evaluate brute-force risk",
        "criteria": { "normal": "Standard typo", "attack": "Automated credential stuffing" }
      },
      "lock_account": {
        "type": "noul",
        "instructions": "Lock user account and require email verification"
      }
    }
  }'
```

---

## 🎯 The Three Primitives Summary

| Primitive | Mathematical Target | Return Type | Typical Use Cases |
| :--- | :--- | :--- | :--- |
| **`Choice`** | Discrete categorical probability distribution | `string` (Key) + `confidence` + `distribution` | Intent routing, department assignment, document categorization, tool picking. |
| **`Score`** | Ordinal scalar distribution | `int` (Level) + `expected_val` + `confidence` | Frustration, risk tier, priority level, quality score, severity rubric. |
| **`Noul`** | Binary veracity probability $P(\text{True}) \in [0, 1]$ | `bool` + `probability` + `confidence` | Guardrails, prompt injection, PII screening, urgent flag, escalation filter. |

---

## ⚡ Performance Rules of Thumb
- **Keep states under 8k tokens** when possible for sub-100ms response times.
- **Group related questions** in a single `client.system_one()` call—they execute simultaneously in the same forward pass!
- **Gate automated code** at `confidence >= 0.90` (RLCD calibrated).
