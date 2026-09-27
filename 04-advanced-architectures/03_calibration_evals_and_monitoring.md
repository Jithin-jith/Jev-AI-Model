# Module 4.3: Calibration Evals, Brier Score & Observability

To run Jev in high-stakes production systems (such as medical triage, financial fraud, or automated refunds), you must evaluate and monitor its **statistical calibration**.

---

## 🎯 Accuracy vs. Statistical Calibration

Most machine learning evaluations look only at **accuracy** (did the model pick the correct class?). However, in automated software pipelines, accuracy alone is insufficient:

- **Accuracy:** *"Is the top prediction correct?"*
- **Calibration:** *"When the model claims 80% confidence, does the event actually occur 80% of the time?"*

### Why Traditional LLMs Are Uncalibrated
Standard frontier LLMs (GPT-4, Claude) trained via RLHF or DPO are tuned for human preference. This incentivizes models to sound persuasive and authoritative even when uncertain, creating **severe overconfidence**. An LLM assigning 90% confidence to an output might only be correct 65%–75% of the time. 

In automated backend microservices, uncalibrated probabilities make hard decision gating unsafe. Jev overcomes this using **RLCD (Reinforcement Learning for Calibrated Decisions)**.

---

## 📐 Mathematical Foundations: The Calibration Condition

A model is **perfectly calibrated** if, for all probability values $p \in [0, 1]$, events predicted with confidence $p$ occur with frequency $p$:

$$P(Y = 1 \mid \hat{P} = p) = p, \quad \forall p \in [0, 1]$$

### Detailed Notation Breakdown:
| Notation | Meaning | Range / Type |
| :--- | :--- | :--- |
| $Y$ | The true binary ground truth outcome (1 if true/occurred, 0 if false/did not occur). | $Y \in \{0, 1\}$ |
| $\hat{P}$ | The model's predicted probability for the event. | $\hat{P} \in [0.0, 1.0]$ |
| $p$ | A specific probability value being evaluated. | $p \in [0.0, 1.0]$ |
| $\mid \hat{P} = p$ | Conditional filter: "Restricting evaluation only to instances where predicted confidence was exactly $p$". | Condition |
| $P(Y = 1 \mid \dots)$ | The empirical (real-world) probability that the event actually occurred within that filtered set. | Probability $[0.0, 1.0]$ |

### Concrete Example:
If Jev evaluates **1,000 incident reports** and assigns an **80% probability** ($p = 0.80$) to `"requires_postmortem"`:
- **Perfect Calibration:** Exactly **800** of those 1,000 incidents genuinely require a postmortem.
- **Overconfident Model:** Only **550** required a postmortem (Actual probability is $0.55$, but model claimed $0.80$).
- **Underconfident Model:** **950** required a postmortem (Actual probability is $0.95$, but model was overly cautious at $0.80$).

---

## 📉 1. Brier Score ($\text{BS}$)

The Brier Score measures the **Mean Squared Error (MSE)** of probabilistic predictions:

$$\text{BS} = \frac{1}{N} \sum_{t=1}^N (f_t - o_t)^2$$

### Notation Breakdown:
- $N$: Total number of evaluated sample predictions.
- $t$: The index of an individual prediction ($t = 1, 2, \dots, N$).
- $f_t$: The forecast / predicted probability emitted by Jev for sample $t$ (`answer.probability` or `answer.noul`).
- $o_t \in \{0, 1\}$: The actual observed binary ground truth outcome.
- $(f_t - o_t)^2$: The squared penalty for the deviation between prediction and reality.

### Score Interpretation & Baselines:
- **Range:** $0.0 \le \text{BS} \le 1.0$ (**Lower is better**).
- $\text{BS} = 0.0$: **Perfect prediction** (model outputs $1.0$ for true events and $0.0$ for false events).
- $\text{BS} = 0.25$: **Uninformative baseline**. A model predicting $0.50$ for every event where the base rate is 50% yields $(0.5 - 1)^2 = 0.25$ and $(0.5 - 0)^2 = 0.25$.
- $\text{BS} > 0.25$: **Harmful prediction** (worse than random guessing; placing high confidence in incorrect outcomes).
- **Benchmark:** $\text{BS} < 0.08$ is considered excellent in production.

### Step-by-Step Numerical Example:
Suppose Jev evaluates 4 customer inquiries for automated refund eligibility:

| Query ($t$) | Model Forecast ($f_t$) | Ground Truth ($o_t$) | Calculation $(f_t - o_t)^2$ | Squared Error |
| :--- | :--- | :--- | :--- | :--- |
| 1 | `0.90` | `1` (Eligible) | $(0.90 - 1.0)^2 = (-0.10)^2$ | `0.01` |
| 2 | `0.80` | `1` (Eligible) | $(0.80 - 1.0)^2 = (-0.20)^2$ | `0.04` |
| 3 | `0.30` | `0` (Ineligible) | $(0.30 - 0.0)^2 = (0.30)^2$ | `0.09` |
| 4 | `0.10` | `0` (Ineligible) | $(0.10 - 0.0)^2 = (0.10)^2$ | `0.01` |

