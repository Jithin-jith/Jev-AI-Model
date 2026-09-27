# Module 2.2: TypeScript/JavaScript SDK Quickstart (`@typesafe-ai/sdk`)

TypeSafe AI provides first-class TypeScript support with **`@typesafe-ai/sdk`**. The SDK leverages TypeScript's advanced generics to infer compile-time answer types directly from question definitions.

---

## 📦 1. Installation

Requires **Node.js 20+** or Bun / Deno:

```bash
npm install @typesafe-ai/sdk
# or
pnpm add @typesafe-ai/sdk
# or
yarn add @typesafe-ai/sdk
# or
bun add @typesafe-ai/sdk
```

---

## 🔑 2. Environment Configuration

```bash
export TYPESAFE_API_KEY="ts_live_xxxxxxxxxxxxxxxxxxxxxx"
```

---

## 🚀 3. TypeScript Example with Type Inference

```typescript
import { TypeSafeClient, choice, score, noul } from "@typesafe-ai/sdk";

// 1. Initialize client
const client = new TypeSafeClient();

// 2. Define State
const transactionLog = `
Transaction ID: tx_9948271
Amount: $4,999.00 USD
Merchant: Luxury Electronics Online
Card Country: Nigeria
IP Geolocation: Romania
Device: Tor Exit Node Browser
Cardholder Home Address: Seattle, WA, USA
`;

async function evaluateTransaction() {
  // 3. Execute systemOne request
  const response = await client.systemOne({
    state: transactionLog,
    questions: {
      risk_level: choice({
        instructions: "Determine the fraud risk category of this transaction",
        criteria: {
          low: "Legitimate user behavior matching historical footprint",
          medium: "Slight anomaly in location or amount",
          high: "Severe mismatch in geolocation, IP proxy, or velocity spikes",
          critical: "Known compromised card network or undeniable fraud markers"
        }
      }),
      fraud_score: score({
        instructions: "Rate likelihood of fraud on 1 to 5 scale",
        criteria: [
          "Definitely safe",
          "Low suspicion",
          "Moderate review recommended",
          "High fraud probability",
          "Confirmed fraud attack"
        ]
      }),
      block_immediately: noul({
        instructions: "Transaction should be blocked immediately to prevent chargeback"
      })
    }
  });

  // 4. Strongly-Typed Answer Access
  // TypeScript knows risk_level.choice can ONLY be 'low' | 'medium' | 'high' | 'critical'
  const risk = response.answers.risk_level;
  console.log(`Risk Choice: ${risk.choice}`); // Type: "low" | "medium" | "high" | "critical"
  console.log(`Confidence:  ${risk.confidence}`);

  const blockDecision = response.answers.block_immediately;
  console.log(`Block?:      ${blockDecision.noul}`);        // boolean
  console.log(`Probability: ${blockDecision.probability}`); // number (0.0 to 1.0)

  // Automated Action based on Calibrated Confidence
  if (blockDecision.probability >= 0.85) {
    console.warn("🚨 [ACTION TRIGGERED] Auto-declining transaction and freezing card.");
  } else if (blockDecision.probability >= 0.50) {
    console.log("⚠️ [ACTION TRIGGERED] Routing to manual fraud operations team.");
  } else {
    console.log("✅ [ACTION TRIGGERED] Approving transaction.");
  }
}

evaluateTransaction().catch(console.error);
```

---

## 🌐 4. Edge Runtime Compatibility (Next.js / Cloudflare / Vercel)

The TypeScript SDK is built on standard `fetch` and works seamlessly on Edge runtimes:

### Next.js App Router API Route (`app/api/triage/route.ts`):
```typescript
import { NextResponse } from "next/server";
import { TypeSafeClient, choice } from "@typesafe-ai/sdk";

export const runtime = "edge";

const client = new TypeSafeClient();

export async function POST(req: Request) {
  const { feedbackText } = await req.json();

  const response = await client.systemOne({
    state: feedbackText,
    questions: {
      sentiment: choice({
        instructions: "Customer feedback sentiment",
        criteria: {
          positive: "Happy, compliments, praise",
          neutral: "Informational or balanced comment",
          negative: "Unhappy, complaints, feature criticism"
        }
      })
    }
  });

  return NextResponse.json({
    sentiment: response.answers.sentiment.choice,
    confidence: response.answers.sentiment.confidence
  });
}
```

---

## 🎯 Summary Takeaways
- Use `@typesafe-ai/sdk` with `choice()`, `score()`, `noul()` helper functions.
- Fully compatible with Node.js, Bun, Cloudflare Workers, and Next.js Edge.
- TypeScript enforces compile-time safety on choice criteria keys.
- Next module: [Module 2.3: REST API Specification](./03_rest_api_specification.md).
