# vBRIEF Extension: Specifications (vSpec)

**Version**: 0.5

**Last Updated**: 2026-01-11

**Status**: DRAFT

## Overview

This extension adds **vSpec** (Specification) as a fourth core container type to vBRIEF, alongside TodoList, Plan, and Playbook. vSpec is designed for structured specification documents including Product Requirements Documents (PRDs), Request for Comments (RFCs), technical design documents, API specifications, and architecture decision records.

vSpec enables specifications to be:
- **Structured**: Requirements, risks, metrics, and decisions as first-class entities
- **Traceable**: Links to implementation Plans, TodoLists, and knowledge Playbooks
- **Versionable**: Track review cycles, approvals, and changes over time
- **Agent-friendly**: Token-efficient TRON encoding with machine-readable structure
- **Standards-compliant**: Uses RFC 2119 priority keywords (MUST, SHOULD, MAY)

## Relationship to Core Specification

This extension builds upon vBRIEF Core v0.4 (see [README.md](./README.md)) and follows the established container patterns:
- Container: `vSpec` (analogous to TodoList, Plan, Playbook)
- Item: `vSpecItem` (analogous to TodoItem, PlanItem, PlaybookItem)
- Container-level narratives use **lowercase keys** (like Plan)
- Item-level narratives use **Title Case keys** (like TodoItem, PlanItem)

## Breaking Changes from Core v0.4

vSpec introduces **kebab-case** for multi-word enum values, which represents a breaking change from v0.4's camelCase:

**Status enum changes:**
- `"inProgress"` → `"in-progress"` (applies to TodoItem, PlanItem, Plan statuses)

**Priority enum:**
- Uses lowercase with hyphens: `"must"`, `"should"`, `"may"`, `"must-not"`, `"should-not"`

These changes improve consistency and readability across all vBRIEF container types.

## When to Use vSpec vs Plan

**Use vSpec when:**
- Documenting **requirements** (functional, non-functional, constraints)
- Capturing **decisions** with rationale and alternatives considered
- Tracking **risks** with severity, probability, and mitigation
- Defining **success metrics** with baselines and targets
- Managing **open questions** during review/approval cycles
- Creating formal specifications (PRD, RFC, technical design, API spec)

**Use Plan when:**
- Organizing **implementation work** into phases or stages
- Coordinating **execution** of a defined approach
- **Less formal** design documents without structured requirements
- Refactoring proposals, spike investigations, or exploratory work

**Rule of thumb**: vSpec answers "WHAT requirements MUST/SHOULD/MAY be satisfied", Plan answers "HOW we'll implement and organize the work".

**In practice**: Many projects will have both — a vSpec (PRD/RFC) that defines requirements, and a Plan that organizes the implementation work. Cross-link them via `uris` or `references`.

---

# Core Data Models

## vSpec (Core Container)

**Purpose**: A structured specification document that captures requirements, constraints, risks, decisions, metrics, and open questions. Used for PRDs, RFCs, technical designs, API specifications, and architecture decision records.

```javascript
vSpec {
  title: string               // Required: Specification title
  status: enum                // Required: Lifecycle status
  type: enum                  // Required: Specification category
  narratives: object          // Required: Container-level sections (lowercase keys)
  items: vSpecItem[]          // Optional: Requirements, risks, metrics, questions, decisions
}
```

### Status Enum

```javascript
vSpecStatus: "draft" | "proposed" | "approved" | "in-progress" | "completed" | "cancelled"
```

**Lifecycle:**
1. `draft` → Author working on specification
2. `proposed` → Submitted for stakeholder review
3. `approved` → Stakeholders signed off; ready for implementation
4. `in-progress` → Being implemented (tracked via linked Plan/TodoList)
5. `completed` → Implementation finished and verified
6. `cancelled` → Specification abandoned or rejected

### Type Enum

```javascript
vSpecType: "prd" | "rfc" | "technical-design" | "architecture" | "api-spec"
```

**Types:**
- `prd`: Product Requirements Document (product features, user requirements)
- `rfc`: Request for Comments (proposals for review and discussion)
- `technical-design`: Technical design document (system architecture, implementation approach)
- `architecture`: Architecture Decision Record (ADR) or architecture specification
- `api-spec`: API specification (REST, GraphQL, RPC interfaces)

### Core Narratives (lowercase keys)

Following the Plan pattern, vSpec uses lowercase narrative keys for container-level sections:

```javascript
vSpec {
  narratives: {
    summary: string,          // Required: Executive summary (1-2 paragraphs)
    problem?: string,         // Problem statement or background context
    solution?: string,        // Proposed solution or approach
    background?: string,      // Current state, prior work, relevant history
    scope?: string,           // What's in scope, out of scope, constraints
    alternatives?: string,    // Alternative approaches considered
    timeline?: string,        // High-level timeline or milestones
    // Custom keys allowed for domain-specific needs
  }
}
```

**Standard narrative keys** (all optional except `summary`):
- **summary**: Executive summary — what, why, and expected outcomes
- **problem**: Problem statement — what needs to be solved/specified
- **solution**: Proposed solution — high-level approach
- **background**: Context — current state, prior work, motivations
- **scope**: Boundaries — what's included, excluded, and constraints
- **alternatives**: Options considered — other approaches and why rejected
- **timeline**: Timeline overview — phases, milestones, dependencies

## vSpecItem (Core Item)

**Purpose**: A discrete component of a specification — requirement, risk, metric, open question, or decision. vSpecItem follows the vBRIEF `Item` abstract base pattern (requires `title` and `status`).

```javascript
vSpecItem extends Item {
  title: string               // Required: Item title (inherited from Item)
  status: enum                // Required: Item status (inherited from Item)
  kind: enum                  // Required: Item discriminator
  priority?: enum             // Optional: RFC 2119 priority level
  narrative?: object          // Optional: Item-level context (Title Case keys)
  metadata?: object           // Optional: Arbitrary key-value data
}
```

### Kind Enum

```javascript
vSpecItemKind: 
  | "requirement"      // Functional or non-functional requirement
  | "risk"             // Risk with mitigation strategy
  | "metric"           // Success metric with target and baseline
  | "question"         // Open question needing resolution
  | "decision"         // Architecture or design decision
  | "constraint"       // Constraint or limitation
  | "dependency"       // External dependency
```