$$\text{BS} = \frac{0.01 + 0.04 + 0.09 + 0.01}{4} = \frac{0.15}{4} = \mathbf{0.0375}$$

---

## 📊 2. Expected Calibration Error ($\text{ECE}$)

While Brier score conflates accuracy and calibration into a single number, **ECE isolates calibration error**. It partitions predictions into $M$ confidence bins and computes the weighted average gap between confidence and accuracy:

$$\text{ECE} = \sum_{m=1}^M \frac{|B_m|}{N} \left| \text{acc}(B_m) - \text{conf}(B_m) \right|$$

### Notation Breakdown:
- $M$: Number of discrete confidence bins (typically $M = 10$, dividing probabilities into intervals of width $0.10$: $[0.0, 0.1), [0.1, 0.2), \dots, [0.9, 1.0]$).
- $m$: Index of the current bin ($m = 1, 2, \dots, M$).
- $B_m$: The set of predictions whose estimated confidence falls within bin $m$.
- $|B_m|$: The number of samples inside bin $m$.
- $N$: Total number of samples across all bins.
- $\frac{|B_m|}{N}$: The **weight** of bin $m$ (bins with more traffic carry more influence).
- $\text{conf}(B_m)$: The **average predicted confidence** of samples in bin $m$:
  $$\text{conf}(B_m) = \frac{1}{|B_m|} \sum_{i \in B_m} \hat{p}_i$$
- $\text{acc}(B_m)$: The **empirical accuracy** (proportion of positive outcomes) in bin $m$:
  $$\text{acc}(B_m) = \frac{1}{|B_m|} \sum_{i \in B_m} y_i$$
- $|\text{acc}(B_m) - \text{conf}(B_m)|$: The **calibration gap** for bin $m$.

### Step-by-Step Numerical Example:
Consider $N = 10$ samples binned into $M = 2$ bins:
- **Bin 1 ($[0.0, 0.5)$):** 4 samples
- **Bin 2 ($[0.5, 1.0]$):** 6 samples

#### Bin 1 Calculation:
- Predictions: `[0.10, 0.20, 0.20, 0.30]`
- Ground truths: `[0, 0, 0, 1]`
- $\text{conf}(B_1) = \frac{0.10 + 0.20 + 0.20 + 0.30}{4} = \mathbf{0.20}$ (20% average confidence)
- $\text{acc}(B_1) = \frac{0 + 0 + 0 + 1}{4} = \mathbf{0.25}$ (25% empirical accuracy)
- Calibration gap: $|0.25 - 0.20| = \mathbf{0.05}$

#### Bin 2 Calculation:
- Predictions: `[0.80, 0.85, 0.90, 0.90, 0.95, 1.00]`
- Ground truths: `[1, 1, 1, 1, 0, 1]`
- $\text{conf}(B_2) = \frac{0.80 + 0.85 + 0.90 + 0.90 + 0.95 + 1.00}{6} = \frac{5.40}{6} = \mathbf{0.90}$ (90% average confidence)
- $\text{acc}(B_2) = \frac{1 + 1 + 1 + 1 + 0 + 1}{6} = \frac{5}{6} \approx \mathbf{0.833}$ (83.3% empirical accuracy)
- Calibration gap: $|0.833 - 0.900| = \mathbf{0.067}$

#### Weighted ECE:
$$\text{ECE} = \left(\frac{4}{10} \times 0.05\right) + \left(\frac{6}{10} \times 0.067\right) = 0.020 + 0.0402 = \mathbf{0.0602}$$

---

## 📈 Visualizing Calibration: Reliability Diagrams

A **Reliability Diagram** plots $\text{conf}(B_m)$ on the X-axis against $\text{acc}(B_m)$ on the Y-axis:

```
Actual Accuracy
 1.00 ┤                                           ▲ (0.90, 0.90)  [Perfect Calibration]
      │                                       ┌───┘
 0.75 ┤                                  ┌────┘
      │                             ┌────┘   ◄── Perfect Line (y = x)
 0.50 ┤                        ┌────┘
      │                   ┌────┘
 0.25 ┤              ┌────┘
      │         ┌────┘
 0.00 ┴─────────┴─────────┴─────────┴─────────┴─────────►
     0.00      0.25      0.50      0.75      1.00   Predicted Confidence
```

