# vBRIEF v0.5 Reference Guide

> **New to vBRIEF?** Start with [docs/getting-started.md](docs/getting-started.md) for a hands-on tutorial.  
> For the formal specification, see [vbrief-spec-0.5.md](vbrief-spec-0.5.md).

This guide is a cookbook of patterns and recipes for common vBRIEF use cases.

---

## Use Cases

### Simple Task List

```json
{
  "vBRIEFInfo": { "version": "0.5" },
  "plan": {
    "title": "Sprint Tasks",
    "status": "running",
    "items": [
      { "title": "Implement login endpoint", "status": "completed", "priority": "high" },
      { "title": "Write unit tests", "status": "running", "priority": "high" },
      { "title": "Update documentation", "status": "pending", "dueDate": "2026-02-10T00:00:00Z" }
    ],
    "tags": ["sprint-1", "backend"]
  }
}
```

### Structured Planning with Narratives

```json
{
  "vBRIEFInfo": { "version": "0.5" },
  "plan": {
    "id": "api-migration",
    "title": "API Migration to GraphQL",
    "status": "proposed",
    "narratives": {
      "Proposal": "Migrate REST API to GraphQL for better DX",
      "Problem": "Overfetching, multiple round-trips, maintenance burden",
      "Constraint": "Must maintain backward compatibility during migration",
      "Alternative": "REST with JSON:API, but lacks type safety",
      "Risk": "Team learning curve, N+1 query optimization"
    },
    "items": [
      { "id": "research", "title": "Research & POC", "status": "completed" },
      { "id": "schema", "title": "Define GraphQL Schema", "status": "running" },
      { "id": "resolvers", "title": "Implement Resolvers", "status": "pending" }
    ]
  }
}
```

### Incident Retrospective

```json
{
  "vBRIEFInfo": { "version": "0.5" },
  "plan": {
    "id": "incident-2026-02-02",
    "title": "Database Outage Postmortem",
    "status": "completed",
    "narratives": {
      "Outcome": "Service restored in 45 minutes, no data loss. 15% users affected.",
      "Strengths": "Clear runbook enabled fast diagnosis. Team communication excellent.",
      "Weaknesses": "Monitoring missed disk space issue. Manual failover took 20 min.",
      "Lessons": "1. Automate failover. 2. Add canary queries. 3. Disk alerts at 70%."
    },
    "items": [
      {
        "id": "detect", "title": "Issue Detected", "status": "completed",
        "completed": "2026-02-02T14:05:00Z",
        "narrative": { "Action": "Production alert: API timeouts" }
      },
      {
        "id": "diagnose", "title": "Root Cause Found", "status": "completed",
        "completed": "2026-02-02T14:15:00Z",
        "narrative": { "Finding": "DB disk at 100%, writes failing" }
      },
      {
        "id": "resolve", "title": "Full Resolution", "status": "completed",
        "completed": "2026-02-02T14:50:00Z",
        "narrative": { "Action": "Scaled volume, verified health" }
      }
    ]
  }
}
```

### DAG Workflow

```json
{
  "vBRIEFInfo": { "version": "0.5" },
  "plan": {
    "id": "ci-pipeline",
    "title": "CI Pipeline",
    "status": "running",
    "items": [
      { "id": "lint", "title": "Lint Code", "status": "completed" },
      { "id": "test", "title": "Run Tests", "status": "running" },
      { "id": "build", "title": "Build Artifacts", "status": "pending" },
      { "id": "deploy-stage", "title": "Deploy to Staging", "status": "pending" },
      { "id": "deploy-prod", "title": "Deploy to Production", "status": "pending" }
    ],
    "edges": [
      { "from": "lint", "to": "build", "type": "blocks" },
      { "from": "test", "to": "build", "type": "blocks" },
      { "from": "build", "to": "deploy-stage", "type": "blocks" },
      { "from": "deploy-stage", "to": "deploy-prod", "type": "blocks" }
    ]
  }
}
```

