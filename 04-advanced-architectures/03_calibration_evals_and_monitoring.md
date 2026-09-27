# Module 4.3: Calibration Evals, Brier Score & Observability

To run Jev in high-stakes production systems (such as medical triage, financial fraud, or automated refunds), you must evaluate and monitor its **statistical calibration**.

---

## 📐 Mathematical Foundations: Calibration & Brier Score

A model is **perfectly calibrated** if, for all probability values $p \in [0, 1]$, events predicted with confidence $p$ occur with frequency $p$:

$$P(Y = 1 \mid \hat{P} = p) = p$$

### 1. Brier Score
The Brier Score measures the mean squared error of probabilistic predictions:

$$\text{BS} = \frac{1}{N} \sum_{t=1}^N (f_t - o_t)^2$$

Where:
- $f_t$ is the predicted probability from Jev (`answer.probability`).
- $o_t \in \{0, 1\}$ is the actual ground truth outcome.
- **Lower is better:** A score of $0.0$ is perfect; $0.25$ is equivalent to uninformative coin tossing.

### 2. Expected Calibration Error (ECE)
ECE bins predictions into $M$ confidence intervals and computes the weighted average difference between accuracy and confidence:

$$\text{ECE} = \sum_{m=1}^M \frac{|B_m|}{N} \left| \text{acc}(B_m) - \text{conf}(B_m) \right|$$

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

## 🔭 Observability & Tracing with Langfuse / Bifrost

You can track Jev decisions in real-time alongside your LLM calls using OpenTelemetry or Langfuse:

```python
from langfuse import Langfuse

langfuse = Langfuse()

def logged_jev_decision(state: str, questions: dict):
    with langfuse.trace(name="system_one_decision") as trace:
        response = client.system_one(state=state, questions=questions)
        
        # Log decision metadata
        trace.generation(
            name="jev_forward_pass",
            model="jev-system-one-v1",
            usage={"input": response.usage.input_tokens, "output": 0},
            metadata={
                "latency_ms": response.latency_ms,
                "answers": {k: v.to_dict() for k, v in response.answers.items()}
            }
        )
        return response
```

By logging Jev's confidence alongside ground-truth user feedback (e.g. user overturned an automated decision), you can monitor for calibration drift over time.