- **On the diagonal ($y = x$):** Perfect calibration.
- **Below the diagonal ($y < x$):** **Overconfidence** (model predicted 90% confidence, but true accuracy was only 60%).
- **Above the diagonal ($y > x$):** **Underconfidence** (model predicted 60% confidence, but true accuracy was 85%).

---

## ⚖️ Architecture Comparison: RLCD vs. Standard LLM RLHF

| Metric / Property | Standard Frontier LLMs (RLHF / Softmax) | Jev with RLCD (Proper Scoring Rules) |
| :--- | :--- | :--- |
| **Training Objective** | Human preference, persuasiveness | Strictly proper scoring rules (Brier + NLL loss) |
| **Typical ECE** | **$0.18 - 0.28$** (Severely uncalibrated) | **$< 0.04$** (Highly calibrated) |
| **Brier Score** | $\approx 0.15 - 0.22$ | **$< 0.06$** |
| **Automated Microservice Thresholds** | Unsafe; requires human review | Safe for zero-human-in-the-loop execution |

---

## 💻 Python Calibration Evaluation Script

```python
import numpy as np

def compute_calibration_metrics(predictions: list[float], ground_truths: list[int], num_bins: int = 10):
    """
    Evaluates Brier Score and Expected Calibration Error (ECE).
    """
    preds = np.array(predictions)
    truths = np.array(ground_truths)

    # 1. Brier Score
    brier_score = np.mean((preds - truths) ** 2)

    # 2. ECE Calculation
    bin_limits = np.linspace(0.0, 1.0, num_bins + 1)
    ece = 0.0

    print("--- CALIBRATION RELIABILITY TABLE ---")
    print(f"{'Bin Range':<15} | {'Count':<6} | {'Avg Confidence':<15} | {'Actual Accuracy':<15}")
    print("-" * 60)

    for i in range(num_bins):
        bin_low = bin_limits[i]
        bin_high = bin_limits[i + 1]
        
        mask = (preds >= bin_low) & (preds < bin_high) if i < num_bins - 1 else (preds >= bin_low) & (preds <= bin_high)
        bin_count = np.sum(mask)

        if bin_count > 0:
            avg_conf = np.mean(preds[mask])
            actual_acc = np.mean(truths[mask])
            abs_diff = np.abs(avg_conf - actual_acc)
            ece += (bin_count / len(preds)) * abs_diff
            print(f"[{bin_low:.1f}, {bin_high:.1f})       | {bin_count:<6} | {avg_conf:<15.3f} | {actual_acc:<15.3f}")

    print("-" * 60)
    print(f"Overall Brier Score: {brier_score:.4f} (Benchmark: < 0.08 is excellent)")
    print(f"Overall ECE:         {ece:.4f} (Benchmark: < 0.05 is excellent)")
    return {"brier_score": brier_score, "ece": ece}

# Test simulation
simulated_preds = [0.95, 0.92, 0.88, 0.84, 0.70, 0.65, 0.40, 0.20, 0.10, 0.05] * 20
simulated_truths = [1, 1, 1, 1, 1, 0, 0, 0, 0, 0] * 20

compute_calibration_metrics(simulated_preds, simulated_truths)
```

---

## 🔭 Observability & Monitoring Calibration Drift in Production

Over time, production data distributions drift (e.g., changes in user behavior, seasonal anomalies, novel fraud vectors). Tracking calibration requires correlating predicted confidence with actual downstream resolutions:

### 1. Tracing with Langfuse / OpenTelemetry
```python
from langfuse import Langfuse
from typesafe_sdk import TypeSafeClient

langfuse = Langfuse()
client = TypeSafeClient()

def logged_jev_decision(state: str, questions: dict, transaction_id: str):
    with langfuse.trace(name="system_one_decision", id=transaction_id) as trace:
        response = client.system_one(state=state, questions=questions)
        
        trace.generation(
            name="jev_forward_pass",
            model="jev-latest",
            usage={"input": response.usage.input_tokens, "output": response.usage.output_tokens},
            metadata={
                "answers": {
                    k: {
                        "type": v.type,
                        "value": getattr(v, "choice", getattr(v, "score", getattr(v, "noul", None))),
                        "confidence": getattr(v, "confidence", getattr(v, "noul", None))
                    }
                    for k, v in response.answers.items()
                }
            }
        )
        return response
```

### 2. Monitoring for Calibration Drift
1. **Log Every Prediction:** Record the confidence score and probability emitted by Jev.
2. **Capture Downstream Truths:** Log ground truth events when available (e.g., chargeback filed, dispute created, human supervisor overturns automated routing).
3. **Rolling Window Evals:** Schedule hourly or daily evaluations of ECE and Brier Score over a 7-day sliding window.
4. **Automated Alerting:** If ECE drifts from $< 0.04$ up to $> 0.10$, alert engineering teams to refresh criteria descriptions or update prompt criteria rubrics.
