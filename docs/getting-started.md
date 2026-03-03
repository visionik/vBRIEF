# Getting Started with vBRIEF

This tutorial walks you through creating your first vBRIEF documents, from a simple task list to a full DAG workflow.

## 1. Your First Minimal Plan

Create a file called `my-plan.vbrief.json`:

```json
{
  "vBRIEFInfo": { "version": "0.5" },
  "plan": {
    "title": "Weekend Errands",
    "status": "running",
    "items": [
      { "title": "Buy groceries", "status": "pending" },
      { "title": "Fix kitchen faucet", "status": "pending" },
      { "title": "Call dentist", "status": "completed" }
    ]
  }
}
```

That's a valid vBRIEF document. Only four fields are required:

- `vBRIEFInfo.version` — must be `"0.5"`
- `plan.title` — any descriptive name
- `plan.status` — one of: `draft`, `proposed`, `approved`, `pending`, `running`, `completed`, `blocked`, `cancelled`
- `plan.items` — array of items (can be empty)

## 2. Adding Narratives for Context

Narratives let you capture the *why* behind a plan. Add a `narratives` object to your plan:

```json
{
  "vBRIEFInfo": { "version": "0.5" },
  "plan": {
    "title": "API Redesign",
    "status": "proposed",
    "narratives": {
      "Proposal": "Redesign the public API to use REST conventions consistently.",
      "Problem": "Current API mixes RPC and REST patterns, confusing consumers.",
      "Constraint": "Must maintain backward compatibility for 6 months.",
      "Risk": "Breaking changes may slip through without integration tests."
    },
    "items": [
      { "id": "audit", "title": "Audit current endpoints", "status": "completed" },
      { "id": "design", "title": "Design new schema", "status": "running" },
      { "id": "implement", "title": "Implement changes", "status": "pending" }
    ]
  }
}
```

Common narrative keys for planning: `Proposal`, `Problem`, `Background`, `Constraint`, `Risk`, `Alternative`.

For retrospectives: `Outcome`, `Strengths`, `Weaknesses`, `Lessons`.

You can also add narratives at the item level using the `narrative` field (singular):

```json
{
  "id": "audit",
  "title": "Audit current endpoints",
  "status": "completed",
  "narrative": {
    "Result": "Found 12 inconsistent endpoints out of 47 total."
  }
}
```

## 3. Adding DAG Edges for Dependencies

When tasks depend on each other, add `edges` to model the workflow:

```json
{
  "vBRIEFInfo": { "version": "0.5" },
  "plan": {
    "title": "Release Pipeline",
    "status": "running",
    "items": [
      { "id": "lint", "title": "Lint code", "status": "completed" },
      { "id": "test", "title": "Run tests", "status": "running" },
      { "id": "build", "title": "Build artifacts", "status": "pending" },
      { "id": "deploy", "title": "Deploy to staging", "status": "pending" }
    ],
    "edges": [
      { "from": "lint", "to": "build", "type": "blocks" },
      { "from": "test", "to": "build", "type": "blocks" },
      { "from": "build", "to": "deploy", "type": "blocks" },
      { "from": "lint", "to": "test", "type": "informs" }
    ]
  }
}
```

Edge types:

| Type | Meaning |
|------|---------|
| `blocks` | Target cannot start until source completes |
| `informs` | Target benefits from source context (not blocking) |
| `invalidates` | Source completion makes target unnecessary |
| `suggests` | Weak recommendation, no dependency |

**Rules:** Edges must form a DAG (no cycles). Both `from` and `to` must reference existing item IDs.

## 4. Using TRON Encoding for Token Efficiency

TRON reduces token usage by ~35–40%. Convert the pipeline example above:

```tron
class Edge: from, to, type
class PlanItem: id, title, status

vBRIEFInfo: { version: "0.5" }
plan: {
  title: "Release Pipeline",
  status: "running",
  items: [
    PlanItem("lint", "Lint code", "completed"),
    PlanItem("test", "Run tests", "running"),
    PlanItem("build", "Build artifacts", "pending"),
    PlanItem("deploy", "Deploy to staging", "pending")
  ],
  edges: [
    Edge("lint", "build", "blocks"),
    Edge("test", "build", "blocks"),
    Edge("build", "deploy", "blocks"),
    Edge("lint", "test", "informs")
  ]
}
```

TRON class definitions at the top map positional arguments to fields. See [docs/tron-encoding.md](tron-encoding.md) for the full reference.

## 5. Validating Your Document

Run the validator:

```bash
python validation/vbrief_validator.py my-plan.vbrief.json
```

The validator checks:

- JSON syntax
- Required fields (`vBRIEFInfo.version`, `plan.title`, `plan.status`, `plan.items`)
- Valid status enum values
- DAG constraints (no cycles, valid edge references)
- Hierarchical ID format
- Schema compliance

## Next Steps

- **[GUIDE.md](../GUIDE.md)** — Patterns and recipes for common use cases
- **[vbrief-spec-0.5.md](../vbrief-spec-0.5.md)** — Formal specification
- **[examples/](../examples/)** — More examples in JSON and TRON
