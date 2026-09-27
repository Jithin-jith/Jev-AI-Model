# Pricing, Latency & Model Benchmarks

A comprehensive engineering reference comparing **Jev (TypeSafe AI)** with frontier autoregressive models and traditional classification models.

---

## 💰 Official Pricing Comparison

| Model | Provider | Input Cost / 1M Tokens | Output Cost / 1M Tokens | Output Cost Mechanics |
| :--- | :--- | :--- | :--- | :--- |
| **Jev (System One)** | **TypeSafe AI** | **$0.042** | **$0.00 (FREE)** | Non-autoregressive parallel forward pass |
| **GPT-4o** | OpenAI | $2.50 | $10.00 | Autoregressive JSON token generation |
| **GPT-4o-mini** | OpenAI | $0.15 | $0.60 | Autoregressive JSON token generation |
| **Claude 3.7 Sonnet** | Anthropic | $3.00 | $15.00 | Autoregressive JSON token generation |
| **Claude 3.5 Haiku** | Anthropic | $0.80 | $4.00 | Autoregressive JSON token generation |
| **Gemini 2.5 Flash** | Google | $0.075 | $0.30 | Autoregressive JSON token generation |

### Key Economic Insight:
For decision-intensive pipelines (e.g. routing 10 million events/month with 200 input tokens each):
- **GPT-4o:** ~$6,000 / month
- **Claude 3.5 Haiku:** ~$1,900 / month
- **Jev:** **~$84 / month** (95% to 98% savings)

---

## ⚡ Latency Benchmarks (p50 & p95)

Latency measured on 250-token inputs across North America edge regions:

| Model | Architecture | Median Latency (p50) | 95th Percentile (p95) |
| :--- | :--- | :--- | :--- |
| **Jev (TypeSafe AI)** | Non-Autoregressive Transformer | **85 ms** | **140 ms** |
| **Claude 3.5 Haiku** | Autoregressive (Serial Tokens) | 680 ms | 1,450 ms |
| **GPT-4o-mini** | Autoregressive (Serial Tokens) | 740 ms | 1,600 ms |
| **GPT-4o** | Autoregressive (Serial Tokens) | 1,280 ms | 2,800 ms |
| **Claude 3.7 Sonnet** | Autoregressive (Serial Tokens) | 1,900 ms | 4,200 ms |

---

## 🎯 Accuracy & Calibration Benchmarks (RLCD)

Benchmarked on enterprise decision datasets (Customer Support Routing, Fraud Screening, Policy Adherence):

| Evaluation Metric | Jev (RLCD) | Standard Frontier LLMs | Traditional DeBERTa / SetFit |
| :--- | :--- | :--- | :--- |
| **Decision Accuracy (Top-1)** | **92.4%** | 93.1% | 86.2% |
| **Expected Calibration Error (ECE)** | **< 0.038** | 0.215 (Severely overconfident) | 0.082 |
| **Brier Score** (Lower is better)| **0.061** | 0.174 | 0.119 |
| **Zero-Shot Generalization** | **High** (natural criteria) | High (prompted) | Low (requires custom fine-tuning) |
| **JSON Parse Crash Rate** | **0.0%** (Typed) | 1.2% - 3.4% (Requires retries) | 0.0% (Trained head) |

### Why Jev Wins in Production:
While a massive frontier model like GPT-4o or Claude 3.7 may achieve a tiny 0.7% edge in raw unconstrained zero-shot accuracy, its **15x higher latency**, **100x higher cost**, and **uncalibrated confidence** make it unsuitable for high-volume automated operational loops. Jev provides frontier-class accuracy at microsecond infrastructure economics.
