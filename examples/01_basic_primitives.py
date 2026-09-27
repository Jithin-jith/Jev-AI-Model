#!/usr/bin/env python3
"""
Example 1: Basic Decision Primitives in Jev (Choice, Score, Noul)
Run directly: python examples/01_basic_primitives.py
"""

import sys
import os

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

sys.path.append(os.path.dirname(__file__))

try:
    from dotenv import load_dotenv, find_dotenv
    load_dotenv(find_dotenv())
except ImportError:
    pass

_api_key = os.getenv("TYPESAFE_API_KEY") or os.getenv("api_key") or os.getenv("API_KEY")
if _api_key and not os.getenv("TYPESAFE_API_KEY"):
    os.environ["TYPESAFE_API_KEY"] = _api_key

from typesafe_sdk import TypeSafeClient, Choice, Score, Noul
client = TypeSafeClient(api_key=_api_key)
mode = "LIVE API"

input_text = """
Hi Support, I noticed a charge of $49 on my card today for an annual renewal.
I thought I had canceled my subscription 2 weeks ago. Could you please check this and refund me?
"""

print(f"=== Running Jev Basic Primitives Demo ({mode}) ===")
print(f"Input State: {input_text.strip()}\n")

response = client.system_one(
    state=input_text,
    questions={
        "topic": Choice(
            instructions="Identify the primary topic of the inquiry",
            criteria={
                "billing": "Charges, invoices, credit cards, or refunds",
                "technical": "Software bugs, crashes, or system errors",
                "sales": "Upgrades, enterprise contracts, or volume pricing"
            }
        ),
        "sentiment": Score(
            instructions="Rate the tone of the customer message from 1 (neutral/polite) to 3 (hostile)",
            criteria=[
                "Polite and constructive",
                "Annoyed or confused",
                "Aggressive or demanding"
            ]
        ),
        "wants_refund": Noul(
            instructions="The user is asking for their money back or a refund"
        )
    }
)

lat = getattr(response, "latency_ms", "N/A")
print(f"Latency:      {lat} ms")
print(f"Topic:        {response.answers['topic'].choice} (Confidence: {response.answers['topic'].confidence:.2%})")
sentiment_val = response.answers['sentiment'].score
print(f"Sentiment:    Level {sentiment_val:.2f} / 3")

wants_ref_ans = response.answers['wants_refund']
ref_p = getattr(wants_ref_ans, "probability", wants_ref_ans.noul if isinstance(wants_ref_ans.noul, (int, float)) else 0.5)
ref_v = wants_ref_ans.noul if isinstance(wants_ref_ans.noul, bool) else (ref_p >= 0.5)
print(f"Wants Refund: {ref_v} (Probability: {ref_p:.2%})")
