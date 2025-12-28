# vAgenda Specification v0.3

> **DRAFT SPECIFICATION**: This document is a draft and subject to change. Feedback, suggestions, and contributions from the community are highly encouraged. Please submit input via GitHub issues or pull requests.

Agentic coding systems increasingly rely on structured memory: **short-term memory** (todo lists for immediate tasks), **medium-term memory** (plans for project organization), and **long-term memory** (playbooks for accumulated strategies and learnings). However, proprietary formats used by different agentic systems hamper interoperability and limit cross-agent collaboration.

vAgenda provides an **open, standardized format** for these memory systems that is:
- **Agent-friendly**: Token-efficient TRON encoding optimized for LLM workflows
- **Human-readable**: Clear structure for direct/TUI/GUI editing and review
- **Interoperable**: JSON compatibility for integration with existing tools
- **Extensible**: Modular architecture supports simple to complex use cases

This enables both agentic systems and human-facing tools to share a common representation of work, plans, and accumulated knowledge.

**Origins and Scope**:
- This specification is based on a review of internal memory formats used by several different agentic coding systems
- The design is inspired by established standards such as vCard and vCalendar/iCalendar
- While primarily intended for agentic coding, the spec is secondarily usable as an interop format for almost any todo, task, or project management software

**Specification Version**: 0.3

**Last Updated**: 2025-12-27T19:16:00Z

**Author**: Jonathan Taylor (visionik@pobox.com)

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

## Conformance and normative language

The key words **MUST**, **SHOULD**, and **MAY** in this document are to be interpreted as normative requirements.

A document is **vAgenda Core v0.3 conformant** if:
- It is a single object containing `vAgendaInfo` and exactly one of `todoList` or `plan`.
- `vAgendaInfo.version` MUST equal `"0.3"`.
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
- Within a single container, `id` values MUST be unique (e.g., within `todoList.items`, within `plan.phases`).
- `uid` values (when present) SHOULD be globally unique and stable across copies.
- `sequence` values (when present) MUST be monotonically non-decreasing for a given document.

## Machine-verifiable schemas (JSON)

This spec includes JSON Schema files intended for validation and tooling:
- Core schema: `schemas/vagenda-core.schema.json`
- Playbooks extension schema: `schemas/vagenda-extension-playbooks.schema.json`

## Design Philosophy

vAgenda uses a **modular, layered architecture**:
1. **Core (MVA)**: Minimum Viable Agenda - essential fields only
2. **Extensions**: Optional feature modules that add capabilities
3. **Compatibility**: Extensions can be mixed and matched

This prevents complexity overload while supporting advanced use cases.

## Why Two Formats? TRON and JSON

vAgenda supports both TRON and JSON encodings. **TRON is the preferred format** for AI/agent workflows due to its token efficiency, with JSON included for wider compatibility with existing tools and systems.

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
- **Use case fit**: TOON excels at flat tabular data; vAgenda's hierarchical structures suit TRON better

**Note**: Both JSON and TRON are lossless representations of the same data model.

## Architecture Layers

```
┌─────────────────────────────────────┐
│   Extensions (Optional Modules)     │
│  ┌─────────────── ──────────────┐   │
│  │  Collaboration, Playbooks, etc. │   │
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
│   Plan, PlanItem                    │
└─────────────────────────────────────┘
```

---

# Part 1: Core (Minimum Viable Agenda)

## Design Principles

