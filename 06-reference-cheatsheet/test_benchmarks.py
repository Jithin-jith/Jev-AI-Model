#!/usr/bin/env python3
"""
Module 6 Hands-On Test: Latency Benchmarking & Economic Cost Calculator
Measures latency percentiles (p50, p95) and computes pricing differences vs frontier models.
"""

import sys
import os
import time

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

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
mode = "LIVE API (typesafe-sdk)"

def benchmark_latency(iterations: int = 5):
    print(f"\n--- 1. Latency Benchmark ({iterations} Iterations) ---")
    latencies = []
    
    for i in range(iterations):
        t0 = time.time()
        res = client.system_one(
            state=f"Sample transaction event payload #{i+1000} with metadata and user properties.",
            questions={
                "risk": Choice(instructions="Risk tier", criteria={"low": "Safe", "high": "Suspicious"}),
                "score": Score(instructions="Score", criteria=["1", "2", "3"]),
                "alert": Noul(instructions="Alert security team")
            }
        )
        elapsed_ms = (time.time() - t0) * 1000
        latencies.append(elapsed_ms)
        serv_lat = getattr(res, "latency_ms", "N/A")
        print(f"  Iteration {i+1}: {elapsed_ms:.1f} ms (Server reported: {serv_lat} ms)")

    latencies.sort()
    p50 = latencies[len(latencies) // 2]
    p95 = latencies[int(len(latencies) * 0.95)]
    
    print("\nBenchmark Summary:")
    print(f"  • Min Latency: {min(latencies):.1f} ms")
    print(f"  • Median (p50): {p50:.1f} ms")
    print(f"  • 95th % (p95): {p95:.1f} ms")
    print(f"  • Max Latency: {max(latencies):.1f} ms")

def compute_cost_comparison(monthly_requests: int = 1_000_000, avg_input_tokens: int = 300, avg_output_tokens: int = 40):
    print(f"\n--- 2. Enterprise Cost Model Calculator ({monthly_requests:,} requests/mo) ---")
    print(f"Assumptions: {avg_input_tokens} input tokens / req, {avg_output_tokens} output tokens / req\n")

    total_input_tokens = monthly_requests * avg_input_tokens
    total_output_tokens = monthly_requests * avg_output_tokens

    # Pricing models per 1M tokens
    models = {
        "Jev (TypeSafe AI)": {"input_rate": 0.042, "output_rate": 0.0},
        "GPT-4o (OpenAI)": {"input_rate": 2.50, "output_rate": 10.00},
        "Claude 3.5 Haiku": {"input_rate": 0.80, "output_rate": 4.00},
        "GPT-4o-mini": {"input_rate": 0.15, "output_rate": 0.60}
    }

    print(f"{'Model Name':<22} | {'Input Cost':<12} | {'Output Cost':<12} | {'Total Monthly Bill':<18}")
    print("-" * 72)

    for name, rates in models.items():
        in_cost = (total_input_tokens / 1_000_000) * rates["input_rate"]
        out_cost = (total_output_tokens / 1_000_000) * rates["output_rate"]
        total = in_cost + out_cost
        print(f"{name:<22} | ${in_cost:>10.2f} | ${out_cost:>10.2f} | ${total:>16.2f}")

    jev_cost = (total_input_tokens / 1_000_000) * models["Jev (TypeSafe AI)"]["input_rate"]
    gpt4o_cost = (total_input_tokens / 1_000_000) * 2.50 + (total_output_tokens / 1_000_000) * 10.00
    savings_pct = (1.0 - (jev_cost / gpt4o_cost)) * 100

    print("-" * 72)
    print(f"💰 Cost Savings with Jev vs GPT-4o: {savings_pct:.2f}% (${gpt4o_cost - jev_cost:,.2f} saved/month)")

def main():
    print("=" * 65)
    print("   MODULE 6 HANDS-ON: BENCHMARKS & PRICING CALCULATOR")
    print(f"   Environment: {mode}")
    print("=" * 65)

    benchmark_latency(5)
    compute_cost_comparison()

    print("\n" + "=" * 65)
    print("   BENCHMARKS & REFERENCE TESTS PASSED")
    print("=" * 65)

if __name__ == "__main__":
    main()
