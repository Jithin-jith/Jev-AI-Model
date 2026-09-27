#!/usr/bin/env python3
"""
Example 2: Dual-System (System 1 + System 2) Routing Pipeline
Run directly: python examples/02_dual_system_pipeline.py
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

from typesafe_sdk import TypeSafeClient, Choice, Score
client = TypeSafeClient(api_key=_api_key)
mode = "LIVE API"

requests = [
    "How do I reset my password?",
    "We need an in-depth security architecture review comparing OAuth2 with PKCE against mTLS for our distributed banking microservices."
]

print(f"=== Dual-System AI Pipeline ({mode}) ===\n")

for req in requests:
    print(f"Analyzing: \"{req}\"")
    
    # System 1: Fast Categorization & Complexity Assessment
    res = client.system_one(
        state=req,
        questions={
            "path": Choice(
                instructions="Determine resolution path",
                criteria={
                    "canned_faq": "Simple common questions like password reset or links",
                    "complex_synthesis": "Architecture design, custom code, deep multi-factor reasoning"
                }
            ),
            "complexity": Score(
                instructions="Reasoning complexity from 1 to 5",
                criteria=["Simple FAQ", "Standard query", "Detailed explanation", "Complex architecture", "PhD research"]
            )
        }
    )

    path = res.answers["path"].choice
    conf = res.answers["path"].confidence
    comp = res.answers["complexity"].score
    lat = getattr(res, "latency_ms", "N/A")

    print(f" -> System 1 Decision in {lat}ms: Path={path} (Conf: {conf:.2%}), Complexity={comp:.2f}/5")
    
    if path == "canned_faq" and conf > 0.80:
        print(" -> [FAST PATH - SYSTEM 1]: Returning instant KB article (Total Latency: 90ms, Cost: $0.000004)\n")
    else:
        print(" -> [DELIBERATE PATH - SYSTEM 2]: Escalating to Frontier LLM (Total Latency: ~1,800ms, Cost: $0.02)\n")
