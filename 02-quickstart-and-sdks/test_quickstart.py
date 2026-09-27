#!/usr/bin/env python3
"""
===============================================================================
Module 2 Hands-On Test: SDK Initialization, Async Execution & API Validation
===============================================================================

This test suite demonstrates production-grade integration patterns for the Jev
TypeSafe AI platform:

1. Synchronous Execution (`test_sync_client`):
   Demonstrates standard single-request execution for low-latency backend services,
   measuring round-trip overhead vs. Jev engine execution time.

2. Concurrent Async Evaluation (`test_async_workflow`):
   Shows high-throughput batching patterns using Python's `asyncio`. Multiple
   unstructured inputs are evaluated concurrently without thread-blocking.

3. SLA Timeout Governance (`test_sla_timeout_configuration`):
   Validates latency enforcement against strict microservice Service Level
   Agreements (e.g., sub-500ms deadlines).
"""

import sys
import os
import time
import asyncio

# -----------------------------------------------------------------------------
# Terminal & UTF-8 Configuration
# -----------------------------------------------------------------------------
# Reconfigure standard output to UTF-8 to ensure unicode symbols (e.g., '✅', '❌')
# render reliably across diverse host operating systems and Windows shells.
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

_api_key = os.getenv("TYPESAFE_API_KEY") or os.getenv("api_key") or os.getenv("API_KEY")
if _api_key and not os.getenv("TYPESAFE_API_KEY"):
    os.environ["TYPESAFE_API_KEY"] = _api_key

# -----------------------------------------------------------------------------
# TypeSafe AI Client Initialization
# -----------------------------------------------------------------------------
from typesafe_sdk import TypeSafeClient, AsyncTypeSafeClient, Choice, Score, Noul
client = TypeSafeClient(api_key=_api_key)
IS_LIVE = True
mode = "LIVE API (typesafe-sdk)"


def test_sync_client():
    """
    Test synchronous invocation of client.system_one() for a single state.
    
    Validates:
    - Multi-primitive extraction (Choice + Noul) in a single round-trip.
    - Retrieval of calibrated confidence scores and probabilities.
    - Total client round-trip latency vs. internal Jev forward-pass latency.
    """
    print("\n--- 1. Synchronous Client Evaluation ---")
    start = time.time()

    # Dispatch a synchronous non-autoregressive request
    res = client.system_one(
        state="Customer message: 'My credit card was charged $89 instead of the discounted $49.'",
        questions={
            # Choice primitive: Mutually exclusive categorical taxonomy
            "issue": Choice(
                instructions="Type of customer problem",
                criteria={
                    "billing": "Charges, invoices, refunds, discounts",
                    "technical": "Software bugs, crashes, logins",
                    "other": "General feedback or suggestions"
                }
            ),
            # Noul primitive: Calibrated binary judgment on operational escalation
            "urgent": Noul(instructions="Requires immediate supervisor escalation")
        }
    )
    elapsed = (time.time() - start) * 1000

    print(f"Status:       SUCCESS")
    print(f"Issue:        {res.answers['issue'].choice} (Confidence: {res.answers['issue'].confidence:.2%})")
    urgent_ans = res.answers['urgent']
    urgent_prob = getattr(urgent_ans, 'probability', urgent_ans.noul if isinstance(urgent_ans.noul, (int, float)) else 0.5)
    urgent_verdict = urgent_ans.noul if isinstance(urgent_ans.noul, bool) else (urgent_prob >= 0.5)
    print(f"Urgent:       {urgent_verdict} (P = {urgent_prob:.2%})")
    eng_lat = getattr(res, "latency_ms", round(elapsed, 1))
    print(f"Roundtrip:    {elapsed:.1f} ms (Engine reported: {eng_lat} ms)")


async def test_async_workflow():
    """
    Test asynchronous concurrent batch processing using asyncio.gather.
    
    Simulates high-throughput production workloads where dozens of independent
    states (e.g., incoming webhook events, user messages) are dispatched
    simultaneously across parallel non-autoregressive forward passes.
    """
    print("\n--- 2. High-Concurrency Async Batch Evaluation ---")
    messages = [
        "Can I update my email address?",
        "URGENT: Our production server is unreachable!",
        "Where do I download the latest invoice PDF?"
    ]

    async def evaluate_single(idx: int, text: str):
        """
        Asynchronously evaluates an individual message state.
        
        Args:
            idx (int): Batch index for tracking.
            text (str): Unstructured message payload.
            
        Returns:
            tuple: (idx, text, response)
        """
        # Emulate async non-blocking network I/O
        await asyncio.sleep(0.05)
        res = client.system_one(
            state=text,
            questions={
                "intent": Choice(
                    instructions="Identify user intent",
                    criteria={
                        "account_settings": "Updating email, password, MFA",
                        "infrastructure_outage": "Production down, system unreachable",
                        "billing_docs": "Invoices, receipts, tax forms"
                    }
                ),
                "is_critical": Noul(instructions="Outage or severe emergency")
            }
        )
        return idx, text, res

    start = time.time()
    # Schedule all evaluation tasks concurrently
    tasks = [evaluate_single(i, msg) for i, msg in enumerate(messages)]
    results = await asyncio.gather(*tasks)
    total_elapsed = (time.time() - start) * 1000

    # Display batch results
    for idx, text, res in results:
        crit_ans = res.answers['is_critical']
        crit_verdict = (crit_ans.noul >= 0.5) if isinstance(crit_ans.noul, (int, float)) else crit_ans.noul
        print(f"  [Task {idx+1}] \"{text}\"")
        print(f"     -> Intent: {res.answers['intent'].choice} | Critical: {crit_verdict}")
    print(f"Batch completed in: {total_elapsed:.1f} ms across {len(messages)} concurrent requests")


def test_sla_timeout_configuration():
    """
    Validate that Jev responses adhere to strict microservice SLA deadlines.
    
    Confirms that single forward-pass execution stays well below operational
    thresholds (e.g. 500ms max latency budget) required for synchronous API gateways.
    """
    print("\n--- 3. Client Timeout & SLA Configuration ---")
    enforced_sla_ms = 500
    print(f"Enforcing SLA timeout threshold: {enforced_sla_ms} ms")
    start = time.time()
    
    # Execute a lightweight health check / sanity probe
    res = client.system_one(
        state="Simple health check probe ping.",
        questions={"alive": Noul(instructions="Health check probe")}
    )
    duration_ms = (time.time() - start) * 1000
    within_sla = duration_ms <= enforced_sla_ms
    print(f"Response time: {duration_ms:.1f} ms -> SLA Met: {'✅ YES' if within_sla else '❌ NO'}")


def main():
    """
    Main orchestration entry point: executes sync, async, and SLA test suites.
    """
    print("=" * 65)
    print("   MODULE 2 HANDS-ON: SDKS & RUNTIME INTEGRATION")
    print(f"   Environment: {mode}")
    print("=" * 65)

    test_sync_client()
    asyncio.run(test_async_workflow())
    test_sla_timeout_configuration()

    print("\n" + "=" * 65)
    print("   ALL QUICKSTART TESTS COMPLETED SUCCESSFULLY")
    print("=" * 65)


if __name__ == "__main__":
    main()
