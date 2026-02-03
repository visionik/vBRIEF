# vBRIEF: Atomic TRON Classes Proposal

**Date**: 2025-12-27  
**Status**: Draft Proposal  
**Purpose**: Define atomic/base TRON classes that TodoList, Plan, Playbook, and ProblemModel compose from

## Overview

This document proposes a set of atomic TRON classes that capture common patterns across vBRIEF's core data structures. By defining these atomic classes, we can:
- Reduce duplication in type definitions
- Make composition patterns explicit
- Simplify extension definitions
- Enable polymorphic operations on common abstractions

## Composition Rules

**All vBRIEF entities MUST:**
- Be **Titled** (have `title` and optional `description`)

**All vBRIEF lifecycle entities (TodoList, TodoItem, Plan, Phase, Playbook, PlaybookEntry) MUST:**
- Be **Statused** (have lifecycle `status`)

**Exception**: ProblemModel is a pure specification/structure (not lifecycle-tracked), so it is Titled but NOT Statused. However, its children (Entity, StateVar, Action, Constraint, Goal) ARE both Titled and Statused.

**All vBRIEF entities MAY (via extensions):**
- Be **Identifiable** (have stable `id`) — Extension 2
- Be **Timestamped** (have `created`/`updated`) — Extension 1
- Be **Versioned** (have `version`/`sequence`) — Extension 10
- Be **Extensible** (have `metadata` escape hatch) — Extension 3
- Be **Tagged** (have `tags` array for categorization) — Extension 3

**Specialized atomics (optional, type-specific):**
- Be **Evidenced** (have `confidence`, `evidence`, `tags`) — PlaybookEntry, specific extensions
- Be **Scheduled** (have temporal fields) — Extension 5
- Be **Collaborative** (have `participants`) — Extension 6

This creates a clear two-tier system:
1. **Core tier** (required): Titled + Statused
2. **Extension tier** (optional): Identifiable + Timestamped + Versioned + Extensible + type-specific

## Atomic Base Classes

### Core Tier (REQUIRED)

These atomics MUST be present in all vBRIEF entities.

#### Titled

**Purpose**: Entity with human-readable name and optional description.

```tron
class Titled: title, description
```

**Fields**:
- `title: string` (required) - Brief, human-readable summary
- `description: string` (optional) - Detailed context or explanation

**Used by**: ALL vBRIEF entities (TodoList, TodoItem, Plan, Phase, Playbook, PlaybookEntry, ProblemModel)

**Rationale**: Every vBRIEF entity must be understandable to humans and agents. A title is the minimum viable description. The description field provides an escape hatch for additional context without requiring new fields.

---

#### Statused

**Purpose**: Entity with lifecycle status tracking.

```tron
class Statused: status
```

**Fields**:
- `status: enum` (required) - Current lifecycle state

**Status enum variants by type**:
- **TodoItem/Phase/PlaybookEntry**: `"pending" | "inProgress" | "completed" | "blocked" | "cancelled"`
- **Plan**: `"draft" | "proposed" | "approved" | "inProgress" | "completed" | "cancelled"`
- **PlaybookEntry** (alternate): `"active" | "deprecated" | "quarantined"`
- **TodoList/Playbook**: Status inferred from items/entries (no explicit status)
- **ProblemModel**: No explicit status (structural, not lifecycle-tracked)

**Used by**: ALL vBRIEF entities except containers (TodoList, Playbook) and pure structures (ProblemModel)

**Rationale**: Status is the primary mechanism for tracking progress and filtering. Making it required ensures all actionable entities have clear lifecycle states. Container status is derivable from children.

---

#### Item (Abstract Base for Contained Entities)

**Purpose**: Abstract base class for all entities that are contained within collections.

```tron
class Item: Titled, Statused
```

**Composes**: Titled + Statused (both required)

**Used by**: TodoItem, Phase (as PlanItem), PlaybookEntry (as PlaybookItem)

**Rationale**: TodoItem, Phase, and PlaybookEntry share a common pattern - they are all:
- Discrete, actionable or knowledge units
- Contained within parent collections (TodoList, Plan, Playbook)
- Titled and Statused entities
- The "many" in a one-to-many relationship

By making this pattern explicit with an abstract `Item` base class, we:
1. **Clarify the abstraction**: Tools can treat all Items polymorphically
2. **Enable generic operations**: Search, filter, sort across any Item type
3. **Simplify composition**: New contained types just extend Item
4. **Document intent**: Clear that these are contained, actionable entities

**Naming convention**: Concrete item types use pattern `<Container>Item`:
- TodoList contains **TodoItem** (already correct)
- Plan contains **PlanItem** (rename from Phase)
- Playbook contains **PlaybookItem** (rename from PlaybookEntry)

**Note**: This is a breaking change that requires renaming Phase → PlanItem and PlaybookEntry → PlaybookItem. Migration path provided in implementation notes.

