# Project 1: Enterprise Support Ticket Triage Engine

An enterprise customer support ticket classifier that processes incoming customer tickets in **< 100ms** to:
1. Classify ticket into departmental queues (`Choice`)
2. Score customer agitation and frustration on a 1-5 scale (`Score`)
3. Detect urgent SLA breach indicators (`Noul`)
4. Detect if customer is requesting a phone call callback (`Noul`)
5. Route ticket according to calibrated confidence thresholds

---

## 🏃 Quick Run

```bash
cd f:\Projects\Jev\05-hands-on-projects\project1-support-triage
python triage_engine.py
```

*(Note: Automatically uses the offline Jev simulator if no `TYPESAFE_API_KEY` is detected, or connects to the live API if configured!)*

---

## 🏗️ Architecture

```
Incoming Customer Ticket
          │
          ▼
   [ Jev System One ] (70 - 100ms)
          │
  ┌───────┼──────────────────────────────┐
  ▼       ▼                              ▼
Choice  Score                          Noul
(Dept)  (Frustration)                  (Urgent / Callback)
  │       │                              │
  └───────┴──────────────┬───────────────┘
                         │
           Routing & Priority Matrix
                         │
     ┌───────────────────┼───────────────────┐
     ▼                   ▼                   ▼
 [ Tier 1: P0 Critical ] [ Tier 2: Standard ] [ Tier 3: Low ]
 Slack Alert + Phone     Zendesk Routing      Queue Triage
```
