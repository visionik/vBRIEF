# vBRIEF TRON Encoding Guide

**Version**: 0.5  
**Status**: Reference Implementation

## Overview

TRON (Token Reduced Object Notation) is the preferred format for vBRIEF documents in AI/agent workflows due to its token efficiency. This guide defines the standard TRON class definitions for vBRIEF v0.5 entities.

## Why TRON?

- **35-40% token reduction** vs JSON for typical vBRIEF documents
- **Lower API costs** for LLM operations
- **More context fits** in fixed-size context windows
- **Human readable** with reduced noise from repeated field names
- **Superset of JSON** - any valid JSON is valid TRON

## Core TRON Classes

### Edge

Represents a directed edge in a Plan's DAG.

```tron
class Edge: from, to, type
```

**Usage:**
```tron
edges: [
  Edge("lint", "build", "blocks"),
  Edge("test", "build", "blocks"),
  Edge("lint", "test", "informs")
]
```

**Core edge types:**
- `blocks` - Target cannot start until source completes
- `informs` - Target benefits from source context but not blocked
- `invalidates` - Source completion makes target unnecessary
- `suggests` - Weak recommendation, no hard dependency

**Custom types allowed** - e.g., `"triggers"`, `"produces"`, etc.

### PlanItem

Represents an item in a Plan, with optional nested subItems.

**Minimal:**
```tron
class PlanItem: id, title, status
```

**Extended (with common optional fields):**
```tron
class PlanItem: id, title, status, priority, dueDate
```

**Usage:**
```tron
items: [
  PlanItem("auth", "Implement authentication", "running", "high", null),
  PlanItem("api", "Build API endpoints", "pending", "medium", "2026-02-10T00:00:00Z")
]
```

**For nested items with full field specification:**
```tron
items: [
  {
    id: "setup",
    title: "Setup Phase",
    status: "running",
    subItems: [
      PlanItem("setup.deps", "Install dependencies", "completed"),
      PlanItem("setup.config", "Configure environment", "running")
    ]
  }
]
```

### Plan (implicit)

Plans use object notation rather than a class since they contain varied optional fields.

```tron
plan: {
  id: "sprint-1",
  title: "Sprint 1 Planning",
  status: "running",
  items: [...],
  edges: [...]
}
```

## Complete Examples

### Minimal Plan (Todo-like)

**TRON** (45 tokens):
```tron
class PlanItem: title, status

vBRIEFInfo: {version: "0.5"}
plan: {
  title: "Daily Tasks",
  status: "running",
  items: [
    PlanItem("Fix bug", "pending"),
    PlanItem("Review PR", "running")
  ]
}
```

**JSON equivalent** (73 tokens):
```json
{
  "vBRIEFInfo": {"version": "0.5"},
  "plan": {
    "title": "Daily Tasks",
    "status": "running",
    "items": [
      {"title": "Fix bug", "status": "pending"},
      {"title": "Review PR", "status": "running"}
    ]
  }
}
```

**Token savings: 38%**

### Structured Plan with Narratives

**TRON** (128 tokens):
```tron
class PlanItem: id, title, status

vBRIEFInfo: {version: "0.5", created: "2026-02-03T09:00:00Z"}
plan: {
  id: "api-redesign",
  title: "API Redesign: REST to GraphQL",
  status: "proposed",
  narratives: {
    Proposal: "Migrate REST API to GraphQL for better developer experience",
    Problem: "Overfetching and maintenance burden with 50+ REST endpoints",
    Risk: "Team learning curve and N+1 query optimization challenges"
  },
  items: [
    PlanItem("research", "Research Phase", "completed"),
    PlanItem("schema", "Define GraphQL Schema", "running"),
    PlanItem("implementation", "Implement Resolvers", "pending")
  ],
  tags: ["api", "graphql"]
}
```

**JSON equivalent** (198 tokens):
```json
{
  "vBRIEFInfo": {"version": "0.5", "created": "2026-02-03T09:00:00Z"},
  "plan": {
    "id": "api-redesign",
    "title": "API Redesign: REST to GraphQL",
    "status": "proposed",
    "narratives": {
      "Proposal": "Migrate REST API to GraphQL for better developer experience",
      "Problem": "Overfetching and maintenance burden with 50+ REST endpoints",
      "Risk": "Team learning curve and N+1 query optimization challenges"
    },
    "items": [
      {"id": "research", "title": "Research Phase", "status": "completed"},
      {"id": "schema", "title": "Define GraphQL Schema", "status": "running"},
      {"id": "implementation", "title": "Implement Resolvers", "status": "pending"}
    ],
    "tags": ["api", "graphql"]
  }
}
```