---

### Extension Tier (OPTIONAL)

These atomics MAY be added via extensions.

#### Identifiable (Extension 2)

**Purpose**: Any entity that needs a stable identifier for cross-referencing.

```tron
class Identifiable: id
```

**Fields**:
- `id: string` (required when present) - Unique identifier within container

**Used by**: All entities when Extension 2 (Identifiers) is active

**Rationale**: IDs enable referencing, relationships, and dependencies. Not required in core to support simple use cases (e.g., quick todo lists without IDs).

**Special case**: PlaybookEntry uses dual identifiers:
```tron
class EventIdentifiable: eventId, targetId
```
- `eventId` - unique identifier for this append-only event
- `targetId` - stable identifier for the logical entry being evolved

---

#### Timestamped (Extension 1)

**Purpose**: Track creation and modification times.

```tron
class Timestamped: created, updated
```

**Fields**:
- `created: datetime` (required when present) - ISO 8601 timestamp of creation
- `updated: datetime` (required when present) - ISO 8601 timestamp of last modification

**Used by**: All entities when Extension 1 (Timestamps) is active

**Rationale**: Timestamps enable temporal queries, sorting, and audit trails. Not required in core to minimize token usage for simple cases.

**Variant for append-only structures**:
```tron
class TimestampedSingle: createdAt
```
Used by PlaybookEntry (append-only, never modified).

---

#### Versioned (Extension 10)

**Purpose**: Track revision/sequence number for concurrency control.

```tron
class Versioned: version
class Sequenced: sequence
```

**Fields**:
- `version: number` (containers like Playbook) - Monotonically increasing version number
- `sequence: number` (versioned documents like Plan, TodoList) - Revision counter for sync

**Used by**: Containers (TodoList, Plan, Playbook) when Extension 10 (Version Control) is active

**Rationale**: Version/sequence numbers enable optimistic concurrency, conflict detection, and sync protocols. Not required in core for single-user or stateless scenarios.

---

#### Extensible (Extension 3)

**Purpose**: Allow arbitrary custom fields via metadata escape hatch.

```tron
class Extensible: metadata
```

**Fields**:
- `metadata: object` (optional) - Arbitrary key-value pairs for custom extensions

**Used by**: All entities when Extension 3 (Rich Metadata) is active

**Rationale**: Provides forward compatibility and allows one-off custom fields without spec changes. The `metadata` field is the designated escape hatch for experimentation.

---

#### Tagged (Extension 3)

**Purpose**: Categorize and label entities with arbitrary tags for filtering and organization.

```tron
class Tagged: tags
```

**Fields**:
- `tags: string[]` (optional) - Array of categorical labels (e.g., `["security", "urgent", "backend"]`)

**Used by**: All entities when Extension 3 (Rich Metadata) is active

**Rationale**: Tags enable flexible categorization without rigid taxonomies. Essential for filtering, searching, and grouping across vBRIEF documents. Common use cases:
- TodoItem: `["bug", "security", "p0"]`
- Plan: `["architecture", "q1-2025"]`
- Phase: `["database", "migration"]`
- PlaybookEntry: `["testing", "debugging"]`
- Playbook: `["backend", "best-practices"]`

---

### Specialized Atomics (TYPE-SPECIFIC)

These atomics apply to specific entity types or extensions.

#### Evidenced (PlaybookEntry, Extension 12)

**Purpose**: Assertion backed by evidence, confidence, and feedback.

```tron
class Evidenced: confidence, evidence, tags, feedbackType
```

**Fields**:
- `confidence: number` (0.0-1.0) - Certainty in this assertion
- `evidence: string[]` - References to supporting evidence
- `tags: string[]` - Categorical labels
- `feedbackType: enum` - How confidence was determined

**Used by**: PlaybookEntry (Extension 12)

**Rationale**: Playbooks are evidence-based knowledge repositories. Tracking confidence and evidence enables filtering by quality and maintaining provenance.

---

## Composition Examples

### TodoList Composition

**Current Definition**:
```javascript
TodoList {
  // Core (REQUIRED)
  title: string              # MUST be titled
  status: enum               # MUST be statused (container - inferred from items)
  items: TodoItem[]          # TodoList-specific
  // Extension 2: Identifiers (OPTIONAL)
  id?: string
  // Extension 1: Timestamps (OPTIONAL)
  created?: datetime
  updated?: datetime
  // Extension 3: Rich Metadata (OPTIONAL)
  description?: string
  metadata?: object
  // Extension 10: Version Control (OPTIONAL)
  uid?: string
  sequence?: number
}
```

