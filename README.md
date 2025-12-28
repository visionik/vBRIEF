# vContext Specification v0.4

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

9. MAY enable **rapid adoption of new agentic research** (ACE, GEPA, System 3, etc.) via third-party tools built on vContext docs

10. MAY **also be used for non-AI tools** that work with todo lists, plans, and playbooks.

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
- **No interoperability guarantees**: One implementation can make Markdown unambiguous, but nothing guarantees consistent, non-ambiguous interpretation across implementations
- **Token inefficiency**: Markdown's human-optimized formatting consumes more tokens than structured formats
- **Inconsistent updates**: Modifying specific items requires regex/heuristics rather than direct field access, increasing error risk
- **No validation**: Invalid or malformed markdown is still valid markdown, making it easy to corrupt data

Markdown is still useful as a **generated output format** for humans, but vContext is intended to be the **canonical storage format** so tools can reliably query, validate, and update structured data across implementations.

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
    proposal: string      # Proposed solution (required)
  }
}
```

**Note**: All narratives in vContext use the same pattern: an object/map with string keys. Plans use lowercase keys (proposal, hypothesis, etc.) as defined in the standard narrative keys. Items (TodoItem, PlanItem, TodoList, Playbook) use Title Case keys (Background, Problem, etc.), allowing multiple narratives per item.

### PlanItem (Core)

**Purpose**: A stage of work within a plan (formerly called Phase). PlanItems organize execution into ordered steps and can be nested hierarchically (with extensions). Each item can have its own status and todo list. Execution order is determined by array position.

```javascript
PlanItem {
  title: string           # Item name
  status: enum            # "pending" | "inProgress" | "completed" | "blocked" | "cancelled"
}
```

**Note**: PlanItem extends the abstract `Item` base class (title + status required).

### Standard Narrative Keys

**Purpose**: Narratives are represented as objects/maps with string keys and markdown content values. vContext defines 13 standard keys that follow the **understand → design → execute → learn** workflow:

**Understand phase** (gathering context):
- **Overview** - High-level summary
- **Background** - Current state, prior work, and what exists today
- **Problem** - What needs fixing or addressing
- **Constraint** - Requirements, boundaries, and invariants that must be maintained

**Design phase** (planning solution):
- **Proposal** - Proposed solution or approach
- **Hypothesis** - Testable prediction or assumption
- **Alternative** - Other option considered (multiple alternatives can be captured as separate narratives)
- **Risk** - Potential issues and mitigations

**Execute phase** (taking action):
- **Test** - Validation approach or testing strategy
- **Action** - Execution or deployment strategy
- **Observation** - Raw data or factual observations from execution

**Learn phase** (capturing outcomes):
- **Result** - Interpreted outcomes and conclusions
- **Reflection** - Meta-cognitive analysis of the process itself

These titles provide a consistent vocabulary across all vContext entities. Tools MAY use these to provide structured workflows, but custom titles are always permitted.

### Playbook (Core)

**Purpose**: A collection of accumulated knowledge for **long-term memory**. Playbooks are designed to support *evolving contexts* via structured, incremental updates (generation → reflection → curation) and to avoid context collapse from monolithic rewrites.

vContext represents playbooks as an **append-only event log**: tools evolve guidance by appending new `PlaybookItem` events, optionally linking updates via `prevEventId`.

```javascript
Playbook {
  version: number          # Monotonic playbook version
  created: datetime        # When playbook was created
  updated: datetime        # Last update time
  items: PlaybookItem[]    # Append-only log of playbook events
  metrics?: object         # Optional summary fields
}
```

### PlaybookItem (Core)

**Purpose**: A single append-only event that creates, refines, or deprecates a logical playbook entry.

```javascript
PlaybookItem {
  eventId: string          # Unique id for this event
  targetId: string         # Stable id for the logical entry being evolved
  operation: enum          # "initial" | "append" | "update" | "deprecate"
  prevEventId?: string     # Prior eventId for this targetId (required for update/deprecate)
  kind?: enum              # "strategy" | "learning" | "rule" | "warning" | "note" (required for initial/append)

  title?: string           # Optional short label
  narrative?: object       # Narrative map (Title Case keys -> markdown strings)

  tags?: string[]
  evidence?: string[]
  confidence?: number      # 0.0–1.0
  delta?: object           # Merge-safe counters (e.g., helpfulCount/harmfulCount)
  feedbackType?: enum

  status?: enum            # "active" | "deprecated" | "quarantined"
  deprecatedReason?: string
  supersedes?: string[]
  supersededBy?: string
  duplicateOf?: string

  createdAt: datetime      # When this event was created
  reason?: string
  metadata?: object
}
```

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

vContextInfo: vContextInfo("0.4")
plan: Plan(
  "Add user authentication",
  "draft",
  {
    "proposal": "Implement JWT-based authentication with refresh tokens"
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
      "proposal": "Implement JWT-based authentication with refresh tokens"
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
class Playbook: version, created, updated, items
class PlaybookItem: eventId, targetId, operation, kind, narrative, createdAt, status

vContextInfo: vContextInfo("0.4")
playbook: Playbook(
  1,
  "2025-12-28T00:00:00Z",
  "2025-12-28T00:00:00Z",
  [
    PlaybookItem(
      "evt-0001",
      "entry-migrations-staging",
      "append",
      "rule",
      {"Overview": "Always run database migrations in staging before production to catch schema conflicts early."},
      "2025-12-28T00:00:00Z",
      "active"
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
    "version": 1,
    "created": "2025-12-28T00:00:00Z",
    "updated": "2025-12-28T00:00:00Z",
    "items": [
      {
        "eventId": "evt-0001",
        "targetId": "entry-migrations-staging",
        "operation": "append",
        "kind": "rule",
        "narrative": {
          "Overview": "Always run database migrations in staging before production to catch schema conflicts early."
        },
        "status": "active",
        "createdAt": "2025-12-28T00:00:00Z"
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

**Note on format**: Each example is shown in both JSON and TRON formats to demonstrate the token efficiency and readability differences.

## A1. TodoList (Operational Execution)

**TRON:**
```tron
class vContextInfo: version, author, description, created, updated, timezone, metadata
class TodoList: id, uid, title, narrative, tags, sequence, agent, lastModifiedBy, changeLog, uris, items
class Agent: id, type, name, email
class ChangeLogEntry: sequence, timestamp, agent, operation, reason
class URI: uri, type, title, description
class TodoItem: id, uid, title, status, narrative, priority, tags, created, updated, dueDate, percentComplete, timezone, participants, relatedComments, uris, classification, sequence, lastModifiedBy, lockedBy, dependencies, reminders, recurrence
class Participant: id, name, email, role, status
class Lock: agent, acquiredAt, type, expiresAt
class Reminder: trigger, action, description
class Recurrence: frequency, interval, byDay

