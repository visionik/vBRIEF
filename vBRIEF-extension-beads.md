# vBRIEF Extension: Beads Interoperability

**Extension Name**: Beads Interop  
**Version**: 0.2  
**Status**: Draft  
**Author**: Jonathan Taylor (visionik@pobox.com)  
**Date**: 2025-12-27

---

## Overview

[Beads](https://github.com/steveyegge/beads) is a git-backed issue tracker created by Steve Yegge that provides persistent, structured memory for coding agents. It stores dependency-aware task graphs in `.beads/` as JSONL, allowing agents to handle long-horizon tasks without losing context between sessions. Beads focuses on \"what matters right now\" - current work, what just finished, and what's blocked.

This extension enables bidirectional interoperability between vBRIEF and Beads by **extending existing vBRIEF classes** rather than creating new types.

## Motivation

**Beads strengths**:
- Real-time execution tracking
- Dependency-aware graph (with bottleneck detection)
- Agent-optimized queries (`bd ready`, `bd blocked`)
- Git-based storage with automatic sync
- Focus on current work

**vBRIEF strengths**:
- Standardized format for cross-system interop
- Rich narratives for plans (the \"why\" and \"how\")
- Long-term memory via Playbooks
- Token-efficient TRON encoding
- Three-tier memory separation

**Integration goal**: Let Beads handle execution tracking while vBRIEF provides knowledge persistence, transfer, and cross-project learning.

## Dependencies

**Required**:
- vBRIEF Core (TodoList, TodoItem, Plan, PlanItem)
- Extension 2 (Identifiers) - for Beads ID mapping
- Extension 4 (Hierarchical) - for dependency tracking

**Recommended**:
- Extension 10 (Version Control & Sync) - for change tracking
- Extension 12 (Playbooks) - for accumulating learnings

---

## Design Principle: Extend Existing Classes

Rather than creating `BeadsIssue` or `BeadsProject` types, we extend existing vBRIEF classes with Beads-specific fields:

- **TodoItem** ↔ Beads issue (with `beadsId`, `beadsMetrics`)
- **Plan** tracks Beads sync state (with `beadsSyncedAt`)
- **PlaybookItem** captures learnings from Beads execution

This maintains vBRIEF's simplicity while enabling rich Beads integration.

---

## Data Model Extensions

### TodoList Extensions

Track which Beads project this TodoList syncs with:

```javascript
TodoList {
  // Core + existing extensions...
  
  // Beads integration
  beadsProject?: string       // Path to Beads project (e.g., ".beads" or "/path/to/project/.beads")
  beadsSyncedAt?: datetime    // Last sync timestamp (ISO 8601)
}
```

### TodoItem Extensions

TodoItems map to Beads issues:

```javascript
TodoItem {
  // Core + existing extensions...
  
  // Beads integration
  beadsId?: string            // Beads issue ID (e.g., "bd-a1b2c3d4")
  beadsMetrics?: {            // Graph metrics from beads_viewer
    pageRank?: number         // PageRank centrality (0-1)
    betweenness?: number      // Betweenness centrality (0-1)
    impactScore?: number      // Estimated impact on project (0-1)
    isBottleneck?: boolean    // Flagged as bottleneck
    inCycle?: boolean         // Part of dependency cycle
    cycleId?: string          // ID of cycle if inCycle=true
  }
}
```

**Note**: TodoItem already has `dependencies` (Extension 4), which maps directly to Beads dependency graph.

### Plan Extensions

Plans track Beads synchronization:

```javascript
Plan {
  // Core + existing extensions...
  
  // Beads integration
  beadsProject?: string       // Associated Beads project path
  beadsSyncedAt?: datetime    // Last sync timestamp
}
```

### PlanItem Extensions

PlanItems can reference Beads issues if tracked:

```javascript
PlanItem {
  // Core + existing extensions...
  
  // Beads integration
  beadsId?: string           // Beads issue ID if this phase is tracked in Beads
}
```

### PlaybookItem Extensions

PlaybookItems accumulate learnings from Beads execution:

```javascript
PlaybookItem {
  // Core + Extension 12 fields...
  
  // Beads integration
  beadsSource?: {            // Provenance from Beads
    project: string          // Beads project path
    issuesCompleted: string[] // Beads IDs that contributed to this learning
    timeframe: {
      start: datetime
      end: datetime
    }
  }
}
```

---

## Mapping Semantics

### Status Mapping: TodoItem ↔ Beads Issue

```
vBRIEF Status    →  Beads Status
-------------------------------------
pending           →  open
inProgress        →  open (with recent activity)
blocked           →  blocked
completed         →  closed
cancelled         →  closed (with cancellation note)
```

### Dependency Mapping

vBRIEF's Extension 4 `dependencies` field maps directly:

```javascript
TodoItem {
  id: "item-2",
  title: "Add auth tests",
  dependencies: ["item-1"],  // Extension 4
  beadsId: "bd-c3d4"         // This extension
}
```

Beads:
```
bd-c3d4: Add auth tests (depends: bd-a1b2)
```

### Metrics Mapping

Beads `beads_viewer --robot-insights` provides graph metrics:

```javascript
TodoItem {
  title: "Refactor auth module",
  beadsMetrics: {
    pageRank: 0.85,           // High centrality
    impactScore: 0.92,        // High impact
    isBottleneck: true,       // Blocking other work
    inCycle: false
  }
}
```

These metrics help prioritize work without requiring separate types.

---

## Usage Patterns

### Pattern 1: Session Handoff

**End of agent session** (Beads → vBRIEF):

```bash
# Agent exports current state
bd export --format=vbrief > session-handoff.json

# Creates vBRIEF TodoList with:
# - Current beads as TodoItems (with beadsId)
# - Dependencies preserved
# - Graph metrics for prioritization
```

Example output:
```json
{
  "vBRIEFInfo": {"version": "0.4"},
  "todoList": {
    "id": "session-2025-12-27",
    "beadsProject": ".beads",
    "beadsSyncedAt": "2025-12-27T21:00:00Z",
    "items": [
      {
        "id": "1",
        "title": "Implement JWT auth",
        "status": "inProgress",
        "beadsId": "bd-a1b2",
        "dependencies": [],
        "beadsMetrics": {
          "impactScore": 0.85,
          "isBottleneck": true
        }
      },
      {
        "id": "2",
        "title": "Add auth tests",
        "status": "pending",
        "beadsId": "bd-c3d4",
        "dependencies": ["1"],
        "beadsMetrics": {
          "impactScore": 0.62,
          "isBottleneck": false
        }
      }
    ]
  }
}
```

**Start of next session** (vBRIEF → Beads):

```bash
# Import updated priorities/context
bd import --format=vbrief session-handoff.json

# Beads sees:
# - New items added by human during planning
# - Updated priorities
# - Context from vBRIEF descriptions
```

### Pattern 2: Plan-Driven Execution

**Human creates Plan, agent executes in Beads:**

```json
{
  "vBRIEFInfo": {"version": "0.4"},
  "plan": {
    "id": "auth-plan",
    "title": "Add OAuth2 Support",
    "status": "approved",
    "beadsProject": ".beads",
    
    "narratives": {
      "proposal": "Add OAuth2 alongside JWT. OAuth for user login, JWT for API tokens.",
      "context": "Must maintain backward compatibility with existing JWT auth."
    },
    
    "items": [
      {
        "id": "phase-1",
        "title": "Configure OAuth provider",
        "status": "pending",
        "description": "Setup OAuth credentials and endpoints for Google/GitHub"
      },
      {
        "id": "phase-2",
        "title": "Implement OAuth flow",
        "status": "pending",
        "dependencies": ["phase-1"],
        "description": "Add OAuth callback handlers and token exchange"
      },
      {
        "id": "phase-3",
        "title": "Test OAuth login",
        "status": "pending",
        "dependencies": ["phase-2"]
      }
    ]
  }
}
```

Agent imports into Beads:
```bash
bd import --format=vbrief auth-plan.json

# Creates Beads issues:
# bd-1: Configure OAuth provider
# bd-2: Implement OAuth flow (depends: bd-1)
# bd-3: Test OAuth login (depends: bd-2)
```

As execution progresses, agent exports back to vBRIEF:
```bash
bd export --format=vbrief > auth-execution.json

# Updates Plan with:
# - PlanItem status changes
# - beadsId fields populated
# - beadsMetrics for tracking progress
```

### Pattern 3: Long-Term Knowledge Extraction

**After completing work, extract learnings to Playbook:**

```bash
# Export completed work
bd export --format=vbrief --closed-since=7d > week-retro.json
```

Human or agent reviews and creates PlaybookItem:
```json
{
  "vBRIEFInfo": {"version": "0.4"},
  "playbook": {
    "version": 1,
    "created": "2025-12-20T00:00:00Z",
    "updated": "2025-12-27T00:00:00Z",
    "items": [
      {
        "eventId": "evt-0001",
        "targetId": "oauth-learning",
        "operation": "append",
        "kind": "strategy",
        "title": "OAuth Integration Best Practices",
        "narrative": {
          "Guidance": "When adding OAuth: (1) Configure provider first, (2) Test token lifecycle early, (3) Maintain JWT compatibility.",
          "Why": "Beads dependency tracking prevented premature integration."
        },
        "status": "active",
        "confidence": 0.9,
        "tags": ["oauth", "authentication"],
        "beadsSource": {
          "project": ".beads",
          "issuesCompleted": ["bd-a1b2", "bd-c3d4", "bd-e5f6"],
          "timeframe": {
            "start": "2025-12-20T00:00:00Z",
            "end": "2025-12-27T00:00:00Z"
          }
        },
        "evidence": [
          {
            "type": "reference",
            "uri": "beads://bd-a1b2",
            "summary": "OAuth config completed without issues"
          },
          {
            "type": "reference",
            "uri": "beads://bd-c3d4",
            "summary": "Token lifecycle testing caught expiry bug early"
          }
        ],
        "createdAt": "2025-12-27T00:00:00Z"
      }
    ]
  }
}
```

### Pattern 4: Multi-Project Learning

Accumulate learnings across projects:

```
Project A (Beads) → vBRIEF Playbook
Project B (Beads) → vBRIEF Playbook  → Unified knowledge base
Project C (Beads) → vBRIEF Playbook
```

Each project's completed Beads issues feed PlaybookItems. Over time, the Playbook captures:
- Which patterns work in which contexts
- Common pitfalls and solutions
- Effective dependency structures
- Bottleneck patterns to avoid

---

## Implementation Notes

### For Beads Developers

Add vBRIEF export to `bd export`:

```go
// In bd export command
case "vbrief":
    exporter := vbrief.NewExporter(db)
    if *closedSince != "" {
        return exporter.ExportPlan(filter, closedSince)
    }
    return exporter.ExportTodoList(filter)
```

**Minimal TodoList export**:
```json
{
  "vBRIEFInfo": {"version": "0.4"},
  "todoList": {
    "items": [
      {
        "id": "1",
        "title": "Fix auth bug",
        "status": "inProgress",
        "beadsId": "bd-a1b2",
        "dependencies": []
      },
      {
        "id": "2",
        "title": "Add tests",
        "status": "pending",
        "beadsId": "bd-c3d4",
        "dependencies": ["1"]
      }
    ],
    "beadsProject": ".beads",
    "beadsSyncedAt": "2025-12-27T21:00:00Z"
  }
}
```

**With metrics** (requires `beads_viewer`):
```json
{
  "vBRIEFInfo": {"version": "0.4"},
  "todoList": {
    "items": [
      {
        "id": "1",
        "title": "Refactor login module",
        "status": "inProgress",
        "beadsId": "bd-a1b2",
        "beadsMetrics": {
          "pageRank": 0.85,
          "impactScore": 0.92,
          "isBottleneck": true,
          "inCycle": false
        }
      }
    ]
  }
}
```

### For vBRIEF Tools

Recognize Beads integration:

```javascript
// When rendering TodoItem
if (item.beadsId) {
  // Show link: beads://bd-a1b2
  // Highlight if isBottleneck or inCycle
  // Sort by impactScore for priority
}

// When rendering PlaybookItem
if (item.beadsSource) {
  // Show provenance
  // Link to source Beads issues
}
```

---

## Integration with Existing Extensions

### Extension 2: Identifiers
- `beadsId` serves as external identifier linking to Beads
- TodoItem `id` remains vBRIEF's internal identifier

### Extension 4: Hierarchical Structures
- `dependencies` array maps directly to Beads dependency graph
- No duplication needed

### Extension 7: Resources & References
- Use `uris` field to link to Beads:
  ```javascript
  TodoItem {
    uris: [
      {
        "uri": "beads://bd-a1b2",
        "type": "x-beads/issue",
        "description": "Source Beads issue"
      }
    ]
  }
  ```

### Extension 10: Version Control & Sync
- `beadsSyncedAt` indicates last Beads sync
- `changeLog` tracks vBRIEF document changes
- Complementary: Beads tracks execution, Extension 10 tracks document evolution

### Extension 12: Playbooks
- `beadsSource` field captures provenance
- PlaybookItems accumulate learnings from Beads execution
- Evidence links back to source Beads issues

---

## Workflow Summary

```
┌─────────────────────────────────────────────────────────────┐
│                      Human Planning                         │
│  vBRIEF Plan with narratives, approach, constraints        │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ↓ bd import --format=vbrief
┌─────────────────────────────────────────────────────────────┐
│                    Agent Execution (Beads)                  │
│  Task tracking, dependency resolution, bottleneck detection │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ↓ bd export --format=vbrief
┌─────────────────────────────────────────────────────────────┐
│                     Session Handoff                         │
│  vBRIEF TodoList with beadsId, metrics, current state      │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ↓ After completion
┌─────────────────────────────────────────────────────────────┐
│                   Knowledge Extraction                      │
│  vBRIEF Playbook with learnings, evidence from Beads       │
└─────────────────────────────────────────────────────────────┘
```

---

## Benefits

1. **No new top-level types** - Uses existing TodoList/Plan/Playbook structure
2. **Simple integration** - Just add `beadsId`, `beadsMetrics`, `beadsSyncedAt` fields
3. **Bidirectional sync** - Beads ↔ vBRIEF in both directions
4. **Preserves strengths** - Beads handles execution, vBRIEF handles knowledge
5. **Cross-project learning** - Playbooks accumulate insights across Beads projects

---

## Open Questions

1. **Should Beads native format adopt vBRIEF?**
   - **Proposal**: Beads keeps JSONL (optimized for agent access), adds vBRIEF as export/import
   
2. **How to handle Beads' memory decay?**
   - Beads compacts old issues to save context
   - vBRIEF Plans preserve full history
   - **Proposal**: Beads compacts for agents, vBRIEF archives for humans

3. **Multi-agent coordination?**
   - Beads uses git for sync
   - vBRIEF Extension 11 (Forking) handles parallel work
   - **Proposal**: Beads for real-time coordination, vBRIEF for merge/conflict resolution

4. **URI scheme for Beads issues?**
   - `beads://bd-a1b2` or `beads://.beads/bd-a1b2`?
   - **Proposal**: `beads://bd-{id}` for simplicity

---

## Migration Path

**Phase 1**: Export only (Beads → vBRIEF)
- Add `bd export --format=vbrief`
- Agents can archive to vBRIEF
- No breaking changes

**Phase 2**: Import support (vBRIEF → Beads)
- Add `bd import --format=vbrief`
- Enable planning → execution workflow
- Still no breaking changes

**Phase 3**: Bidirectional sync
- Real-time sync between Beads and vBRIEF
- vBRIEF tools can query live Beads state
- beads_viewer renders vBRIEF Plans

---

## Examples

### Example 1: Simple TodoList Export

**TRON**:
```tron
class vBRIEFInfo: version
class TodoList: id, items, beadsProject, beadsSyncedAt
class TodoItem: id, title, status, beadsId, dependencies

vBRIEFInfo: vBRIEFInfo("0.4")
todoList: TodoList(
  "session-001",
  [
    TodoItem("1", "Implement JWT auth", "inProgress", "bd-a1b2", []),
    TodoItem("2", "Add auth tests", "pending", "bd-c3d4", ["1"])
  ],
  ".beads",
  "2025-12-27T21:00:00Z"
)
```

### Example 2: TodoList with Metrics

**JSON**:
```json
{
  "vBRIEFInfo": {"version": "0.4"},
  "todoList": {
    "id": "session-002",
    "beadsProject": ".beads",
    "beadsSyncedAt": "2025-12-27T21:30:00Z",
    "items": [
      {
        "id": "1",
        "title": "Refactor login module",
        "status": "inProgress",
        "beadsId": "bd-a1b2",
        "dependencies": [],
        "beadsMetrics": {
          "pageRank": 0.85,
          "impactScore": 0.92,
          "isBottleneck": true,
          "inCycle": false
        }
      },
      {
        "id": "2",
        "title": "Update documentation",
        "status": "pending",
        "beadsId": "bd-c3d4",
        "dependencies": ["1"],
        "beadsMetrics": {
          "pageRank": 0.12,
          "impactScore": 0.15,
          "isBottleneck": false
        }
      }
    ]
  }
}
```

### Example 3: Playbook from Beads Execution

**JSON**:
```json
{
  "vBRIEFInfo": {"version": "0.4"},
  "playbook": {
    "version": 1,
    "created": "2025-12-20T00:00:00Z",
    "updated": "2025-12-27T00:00:00Z",
    "items": [
      {
        "eventId": "evt-0001",
        "targetId": "auth-strategy",
        "operation": "append",
        "kind": "strategy",
        "title": "Dependency-First Auth Implementation",
        "narrative": {
          "Guidance": "When implementing authentication: (1) Setup infrastructure first (DB, providers), (2) Implement core auth logic, (3) Add tests, (4) Integrate with app.",
          "Why": "This dependency order, tracked in Beads, prevented integration bugs."
        },
        "status": "active",
        "confidence": 0.92,
        "tags": ["authentication", "dependencies", "testing"],
        "beadsSource": {
          "project": ".beads",
          "issuesCompleted": ["bd-001", "bd-002", "bd-003", "bd-004"],
          "timeframe": {
            "start": "2025-12-20T00:00:00Z",
            "end": "2025-12-27T00:00:00Z"
          }
        },
        "evidence": [
          {
            "type": "reference",
            "uri": "beads://bd-001",
            "summary": "DB setup - no blocking issues"
          },
          {
            "type": "reference",
            "uri": "beads://bd-002",
            "summary": "Core auth - depended on bd-001, smooth execution"
          },
          {
            "type": "reference",
            "uri": "beads://bd-003",
            "summary": "Testing - caught token expiry bug before integration"
          }
        ],
        "createdAt": "2025-12-27T00:00:00Z"
      }
    ]
  }
}
```

---

## References

- **vBRIEF Core Specification v0.3**: README.md
- **Extension 2 (Identifiers)**: README.md#extension-2-identifiers
- **Extension 4 (Hierarchical)**: README.md#extension-4-hierarchical
- **Extension 10 (Version Control)**: README.md#extension-10-version-control
- **Extension 12 (Playbooks)**: vBRIEF-extension-playbooks.md
- **Beads**: https://github.com/steveyegge/beads
- **beads_viewer**: https://github.com/Dicklesworthstone/beads_viewer
- **Steve Yegge's article**: https://steve-yegge.medium.com/introducing-beads-a-coding-agent-memory-system-637d7d92514a

---

## License

This specification is released under CC BY 4.0.

---

## Changelog

### Version 0.2 (2025-12-27)
- Updated to vBRIEF v0.3 spec
- Simplified to extend existing classes (no new top-level types)
- `beadsMetrics` embedded in TodoItem (not separate type)
- `beadsSyncedAt` on TodoList and Plan (not separate sync type)
- PlaybookItem gets `beadsSource` for provenance tracking
- Clearer workflow diagrams and examples

### Version 0.1 (2025-12-27)
- Initial draft
- Separate BeadsMetrics type
- PlanItem extensions (now PlanItem in v0.3)
