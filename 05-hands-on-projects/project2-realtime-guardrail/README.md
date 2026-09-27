# Project 2: Real-Time Security Guardrail Proxy

A high-performance security interceptor designed for LLM applications. Before sending user input to expensive frontier models (GPT-4o, Claude 3.7, Gemini 2.5), this proxy evaluates safety in **< 85ms**.

---

## 🛡️ Vectors Screened Concurrently
1. **Adversarial Jailbreak / Prompt Injection (`is_jailbreak` - `Noul`)**
2. **Sensitive Secret / PII Exfiltration Probe (`is_secret_probe` - `Noul`)**
3. **Severe Toxicity & Harassment (`toxicity_score` - `Score`)**
4. **Out-of-Scope Off-Topic Queries (`scope_category` - `Choice`)**

---

## 🏃 Quick Run

```bash
cd f:\Projects\Jev\05-hands-on-projects\project2-realtime-guardrail
python guardrail_proxy.py
```