### Priority Enum (RFC 2119)

```javascript
vSpecPriority: "must" | "should" | "may" | "must-not" | "should-not"
```

**Priority semantics** (aligned with RFC 2119):
- `must`: Absolute requirement — must be implemented for launch
- `should`: Strong recommendation — should implement unless good reason not to
- `may`: Optional — nice-to-have, can be deferred
- `must-not`: Explicitly forbidden — must NOT be implemented
- `should-not`: Discouraged — should NOT implement unless good reason to

**Usage:**
- Requirements use `must`, `should`, `may`, `must-not`, `should-not`
- Risks use severity levels in `metadata.severity`: `"critical"`, `"high"`, `"medium"`, `"low"`
- Metrics use importance in `priority`: `"critical"`, `"high"`, `"medium"`, `"low"`
- Questions use priority: `"critical"`, `"high"`, `"medium"`, `"low"`
- Decisions typically don't use priority (use `status` to track completion)

### Status Enum

```javascript
vSpecItemStatus: "pending" | "in-progress" | "completed" | "blocked" | "cancelled"
```

**Status by kind:**
- **requirement**: `pending` (not started), `in-progress` (being implemented), `completed` (verified), `blocked` (dependency/issue), `cancelled` (won't implement)
- **risk**: `pending` (open), `in-progress` (mitigating), `completed` (mitigated/accepted), `cancelled` (no longer relevant)
- **metric**: `pending` (not measuring), `in-progress` (measuring), `completed` (target met), `cancelled` (abandoned)
- **question**: `pending` (unanswered), `completed` (answered), `cancelled` (deferred/irrelevant)
- **decision**: `pending` (not decided), `completed` (decided), `cancelled` (rejected)

### Item Narratives (Title Case keys)

Following vBRIEF patterns, vSpecItem uses Title Case narrative keys:

```javascript
vSpecItem {
  narrative: {
    "Description": string,           // Item description
    "Acceptance Criteria": string,   // For requirements: testable criteria
    "Rationale": string,             // Why this is needed
    "Impact": string,                // For risks: what happens if risk occurs
    "Mitigation": string,            // For risks: how to prevent/reduce
    "Target": string,                // For metrics: target value
    "Baseline": string,              // For metrics: current/starting value
    "Measurement": string,           // For metrics: how to measure
    "Context": string,               // For questions: background context
    "Options": string,               // For questions: possible answers
    "Decision": string,              // For decisions: what was decided
    "Alternatives Rejected": string, // For decisions: why other options rejected
    // Custom Title Case keys allowed
  }
}
```

---

# Examples

## Example 1: Product Requirements Document (PRD)

### Minimal PRD

**TRON:**
```tron
class vBRIEFInfo: version
class vSpec: title, status, type, narratives, items
class vSpecItem: id, kind, title, status, priority, narrative

vBRIEFInfo: vBRIEFInfo("0.5")

vSpec: vSpec(
  "User Authentication - OAuth 2.0",
  "approved",
  "prd",
  {
    "summary": "Enable secure user authentication via OAuth 2.0 with social login providers to increase signup conversion by 25%.",
    "problem": "Users cannot securely authenticate. Current password system lacks MFA and SSO, leading to security risks and poor UX.",
    "solution": "Implement OAuth 2.0 with Google and GitHub providers. Include TOTP-based MFA.",
    "scope": "**In scope**: OAuth flows, TOTP MFA, user migration.\n**Out of scope**: SMS MFA, biometric auth.\n**Constraints**: $50k budget, 12-week timeline."
  },
  [
    vSpecItem(
      "FR-1",
      "requirement",
      "OAuth 2.0 Provider Integration",
      "in-progress",
      "must",
      {
        "Description": "Support Google and GitHub OAuth providers with PKCE flow",
        "Acceptance Criteria": "- Users can sign up via Google OAuth\n- Users can sign up via GitHub OAuth\n- Token refresh works seamlessly"
      }
    ),
    vSpecItem(
      "FR-2",
      "requirement",
      "Multi-Factor Authentication",
      "pending",
      "must",
      {
        "Description": "TOTP-based MFA for all authentication methods",
        "Acceptance Criteria": "- Users can enable/disable MFA\n- Recovery codes generated\n- Sessions invalidated on suspicious activity"
      }
    ),
    vSpecItem(
      "NFR-1",
      "requirement",
      "OAuth Flow Latency",
      "pending",
      "must",
      {
        "Description": "Auth flow completes within 2 seconds p95",
        "Acceptance Criteria": "p95 latency < 2s under normal load"
      }
    ),
    vSpecItem(
      "RISK-1",
      "risk",
      "OAuth provider outage affects service",
      "pending",
      null,
      {
        "Impact": "Users cannot sign up via social login during outage",
        "Mitigation": "Support multiple providers; fallback to email signup"
      }
    ),
    vSpecItem(
      "METRIC-1",
      "metric",
      "Signup Conversion Rate",
      "pending",
      "critical",
      {
        "Target": "+25% increase",
        "Baseline": "42% (Q4 2025)",
        "Measurement": "Mixpanel funnel analysis"
      }
    )
  ]
)
```

**JSON:**
```json
{
  "vBRIEFInfo": {
    "version": "0.5"
  },
  "vSpec": {
    "title": "User Authentication - OAuth 2.0",
    "status": "approved",
    "type": "prd",
    "narratives": {
      "summary": "Enable secure user authentication via OAuth 2.0 with social login providers to increase signup conversion by 25%.",
      "problem": "Users cannot securely authenticate. Current password system lacks MFA and SSO, leading to security risks and poor UX.",
      "solution": "Implement OAuth 2.0 with Google and GitHub providers. Include TOTP-based MFA.",
      "scope": "**In scope**: OAuth flows, TOTP MFA, user migration.\n**Out of scope**: SMS MFA, biometric auth.\n**Constraints**: $50k budget, 12-week timeline."
    },
    "items": [
      {
        "id": "FR-1",
        "kind": "requirement",
        "title": "OAuth 2.0 Provider Integration",
        "status": "in-progress",
        "priority": "must",
        "narrative": {
          "Description": "Support Google and GitHub OAuth providers with PKCE flow",
          "Acceptance Criteria": "- Users can sign up via Google OAuth\n- Users can sign up via GitHub OAuth\n- Token refresh works seamlessly"
        }
      },
      {
        "id": "FR-2",
        "kind": "requirement",
        "title": "Multi-Factor Authentication",
        "status": "pending",
        "priority": "must",
        "narrative": {
          "Description": "TOTP-based MFA for all authentication methods",
          "Acceptance Criteria": "- Users can enable/disable MFA\n- Recovery codes generated\n- Sessions invalidated on suspicious activity"
        }
      },
      {
        "id": "NFR-1",
        "kind": "requirement",
        "title": "OAuth Flow Latency",
        "status": "pending",
        "priority": "must",
        "narrative": {
          "Description": "Auth flow completes within 2 seconds p95",
          "Acceptance Criteria": "p95 latency < 2s under normal load"
        }
      },
      {
        "id": "RISK-1",
        "kind": "risk",
        "title": "OAuth provider outage affects service",
        "status": "pending",
        "narrative": {
          "Impact": "Users cannot sign up via social login during outage",
          "Mitigation": "Support multiple providers; fallback to email signup"
        }
      },
      {
        "id": "METRIC-1",
        "kind": "metric",
        "title": "Signup Conversion Rate",
        "status": "pending",
        "priority": "critical",
        "narrative": {
          "Target": "+25% increase",
          "Baseline": "42% (Q4 2025)",
          "Measurement": "Mixpanel funnel analysis"
        }
      }
    ]
  }
}
```

## Example 2: Request for Comments (RFC)

**TRON:**
```tron
class vBRIEFInfo: version
class vSpec: title, status, type, author, reviewers, tags, narratives, items, uris
class vSpecItem: id, kind, title, status, priority, narrative, metadata
class URI: uri, type, title

vBRIEFInfo: vBRIEFInfo("0.5")

vSpec: vSpec(
  "RFC-042: Adopt Event Sourcing for User State",
  "proposed",
  "rfc",
  "Backend Team",
  ["Platform Lead", "Data Team"],
  ["architecture", "event-sourcing", "user-state"],
  {
    "summary": "Propose adopting event sourcing for user state management to enable temporal queries, audit trails, and simplified CQRS patterns.",
    "problem": "Current CRUD model makes it difficult to answer 'what was user state at time T?', audit trails are ad-hoc, and read/write models are tightly coupled.",
    "solution": "Implement event sourcing for User aggregate: all state changes become immutable events, projections rebuild current state, separate read models for queries.",
    "background": "Increasing compliance requirements need audit trails. Analytics team needs historical state snapshots. Performance issues from complex JOIN queries suggest CQRS would help.",
    "alternatives": "1. Change Data Capture (CDC) on database: Less invasive but doesn't provide event semantics or bounded contexts.\n2. Hybrid: Event sourcing for audit, CRUD for core: More complexity, unclear boundaries.\n3. Full event sourcing (proposed): Clean model, audit trail by design."
  },
  [
    vSpecItem(
      "REQ-1",
      "requirement",
      "Immutable Event Log",
      "pending",
      "must",
      {
        "Description": "All user state changes MUST be persisted as immutable events in append-only log",
        "Acceptance Criteria": "- Events MUST include timestamp, user ID, event type, payload\n- Events MUST NOT be deleted or modified after write\n- Event log MUST support sequential reads by aggregate ID"
      },
      {"category": "functional"}
    ),
    vSpecItem(
      "REQ-2",
      "requirement",
      "Event Replay and Projections",
      "pending",
      "must",
      {
        "Description": "System MUST support replaying events to rebuild state projections",
        "Acceptance Criteria": "- Projections can be rebuilt from event log\n- Replay supports point-in-time snapshots\n- Failed projections can be repaired via replay"
      },
      {"category": "functional"}
    ),
    vSpecItem(
      "REQ-3",
      "requirement",
      "Backwards Compatibility",
      "pending",
      "must",
      {
        "Description": "System MUST maintain backwards compatibility during migration",
        "Acceptance Criteria": "- Existing CRUD APIs continue to work\n- Dual-write period supports both models\n- Rollback path exists if event sourcing fails"
      },
      {"category": "functional", "migration": true}
    ),
    vSpecItem(
      "REQ-4",
      "requirement",
      "Event Schema Versioning",
      "pending",
      "should",
      {
        "Description": "Event schemas SHOULD be versioned to support evolution",
        "Rationale": "Events are immutable; schema changes require version management"
      },
      {"category": "functional"}
    ),
    vSpecItem(
      "Q-1",
      "question",
      "Which event store: custom vs existing?",
      "pending",
      "critical",
      {
        "Context": "Need to decide on PostgreSQL + custom events table vs dedicated event store (EventStoreDB, Kafka).",
        "Options": "1. PostgreSQL + jsonb events table: Simpler ops, leverages existing DB\n2. EventStoreDB: Purpose-built, better performance, new ops burden\n3. Kafka: Already in stack, great for event streaming, not optimized for replay",
        "Owner": "Platform Lead"
      },
      {}
    ),
    vSpecItem(
      "Q-2",
      "question",
      "Snapshot frequency for performance?",
      "pending",
      "high",
      {
        "Context": "Replaying thousands of events per user on every read is expensive. Need snapshot strategy.",
        "Options": "Every 100 events? Every hour? On-demand via background job?",
        "Owner": "Backend Team"
      },
      {}
    ),
    vSpecItem(
      "DEC-1",
      "decision",
      "Start with User aggregate only",
      "completed",
      null,
      {
        "Decision": "Event sourcing for User aggregate only in Phase 1; evaluate for other aggregates after",
        "Rationale": "Reduces scope and risk. User state is highest priority for audit trail. Learn from one aggregate before expanding.",
        "Alternatives Rejected": "Event sourcing for all aggregates: Too much scope, high migration risk"
      },
      {}
    ),
    vSpecItem(
      "RISK-1",
      "risk",
      "Event replay performance degrades over time",
      "pending",
      null,
      {
        "Impact": "As event log grows, replaying full history becomes too slow for real-time queries",
        "Mitigation": "Implement periodic snapshotting; benchmark replay time with 1M+ events; set alert thresholds"
      },
      {"severity": "high", "probability": "medium"}
    )
  ],
  [
    URI("https://martinfowler.com/eaaDev/EventSourcing.html", "text/html", "Martin Fowler: Event Sourcing"),
    URI("https://github.com/org/repo/issues/420", "x-github/issue", "Event Sourcing Epic"),
    URI("file://./designs/event-sourcing-architecture.png", "image/png", "Architecture diagram")
  ]
)
```

## Example 3: Technical Design Document

**TRON:**
```tron
class vBRIEFInfo: version
class vSpec: title, status, type, author, tags, narratives, items, references
class vSpecItem: id, kind, title, status, priority, narrative, metadata
class URI: uri, type, title

vBRIEFInfo: vBRIEFInfo("0.5")

vSpec: vSpec(
  "Rate Limiting Service: Token Bucket Implementation",
  "approved",
  "technical-design",
  "Platform Team",
  ["rate-limiting", "distributed-systems", "redis"],
  {
    "summary": "Design and implement a distributed rate limiting service using token bucket algorithm with Redis backend.",
    "problem": "Multiple services need rate limiting. Current in-memory limiters don't work across instances. Need centralized, low-latency solution.",
    "solution": "Build rate limiting service with: Redis-based token bucket, Lua scripts for atomicity, gRPC API, 99.9% availability.",
    "background": "API gateway needs 10k req/s rate limiting. Background workers need per-user limits. In-memory limiters cause inconsistent limits across replicas.",
    "scope": "**In scope**: Token bucket algorithm, Redis backend, gRPC API, metrics.\n**Out of scope**: Leaky bucket (future), rate limit UI (separate), billing integration."
  },
  [
    vSpecItem(
      "REQ-1",
      "requirement",
      "Token Bucket Algorithm",
      "completed",
      "must",
      {
        "Description": "Implement token bucket rate limiting algorithm",
        "Acceptance Criteria": "- Tokens refill at configured rate\n- Burst capacity supported\n- Atomicity via Lua scripts"
      },
      {"category": "functional"}
    ),
    vSpecItem(
      "REQ-2",
      "requirement",
      "Redis Backend",
      "completed",
      "must",
      {
        "Description": "Use Redis as distributed state backend",
        "Acceptance Criteria": "- Keys expire automatically\n- Supports Redis Cluster\n- Lua scripts for atomic ops"
      },
      {"category": "functional"}
    ),
    vSpecItem(
      "NFR-1",
      "requirement",
      "Latency Target",
      "in-progress",
      "must",
      {
        "Description": "Rate limit check MUST complete in < 5ms p99",
        "Rationale": "Inline with API gateway request path; cannot add significant latency"
      },
      {"category": "performance"}
    ),
    vSpecItem(
      "NFR-2",
      "requirement",
      "Availability Target",
      "pending",
      "must",
      {
        "Description": "Service MUST maintain 99.9% availability",
        "Rationale": "Rate limiting is critical path; outages block all traffic"
      },
      {"category": "availability"}
    ),
    vSpecItem(
      "DEC-1",
      "decision",
      "Token Bucket over Leaky Bucket",
      "completed",
      null,
      {
        "Decision": "Use token bucket algorithm instead of leaky bucket",
        "Rationale": "Token bucket supports bursts naturally. Simpler implementation. Industry standard for API rate limiting.",
        "Alternatives Rejected": "Leaky bucket: More complex, doesn't support bursts without additional logic"
      },
      {}
    ),
    vSpecItem(
      "DEC-2",
      "decision",
      "Redis over Cassandra",
      "completed",
      null,
      {
        "Decision": "Use Redis for state storage instead of Cassandra",
        "Rationale": "Sub-millisecond latency required. Lua scripts provide atomicity. TTL support built-in. Team has Redis expertise.",
        "Alternatives Rejected": "Cassandra: Higher latency (5-15ms), no Lua scripts, manual TTL cleanup"
      },
      {}
    ),
    vSpecItem(
      "CONST-1",
      "constraint",
      "Must integrate with existing Redis cluster",
      "pending",
      null,
      {
        "Description": "Rate limiter MUST use existing production Redis cluster; cannot deploy separate cluster due to ops constraints"
      },
      {}
    )
  ],
  [
    URI("file://./plans/rate-limiting-implementation.vbrief.json", "x-vbrief/plan", "Implementation plan"),
    URI("file://./playbooks/redis-best-practices.vbrief.json", "x-vbrief/playbook", "Redis playbook")
  ]
)
```

## Example 4: API Specification

**JSON:**
```json
{
  "vBRIEFInfo": {
    "version": "0.5"
  },
  "vSpec": {
    "title": "User Management API v2",
    "status": "approved",
    "type": "api-spec",
    "author": "API Team",
    "tags": ["api", "rest", "users", "v2"],
    "narratives": {
      "summary": "RESTful API for user management operations: CRUD, search, and role assignment.",
      "background": "v1 API has inconsistent error handling, no pagination, and missing batch operations. v2 addresses these gaps.",
      "scope": "**In scope**: User CRUD, search, roles, pagination, batch ops.\n**Out of scope**: Authentication (separate service), user preferences (future)."
    },
    "items": [
      {
        "id": "API-1",
        "kind": "requirement",
        "title": "GET /v2/users/:id - Retrieve User",
        "status": "completed",
        "priority": "must",
        "narrative": {
          "Description": "Retrieve a single user by ID",
          "Acceptance Criteria": "- Returns 200 with user object on success\n- Returns 404 if user not found\n- Returns 403 if caller lacks permission\n- Response includes user ID, email, name, roles, created_at, updated_at"
        },
        "metadata": {
          "method": "GET",
          "path": "/v2/users/:id",
          "auth": "required"
        }
      },
      {
        "id": "API-2",
        "kind": "requirement",
        "title": "POST /v2/users - Create User",
        "status": "completed",
        "priority": "must",
        "narrative": {
          "Description": "Create a new user",
          "Acceptance Criteria": "- Requires email, name in request body\n- Returns 201 with created user on success\n- Returns 400 if validation fails\n- Returns 409 if email already exists"
        },
        "metadata": {
          "method": "POST",
          "path": "/v2/users",
          "auth": "required",
          "role": "admin"
        }
      },
      {
        "id": "API-3",
        "kind": "requirement",
        "title": "GET /v2/users - List Users with Pagination",
        "status": "in-progress",
        "priority": "must",
        "narrative": {
          "Description": "List users with cursor-based pagination",
          "Acceptance Criteria": "- Supports ?limit and ?cursor query params\n- Returns users array and next_cursor\n- Max limit: 100 users per page\n- Supports filtering by role"
        },
        "metadata": {
          "method": "GET",
          "path": "/v2/users",
          "auth": "required"
        }
      },
      {
        "id": "API-4",
        "kind": "requirement",
        "title": "POST /v2/users/batch - Batch Create Users",
        "status": "pending",
        "priority": "should",
        "narrative": {
          "Description": "Create multiple users in single request",
          "Acceptance Criteria": "- Accepts array of user objects (max 100)\n- Returns 207 Multi-Status with per-user results\n- Partial success allowed (some users created, some failed)"
        },
        "metadata": {
          "method": "POST",
          "path": "/v2/users/batch",
          "auth": "required",
          "role": "admin"
        }
      },
      {
        "id": "NFR-1",
        "kind": "requirement",
        "title": "Response Time Target",
        "status": "pending",
        "priority": "must",
        "narrative": {
          "Description": "All API endpoints MUST respond within 200ms p95",
          "Acceptance Criteria": "p95 latency < 200ms under normal load (1000 req/s)"
        },
        "metadata": {
          "category": "performance"
        }
      },
      {
        "id": "NFR-2",
        "kind": "requirement",
        "title": "Consistent Error Format",
        "status": "completed",
        "priority": "must",
        "narrative": {
          "Description": "All errors MUST use RFC 7807 Problem Details format",
          "Acceptance Criteria": "Error response includes type, title, status, detail, instance fields"
        },
        "metadata": {
          "category": "api-design"
        }
      },
      {
        "id": "DEC-1",
        "kind": "decision",
        "title": "Cursor-based pagination over offset",
        "status": "completed",
        "narrative": {
          "Decision": "Use cursor-based pagination instead of offset/limit",
          "Rationale": "Cursor pagination is more efficient for large datasets, prevents missed/duplicate records during concurrent modifications.",
          "Alternatives Rejected": "Offset/limit: Deep pagination performance issues, inconsistent results with concurrent writes"
        }
      }
    ],
    "uris": [
      {
        "uri": "https://api.example.com/openapi/v2.yaml",
        "type": "application/yaml",
        "title": "OpenAPI 3.0 Spec"
      },
      {
        "uri": "file://./docs/api-migration-v1-to-v2.md",
        "type": "text/markdown",
        "title": "Migration Guide"
      }
    ]
  }
}
```

---

# Extension Fields

vSpec leverages existing vBRIEF extensions for additional functionality:

## Extension 1: Timestamps

Adds `created`, `updated` timestamps to vSpec and vSpecItem.

```javascript
vSpec {
  // Core fields...
  created?: datetime
  updated?: datetime
}

vSpecItem {
  // Core fields...
  created?: datetime
  updated?: datetime
}
```

## Extension 2: Identifiers

Adds `id` and `uid` for cross-referencing.

```javascript
vSpec {
  // Core fields...
  id?: string        // Document identifier
  uid?: string       // Globally unique identifier
}

vSpecItem {
  // Core fields...
  id?: string        // Item identifier (often FR-1, NFR-2, RISK-1)
  uid?: string       // Globally unique identifier
}
```

## Extension 3: Rich Metadata

Adds `tags`, `metadata` for classification.

```javascript
vSpec {
  // Core fields...
  tags?: string[]           // ["authentication", "security", "Q1-2026"]
  metadata?: object         // Arbitrary key-value pairs
}

vSpecItem {
  // Core fields...
  tags?: string[]           // ["api", "performance"]
  metadata?: object         // {effort: "40h", category: "functional", severity: "high"}
}
```

**Common metadata patterns:**
- Requirements: `{effort, category, subcategory}`
- Risks: `{severity, probability}`
- Metrics: `{unit, frequency}`
- Questions: `{owner, due_date}`

## Extension 4: Hierarchical Structures

Adds `subItems` for nested requirements.

```javascript
vSpecItem {
  // Core fields...
  subItems?: vSpecItem[]    // Nested sub-requirements
}
```

**Example**: Parent requirement "OAuth Integration" with sub-requirements "Google Provider", "GitHub Provider", "Token Refresh".

## Extension 6: Participants & Collaboration

Adds `author`, `reviewers`, `participants` for collaboration tracking.

```javascript
vSpec {
  // Core fields...
  author?: string           // Specification author
  reviewers?: string[]      // Stakeholders reviewing the spec
}

vSpecItem {
  // Core fields...
  participants?: Participant[]  // People involved in item
}

Participant {
  id: string                // Participant identifier
  name?: string             // Display name
  email?: string            // Email address
  role: enum                // "owner" | "assignee" | "reviewer" | "observer"
  status?: enum             // "accepted" | "declined" | "tentative" | "needs-action"
}
```

## Extension 7: Resources & References

Adds `uris` and `references` for linking to external resources and vBRIEF documents.

```javascript
vSpec {
  // Core fields...
  uris?: URI[]              // External resources (docs, mockups, tickets)
  references?: Reference[]  // Links to other vBRIEF documents
}

vSpecItem {
  // Core fields...
  uris?: URI[]              // Item-specific resources
  todoList?: TodoList       // Embed implementation tasks
  plan?: Plan               // Link to implementation plan
}

URI {
  uri: string               // Resource URI (file://, https://)
  type?: string             // MIME type or custom type
  title?: string            // Human-readable title
  description?: string      // Resource description
}

Reference {
  uri: string               // vBRIEF document URI
  type: string              // "x-vbrief/todoList" | "x-vbrief/plan" | "x-vbrief/playbook"
  title?: string            // Document title
}
```

**Common URI types:**
- `x-github/issue`, `x-github/pr`: GitHub issues and pull requests
- `x-vbrief/todoList`, `x-vbrief/plan`, `x-vbrief/playbook`: vBRIEF documents
- `text/markdown`, `application/pdf`, `image/png`: Standard MIME types
- `x-incident`, `x-design`, `x-competitor-analysis`: Custom types

## Extension 10: Version Control & Sync

Adds `sequence`, `changeLog` for tracking revisions.

```javascript
vSpec {
  // Core fields...
  sequence?: number         // Monotonically increasing version number
  changeLog?: Change[]      // History of changes
}

Change {
  sequence: number          // Change sequence number
  timestamp: datetime       // When change occurred
  agent: Agent              // Who made the change
  operation: string         // "create" | "update" | "approve" | "reject"
  reason?: string           // Why the change was made
}

Agent {
  id: string                // Agent identifier
  type: string              // "human" | "ai" | "system"
  name?: string             // Display name
  email?: string            // Email address
}
```

---

# Cross-Container Relationships

vSpec works seamlessly with other vBRIEF containers:

## vSpec → Plan
**Relationship**: Specification defines **what**, Plan defines **how**.

```javascript
// PRD (vSpec) links to implementation plan
{
  "vSpec": {
    "title": "User Authentication - OAuth 2.0",
    "type": "prd",
    "status": "approved",
    "references": [
      {
        "uri": "file://./plans/auth-implementation.vbrief.json",
        "type": "x-vbrief/plan",
        "title": "OAuth Implementation Plan"
      }
    ]
  }
}

// Implementation Plan references PRD
{
  "plan": {
    "title": "OAuth Implementation Plan",
    "status": "in-progress",
    "uris": [
      {
        "uri": "file://./specs/oauth-prd.vbrief.json",
        "type": "x-vbrief/spec",
        "title": "User Authentication PRD"
      }
    ]
  }
}
```

## vSpec → TodoList
**Relationship**: vSpecItem requirements link to implementation tasks.

```javascript
// Requirement with embedded TodoList
{
  "vSpecItem": {
    "id": "FR-1",
    "kind": "requirement",
    "title": "OAuth 2.0 Provider Integration",
    "status": "in-progress",
    "todoList": {
      "items": [
        {"title": "Implement Google OAuth client", "status": "completed"},
        {"title": "Implement GitHub OAuth client", "status": "in-progress"},
        {"title": "Add token refresh logic", "status": "pending"}
      ]
    }
  }
}
```

## vSpec → Playbook
**Relationship**: Specifications reference accumulated knowledge; Playbooks capture lessons learned from implementations.

```javascript
// RFC references playbook for best practices
{
  "vSpec": {
    "title": "RFC-042: Event Sourcing",
    "type": "rfc",
    "references": [
      {
        "uri": "file://./playbooks/distributed-systems-playbook.vbrief.json",
        "type": "x-vbrief/playbook",
        "title": "Distributed Systems Best Practices"
      }
    ]
  }
}

// After implementation, update playbook
{
  "playbook": {
    "items": [
      {
        "eventId": "evt-101",
        "targetId": "event-sourcing-lessons",
        "operation": "append",
        "kind": "learning",
        "narrative": {
          "Lesson": "Event replay performance degrades after 10k events without snapshots. Implement snapshotting from day 1.",
          "Evidence": "Observed in RFC-042 implementation; caused production issues"
        },
        "tags": ["event-sourcing", "performance"],
        "evidence": ["RFC-042", "INC-2401"]
      }
    ]
  }
}
```

---

# Use Case Patterns

## Pattern 1: PRD → Plan → TodoList → Playbook

Complete specification-to-execution-to-learning workflow:

1. **vSpec (PRD)**: Define requirements, success metrics, risks
2. **Plan**: Break down implementation into phases
3. **TodoList**: Track tactical execution of each phase
4. **Playbook**: Capture lessons learned during implementation

```
specs/auth-prd.vbrief.json (vSpec)
  ↓ references
plans/auth-implementation.vbrief.json (Plan)
  ↓ contains
plans/auth-implementation.vbrief.json#phase-1 (PlanItem)
  ↓ todoList
  [TodoItem, TodoItem, TodoItem]
  ↓ after completion
playbooks/authentication-playbook.vbrief.json (Playbook)
  ↓ contains
  [PlaybookItem: "Always test OAuth token refresh under load"]
```

## Pattern 2: RFC → Decision → Follow-up RFCs

RFC review process with decision tracking:

1. **vSpec (RFC)**: Propose architecture change with alternatives
2. **vSpecItem (question)**: Open questions during review
3. **vSpecItem (decision)**: Record approved decision with rationale
4. **New vSpec (RFC)**: Follow-up RFCs for deferred items

```javascript
// Initial RFC
{
  "vSpec": {
    "title": "RFC-042: Event Sourcing",
    "status": "approved",
    "items": [
      {"kind": "question", "title": "Which event store?", "status": "completed"},
      {"kind": "decision", "title": "Use PostgreSQL + jsonb", "status": "completed"}
    ]
  }
}

// Follow-up RFC for deferred item
{
  "vSpec": {
    "title": "RFC-043: Migrate to EventStoreDB",
    "status": "draft",
    "narratives": {
      "background": "RFC-042 chose PostgreSQL for simplicity. After 6 months, performance limitations suggest dedicated event store."
    },
    "uris": [
      {"uri": "file://./specs/rfc-042.vbrief.json", "type": "x-vbrief/spec", "title": "RFC-042"}
    ]
  }
}
```

## Pattern 3: API Spec → Client Libraries → Integration Tests

API specification driving implementation:

1. **vSpec (api-spec)**: Define API endpoints, request/response schemas
2. **Plan**: Organize server + client library implementation
3. **TodoList**: Track client library tasks per language
4. **vSpecItem (requirement)**: Link to integration test suite

```javascript
{
  "vSpec": {
    "title": "User Management API v2",
    "type": "api-spec",
    "items": [
      {
        "id": "API-1",
        "kind": "requirement",
        "title": "GET /v2/users/:id",
        "status": "completed",
        "uris": [
          {"uri": "file://./tests/integration/users_test.go", "type": "text/plain", "title": "Integration tests"}
        ]
      }
    ],
    "references": [
      {"uri": "file://./plans/api-v2-rollout.vbrief.json", "type": "x-vbrief/plan"}
    ]
  }
}
```

---

# Comparison with Existing Standards

vSpec is designed to capture structured specifications in machine-readable format while remaining compatible with industry-standard approaches:

## PRD Standards

Traditional PRDs are typically written in:
- **Google Docs / Markdown**: Unstructured prose
- **Confluence / Notion**: Semi-structured pages
- **Linear / Jira**: Issue-tracking tools (not specification format)

**vSpec advantages:**
- Machine-readable structure (requirements, metrics, risks as first-class entities)
- Version control friendly (JSON/TRON diffs)
- Traceable to implementation (links to Plan, TodoList)
- Agent-friendly (LLMs can parse, update, generate)

**vSpec compatibility:**
- Can generate Markdown/HTML from vSpec for human review
- Can import requirements from existing tools via scripts
- Maintains human-readable narratives for context

## RFC Patterns

RFCs follow formats like:
- **IETF RFCs**: Structured text with MUST/SHOULD/MAY keywords (RFC 2119)
- **Rust RFCs**: Markdown with Summary, Motivation, Guide, Reference sections
- **Python PEPs**: reStructuredText with Abstract, Motivation, Specification sections

**vSpec advantages:**
- Uses RFC 2119 priority keywords (MUST, SHOULD, MAY)
- Structured decisions and alternatives (not buried in prose)
- Tracks open questions with owners and due dates
- Cross-links to implementation artifacts

**vSpec compatibility:**
- Narratives map to RFC sections (summary → Abstract, problem → Motivation, solution → Specification)
- Can generate RFC-format text from vSpec for external publication
- Maintains RFC numbering via `id` field (RFC-042)

## API Specifications

API specs use formats like:
- **OpenAPI (Swagger)**: YAML/JSON schema for REST APIs
- **GraphQL Schema**: SDL (Schema Definition Language)
- **Protocol Buffers**: `.proto` files for gRPC
- **AsyncAPI**: YAML schema for event-driven APIs

**vSpec advantages:**
- Higher-level requirements capture (why endpoints exist, success criteria)
- Tracks non-functional requirements (latency, error handling)
- Links API spec to implementation plan and tests
- Captures design decisions (why REST over GraphQL, etc.)

**vSpec compatibility:**
- Can reference OpenAPI/GraphQL schemas via `uris`
- Can embed API design decisions not captured in OpenAPI (versioning strategy, pagination approach)
- Can generate OpenAPI stubs from vSpecItems for endpoints

## Architecture Decision Records (ADRs)

ADRs follow formats like:
- **Michael Nygard ADR**: Context, Decision, Status, Consequences
- **Y-Statements**: "In context X, facing Y, we decided Z to achieve W, accepting Q"
- **Markdown templates**: Various templates with Status, Context, Decision, Consequences sections

**vSpec advantages:**
- Structured alternatives and rationale (not prose)
- Decision status tracking (proposed → completed)
- Links to related decisions and implementations
- Machine-readable for querying decision history

**vSpec compatibility:**
- `vSpecItem kind: "decision"` maps to ADR format
- Narratives map to ADR sections (Context → Context, Decision → Decision, "Alternatives Rejected" → not captured in traditional ADR)
- Can generate ADR Markdown from vSpecItem decisions

---

# Best Practices

## Requirement IDs

Use prefixed identifiers:
- `FR-1`, `FR-2`: Functional Requirements
- `NFR-1`, `NFR-2`: Non-Functional Requirements
- `RISK-1`, `RISK-2`: Risks
- `METRIC-1`, `METRIC-2`: Success Metrics
- `Q-1`, `Q-2`: Open Questions
- `DEC-1`, `DEC-2`: Decisions
- `CONST-1`, `CONST-2`: Constraints
- `DEP-1`, `DEP-2`: Dependencies

## Priority Guidelines

**Use `must` when:**
- Requirement is blocking for launch
- Non-negotiable constraint
- Regulatory/compliance requirement

**Use `should` when:**
- Strongly recommended but can be deferred
- Degrades experience if missing but doesn't block launch
- Best practice but workarounds exist

**Use `may` when:**
- Nice-to-have feature
- Can be deferred to future phase
- Low-impact improvement

**Use `must-not` when:**
- Security anti-pattern
- Explicitly forbidden by regulation
- Known to cause critical issues

**Use `should-not` when:**
- Discouraged but not forbidden
- Code smell or non-ideal pattern
- Prefer alternative approach

## Narrative Keys

**Container-level (lowercase):**
- Keep narratives focused: 1-3 paragraphs each
- Use Markdown for formatting (lists, bold, links)
- `summary` is always required; other narratives optional

**Item-level (Title Case):**
- "Description": What the item is
- "Acceptance Criteria": Testable conditions (for requirements)
- "Rationale": Why it's needed
- "Impact": What happens if risk occurs (for risks)
- "Mitigation": How to prevent/reduce (for risks)
- "Target": Success target (for metrics)
- "Baseline": Starting value (for metrics)
- "Measurement": How to measure (for metrics)

## Linking Specs to Implementation

Always cross-link specifications to execution artifacts:

```javascript
{
  "vSpec": {
    "title": "PRD: Feature X",
    "references": [
      {"uri": "file://./plans/feature-x.vbrief.json", "type": "x-vbrief/plan", "title": "Implementation Plan"},
      {"uri": "file://./playbooks/feature-playbook.vbrief.json", "type": "x-vbrief/playbook", "title": "Lessons Learned"}
    ]
  }
}
```

## Review Workflow

Leverage `status` for review cycles:

1. `draft` → Author writing spec
2. `proposed` → Send for review (set `reviewers` field)
3. During review: Add `vSpecItem kind: "question"` for open questions
4. `approved` → Stakeholders signed off
5. `in-progress` → Implementation started (link to Plan/TodoList)
6. `completed` → Implementation finished, metrics verified

## Metadata Patterns

Use `metadata` for domain-specific fields:

**Requirements:**
```javascript
{
  "kind": "requirement",
  "metadata": {
    "effort": "40 hours",
    "category": "functional",
    "subcategory": "authentication",
    "team": "backend"
  }
}
```

**Risks:**
```javascript
{
  "kind": "risk",
  "metadata": {
    "severity": "high",
    "probability": "medium",
    "owner": "Platform Lead",
    "review_date": "2026-02-01"
  }
}
```

**Metrics:**
```javascript
{
  "kind": "metric",
  "metadata": {
    "unit": "percentage",
    "frequency": "daily",
    "dashboard": "https://grafana.example.com/d/metrics"
  }
}
```

---

# Migration from Other Formats

## From Markdown PRD

1. Parse headings into narratives (Problem → problem, Solution → solution)
2. Extract requirements from bulleted lists → `vSpecItem kind: "requirement"`
3. Extract risks from "Risks" section → `vSpecItem kind: "risk"`
4. Extract metrics from "Success Criteria" → `vSpecItem kind: "metric"`
5. Set `status: "draft"` initially

## From Confluence/Notion

1. Export to Markdown or HTML
2. Parse structured sections into narratives
3. Extract tables (requirements, risks) into vSpecItems
4. Preserve attachments/images as URIs
5. Maintain version history via changeLog

## From Jira Epic

1. Epic title → vSpec title
2. Epic description → narratives.summary
3. Linked issues → vSpecItems (Story → requirement, Risk → risk)
4. Acceptance criteria → vSpecItem.narrative["Acceptance Criteria"]
5. Link back to Jira via uris (x-jira/epic)

---

# Appendix: Complete Schema

## vSpec (Core)

```javascript
vSpec {
  // Required fields
  title: string                    // Specification title
  status: vSpecStatus              // Lifecycle status
  type: vSpecType                  // Specification category
  narratives: {                    // Container-level narratives (lowercase keys)
    summary: string,               // Required: Executive summary
    problem?: string,              // Optional: Problem statement
    solution?: string,             // Optional: Proposed solution
    background?: string,           // Optional: Context
    scope?: string,                // Optional: Boundaries
    alternatives?: string,         // Optional: Alternatives considered
    timeline?: string,             // Optional: Timeline overview
    [key: string]: string          // Custom narrative keys allowed
  }
  
  // Optional fields (core)
  items?: vSpecItem[]              // Specification items
  
  // Extension fields
  id?: string                      // Ext 2: Document identifier
  uid?: string                     // Ext 2: Globally unique identifier
  author?: string                  // Ext 6: Author name
  reviewers?: string[]             // Ext 6: Reviewer names
  tags?: string[]                  // Ext 3: Tags for classification
  metadata?: object                // Ext 3: Arbitrary key-value pairs
  created?: datetime               // Ext 1: Creation timestamp
  updated?: datetime               // Ext 1: Last update timestamp
  timezone?: string                // Ext 1: IANA timezone
  sequence?: number                // Ext 10: Version number
  changeLog?: Change[]             // Ext 10: Change history
  uris?: URI[]                     // Ext 7: External resources
  references?: Reference[]         // Ext 7: vBRIEF document links
}
```

## vSpecItem (Core)

```javascript
vSpecItem extends Item {
  // Required fields
  title: string                    // Item title (from Item)
  status: vSpecItemStatus          // Item status (from Item)
  kind: vSpecItemKind              // Item discriminator
  
  // Optional fields (core)
  priority?: vSpecPriority         // RFC 2119 priority
  narrative?: {                    // Item-level narratives (Title Case keys)
    [key: string]: string          // Title Case keys: "Description", "Acceptance Criteria", etc.
  }
  metadata?: object                // Arbitrary key-value pairs
  
  // Extension fields
  id?: string                      // Ext 2: Item identifier
  uid?: string                     // Ext 2: Globally unique identifier
  tags?: string[]                  // Ext 3: Tags
  created?: datetime               // Ext 1: Creation timestamp
  updated?: datetime               // Ext 1: Last update timestamp
  subItems?: vSpecItem[]           // Ext 4: Nested sub-items
  participants?: Participant[]     // Ext 6: People involved
  uris?: URI[]                     // Ext 7: External resources
  todoList?: TodoList              // Ext 7: Embedded implementation tasks
  plan?: Plan                      // Ext 7: Link to implementation plan
}
```

## Enums

```javascript
vSpecStatus: "draft" | "proposed" | "approved" | "in-progress" | "completed" | "cancelled"

vSpecItemStatus: "pending" | "in-progress" | "completed" | "blocked" | "cancelled"

vSpecType: "prd" | "rfc" | "technical-design" | "architecture" | "api-spec"

vSpecItemKind: "requirement" | "risk" | "metric" | "question" | "decision" | "constraint" | "dependency"

vSpecPriority: "must" | "should" | "may" | "must-not" | "should-not"
```

---

# Appendix: Open Questions

1. **Should vSpec be added to Core v0.5 or remain an extension?**
   - Adding to core makes it a 4th sibling to TodoList/Plan/Playbook
   - Keeping as extension maintains backward compatibility with v0.4
   - Recommendation: Promote to core in v0.5 given clear use case and pattern alignment

2. **Should we add `rejected` to vSpecStatus?**
   - Distinguishes "cancelled during drafting" from "formally rejected after review"
   - Current workaround: Use `cancelled` + changeLog entry
   - Recommendation: Add `rejected` for clarity

3. **Should vSpecItem support `dependencies` field?**
   - PlanItem already has `dependencies: string[]` for task ordering
   - vSpecItem could use it for requirement dependencies
   - Current workaround: Use `narrative` or `metadata` to describe dependencies
   - Recommendation: Add `dependencies?: string[]` to vSpecItem (Extension 5)

4. **Should we standardize metadata schemas per kind?**
   - Example: All `kind: "risk"` items should have `metadata.severity` and `metadata.probability`
   - Pro: Enables better tooling, validation, querying
   - Con: Reduces flexibility, increases spec complexity
   - Recommendation: Define recommended metadata patterns in best practices, keep validation optional

5. **Should narrative keys be enumerated or freeform?**
   - Current: Freeform Title Case keys with recommended patterns
   - Alternative: Enumerate allowed keys per `kind` (stricter validation)
   - Recommendation: Keep freeform; recommend patterns in best practices

---

# License

This extension specification is released under CC BY 4.0.

# Feedback and Contributions

Feedback, suggestions, and contributions are highly encouraged. Please submit input via GitHub issues or pull requests at: https://github.com/visionik/vbrief
