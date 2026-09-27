#!/usr/bin/env python3
"""
===============================================================================
Project 3: Dual-System Agent Orchestration Pipeline
===============================================================================

Architectural Overview:
Inspired by Daniel Kahneman's cognitive framework in 'Thinking, Fast and Slow',
this enterprise architecture establishes a dual-tier agent routing system:

1. System 1 (Fast & Intuitive - Jev):
   - Non-autoregressive forward pass executing in 70ms–150ms.
   - Evaluates input state to determine:
     * Optimal action route (`cached_faq`, `database_tool`, or `deep_reasoning`).
     * Complexity level (1 to 5 ordinal rubric).
     * Generation necessity (`needs_llm_generation` boolean veracity).
   - Extremely cost-efficient: $0.042 per 1M tokens ($0.00 output tokens).

2. System 2 (Slow & Deliberative - Frontier LLM):
   - Multi-second autoregressive generation (Claude 3.7 Sonnet, GPT-4o).
   - Reserved strictly for ambiguous, multi-factor architectural synthesis,
     complex code drafting, or strategic decision-making.
   - Higher operational cost: $5.00–$15.00 per 1M tokens.

Economic & Latency Impact:
By delegating 70%–80% of routine requests to System 1 instant cache or deterministic
SQL tools, overall system latency drops by 80% and API infrastructure bills
are reduced by up to 90%.
"""

import sys
import os
import time

# -----------------------------------------------------------------------------
# Terminal & UTF-8 Configuration
# -----------------------------------------------------------------------------
# Reconfigure standard output to UTF-8 to prevent unicode encoding failures on Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# -----------------------------------------------------------------------------
# Environment & API Key Resolution
# -----------------------------------------------------------------------------
try:
    from dotenv import load_dotenv, find_dotenv
    load_dotenv(find_dotenv())
except ImportError:
    pass

_api_key = os.getenv("TYPESAFE_API_KEY") or os.getenv("api_key") or os.getenv("API_KEY")
if _api_key and not os.getenv("TYPESAFE_API_KEY"):
    os.environ["TYPESAFE_API_KEY"] = _api_key

# -----------------------------------------------------------------------------
# Official SDK Client Initialization
# -----------------------------------------------------------------------------
from typesafe_sdk import TypeSafeClient, Choice, Score, Noul
client = TypeSafeClient(api_key=_api_key)
IS_LIVE = True

# -----------------------------------------------------------------------------
# Representative User Query Scenarios
# -----------------------------------------------------------------------------
USER_SCENARIOS = [
    {
        "id": "SCN-1",
        "description": "Standard FAQ Inquiry",
        "query": "Where can I view the API rate limits and how do I request a quota increase?"
    },
    {
        "id": "SCN-2",
        "description": "Deterministic Database Lookup",
        "query": "Can you check the current status and tracking number for Order #98214?"
    },
    {
        "id": "SCN-3",
        "description": "Complex Analytical Reasoning Task",
        "query": (
            "Compare our cloud deployment architecture in AWS vs Azure, accounting for "
            "SOC2 compliance, multi-region failover, and projected 3-year egress costs "
            "with 50TB monthly transfer."
        )
    }
]


def simulate_system_2_llm(query: str) -> str:
    """
    Simulates a heavy, multi-second deliberative generation from a Frontier LLM.
    
    Args:
        query (str): The complex query requiring deep synthesis.
        
    Returns:
        str: Synthesized multi-paragraph analytical response.
    """
    print("   [SYSTEM 2] Activating Frontier LLM (Thinking, Fast & Slow: Deliberative Mode)...")
    time.sleep(0.5)  # Simulate model latency (in reality 1,500ms - 4,000ms)
    return (
        "Based on comprehensive analysis: AWS provides multi-region active-active Aurora and GovCloud "
        "tailored for SOC2 Type II. Azure offers comparable ExpressRoute interconnects. With 50TB egress, "
        "AWS CloudFront with private pricing achieves 18% lower 3-year TCO over Azure front-door routing..."
    )


