# vBRIEF

![Status: Beta](https://img.shields.io/badge/status-beta-yellow)

**vBRIEF** (Basic Relational Intent Exchange Format) is an open format for agentic memory — todos, plans, playbooks, and workflows in one unified Plan model.

## Quick Start

A minimal vBRIEF document has just four fields:

```json
{
  "vBRIEFInfo": { "version": "0.5" },
  "plan": {
    "title": "My First Plan",
    "status": "running",
    "items": [
      { "title": "Do the thing", "status": "pending" }
    ]
  }
}
```

That's a valid vBRIEF document. Everything else is optional.

## Graduated Complexity

Start simple. Add structure only when you need it.

- **Minimal** — A flat task list. Title, status, items. → [`examples/minimal-plan.vbrief.json`](examples/minimal-plan.vbrief.json)
- **Structured** — Add narratives for context and rationale. → [`examples/structured-plan.vbrief.json`](examples/structured-plan.vbrief.json)
- **Retrospective** — Capture outcomes, strengths, weaknesses, lessons. → [`examples/retrospective-plan.vbrief.json`](examples/retrospective-plan.vbrief.json)
- **Graph / DAG** — Add edges for dependencies and workflows. → [`examples/dag-plan.vbrief.json`](examples/dag-plan.vbrief.json)

## Why vBRIEF?

- **Token efficient** — TRON encoding cuts LLM token usage by 35–40%
- **DAG support** — Model dependencies, pipelines, and conditional workflows
- **Graduated complexity** — No boilerplate; add features only as needed
- **Interoperable** — JSON Schema validation, standard JSON/TRON serialization
- **Open standard** — RFC-style specification, no proprietary extensions
- **No vendor lock-in** — Plain files, any tool can read/write them

## Documentation

| Document | Description |
|----------|-------------|
| [vbrief-spec-0.5.md](vbrief-spec-0.5.md) | Formal specification (RFC 2119) |
| [GUIDE.md](GUIDE.md) | Reference guide with patterns and recipes |
| [docs/getting-started.md](docs/getting-started.md) | Tutorial for beginners |
| [docs/tron-encoding.md](docs/tron-encoding.md) | TRON format reference |
| [MIGRATION.md](MIGRATION.md) | v0.4 → v0.5 migration guide |

## Repo Structure

```
vBRIEF/
├── vbrief-spec-0.5.md    # Formal specification
├── GUIDE.md               # Reference / cookbook
├── examples/              # Graduated complexity examples (JSON + TRON)
├── schemas/               # JSON Schema
├── libvbrief/             # Python library
├── docs/                  # Guides and references
├── validation/            # Validators
├── tests/                 # Test suite
└── history/               # Archived drafts and old docs
```

## Install

```bash
pip install libvbrief
```

Or from source:

```bash
git clone https://github.com/visionik/vBRIEF.git
cd vBRIEF
pip install -e .
```

## Validate

```bash
python validation/vbrief_validator.py your-plan.vbrief.json
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Feedback and issues welcome at [GitHub Issues](https://github.com/visionik/vBRIEF/issues).

## License

Open standard. See repository for license details.