vContextInfo: vContextInfo(
  "0.4",
  "Platform Team",
  "On-call followups for incident INC-2042",
  "2025-12-27T17:20:00Z",
  "2025-12-28T07:35:00Z",
  "America/Los_Angeles",
  {"extensions": ["timestamps", "identifiers", "rich-metadata", "hierarchical", "workflow", "participants", "resources", "recurring", "security", "version-control", "forking", "playbooks"]}
)

todoList: TodoList(
  "todo-inc-2042",
  "f7d2a4c6-1e3f-4d62-9c9a-3a2e8f4b1f10",
  "INC-2042: Payment webhook latency regression",
  {"Overview": "Follow-ups after incident. Goal: prevent recurrence and improve observability."},
  ["incident", "payments", "webhooks", "on-call"],
  12,
  Agent("human-jt", "human", "JT", "visionik@pobox.com"),
  Agent("agent-ops-bot", "system", "ops-bot", null),
  [
    ChangeLogEntry(10, "2025-12-28T06:50:00Z", Agent("agent-ops-bot", "system", "ops-bot", null), "update", "Auto-imported incident tasks from pager escalation"),
    ChangeLogEntry(12, "2025-12-28T07:35:00Z", Agent("human-jt", "human", "JT", null), "update", "Added rollback drill and recurring SLA review")
  ],
  [
    URI("https://status.example.com/incidents/INC-2042", "x-incident", "Incident timeline", "Primary incident record"),
    URI("file://./plans/payment-webhooks-plan.vcontext.json", "x-vcontext/plan", "Remediation plan", null),
    URI("file://./playbooks/platform-reliability-playbook.vcontext.json", "x-vcontext/playbook", "Reliability playbook", null)
  ],
  [
    TodoItem(
      "t1",
      "8c0d8b2f-2d08-4e4a-a34f-6a21f8f8a0b1",
      "Add p95/p99 alert for /webhooks/process",
      "inProgress",
      {"Background": "Alert on sustained p95>2s for 10m. Include saturation + queue depth as signals."},
      "critical",
      ["observability", "alerts"],
      "2025-12-28T06:55:00Z",
      "2025-12-28T07:30:00Z",
      "2025-12-29T02:00:00Z",
      40,
      "America/Los_Angeles",
      [
        Participant("human-jt", "JT", null, "owner", "accepted"),
        Participant("human-alex", "Alex", "alex@example.com", "contributor", "accepted")
      ],
      ["pr-comment-1842", "pr-comment-1849"],
      [URI("https://grafana.example.com/d/webhooks", "text/html", "Webhook dashboard", null)],
      "private",
      3,
      Agent("human-jt", "human", "JT", null),
      Lock(Agent("human-jt", "human", "JT", null), "2025-12-28T07:10:00Z", "soft", "2025-12-28T09:10:00Z"),
      null,
      null,
      null
    ),
    TodoItem(
      "t2",
      "b112f9e9-1c84-4b8b-9893-6a0b2a1a40f7",
      "Run rollback drill for payment-webhooks",
      "pending",
      {"Background": "Practice rollback procedure in staging; capture time-to-recover and gaps."},
      "high",
      ["runbook", "resilience"],
      "2025-12-28T07:33:00Z",
      "2025-12-28T07:33:00Z",
      "2025-12-30T18:00:00Z",
      null,
      null,
      null,
      null,
      [URI("file://./docs/rollback.md", "text/markdown", "Rollback runbook", null)],
      "confidential",
      null,
      null,
      null,
      ["t1"],
      [Reminder("-PT1H", "email", "Rollback drill in 1 hour")],
      null
    ),
    TodoItem(
      "t3",
      "61c0c8c1-1db5-4e4e-b5da-1b7cbb1b2c22",
      "Weekly: review webhook SLA + alert thresholds",
      "pending",
      {"Background": "Adjust for seasonal traffic. Ensure alert noise is acceptable."},
      "medium",
      ["recurring", "slo"],
      "2025-12-28T07:34:00Z",
      "2025-12-28T07:34:00Z",
      "2026-01-05T18:00:00Z",
      null,
      null,
      null,
      null,
      null,
      "private",
      null,
      null,
      null,
      null,
      [Reminder("-PT15M", "display", "SLA review starts in 15 minutes")],
      Recurrence("weekly", 1, ["MO"])
    )
  ]
)
```

**JSON:**
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
    "narrative": {
      "Overview": "Follow-ups after incident. Goal: prevent recurrence and improve observability."
    },
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
        "narrative": {
          "Background": "Alert on sustained p95>2s for 10m. Include saturation + queue depth as signals."
        },
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
        "narrative": {
          "Background": "Practice rollback procedure in staging; capture time-to-recover and gaps."
        },
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
        "narrative": {
          "Background": "Adjust for seasonal traffic. Ensure alert noise is acceptable."
        },
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

**TRON:**
```tron
class vContextInfo: version, author, description, created, updated, timezone, metadata
class Plan: id, uid, title, status, author, reviewers, tags, created, updated, timezone, sequence, agent, lastModifiedBy, changeLog, fork, narratives, references, uris, items
class Agent: id, type, name
class ChangeLogEntry: sequence, timestamp, agent, operation, reason
class Fork: parentUid, parentSequence, forkedAt, forkReason, mergeStatus
class URI: uri, type, title
class PlanItem: id, uid, title, status, narrative, tags, dependencies, startDate, percentComplete, participants, classification, todoList, subItems, location
class Participant: id, name, role, status
class TodoList: items
class TodoItem: title, status
class SubItem: id, title, status, dependencies, reminders, location
class Reminder: trigger, action, description
class Location: name, url

