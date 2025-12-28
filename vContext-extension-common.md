# vContext Common Extensions

**Version**: 0.4

**Last Updated**: 2025-12-28

**Status**: DRAFT

## Overview

This document defines the common extensions that can be applied to vContext Core v0.4 documents. These extensions add optional fields and capabilities to TodoLists, Plans, and Playbooks.

Extensions are modular and can be combined as needed. Implementations SHOULD preserve unknown fields when rewriting documents to avoid data loss.

## Relationship to Core Specification

This document extends the core specification defined in [README.md](./README.md). All extensions build upon the core data models (vContextInfo, TodoList, TodoItem, Plan, PlanItem, Playbook, PlaybookItem).

##Conformance

- Implementations MAY support any combination of extensions
- Consumers MUST ignore unknown fields from unsupported extensions
- Producers SHOULD declare which extensions are in use (implementation-specific)

---

# Extensions

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

vContextInfo: vContextInfo("0.4", "2024-12-27T09:00:00Z", "2024-12-27T10:00:00Z", "America/Los_Angeles")
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
    "version": "0.4",
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

vContextInfo: vContextInfo("0.4")
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
    "version": "0.4"
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
  narrative?: Narrative    # Detailed description
  tags?: string[]          # Categorical labels
  metadata?: object        # Custom fields
}
```

### TodoItem Extensions
```javascript
TodoItem {
  // Core fields...
  narrative?: Narrative    # Detailed context
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
  tags?: string[]          # Categorical labels
  narratives: {
    proposal: Narrative,     # Proposal (required, standard title)
    overview?: Narrative,    # Overview (standard title)
    background?: Narrative,  # Background (standard title)
    problem?: Narrative,     # Problem (standard title)
    constraint?: Narrative,  # Constraint (standard title)
    hypothesis?: Narrative,  # Hypothesis (standard title)
    alternative?: Narrative, # Alternative (standard title)
    risk?: Narrative,        # Risk (standard title)
    test?: Narrative,        # Test (standard title)
    action?: Narrative,      # Action (standard title)
    observation?: Narrative, # Observation (standard title)
    result?: Narrative,      # Result (standard title)
    reflection?: Narrative,  # Reflection (standard title)
    custom?: Narrative[]     # User-defined narratives
  }
  metadata?: object        # Custom fields
}
```

### PlanItem Extensions
```javascript
PlanItem {
  // Core fields...
  narrative?: Narrative    # Item description
  tags?: string[]          # Categorical labels
  metadata?: object        # Custom fields
}
```

### Playbook Extensions
```javascript
Playbook {
  // Core fields...
  tags?: string[]          # Categorical labels
  metadata?: object        # Custom fields
}
```

### PlaybookItem Extensions
```javascript
PlaybookItem {
  // Core fields...
  tags?: string[]          # Categorical labels
  metadata?: object        # Custom fields
}
```

### Example

**TRON:**
```tron
class TodoItem: id, title, status, narrative, priority, tags, metadata
class Narrative: title, content

TodoItem(
  "item-2",
  "Implement JWT authentication",
  "inProgress",
  Narrative("Background", "Add JWT token generation and validation for secure API access"),
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
  "narrative": {
    "title": "Background",
    "content": "Add JWT token generation and validation for secure API access"
  },
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

vContextInfo: vContextInfo("0.4")
plan: Plan(
  "plan-002",
  "Build authentication system",
  "inProgress",
  {
    "proposal": Narrative(
      "Proposal",
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
    "version": "0.4"
  },
  "plan": {
    "id": "plan-002",
  "title": "Build authentication system",
  "status": "inProgress",
  "narratives": {
    "proposal": {
      "title": "Proposal",
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
  "vContextInfo": {"version": "0.4"},
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
  "vContextInfo": {"version": "0.4"},
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

vContextInfo: vContextInfo("0.4")
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
    "version": "0.4"
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

vContextInfo: vContextInfo("0.4")
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
    "version": "0.4"
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