**Token savings: 35%**

### DAG Plan with Edges

**TRON** (162 tokens):
```tron
class Edge: from, to, type
class PlanItem: id, title, status

vBRIEFInfo: {version: "0.5"}
plan: {
  id: "build-pipeline",
  title: "CI/CD Build Pipeline",
  status: "running",
  items: [
    PlanItem("lint", "Lint code", "completed"),
    PlanItem("test", "Run tests", "running"),
    PlanItem("build", "Build artifacts", "pending"),
    PlanItem("deploy-staging", "Deploy to staging", "pending"),
    PlanItem("integration-tests", "Integration tests", "pending"),
    PlanItem("deploy-prod", "Deploy to production", "pending")
  ],
  edges: [
    Edge("lint", "build", "blocks"),
    Edge("test", "build", "blocks"),
    Edge("build", "deploy-staging", "blocks"),
    Edge("deploy-staging", "integration-tests", "blocks"),
    Edge("integration-tests", "deploy-prod", "blocks"),
    Edge("lint", "test", "informs")
  ]
}
```

**JSON equivalent** (267 tokens):
```json
{
  "vBRIEFInfo": {"version": "0.5"},
  "plan": {
    "id": "build-pipeline",
    "title": "CI/CD Build Pipeline",
    "status": "running",
    "items": [
      {"id": "lint", "title": "Lint code", "status": "completed"},
      {"id": "test", "title": "Run tests", "status": "running"},
      {"id": "build", "title": "Build artifacts", "status": "pending"},
      {"id": "deploy-staging", "title": "Deploy to staging", "status": "pending"},
      {"id": "integration-tests", "title": "Integration tests", "status": "pending"},
      {"id": "deploy-prod", "title": "Deploy to production", "status": "pending"}
    ],
    "edges": [
      {"from": "lint", "to": "build", "type": "blocks"},
      {"from": "test", "to": "build", "type": "blocks"},
      {"from": "build", "to": "deploy-staging", "type": "blocks"},
      {"from": "deploy-staging", "to": "integration-tests", "type": "blocks"},
      {"from": "integration-tests", "to": "deploy-prod", "type": "blocks"},
      {"from": "lint", "to": "test", "type": "informs"}
    ]
  }
}
```

**Token savings: 39%**

### Retrospective Plan (Playbook-style)

**TRON** (148 tokens):
```tron
class PlanItem: id, title, status

vBRIEFInfo: {version: "0.5"}
plan: {
  id: "incident-db",
  title: "Incident: Database Outage",
  status: "completed",
  narratives: {
    Outcome: "Restored service in 45 minutes, no data loss",
    Strengths: "Clear runbook, excellent team communication",
    Weaknesses: "Monitoring gaps, manual failover was slow",
    Lessons: "Automate failover, add disk space alerts at 70%"
  },
  items: [
    PlanItem("detection", "Issue Detected", "completed"),
    PlanItem("diagnosis", "Root Cause Found", "completed"),
    PlanItem("mitigation", "Immediate Fix", "completed"),
    PlanItem("resolution", "Full Resolution", "completed")
  ],
  tags: ["incident", "postmortem"]
}
```

**JSON equivalent** (233 tokens):
```json
{
  "vBRIEFInfo": {"version": "0.5"},
  "plan": {
    "id": "incident-db",
    "title": "Incident: Database Outage",
    "status": "completed",
    "narratives": {
      "Outcome": "Restored service in 45 minutes, no data loss",
      "Strengths": "Clear runbook, excellent team communication",
      "Weaknesses": "Monitoring gaps, manual failover was slow",
      "Lessons": "Automate failover, add disk space alerts at 70%"
    },
    "items": [
      {"id": "detection", "title": "Issue Detected", "status": "completed"},
      {"id": "diagnosis", "title": "Root Cause Found", "status": "completed"},
      {"id": "mitigation", "title": "Immediate Fix", "status": "completed"},
      {"id": "resolution", "title": "Full Resolution", "status": "completed"}
    ],
    "tags": ["incident", "postmortem"]
  }
}
```