- **Format-agnostic**: Support both JSON and [TRON](https://tron-format.github.io/) encodings
- **Minimal**: Only essential fields in core
- **Extensible**: Easy to add fields via extensions or metadata
- **Compatible**: All extensions are backward compatible with core

## Core Data Models

### When to Use TodoList vs Plan

**TodoList** is for **immediate execution** — tracking tasks that need to be done now or soon:
- Simple, flat list of action items
- Focus on "what" needs to be done, not "why" or "how"
- Short lifecycle (hours to days)
- Examples: daily tasks, sprint backlog, debugging checklist

**Plan** is for **coordination and documentation** — organizing complex work with context:
- Requires explanation of approach, rationale, or design
- Multi-phase work that needs to be broken down
- Needs review, approval, or stakeholder communication
- Medium lifecycle (days to weeks/months)
- Examples: feature implementation plans, refactoring proposals, architectural designs

**Rule of thumb**: If you find yourself wanting to explain "why" or document the approach, use a Plan. If you just need to track "what" to do, use a TodoList.

### vAgendaInfo (Core)

**Purpose**: Document-level metadata that appears once per file, as a sibling to the main content object (TodoList or Plan). Contains version information and optional authorship details.

```javascript
vAgendaInfo {
  version: string          # Schema version (e.g., "0.2")
  author?: string          # Document creator
  description?: string     # Brief document description
  metadata?: object        # Custom document-level fields
}
```

**Document Structure**: A vAgenda document contains `vAgendaInfo` and either `todoList` or `plan`:
```javascript
{
  vAgendaInfo: vAgendaInfo,  # Document metadata (required)
  todoList?: TodoList,       # Either todoList...
  plan?: Plan                # ...or plan (not both)
}
```

**Cross-document references**: Containers and items MAY reference other vAgenda documents or external resources using URIs (see Extension 7). This allows related containers to be linked without embedding them in a single file:
```javascript
// Plan referencing a separate TodoList document
{
  vAgendaInfo: {...},
  plan: {
    title: "Feature Implementation",
    uris: [{uri: "file://./tasks.vagenda.json", type: "x-vagenda/todoList"}],
    ...
  }
}

// TodoItem referencing a Plan document
{
  vAgendaInfo: {...},
  todoList: {
    items: [
      {
        title: "Implement auth feature",
        uris: [{uri: "file://./auth-plan.vagenda.json", type: "x-vagenda/plan"}]
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

**Purpose**: A single actionable task with status tracking. The fundamental unit of work in vAgenda.

```javascript
TodoItem {
  title: string            # Brief summary (required)
  status: enum             # "pending" | "inProgress" | "completed" | "blocked" | "cancelled"
}
```

### Plan (Core)

**Purpose**: A structured design document for **medium-term memory**. Used to organize projects, document approaches, and coordinate multi-phase work. Plans can contain phases and reference other resources.

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

## Core Examples

### Minimal TodoList

**TRON:**
```tron
class vAgendaInfo: version
class TodoList: items
class TodoItem: title, status

vAgendaInfo: vAgendaInfo("0.2")
todoList: TodoList([
  TodoItem("Implement authentication", "pending"),
  TodoItem("Write API documentation", "pending")
])
```

**JSON:**
```json
{
  "vAgendaInfo": {
    "version": "0.2"
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
class vAgendaInfo: version
class Plan: title, status, narratives, items
class PlanItem: title, status
class Narrative: title, content

vAgendaInfo: vAgendaInfo("0.2")
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
  "vAgendaInfo": {
    "version": "0.2"
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

---

# Part 2: Extensions

Extensions add optional fields to core types. Implementations can support any combination.

## Extension documents

Some extensions have dedicated spec documents:

- `vAgenda-extension-playbooks.md` — Playbooks (long-term, evolving context)
- `vAgenda-extension-MCP.md` — Model Context Protocol (MCP) integration
- `vAgenda-extension-beads.md` — Beads integration
- `vAgenda-extension-claude.md` — Claude integration
- `vAgenda-extension-security.md` — Security extension
- `vAgenda-extension-api-go.md` — Go API extension
- `vAgenda-extension-api-python.md` — Python API extension
- `vAgenda-extension-api-typescript.md` — TypeScript API extension

## Extension 1: Timestamps

**Depends on:** Core only

Adds creation and modification tracking with timezone support.

### vAgendaInfo Extensions
```javascript
vAgendaInfo {
  // Core fields...
  created: datetime        # ISO 8601 timestamp (UTC default)
  updated: datetime        # ISO 8601 timestamp (UTC default)
  timezone?: string        # IANA timezone (defaults to UTC if not specified)
}
```

### TodoItem Extensions
```javascript
TodoItem {
  // Core fields...
  created: datetime        # ISO 8601 timestamp (UTC default)
  updated: datetime        # ISO 8601 timestamp (UTC default)
}
```

### Example

**TRON:**
```tron
class vAgendaInfo: version, created, updated, timezone
class TodoList: items
class TodoItem: title, status, created, updated

vAgendaInfo: vAgendaInfo("0.2", "2024-12-27T09:00:00Z", "2024-12-27T10:00:00Z", "America/Los_Angeles")
todoList: TodoList([
  TodoItem(
    "Implement authentication",
    "pending",
    "2024-12-27T09:00:00Z",
    "2024-12-27T09:30:00Z"
  ),
  TodoItem(
    "Write tests",
    "pending",
    "2024-12-27T10:00:00Z",
    "2024-12-27T10:00:00Z"
  )
])
```

**JSON:**
```json
{
  "vAgendaInfo": {
    "version": "0.2",
    "created": "2024-12-27T09:00:00Z",
    "updated": "2024-12-27T10:00:00Z",
    "timezone": "America/Los_Angeles"
  },
  "todoList": {
    "items": [
      {
        "title": "Implement authentication",
        "status": "pending",
        "created": "2024-12-27T09:00:00Z",
        "updated": "2024-12-27T09:30:00Z"
      },
      {
        "title": "Write tests",
        "status": "pending",
        "created": "2024-12-27T10:00:00Z",
        "updated": "2024-12-27T10:00:00Z"
      }
    ]
  }
}
```

## Extension 2: Identifiers

**Depends on:** Core only

Adds stable identifiers for cross-referencing items, phases, and documents. Required for any extension that needs to reference or track relationships between entities.

### TodoList Extensions
```javascript
TodoList {
  // Core fields...
  id: string               # Unique identifier
}
```

### TodoItem Extensions
```javascript
TodoItem {
  // Core fields...
  id: string               # Unique identifier within list
}
```

### Plan Extensions
```javascript
Plan {
  // Core fields...
  id: string              # Unique identifier
}
```

### PlanItem Extensions
```javascript
PlanItem {
  // Core fields...
  id: string              # Unique identifier within plan
}
```

### Example

**TRON:**
```tron
class vAgendaInfo: version
class TodoList: id, items
class TodoItem: id, title, status

vAgendaInfo: vAgendaInfo("0.2")
todoList: TodoList(
  "todo-001",
  [
    TodoItem("item-1", "Implement authentication", "pending"),
    TodoItem("item-2", "Write API documentation", "inProgress")
  ]
)
```

**JSON:**
```json
{
  "vAgendaInfo": {
    "version": "0.2"
  },
  "todoList": {
    "id": "todo-001",
    "items": [
      {
        "id": "item-1",
        "title": "Implement authentication",
        "status": "pending"
      },
      {
        "id": "item-2",
        "title": "Write API documentation",
        "status": "inProgress"
      }
    ]
  }
}
```

## Extension 3: Rich Metadata

**Depends on:** Core only

Adds descriptive and organizational fields.

**Key atomic: Tagged** - The `tags` field can be added to ALL vAgenda entities (TodoList, TodoItem, Plan, PlanItem, Playbook, PlaybookItem, ProblemModel) for categorization and filtering. Tags enable flexible organization without rigid taxonomies.

### TodoList Extensions
```javascript
TodoList {
  // Core fields...
  title?: string           # Optional list title
  description?: string     # Detailed description
  tags?: string[]          # Categorical labels
  metadata?: object        # Custom fields
}
```

### TodoItem Extensions
```javascript
TodoItem {
  // Core fields...
  description?: string     # Detailed context
  priority?: enum          # "low" | "medium" | "high" | "critical"
  tags?: string[]          # Categorical labels
  metadata?: object        # Custom fields
}
```

### Plan Extensions
```javascript
Plan {
  // Core fields...
  author?: string          # Creator
  reviewers?: string[]     # Approvers
  description?: string     # Plan overview
  tags?: string[]          # Categorical labels
  narratives: {
    proposal: Narrative,
    problem?: Narrative,     # Problem statement
    context?: Narrative,     # Current state
    alternatives?: Narrative,# Other approaches
    risks?: Narrative,       # Risks and mitigations
    testing?: Narrative,     # Validation approach
    rollout?: Narrative,     # Deployment strategy
    custom?: Narrative[]     # User-defined narratives
  }
  metadata?: object        # Custom fields
}
```

### PlanItem Extensions
```javascript
PlanItem {
  // Core fields...
  description?: string     # Item description
  tags?: string[]          # Categorical labels
  metadata?: object        # Custom fields
}
```

### Example

**TRON:**
```tron
class TodoItem: id, title, status, description, priority, tags, metadata

TodoItem(
  "item-2",
  "Implement JWT authentication",
  "inProgress",
  "Add JWT token generation and validation for secure API access",
  "high",
  ["security", "backend", "auth"],
  {"estimatedHours": 8, "complexity": "medium"}
)
```

**JSON:**
```json
{
  "id": "item-2",
  "title": "Implement JWT authentication",
  "status": "inProgress",
  "description": "Add JWT token generation and validation for secure API access",
  "priority": "high",
  "tags": ["security", "backend", "auth"],
  "metadata": {
    "estimatedHours": 8,
    "complexity": "medium"
  }
}
```

## Extension 4: Hierarchical Structures

**Depends on:** Extension 2 (Identifiers)

Adds nested organization and dependencies.

### TodoItem Extensions
```javascript
TodoItem {
  // Core + Rich Metadata fields...
  dependencies?: string[]  # IDs of items that must complete first
}
```

### Plan Extensions
```javascript
Plan {
  // Core + Rich Metadata fields...
  items?: PlanItem[]         # Implementation phases
}
```

### PlanItem Extensions
```javascript
PlanItem {
  // Core + Rich Metadata fields...
  dependencies?: string[] # IDs of phases that must complete first
  subItems?: PlanItem[]     # Child phases (nested hierarchy)
  todoList?: TodoList     # Associated todo list
}
```

### Example

**TRON:**
```tron
class vAgendaInfo: version
class TodoItem: id, title, status, dependencies
class Plan: id, title, status, narratives, phases
class PlanItem: id, title, status, dependencies
class Narrative: title, content

vAgendaInfo: vAgendaInfo("0.2")
plan: Plan(
  "plan-002",
  "Build authentication system",
  "inProgress",
  {
    "proposal": Narrative(
      "Overview",
      "Multi-phase authentication implementation"
    )
  },
  [
    PlanItem("phase-1", "Database setup", "completed", []),
    PlanItem("phase-2", "JWT implementation", "inProgress", ["phase-1"]),
    PlanItem("phase-3", "OAuth integration", "pending", ["phase-2"])
  ]
)
```

**JSON:**
```json
{
  "vAgendaInfo": {
    "version": "0.2"
  },
  "plan": {
    "id": "plan-002",
  "title": "Build authentication system",
  "status": "inProgress",
  "narratives": {
    "proposal": {
      "title": "Overview",
      "content": "Multi-phase authentication implementation"
    }
  },
  "phases": [
    {
      "id": "phase-1",
      "title": "Database setup",
      "status": "completed",
      "dependencies": []
    },
    {
      "id": "phase-2",
      "title": "JWT implementation",
      "status": "inProgress",
      "dependencies": ["phase-1"]
    },
    {
      "id": "phase-3",
      "title": "OAuth integration",
      "status": "pending",
      "dependencies": ["phase-2"]
    }
  ]
}
```

## Extension 5: Workflow & Scheduling

**Depends on:** Core only

Adds time tracking, progress, and team coordination.

### TodoItem Extensions
```javascript
TodoItem {
  // Prior extensions...
  dueDate?: datetime       # When item should be completed
  completed?: datetime     # When item was completed
  percentComplete?: number # 0-100, progress indicator
  timezone?: string        # IANA timezone (defaults to UTC if not specified)
}
```

### PlanItem Extensions
```javascript
PlanItem {
  // Prior extensions...
  startDate?: datetime    # Planned or actual start
  endDate?: datetime      # Planned or actual end
  percentComplete?: number # 0-100, can be aggregate or manual
  timezone?: string       # IANA timezone (defaults to UTC if not specified)
}
```

### Example

**TRON:**
```tron
class TodoItem: id, title, status, dueDate, completed, percentComplete, timezone

TodoItem(
  "item-3",
  "Complete API documentation",
  "completed",
  "2024-12-30T17:00:00Z",
  "2024-12-29T16:45:00Z",
  100,
  "America/New_York"
)
```

**JSON:**
```json
{
  "id": "item-3",
  "title": "Complete API documentation",
  "status": "completed",
  "dueDate": "2024-12-30T17:00:00Z",
  "completed": "2024-12-29T16:45:00Z",
  "percentComplete": 100,
  "timezone": "America/New_York"
}
```

## Extension 6: Participants & Collaboration

**Depends on:** Extension 2 (Identifiers) — for `relatedComments` field

Adds multi-user/agent support.

### New Types
```javascript
Participant {
  id: string              # Unique identifier
  name?: string           # Display name
  email?: string          # Email address
  role: enum              # "owner" | "assignee" | "reviewer" | "observer" | "contributor"
  status?: enum           # "accepted" | "declined" | "tentative" | "needsAction"
}
```

### TodoItem Extensions
```javascript
TodoItem {
  // Prior extensions...
  participants?: Participant[] # People involved with roles
  relatedComments?: string[] # Comment IDs from code review
}
```

### PlanItem Extensions
```javascript
PlanItem {
  // Prior extensions...
  participants?: Participant[] # People involved with roles
}
```

### Example

**TRON:**
```tron
class TodoItem: id, title, status, participants, relatedComments
class Participant: id, name, email, role, status

TodoItem(
  "item-4",
  "Review authentication PR",
  "inProgress",
  [
    Participant("alice", "Alice Smith", "alice@example.com", "owner", "accepted"),
    Participant("bob", "Bob Jones", "bob@example.com", "reviewer", "accepted")
  ],
  ["comment-123", "comment-456"]
)
```

**JSON:**
```json
{
  "id": "item-4",
  "title": "Review authentication PR",
  "status": "inProgress",
  "participants": [
    {
      "id": "alice",
      "name": "Alice Smith",
      "email": "alice@example.com",
      "role": "owner",
      "status": "accepted"
    },
    {
      "id": "bob",
      "name": "Bob Jones",
      "email": "bob@example.com",
      "role": "reviewer",
      "status": "accepted"
    }
  ],
  "relatedComments": ["comment-123", "comment-456"]
}
```

## Extension 7: Resources & References

**Depends on:** Core only

Adds URIs and location tracking.

### New Types
```javascript
URI {
  uri: string             # The URI/URL (required)
  description?: string    # Human-readable description
  type?: string           # MIME type or custom (e.g., "application/pdf", "x-conferencing/zoom")
  title?: string          # Short title
  tags?: string[]         # Categorical labels
}

Location {
  name?: string           # Human-readable name
  address?: string        # Physical address
  geo?: [number, number]  # [latitude, longitude]
  url?: string            # Link to location info
}

Reference {
  type: enum              # "file" | "line" | "range" | "url" | "issue" | "pr"
  path?: string           # File path or URL
  line?: number           # Single line number
  start?: number          # Range start
  end?: number            # Range end
  description?: string    # What this references
}

Attachment {
  name: string            # Filename
  type: string            # MIME type
  path?: string           # Local path
  url?: string            # Remote URL
  encoding?: string       # "base64" | "utf8" | etc.
  data?: string           # Inline content
}
```

### TodoList Extensions
```javascript
TodoList {
  // Core fields...
  uris?: URI[]            # References to other containers or resources
}
```

### TodoItem Extensions
```javascript
TodoItem {
  // Prior extensions...
  uris?: URI[]            # References to other containers or resources
}
```

### PlanItem Extensions
```javascript
PlanItem {
  // Prior extensions...
  location?: Location     # Physical location for work
  uris?: URI[]            # References to other containers or resources
}
```

### Plan Extensions
```javascript
Plan {
  // Prior extensions...
  uris?: URI[]            # References to other containers or resources
  references?: Reference[] # Files, lines, URLs, issues
  attachments?: Attachment[] # Diagrams, configs, etc.
}
```

### Example: External Resources

**TRON:**
```tron
class TodoItem: id, title, status, uris
class URI: uri, description, type, title

TodoItem(
  "item-5",
  "Update API documentation",
  "pending",
  [
    URI("https://docs.example.com/api", "Current API docs", "text/html", "API Docs"),
    URI("https://github.com/org/repo/issues/42", "Related issue", "x-github/issue", "Issue #42")
  ]
)
```

**JSON:**
```json
{
  "id": "item-5",
  "title": "Update API documentation",
  "status": "pending",
  "uris": [
    {
      "uri": "https://docs.example.com/api",
      "description": "Current API docs",
      "type": "text/html",
      "title": "API Docs"
    },
    {
      "uri": "https://github.com/org/repo/issues/42",
      "description": "Related issue",
      "type": "x-github/issue",
      "title": "Issue #42"
    }
  ]
}
```

### Example: Cross-Container References

URIs enable linking related vAgenda documents without embedding them:

**JSON (Plan referencing TodoList):**
```json
{
  "vAgendaInfo": {"version": "0.3"},
  "plan": {
    "title": "Authentication System",
    "status": "inProgress",
    "narratives": {
      "proposal": {
        "title": "Overview",
        "content": "Implement JWT-based auth"
      }
    },
    "uris": [
      {
        "uri": "file://./auth-tasks.vagenda.json",
        "type": "x-vagenda/todoList",
        "description": "Implementation tasks"
      }
    ]
  }
}
```

**JSON (TodoList with items referencing Plans):**
```json
{
  "vAgendaInfo": {"version": "0.3"},
  "todoList": {
    "items": [
      {
        "title": "Review auth plan",
        "status": "pending",
        "uris": [
          {
            "uri": "file://./auth-plan.vagenda.json",
            "type": "x-vagenda/plan"
          }
        ]
      },
      {
        "title": "Implement JWT",
        "status": "inProgress",
        "uris": [
          {
            "uri": "file://./auth-plan.vagenda.json#jwt-phase",
            "type": "x-vagenda/plan",
            "description": "JWT implementation phase"
          }
        ]
      }
    ]
  }
}
```

## Extension 8: Recurring & Reminders

**Depends on:** Extension 5 (Workflow & Scheduling) — for scheduling contexts

Adds time-based automation.

### New Types
```javascript
RecurrenceRule {
  frequency: enum         # "daily" | "weekly" | "monthly" | "yearly"
  interval?: number       # Every N periods (default: 1)
  until?: datetime        # End date for recurrence
  count?: number          # Number of occurrences
  byDay?: string[]        # Days of week: ["MO", "TU", "WE", "TH", "FR", "SA", "SU"]
  byMonth?: number[]      # Months: [1-12]
  byMonthDay?: number[]   # Days of month: [1-31]
}

Reminder {
  trigger: string         # ISO 8601 duration (e.g., "-PT15M" = 15 min before)
  action: enum            # "display" | "email" | "webhook" | "audio"
  description?: string    # Reminder message
}
```

### TodoItem Extensions
```javascript
TodoItem {
  // Prior extensions...
  recurrence?: RecurrenceRule # For recurring tasks
  reminders?: Reminder[]   # Notifications before due date
}
```

### PlanItem Extensions
```javascript
PlanItem {
  // Prior extensions...
  reminders?: Reminder[]  # Notifications for phase milestones
}
```

### Example

**TRON:**
```tron
class TodoItem: id, title, status, dueDate, recurrence, reminders
class RecurrenceRule: frequency, interval, byDay
class Reminder: trigger, action, description

TodoItem(
  "item-6",
  "Weekly team sync",
  "pending",
  "2024-12-30T15:00:00Z",
  RecurrenceRule("weekly", 1, ["MO"]),
  [
    Reminder("-PT15M", "display", "Team sync starts in 15 minutes"),
    Reminder("-PT1H", "email", "Prepare agenda for team sync")
  ]
)
```

**JSON:**
```json
{
  "id": "item-6",
  "title": "Weekly team sync",
  "status": "pending",
  "dueDate": "2024-12-30T15:00:00Z",
  "recurrence": {
    "frequency": "weekly",
    "interval": 1,
    "byDay": ["MO"]
  },
  "reminders": [
    {
      "trigger": "-PT15M",
      "action": "display",
      "description": "Team sync starts in 15 minutes"
    },
    {
      "trigger": "-PT1H",
      "action": "email",
      "description": "Prepare agenda for team sync"
    }
  ]
}
```

## Extension 9: Security & Privacy

**Depends on:** Core only

Adds access control and data classification.

### TodoItem Extensions
```javascript
TodoItem {
  // Prior extensions...
  classification?: enum    # "public" | "private" | "confidential"
}
```

### PlanItem Extensions
```javascript
PlanItem {
  // Prior extensions...
  classification?: enum   # "public" | "private" | "confidential"
}
```

### Example

**TRON:**
```tron
class TodoItem: id, title, status, classification

TodoItem(
  "item-7",
  "Review security audit findings",
  "inProgress",
  "confidential"
)
```

**JSON:**
```json
{
  "id": "item-7",
  "title": "Review security audit findings",
  "status": "inProgress",
  "classification": "confidential"
}
```

## Extension 10: Version Control & Sync

**Depends on:** Extension 2 (Identifiers) — for `uid` and `relatedChanges` fields

Adds cross-system sync and conflict resolution.

### New Types
```javascript
Agent {
  id: string              # Unique agent identifier
  type: enum              # "human" | "aiAgent" | "system"
  name?: string           # Display name
  email?: string          # Contact for humans
  model?: string          # AI model identifier (e.g., "claude-3.5-sonnet")
  version?: string        # Agent software version
}

Change {
  sequence: number        # Sequence number for this change
  timestamp: datetime     # When change occurred
  agent: Agent            # Who made the change
  operation: enum         # "create" | "update" | "delete" | "fork" | "merge"
  reason?: string         # Why this change was made (strongly recommended)
  path?: string           # JSONPath to changed field
  oldValue?: any          # Previous value
  newValue?: any          # New value
  description?: string    # Human-readable change description
  snapshotUri?: string    # URI to full document snapshot at this sequence
  relatedChanges?: string[] # References to related changes
}
```

### TodoList Extensions
```javascript
TodoList {
  // Prior extensions...
  uid?: string             # Globally unique identifier (for cross-system sync)
  agent?: Agent            # Agent/user who owns this
  lastModifiedBy?: Agent   # Last agent to modify
  changeLog?: Change[]     # History of modifications
  sequence?: number        # Revision counter
}
```

### TodoItem Extensions
```javascript
TodoItem {
  // Prior extensions...
  uid?: string             # Globally unique identifier
  sequence?: number        # Revision counter
  lastModifiedBy?: Agent   # Last agent to modify this item
}
```

### Plan Extensions
```javascript
Plan {
  // Prior extensions...
  uid?: string            # Globally unique identifier
  agent?: Agent           # Agent/user who owns this
  lastModifiedBy?: Agent  # Last agent to modify
  changeLog?: Change[]    # History of modifications
  sequence?: number       # Revision counter
}
```

### PlanItem Extensions
```javascript
PlanItem {
  // Prior extensions...
  uid?: string            # Globally unique identifier
  sequence?: number       # Revision counter
  lastModifiedBy?: Agent  # Last agent to modify this phase
}
```

### Example

**TRON:**
```tron
class vAgendaInfo: version
class TodoList: id, items, uid, agent, sequence, changeLog
class TodoItem: id, title, status
class Agent: id, type, name, model
class Change: sequence, timestamp, agent, operation, reason

vAgendaInfo: vAgendaInfo("0.2")
todoList: TodoList(
  "todo-002",
  [
    TodoItem("item-8", "Sync tasks across devices", "completed")
  ],
  "550e8400-e29b-41d4-a716-446655440000",
  Agent("agent-1", "aiAgent", "Claude", "claude-3.5-sonnet"),
  3,
  [
    Change(1, "2024-12-27T10:00:00Z", Agent("agent-1", "aiAgent", "Claude", null), "create", "Initial creation"),
    Change(2, "2024-12-27T10:30:00Z", Agent("agent-1", "aiAgent", "Claude", null), "update", "Added new item"),
    Change(3, "2024-12-27T11:00:00Z", Agent("agent-1", "aiAgent", "Claude", null), "update", "Marked item completed")
  ]
)
```

**JSON:**
```json
{
  "vAgendaInfo": {
    "version": "0.2"
  },
  "todoList": {
    "id": "todo-002",
  "items": [
    {
      "id": "item-8",
      "title": "Sync tasks across devices",
      "status": "completed"
    }
  ],
  "uid": "550e8400-e29b-41d4-a716-446655440000",
  "agent": {
    "id": "agent-1",
    "type": "aiAgent",
    "name": "Claude",
    "model": "claude-3.5-sonnet"
  },
  "sequence": 3,
  "changeLog": [
    {
      "sequence": 1,
      "timestamp": "2024-12-27T10:00:00Z",
      "agent": {
        "id": "agent-1",
        "type": "aiAgent",
        "name": "Claude"
      },
      "operation": "create",
      "reason": "Initial creation"
    },
    {
      "sequence": 2,
      "timestamp": "2024-12-27T10:30:00Z",
      "agent": {
        "id": "agent-1",
        "type": "aiAgent",
        "name": "Claude"
      },
      "operation": "update",
      "reason": "Added new item"
    },
    {
      "sequence": 3,
      "timestamp": "2024-12-27T11:00:00Z",
      "agent": {
        "id": "agent-1",
        "type": "aiAgent",
        "name": "Claude"
      },
      "operation": "update",
      "reason": "Marked item completed"
    }
  ]
  }
}
```

## Extension 11: Multi-Agent Forking

**Depends on:** Extension 10 (Version Control & Sync) — for `uid`, `Agent`, and change tracking

Adds parallel work and merge support.

### New Types
```javascript
Fork {
  parentUid: string       # UID of the parent document
  parentSequence: number  # Sequence number when forked
  forkedAt: datetime      # When this fork was created
  forkReason?: string     # Why this fork was created
  mergeStatus?: enum      # "unmerged" | "mergePending" | "merged" | "conflict"
  mergedAt?: datetime     # When merged back to parent
  mergedBy?: Agent        # Who performed the merge
  conflictResolution?: ConflictResolution
}

ConflictResolution {
  strategy: enum          # "ours" | "theirs" | "manual" | "threeWayMerge"
  conflicts: Conflict[]   # List of conflicts found
  resolvedBy?: Agent      # Who resolved conflicts
  resolvedAt?: datetime   # When conflicts were resolved
}

Conflict {
  path: string            # JSONPath to conflicting field
  baseValue: any          # Value in common ancestor
  oursValue: any          # Value in our fork
  theirsValue: any        # Value in their fork/parent
  resolution?: any        # Resolved value if resolved
  status: enum            # "unresolved" | "resolved" | "deferred"
}

Lock {
  agent: Agent            # Who holds the lock
  acquiredAt: datetime    # When lock was acquired
  expiresAt?: datetime    # When lock expires
  type: enum              # "soft" | "hard"
}
```

### TodoList Extensions
```javascript
TodoList {
  // Prior extensions...
  fork?: Fork              # If this is a fork, track the parent
}
```

### TodoItem Extensions
```javascript
TodoItem {
  // Prior extensions...
  lockedBy?: Lock          # If claimed by an agent
}
```

### Plan Extensions
```javascript
Plan {
  // Prior extensions...
  fork?: Fork             # If this is a fork, track the parent
}
```

### PlanItem Extensions
```javascript
PlanItem {
  // Prior extensions...
  lockedBy?: Lock         # If claimed by an agent
}
```

### Example

**TRON:**
```tron
class vAgendaInfo: version
class Plan: id, title, status, narratives, uid, fork
class Narrative: title, content
class Fork: parentUid, parentSequence, forkedAt, forkReason, mergeStatus

vAgendaInfo: vAgendaInfo("0.2")
plan: Plan(
  "plan-fork-001",
  "Authentication - Alternative approach",
  "inProgress",
  {"proposal": Narrative("Alternative", "Try OAuth2 instead of JWT")},
  "660e8400-e29b-41d4-a716-446655440001",
  Fork(
    "550e8400-e29b-41d4-a716-446655440000",
    5,
    "2024-12-27T12:00:00Z",
    "Exploring alternative authentication approach",
    "unmerged"
  )
)
```

**JSON:**
```json
{
  "vAgendaInfo": {
    "version": "0.2"
  },
  "plan": {
    "id": "plan-fork-001",
  "title": "Authentication - Alternative approach",
  "status": "inProgress",
  "narratives": {
    "proposal": {
      "title": "Alternative",
      "content": "Try OAuth2 instead of JWT"
    }
  },
  "uid": "660e8400-e29b-41d4-a716-446655440001",
  "fork": {
    "parentUid": "550e8400-e29b-41d4-a716-446655440000",
    "parentSequence": 5,
    "forkedAt": "2024-12-27T12:00:00Z",
    "forkReason": "Exploring alternative authentication approach",
    "mergeStatus": "unmerged"
  }
  }
}
```

## Extension 12: Playbooks

The Playbooks extension spec is in `vAgenda-extension-playbooks.md` (see that document for the full schema, invariants, merge semantics, and examples).

- **Requires**: Extension 2 (Identifiers)
- **Recommended**: Extension 10 (Version Control & Sync)

Playbooks add long-term memory via `playbook.entries` as an append-only log of playbook entries (each entry has an `operation` and a per-entry linked-list reference for updates/deprecations).

---

# Part 3: Format Encodings

## JSON Format

Standard JSON encoding with UTF-8. Use 2-space indentation for human readability.

## TRON Format

[TRON (Token Reduced Object Notation)](https://tron-format.github.io/) provides a more concise syntax using class definitions.

For the complete TRON specification, see: https://tron-format.github.io/

### Core TRON Classes

```tron
# vAgendaInfo (Core) - appears once per document at root level
class vAgendaInfo: version

# TodoList (Core)
class TodoList: items

# TodoItem (Core)
class TodoItem: title, status

# Plan (Core)
class Plan: title, status, narratives

# Phase (Core)
class PlanItem: title, status

# Narrative (Core)
class Narrative: title, content
```

### Extension TRON Classes

Implementations define only the classes for extensions they support.

---

# Part 4: Extension Compatibility Matrix

| Extension | Depends On | Conflicts With |
|-----------|------------|----------------|
| 1. Timestamps | Core | None |
| 2. Identifiers | Core | None |
| 3. Rich Metadata | Core | None |
| 4. Hierarchical | Identifiers | None |
| 5. Workflow | Core | None |
| 6. Participants | Identifiers | None |
| 7. Resources | Core | None |
| 8. Recurring | Workflow | None |
| 9. Security | Core | None |
| 10. Version Control | Identifiers | None |
| 11. Forking | Version Control | None |
|| 12. Playbooks (`vAgenda-extension-playbooks.md`) | Identifiers, Version Control | None |

---

# Part 5: Best Practices

## Core Usage

1. **IDs**: Use UUIDs or timestamp-based IDs for uniqueness
2. **Timestamps**: Always use ISO 8601 format with timezone (UTC default)
3. **Status**: Update status field before updating timestamps
4. **Minimal Start**: Begin with core, add extensions as needed

## Extension Guidelines

5. **Selective Adoption**: Only implement extensions you need
6. **Document Usage**: Clearly indicate which extensions are used in your implementation
7. **Metadata Escape Hatch**: Use `metadata` for one-off custom fields
8. **Version Field**: Include schema version to track core + extension compatibility

## File naming conventions

- TodoLists: `todo-<identifier>.<format>` or `<name>-todo.<format>`
  - Examples: `todo-001.json`, `auth-feature-todo.tron`
- Plans: `plan-<identifier>.<format>` or `<name>-plan.<format>`
  - Examples: `plan-001.json`, `microservices-plan.tron`
- Prefer hyphens (not underscores) in filenames.

## Status transitions

These are the intended lifecycles; tools should avoid inventing additional statuses.

### TodoItem status flow

```
pending → inProgress → completed
    ↓          ↓            ↓
  blocked → cancelled    (terminal)
    ↓
  pending (after unblock)
```

### Plan status flow

```
draft → proposed → approved → inProgress → completed
   ↓        ↓          ↓           ↓            ↓
        cancelled (any stage)                (terminal)
```

## Versioning & migrations

When the spec changes:
- Increment **major** version for breaking changes.
- Increment **minor** version for backward-compatible additions.

Implementation guidance:
- Tools should handle unknown fields gracefully.
- Tools should preserve unknown fields during updates (don’t drop extension data).
- Provide migration utilities for version upgrades where possible.

## Tooling integration

### For agentic development environments

Tools should:
- Read and write both JSON and TRON formats.
- Validate against `vAgendaInfo.version`.
- Preserve unknown fields during updates.
- Generate unique IDs (UUIDs or similar) when using identifiers.
- Update timestamps automatically when timestamp fields are present.
- Support partial updates (patching) where possible.

### For human workflows

Editors should:
- Syntax highlight both formats.
- Validate on save.
- Provide templates/snippets for new documents.
- Support format conversion (JSON ↔ TRON).
- Show warnings for missing required fields.

## Extension-Specific Best Practices

### Rich Metadata
- Keep titles brief (<80 chars), use description for details
- Use tags consistently across documents

### Hierarchical
- Validate dependency graphs are acyclic
- Limit nesting depth to 3-4 levels for maintainability

### Workflow
- Update percentComplete automatically when possible
- Set realistic due dates

### Participants
- Use explicit roles for clarity
- Include contact info for humans

### Resources
- Use standard MIME types when available
- For non-file resources, use x- prefixed types (e.g., "x-conferencing/zoom")
- Prefer relative paths for files in same repository

### Version Control
- Increment sequence on every change
- Always provide `reason` in changes to document "why"
- Optionally store snapshots at key sequences

### Forking
- Set fork.parentUid and fork.parentSequence when forking
- Check if parentSequence < parent.sequence before merging
- Use three-way merge for conflict detection

### Playbooks
See `vAgenda-extension-playbooks.md` for playbooks best practices (e.g. grow-and-refine, evidence linking, dedup, and append-only `operation` entries).

---

# Appendix A: Complete Example with Extensions

## Plan with Multiple Extensions

```json
{
  "vAgendaInfo": {
    "version": "0.2",
    "created": "2024-12-27T00:00:00Z",
    "updated": "2024-12-27T10:00:00Z"
  },
  "plan": {
    "id": "plan-001",
    "uid": "20241227T000000Z-123456@example.com",
    "title": "Implement microservices architecture",
    "description": "Migrate from monolith to microservices",
    "status": "inProgress",
    "author": "Architecture Team",
    "sequence": 5,

    "narratives": {
      "proposal": {
        "title": "Proposed Changes",
        "content": "Split into three services: auth, api, worker"
      },
      "problem": {
        "title": "Problem Statement",
        "content": "Monolith limits scalability"
      }
    },

    "phases": [
      {
        "id": "phase-1",
        "uid": "phase-1-uid",
        "title": "Foundation",
        "description": "Set up infrastructure",
        "order": 1,
        "status": "completed",
        "startDate": "2024-12-01T00:00:00Z",
        "endDate": "2024-12-15T00:00:00Z",
        "percentComplete": 100,
        "participants": [
          {
            "id": "backend-team",
            "name": "Backend Team",
            "role": "owner",
            "status": "accepted"
          }
        ]
      }
    ],

    "playbook": {
      "version": 1,
      "created": "2024-12-01T00:00:00Z",
      "updated": "2024-12-27T10:00:00Z",
      "entries": [
        {
          "id": "entry-001",
          "kind": "strategy",
          "title": "Parallel Phase Execution",
          "text": "Run independent phases in parallel when they don’t share hard dependencies",
          "confidence": 0.95,
          "helpfulCount": 3,
          "harmfulCount": 0,
          "feedbackType": "executionOutcome",
          "status": "active",
          "tags": ["performance"]
        }
      ],
      "metrics": {
        "totalEntries": 1,
        "averageConfidence": 0.95,
        "lastUpdated": "2024-12-27T10:00:00Z"
      }
    },

    "metadata": {
      "extensions": [
        "rich-metadata",
        "hierarchical",
        "workflow",
        "participants",
        "version-control",
        "playbooks"
      ],
      "customField": "custom value"
    }
  }
}
```

This example uses:
- **Core**: Basic structure
- **Rich Metadata**: title, description, author
- **Hierarchical**: phases array
- **Workflow**: dates, percentComplete
- **Participants**: team assignment
- **Version Control**: uid, sequence
- **Playbooks**: playbook with entries

---

# Appendix B: License

This specification is released under CC BY 4.0.
