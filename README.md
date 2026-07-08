# xBRIEF

![Status: Beta](https://img.shields.io/badge/status-beta-yellow)

**xBRIEF** (Basic Relational Intent Exchange Format) is a universal format for structured thinking — from a quick todo list to a full project plan to an AI agent's memory. One schema, graduated complexity, token-efficient by design.

> **TLDR:** Every AI agent invents its own memory format. Every planning tool has its own schema. xBRIEF is the common language — an open format that unifies todos, plans, playbooks, specs, and agent memory into a single Plan model. Start with 4 fields, graduate to DAG workflows. Token-efficient by design.

## Quick Start

A minimal xBRIEF document has just four fields:

```json
{
  "xBRIEFInfo": { "version": "0.8" },
  "plan": {
    "title": "My First Plan",
    "status": "running",
    "items": [
      { "title": "Do the thing", "status": "pending" }
    ]
  }
}
```

That's a valid xBRIEF document. Everything else is optional.

## Graduated Complexity

Start simple. Add structure only when you need it.

- **Minimal** — A flat task list. Title, status, items. → [`examples/minimal-plan.xbrief.json`](examples/minimal-plan.xbrief.json)
- **Structured** — Add narratives for context and rationale. → [`examples/structured-plan.xbrief.json`](examples/structured-plan.xbrief.json)
- **Retrospective** — Capture outcomes, strengths, weaknesses, lessons. → [`examples/retrospective-plan.xbrief.json`](examples/retrospective-plan.xbrief.json)
- **Graph / DAG** — Add edges for dependencies and workflows. → [`examples/dag-plan.xbrief.json`](examples/dag-plan.xbrief.json)

## Why xBRIEF?

- **Token efficient** — TRON encoding cuts LLM token usage by 35–40%
- **DAG support** — Model dependencies, pipelines, and conditional workflows
- **Graduated complexity** — No boilerplate; add features only as needed
- **Interoperable** — JSON Schema validation, standard JSON/TRON serialization
- **Open standard** — RFC-style specification, no proprietary extensions
- **No vendor lock-in** — Plain files, any tool can read/write them

## Documentation

| Document | Description |
|----------|-------------|
| [docs/xbrief-spec-0.5.md](docs/xbrief-spec-0.5.md) | Formal specification (RFC 2119) |
| [docs/GUIDE.md](docs/GUIDE.md) | Reference guide with patterns and recipes |
| [docs/getting-started.md](docs/getting-started.md) | Tutorial for beginners |
| [docs/tron-encoding.md](docs/tron-encoding.md) | TRON format reference |
| [docs/xbrief-workflow-profile.md](docs/xbrief-workflow-profile.md) | Workflow Profile extension (flow-based programming) |
| [docs/MIGRATION.md](docs/MIGRATION.md) | v0.4 → v0.5 migration guide |
| [libxbrief-ts/README.md](libxbrief-ts/README.md) | TypeScript package usage and examples |

## Repo Structure

```
xBRIEF/
├── docs/                  # Guides, spec, and references
├── examples/              # Graduated complexity examples (JSON + TRON)
├── schemas/               # JSON Schema
├── libxbrief/             # Python library
├── libxbrief-ts/          # TypeScript library + examples
├── validation/            # Validators
├── tests/                 # Test suite
└── history/               # Archived drafts and old docs
```

## Install
Python library:

```bash
pip install libxbrief
```
TypeScript package from this repo:

```bash
npm install ./libxbrief-ts
```

From a fresh clone:

```bash
git clone https://github.com/visionik/xBRIEF.git
cd xBRIEF
pip install -e .
npm install ./libxbrief-ts
```

## Library Quick Examples

TypeScript parsing and validation:

```ts
import { loads, validate } from "libxbrief-ts";

const document = loads(`{
  "xBRIEFInfo": { "version": "0.8" },
  "plan": {
    "title": "Release Checklist",
    "status": "running",
    "items": [{ "title": "Ship TypeScript port", "status": "pending" }]
  }
}`);

const report = validate(document);
console.log(report.isValid);
```

TypeScript builder API:

```ts
import { PlanBuilder } from "libxbrief-ts";

const builder = new PlanBuilder("Ship libxbrief-ts", { status: "running" });
builder.addNarrative("Proposal", "Deliver a TypeScript port with Python parity");

const implement = builder.addItem("Implement package");
implement.addSubitem("Add schemas");
implement.addSubitem("Add tests");

builder.addItem("Write docs");
builder.addEdgesFrom([["implement-package", "write-docs", "blocks"]]);

const document = builder.toDocument();
console.log(document.toJson());
```

## Validate

```bash
python validation/xbrief_validator.py your-plan.xbrief.json
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Feedback and issues welcome at [GitHub Issues](https://github.com/visionik/xBRIEF/issues).

## License

Open standard. See repository for license details.
