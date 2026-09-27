# Module 4.1: Hybrid System 1 + System 2 Pipeline

The pinnacle of modern GenAI production engineering is the **Hybrid Dual-System Architecture**.

Rather than choosing between Jev or a Frontier LLM (such as GPT-4o, Claude 3.7 Sonnet, or Gemini 2.5 Pro), enterprise architects combine them into a symbiotic pipeline where each model operates strictly within its cognitive domain.

---

## 🏛️ The Canonical Dual-System Architecture

```
                                [ Incoming User Event ]
                                           │
                                           ▼
                            ┌─────────────────────────────┐
                            │      STAGE 1: SYSTEM 1      │
                            │      Jev (TypeSafe AI)      │
                            │      Latency: ~90ms         │
                            │      Cost: $0.042 / 1M      │
                            └──────────────┬──────────────┘
                                           │
                                  Confidence & Intent
                                           │
          ┌────────────────────────────────┼────────────────────────────────┐
          ▼                                ▼                                ▼
  [ Intent: FAQ / Cache ]          [ Intent: Actionable API ]     [ Intent: Complex Synthesis ]
  Confidence > 0.92                Confidence > 0.90              or Low Confidence (< 0.85)
          │                                │                                │
          ▼                                ▼                                ▼
┌───────────────────┐            ┌───────────────────┐            ┌───────────────────────────┐
│ Instant Cache Hit │            │ Direct Microserv. │            │     STAGE 2: SYSTEM 2     │
│ Return static FAQ │            │ Execute SQL/Stripe│            │     Frontier LLM          │
│ Total Time: 95ms  │            │ Total Time: 130ms │            │     (Claude / GPT-4o)     │
│ Cost: ~$0.000004  │            │ Cost: ~$0.000005  │            │     Deep Generative Draft │
└───────────────────┘            └───────────────────┘            │     Total Time: 1,800ms   │
                                                                  │     Cost: ~$0.025         │
                                                                  └───────────────────────────┘
```

---

## 💻 Full Python End-to-End Pipeline

```python
import os
from typesafe_sdk import TypeSafeClient, Choice, Score, Noul
# Optional: from openai import OpenAI or anthropic import Anthropic

client_jev = TypeSafeClient()

def process_customer_message(user_message: str, customer_id: str) -> dict:
    """
    Hybrid Dual-System Pipeline:
    - 80% of traffic handled in <120ms by Jev System 1
    - 20% escalated to Frontier LLM System 2
    """
    print(f"\n[SYSTEM 1] Analyzing incoming request: '{user_message}'")
    
    # 1. System 1: Fast Parallel Triage
    sys1_response = client_jev.system_one(
        state=user_message,
        questions={
            "intent": Choice(
                instructions="Determine the user's primary goal",
                criteria={
                    "order_status": "Checking shipping, tracking number, or delivery date",
                    "cancellation": "Canceling an order before shipment",
                    "faq_return_policy": "Asking what the return policy or warranty terms are",
                    "complex_inquiry": "Custom quotation, edge-case troubleshooting, or multi-part complaints"
                }
            ),
            "sentiment_score": Score(
                instructions="Assess customer agitation from 1 (placid) to 5 (outraged)",
                criteria=[
                    "Friendly / neutral",
                    "Mildly curious",
                    "Concerned",
                    "Angry",
                    "Furious / demanding compensation"
                ]
            ),
            "requires_human_agent": Noul(
                instructions="The customer demands to talk to a human supervisor immediately"
            )
        }
    )

    intent = sys1_response.answers["intent"].choice
    confidence = sys1_response.answers["intent"].confidence
    agitation = sys1_response.answers["sentiment_score"].score
    needs_human = sys1_response.answers["requires_human_agent"].noul

    print(f"[SYSTEM 1 RESULT] Intent: {intent} (Confidence: {confidence:.2f}), Agitation: {agitation}/5")

    # Safety override: if customer is furious or asks for human, bypass bot
    if needs_human or agitation >= 4:
        return {
            "handler": "HUMAN_SUPERVISOR_QUEUE",
            "latency": sys1_response.latency_ms,
            "message": "Connecting you directly to a senior support supervisor now."
        }

    # Fast Path 1: Instant FAQ lookup
    if intent == "faq_return_policy" and confidence >= 0.88:
        return {
            "handler": "SYSTEM_1_INSTANT_CACHE",
            "latency": sys1_response.latency_ms,
            "message": "We offer 30-day no-questions-asked returns. Print your return label here: https://store.example/returns"
        }

    # Fast Path 2: Deterministic Backend API lookup
    if intent == "order_status" and confidence >= 0.90:
        tracking_info = lookup_order_database(customer_id)
        return {
            "handler": "SYSTEM_1_DETERMINISTIC_API",
            "latency": sys1_response.latency_ms,
            "message": f"Your order #{tracking_info['id']} is currently {tracking_info['status']} and estimated for delivery on {tracking_info['delivery_date']}."
        }

    # Escalation Path: System 2 Frontier LLM
    print("⚡ System 1 determined request requires deep reasoning. Invoking System 2 LLM...")
    return invoke_system_2_frontier_llm(user_message, intent, sys1_response.latency_ms)

def lookup_order_database(customer_id: str):
    # Simulated fast database lookup
    return {"id": "ORD-88192", "status": "In Transit via FedEx", "delivery_date": "Tomorrow by 5 PM"}

def invoke_system_2_frontier_llm(user_message: str, classified_intent: str, sys1_lat: int):
    # System 2: Frontier LLM handles generation with pre-triaged intent context
    # (e.g. OpenAI / Anthropic call)
    simulated_llm_response = (
        f"[Drafted by Claude 3.7 / GPT-4o] Thank you for detailing this unique inquiry regarding "
        f"{classified_intent}. Here is our custom proposal..."
    )
    return {
        "handler": "SYSTEM_2_FRONTIER_LLM",
        "total_latency_ms": sys1_lat + 1450,
        "message": simulated_llm_response
    }
```

---

## 📊 Business & Financial Impact

For a company processing **5,000,000 requests / month**:

| Metric | 100% LLM (Monolithic) | Dual-System (Jev + Frontier LLM) | Difference |
| :--- | :--- | :--- | :--- |
| **Median Latency (p50)** | 1,450 ms | **110 ms** | **13.1x Faster** |
| **95th Percentile (p95)**| 3,800 ms | **320 ms** | **11.8x Faster** |
| **Monthly Compute Cost** | $42,500 / mo | **$6,800 / mo** | **84% Cost Savings ($35.7k saved/mo)** |
| **JSON Parse Exceptions**| ~12,500 / mo | **0 / mo** | **100% Deterministic** |
