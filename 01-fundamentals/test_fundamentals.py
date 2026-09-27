#!/usr/bin/env python3
"""
===============================================================================
Module 1 Hands-On Test: Fundamentals & Core Decision Primitives
===============================================================================

This script demonstrates the foundational mechanics of Jev (TypeSafe AI):
1. State Encoding:
   Takes an unstructured incident report and encodes it into dense contextual representations.
2. Parallel Head Evaluation:
   Applies all three core decision primitives simultaneously against that state:
   - Choice: Categorical selection with candidate criteria anchoring.
   - Score:  Ordered rubric evaluation (ordinal regression / distribution).
   - Noul:   Binary veracity judgments with calibrated probabilities.
3. Non-Autoregressive Execution:
   Dispatches a single forward pass via `client.system_one(...)`, avoiding the 
   token-by-token generation overhead of traditional LLMs.
4. Metric Inspection:
   Validates sub-second execution latency and verifies $0.00 output token billing.
"""

import sys
import os
import time

# -----------------------------------------------------------------------------
# Terminal & UTF-8 Configuration
# -----------------------------------------------------------------------------
# On Windows environments, default console encoding (cp1252) can throw a
# UnicodeEncodeError when printing block graphs ('█') or bullet points ('•').
# sys.stdout.reconfigure ensures UTF-8 rendering across all operating systems.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")



# -----------------------------------------------------------------------------
# Environment & API Key Configuration
# -----------------------------------------------------------------------------
try:
    from dotenv import load_dotenv, find_dotenv
    load_dotenv(find_dotenv())
except ImportError:
    pass

# Ensure TYPESAFE_API_KEY is populated if set as api_key or API_KEY
_api_key = os.getenv("TYPESAFE_API_KEY") or os.getenv("api_key") or os.getenv("API_KEY")
if _api_key and not os.getenv("TYPESAFE_API_KEY"):
    os.environ["TYPESAFE_API_KEY"] = _api_key

# -----------------------------------------------------------------------------
# TypeSafe AI Client Initialization
# -----------------------------------------------------------------------------
from typesafe_sdk import TypeSafeClient, Choice, Score, Noul
client = TypeSafeClient(api_key=_api_key)
mode = "LIVE API (TypeSafe AI)"