**Composed from Atomics**:
```tron
# Core tier (REQUIRED)
class Titled: title, description
class Statused: status

# Extension tier (OPTIONAL)
class Identifiable: id
class Timestamped: created, updated
class Sequenced: sequence
class Extensible: metadata

# TodoList = Core + Extensions + specific fields
class TodoListCore: Titled, items
class TodoListFull: Titled, Identifiable, Timestamped, Sequenced, Extensible, items
```

**TRON Instance (Core - minimal)**:
```tron
class TodoListCore: Titled, items

TodoListCore(
  "Sprint 42 Tasks",             # title (Titled - REQUIRED)
  [                              # items (TodoList-specific)
    TodoItem("Implement JWT", "inProgress"),
    TodoItem("Add tests", "pending")
  ]
)
```

**TRON Instance (Full - with all extensions)**:
```tron
class TodoListFull: Titled, Identifiable, Timestamped, Sequenced, Extensible, items

TodoListFull(
  "Sprint 42 Tasks",             # title (Titled - REQUIRED)
  "Tasks for Q1 sprint",         # description (Titled - OPTIONAL)
  "todo-001",                    # id (Identifiable - Extension 2)
  "2024-12-27T10:00:00Z",        # created (Timestamped - Extension 1)
  "2024-12-27T12:00:00Z",        # updated (Timestamped - Extension 1)
  3,                             # sequence (Sequenced - Extension 10)
  {"project": "auth-service"},   # metadata (Extensible - Extension 3)
  [                              # items (TodoList-specific)
    TodoItem("item-1", "Implement JWT", "inProgress"),
    TodoItem("item-2", "Add tests", "pending")
  ]
)
```

---

### TodoItem Composition

**Current Definition**:
```javascript
TodoItem {
  // Core (REQUIRED)
  title: string              # MUST be titled
  status: enum               # MUST be statused
  // Extension 2: Identifiers (OPTIONAL)
  id?: string
  // Extension 1: Timestamps (OPTIONAL)
  created?: datetime
  updated?: datetime
  // Extension 3: Rich Metadata (OPTIONAL)
  description?: string
  priority?: enum
  tags?: string[]
  metadata?: object
}
```

**Composed from Atomics**:
```tron
# Core (REQUIRED) - TodoItem extends Item
class Item: Titled, Statused
class TodoItemCore: Item

# Full (with extensions)
class TodoItemFull: Item, Identifiable, Timestamped, Tagged, Extensible, priority
```

**TRON Instance (Core - minimal)**:
```tron
class Item: Titled, Statused
class TodoItemCore: Item

TodoItemCore(
  "Implement JWT authentication", # title (REQUIRED)
  "inProgress"                    # status (REQUIRED)
)
```

**TRON Instance (Full - with extensions)**:
```tron
class TodoItemFull: Titled, Statused, Identifiable, Timestamped, Tagged, Extensible, priority

TodoItemFull(
  "Implement JWT authentication",              # title (REQUIRED)
  "Add token generation and validation",       # description (OPTIONAL)
  "inProgress",                                 # status (REQUIRED)
  "item-1",                                     # id (Extension 2)
  "2024-12-27T10:00:00Z",                       # created (Extension 1)
  "2024-12-27T11:30:00Z",                       # updated (Extension 1)
  ["security", "backend", "auth"],             # tags (Extension 3 - Tagged)
  {"estimatedHours": 8},                        # metadata (Extension 3 - Extensible)
  "high"                                        # priority (Extension 3)
)
```

---

### Plan Composition

**Current Definition**:
```javascript
Plan {
  // Core (REQUIRED)
  title: string              # MUST be titled
  status: enum               # MUST be statused
  narratives: {...}          # Plan-specific (proposal required)
  // Extension 2: Identifiers (OPTIONAL)
  id?: string
  // Extension 1: Timestamps (OPTIONAL)
  created?: datetime
  updated?: datetime
  // Extension 3: Rich Metadata (OPTIONAL)
  description?: string
  author?: string
  reviewers?: string[]
  metadata?: object
  // Extension 4: Hierarchical (OPTIONAL)
  items?: PlanItem[]         # Renamed from phases, contains PlanItem (formerly Phase)
  // Extension 10: Version Control (OPTIONAL)
  sequence?: number
}
```

**Composed from Atomics**:
```tron
# Core (REQUIRED)
class PlanCore: Titled, Statused, narratives

# Full (with extensions)
class PlanFull: Titled, Statused, Identifiable, Timestamped, Sequenced, Tagged, Extensible, 
                narratives, items, author, reviewers
```

**TRON Instance (Core - minimal)**:
```tron
class PlanCore: Titled, Statused, narratives

PlanCore(
  "Microservices Migration",                     # title (REQUIRED)
  "approved",                                     # status (REQUIRED)
  {                                               # narratives (REQUIRED)
    "proposal": "Migrate to microservices..."
  }
)
```