vContextInfo: vContextInfo(
  "0.4",
  "Platform Team",
  "Remediation plan for payment webhooks latency regression",
  "2025-12-27T18:00:00Z",
  "2025-12-28T07:20:00Z",
  "America/Los_Angeles",
  {"extensions": ["timestamps", "identifiers", "rich-metadata", "hierarchical", "workflow", "participants", "resources", "recurring", "security", "version-control", "forking", "playbooks"]}
)

plan: Plan(
  "plan-payment-webhooks",
  "b28c7d9d-22e7-4cd1-8f36-6d2ef2fbf12a",
  "Payment webhooks: reduce latency + prevent recurrence",
  "inProgress",
  "Platform Team",
  ["SRE Lead", "Payments TL"],
  ["payments", "webhooks", "reliability"],
  "2025-12-27T18:00:00Z",
  "2025-12-28T07:20:00Z",
  "America/Los_Angeles",
  7,
  Agent("human-jt", "human", "JT"),
  Agent("human-jt", "human", "JT"),
  [
    ChangeLogEntry(6, "2025-12-28T06:40:00Z", Agent("human-jt", "human", "JT"), "update", "Added load-test acceptance criteria and rollout plan"),
    ChangeLogEntry(7, "2025-12-28T07:20:00Z", Agent("human-jt", "human", "JT"), "update", "Expanded risks and rollback procedure")
  ],
  Fork("b28c7d9d-22e7-4cd1-8f36-6d2ef2fbf12a", 5, "2025-12-28T06:10:00Z", "Exploring alternative queueing strategy", "unmerged"),
  {
    "proposal": "1) Fix N+1 DB queries in webhook processing.\n2) Add queue-depth based autoscaling.\n3) Add p95/p99 alerts + dashboards.\n4) Add rollback drill + runbook improvements.",
    "problem": "Production latency regression increased webhook processing time from ~250ms to >2s p95 under load.",
    "background": "Webhook handler performs per-event DB lookups (N+1) and competes with background reconciliation jobs.",
    "constraint": "- No changes to webhook API contract\n- Must maintain exactly-once delivery guarantee\n- Zero downtime deployment required\n- SLA: p95 latency < 500ms",
    "hypothesis": "Moving reconciliation to separate worker pool will eliminate DB contention, reducing p95 latency by 60%+. Query batching will reduce DB round trips by 80%.",
    "alternative": "- Add more replicas only (insufficient: DB bottleneck)\n- Change DB isolation level (riskier)\n- Move reconciliation to separate worker pool (selected)",
    "risk": "- Changing worker pool may affect ordering guarantees\n- Autoscaling could amplify DB load if not bounded\nMitigations: rate limits, circuit breakers, staged rollout.",
    "test": "- Reproduce regression with load test\n- Confirm p95<400ms at 2x typical throughput\n- Run rollback drill in staging\n- Validate alert noise for 48h",
    "action": "1) Feature flag new worker pool\n2) Canary 5%\n3) Ramp 25% → 100%\n4) Post-deploy review at 24h",
    "observation": "After implementing changes:\n- p95 latency: 180ms (target: <400ms) ✓\n- p99 latency: 320ms (was 3200ms)\n- DB query count: reduced 78%\n- Zero webhook delivery failures during rollout",
    "reflection": "Load testing proved critical - caught queue saturation issue in staging. Should have profiled DB queries earlier to identify N+1 pattern sooner. Worker pool separation pattern worked well, consider for other high-throughput endpoints."
  },
  [
    URI("file://./todo/inc-2042-todo.vcontext.json", "x-vcontext/todoList", "Execution checklist"),
    URI("file://./playbooks/platform-reliability-playbook.vcontext.json", "x-vcontext/playbook", "Reliability playbook")
  ],
  [
    URI("https://github.com/org/repo/issues/2042", "x-github/issue", "INC-2042 issue"),
    URI("https://github.com/org/repo/pull/1842", "x-github/pr", "Fix N+1 queries"),
    URI("file://./services/webhooks/handler.ts", "text/plain", "Webhook handler"),
    URI("https://files.example.com/inc-2042/latency.png", "image/png", "Latency before/after")
  ],
  [
    PlanItem(
      "p1",
      "p1-uid",
      "Diagnose and fix root cause",
      "inProgress",
      {"Background": "Remove N+1 queries; isolate reconciliation job impact."},
      ["root-cause"],
      [],
      "2025-12-27T18:30:00Z",
      60,
      [Participant("human-jt", "JT", "owner", "accepted")],
      "private",
      TodoList([TodoItem("Add query batching", "inProgress"), TodoItem("Write regression load test", "pending")]),
      [
        SubItem("p1-1", "Fix N+1 DB lookups", "inProgress", [], [Reminder("-PT30M", "display", "PR review in 30 minutes")], null),
        SubItem("p1-2", "Split reconciliation to separate worker pool", "pending", ["p1-1"], null, Location("Remote", "https://zoom.example.com/room/ops"))
      ],
      null
    ),
    PlanItem(
      "p2",
      "p2-uid",
      "Observability + guardrails",
      "pending",
      {"Background": "Dashboards, alerts, SLOs, and bounded autoscaling."},
      null,
      ["p1"],
      null,
      null,
      [Participant("human-alex", "Alex", "assignee", "accepted")],
      "private",
      null,
      null,
      null
    ),
    PlanItem(
      "p3",
      "p3-uid",
      "Rollout + rollback drill",
      "pending",
      {"Background": "Canary rollout, validate rollback, and document runbook."},
      null,
      ["p1", "p2"],
      null,
      null,
      [
        Participant("human-jt", "JT", "owner", "accepted"),
        Participant("human-sre", "SRE Lead", "reviewer", "needsAction")
      ],
      "confidential",
      null,
      null,
      null
    )
  ]
)
```

**JSON:**
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
      "proposal": "1) Fix N+1 DB queries in webhook processing.\n2) Add queue-depth based autoscaling.\n3) Add p95/p99 alerts + dashboards.\n4) Add rollback drill + runbook improvements.",
      "problem": "Production latency regression increased webhook processing time from ~250ms to >2s p95 under load.",
      "background": "Webhook handler performs per-event DB lookups (N+1) and competes with background reconciliation jobs.",
      "constraint": "- No changes to webhook API contract\n- Must maintain exactly-once delivery guarantee\n- Zero downtime deployment required\n- SLA: p95 latency < 500ms",
      "hypothesis": "Moving reconciliation to separate worker pool will eliminate DB contention, reducing p95 latency by 60%+. Query batching will reduce DB round trips by 80%.",
      "alternative": "- Add more replicas only (insufficient: DB bottleneck)\n- Change DB isolation level (riskier)\n- Move reconciliation to separate worker pool (selected)",
      "risk": "- Changing worker pool may affect ordering guarantees\n- Autoscaling could amplify DB load if not bounded\nMitigations: rate limits, circuit breakers, staged rollout.",
      "test": "- Reproduce regression with load test\n- Confirm p95<400ms at 2x typical throughput\n- Run rollback drill in staging\n- Validate alert noise for 48h",
      "action": "1) Feature flag new worker pool\n2) Canary 5%\n3) Ramp 25% → 100%\n4) Post-deploy review at 24h",
      "observation": "After implementing changes:\n- p95 latency: 180ms (target: <400ms) ✓\n- p99 latency: 320ms (was 3200ms)\n- DB query count: reduced 78%\n- Zero webhook delivery failures during rollout",
      "reflection": "Load testing proved critical - caught queue saturation issue in staging. Should have profiled DB queries earlier to identify N+1 pattern sooner. Worker pool separation pattern worked well, consider for other high-throughput endpoints."
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
        "narrative": {
          "Background": "Remove N+1 queries; isolate reconciliation job impact."
        },
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
        "narrative": {
          "Background": "Dashboards, alerts, SLOs, and bounded autoscaling."
        },
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
        "narrative": {
          "Background": "Canary rollout, validate rollback, and document runbook."
        },
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

**TRON:**
```tron
class vContextInfo: version, author, description, created, updated, timezone, metadata
class Playbook: version, created, updated, items, metrics
class PlaybookItem: eventId, targetId, operation, prevEventId, kind, title, text, tags, evidence, confidence, feedbackType, status, createdAt, reason, delta
class Delta: helpfulCount, harmfulCount
class Metrics: totalEntries, averageConfidence, lastUpdated

