# vContext Specification v0.3

> **DRAFT SPECIFICATION**: This document is a draft and subject to change. Feedback, suggestions, and contributions from the community are highly encouraged. Please submit input via GitHub issues or pull requests.

Agentic coding systems increasingly rely on structured memory: **short-term memory** (todo lists for immediate tasks), **medium-term memory** (plans for project organization), and **long-term memory** (playbooks for accumulated strategies and learnings). However, proprietary formats used by different agentic systems hamper interoperability and limit cross-agent collaboration.

vContext provides an **open, standardized format** for these memory systems that is:
- **Agent-friendly**: Token-efficient TRON encoding optimized for LLM workflows
- **Human-readable**: Clear structure for direct/TUI/GUI editing and review
- **Interoperable**: JSON compatibility for integration with existing tools
- **Extensible**: Modular architecture supports simple to complex use cases

This enables both agentic systems and human-facing tools to share a common representation of work, plans, and accumulated knowledge.

**Origins and Scope**:
- This specification began with a review of internal memory formats used by several agentic coding systems to ensure it addresses real-world requirements
- The design is inspired by established standards such as vCard and vCalendar/iCalendar

**Specification Version**: 0.4

**Last Updated**: 2025-12-28T00:00:00Z

**Author**: Jonathan Taylor (visionik@pobox.com)

## Goals

vContext aims to establish a universal, open standard for agentic memory systems that:

1. MUST **Reduce LLM context window overhead** by representing key contextual memory with efficient structures

2. MUST **Help avoid LLM context collapse and brevity bias** by keeping memories in a more detailed and structured format that preserves important context and nuance

3. MUST **Enable interoperability** across different AI coding agents and tools by providing a common format for representing work items, plans, and accumulated knowledge

4. MUST **Support the full lifecycle** of agentic work from immediate task execution (TodoLists) to strategic planning (Plans) to long-term knowledge retention (Playbooks)

5. MAY **Prevent vendor lock-in** by ensuring all agentic memory is stored in an open, documented format that any tool can read and write

6. MUST **Scale from simple to complex** via a modular extension system that keeps the core specification minimal while supporting advanced features when needed

7. MAY **Bridge human and AI collaboration** by maintaining both machine-optimized (TRON) and universally-compatible (JSON) representations of the same data

8. MAY be **extended to serve as a transactional log** of agentic coding sessions for legal and intellectual property defense

9. MAY **also be use for non-AI tools** that work with todo lists, plans, and playbooks.

By standardizing how agentic systems remember and organize their work, vContext enables a future where agents and tools can seamlessly share context, learn from each other's experiences, and collaborate across platforms.

## Changelog: v0.2 → v0.3

**Breaking Changes**:
- **Phase → PlanItem**: Renamed `Phase` to `PlanItem` to follow `<Container>Item` naming convention
- **plan.phases → plan.items**: Plans now use `items` field (was `phases`) to contain PlanItem[]
- **phase.subPhases → planItem.subItems**: Nested items use `subItems` field (was `subPhases`)
- **PlaybookEntry → PlaybookItem**: Renamed `PlaybookEntry` to `PlaybookItem` for consistency
- **playbook.entries → playbook.items**: Playbooks now use `items` field (was `entries`) to contain PlaybookItem[]