**TRON Instance (Full - with extensions)**:
```tron
class PlanFull: Titled, Statused, Identifiable, Timestamped, Sequenced, Tagged, Extensible, 
                narratives, items, author, reviewers

PlanFull(
  "Microservices Migration",                     # title (REQUIRED)
  "Split monolith into services",                # description (OPTIONAL)
  "approved",                                     # status (REQUIRED)
  "plan-001",                                     # id (Extension 2)
  "2024-12-01T00:00:00Z",                         # created (Extension 1)
  "2024-12-27T10:00:00Z",                         # updated (Extension 1)
  7,                                              # sequence (Extension 10)
  ["architecture", "migration", "q1-2025"],      # tags (Extension 3)
  {"budget": 100000},                             # metadata (Extension 3)
  {                                               # narratives (REQUIRED)
    "proposal": "Migrate to microservices...",
    "problem": "Monolith doesn't scale..."
  },
  [                                               # items (Extension 4) - PlanItem[]
    PlanItem("Foundation", "completed"),
    PlanItem("Migration", "inProgress")
  ],
  "Architecture Team",                            # author (Extension 3)
  ["Alice", "Bob"]                                # reviewers (Extension 3)
)
```

---

### PlanItem Composition (formerly Phase)

**Current Definition**:
```javascript
PlanItem {  // Renamed from Phase
  // Core (REQUIRED)
  title: string              # MUST be titled
  status: enum               # MUST be statused
  // Extension 2: Identifiers (OPTIONAL)
  id?: string
  // Extension 1: Timestamps (OPTIONAL)
  created?: datetime
  updated?: datetime
  // Extension 3: Rich Metadata (OPTIONAL)
  description?: string
  metadata?: object
  // Extension 4: Hierarchical (OPTIONAL)
  dependencies?: string[]
  subItems?: PlanItem[]      # Renamed from subPhases
  todoList?: TodoList
}
```

**Composed from Atomics**:
```tron
# Core (REQUIRED) - PlanItem extends Item
class Item: Titled, Statused
class PlanItemCore: Item

# Full (with extensions)
class PlanItemFull: Item, Identifiable, Timestamped, Tagged, Extensible, 
                    dependencies, subItems, todoList
```

**TRON Instance (Core - minimal)**:
```tron
class Item: Titled, Statused
class PlanItemCore: Item

PlanItemCore(
  "Foundation Setup",            # title (REQUIRED)
  "completed"                    # status (REQUIRED)
)
```

**TRON Instance (Full - with extensions)**:
```tron
class PlanItemFull: Item, Identifiable, Timestamped, Tagged, Extensible, 
                    dependencies, subItems, todoList

PlanItemFull(
  "Foundation Setup",                    # title (REQUIRED)
  "Infrastructure provisioning",         # description (OPTIONAL)
  "completed",                           # status (REQUIRED)
  "phase-1",                             # id (Extension 2)
  "2024-12-01T00:00:00Z",                # created (Extension 1)
  "2024-12-15T00:00:00Z",                # updated (Extension 1)
  ["infrastructure", "devops"],          # tags (Extension 3)
  {"team": "devops"},                    # metadata (Extension 3)
  [],                                    # dependencies (Extension 4)
  null,                                  # subItems (Extension 4)
  TodoList(...)                          # todoList (Extension 4)
)
```

---

### Playbook Composition

**Current Definition**:
```javascript
Playbook {
  // Core (REQUIRED)
  title: string              # MUST be titled (container title)
  status: enum               # Container status (inferred from items)
  items: PlaybookItem[]      # Renamed from entries, contains PlaybookItem (formerly PlaybookEntry)
  // Extension 1: Timestamps (OPTIONAL)
  created?: datetime
  updated?: datetime
  // Extension 10: Version Control (OPTIONAL)
  version?: number
  // Playbook-specific
  metrics?: PlaybookMetrics
}
```

**Composed from Atomics**:
```tron
# Core (REQUIRED) - Playbook is a titled container
class PlaybookCore: Titled, items

# Full (with extensions)
class PlaybookFull: Titled, Timestamped, Versioned, items, metrics
```

**TRON Instance (Core - minimal)**:
```tron
class PlaybookCore: Titled, items

PlaybookCore(
  "Auth System Playbook",        # title (REQUIRED)
  [                              # items (Playbook-specific)
    PlaybookItem(...),
    PlaybookItem(...)
  ]
)
```

**TRON Instance (Full - with extensions)**:
```tron
class PlaybookFull: Titled, Timestamped, Versioned, Tagged, items, metrics

PlaybookFull(
  "Auth System Playbook",        # title (REQUIRED)
  "Best practices for auth",     # description (OPTIONAL)
  "2024-01-10T00:00:00Z",        # created (Extension 1)
  "2024-12-27T10:00:00Z",        # updated (Extension 1)
  4,                             # version (Extension 10)
  ["backend", "security"],       # tags (Extension 3)
  [                              # items (Playbook-specific)
    PlaybookItem(...),
    PlaybookItem(...)
  ],
  PlaybookMetrics(...)           # metrics (Playbook-specific)
)
```