**Token savings: 36%**

## Best Practices

### 1. Define Classes at Document Start

Place class definitions at the top of the document, before any data:

```tron
class Edge: from, to, type
class PlanItem: id, title, status

vBRIEFInfo: {version: "0.5"}
plan: {...}
```

### 2. Use Classes for Repeated Structures

If you have multiple items with the same structure, use a class:

**Good:**
```tron
class PlanItem: id, title, status
items: [
  PlanItem("a", "Task A", "pending"),
  PlanItem("b", "Task B", "running")
]
```

**Avoid:**
```tron
items: [
  {id: "a", title: "Task A", status: "pending"},
  {id: "b", title: "Task B", status: "running"}
]
```

### 3. Mix Object Notation for Complex Cases

Use object notation when items have varying optional fields:

```tron
class PlanItem: id, title, status

items: [
  PlanItem("simple", "Simple task", "pending"),
  {
    id: "complex",
    title: "Complex task",
    status: "running",
    priority: "high",
    dueDate: "2026-02-10T00:00:00Z",
    narrative: {
      Detail: "This task has many optional fields"
    },
    subItems: [
      PlanItem("complex.1", "Subtask 1", "completed"),
      PlanItem("complex.2", "Subtask 2", "pending")
    ]
  }
]
```

### 4. Keep Positional Arguments Consistent

Class definitions specify field order. Always use the same order:

```tron
class Edge: from, to, type

# Correct
Edge("a", "b", "blocks")

# Wrong - fields out of order
Edge("blocks", "a", "b")  # This would assign incorrectly!
```

### 5. Use null for Optional Fields

When using positional arguments but don't need a field:

```tron
class PlanItem: id, title, status, priority, dueDate

items: [
  PlanItem("a", "Task A", "pending", "high", "2026-02-10T00:00:00Z"),
  PlanItem("b", "Task B", "running", null, null)  # No priority or dueDate
]
```

## Conversion Tools

### TRON → JSON

Use TRON parsers available for your language:
- **Python**: `tron-py` (TBD - future implementation)
- **Go**: `tron-go` (TBD - future implementation)
- **TypeScript**: `tron-ts` (TBD - future implementation)

### JSON → TRON

Manual conversion or use language-specific tools. General process:

1. Identify repeated structures
2. Define classes for them
3. Replace object literals with class instantiation
4. Preserve object notation for complex/varying structures

## Token Counting

To verify token savings, use your LLM's tokenizer:

**Python example** (using tiktoken for GPT models):
```python
import tiktoken

encoder = tiktoken.encoding_for_model("gpt-4")

json_str = open("plan.vbrief.json").read()
tron_str = open("plan.vbrief.tron").read()

json_tokens = len(encoder.encode(json_str))
tron_tokens = len(encoder.encode(tron_str))

savings = (1 - tron_tokens / json_tokens) * 100
print(f"JSON: {json_tokens} tokens")
print(f"TRON: {tron_tokens} tokens")
print(f"Savings: {savings:.1f}%")
```

## Language-Specific Notes

### Python

Use Pydantic models for TRON class definitions:

```python
from pydantic import BaseModel

class Edge(BaseModel):
    from_: str  # 'from' is Python keyword, use alias
    to: str
    type: str
    
    class Config:
        alias_generator = lambda x: x.rstrip('_')
```

### Go

Use structs with TRON tags:

```go
type Edge struct {
    From string `tron:"from"`
    To   string `tron:"to"`
    Type string `tron:"type"`
}
```

### TypeScript

Use interfaces with TRON decorators:

```typescript
interface Edge {
  from: string;
  to: string;
  type: string;
}
```

## References

- TRON Specification: https://tron-format.github.io/
- TRON vs JSON comparison: https://www.piotr-sikora.com/blog/2025-12-05-toon-tron-csv-yaml-json-format-comparison
- vBRIEF v0.5 Specification: See SPECIFICATION.md

## Future: Data Flow Extension

When data flow edges are added (future extension), expect:

```tron
class DataFlowEdge: from, to, type, mapping

edges: [
  DataFlowEdge("analyze", "report", "dataFlow", {"output.result": "input.data"})
]
```

This will enable full prompt-graph capabilities while maintaining token efficiency.
