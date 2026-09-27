# Module 3.1: Confidence Gating & Dynamic Routing

In software engineering, deterministic control flow requires predictability. When building AI systems, uncalibrated decisions lead to either:
1. **False Positives:** Automated actions trigger when they shouldn't (e.g. issuing unauthorized refunds).
2. **False Negatives:** Legitimate user requests get blocked or dropped.

Because Jev is trained via **RLCD (Reinforcement Learning for Calibrated Decisions)**, its confidence scores accurately reflect the empirical probability of correctness. This enables the **Confidence Gating Pattern**.

---

## 🎯 The Three-Tier Gating Architecture

When processing incoming requests, set explicit threshold tiers:

```
                  ┌───────────────────────────────┐
                  │      Jev Evaluation ($0.042)  │
                  └───────────────┬───────────────┘
                                  │
                                  ▼
                    Confidence Score Evaluation
                 ┌────────────────┼────────────────┐
                 ▼                ▼                ▼
         [ Score >= 0.90 ]  [ 0.65 <= Score < 0.90 ] [ Score < 0.65 ]
                 │                │                │
                 ▼                ▼                ▼
         Tier 1: Fast Path    Tier 2: LLM Eval    Tier 3: Human Review
         • Fully automated    • System 2 reason   • Escalation queue
         • Sub-150ms SLA      • Synthesize logic  • Human-in-the-loop
         • Zero human cost    • 1,500ms SLA       • Audit trail
```

---

## 💻 Python Implementation

```python
from typesafe_sdk import TypeSafeClient, Choice

client = TypeSafeClient()

def route_refund_request(user_message: str, transaction_amount: float):
    response = client.system_one(
        state=f"Amount: ${transaction_amount}\nUser: {user_message}",
        questions={
            "refund_eligibility": Choice(
                instructions="Determine if this transaction is eligible for automated refund under policy",
                criteria={
                    "eligible_instant": "Item was not received within delivery guarantee, or defective upon arrival",
                    "eligible_standard": "Return within 30 days, unopened, standard return policy",
                    "ineligible": "Past 30 days, buyer remorse, digital goods already redeemed",
                    "fraud_risk": "Suspicious account behavior or chargeback threats"
                }
            )
        }
    )

    decision = response.answers["refund_eligibility"]
    category = decision.choice
    confidence = decision.confidence

    print(f"Jev Decision: {category} (Confidence: {confidence:.2%})")

    # Tier 1: High Confidence Automation
    if confidence >= 0.92:
        if category == "eligible_instant" and transaction_amount <= 100.0:
            return execute_instant_stripe_refund(transaction_amount)
        elif category == "ineligible":
            return send_automated_denial_email()

    # Tier 2: Medium Confidence -> System 2 Frontier LLM
    elif confidence >= 0.65:
        print("⚡ System 1 uncertainty detected. Escalating to Frontier LLM for deep policy reasoning...")
        return escalate_to_frontier_llm(user_message, transaction_amount)

    # Tier 3: Low Confidence -> Human-In-The-Loop
    else:
        print("⚠️ High ambiguity. Escalating to human customer support specialist...")
        return create_zendesk_human_ticket(user_message, category, confidence)

def execute_instant_stripe_refund(amount):
    return {"status": "SUCCESS", "action": "INSTANT_REFUND", "amount": amount}

def send_automated_denial_email():
    return {"status": "DENIED", "action": "AUTO_REJECTION_EMAIL"}

def escalate_to_frontier_llm(msg, amount):
    return {"status": "SYSTEM_2_ESCALATION", "agent": "Claude-3.7-Sonnet"}

def create_zendesk_human_ticket(msg, cat, conf):
    return {"status": "HUMAN_TRIAGE", "suggested_category": cat, "confidence": conf}
```

---

## 📈 Real-World Benefits of Gating

In typical customer service or ecommerce workloads:
- **70% to 85% of traffic** qualifies for Tier 1 (High Confidence, > 92%). These requests finish in **< 150ms** for pennies.
- **10% to 20% of traffic** escalates to Tier 2 (LLM deep reasoning).
- **Only 5% of traffic** requires human staff intervention.

This reduces total LLM operational spend by **80%+** while cutting median customer wait time from minutes to sub-second.