---

### PlaybookItem Composition (formerly PlaybookEntry)

**Current Definition**:
```javascript
PlaybookItem {  // Renamed from PlaybookEntry
  // Core (REQUIRED)
  title: string              # MUST be titled (or text if title absent)
  status: enum               # MUST be statused ("active" | "deprecated" | "quarantined")
  // PlaybookItem-specific identity (REQUIRED)
  eventId: string            # Unique event identifier
  targetId: string           # Stable logical entry identifier
  operation: enum            # "initial" | "append" | "update" | "deprecate"
  // Extension 1: Timestamps (OPTIONAL)
  createdAt?: datetime
  // Extension 12: Evidence (OPTIONAL but recommended)
  kind?: enum
  text?: string
  tags?: string[]
  evidence?: string[]
  confidence?: number
  delta?: { helpfulCount, harmfulCount }
  feedbackType?: enum
  // PlaybookItem-specific relationships
  prevEventId?: string
  deprecatedReason?: string
  supersedes?: string[]
  supersededBy?: string
  duplicateOf?: string
  reason?: string
  // Extension 3: Rich Metadata (OPTIONAL)
  metadata?: object
}
```

**Composed from Atomics**:
```tron
# Special identity for append-only log entries
class EventIdentifiable: eventId, targetId

# Core (REQUIRED) - PlaybookItem extends Item + adds EventIdentifiable
class Item: Titled, Statused
class PlaybookItemCore: Item, EventIdentifiable, operation

# Full (with extensions)
class PlaybookItemFull: Item, EventIdentifiable, TimestampedSingle, 
                        Evidenced, Extensible, operation, prevEventId, kind, 
                        delta, deprecatedReason, supersedes, supersededBy, 
                        duplicateOf, reason
```

**TRON Instance (Core - minimal)**:
```tron
class Item: Titled, Statused
class EventIdentifiable: eventId, targetId
class PlaybookItemCore: Item, EventIdentifiable, operation

PlaybookItemCore(
  "Write tests before code",                      # title (REQUIRED)
  "active",                                        # status (REQUIRED)
  "evt-0100",                                      # eventId (REQUIRED)
  "entry-test-first",                              # targetId (REQUIRED)
  "append"                                         # operation (REQUIRED)
)
```

**TRON Instance (Full - with extensions)**:
```tron
class PlaybookItemFull: Item, EventIdentifiable, TimestampedSingle, 
                        Evidenced, Extensible, operation, prevEventId, kind, 
                        delta, deprecatedReason, supersedes, supersededBy, 
                        duplicateOf, reason

PlaybookItemFull(
  "Write tests before code",                      # title (REQUIRED)
  "Before changing code, write failing test...",  # description (OPTIONAL)
  "active",                                        # status (REQUIRED)
  "evt-0100",                                      # eventId (REQUIRED)
  "entry-test-first",                              # targetId (REQUIRED)
  "2024-12-27T09:00:00Z",                          # createdAt (Extension 1)
  0.95,                                            # confidence (Extension 12)
  ["pr:42", "ci:green"],                           # evidence (Extension 12)
  ["testing", "debugging"],                        # tags (Extension 12)
  "executionOutcome",                              # feedbackType (Extension 12)
  {},                                              # metadata (Extension 3)
  "append",                                        # operation (REQUIRED)
  null,                                            # prevEventId
  "strategy",                                      # kind
  {"helpfulCount": 3},                             # delta
  null,                                            # deprecatedReason
  [],                                              # supersedes
  null,                                            # supersededBy
  null,                                            # duplicateOf
  "Proven effective in bug fixes"                 # reason
)
```

---

### ProblemModel Composition

**Current Definition**:
```javascript
ProblemModel {
  // Core (REQUIRED)
  title: string              # MUST be titled
  // NOTE: ProblemModel is structural, not statused
  // It doesn't have lifecycle status - it's a specification
  
  // ProblemModel-specific collections
  entities: Entity[]
  stateVariables: StateVar[]
  actions: Action[]
  constraints: Constraint[]
  goals: Goal[]
  assumptions?: string[]
  
  // Extension 3: Rich Metadata (OPTIONAL)
  description?: string
}
```

**Composed from Atomics**:
```tron
# Core: Titled only (ProblemModel is structural, not statused)
class ProblemModelCore: Titled, entities, stateVariables, actions, constraints, goals

# Full: With optional assumptions and extensions
class ProblemModelFull: Titled, Extensible, entities, stateVariables, actions, 
                        constraints, goals, assumptions
```

**Child entities ARE titled, statused, and identifiable:**

