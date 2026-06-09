# Day 09 Report - Bui Minh Hieu 2A202600876

## Stage 5 - Distributed A2A System

Stage 5 runs the same multi-agent idea from Stage 4, but each agent is deployed as a separate HTTP service:

| Service | Port | Role |
|---|---:|---|
| Registry | 10000 | Stores agent endpoints and supports discovery |
| Customer Agent | 10100 | Entry point for user questions |
| Law Agent | 10101 | Legal orchestrator |
| Tax Agent | 10102 | Tax specialist |
| Compliance Agent | 10103 | Compliance specialist |

Windows run commands:

```powershell
.\.venv\Scripts\Activate.ps1
.\start_all.ps1
python test_client.py
.\stop_all.ps1
```

Request flow:

```text
test_client.py
  -> Customer Agent
  -> Registry discovers Law Agent
  -> Law Agent analyzes the legal question
  -> Registry discovers Tax/Compliance specialists if needed
  -> Tax and Compliance Agents answer through A2A
  -> Law Agent aggregates
  -> Customer Agent returns final response
```

The client now prints both A2A request latency and total client latency, so the measured value can be copied directly from terminal output.

Measured run:

```text
A2A request latency: 48.38s
Total client latency: 49.17s
```

## Stage 6 - Review Questions

**1. When should we use a single agent instead of multi-agent?**

Use a single agent when the task is narrow, the required tools are few, and there is no strong need for domain specialization. A single agent is easier to debug, cheaper to run, and has lower coordination overhead. Multi-agent becomes useful when the question naturally splits into specialist domains such as law, tax, privacy, compliance, or finance.

**2. What are the advantages of A2A compared with normal REST/gRPC?**

A2A is designed around agent concepts: agent cards, tasks, messages, artifacts, and capability discovery. REST/gRPC can transport data, but A2A provides a shared protocol for agents to describe what they can do and exchange task-oriented messages. This makes dynamic discovery and agent interoperability easier.

**3. How can we prevent infinite delegation loops?**

Use a maximum delegation depth, pass trace/context IDs through every request, record which agents have already handled the task, and stop delegation when confidence is high enough or when no new specialist is needed. The system should also return a controlled error instead of delegating forever.

**4. Why do we need a Registry service? Can we hardcode URLs?**

The Registry lets agents register capabilities and lets other agents discover them at runtime. Hardcoded URLs work for small demos, but they make the system brittle: every address change requires code changes. Registry-based discovery is more flexible and closer to production service discovery.

## Latency Improvement Proposal

Baseline Stage 5 latency is dominated by multiple LLM calls across Customer, Law, Tax, and Compliance Agents. To reduce latency:

1. Run specialist agents in parallel where possible.
2. Use a lower-latency model for routing and summarization.
3. Reduce `OPENROUTER_MAX_TOKENS` for intermediate specialist answers.
4. Cache registry discovery results inside each agent.
5. Skip specialists when routing confidence says they are unnecessary.

Implemented improvement in this submission:

- `OPENROUTER_MAX_TOKENS=384` is supported in `common/llm.py`, preventing overly large completions and avoiding credit errors from very large token requests.
- `test_client.py` measures latency so before/after comparisons can be shown.

Observed result:

```text
Before optimization: failed because the model requested more output tokens than the account could afford.
After optimization:  Stage 5 completed successfully.
A2A latency:         48.38s
Total latency:       49.17s
```
