# Module 3.3: Batch & Multi-Dimensional Questioning

A common bottleneck in GenAI microservices is feature extraction. For instance, when analyzing a resume, a contract, or an incoming loan application, systems often need answers to 10 to 30 distinct questions.

With standard LLMs, engineers either:
1. Make 20 sequential calls (taking 20–40 seconds).
2. Ask for a massive JSON object with 20 keys, which frequently leads to missing keys, invalid syntax, or hallucinated fields.

Jev solves this by evaluating **arbitrary numbers of questions in a single forward pass**.

---

## ⚡ The Multi-Question Parallel Forward Pass

Because Jev's attention mechanism handles multiple question cross-attentions against a single encoded state representation, adding questions scales sub-linearly with latency.

```
State (Contract Text: 2,500 tokens)
   │
   ├── Question 1: governing_law (Choice)
   ├── Question 2: liability_cap_exceeded (Noul)
   ├── Question 3: auto_renew (Noul)
   ├── Question 4: payment_term_days (Score)
   ├── Question 5: exclusivity_clause (Noul)
   ├── Question 6: indemnity_risk (Score)
   └── ... up to 25+ questions
```

---

## 💻 Python Example: 8-Factor Legal Contract Analysis

```python
from typesafe_sdk import TypeSafeClient, Choice, Score, Noul

client = TypeSafeClient()

contract_text = """
MASTER SERVICES AGREEMENT (MSA)
Section 4. Payment Terms: All undisputed invoices shall be paid net 60 days from receipt.
Section 9. Term & Termination: This agreement renews automatically for successive 1-year terms
unless either party gives 90 days written notice of cancellation.
Section 12. Limitation of Liability: Neither party's aggregate liability under this agreement
shall exceed 10x the total fees paid in the preceding 12 months.
Section 16. Governing Law: This Agreement shall be governed by the laws of the State of Delaware.
Section 18. Exclusivity: Customer agrees not to engage or contract with any competing provider
of similar SaaS products during the term.
"""

response = client.system_one(
    state=contract_text,
    questions={
        "governing_jurisdiction": Choice(
            instructions="Identify the legal jurisdiction governing this agreement",
            criteria={
                "delaware": "State of Delaware",
                "california": "State of California",
                "new_york": "State of New York",
                "england_wales": "England and Wales",
                "other": "Any other jurisdiction"
            }
        ),
        "has_auto_renewal": Noul(
            instructions="The contract renews automatically unless cancelled"
        ),
        "has_exclusivity_lockout": Noul(
            instructions="The contract includes non-compete or vendor exclusivity obligations"
        ),
        "liability_risk_tier": Score(
            instructions="Evaluate the financial liability risk level from 1 to 5",
            criteria=[
                "Extremely favorable (capped at fees paid)",
                "Standard commercial terms (capped at 1x-2x annual fees)",
                "High risk (capped at 5x-10x annual fees)",
                "Severe risk (unlimited liability for general breaches)",
                "Catastrophic (uncapped indirect & consequential damages)"
            ]
        ),
        "payment_flexibility": Choice(
            instructions="Determine the invoice payment window",
            criteria={
                "net_15": "Payment due within 15 days",
                "net_30": "Standard 30 days window",
                "net_60": "Extended 60 days window",
                "net_90_plus": "Very long delay (90+ days)"
            }
        )
    }
)

# Process all dimensions cleanly
answers = response.answers
print(f"Jurisdiction:    {answers['governing_jurisdiction'].choice}")
print(f"Auto-Renewal:    {answers['has_auto_renewal'].noul}")
print(f"Exclusivity:     {answers['has_exclusivity_lockout'].noul}")
print(f"Liability Tier:  {answers['liability_risk_tier'].score} / 5")
print(f"Payment Term:    {answers['payment_flexibility'].choice}")
print(f"Execution Time:  {response.latency_ms} ms")
```

---

## 📊 Performance Benchmark

Evaluating 8 complex questions across a 2,500-token contract:

| Metric | GPT-4o (JSON Mode) | Jev System One |
| :--- | :--- | :--- |
| **Response Time** | 2,850 ms | **165 ms** |
| **Cost per 1,000 Contracts** | ~$18.00 | **~$0.11** |
| **Schema Validation Errors** | 1.8% | **0.0%** |