### Technical RFC

```json
{
  "vBRIEFInfo": { "version": "0.5" },
  "plan": {
    "title": "RFC: Microservices Architecture",
    "status": "proposed",
    "narratives": {
      "Proposal": "Split monolith into microservices",
      "Problem": "Monolith is hard to scale and deploy",
      "Alternative": "Modular monolith with clear boundaries",
      "Risk": "Increased operational complexity",
      "Test": "Pilot with user service, measure latency"
    },
    "items": [
      { "title": "Phase 1: Extract User Service", "status": "proposed" },
      { "title": "Phase 2: Extract Product Service", "status": "draft" }
    ]
  }
}
```

### Release Checklist with Dependencies

```json
{
  "vBRIEFInfo": { "version": "0.5" },
  "plan": {
    "title": "v2.0 Release",
    "status": "running",
    "items": [
      { "id": "freeze", "title": "Code freeze", "status": "completed" },
      { "id": "regression", "title": "Regression tests", "status": "completed" },
      { "id": "staging", "title": "Deploy to staging", "status": "pending" },
      { "id": "smoke", "title": "Smoke tests", "status": "pending" },
      { "id": "prod", "title": "Deploy to production", "status": "pending" }
    ],
    "edges": [
      { "from": "freeze", "to": "regression", "type": "blocks" },
      { "from": "regression", "to": "staging", "type": "blocks" },
      { "from": "staging", "to": "smoke", "type": "blocks" },
      { "from": "smoke", "to": "prod", "type": "blocks" }
    ]
  }
}
```

---

## Best Practices

### Start Simple, Add Complexity

Begin with a minimal plan (title, status, items). Add narratives when you need context. Add edges when you need dependencies. Don't over-structure upfront.

### Use Semantic IDs

**Good:** `"backend.auth.jwt"`  
**Avoid:** `"task-17-implementation-jwt"`

### Choose the Right Edge Type

- **`blocks`** — hard dependency, must wait
- **`informs`** — context sharing, nice to have
- **`invalidates`** — conditional path, optimization
- **`suggests`** — recommendation, optional

### Keep DAGs Shallow

Prefer wide, shallow graphs over deep chains. Deep chains create bottlenecks.

### Add Retrospectives

When work completes, add `Outcome`, `Strengths`, `Weaknesses`, `Lessons` narratives. Future-you will thank you.

---

## TRON Format

For token efficiency in AI workflows, use TRON encoding. A typical plan saves 35–40% tokens:

```tron
class Edge: from, to, type
class PlanItem: id, title, status

vBRIEFInfo: { version: "0.5" }
plan: {
  title: "Build Pipeline",
  status: "running",
  items: [
    PlanItem("lint", "Lint", "completed"),
    PlanItem("test", "Test", "running"),
    PlanItem("build", "Build", "pending")
  ],
  edges: [
    Edge("lint", "build", "blocks"),
    Edge("test", "build", "blocks")
  ]
}
```

See [docs/tron-encoding.md](docs/tron-encoding.md) for the full format reference.

---

## Modular Plans with planRef

Break large plans into separate files:

```json
{
  "items": [
    { "id": "backend", "title": "Backend", "status": "running", "planRef": "file://./backend.vbrief.json" },
    { "id": "frontend", "title": "Frontend", "status": "pending", "planRef": "file://./frontend.vbrief.json" }
  ]
}
```

URI schemes: `#item-id` (internal), `file://` (local), `https://` (remote).

---

## Validation

```bash
python validation/vbrief_validator.py your-plan.vbrief.json
```

---

## Further Reading

- [Formal Specification](vbrief-spec-0.5.md)
- [Migration Guide](MIGRATION.md) — v0.4 → v0.5
- [TRON Encoding](docs/tron-encoding.md)
- [Examples](examples/)
- [JSON Schema](schemas/vbrief-core.schema.json)
- [Issues](https://github.com/visionik/vBRIEF/issues)