vContextInfo: vContextInfo(
  "0.4",
  "Platform Team",
  "Reliability practices for latency regressions and incident followups",
  "2025-11-10T18:00:00Z",
  "2025-12-28T07:10:00Z",
  "America/Los_Angeles",
  {"extensions": ["timestamps", "identifiers", "rich-metadata", "version-control", "playbooks"]}
)

playbook: Playbook(
  9,
  "2025-11-10T18:00:00Z",
  "2025-12-28T07:10:00Z",
  [
    PlaybookItem(
      "evt-0900",
      "pb-latency-regression-triage",
      "append",
      null,
      "strategy",
      "Triage latency regressions with a 3-signal check",
      "When p95/p99 regresses, check (1) saturation (CPU/DB/queue), (2) error rate, (3) downstream latency. Avoid only scaling replicas until you confirm bottleneck.",
      ["reliability", "latency", "triage"],
      ["INC-1988", "INC-2042"],
      0.9,
      "executionOutcome",
      "active",
      "2025-12-10T09:00:00Z",
      "Repeated incidents showed scaling alone delayed diagnosis",
      null
    ),
    PlaybookItem(
      "evt-0901",
      "pb-latency-regression-triage",
      "update",
      "evt-0900",
      null,
      null,
      null,
      null,
      null,
      null,
      null,
      null,
      "2025-12-28T07:05:00Z",
      "Applied successfully during INC-2042",
      Delta(2, null)
    ),
    PlaybookItem(
      "evt-0910",
      "pb-rollback-drill",
      "append",
      null,
      "rule",
      "Always run a rollback drill after a risky change",
      "For changes that alter processing topology (new worker pools, new queues), run a rollback drill in staging and record time-to-recover + missing steps in the runbook.",
      ["runbook", "rollback", "change-management"],
      null,
      0.95,
      "humanReview",
      "active",
      "2025-12-28T07:10:00Z",
      "Rollback procedures drift unless practiced",
      null
    ),
    PlaybookItem(
      "evt-0911",
      "pb-scale-first-antipattern",
      "append",
      null,
      "warning",
      "Anti-pattern: scale-first masking DB bottlenecks",
      "If you scale replicas without bounding concurrency, you can amplify DB contention and worsen p99. Add queue bounds / rate limits before scaling.",
      ["anti-pattern", "database", "latency"],
      null,
      0.85,
      null,
      "active",
      "2025-12-20T14:00:00Z",
      "Observed multiple times in load-related regressions",
      null
    )
  ],
  Metrics(3, 0.9, "2025-12-28T07:10:00Z")
)
```

**JSON:**
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
        "narrative": {
          "Overview": "When p95/p99 regresses, check (1) saturation (CPU/DB/queue), (2) error rate, (3) downstream latency.",
          "Anti-pattern": "Avoid only scaling replicas until you confirm the bottleneck."
        },
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
        "narrative": {
          "Guidance": "For changes that alter processing topology (new worker pools, new queues), run a rollback drill in staging and record time-to-recover + missing steps in the runbook."
        },
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
        "narrative": {
          "Problem": "If you scale replicas without bounding concurrency, you can amplify DB contention and worsen p99.",
          "Mitigation": "Add queue bounds / rate limits before scaling."
        },
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

15. **Should we use 'namespaced' extensions in the JSON/TRON?**
   - Today: Extension fields are added directly to core types (flat structure), making it unclear which fields come from which extension.
   - Alternative: Group all extension fields within their own nested objects (e.g., `time`, `identity`, `meta`) for clear namespace separation.
   - Benefits: Clearer field ownership, easier feature detection, no naming conflicts, simpler validation.
   - Costs: 10-15% token increase in JSON, breaking change requiring migration, more complex access patterns.
   - See `vContext-alternative-namespaced.md` for detailed analysis and examples.

---

# Appendix C: License

This specification is released under CC BY 4.0.