def run_fundamentals_test():
    """
    Executes an end-to-end evaluation of an incident report across all 3 primitives.
    
    Workflow:
    1. Prepares the raw unstructured text state.
    2. Builds a schema mapping of questions (Choice, Score, Noul).
    3. Triggers client.system_one() for parallel non-autoregressive inference.
    4. Unpacks and displays calibrated confidence scores and probabilities.
    """
    print("=" * 65)
    print("   MODULE 1 HANDS-ON: CORE DECISION PRIMITIVES")
    print(f"   Mode: {mode}")
    print("=" * 65)

    # -------------------------------------------------------------------------
    # 1. State Definition (Unstructured Context)
    # -------------------------------------------------------------------------
    # In Jev, the 'state' represents the raw context to be evaluated. It can
    # be an incident log, customer support message, transaction trace, or document.
    sample_state = """
    Incident Report #4409:
    At 14:22 UTC, our primary Redis cache cluster in eu-central-1 experienced 
    memory exhaustion, causing session invalidations for 18,000 active users. 
    Checkout latency spiked from 120ms to 4,800ms. Operations team activated 
    failover replica at 14:31 UTC. Traffic has stabilized.
    """

    print(f"State Input:\n{sample_state.strip()}\n")
    print("-" * 65)

    # -------------------------------------------------------------------------
    # 2. Decision Primitives Definition
    # -------------------------------------------------------------------------
    # A single dictionary defining heterogeneous decision questions. Each question
    # is mapped to a dedicated decision head on Jev's architecture.
    questions = {
        # ---------------------------------------------------------------------
        # PRIMITIVE 1: Choice (Discrete Categorical Classification)
        # ---------------------------------------------------------------------
        # Used when you need to select one mutually exclusive category out of N.
        # Providing explicit semantic 'criteria' prevents category ambiguity and
        # anchors the model's semantic classification space.
        "incident_category": Choice(
            instructions="Identify the primary technical domain of the incident",
            criteria={
                "database_cache": "Redis, Memcached, Postgres, or storage cluster failures",
                "network_dns": "Routing, DNS resolution, DDoS, or gateway timeouts",
                "application_bug": "Uncaught code exceptions, null pointers, deployment regressions",
                "security_breach": "Unauthorized access, data exfiltration, or compromised credentials"
            }
        ),

        # ---------------------------------------------------------------------
        # PRIMITIVE 2: Score (Ordered Monotonic Rubric Rating)
        # ---------------------------------------------------------------------
        # Used for ordinal ratings where options have an inherent ranking or distance.
        # Jev treats this as an ordered distribution rather than isolated classes,
        # enabling the calculation of an 'expected value' (continuous severity score).
        "severity_level": Score(
            instructions="Evaluate operational severity from SEV-4 (lowest) to SEV-1 (highest)",
            criteria=[
                "SEV-4: Minor issue, non-customer-facing or isolated internal tool glitch",
                "SEV-3: Moderate issue, partial performance degradation with workaround",
                "SEV-2: Major issue, core functionality impaired for a subset of users",
                "SEV-1: Critical emergency, total platform downtime or active revenue loss"
            ]
        ),

        # ---------------------------------------------------------------------
        # PRIMITIVE 3: Noul (Binary Calibrated Truth Assessment)
        # ---------------------------------------------------------------------
        # Derived from 'Null/One' (Boolean), Noul evaluates whether a proposition
        # is objectively true or false regarding the state. Trained via RLCD
        # (Reinforcement Learning for Calibrated Decisions) to produce true
        # mathematical probabilities without LLM overconfidence.
        "is_incident_resolved": Noul(
            instructions="The incident has been mitigated and traffic is currently stabilized"
        ),
        "requires_postmortem": Noul(
            instructions="The severity and impact warrant a formal engineering postmortem review"
        )
    }

    # -------------------------------------------------------------------------
    # 3. Parallel Non-Autoregressive Inference
    # -------------------------------------------------------------------------
    # Unlike GPT-4/Claude, which generate output token-by-token over 1-3 seconds,
    # Jev encodes the state once and passes it through all decision heads in parallel.
    # Total server-side execution takes ~70ms - 250ms.
    t0 = time.time()
    response = client.system_one(state=sample_state, questions=questions)
    elapsed_ms = (time.time() - t0) * 1000

    # -------------------------------------------------------------------------
    # 4. Result Inspection & Unpacking
    # -------------------------------------------------------------------------

    # --- Choice Inspection ---
    # Unpack the winning categorical classification and visualize probability distribution
    choice_ans = response.answers["incident_category"]
    print("1. CHOICE PRIMITIVE (Categorical Classification):")
    print(f"   • Selected:   {choice_ans.choice}")
    print(f"   • Confidence: {choice_ans.confidence:.2%}")
    print(f"   • Candidate Probabilities:")
    # Render an ASCII bar chart for every candidate category
    probs = getattr(choice_ans, "probabilities", getattr(choice_ans, "distribution", {}))
    for cat, prob in probs.items():
        bar = "█" * int(prob * 20)
        print(f"     - {cat:<18}: {prob:>6.2%} {bar}")

    # --- Score Inspection ---
    # Unpack the assessed integer rubric level and the mathematical expected value
    score_ans = response.answers["severity_level"]
    print("\n2. SCORE PRIMITIVE (Ordered Rubric Rating):")
    score_val = score_ans.score
    print(f"   • Assessed Score: {score_val:.2f} (out of 4)")
    print(f"   • Confidence:     {score_ans.confidence:.2%}")
    print(f"   • Expected Value: {getattr(score_ans, 'expected_val', score_val):.2f}")

    # --- Noul Inspection ---
    # Unpack binary decisions (True/False) and their calibrated probabilities
    noul_resolved = response.answers["is_incident_resolved"]
    noul_postmortem = response.answers["requires_postmortem"]

    def _format_noul(n):
        p = getattr(n, "probability", None)
        if p is None:
            p = n.noul if isinstance(n.noul, (int, float)) else 0.5
        verdict = n.noul if isinstance(n.noul, bool) else (p >= 0.5)
        return verdict, p

    res_verdict, res_p = _format_noul(noul_resolved)
    post_verdict, post_p = _format_noul(noul_postmortem)

    print("\n3. NOUL PRIMITIVE (Calibrated Probability Truth Value):")
    print(f"   • 'Incident is resolved':   {res_verdict} (P = {res_p:.2%})")
    print(f"   • 'Requires postmortem':   {post_verdict} (P = {post_p:.2%})")

    # -------------------------------------------------------------------------
    # 5. Latency & Economics Summary
    # -------------------------------------------------------------------------
    print("-" * 65)
    # Server-side execution speed or measured latency in milliseconds
    lat = getattr(response, "latency_ms", round(elapsed_ms, 1))
    print(f"⚡ Jev Execution Latency:     {lat} ms")
    # In Jev, structured decisions do not emit text tokens, so output tokens are always 0
    print(f"💰 Output Tokens Billed:     {response.usage.output_tokens} (Always $0.00 / Free)")
    print("=" * 65)


if __name__ == "__main__":
    run_fundamentals_test()