```tron
# Entity children follow standard atomic patterns
class Entity: Titled, Statused, Identifiable, Extensible, type, properties
class StateVar: Titled, Statused, Identifiable, entity, name, type, possibleValues, initialValue
class Action: Titled, Statused, Identifiable, parameters, preconditions, effects, duration, cost
class Constraint: Titled, Statused, Identifiable, type, priority, conditions, scope, violation
class Goal: Titled, Statused, Identifiable, conditions, priority
```

**Note**: ProblemModel is an exception to the "all entities must be statused" rule because it's a pure specification/structure, not a lifecycle-tracked entity. However, all its children (Entity, StateVar, Action, etc.) DO have status.

**TRON Instance**:
```tron
ProblemModel(
  [                              # entities
    Entity("user-1", "User", "User entity", "User", {"role": "admin"}),
    Entity("token-1", "Token", "Auth token", "Token", {})
  ],
  [                              # stateVariables
    StateVar("user.authenticated", "user-1", "authenticated", "boolean", null, false, "Is user logged in"),
    StateVar("token.valid", "token-1", "valid", "boolean", null, false, "Is token valid")
  ],
  [                              # actions
    Action(
      "login",
      "User Login",
      "Authenticate user with credentials",
      [Parameter("username", "string", true), Parameter("password", "string", true)],
      [Condition("user.authenticated", "==", false)],  # preconditions
      [Effect("user.authenticated", "set", true)],     # effects
      "PT5M",                    # duration
      1                          # cost
    )
  ],
  [                              # constraints
    Constraint(
      "c1",
      "User must be authenticated to access API",
      "hard",
      null,
      [Condition("user.authenticated", "==", true)],
      "global",
      "403 Forbidden"
    )
  ],
  [                              # goals
    Goal("g1", "User authenticated", [Condition("user.authenticated", "==", true)], 1)
  ],
  ["Assume secure HTTPS connection"]  # assumptions
)
```

---

## Benefits of Atomic Composition

### 1. Reduced Duplication

**Before** (repeated across types):
```javascript
TodoItem { id, title, description, created, updated, metadata, ... }
Phase { id, title, description, created, updated, metadata, ... }
PlaybookEntry { eventId, title, text, createdAt, metadata, ... }
```

**After** (composed from atomics):
```tron
class TodoItem: Identifiable, Titled, Timestamped, Extensible, ...
class Phase: Identifiable, Titled, Timestamped, Extensible, ...
class PlaybookEntry: EventIdentifiable, Titled, Timestamped, Extensible, ...
```

### 2. Clear Extension Points

Extensions can target atomic classes:
- Extension 1 (Timestamps) → adds `Timestamped` to all types
- Extension 2 (Identifiers) → adds `Identifiable` to all types
- Extension 3 (Rich Metadata) → adds `Titled` and `Extensible` to all types

### 3. Polymorphic Operations

```tron
# Generic function for any Identifiable
function findById(id: string, collection: Identifiable[]) -> Identifiable

# Generic function for any Statused
function getActive(collection: Statused[]) -> Statused[]
  return collection.filter(item => item.status != "cancelled" && item.status != "deprecated")

# Generic function for any Timestamped
function sortByRecent(collection: Timestamped[]) -> Timestamped[]
  return collection.sort((a, b) => b.updated - a.updated)
```

### 4. Simplified Schema Definitions

JSON Schema can define atomic schemas once:

```json
{
  "$defs": {
    "Identifiable": {
      "type": "object",
      "properties": {
        "id": { "type": "string" }
      },
      "required": ["id"]
    },
    "Titled": {
      "type": "object",
      "properties": {
        "title": { "type": "string" },
        "description": { "type": "string" }
      }
    }
  }
}
```

Then compose:
```json
{
  "TodoItem": {
    "allOf": [
      { "$ref": "#/$defs/Identifiable" },
      { "$ref": "#/$defs/Titled" },
      { "$ref": "#/$defs/Timestamped" },
      ...
    ]
  }
}
```

---

## Implementation Considerations

### TRON Multiple Inheritance

TRON supports class composition naturally:

```tron
class Base1: field1, field2
class Base2: field3, field4
class Derived: Base1, Base2, field5

# Derived has: field1, field2, field3, field4, field5
```

This maps cleanly to our atomic composition approach.

### Field Ordering

When composing from multiple atomics, field order matters for positional instantiation:

```tron
class TodoItem: Identifiable, Titled, Statused, Timestamped, Extensible, priority, tags

# Instantiation order:
TodoItem(
  id,           # Identifiable
  title,        # Titled
  description,  # Titled
  status,       # Statused
  created,      # Timestamped
  updated,      # Timestamped
  metadata,     # Extensible
  priority,     # TodoItem-specific
  tags          # TodoItem-specific
)
```

