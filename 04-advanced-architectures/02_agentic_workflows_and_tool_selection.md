# Module 4.2: Agentic Workflows & Tool Selection

In autonomous agent architectures (like LangChain, AutoGen, CrewAI, or bespoke agent loops), the biggest bottleneck is **Tool Selection Latency**.

When an agent needs to choose a tool from a toolset of 20 functions, traditional agents pass all 20 JSON schemas to an LLM, prompting: *"Which tool should I use next?"*
- **Problem:** Every single decision takes 1.5 to 3 seconds and costs hundreds of input/output tokens. A 5-step agent loop takes 15 seconds!

With Jev, tool selection becomes a **sub-100ms `Choice` primitive**.

---

## ⚡ The Jev Fast Agent Dispatcher

```
Agent State (Conversation History + Current Objective)
                        │
                        ▼
       ┌─────────────────────────────────┐
       │   Jev Dispatcher: Choice (<90ms)│
       │   (Selects from 50 tools)       │
       └────────────────┬────────────────┘
                        │
       ┌────────────────┴────────────────┐
       ▼                                 ▼
[ Deterministic Tool Call ]      [ Reasoning Required / Ambiguity ]
Direct Python function execution └──► Frontier LLM for ReAct loop
```

---

## 💻 Python Agent Dispatcher Implementation

```python
from typesafe_sdk import TypeSafeClient, Choice, Noul

client = TypeSafeClient()

AGENT_TOOLS = {
    "search_knowledgebase": "Search internal company docs for policies, guides, and manuals",
    "query_sql_database": "Retrieve structured customer, billing, or inventory records from PostgreSQL",
    "send_email": "Dispatch transactional or notification email to a verified user",
    "restart_server": "Trigger an automated reboot of a staging or dev VM",
    "escalate_to_human": "Route the ticket or issue to human engineer",
    "finish_task": "Goal has been completely fulfilled, no further action needed"
}

def agent_dispatch_step(conversation_context: str) -> dict:
    """
    Selects the next action for an autonomous agent in <100ms.
    """
    response = client.system_one(
        state=conversation_context,
        questions={
            "next_tool": Choice(
                instructions="Select the next optimal tool to advance the user's goal",
                criteria=AGENT_TOOLS
            ),
            "is_goal_satisfied": Noul(
                instructions="The user's goal has been completely achieved and answered"
            )
        }
    )

    next_tool = response.answers["next_tool"].choice
    confidence = response.answers["next_tool"].confidence
    is_finished = response.answers["is_goal_satisfied"].noul

    return {
        "tool": next_tool,
        "confidence": confidence,
        "is_finished": is_finished,
        "latency_ms": response.latency_ms
    }

# Example Context
context = """
User: "Can you tell me how many active subscriptions we have in Europe right now?"
Agent: "I will check the subscriber database."
"""

action = agent_dispatch_step(context)
print(f"Selected Tool: {action['tool']} (Confidence: {action['confidence']:.2f}, Latency: {action['latency_ms']}ms)")
# -> Selected Tool: query_sql_database (Confidence: 0.96, Latency: 92ms)
```

---

## 🚀 Accelerating Multi-Agent Systems
By using Jev for routing between agents (e.g. `CoderAgent`, `TesterAgent`, `ReviewerAgent`), the multi-agent orchestration overhead drops from seconds to milliseconds.
