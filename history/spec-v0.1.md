# vBRIEF Specification v1.0

A flexible, extensible specification for todo lists and plan files, designed for both agentic development environments and human workflows.

**Specification Version**: 1.0  
**Last Updated**: 2024-12-27

## Design Principles

- **Format-agnostic**: Support both JSON and [TRON](https://tron-format.github.io/) encodings
- **Human-readable**: Optimized for direct editing and review
- **Machine-parseable**: Enable automated processing by AI agents and tooling
- **Extensible**: Allow custom fields and metadata without breaking compatibility
- **Version-aware**: Support schema evolution and migrations

## Core Data Models

### 1. Todo List

A collection of actionable items tracking work to be completed.

#### Schema

```
TodoList {
  version: string           # Schema version (e.g., "1.0")
  id: string               # Unique identifier
  uid?: string             # Globally unique identifier (for cross-system sync)
  title?: string           # Optional list title
  created: datetime        # ISO 8601 timestamp
  updated: datetime        # ISO 8601 timestamp
  fork?: Fork              # If this is a fork, track the parent
  agent?: Agent            # Agent/user who owns this fork
  lastModifiedBy?: Agent   # Last agent to modify this document
  changeLog?: Change[]     # History of modifications
  playbook?: Playbook      # Evolving strategies and learnings
  metadata?: object        # Extensible metadata
  items: TodoItem[]        # Array of todo items
}

TodoItem {
  id: string               # Unique identifier within list
  uid?: string             # Globally unique identifier (for cross-system sync)
  title: string            # Brief summary (required)
  description?: string     # Detailed context
  status: enum             # "pending" | "inProgress" | "completed" | "blocked" | "cancelled"
  priority?: enum          # "low" | "medium" | "high" | "critical"
  created: datetime        # ISO 8601 timestamp
  updated: datetime        # ISO 8601 timestamp
  completed?: datetime     # When item was completed
  dueDate?: datetime       # When item should be completed
  percentComplete?: number # 0-100, progress indicator
  tags?: string[]          # Categorical labels
  dependencies?: string[]  # IDs of items that must complete first
  participants?: Participant[] # People involved with roles
  relatedComments?: string[] # Comment IDs from code review
  uris?: URI[]             # Associated URIs (files, docs, PRs, issues, etc.)
  recurrence?: RecurrenceRule # For recurring tasks
  reminders?: Reminder[]   # Notifications before due date
  classification?: enum    # "public" | "private" | "confidential"
  sequence?: number        # Revision counter for conflict resolution
  timezone?: string        # IANA timezone (defaults to UTC if not specified)
  lastModifiedBy?: Agent   # Last agent to modify this item
  lockedBy?: Lock          # If claimed by an agent
  metadata?: object        # Extensible metadata
}
```

### 2. Plan

A structured design document describing approach, context, and proposed changes.

#### Schema

```
Plan {
  version: string          # Schema version (e.g., "1.0")
  id: string              # Unique identifier
  uid?: string            # Globally unique identifier (for cross-system sync)
  title: string           # Plan title
  created: datetime       # ISO 8601 timestamp
  updated: datetime       # ISO 8601 timestamp
  status: enum            # "draft" | "proposed" | "approved" | "inProgress" | "completed" | "cancelled"
  author?: string         # Creator
  reviewers?: string[]    # Approvers
  fork?: Fork             # If this is a fork, track the parent
  agent?: Agent           # Agent/user who owns this fork
  lastModifiedBy?: Agent  # Last agent to modify this document
  changeLog?: Change[]    # History of modifications
  sequence?: number       # Revision counter for conflict resolution
  metadata?: object       # Extensible metadata
  
  sections: {
    problem?: Section      # Problem statement
    context?: Section      # Current state overview
    proposal: Section      # Proposed changes (required)
    alternatives?: Section # Other approaches considered
    risks?: Section        # Known risks and mitigations
    testing?: Section      # Validation approach
    rollout?: Section      # Deployment strategy
    custom?: Section[]     # User-defined sections
  }
  
  phases?: Phase[]         # Implementation phases
  playbook?: Playbook      # Evolving strategies and learnings
  references?: Reference[] # Files, lines, URLs, issues
  attachments?: Attachment[] # Diagrams, configs, etc.
}

Section {
  title: string           # Section heading
  content: string         # Markdown content
  order?: number          # Display order
  metadata?: object       # Extensible metadata
}

Phase {
  id: string              # Unique identifier within plan
  uid?: string            # Globally unique identifier (for cross-system sync)
  title: string           # Phase name
  description?: string    # Phase description
  order: number           # Execution order
  status: enum            # "pending" | "inProgress" | "completed" | "blocked" | "cancelled"
  dependencies?: string[] # IDs of phases that must complete first
  startDate?: datetime    # Planned or actual start
  endDate?: datetime      # Planned or actual end
  percentComplete?: number # 0-100, can be aggregate or manual
  participants?: Participant[] # People involved with roles
  location?: Location     # Physical location for work
  phases?: Phase[]        # Child phases (hierarchical structure)
  todoList?: TodoList     # Associated todo list for this phase
  uris?: URI[]            # Associated URIs (files, docs, specs, etc.)
  reminders?: Reminder[]  # Notifications for phase milestones
  classification?: enum   # "public" | "private" | "confidential"
  sequence?: number       # Revision counter for conflict resolution
  timezone?: string       # IANA timezone (defaults to UTC if not specified)
  lastModifiedBy?: Agent  # Last agent to modify this phase
  lockedBy?: Lock         # If claimed by an agent
  metadata?: object       # Extensible metadata
}

Reference {
  type: enum              # "file" | "line" | "range" | "url" | "issue" | "pr"
  path?: string           # File path or URL
  line?: number           # Single line number
  start?: number          # Range start
  end?: number            # Range end
  description?: string    # What this references
  metadata?: object       # Extensible metadata
}

Attachment {
  name: string            # Filename
  type: string            # MIME type
  path?: string           # Local path
  url?: string            # Remote URL
  encoding?: string       # "base64" | "utf8" | etc.
  data?: string           # Inline content
  metadata?: object       # Extensible metadata
}

Participant {
  id: string              # Unique identifier
  name?: string           # Display name
  email?: string          # Email address
  role: enum              # "owner" | "assignee" | "reviewer" | "observer" | "contributor"
  status?: enum           # "accepted" | "declined" | "tentative" | "needsAction"
  metadata?: object       # Extensible metadata
}

RecurrenceRule {
  frequency: enum         # "daily" | "weekly" | "monthly" | "yearly"
  interval?: number       # Every N periods (default: 1)
  until?: datetime        # End date for recurrence
  count?: number          # Number of occurrences
  byDay?: string[]        # Days of week: ["MO", "TU", "WE", "TH", "FR", "SA", "SU"]
  byMonth?: number[]      # Months: [1-12]
  byMonthDay?: number[]   # Days of month: [1-31]
  metadata?: object       # Extensible metadata
}

Reminder {
  trigger: string         # ISO 8601 duration (e.g., "-PT15M" = 15 min before, "PT0M" = at time)
  action: enum            # "display" | "email" | "webhook" | "audio"
  description?: string    # Reminder message
  metadata?: object       # Extensible metadata
}

Location {
  name?: string           # Human-readable name (e.g., "Conference Room A")
  address?: string        # Physical address
  geo?: [number, number]  # [latitude, longitude]
  url?: string            # Link to location info
  metadata?: object       # Extensible metadata
}

URI {
  uri: string             # The URI/URL (required)
  description?: string    # Human-readable description of what this URI points to
  type?: string           # Content/resource type (preferably MIME type when available)
                          # Examples: "application/pdf", "text/html", "image/png"
                          # For non-file resources: "x-conferencing/zoom", "x-issue-tracker/github"
  title?: string          # Short title for the resource
  tags?: string[]         # Categorical labels for this URI
  metadata?: object       # Extensible metadata
}

Fork {
  parentUid: string       # UID of the parent document
  parentSequence: number  # Sequence number when forked
  forkedAt: datetime      # When this fork was created
  forkReason?: string     # Why this fork was created
  mergeStatus?: enum      # "unmerged" | "mergePending" | "merged" | "conflict"
  mergedAt?: datetime     # When merged back to parent
  mergedBy?: Agent        # Who performed the merge
  conflictResolution?: ConflictResolution
  metadata?: object       # Extensible metadata
}

Agent {
  id: string              # Unique agent identifier
  type: enum              # "human" | "aiAgent" | "system"
  name?: string           # Display name
  email?: string          # Contact for humans
  model?: string          # AI model identifier (e.g., "claude-3.5-sonnet")
  version?: string        # Agent software version
  metadata?: object       # Extensible metadata
}

Change {
  sequence: number        # Sequence number for this change
  timestamp: datetime     # When change occurred
  agent: Agent            # Who made the change
  operation: enum         # "create" | "update" | "delete" | "fork" | "merge"
  reason?: string         # Why this change was made (strongly recommended)
  path?: string           # JSONPath to changed field (e.g., "phases[0].status")
  oldValue?: any          # Previous value (JSON-compatible type)
  newValue?: any          # New value (JSON-compatible type)
  description?: string    # Human-readable change description
  snapshotUri?: string    # URI to full document snapshot at this sequence
  relatedChanges?: string[] # References to related change sequence numbers
  metadata?: object       # Extensible metadata
}

ConflictResolution {
  strategy: enum          # "ours" | "theirs" | "manual" | "threeWayMerge"
  conflicts: Conflict[]   # List of conflicts found
  resolvedBy?: Agent      # Who resolved conflicts
  resolvedAt?: datetime   # When conflicts were resolved
  metadata?: object       # Extensible metadata
}

Conflict {
  path: string            # JSONPath to conflicting field
  baseValue: any          # Value in common ancestor (JSON-compatible type)
  oursValue: any          # Value in our fork (JSON-compatible type)
  theirsValue: any        # Value in their fork/parent (JSON-compatible type)
  resolution?: any        # Resolved value if resolved (JSON-compatible type)
  status: enum            # "unresolved" | "resolved" | "deferred"
  metadata?: object       # Extensible metadata
}

Lock {
  agent: Agent            # Who holds the lock
  acquiredAt: datetime    # When lock was acquired
  expiresAt?: datetime    # When lock expires (for timeout)
  type: enum              # "soft" | "hard"
  metadata?: object       # Extensible metadata
}

Playbook {
  version: number         # Playbook version, increments with updates
  created: datetime       # When playbook was created
  updated: datetime       # Last update time
  strategies: Strategy[]  # Accumulated strategies and patterns
  learnings: Learning[]   # Domain insights and lessons learned
  reflections: Reflection[] # Agent reflections on execution
  metrics?: PlaybookMetrics # Success metrics for this playbook
  metadata?: object       # Extensible metadata
}

Strategy {
  id: string              # Unique strategy identifier
  title: string           # Short strategy name
  description: string     # What this strategy does
  context?: string        # When/where to apply this strategy
  confidence: number      # 0.0-1.0, how reliable this strategy is
  examples?: string[]     # Example scenarios where this worked
  antipatterns?: string[] # What to avoid
  createdAt: datetime     # When strategy was discovered
  updatedAt: datetime     # Last refinement
  usageCount?: number     # How many times applied
  successRate?: number    # 0.0-1.0, success rate when applied
  source?: enum           # "execution" | "reflection" | "manual" | "transferred"
  relatedStrategies?: string[] # IDs of related strategies
  tags?: string[]         # Categorical labels
  metadata?: object       # Extensible metadata
}

Learning {
  id: string              # Unique learning identifier
  content: string         # The insight or lesson learned
  evidence?: string[]     # Supporting evidence (references to changes, outcomes)
  confidence: number      # 0.0-1.0, confidence in this learning
  domain?: string         # Domain area (e.g., "testing", "deployment", "debugging")
  applicability?: string  # When this learning applies
  discoveredAt: datetime  # When this was learned
  discoveredBy: Agent     # Who discovered this
  reinforcementCount?: number # How many times this has been confirmed
  contradictions?: string[] # IDs of learnings that contradict this
  tags?: string[]         # Categorical labels
  metadata?: object       # Extensible metadata
}

Reflection {
  id: string              # Unique reflection identifier
  timestamp: datetime     # When reflection occurred
  agent: Agent            # Who reflected
  scope?: string          # What was reflected on (phase, task, decision)
  trigger: enum           # "completion" | "failure" | "milestone" | "scheduled" | "manual"
  observation: string     # What was observed
  analysis?: string       # Analysis of what happened
  improvements?: string[] # Suggested improvements
  strategiesApplied?: string[] # Strategy IDs that were used
  strategiesProposed?: Strategy[] # New strategies discovered
  learningsExtracted?: Learning[] # New learnings extracted
  metadata?: object       # Extensible metadata
}

PlaybookMetrics {
  totalStrategies: number # Count of strategies
  totalLearnings: number  # Count of learnings
  averageConfidence: number # Average confidence across strategies
  lastReflection?: datetime # Most recent reflection
  adaptationRate?: number # How frequently playbook updates (updates/day)
  successImpact?: number  # Measured improvement from playbook use
  metadata?: object       # Extensible metadata
}
```

## Encoding Formats

### Timezone Handling

**Default Timezone**: All datetime fields default to **UTC** unless explicitly specified otherwise.

- If `timezone` field is omitted, all datetime values are interpreted as UTC
- If `timezone` field is present, it should use IANA timezone identifiers (e.g., "America/New_York", "Europe/London", "Asia/Tokyo")
- Datetime values should always be in ISO 8601 format with timezone indicator (e.g., "2024-12-27T00:00:00Z" for UTC)

### JSON Format

Standard JSON encoding with UTF-8. Use 2-space indentation for human readability.

**TodoList Example:**

```json
{
  "version": "1.0",
  "id": "todo-2024-001",
  "title": "Implement user authentication",
  "created": "2024-12-26T23:00:00Z",
  "updated": "2024-12-26T23:30:00Z",
  "items": [
    {
      "id": "item-1",
      "title": "Add JWT token generation",
      "description": "Implement token signing with RS256",
      "status": "completed",
      "priority": "high",
      "created": "2024-12-26T23:00:00Z",
      "updated": "2024-12-26T23:15:00Z",
      "completed": "2024-12-26T23:15:00Z",
      "tags": ["auth", "backend"],
      "uris": [
        {
          "uri": "file://src/auth/token.go",
          "description": "Token generation implementation",
          "type": "text/x-go"
        }
      ]
    },
    {
      "id": "item-2",
      "title": "Create login endpoint",
      "description": "POST /api/v1/auth/login with email/password",
      "status": "inProgress",
      "priority": "high",
      "created": "2024-12-26T23:15:00Z",
      "updated": "2024-12-26T23:30:00Z",
      "tags": ["auth", "backend", "api"],
      "dependencies": ["item-1"],
      "uris": [
        {
          "uri": "file://src/handlers/auth.go",
          "description": "Login endpoint handler",
          "type": "text/x-go"
        }
      ]
    }
  ]
}
```

**Plan Example:**

```json
{
  "version": "1.0",
  "id": "plan-2024-001",
  "title": "Migrate to microservices architecture",
  "created": "2024-12-26T23:00:00Z",
  "updated": "2024-12-26T23:00:00Z",
  "status": "proposed",
  "author": "agent-1",
  "sections": {
    "problem": {
      "title": "Problem Statement",
      "content": "Monolithic architecture limits scalability and deployment flexibility.",
      "order": 1
    },
    "proposal": {
      "title": "Proposed Changes",
      "content": "Split into three services: auth, api, worker. Use gRPC for inter-service communication.",
      "order": 3
    }
  },
  "phases": [
    {
      "id": "phase-1",
      "title": "Foundation",
      "description": "Set up infrastructure and tooling",
      "order": 1,
      "status": "inProgress",
      "phases": [
        {
          "id": "phase-1.1",
          "title": "gRPC setup",
          "order": 1,
          "status": "completed",
          "participants": [
            {
              "id": "backend-team",
              "name": "Backend Team",
              "role": "owner"
            }
          ],
          "todoList": {
            "version": "1.0",
            "id": "todo-phase-1.1",
            "created": "2024-12-26T23:00:00Z",
            "updated": "2024-12-26T23:30:00Z",
            "items": [
              {
                "id": "item-1",
                "title": "Install gRPC dependencies",
                "status": "completed",
                "created": "2024-12-26T23:00:00Z",
                "updated": "2024-12-26T23:15:00Z",
                "completed": "2024-12-26T23:15:00Z"
              },
              {
                "id": "item-2",
                "title": "Define proto files",
                "status": "completed",
                "created": "2024-12-26T23:15:00Z",
                "updated": "2024-12-26T23:30:00Z",
                "completed": "2024-12-26T23:30:00Z"
              }
            ]
          }
        },
        {
          "id": "phase-1.2",
          "title": "Database schemas",
          "order": 2,
          "status": "inProgress",
          "dependencies": ["phase-1.1"],
          "participants": [
            {
              "id": "backend-team",
              "name": "Backend Team",
              "role": "owner"
            }
          ],
          "todoList": {
            "version": "1.0",
            "id": "todo-phase-1.2",
            "created": "2024-12-26T23:30:00Z",
            "updated": "2024-12-26T23:45:00Z",
            "items": [
              {
                "id": "item-1",
                "title": "Design auth service schema",
                "status": "completed",
                "created": "2024-12-26T23:30:00Z",
                "updated": "2024-12-26T23:40:00Z",
                "completed": "2024-12-26T23:40:00Z"
              },
              {
                "id": "item-2",
                "title": "Design API service schema",
                "status": "inProgress",
                "created": "2024-12-26T23:40:00Z",
                "updated": "2024-12-26T23:45:00Z"
              }
            ]
          }
        }
      ]
    },
    {
      "id": "phase-2",
      "title": "Service Implementation",
      "order": 2,
      "status": "pending",
      "dependencies": ["phase-1"],
      "phases": [
        {
          "id": "phase-2.1",
          "title": "Auth service",
          "order": 1,
          "status": "pending",
          "phases": [
            {
              "id": "phase-2.1.1",
              "title": "Core auth logic",
              "order": 1,
              "status": "pending"
            },
            {
              "id": "phase-2.1.2",
              "title": "JWT token handling",
              "order": 2,
              "status": "pending",
              "dependencies": ["phase-2.1.1"]
            }
          ]
        },
        {
          "id": "phase-2.2",
          "title": "API service",
          "order": 2,
          "status": "pending"
        },
        {
          "id": "phase-2.3",
          "title": "Worker service",
          "order": 3,
          "status": "pending"
        }
      ]
    }
  ],
  "references": [
    {
      "type": "file",
      "path": "src/main.go",
      "description": "Current monolith entry point"
    },
    {
      "type": "range",
      "path": "src/database/client.go",
      "start": 45,
      "end": 78,
      "description": "Database connection pool to be shared"
    }
  ]
}
```

### TRON Format

[TRON (Token Reduced Object Notation)](https://tron-format.github.io/) provides a more concise, human-friendly syntax while maintaining machine parseability. TRON uses class definitions to declare schemas and class instantiation to encode data efficiently.

For the complete TRON specification, see: https://tron-format.github.io/

**Class Definitions:**

```tron
# TodoList schema
class TodoList:
  version, id, uid, title, created, updated,
  fork, agent, lastModifiedBy, changeLog, metadata, items

# TodoItem schema
class TodoItem:
  id, uid, title, description, status, priority,
  created, updated, completed, dueDate, percentComplete, tags,
  dependencies, participants, relatedComments, uris,
  recurrence, reminders, classification, sequence, timezone,
  lastModifiedBy, lockedBy, metadata

# Plan schema
class Plan:
  version, id, title, created, updated, status,
  author, reviewers, metadata, sections, phases, references, attachments

# Phase schema
class Phase:
  id, uid, title, description, order, status, dependencies,
  startDate, endDate, percentComplete, participants, location,
  phases, todoList, uris, reminders, classification, sequence, timezone,
  lastModifiedBy, lockedBy, metadata

# Participant schema
class Participant: id, name, email, role, status, metadata

# RecurrenceRule schema
class RecurrenceRule:
  frequency, interval, until, count, byDay, byMonth, byMonthDay, metadata

# Reminder schema
class Reminder: trigger, action, description, metadata

# Location schema
class Location: name, address, geo, url, metadata

# URI schema
class URI: uri, description, type, title, tags, metadata

# Fork schema
class Fork:
  parentUid, parentSequence, forkedAt, forkReason,
  mergeStatus, mergedAt, mergedBy, conflictResolution, metadata

# Agent schema
class Agent: id, type, name, email, model, version, metadata

# Change schema
class Change:
  sequence, timestamp, agent, operation, reason, path,
  oldValue, newValue, description, snapshotUri, relatedChanges, metadata

# ConflictResolution schema
class ConflictResolution: strategy, conflicts, resolvedBy, resolvedAt, metadata

# Conflict schema
class Conflict: path, baseValue, oursValue, theirsValue, resolution, status, metadata

# Lock schema
class Lock: agent, acquiredAt, expiresAt, type, metadata

# Playbook schema
class Playbook: version, created, updated, strategies, learnings, reflections, metrics, metadata

# Strategy schema
class Strategy:
  id, title, description, context, confidence, examples, antipatterns,
  createdAt, updatedAt, usageCount, successRate, source, relatedStrategies, tags, metadata

# Learning schema
class Learning:
  id, content, evidence, confidence, domain, applicability,
  discoveredAt, discoveredBy, reinforcementCount, contradictions, tags, metadata

# Reflection schema
class Reflection:
  id, timestamp, agent, scope, trigger, observation, analysis,
  improvements, strategiesApplied, strategiesProposed, learningsExtracted, metadata

# PlaybookMetrics schema
class PlaybookMetrics:
  totalStrategies, totalLearnings, averageConfidence,
  lastReflection, adaptationRate, successImpact, metadata
```
# URI schema
class URI: uri, description, type, title, tags, metadata
```
# Section schema
class Section: title, content, order, metadata

# Reference schema
class Reference: type, path, line, start, end, description, metadata

# Attachment schema
class Attachment: name, type, path, url, encoding, data, metadata
```

**TodoList Example:**

```tron
class TodoList: version, id, title, created, updated, items
class TodoList: version, id, title, created, updated, items
class TodoItem:
  id, uid, title, description, status, priority,
  created, updated, completed, dueDate, percentComplete, tags,
  dependencies, participants, relatedComments, uris, recurrence, reminders, classification

TodoList(
  "1.0",
  "todo-2024-001",
  "Implement user authentication",
  "2024-12-26T23:00:00Z",
  "2024-12-26T23:30:00Z",
  [
    TodoItem(
      "item-1",
      "Add JWT token generation",
      "Implement token signing with RS256",
      "completed",
      "high",
      "2024-12-26T23:00:00Z",
      "2024-12-26T23:15:00Z",
      "2024-12-26T23:15:00Z",
    ["auth", "backend"],
    null,
    null
    ),
    TodoItem(
      "item-2",
      "Create login endpoint",
      "POST /api/v1/auth/login with email/password",
      "in_progress",
      "high",
      "2024-12-26T23:15:00Z",
      "2024-12-26T23:30:00Z",
      null,
    ["auth", "backend", "api"],
    ["item-1"],
    null
    )
  ]
)
```

**Plan Example:**

```tron
class Plan:
  version, id, uid, title, created, updated, status, author,
  fork, agent, lastModifiedBy, changeLog, sequence,
  sections, phases, references
class Section: title, content, order
class Phase:
  id, uid, title, order, status, dependencies,
  startDate, endDate, percentComplete, participants, location, phases, todoList, uris, reminders
class Participant: id, name, email, role, status
class URI: uri, description, mimeType, title
class Reminder: trigger, action, description
class Location: name, address, geo
class Reference: type, path, start, end, description

Plan(
  "1.0",
  "plan-2024-001",
  "Migrate to microservices architecture",
  "2024-12-26T23:00:00Z",
  "2024-12-26T23:00:00Z",
  "proposed",
  "agent-1",
  {
    "problem": Section(
      "Problem Statement",
      "Monolithic architecture limits scalability and deployment flexibility. Current bottlenecks in deployment pipeline affect team velocity.",
      1
    ),
    "context": Section(
      "Current State",
      "Single Go binary (~150k LOC) handling all responsibilities. Deployment requires full system downtime. Database connection pool shared across all features.",
      2
    ),
    "proposal": Section(
      "Proposed Changes",
      "Split into three services: Auth service (authentication, JWT issuance), API service (business logic, REST endpoints), Worker service (async tasks, background jobs). Use gRPC for inter-service communication. Shared PostgreSQL with service-specific schemas.",
      3
    )
  },
  [
    Phase(
      "phase-1",
      "Foundation",
      "Set up infrastructure and tooling",
      1,
      "inProgress",
      null,
      [
        Participant("backend-team", "Backend Team", null, "owner", null, null)
      ],
      [
        Phase(
          "phase-1.1",
          "gRPC setup",
          null,
          1,
          "completed",
          null,
          [
            Participant("backend-team", "Backend Team", null, "owner", null, null)
          ],
          null,
          TodoList(
            "1.0",
            "todo-phase-1.1",
            null,
            "2024-12-26T23:00:00Z",
            "2024-12-26T23:30:00Z",
            null,
            [
              TodoItem("item-1", "Install gRPC dependencies", null, "completed", null, "2024-12-26T23:00:00Z", "2024-12-26T23:15:00Z", "2024-12-26T23:15:00Z", null, null, null),
              TodoItem("item-2", "Define proto files", null, "completed", null, "2024-12-26T23:15:00Z", "2024-12-26T23:30:00Z", "2024-12-26T23:30:00Z", null, null, null)
            ]
          )
        ),
        Phase(
          "phase-1.2",
          "Database schemas",
          null,
          2,
          "inProgress",
          ["phase-1.1"],
          [
            Participant("backend-team", "Backend Team", null, "owner", null, null)
          ],
          null,
          TodoList(
            "1.0",
            "todo-phase-1.2",
            null,
            "2024-12-26T23:30:00Z",
            "2024-12-26T23:45:00Z",
            null,
            [
              TodoItem("item-1", "Design auth service schema", null, "completed", null, "2024-12-26T23:30:00Z", "2024-12-26T23:40:00Z", "2024-12-26T23:40:00Z", null, null, null),
              TodoItem("item-2", "Design API service schema", null, "inProgress", null, "2024-12-26T23:40:00Z", "2024-12-26T23:45:00Z", null, null, null)
            ]
          )
        )
      ],
      null
    ),
    Phase(
      "phase-2",
      "Service Implementation",
      null,
      2,
      "pending",
      ["phase-1"],
      null,
      [
        Phase(
          "phase-2.1",
          "Auth service",
          null,
          1,
          "pending",
          null,
          null,
          [
            Phase("phase-2.1.1", "Core auth logic", null, 1, "pending", null, null, null, null),
            Phase("phase-2.1.2", "JWT token handling", null, 2, "pending", ["phase-2.1.1"], null, null, null)
          ],
          null
        ),
        Phase("phase-2.2", "API service", null, 2, "pending", null, null, null, null),
        Phase("phase-2.3", "Worker service", null, 3, "pending", null, null, null, null)
      ],
      null
    )
  ],
  [
    Reference("file", "src/main.go", null, null, "Current monolith entry point"),
    Reference("range", "src/database/client.go", 45, 78, "Database connection pool to be shared"),
    Reference("url", "https://grpc.io/docs/languages/go/quickstart/", null, null, "gRPC Go documentation")
  ]
)
```

## File Naming Conventions

- TodoLists: `todo-<identifier>.<format>` or `<name>-todo.<format>`
  - Examples: `todo-001.json`, `auth-feature-todo.tron`
- Plans: `plan-<identifier>.<format>` or `<name>-plan.<format>`
  - Examples: `plan-001.json`, `microservices-plan.tron`
- Use hyphens (not underscores) in filenames

## Extension Guidelines

### Adding Custom Fields

Both formats support extension through the `metadata` field in any object:

```json
{
  "id": "item-1",
  "title": "Example",
  "status": "pending",
  "metadata": {
    "estimatedHours": 4,
    "complexity": "medium",
    "customTrackerId": "JIRA-1234"
  }
}
```

```tron
class TodoItem: id, title, status, metadata

TodoItem(
  "item-1",
  "Example",
  "pending",
  {
    "estimatedHours": 4,
    "complexity": "medium",
    "customTrackerId": "JIRA-1234"
  }
)
```

### Version Migration

When schema changes:
1. Increment major version for breaking changes
2. Increment minor version for backward-compatible additions
3. Tools should handle unknown fields gracefully
4. Include migration utilities for version upgrades

## Tool Integration

### For Agentic Development Environments

Tools should:
- Read and write both JSON and TRON formats
- Validate against schema version
- Preserve unknown fields during updates
- Generate unique IDs using UUIDs or similar
- Update timestamps automatically
- Support partial updates (patching)

### For Human Workflows

Editors should:
- Syntax highlight both formats
- Validate on save
- Provide templates for new items
- Support format conversion (JSON ↔ TRON)
- Show warnings for missing required fields

## Status Transitions

### TodoItem Status Flow

```
pending → inProgress → completed
    ↓          ↓            ↓
  blocked → cancelled    (terminal)
    ↓
  pending (after unblock)
```

### Plan Status Flow

```
draft → proposed → approved → inProgress → completed
   ↓        ↓          ↓           ↓            ↓
        cancelled (any stage)                (terminal)
```

## Multi-Agent Collaboration

vBRIEF supports multiple agents (AI or human) working on plans and todo lists in parallel through forking, conflict detection, and merge operations.

### Forking Workflow

1. **Fork Creation**: Agent creates a copy with fork metadata
   - Set `fork.parentUid` to parent document's UID
   - Set `fork.parentSequence` to parent's current sequence
   - Set `agent` field to identify fork ownership
   - Set `mergeStatus` to "unmerged"

2. **Parallel Work**: Each fork works independently
   - Increment `sequence` on every change
   - Append to `changeLog` for audit trail
   - Use `lockedBy` for optimistic locking of phases/items

3. **Merge Detection**: Before merging back
   - Check if `fork.parentSequence` < parent's current `sequence`
   - If yes, changes occurred in parallel → potential conflicts

4. **Three-Way Merge**:
   - **Base**: Common ancestor at `fork.parentSequence`
   - **Ours**: Current fork state
   - **Theirs**: Current parent state
   - Auto-merge non-overlapping changes
   - Mark conflicts for resolution

5. **Conflict Resolution**:
   - Strategy "ours": Keep fork's changes
   - Strategy "theirs": Accept parent's changes
   - Strategy "manual": Human/agent decides per conflict
   - Strategy "threeWayMerge": Intelligent merge algorithm

6. **Merge Completion**:
   - Update `mergeStatus` to "merged"
   - Set `mergedAt` and `mergedBy`
   - Increment parent's `sequence`

### Example Parallel Work Scenario

```
Master Plan (seq=5, uid=master-123)
├─ Agent A forks → Plan A (seq=5, fork.parentSequence=5)
└─ Agent B forks → Plan B (seq=5, fork.parentSequence=5)

Agent A modifies Phase 1:
  Plan A: seq=6, phases[0].status="completed"

Agent B modifies Phase 2:
  Plan B: seq=6, phases[1].status="inProgress"

Agent A merges first:
  Master Plan: seq=6 (includes Phase 1 changes)

Agent B attempts merge:
  - fork.parentSequence=5, Master.sequence=6 → conflict detection
  - Three-way merge:
    * Base (seq=5): phases[0]=pending, phases[1]=pending
    * Ours (Plan B): phases[0]=pending, phases[1]=inProgress
    * Theirs (Master): phases[0]=completed, phases[1]=pending
  - Auto-merge result:
    * phases[0]=completed (from Theirs, no conflict)
    * phases[1]=inProgress (from Ours, no conflict)
  Master Plan: seq=7 (merged)
```

### Optimistic Locking

```json
{
  "phases": [
    {
      "id": "phase-1",
      "lockedBy": {
        "agent": {
          "id": "agent-a",
          "type": "aiAgent",
          "model": "claude-3.5-sonnet"
        },
        "acquiredAt": "2024-12-27T10:00:00Z",
        "expiresAt": "2024-12-27T10:15:00Z",
        "type": "soft"
      }
    }
  ]
}
```

**Lock Types**:
- **soft**: Advisory lock, can be broken/ignored by other agents
- **hard**: Enforced lock, modifications rejected until released

### Change Tracking Example

```json
{
  "changeLog": [
    {
      "sequence": 6,
      "timestamp": "2024-12-27T10:00:00Z",
      "agent": {
        "id": "agent-a",
        "type": "aiAgent",
        "model": "claude-3.5-sonnet"
      },
      "operation": "update",
      "reason": "User feedback indicated Phase 1 should start immediately",
      "path": "phases[0].status",
      "oldValue": "pending",
      "newValue": "inProgress",
      "description": "Started implementation of Phase 1",
      "snapshotUri": "file://snapshots/plan-001-seq-6.json"
    },
    {
      "sequence": 7,
      "timestamp": "2024-12-27T11:00:00Z",
      "agent": {
        "id": "agent-a",
        "type": "aiAgent",
        "model": "claude-3.5-sonnet"
      },
      "operation": "update",
      "reason": "All subtasks completed successfully",
      "path": "phases[0].percentComplete",
      "oldValue": 0,
      "newValue": 100,
      "description": "Completed Phase 1",
      "snapshotUri": "file://snapshots/plan-001-seq-7.json",
      "relatedChanges": ["6"]
    },
    {
      "sequence": 8,
      "timestamp": "2024-12-27T14:00:00Z",
      "agent": {
        "id": "user-123",
        "type": "human",
        "name": "Alice Chen",
        "email": "alice@example.com"
      },
      "operation": "update",
      "reason": "Stakeholder requested addition of security audit phase due to compliance requirements",
      "path": "phases",
      "oldValue": "[...2 phases]",
      "newValue": "[...3 phases]",
      "description": "Added Phase 2.5: Security Audit between implementation and deployment",
      "snapshotUri": "file://snapshots/plan-001-seq-8.json"
    }
  ]
}
```

### Referencing Prior Versions

**Method 1: Via Sequence Number**
```json
{
  "comment": "Referring to the plan as it was at sequence 6",
  "referenceSequence": 6,
  "snapshotUri": "file://snapshots/plan-001-seq-6.json"
}
```

**Method 2: Via Snapshot URIs**
Store complete document snapshots at each sequence:
```
snapshots/
├── plan-001-seq-5.json  # Original version
├── plan-001-seq-6.json  # After Agent A started Phase 1
├── plan-001-seq-7.json  # After Phase 1 completed
└── plan-001-seq-8.json  # After security audit phase added
```

**Method 3: Reconstruct from ChangeLog**
Apply changes in reverse to reconstruct any prior version:
```javascript
function getPlanAtSequence(currentPlan, targetSequence) {
  let plan = cloneDeep(currentPlan);
  
  // Apply changes in reverse from current to target
  for (let change of plan.changeLog.reverse()) {
    if (change.sequence <= targetSequence) break;
    
    // Undo this change
    setValueAtPath(plan, change.path, change.oldValue);
  }
  
  return plan;
}
```

### Understanding Change Motivation

Query the changeLog to understand decision history:

```javascript
// Why was Phase 2.5 added?
const change = plan.changeLog.find(c => 
  c.path === "phases" && c.description.includes("Security Audit")
);

console.log(change.reason);
// "Stakeholder requested addition of security audit phase due to compliance requirements"

console.log(change.agent);
// {id: "user-123", type: "human", name: "Alice Chen"}
```

```javascript
// What changed between sequence 5 and 8?
const changes = plan.changeLog.filter(c => 
  c.sequence > 5 && c.sequence <= 8
);

changes.forEach(c => {
  console.log(`Seq ${c.sequence}: ${c.reason}`);
});
// Seq 6: User feedback indicated Phase 1 should start immediately
// Seq 7: All subtasks completed successfully  
// Seq 8: Stakeholder requested addition of security audit phase...
```

### Evolving Playbooks

vBRIEF supports evolving playbooks where plans and todo lists accumulate, refine, and organize strategies through execution feedback.

#### Playbook Structure

A playbook contains:
- **Strategies**: Reusable patterns discovered through execution
- **Learnings**: Domain insights that persist across work
- **Reflections**: Agent self-analysis after milestones
- **Metrics**: Track playbook evolution and impact

#### Example Playbook

```json
{
  "playbook": {
    "version": 3,
    "created": "2024-12-01T00:00:00Z",
    "updated": "2024-12-27T15:00:00Z",
    "strategies": [
      {
        "id": "strat-001",
        "title": "Parallel Phase Execution",
        "description": "Phases 1 and 2 can run in parallel if they don't share database schema",
        "context": "When phases have independent database resources",
        "confidence": 0.95,
        "examples": [
          "Auth service and API service built simultaneously",
          "Frontend and backend work parallelized"
        ],
        "antipatterns": [
          "Don't parallelize if shared schema migrations needed"
        ],
        "createdAt": "2024-12-15T10:00:00Z",
        "updatedAt": "2024-12-20T14:00:00Z",
        "usageCount": 12,
        "successRate": 0.92,
        "source": "execution",
        "tags": ["performance", "optimization"]
      },
      {
        "id": "strat-002",
        "title": "Early Security Review",
        "description": "Add security review phase before implementation, not after",
        "context": "For any feature touching authentication or authorization",
        "confidence": 0.88,
        "examples": [
          "JWT implementation caught design flaw in early review"
        ],
        "createdAt": "2024-12-18T11:00:00Z",
        "updatedAt": "2024-12-27T15:00:00Z",
        "usageCount": 5,
        "successRate": 1.0,
        "source": "reflection",
        "relatedStrategies": ["strat-001"],
        "tags": ["security", "architecture"]
      }
    ],
    "learnings": [
      {
        "id": "learn-001",
        "content": "Stakeholders require compliance documentation earlier than expected",
        "evidence": [
          "Change seq-8: Security audit phase added",
          "Blocked deployment in 3 previous projects"
        ],
        "confidence": 0.9,
        "domain": "compliance",
        "applicability": "All projects with customer data",
        "discoveredAt": "2024-12-27T14:00:00Z",
        "discoveredBy": {
          "id": "agent-a",
          "type": "aiAgent",
          "model": "claude-3.5-sonnet"
        },
        "reinforcementCount": 3,
        "tags": ["compliance", "stakeholder-management"]
      }
    ],
    "reflections": [
      {
        "id": "refl-001",
        "timestamp": "2024-12-27T15:00:00Z",
        "agent": {
          "id": "agent-a",
          "type": "aiAgent",
          "model": "claude-3.5-sonnet"
        },
        "scope": "Phase 1 completion",
        "trigger": "completion",
        "observation": "Phase 1 completed 20% faster than estimated due to parallel execution strategy",
        "analysis": "Strategy strat-001 was highly effective. Team coordination overhead was minimal.",
        "improvements": [
          "Could apply same strategy to phases 2.1 and 2.2",
          "Document dependency graph upfront for better parallelization planning"
        ],
        "strategiesApplied": ["strat-001"],
        "strategiesProposed": [
          {
            "id": "strat-003",
            "title": "Upfront Dependency Mapping",
            "description": "Create visual dependency graph before phase planning",
            "confidence": 0.7,
            "source": "reflection",
            "tags": ["planning"]
          }
        ]
      }
    ],
    "metrics": {
      "totalStrategies": 3,
      "totalLearnings": 1,
      "averageConfidence": 0.85,
      "lastReflection": "2024-12-27T15:00:00Z",
      "adaptationRate": 0.5,
      "successImpact": 0.18
    }
  }
}
```

#### Playbook Evolution Cycle

```
1. Execution → Collect feedback
   ↓
2. Reflection → Agent analyzes outcomes
   ↓
3. Strategy Generation → Extract reusable patterns
   ↓
4. Curation → Validate, refine, and organize
   ↓
5. Application → Use strategies in next execution
   ↓
   (repeat)
```

#### Preventing Context Collapse

Playbook principles prevent information loss:

1. **Structured Updates**: Strategies are added/refined, not replaced
2. **Confidence Tracking**: Low-confidence strategies retained for learning
3. **Evidence Preservation**: Learnings link to specific changes/outcomes
4. **Reflection History**: Complete reflection trail maintained
5. **Contradiction Detection**: Conflicting learnings explicitly tracked

#### Strategy Transfer

Strategies can be transferred between plans:

```json
{
  "strategy": {
    "id": "strat-001",
    "source": "transferred",
    "metadata": {
      "transferredFrom": "plan-001",
      "transferredAt": "2024-12-27T16:00:00Z",
      "adaptations": "Adjusted context for frontend work"
    }
  }
}
```

## Best Practices

### Core Practices

1. **IDs**: Use UUIDs or timestamp-based IDs for uniqueness within a document
2. **UIDs**: Use globally unique identifiers (e.g., "20241227T000000Z-123456@example.com") for cross-system synchronization
3. **Timestamps**: Always use ISO 8601 format with timezone indicator (e.g., "2024-12-27T00:00:00Z")
4. **Timezone**: Omit `timezone` field to default to UTC; specify only when non-UTC times are required
5. **References**: Use relative paths for files in same repository
6. **Descriptions**: Keep titles brief (<80 chars), use description for details
7. **Status**: Update status field before updating timestamps
8. **Sequence**: Increment sequence number on every modification for conflict resolution
9. **Dependencies**: Validate dependency graphs are acyclic
10. **Participants**: Use `participants` array with explicit roles for team collaboration
11. **Classification**: Use "public" for shared work, "private" for personal, "confidential" for sensitive
12. **Percent Complete**: Update automatically based on child items/phases, or manually if no children
13. **URIs**: Use for all resource references (files via file:// URIs, docs, wikis, tickets, PRs, designs, etc.)
14. **URI Types**: 
    - Use standard MIME types when available (e.g., "application/pdf", "text/html", "image/png")
    - For non-file resources, use x- prefixed types (e.g., "x-conferencing/zoom", "x-issue-tracker/github", "x-video-call/teams")
    - Helps clients render or handle URIs appropriately
15. **Metadata**: Document custom metadata fields in project README

### Multi-Agent Collaboration

16. **Fork Creation**: Always populate `fork.parentUid` and `fork.parentSequence` when creating a fork
17. **Agent Identity**: Set `agent` field to identify who owns the fork
18. **Change Logging**: Append to `changeLog` for every modification to maintain audit trail
19. **Sequence Increment**: Increment `sequence` on every change for conflict detection
20. **Pre-Merge Check**: Before merging, verify `fork.parentSequence` < parent's current `sequence`
21. **Conflict Resolution**:
    - Auto-merge non-overlapping changes to different fields/paths
    - Mark conflicts with `status: "unresolved"` when same field modified
    - Require manual resolution or apply policy-based strategy
22. **Lock Management**:
    - Use "soft" locks for advisory coordination between cooperative agents
    - Use "hard" locks when strict exclusion is required
    - Always set `expiresAt` to prevent indefinite locks
23. **Change Paths**: Use JSONPath notation in `Change.path` for precise field references
24. **Agent Type**: Specify `aiAgent` vs `human` vs `system` to distinguish actors
25. **Change Reasoning**: Always provide `reason` field in changes to document "why" decisions were made
26. **Version Snapshots**: Optionally store complete document snapshots at key sequences via `snapshotUri`
27. **Related Changes**: Link related modifications using `relatedChanges` array of sequence numbers

### Playbooks

28. **Strategy Accumulation**: Add new strategies rather than replacing existing ones to prevent context collapse
29. **Confidence Tracking**: Track confidence (0.0-1.0) for all strategies and learnings; refine confidence over time
30. **Evidence-Based Learning**: Always link learnings to specific evidence (change sequences, outcomes)
31. **Regular Reflection**: Trigger reflections at completions, failures, and milestones to extract insights
32. **Strategy Usage Tracking**: Increment `usageCount` and update `successRate` when strategies are applied
33. **Contradiction Handling**: When learnings conflict, track both and their contradictions explicitly
34. **Strategy Transfer**: Mark transferred strategies with `source: "transferred"` and document adaptations
35. **Metric Monitoring**: Track `adaptationRate` and `successImpact` to measure playbook effectiveness
36. **Antipattern Documentation**: Always document what NOT to do alongside successful strategies

### Preservation and Archival (Optional)

For long-term preservation, archival, and institutional use, consider these additional practices based on Library of Congress guidelines:

#### File Format Preferences

1. **Character Encoding**: 
   - JSON files should use UTF-8 encoding (preferred)
   - UTF-16 with BOM acceptable as fallback
   - Always specify encoding in metadata if non-UTF-8

2. **Format Durability**:
   - JSON and TRON are platform-independent, character-based formats (ideal for preservation)
   - Avoid binary serialization for archival copies
   - Use well-documented public format specifications

#### Archival Metadata

When archiving TodoLists or Plans, include these in document metadata:

```json
{
  "archival": {
    "creator": "Organization or individual name",
    "creatorContact": "email@example.com",
    "publisher": "Organization name",
    "language": "en",
    "abstract": "Brief description of work covered",
    "identifiers": {
      "doi": "10.xxxx/xxxxx",
      "url": "https://permanent.url/path"
    },
    "softwareUsed": [
      {"name": "vBRIEF Client", "version": "1.0.0"},
      {"name": "Task Management System", "version": "2.3.1"}
    ],
    "checksums": {
      "sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
    },
    "copyrightTerms": "CC BY 4.0" or "All rights reserved",
    "grantNumber": "NSF-1234567" (if applicable),
    "repository": {
      "name": "Institutional Repository Name",
      "url": "https://repository.example.edu/collection/123",
      "doi": "10.xxxx/repo.xxxxx"
    },
    "dataCollection": "Description of how todos/plan data was collected",
    "sampling": "Description of any filtering or post-processing applied",
    "permanentVersionSpecifier": "v1.2.3" or "2024-12-27"
  }
}
```

#### Packaging for Transfer

1. **Compression**: Use ZIP, tar, or 7z without encryption for bundling
2. **Manifest**: Include a manifest file listing all contents with checksums
3. **README**: Include human-readable documentation explaining the archive
4. **Schemas**: Bundle the vBRIEF specification version used

#### Example Archive Structure

```
project-archive-2024-12-27.zip
├── README.txt                    # Human-readable overview
├── MANIFEST.txt                  # File list with SHA256 checksums
├── vbrief-spec-v1.0.md         # Specification version used
├── metadata.json                 # Archival metadata
├── plans/
│   ├── plan-001.json
│   └── plan-002.json
├── todos/
│   ├── todo-phase-1.json
│   └── todo-phase-2.json
└── attachments/
    ├── diagram.png
    └── architecture.pdf
```

#### Checksums and Verification

1. **Generate checksums** (SHA-256 preferred) for each file
2. **Include checksums** in manifest or metadata
3. **Verify on receipt** when restoring from archive

#### Version Control

1. **Version specifiers**: Use semantic versioning or ISO date stamps
2. **Change logs**: Document modifications in metadata or separate changelog
3. **Permanent identifiers**: Assign DOIs or permanent URLs for published archives

## Interoperability Notes

### Compatibility with iCalendar/vCard

vBRIEF draws inspiration from iCalendar (RFC 5545) and vCard (RFC 6350) standards:

- **UID**: Compatible with iCalendar UID for cross-system sync
- **Recurrence**: Based on iCalendar RRULE syntax
- **Reminders**: Similar to iCalendar VALARM
- **Participants**: Inspired by iCalendar ATTENDEE/ORGANIZER
- **Classification**: Matches iCalendar CLASS property
- **Sequence**: Same concept as iCalendar SEQUENCE for revisions
- **Timezone**: Uses IANA timezone identifiers like iCalendar VTIMEZONE
- **Location**: Based on iCalendar LOCATION and GEO properties

### Differences from iCalendar

- vBRIEF uses JSON/TRON instead of plain text format
- Hierarchical phases extend beyond iCalendar's VTODO parent-child
- TodoList as a first-class container (not just individual VTODOs)
- Embedded todo lists within phases for better organization
- File and code references for software development workflows

## Future Considerations

- Binary encoding for large datasets
- Diff/patch format for incremental updates
- Query language for filtering items
- Hooks/webhooks for status changes and reminders
- Import/export from iCalendar (VTODO), Markdown, YAML
- Localization support for multi-language content
- Rich text/markdown in content fields
- Encrypted fields for sensitive data
- Free/busy time tracking for resource scheduling
- Conflict resolution strategies for concurrent edits