**Recommendation**: Define a canonical ordering for atomic classes:
1. Identity (id, uid, eventId/targetId)
2. Content (title, description/text)
3. Status (status)
4. Temporal (created, updated, createdAt)
5. Versioning (version, sequence)
6. Evidence (confidence, evidence, tags, feedbackType)
7. Metadata (metadata)
8. Type-specific fields

### Optional vs Required

Some atomic fields are optional (Extension-dependent):
- Core: Only `title` and `status` are required for TodoItem/Phase
- Extension 1: Makes `created`/`updated` available
- Extension 2: Makes `id` available

**Approach**: Define "Core" vs "Extended" variants:

```tron
# Core (minimal)
class TodoItemCore: title, status

# With Extensions 1+2
class TodoItemExtended: Identifiable, Titled, Statused, Timestamped

# Full (all extensions)
class TodoItemFull: Identifiable, Titled, Statused, Timestamped, Extensible, 
                    dependencies, priority, tags, participants, uris, ...
```

---

## Migration Path

### Phase 1: Define Atomics
- Add atomic class definitions to spec
- Document composition rules
- Update JSON Schema with `$defs` for atomics

### Phase 2: Refactor Core Types
- Redefine TodoList, Plan, Playbook using atomic composition
- Show equivalent definitions (old vs new)
- Maintain backward compatibility

### Phase 3: Update Extensions
- Express extensions as atomic class additions
- Extension 1 → "adds Timestamped to all types"
- Extension 2 → "adds Identifiable to all types"

### Phase 4: Tooling Support
- Update TRON parsers to handle composition
- Generate JSON Schema from composed classes
- Add validation for atomic constraints

---

## Open Questions

1. **Naming**: Should atomics use `-able` suffix (Identifiable, Timestampable) or not (Identifier, Timestamp)?
   - **Current proposal**: `-able` for trait-like atomics, noun for data-like atomics

2. **Granularity**: Are these atomics too fine-grained? Should we combine some?
   - Example: `Identifiable + Titled + Timestamped` → `CoreEntity`?
   - **Recommendation**: Keep fine-grained for max flexibility

3. **Status Polymorphism**: Different types have different status enums. How to handle?
   - **Option A**: Single `Statused` class, type-specific enums
   - **Option B**: Specialized `TodoStatused`, `PlanStatused`, `PlaybookStatused`
   - **Current proposal**: Option A (single class, document enum differences)

4. **Extension Expression**: Should extensions be expressed as "adds atomic X" or "adds fields Y"?
   - **Recommendation**: Both - atomic for common patterns, fields for one-offs

---

## Migration Guide

### Breaking Changes

Option C introduces breaking changes to align all contained items under the `Item` abstraction:

#### 1. Phase → PlanItem

**Before:**
```javascript
Plan {
  phases: Phase[]
}

Phase {
  title: string
  status: enum
  subPhases?: Phase[]
}
```

**After:**
```javascript
Plan {
  items: PlanItem[]  // Renamed from phases
}

PlanItem {  // Renamed from Phase
  title: string
  status: enum
  subItems?: PlanItem[]  // Renamed from subPhases
}
```

**Migration code:**
```typescript
function migratePhase(plan: any): any {
  if (plan.phases) {
    plan.items = plan.phases.map(phase => ({
      ...phase,
      subItems: phase.subPhases  // Rename nested property
    }));
    delete plan.phases;
  }
  return plan;
}
```

#### 2. PlaybookEntry → PlaybookItem

**Before:**
```javascript
Playbook {
  entries: PlaybookEntry[]
}

PlaybookEntry {
  eventId: string
  targetId: string
  ...
}
```

**After:**
```javascript
Playbook {
  items: PlaybookItem[]  // Renamed from entries
}

PlaybookItem {  // Renamed from PlaybookEntry
  eventId: string
  targetId: string
  ...
}
```

**Migration code:**
```typescript
function migratePlaybook(playbook: any): any {
  if (playbook.entries) {
    playbook.items = playbook.entries;
    delete playbook.entries;
  }
  return playbook;
}
```

### Rationale

**Why break backward compatibility?**

1. **Consistency**: All containers now use `items` field (TodoList.items, Plan.items, Playbook.items)
2. **Clarity**: `<Container>Item` naming makes the pattern explicit
3. **Polymorphism**: Tools can treat all Items uniformly
4. **Future-proof**: New contained types follow clear convention

**Migration timeline:**

- **Phase 1** (v0.3): Add deprecation warnings, support both old and new names
- **Phase 2** (v0.4): Tools auto-migrate on read, write new format
- **Phase 3** (v0.5): Drop support for old names

### Field Mapping

