# Module 2.3: REST API Specification

If you are using languages without an official SDK (such as Go, Rust, Java, C#, or Elixir), or if you are integrating via an API proxy or custom gateway, you can interact directly with the TypeSafe AI REST endpoint.

---

## 🌐 Endpoint Details

- **Method:** `POST`
- **URL:** `https://api.typesafe.ai/v1/systemone`
- **Authentication:** Bearer Token via `Authorization` header

---

## 📋 Headers

```http
POST /v1/systemone HTTP/1.1
Host: api.typesafe.ai
Authorization: Bearer YOUR_TYPESAFE_API_KEY
Content-Type: application/json
Accept: application/json
```

---

## 📥 Request Body Schema

```json
{
  "state": "String containing the context, document, log, or conversation to evaluate",
  "questions": {
    "<question_key>": {
      "type": "choice | score | noul",
      "instructions": "Evaluation instruction string",
      "criteria": { ... } // Required for choice and score
    }
  },
  "options": {
    "temperature": 0.0,
    "confidence_threshold": 0.5
  }
}
```

### Detailed Field Definitions

| Field | Type | Description |
| :--- | :--- | :--- |
| `state` | `string` | The text context to evaluate (supports up to 64k tokens in early access). |
| `questions` | `object` | Map of question identifier strings to question definition objects. |
| `questions[key].type` | `string` | Must be `"choice"`, `"score"`, or `"noul"`. |
| `questions[key].instructions`| `string` | The exact instruction to evaluate. |
| `questions[key].criteria` | `object` or `array` | For `"choice"`: key-value map of label-to-description.<br>For `"score"`: array of ordered rubric levels. |

---

## 📤 Response Body Schema

```json
{
  "id": "sys1_req_01j7b9k2x1y8z9w3v4u5",
  "created_at": 1790428800,
  "model": "jev-system-one-v1",
  "usage": {
    "input_tokens": 142,
    "output_tokens": 0,
    "total_cost_usd": 0.000005964
  },
  "latency_ms": 118,
  "answers": {
    "urgency": {
      "type": "score",
      "score": 4,
      "confidence": 0.912,
      "expected_val": 4.18
    },
    "routing": {
      "type": "choice",
      "choice": "engineering",
      "confidence": 0.965,
      "distribution": {
        "engineering": 0.965,
        "billing": 0.021,
        "support": 0.014
      }
    },
    "is_escalation": {
      "type": "noul",
      "noul": true,
      "probability": 0.948,
      "confidence": 0.896
    }
  }
}
```

---

## 💻 `curl` Example

```bash
curl -X POST https://api.typesafe.ai/v1/systemone \
  -H "Authorization: Bearer $TYPESAFE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "state": "The user entered an expired coupon code: SUMMER2024.",
    "questions": {
      "issue_type": {
        "type": "choice",
        "instructions": "Classify the promotional issue",
        "criteria": {
          "expired": "Coupon code date validity has passed",
          "invalid": "Coupon code never existed in the database",
          "ineligible": "User does not meet cart minimum requirements"
        }
      },
      "allow_override": {
        "type": "noul",
        "instructions": "Allow customer support representative to manually apply a discount"
      }
    }
  }'
```

---

## ⚡ Error Codes & HTTP Statuses

| HTTP Status | Error Code | Description | Recommended Action |
| :--- | :--- | :--- | :--- |
| `200 OK` | - | Successful evaluation | Process response. |
| `400 Bad Request` | `invalid_criteria` | Criteria missing or malformed | Inspect question definition structure. |
| `401 Unauthorized` | `invalid_api_key` | Missing or invalid Bearer token | Check `TYPESAFE_API_KEY`. |
| `422 Unprocessable` | `state_too_long` | State exceeds context window | Truncate or chunk state input. |
| `429 Too Many Req` | `rate_limit_exceeded`| Concurrency/QPS limit hit | Implement exponential backoff. |
| `500 Server Error` | `internal_error` | TypeSafe AI infrastructure glitch | Fallback to secondary decision path. |