**New Features**:
- **Item abstract base**: Added `Item` as abstract base class for all contained entities (TodoItem, PlanItem, PlaybookItem)
- **Tagged atomic**: Added universal `tags` field to Extension 3 - ALL entities (TodoList, TodoItem, Plan, PlanItem, Playbook, PlaybookItem) can now be tagged
- **Unified container pattern**: All containers (TodoList, Plan, Playbook) now consistently use `.items` field
- **Container references**: Containers and items MAY reference other containers via URI (file:// or https://), enabling cross-document linking without embedding multiple containers in a single file

**Migration**: See `history/spec-v0.2.md` for previous version. Migration tools provided in atomic-classes-proposal.md.


## Changelog: v0.3 → v0.4

**Breaking Changes**:
- **Playbooks promoted to core**: Playbook is now a core container type (alongside TodoList and Plan)
- **Extensions extracted**: All extension definitions moved to `vContext-extension-common.md`
- **Minimal Playbook structure**: Core includes basic Playbook/PlaybookItem; advanced features remain in extensions

**New Features**:
- **Playbook** core container with `title`, `description`, `items` fields
- **PlaybookItem** core type with `title`, `status`, `content` fields
- **Extension reference model**: Extensions now maintained in separate document for modularity

**Migration**: See `history/spec-v0.3.md` for previous version.

## Conformance and normative language

The key words **MUST**, **SHOULD**, and **MAY** in this document are to be interpreted as normative requirements.

A document is **vContext Core v0.4 conformant** if:
- It is a single object containing `vContextInfo` and exactly one of `todoList`, `plan`, or `playbook`.
- `vContextInfo.version` MUST equal `"0.4"`.
- Any `status` fields MUST use only the enumerated values defined in this spec.

### Extensibility and unknown fields

- Producers MAY include additional fields not defined in core or extensions.
- Consumers MUST ignore unknown fields.
- Tools that rewrite documents SHOULD preserve unknown fields (do not drop extension data).

### Date/time and timezone

- All `datetime` values MUST be RFC 3339 / ISO 8601 timestamps that include an explicit offset (`Z` or `±hh:mm`).
- `timezone` (when present) SHOULD be treated as display intent (IANA timezone name), not as a parsing fallback.

### Identifiers and sequencing

When Extension 2 (Identifiers) and/or Extension 10 (Version Control & Sync) are in use:
- Within a single container, `id` values MUST be unique (e.g., within `todoList.items`, within `plan.items`).
- `uid` values (when present) SHOULD be globally unique and stable across copies.
- `sequence` values (when present) MUST be monotonically non-decreasing for a given document.

## Machine-verifiable schemas (JSON)

This spec includes JSON Schema files intended for validation and tooling:
- Core schema: `schemas/vcontext-core.schema.json`
- Playbooks extension schema: `schemas/vcontext-extension-playbooks.schema.json`

## Design Philosophy

vContext uses a **modular, layered architecture**:
1. **Core (MVA)**: Minimum Viable Account - essential fields only
2. **Extensions**: Optional feature modules that add capabilities
3. **Compatibility**: Extensions can be mixed and matched

In this context, "account" means a written or stored record or description of events, experiences, or facts.

This prevents complexity overload while supporting advanced use cases.

## Why Two Formats? TRON and JSON

vContext supports both TRON and JSON encodings. **TRON is the preferred format** for AI/agent workflows due to its token efficiency, with JSON included for wider compatibility with existing tools and systems.

### TRON (Token Reduced Object Notation) — Preferred

**TRON is a superset of JSON**, meaning any valid JSON document is also valid TRON. The format extends JSON by adding class instantiation features designed to reduce token usage through schema definitions. JSON can be included anywhere within TRON documents, though TRON classes should be used whenever possible for maximum efficiency.

**Example comparison** — same data in both formats:

**JSON** (98 tokens):
```json
{
  "items": [
    {"id": "1", "title": "Auth", "status": "completed"},
    {"id": "2", "title": "API", "status": "inProgress"},
    {"id": "3", "title": "Tests", "status": "pending"}
  ]
}
```

**TRON** (62 tokens, 37% reduction):
```tron
class Item: id, title, status

items: [
  Item("1", "Auth", "completed"),
  Item("2", "API", "inProgress"),
  Item("3", "Tests", "pending")
]
```

**Key benefits**:
- **Token efficiency**: Uses 35-40% fewer LLM tokens than JSON for structured data
- **Class-based schemas**: Define structure once, reuse for all instances
- **Positional encoding**: `TodoItem("item-1", "Fix bug", "pending", ...)` vs `{"id": "item-1", "title": "Fix bug", "status": "pending", ...}`
- **Human readability**: Subjectively more readable than JSON due to reduced noise from repeated field names
- **Cost savings**: Fewer tokens = lower API costs for AI operations
- **Context preservation**: More data fits in LLM context windows
- **Best for**: Humans, internal storage, agent-to-agent communication, token-constrained scenarios

**Resources**:
- Specification: https://tron-format.github.io/
- Discussion: https://www.reddit.com/r/LocalLLaMA/comments/1pa3ok3/toon_is_terrible_so_i_invented_a_new_format_tron/
- Format Comparison: https://www.piotr-sikora.com/blog/2025-12-05-toon-tron-csv-yaml-json-format-comparison

### JSON — For Compatibility
- **Universal compatibility**: Every programming language has JSON support
- **Tooling ecosystem**: Linters, validators, editors all support JSON
- **Familiarity**: Ubiquitous in web development and APIs
- **Best for**: LLMs (until trained on TRON), APIs, system integration, archival, human editing with standard tools

### Why Not TOON?

[TOON (Token-Oriented Object Notation)](https://github.com/toon-format/toon) was also considered. TRON was chosen because:

- **Nested structures**: TRON objectively uses fewer tokens for deeply nested data (plans with phases, hierarchical todo lists)
- **Readability**: TRON's class syntax `TodoItem("id", "title")` is subjectively more human readable than TOON's YAML+CSV hybrid
- **Use case fit**: TOON excels at flat tabular data; vContext's hierarchical structures suit TRON better

**Note**: Both JSON and TRON are lossless representations of the same data model.

### Why Not Markdown?

Markdown is widely used for human-readable documents and might seem like a natural choice for representing plans and todos. However, it has significant limitations for agentic memory systems:

**Problems with Markdown**:
- **Parsing ambiguity**: Markdown has no formal schema, leading to inconsistent parsing across tools and making reliable programmatic access difficult
- **Weak structure**: Lists, headings, and nested content lack semantic meaning (is `- [ ]` a todo item, a checklist, or just formatted text?)
- **No type system**: Can't distinguish between a priority level, status value, or arbitrary text without custom conventions
- **Token inefficiency**: Markdown's human-optimized formatting (repeated `- [ ]`, `**bold**`, etc.) consumes more tokens than structured formats
- **Inconsistent updates**: Modifying specific items requires regex/heuristics rather than direct field access, increasing error risk
- **No validation**: Invalid or malformed markdown is still valid markdown, making it easy to corrupt data

**Markdown as an output format**:

While we believe many agents and tools will convert vContext files to Markdown for human presentation, reporting, or integration with Markdown-based workflows, a consistent, structured, low-token format is needed for:

- **Reliable programmatic access**: Agents need to query, filter, and update specific fields without parsing ambiguity
- **Cross-agent interoperability**: Different agents must interpret the same document identically
- **Token efficiency**: Minimizing context window usage in LLM operations
- **Data validation**: Ensuring documents conform to expected schemas
- **Consistent updates**: Making precise modifications without risking corruption
- **Machine learning**: Structured data enables better training and fine-tuning of agentic systems

vContext serves as the canonical storage format, while Markdown can be generated on-demand for human consumption.

## Architecture Layers

```
┌─────────────────────────────────────┐
│   Extensions (Optional Modules)     │
│  ┌─────────────── ──────────────┐   │
│  │  Advanced Playbook, etc.       │   │
│  └────────────── ───────────────┘   │
│  ┌────────────── ───────────────┐   │
│  │   Workflow & Scheduling      │   │
│  └─────────────── ──────────────┘   │
│  ┌────────────── ───────────────┐   │
│  │    Rich Metadata             │   │
│  └─────────────── ──────────────┘   │
├─────────────────────────────────────┤
│   Core (MVA)                        │
│   Item, TodoList, TodoItem,         │
│   Plan, PlanItem,                   │
│   Playbook, PlaybookItem            │
└─────────────────────────────────────┘
```

---

# Part 1: Core (Minimum Viable Account)

_* In this context, "account" means a written or stored record or description of events, experiences, or facts._

## Design Principles

- **Format-agnostic**: Support both JSON and [TRON](https://tron-format.github.io/) encodings
- **Minimal**: Only essential fields in core
- **Extensible**: Easy to add fields via extensions or metadata
- **Compatible**: All extensions are backward compatible with core

## Core Data Models

### When to Use TodoList vs Plan vs Playbook

**TodoList** is for **immediate execution** (short-term memory) — tracking tasks that need to be done now or soon:
- Simple, flat list of action items
- Focus on "what" needs to be done, not "why" or "how"
- Short lifecycle (hours to days)
- Examples: daily tasks, sprint backlog, debugging checklist

**Plan** is for **coordination and documentation** (medium-term memory) — organizing complex work with context:
- Requires explanation of approach, rationale, or design
- Multi-phase work that needs to be broken down
- Needs review, approval, or stakeholder communication
- Medium lifecycle (days to weeks/months)
- Examples: feature implementation plans, refactoring proposals, architectural designs

**Playbook** is for **accumulated knowledge** (long-term memory) — lessons learned that persist across sessions:
- Strategies that have proven effective
- Common pitfalls and how to avoid them
- Best practices and guidelines
- Warnings about what not to do
- Long lifecycle (months to years)
- Examples: coding standards, deployment checklists, debugging strategies, architecture principles

**Rule of thumb**: Use TodoList for "what to do now", Plan for "how to approach this project", and Playbook for "what we've learned that applies to future work".

### vContextInfo (Core)

**Purpose**: Document-level metadata that appears once per file, as a sibling to the main content object (TodoList or Plan). Contains version information and optional authorship details.

```javascript
vContextInfo {
  version: string          # Schema version (e.g., "0.2")
  author?: string          # Document creator
  description?: string     # Brief document description
  metadata?: object        # Custom document-level fields
}
```

**Document Structure**: A vContext document contains `vContextInfo` and exactly one container (`todoList`, `plan`, or `playbook`):
```javascript
{
  vContextInfo: vContextInfo,  # Document metadata (required)
  todoList?: TodoList,       # Either todoList...
  plan?: Plan,               # ...or plan...
  playbook?: Playbook        # ...or playbook (exactly one)
}
```

**Cross-document references**: Containers and items MAY reference other vContext documents or external resources using URIs (see Extension 7). This allows related containers to be linked without embedding them in a single file:
```javascript
// Plan referencing a separate TodoList document
{
  vContextInfo: {...},
  plan: {
    title: "Feature Implementation",
    uris: [{uri: "file://./tasks.vcontext.json", type: "x-vcontext/todoList"}],
    ...
  }
}

// TodoItem referencing a Plan document
{
  vContextInfo: {...},
  todoList: {
    items: [
      {
        title: "Implement auth feature",
        uris: [{uri: "file://./auth-plan.vcontext.json", type: "x-vcontext/plan"}]
      }
    ]
  }
}
```

### Item (Core Abstract Base)

**Purpose**: Abstract base class for all contained entities (TodoItem, PlanItem, PlaybookItem). Provides the fundamental pattern for discrete, actionable units within collections.

```javascript
Item {
  title: string            # Brief summary (required)
  status: enum             # Lifecycle status (required)
}
```

**Rationale**: TodoItem, PlanItem (formerly Phase), and PlaybookItem (formerly PlaybookEntry) share a common "contained item" pattern:
- They are discrete, actionable or knowledge units
- They exist within parent containers (TodoList, Plan, Playbook)
- They ALL have `title` and `status` (core requirements)
- They can be independently referenced when Identifiable (Extension 2)

**Naming convention**: Concrete types follow `<Container>Item` pattern:
- TodoList → contains → **TodoItem**
- Plan → contains → **PlanItem** (renamed from Phase)
- Playbook → contains → **PlaybookItem** (renamed from PlaybookEntry)

**Status enums by type**:
- TodoItem/PlanItem: `"pending" | "inProgress" | "completed" | "blocked" | "cancelled"`
- Plan: `"draft" | "proposed" | "approved" | "inProgress" | "completed" | "cancelled"`
- PlaybookItem: `"active" | "deprecated" | "quarantined"`

### TodoList (Core)

**Purpose**: A collection of actionable work items for **short-term memory**. Used by agents and humans to track immediate tasks, subtasks, and tactical execution.

```javascript
TodoList {
  items: TodoItem[]        # Array of todo items
}
```

### TodoItem (Core)

**Purpose**: A single actionable task with status tracking. The fundamental unit of work in vContext.

```javascript
TodoItem {
  title: string            # Brief summary (required)
  status: enum             # "pending" | "inProgress" | "completed" | "blocked" | "cancelled"
}
```

### Plan (Core)

**Purpose**: A structured design document for **medium-term memory**. Used to organize projects, document approaches, and coordinate multi-step work. Plans contain `items` (PlanItems) and may reference other resources.

```javascript
Plan {
  title: string           # Plan title
  status: enum            # "draft" | "proposed" | "approved" | "inProgress" | "completed" | "cancelled"
  narratives: {
    proposal: Narrative   # Proposed changes (required)
  }
}
```

### PlanItem (Core)

**Purpose**: A stage of work within a plan (formerly called Phase). PlanItems organize execution into ordered steps and can be nested hierarchically (with extensions). Each item can have its own status and todo list. Execution order is determined by array position.

```javascript
PlanItem {
  title: string           # Item name
  status: enum            # "pending" | "inProgress" | "completed" | "blocked" | "cancelled"
}
```

**Note**: PlanItem extends the abstract `Item` base class (title + status required).

### Narrative (Core)

**Purpose**: A named block of documentation within a plan. Narratives organize written content (problem statements, proposals, testing approaches, etc.) using markdown formatting.

```javascript
Narrative {
  title: string           # Narrative heading
  content: string         # Markdown content
}
```

### Playbook (Core)

**Purpose**: A collection of accumulated knowledge for **long-term memory**. Used to store lessons learned, best practices, warnings, and strategies that persist across sessions. Playbooks help agents avoid repeating mistakes and apply proven approaches.

```javascript
Playbook {
  title: string           # Playbook title
  description?: string    # Optional description
  items: PlaybookItem[]   # Array of playbook entries
}
```

### PlaybookItem (Core)

**Purpose**: A single piece of accumulated knowledge or guidance. The minimal core version includes just the essential fields. Advanced features (event sourcing, metrics, linked-list updates) are available via Extension 12.

```javascript
PlaybookItem {
  title: string           # Brief summary of the guidance
  status: enum            # "active" | "deprecated" | "quarantined"
  content: string         # The actual guidance or lesson learned
}
```

**Note**: PlaybookItem extends the abstract `Item` base class (title + status required). The `content` field is required in core to ensure each item contains actionable guidance.

## Core Examples

### Minimal TodoList

**TRON:**
```tron
class vContextInfo: version
class TodoList: items
class TodoItem: title, status

vContextInfo: vContextInfo("0.4")
todoList: TodoList([
  TodoItem("Implement authentication", "pending"),
  TodoItem("Write API documentation", "pending")
])
```

**JSON:**
```json
{
  "vContextInfo": {
    "version": "0.4"
  },
  "todoList": {
    "items": [
      {
        "title": "Implement authentication",
        "status": "pending"
      },
      {
        "title": "Write API documentation",
        "status": "pending"
      }
    ]
  }
}
```

### Minimal Plan

**TRON:**
```tron
class vContextInfo: version
class Plan: title, status, narratives, items
class PlanItem: title, status
class Narrative: title, content

vContextInfo: vContextInfo("0.4")
plan: Plan(
  "Add user authentication",
  "draft",
  {
    "proposal": Narrative(
      "Proposed Changes",
      "Implement JWT-based authentication with refresh tokens"
    )
  },
  [
    PlanItem("Database schema", "completed"),
    PlanItem("JWT implementation", "pending")
  ]
)
```

**JSON:**
```json
{
  "vContextInfo": {
    "version": "0.4"
  },
  "plan": {
    "title": "Add user authentication",
    "status": "draft",
    "narratives": {
      "proposal": {
        "title": "Proposed Changes",
        "content": "Implement JWT-based authentication with refresh tokens"
      }
    },
    "items": [
      {
        "title": "Database schema",
        "status": "completed"
      },
      {
        "title": "JWT implementation",
        "status": "pending"
      }
    ]
  }
}
```

### Minimal Playbook

**TRON:**
```tron
class vContextInfo: version
class Playbook: title, description, items
class PlaybookItem: title, status, content

vContextInfo: vContextInfo("0.4")
playbook: Playbook(
  "Backend Development Best Practices",
  "Accumulated lessons learned from backend development",
  [
    PlaybookItem(
      "Test database migrations in staging first",
      "active",
      "Always run database migrations in staging environment before production to catch schema conflicts early."
    ),
    PlaybookItem(
      "Use connection pooling for database access",
      "active",
      "Configure connection pooling to handle load spikes and prevent connection exhaustion."
    )
  ]
)
```

**JSON:**
```json
{
  "vContextInfo": {
    "version": "0.4"
  },
  "playbook": {
    "title": "Backend Development Best Practices",
    "description": "Accumulated lessons learned from backend development",
    "items": [
      {
        "title": "Test database migrations in staging first",
        "status": "active",
        "content": "Always run database migrations in staging environment before production to catch schema conflicts early."
      },
      {
        "title": "Use connection pooling for database access",
        "status": "active",
        "content": "Configure connection pooling to handle load spikes and prevent connection exhaustion."
      }
    ]
  }
}
```

---

# Part 2: Extensions

All extension definitions have been moved to [vContext-extension-common.md](./vContext-extension-common.md).

The common extensions include:
- Extension 1: Timestamps
- Extension 2: Identifiers  
- Extension 3: Rich Metadata
- Extension 4: Hierarchical Structures
- Extension 5: Workflow & Scheduling
- Extension 6: Participants & Collaboration
- Extension 7: Resources & References
- Extension 8: Recurring & Reminders
- Extension 9: Security & Privacy
- Extension 10: Version Control & Sync
- Extension 11: Multi-Agent Forking
- Extension 12: Advanced Playbook Features (event sourcing, metrics, etc.)

See also domain-specific extension documents:
- `vContext-extension-playbooks.md` — Advanced playbook features
- `vContext-extension-MCP.md` — Model Context Protocol integration
- `vContext-extension-beads.md` — Beads integration
- `vContext-extension-claude.md` — Claude integration
- `vContext-extension-security.md` — Security extension
- `vContext-extension-api-go.md` — Go API
- `vContext-extension-api-python.md` — Python API
- `vContext-extension-api-typescript.md` — TypeScript API

---

# Appendix A: Complete Examples (All Extensions)

These examples are intentionally "real-world" and include fields from **Core + Extensions 1–12**. Unknown fields are allowed and tools should preserve them.

## A1. TodoList (Operational Execution)

```json
{
  "vContextInfo": {
    "version": "0.4",
    "author": "Platform Team",
    "description": "On-call followups for incident INC-2042",
    "created": "2025-12-27T17:20:00Z",
    "updated": "2025-12-28T07:35:00Z",
    "timezone": "America/Los_Angeles",
    "metadata": {
      "extensions": [
        "timestamps",
        "identifiers",
        "rich-metadata",
        "hierarchical",
        "workflow",
        "participants",
        "resources",
        "recurring",
        "security",
        "version-control",
        "forking",
        "playbooks"
      ]
    }
  },
  "todoList": {
    "id": "todo-inc-2042",
    "uid": "f7d2a4c6-1e3f-4d62-9c9a-3a2e8f4b1f10",
    "title": "INC-2042: Payment webhook latency regression",
    "description": "Follow-ups after incident. Goal: prevent recurrence and improve observability.",
    "tags": ["incident", "payments", "webhooks", "on-call"],
    "sequence": 12,
    "agent": {
      "id": "human-jt",
      "type": "human",
      "name": "JT",
      "email": "visionik@pobox.com"
    },
    "lastModifiedBy": {
      "id": "agent-ops-bot",
      "type": "system",
      "name": "ops-bot"
    },
    "changeLog": [
      {
        "sequence": 10,
        "timestamp": "2025-12-28T06:50:00Z",
        "agent": {"id": "agent-ops-bot", "type": "system", "name": "ops-bot"},
        "operation": "update",
        "reason": "Auto-imported incident tasks from pager escalation"
      },
      {
        "sequence": 12,
        "timestamp": "2025-12-28T07:35:00Z",
        "agent": {"id": "human-jt", "type": "human", "name": "JT"},
        "operation": "update",
        "reason": "Added rollback drill and recurring SLA review"
      }
    ],
    "uris": [
      {
        "uri": "https://status.example.com/incidents/INC-2042",
        "type": "x-incident",
        "title": "Incident timeline",
        "description": "Primary incident record"
      },
      {
        "uri": "file://./plans/payment-webhooks-plan.vcontext.json",
        "type": "x-vcontext/plan",
        "title": "Remediation plan"
      },
      {
        "uri": "file://./playbooks/platform-reliability-playbook.vcontext.json",
        "type": "x-vcontext/playbook",
        "title": "Reliability playbook"
      }
    ],
    "items": [
      {
        "id": "t1",
        "uid": "8c0d8b2f-2d08-4e4a-a34f-6a21f8f8a0b1",
        "title": "Add p95/p99 alert for /webhooks/process",
        "status": "inProgress",
        "description": "Alert on sustained p95>2s for 10m. Include saturation + queue depth as signals.",
        "priority": "critical",
        "tags": ["observability", "alerts"],
        "created": "2025-12-28T06:55:00Z",
        "updated": "2025-12-28T07:30:00Z",
        "dueDate": "2025-12-29T02:00:00Z",
        "percentComplete": 40,
        "timezone": "America/Los_Angeles",
        "participants": [
          {"id": "human-jt", "name": "JT", "role": "owner", "status": "accepted"},
          {"id": "human-alex", "name": "Alex", "email": "alex@example.com", "role": "contributor", "status": "accepted"}
        ],
        "relatedComments": ["pr-comment-1842", "pr-comment-1849"],
        "uris": [
          {"uri": "https://grafana.example.com/d/webhooks", "type": "text/html", "title": "Webhook dashboard"}
        ],
        "classification": "private",
        "sequence": 3,
        "lastModifiedBy": {"id": "human-jt", "type": "human", "name": "JT"},
        "lockedBy": {
          "agent": {"id": "human-jt", "type": "human", "name": "JT"},
          "acquiredAt": "2025-12-28T07:10:00Z",
          "type": "soft",
          "expiresAt": "2025-12-28T09:10:00Z"
        }
      },
      {
        "id": "t2",
        "uid": "b112f9e9-1c84-4b8b-9893-6a0b2a1a40f7",
        "title": "Run rollback drill for payment-webhooks",
        "status": "pending",
        "description": "Practice rollback procedure in staging; capture time-to-recover and gaps.",
        "priority": "high",
        "tags": ["runbook", "resilience"],
        "created": "2025-12-28T07:33:00Z",
        "updated": "2025-12-28T07:33:00Z",
        "dueDate": "2025-12-30T18:00:00Z",
        "reminders": [
          {"trigger": "-PT1H", "action": "email", "description": "Rollback drill in 1 hour"}
        ],
        "dependencies": ["t1"],
        "uris": [
          {"uri": "file://./docs/rollback.md", "type": "text/markdown", "title": "Rollback runbook"}
        ],
        "classification": "confidential"
      },
      {
        "id": "t3",
        "uid": "61c0c8c1-1db5-4e4e-b5da-1b7cbb1b2c22",
        "title": "Weekly: review webhook SLA + alert thresholds",
        "status": "pending",
        "description": "Adjust for seasonal traffic. Ensure alert noise is acceptable.",
        "priority": "medium",
        "tags": ["recurring", "slo"],
        "created": "2025-12-28T07:34:00Z",
        "updated": "2025-12-28T07:34:00Z",
        "dueDate": "2026-01-05T18:00:00Z",
        "recurrence": {"frequency": "weekly", "interval": 1, "byDay": ["MO"]},
        "reminders": [
          {"trigger": "-PT15M", "action": "display", "description": "SLA review starts in 15 minutes"}
        ],
        "classification": "private"
      }
    ]
  }
}
```

## A2. Plan (Coordination + Documentation)

```json
{
  "vContextInfo": {
    "version": "0.4",
    "author": "Platform Team",
    "description": "Remediation plan for payment webhooks latency regression",
    "created": "2025-12-27T18:00:00Z",
    "updated": "2025-12-28T07:20:00Z",
    "timezone": "America/Los_Angeles",
    "metadata": {
      "extensions": [
        "timestamps",
        "identifiers",
        "rich-metadata",
        "hierarchical",
        "workflow",
        "participants",
        "resources",
        "recurring",
        "security",
        "version-control",
        "forking",
        "playbooks"
      ]
    }
  },
  "plan": {
    "id": "plan-payment-webhooks",
    "uid": "b28c7d9d-22e7-4cd1-8f36-6d2ef2fbf12a",
    "title": "Payment webhooks: reduce latency + prevent recurrence",
    "status": "inProgress",
    "author": "Platform Team",
    "reviewers": ["SRE Lead", "Payments TL"],
    "description": "Fix root cause, add guardrails, improve observability, and validate rollback.",
    "tags": ["payments", "webhooks", "reliability"],

    "created": "2025-12-27T18:00:00Z",
    "updated": "2025-12-28T07:20:00Z",
    "timezone": "America/Los_Angeles",

    "sequence": 7,
    "agent": {"id": "human-jt", "type": "human", "name": "JT"},
    "lastModifiedBy": {"id": "human-jt", "type": "human", "name": "JT"},
    "changeLog": [
      {
        "sequence": 6,
        "timestamp": "2025-12-28T06:40:00Z",
        "agent": {"id": "human-jt", "type": "human", "name": "JT"},
        "operation": "update",
        "reason": "Added load-test acceptance criteria and rollout plan"
      },
      {
        "sequence": 7,
        "timestamp": "2025-12-28T07:20:00Z",
        "agent": {"id": "human-jt", "type": "human", "name": "JT"},
        "operation": "update",
        "reason": "Expanded risks and rollback procedure"
      }
    ],

    "fork": {
      "parentUid": "b28c7d9d-22e7-4cd1-8f36-6d2ef2fbf12a",
      "parentSequence": 5,
      "forkedAt": "2025-12-28T06:10:00Z",
      "forkReason": "Exploring alternative queueing strategy",
      "mergeStatus": "unmerged"
    },

    "narratives": {
      "proposal": {
        "title": "Proposed Changes",
        "content": "1) Fix N+1 DB queries in webhook processing.\n2) Add queue-depth based autoscaling.\n3) Add p95/p99 alerts + dashboards.\n4) Add rollback drill + runbook improvements."
      },
      "problem": {
        "title": "Problem Statement",
        "content": "Production latency regression increased webhook processing time from ~250ms to >2s p95 under load." 
      },
      "context": {
        "title": "Current State",
        "content": "Webhook handler performs per-event DB lookups (N+1) and competes with background reconciliation jobs." 
      },
      "alternatives": {
        "title": "Alternatives Considered",
        "content": "- Add more replicas only (insufficient: DB bottleneck)\n- Change DB isolation level (riskier)\n- Move reconciliation to separate worker pool (selected)"
      },
      "risks": {
        "title": "Risks",
        "content": "- Changing worker pool may affect ordering guarantees\n- Autoscaling could amplify DB load if not bounded\nMitigations: rate limits, circuit breakers, staged rollout." 
      },
      "testing": {
        "title": "Testing / Validation",
        "content": "- Reproduce regression with load test\n- Confirm p95<400ms at 2x typical throughput\n- Run rollback drill in staging\n- Validate alert noise for 48h" 
      },
      "rollout": {
        "title": "Rollout",
        "content": "1) Feature flag new worker pool\n2) Canary 5%\n3) Ramp 25% → 100%\n4) Post-deploy review at 24h"
      }
    },

    "references": [
      {"uri": "file://./todo/inc-2042-todo.vcontext.json", "type": "x-vcontext/todoList", "title": "Execution checklist"},
      {"uri": "file://./playbooks/platform-reliability-playbook.vcontext.json", "type": "x-vcontext/playbook", "title": "Reliability playbook"}
    ],

    "uris": [
      {"uri": "https://github.com/org/repo/issues/2042", "type": "x-github/issue", "title": "INC-2042 issue"},
      {"uri": "https://github.com/org/repo/pull/1842", "type": "x-github/pr", "title": "Fix N+1 queries"},
      {"uri": "file://./services/webhooks/handler.ts", "type": "text/plain", "title": "Webhook handler"},
      {"uri": "https://files.example.com/inc-2042/latency.png", "type": "image/png", "title": "Latency before/after"}
    ],

    "items": [
      {
        "id": "p1",
        "uid": "p1-uid",
        "title": "Diagnose and fix root cause",
        "status": "inProgress",
        "description": "Remove N+1 queries; isolate reconciliation job impact.",
        "tags": ["root-cause"],
        "dependencies": [],
        "startDate": "2025-12-27T18:30:00Z",
        "percentComplete": 60,
        "participants": [
          {"id": "human-jt", "name": "JT", "role": "owner", "status": "accepted"}
        ],
        "classification": "private",
        "todoList": {
          "items": [
            {"title": "Add query batching", "status": "inProgress"},
            {"title": "Write regression load test", "status": "pending"}
          ]
        },
        "subItems": [
          {
            "id": "p1-1",
            "title": "Fix N+1 DB lookups",
            "status": "inProgress",
            "dependencies": [],
            "reminders": [{"trigger": "-PT30M", "action": "display", "description": "PR review in 30 minutes"}]
          },
          {
            "id": "p1-2",
            "title": "Split reconciliation to separate worker pool",
            "status": "pending",
            "dependencies": ["p1-1"],
            "location": {"name": "Remote", "url": "https://zoom.example.com/room/ops"}
          }
        ]
      },
      {
        "id": "p2",
        "uid": "p2-uid",
        "title": "Observability + guardrails",
        "status": "pending",
        "description": "Dashboards, alerts, SLOs, and bounded autoscaling.",
        "dependencies": ["p1"],
        "classification": "private",
        "participants": [
          {"id": "human-alex", "name": "Alex", "role": "assignee", "status": "accepted"}
        ]
      },
      {
        "id": "p3",
        "uid": "p3-uid",
        "title": "Rollout + rollback drill",
        "status": "pending",
        "description": "Canary rollout, validate rollback, and document runbook.",
        "dependencies": ["p1", "p2"],
        "classification": "confidential",
        "participants": [
          {"id": "human-jt", "name": "JT", "role": "owner", "status": "accepted"},
          {"id": "human-sre", "name": "SRE Lead", "role": "reviewer", "status": "needsAction"}
        ]
      }
    ]
  }
}
```

## A3. Playbook (Long-Term Memory)

```json
{
  "vContextInfo": {
    "version": "0.4",
    "author": "Platform Team",
    "description": "Reliability practices for latency regressions and incident followups",
    "created": "2025-11-10T18:00:00Z",
    "updated": "2025-12-28T07:10:00Z",
    "timezone": "America/Los_Angeles",
    "metadata": {
      "extensions": [
        "timestamps",
        "identifiers",
        "rich-metadata",
        "version-control",
        "playbooks"
      ]
    }
  },
  "playbook": {
    "version": 9,
    "created": "2025-11-10T18:00:00Z",
    "updated": "2025-12-28T07:10:00Z",
    "items": [
      {
        "eventId": "evt-0900",
        "targetId": "pb-latency-regression-triage",
        "operation": "append",
        "kind": "strategy",
        "title": "Triage latency regressions with a 3-signal check",
        "text": "When p95/p99 regresses, check (1) saturation (CPU/DB/queue), (2) error rate, (3) downstream latency. Avoid only scaling replicas until you confirm bottleneck.",
        "tags": ["reliability", "latency", "triage"],
        "evidence": ["INC-1988", "INC-2042"],
        "confidence": 0.9,
        "feedbackType": "executionOutcome",
        "status": "active",
        "createdAt": "2025-12-10T09:00:00Z",
        "reason": "Repeated incidents showed scaling alone delayed diagnosis"
      },
      {
        "eventId": "evt-0901",
        "targetId": "pb-latency-regression-triage",
        "operation": "update",
        "prevEventId": "evt-0900",
        "delta": {"helpfulCount": 2},
        "createdAt": "2025-12-28T07:05:00Z",
        "reason": "Applied successfully during INC-2042"
      },
      {
        "eventId": "evt-0910",
        "targetId": "pb-rollback-drill",
        "operation": "append",
        "kind": "rule",
        "title": "Always run a rollback drill after a risky change",
        "text": "For changes that alter processing topology (new worker pools, new queues), run a rollback drill in staging and record time-to-recover + missing steps in the runbook.",
        "tags": ["runbook", "rollback", "change-management"],
        "confidence": 0.95,
        "feedbackType": "humanReview",
        "status": "active",
        "createdAt": "2025-12-28T07:10:00Z",
        "reason": "Rollback procedures drift unless practiced"
      },
      {
        "eventId": "evt-0911",
        "targetId": "pb-scale-first-antipattern",
        "operation": "append",
        "kind": "warning",
        "title": "Anti-pattern: scale-first masking DB bottlenecks",
        "text": "If you scale replicas without bounding concurrency, you can amplify DB contention and worsen p99. Add queue bounds / rate limits before scaling.",
        "tags": ["anti-pattern", "database", "latency"],
        "confidence": 0.85,
        "status": "active",
        "createdAt": "2025-12-20T14:00:00Z",
        "reason": "Observed multiple times in load-related regressions"
      }
    ],
    "metrics": {
      "totalEntries": 3,
      "averageConfidence": 0.9,
      "lastUpdated": "2025-12-28T07:10:00Z"
    }
  }
}
```

---

# Appendix B: Outstanding Questions

This spec is intentionally iterative. The following open questions are candidates for future simplification or clarification.

1. **Do we need separate `references` and `uris`?**
   - Today: `uris` can point to anything (external URLs, files, other vContext documents), while `references` are vContext-only links.
   - Alternative: remove `references` entirely and rely on `uris` + a constrained `type` set for vContext document linking.

2. **Can we combine `changeLog` and Playbook events into one concept?**
   - Today: `changeLog` records document edits (create/update/fork/merge), while Playbooks use append-only PlaybookItem events to evolve long-term guidance.
   - Alternative: unify into a single append-only event log model with different event kinds/scopes (document mutation vs knowledge evolution), reducing duplicated machinery.

3. **Do we need recurring & reminders at all?**
   - Today: Extension 8 adds `recurrence` and `reminders` to support calendar-like automation.
   - Alternative: remove Extension 8 from core scope and rely on external scheduling systems + `uris` to link to them.

4. **Do we need `percentComplete`?**
   - It can be hard to define consistently for individual TodoItems.
   - For many uses, progress for TodoLists/Plans can be derived from item statuses (e.g., completed/total), optionally weighting blocked/cancelled.
   - Alternative: remove `percentComplete` and standardize derived progress calculations for containers and/or PlanItems only.

5. **Do we need the `timezone` field?**
   - Alternative: standardize on UTC timestamps only and let agents/apps display in local time when needed.
   - Counterpoint: explicit timezone can represent user intent for display/scheduling (especially for due dates and reminders).

6. **Would `progressing` be a better status name than `inProgress`?**
   - Potential benefit: shorter and more natural language.
   - Potential cost: breaking change across all documents/tools and less familiar than `inProgress`.

7. **Do we need both `id` and `uid` everywhere?**
   - Today: `id` is typically container-local, while `uid` is intended to be globally unique/stable for sync.
   - Alternative: standardize on one identifier concept for most entities, reserving dual identifiers only for append-only event logs.

8. **Should `narratives` remain a keyed object, or become `Narrative[]` with a `type` field?**
   - Today: `narratives` is an object with well-known keys (`proposal`, `problem`, `risks`, etc.) plus optional custom keys.
   - Alternative: model narratives as an array `{type, title, content}` to reduce schema surface area and avoid key proliferation.

9. **Should status enums be unified across types?**
   - Today: TodoItem/PlanItem share one enum, Plans have another, and PlaybookItems have a different lifecycle.
   - Alternative: unify where possible (or define a small base set + type-specific extensions) to simplify tooling.

10. **Do we need `blocked` / `cancelled` as first-class statuses?**
   - Alternative: treat these as tags or derived states, keeping the core status progression smaller.

11. **Do we need both `completed` timestamps and status transitions?**
   - Today: items can have `completed` timestamps and also have a terminal status (`completed`).
   - Alternative: infer completion timestamps from status transitions + `updated`, or standardize how tools set `completed`.

12. **Should containers support standardized derived metrics?**
   - Alternative: keep documents purely declarative and have tools compute progress/rollups (counts, rates) rather than storing them.
   - Counterpoint: stored metrics can speed up UIs and enable offline/low-cost summaries if clearly marked as derived.

13. **Should we support a .jsonl format for context streaming?**
   - Today: vContext documents are single JSON/TRON objects containing one container (TodoList, Plan, or Playbook).
   - Alternative: define a JSONL (JSON Lines) format where each line is a separate vContext document or container, enabling streaming consumption of large context collections.
   - Use cases: LLMs consuming multiple documents in sequence, batch processing, log-style append operations, large-scale context aggregation.
   - Consideration: how would this interact with cross-document references and container linking?

14. **Should TodoList be called TaskList?**
   - "Task" is a more general and widely-used term than "todo" in project management and software development.
   - "TodoList" clearly signals the immediate, action-oriented nature, but may sound less professional.
   - Alternative naming: TaskList/Task, WorkList/WorkItem, ActionList/Action.
   - Consideration: changing now would be a breaking change; however, TodoItem could be aliased to Task for familiarity.

---

# Appendix C: License

This specification is released under CC BY 4.0.