| Old Name | New Name | Container |
|----------|----------|------------|
| `Phase` | `PlanItem` | Plan |
| `plan.phases` | `plan.items` | Plan |
| `phase.subPhases` | `planItem.subItems` | PlanItem |
| `PlaybookEntry` | `PlaybookItem` | Playbook |
| `playbook.entries` | `playbook.items` | Playbook |
| `TodoItem` | `TodoItem` | TodoList (unchanged) |
| `todoList.items` | `todoList.items` | TodoList (unchanged) |

---

## Next Steps

1. **Update atomic-classes-questions.md** with Option C decision
2. **Validate with Examples**: Ensure all current vBRIEF examples can be expressed with Item base
3. **JSON Schema Update**: Generate schemas using Item composition
4. **Spec Update**: Refactor README.md to introduce Item abstraction
5. **Tool Support**: Update reference implementations with migration support

---

## Summary of Changes

This refactored proposal establishes a clear two-tier architecture:

### Core Tier (REQUIRED - Zero Extensions)
Every vBRIEF entity gets:
- **Titled**: `title` + optional `description`
- **Statused**: `status` enum (except ProblemModel)

**Item Abstraction**: TodoItem, PlanItem (formerly Phase), and PlaybookItem (formerly PlaybookEntry) all extend the abstract `Item` base:

```tron
class Item: Titled, Statused
```

Minimal valid entities:
```tron
TodoItem("Fix bug", "pending")
PlanItem("Foundation", "completed")                          # Renamed from Phase
Plan("Migration", "approved", {"proposal": "..."})
Playbook("Best Practices", [...])
PlaybookItem("Test First", "active", "evt-1", "target-1", "append")  # Renamed from PlaybookEntry
```

### Extension Tier (OPTIONAL - Via Extensions)
Entities MAY add:
- **Identifiable** (Extension 2): `id` for cross-referencing
- **Timestamped** (Extension 1): `created`, `updated`
- **Versioned/Sequenced** (Extension 10): `version`, `sequence`
- **Extensible** (Extension 3): `metadata` escape hatch
- **Type-specific atomics**: `Evidenced`, `Scheduled`, `Collaborative`, etc.

### Key Benefits

1. **Simplicity**: Core entities require only 2-5 fields (title, status, + type-specific)
2. **Consistency**: All entities follow same Titled + Statused pattern
3. **Extensibility**: Extensions add atomics, not ad-hoc fields
4. **Token Efficiency**: Minimal core = fewer tokens for simple use cases
5. **Clear Migration**: Extensions map cleanly to atomic additions

### Migration Impact

**Before**: Extensions added random fields
```javascript
// Extension 1 adds: created, updated
// Extension 2 adds: id
// Extension 3 adds: description, priority, tags, metadata
```

**After**: Extensions add atomic classes
```javascript
// Extension 1 adds: Timestamped (created, updated)
// Extension 2 adds: Identifiable (id)
// Extension 3 adds: Titled.description + Extensible (metadata) + priority + tags
```

### Conformance

**Core-conformant document** (no extensions):
```tron
class vBRIEFInfo: version
class TodoItemCore: Titled, Statused
class TodoListCore: Titled, items

vBRIEFInfo: vBRIEFInfo("0.2")
todoList: TodoListCore(
  "Sprint Tasks",
  [
    TodoItemCore("Implement auth", "pending"),
    TodoItemCore("Write tests", "pending")
  ]
)
```

**Full-conformant document** (all extensions):
```tron
class TodoItemFull: Titled, Statused, Identifiable, Timestamped, Extensible, priority, tags
class TodoListFull: Titled, Identifiable, Timestamped, Sequenced, Extensible, items

# ... with all extension fields
```

---

## Appendix: Complete Atomic Class Library

```tron
# ===== CORE TIER (REQUIRED) =====
class Titled: title, description
class Statused: status

# ===== EXTENSION TIER (OPTIONAL) =====

# Identity (Extension 2)
class Identifiable: id
class EventIdentifiable: eventId, targetId
class GloballyIdentifiable: uid  # For cross-system sync

# Temporal (Extension 1)
class Timestamped: created, updated
class TimestampedSingle: createdAt  # For append-only structures

# Versioning (Extension 10)
class Versioned: version
class Sequenced: sequence

# Organization (Extension 3)
class Tagged: tags                  # For categorization/filtering
class Extensible: metadata          # For custom fields
class Prioritized: priority         # For TodoItem priority

# Evidence (Extension 12 - Playbooks)
class Evidenced: confidence, evidence, feedbackType
class Countable: delta              # For merge-safe counters

# Scheduling (Extension 5)
class Scheduled: startDate, endDate, dueDate, timezone
class Timed: duration, cost

# Collaboration (Extension 6)
class Owned: author, owner
class Collaborative: participants, reviewers

# Relationships (Extension 4)
class Dependent: dependencies
class Hierarchical: subPhases, subItems
class Linked: supersedes, supersededBy, duplicateOf

# Specialized
class Scoped: scope
```
