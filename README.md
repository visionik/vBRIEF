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

**Specification Version**: 0.3

**Last Updated**: 2025-12-27T19:16:00Z

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

## Conformance and normative language

The key words **MUST**, **SHOULD**, and **MAY** in this document are to be interpreted as normative requirements.

A document is **vContext Core v0.3 conformant** if:
- It is a single object containing `vContextInfo` and exactly one of `todoList`, `plan`, or `playbook`.
- `vContextInfo.version` MUST equal `"0.3"`.
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
1. **Core (MVA)**: Minimum Viable Agenda - essential fields only
2. **Extensions**: Optional feature modules that add capabilities
3. **Compatibility**: Extensions can be mixed and matched

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

**Document Structure**: A vContext document contains `vContextInfo` and either `todoList` or `plan`:
```javascript
{
  vContextInfo: vContextInfo,  # Document metadata (required)
  todoList?: TodoList,       # Either todoList...
  plan?: Plan                # ...or plan (not both)
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

## Core Examples

### Minimal TodoList

**TRON:**
```tron
class vContextInfo: version
class TodoList: items
class TodoItem: title, status

vContextInfo: vContextInfo("0.3")
todoList: TodoList([
  TodoItem("Implement authentication", "pending"),
  TodoItem("Write API documentation", "pending")
])
```

**JSON:**
```json
{
  "vContextInfo": {
    "version": "0.3"
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

vContextInfo: vContextInfo("0.3")
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
    "version": "0.3"
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

- `vContext-extension-playbooks.md` — Playbooks (long-term, evolving context)
- `vContext-extension-MCP.md` — Model Context Protocol (MCP) integration
- `vContext-extension-beads.md` — Beads integration
- `vContext-extension-claude.md` — Claude integration
- `vContext-extension-security.md` — Security extension
- `vContext-extension-api-go.md` — Go API extension
- `vContext-extension-api-python.md` — Python API extension
- `vContext-extension-api-typescript.md` — TypeScript API extension

## Extension 1: Timestamps

**Depends on:** Core only

Adds creation and modification tracking with timezone support.

### vContextInfo Extensions
```javascript
vContextInfo {
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
class vContextInfo: version, created, updated, timezone
class TodoList: items
class TodoItem: title, status, created, updated

vContextInfo: vContextInfo("0.3", "2024-12-27T09:00:00Z", "2024-12-27T10:00:00Z", "America/Los_Angeles")
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
  "vContextInfo": {
    "version": "0.3",
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

Adds stable identifiers for cross-referencing items and documents. Required for any extension that needs to reference or track relationships between entities.

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
class vContextInfo: version
class TodoList: id, items
class TodoItem: id, title, status

vContextInfo: vContextInfo("0.3")
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
  "vContextInfo": {
    "version": "0.3"
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

**Key atomic: Tagged** - The `tags` field can be added to ALL vContext entities (TodoList, TodoItem, Plan, PlanItem, Playbook, PlaybookItem, ProblemModel) for categorization and filtering. Tags enable flexible organization without rigid taxonomies.

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

Adds dependency tracking and nested (tree) structure for items.

### TodoItem Extensions
```javascript
TodoItem {
  // Core + Rich Metadata fields...
  dependencies?: string[]  # IDs of items that must complete first
}
```

### PlanItem Extensions
```javascript
PlanItem {
  // Core + Rich Metadata fields...
  dependencies?: string[] # IDs of items that must complete first
  subItems?: PlanItem[]   # Child items (nested hierarchy)
  todoList?: TodoList     # Associated todo list
}
```

### Example

**TRON:**
```tron
class vContextInfo: version
class TodoItem: id, title, status, dependencies
class Plan: id, title, status, narratives, items
class PlanItem: id, title, status, dependencies
class Narrative: title, content

vContextInfo: vContextInfo("0.3")
plan: Plan(
  "plan-002",
  "Build authentication system",
  "inProgress",
  {
    "proposal": Narrative(
      "Overview",
      "Multi-step authentication implementation"
    )
  },
  [
    PlanItem("item-1", "Database setup", "completed", []),
    PlanItem("item-2", "JWT implementation", "inProgress", ["item-1"]),
    PlanItem("item-3", "OAuth integration", "pending", ["item-2"])
  ]
)
```

**JSON:**
```json
{
  "vContextInfo": {
    "version": "0.3"
  },
  "plan": {
    "id": "plan-002",
  "title": "Build authentication system",
  "status": "inProgress",
  "narratives": {
    "proposal": {
      "title": "Overview",
      "content": "Multi-step authentication implementation"
    }
  },
  "items": [
    {
      "id": "item-1",
      "title": "Database setup",
      "status": "completed",
      "dependencies": []
    },
    {
      "id": "item-2",
      "title": "JWT implementation",
      "status": "inProgress",
      "dependencies": ["item-1"]
    },
    {
      "id": "item-3",
      "title": "OAuth integration",
      "status": "pending",
      "dependencies": ["item-2"]
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

VAgendaReference {
  # Same shape as URI, but MUST point to another vContext document.
  uri: string             # MUST be a URI to a vContext document (file:// or https://)
  type: enum              # MUST be one of:
                          #   "x-vcontext/todoList" | "x-vcontext/plan" | "x-vcontext/playbook"
  title?: string
  description?: string
  tags?: string[]
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
  uris?: URI[]                    # External resources OR other vContext documents
  references?: VAgendaReference[] # vContext-only links (subset of URI)
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

URIs enable linking related vContext documents without embedding them:

**JSON (Plan referencing TodoList):**
```json
{
  "vContextInfo": {"version": "0.3"},
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
        "uri": "file://./auth-tasks.vcontext.json",
        "type": "x-vcontext/todoList",
        "description": "Implementation tasks"
      }
    ]
  }
}
```

**JSON (TodoList with items referencing Plans):**
```json
{
  "vContextInfo": {"version": "0.3"},
  "todoList": {
    "items": [
      {
        "title": "Review auth plan",
        "status": "pending",
        "uris": [
          {
            "uri": "file://./auth-plan.vcontext.json",
            "type": "x-vcontext/plan"
          }
        ]
      },
      {
        "title": "Implement JWT",
        "status": "inProgress",
        "uris": [
          {
            "uri": "file://./auth-plan.vcontext.json#jwt-phase",
            "type": "x-vcontext/plan",
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

### Sequence: intended semantics

When present, `sequence` is a **revision counter** for a TodoList/Plan (and optionally for individual items) used for multi-writer safety.

- Producers SHOULD increment the container’s `sequence` on every change to the document.
- `sequence` MUST be monotonically non-decreasing.
- Consumers MAY use `sequence` for **optimistic concurrency** ("apply update only if sequence is still N").
- When combined with `changeLog` (and optional `snapshotUri`), `sequence` provides an audit-friendly way to refer to prior revisions.
- With Extension 11 (Forking), `fork.parentSequence` can be compared to the parent’s current `sequence` to detect parallel edits before merging.

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
  lastModifiedBy?: Agent  # Last agent to modify this item
}
```

### Example

**TRON:**
```tron
class vContextInfo: version
class TodoList: id, items, uid, agent, sequence, changeLog
class TodoItem: id, title, status
class Agent: id, type, name, model
class Change: sequence, timestamp, agent, operation, reason

vContextInfo: vContextInfo("0.3")
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
  "vContextInfo": {
    "version": "0.3"
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
class vContextInfo: version
class Plan: id, title, status, narratives, uid, fork
class Narrative: title, content
class Fork: parentUid, parentSequence, forkedAt, forkReason, mergeStatus

vContextInfo: vContextInfo("0.3")
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
  "vContextInfo": {
    "version": "0.3"
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

The Playbooks extension spec is in `vContext-extension-playbooks.md` (see that document for the full schema, invariants, merge semantics, and examples).

- **Requires**: Extension 2 (Identifiers)
- **Recommended**: Extension 10 (Version Control & Sync)

Playbooks add long-term memory via `playbook.items` as an append-only log of playbook items (each item has an `operation` and a per-item linked-list reference for updates/deprecations).

---

# Part 3: Format Encodings

## JSON Format

Standard JSON encoding with UTF-8. Use 2-space indentation for human readability.

## TRON Format

[TRON (Token Reduced Object Notation)](https://tron-format.github.io/) provides a more concise syntax using class definitions.

For the complete TRON specification, see: https://tron-format.github.io/

### Core TRON Classes

```tron
# vContextInfo (Core) - appears once per document at root level
class vContextInfo: version

# TodoList (Core)
class TodoList: items

# TodoItem (Core)
class TodoItem: title, status

# Plan (Core)
class Plan: title, status, narratives

# PlanItem (Core)
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
|| 12. Playbooks (`vContext-extension-playbooks.md`) | Identifiers, Version Control | None |

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
- Validate against `vContextInfo.version`.
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
See `vContext-extension-playbooks.md` for playbooks best practices (e.g. grow-and-refine, evidence linking, dedup, and append-only `operation` entries).

---

# Appendix A: Complete Examples (All Extensions)

These examples are intentionally "real-world" and include fields from **Core + Extensions 1–12**. Unknown fields are allowed and tools should preserve them.

## A1. TodoList (Operational Execution)

```json
{
  "vContextInfo": {
    "version": "0.3",
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
    "version": "0.3",
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
    "version": "0.3",
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

---

# Appendix C: License

This specification is released under CC BY 4.0.