def orchestrate(scenario: dict):
    """
    Executes end-to-end dual-system orchestration for an incoming user query.
    
    Args:
        scenario (dict): Dictionary with 'id', 'description', and 'query' text.
        
    Workflow:
    1. System 1 (Jev) inspects query in a single forward pass (<100ms).
    2. Checks routing classification confidence and complexity score.
    3. If query is a routine FAQ or structured tool lookup, handles it instantly.
    4. If query demands deep generative reasoning, escalates to System 2 LLM.
    """
    print(f"\n=======================================================")
    print(f"🤖 User Query [{scenario['id']} - {scenario['description']}]")
    print(f"Text: \"{scenario['query']}\"")
    print(f"-------------------------------------------------------")

    start_time = time.time()

    # -------------------------------------------------------------------------
    # Stage 1: System 1 Parallel Forward Pass via Jev
    # -------------------------------------------------------------------------
    response = client.system_one(
        state=scenario["query"],
        questions={
            # Choice: Dispatches between fast paths (FAQ/DB) and heavy reasoning
            "action_route": Choice(
                instructions="Determine the execution path for this query",
                criteria={
                    "cached_faq": "Standard documentation questions, rate limits, pricing tiers, links",
                    "database_tool": "Specific transactional lookups, order status, account IDs",
                    "deep_reasoning": "Architecture comparisons, custom code writing, strategic advice, nuanced analysis"
                }
            ),
            # Score: Ordinal rubric quantifying analytical depth
            "complexity_level": Score(
                instructions="Assess reasoning complexity from 1 (trivial/lookup) to 5 (advanced multi-factor analysis)",
                criteria=[
                    "Trivial factual lookup",
                    "Simple single-step request",
                    "Multi-step procedure",
                    "Complex domain synthesis",
                    "PhD-level deep strategic or mathematical reasoning"
                ]
            ),
            # Noul: Calibrated judgment verifying if bespoke natural language prose is required
            "needs_llm_generation": Noul(
                instructions="The request requires synthesizing custom, non-templated natural language prose"
            )
        }
    )

    ans = response.answers
    route = ans["action_route"].choice
    conf = ans["action_route"].confidence
    complexity = ans["complexity_level"].score
    
    needs_gen_ans = ans["needs_llm_generation"]
    gen_p = getattr(needs_gen_ans, "probability", needs_gen_ans.noul if isinstance(needs_gen_ans.noul, (int, float)) else 0.5)
    needs_gen = needs_gen_ans.noul if isinstance(needs_gen_ans.noul, bool) else (gen_p >= 0.5)

    lat = getattr(response, "latency_ms", "N/A")
    print(f"⚡ System 1 (Jev) Evaluated in {lat} ms (Mode: {'LIVE' if IS_LIVE else 'SIMULATOR'})")
    print(f"   • Recommended Route: {route} (Confidence: {conf:.2%})")
    print(f"   • Complexity Score:  {complexity:.2f} / 5")
    print(f"   • Needs Generation:  {needs_gen} (Prob: {gen_p:.2%})")

    # -------------------------------------------------------------------------
    # Stage 2: Dual-Process Routing Logic
    # -------------------------------------------------------------------------
    
    # Path A: Fast System 1 Instant Knowledge Base Cache
    if route == "cached_faq" and conf >= 0.85:
        total_time = round((time.time() - start_time) * 1000, 1)
        print(f"\n🚀 [PATH: SYSTEM 1 INSTANT RESOLUTION - {total_time}ms]")
        print("Response: 'Rate limits are 1,000 QPS on Pro tiers. Quota requests can be made at https://console.example.com/quotas'")
    
    # Path B: Fast System 1 Deterministic SQL/API Tool Execution
    elif route == "database_tool" and conf >= 0.85:
        total_time = round((time.time() - start_time) * 1000, 1)
        print(f"\n🚀 [PATH: SYSTEM 1 DETERMINISTIC TOOL DISPATCH - {total_time}ms]")
        print("Response: 'Order #98214 is In-Transit via UPS (Tracking: 1Z9999999999999999). Delivery by Tomorrow.'")
    
    # Path C: Deliberative System 2 Escalation (Frontier LLM Reasoning)
    else:
        print(f"\n⚡ [PATH: SYSTEM 2 ESCALATION REQUIRED]")
        llm_reply = simulate_system_2_llm(scenario["query"])
        total_time = round((time.time() - start_time) * 1000, 1)
        print(f"\n🧠 [SYSTEM 2 FINAL GENERATION - {total_time}ms]")
        print(f"Response: {llm_reply}")


def main():
    """
    Main orchestration entry point: evaluates all sample scenarios.
    """
    print("=======================================================")
    print("     DUAL-SYSTEM AGENT ORCHESTRATION PIPELINE          ")
    print("=======================================================")
    for scenario in USER_SCENARIOS:
        orchestrate(scenario)


if __name__ == "__main__":
    main()
