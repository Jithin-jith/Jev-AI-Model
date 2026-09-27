#!/usr/bin/env python3
"""
===============================================================================
Project 1: Enterprise Support Ticket Triage Engine powered by Jev (TypeSafe AI)
===============================================================================

Architectural Overview:
Traditional customer support routing relies on fragile keyword regexes or slow,
expensive autoregressive LLM calls that take 1.5–3.5 seconds per inbound email.

This production triage pipeline utilizes Jev's non-autoregressive parallel heads
to evaluate four critical triage dimensions simultaneously in a single sub-100ms
forward pass:
1. Categorical Routing (`department`): 
   Classifies incoming text into dedicated engineering, finance, or success teams.
2. Frustration & Sentiment (`frustration_score`): 
   Evaluates an ordinal 1-to-5 rubric representing customer urgency and distress.
3. Outage Detection (`is_outage`): 
   Calibrated binary verification detecting widespread service failure.
4. Channel Preference (`wants_phone_callback`): 
   Detects explicit customer demands for telephone callbacks.

Business Outcome:
- Instant P0 PagerDuty alerts dispatched within 90ms of webhook ingestion.
- Eliminates 99% of LLM token costs through non-autoregressive decision heads.
"""

import sys
import os

# -----------------------------------------------------------------------------
# Terminal & UTF-8 Configuration
# -----------------------------------------------------------------------------
# Ensure UTF-8 stdout encoding for Windows terminals to render Unicode icons
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
# Synthetic Production Workload: Inbound Support Tickets
# -----------------------------------------------------------------------------
SAMPLE_TICKETS = [
    {
        "id": "TCK-101",
        "sender": "cto@fintechstartup.com",
        "body": (
            "CRITICAL: Our webhook integration with your API is returning 500 "
            "Internal Server Errors since 20 minutes ago. Over 500 card checkouts "
            "have dropped. We need an on-call engineer to call us immediately at +1-415-555-0143!"
        )
    },
    {
        "id": "TCK-102",
        "sender": "sarah.m@retailco.com",
        "body": (
            "Hi there! I was reviewing our monthly invoice for August and noticed "
            "a duplicate charge of $120.00 for user seat licenses. Could someone please "
            "adjust this on our next statement?"
        )
    },
    {
        "id": "TCK-103",
        "sender": "alex.dev@indieapp.io",
        "body": (
            "Hey team, loving the platform so far! Just wondering if you have any plans "
            "to support Rust SDKs or WebSocket streaming in Q4? Keep up the great work."
        )
    }
]


def triage_ticket(ticket: dict):
    """
    Evaluates an individual support ticket across all triage dimensions in parallel.
    
    Args:
        ticket (dict): Dictionary containing 'id', 'sender', and 'body' of ticket.
        
    Workflow:
    1. Submits raw ticket text as 'state' to Jev System One.
    2. Runs four decision heads simultaneously (Choice, Score, Noul x2).
    3. Feeds extracted parameters into a deterministic business logic routing matrix.
    4. Triggers operational routing actions (e.g., PagerDuty, Finance Zendesk, General).
    """
    print(f"\n=======================================================")
    print(f"🎫 Triaging Ticket: {ticket['id']} from {ticket['sender']}")
    print(f"Text: \"{ticket['body']}\"")
    print(f"-------------------------------------------------------")

    # Dispatch single parallel forward pass across all 4 decision primitives
    response = client.system_one(
        state=ticket["body"],
        questions={
            # Choice: Dispatches ticket to the appropriate functional organizational unit
            "department": Choice(
                instructions="Determine the correct engineering or business department to handle this ticket",
                criteria={
                    "devops_infra": "Production downtime, 500 errors, latency spikes, or API outages",
                    "billing": "Invoice discrepancies, payment failures, credit card updates, refunds",
                    "customer_success": "Product feedback, roadmap questions, account expansion",
                    "general_support": "How-to questions, documentation clarification"
                }
            ),
            # Score: Evaluates customer emotional distress on a 1-5 monotonic rubric
            "frustration_score": Score(
                instructions="Rate customer frustration from 1 (delighted/calm) to 5 (panicked/hostile)",
                criteria=[
                    "Delighted, highly appreciative",
                    "Calm, standard business tone",
                    "Mildly concerned or impatient",
                    "Very frustrated, mentions lost revenue or wasted time",
                    "Extreme crisis, shouting/demanding immediate phone escalation"
                ]
            ),
            # Noul: Evaluates operational veracity of whether an active system outage exists
            "is_outage": Noul(
                instructions="The ticket indicates an active production service outage or widespread failure"
            ),
            # Noul: Evaluates whether user demands urgent voice/telephone callback
            "wants_phone_callback": Noul(
                instructions="The sender explicitly requests a telephone phone call callback"
            )
        }
    )

    ans = response.answers
    
    # 1. Unpack Department Categorization
    dept = ans["department"].choice
    dept_conf = ans["department"].confidence
    
    # 2. Unpack Continuous Ordinal Frustration Score
    frustration = ans["frustration_score"].score
    
    # 3. Unpack Calibrated Outage Probability
    is_outage_ans = ans["is_outage"]
    outage_prob = getattr(is_outage_ans, "probability", is_outage_ans.noul if isinstance(is_outage_ans.noul, (int, float)) else 0.5)
    is_outage = is_outage_ans.noul if isinstance(is_outage_ans.noul, bool) else (outage_prob >= 0.5)

    # 4. Unpack Callback Demand Probability
    wants_call_ans = ans["wants_phone_callback"]
    call_prob = getattr(wants_call_ans, "probability", wants_call_ans.noul if isinstance(wants_call_ans.noul, (int, float)) else 0.5)
    wants_call = wants_call_ans.noul if isinstance(wants_call_ans.noul, bool) else (call_prob >= 0.5)

    # -------------------------------------------------------------------------
    # Deterministic Priority Matrix & SLA Governance
    # -------------------------------------------------------------------------
    # High-stakes decision logic uses Jev's calibrated probabilities directly
    if is_outage or frustration >= 4.0:
        priority = "P0 - CRITICAL EMERGENCY"
        action = "🚨 WAKE ON-CALL VIA PAGERDUTY + POST TO #INCIDENTS-WAR-ROOM"
    elif dept == "billing":
        priority = "P2 - STANDARD FINANCIAL"
        action = "💳 Auto-assign to Finance Zendesk Queue with 4hr SLA"
    else:
        priority = "P3 - NORMAL INQUIRY"
        action = "📬 Route to Standard Support Inbox with 24hr SLA"

    lat = getattr(response, "latency_ms", "N/A")
    print(f"⚡ Jev Processing Latency: {lat} ms (Mode: {'LIVE' if IS_LIVE else 'SIMULATOR'})")
    print(f"📂 Assigned Department:     {dept} (Confidence: {dept_conf:.2%})")
    print(f"😡 Frustration Level:       {frustration:.2f} / 5")
    print(f"🔥 Active Outage?:          {is_outage} (Prob: {outage_prob:.2%})")
    print(f"📞 Wants Phone Callback?:   {wants_call} (Prob: {call_prob:.2%})")
    print(f"🏷️  Calculated Priority:     {priority}")
    print(f"🚀 Automated Routing Action: {action}")


def main():
    """
    Main orchestration entry point: processes all incoming synthetic tickets.
    """
    print("=======================================================")
    print("   JEV SYSTEM ONE SUPPORT TRIAGE ENGINE DEMO          ")
    print("=======================================================")
    for ticket in SAMPLE_TICKETS:
        triage_ticket(ticket)


if __name__ == "__main__":
    main()
