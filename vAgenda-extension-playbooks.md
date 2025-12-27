# vAgenda Extension: Playbooks

> **DRAFT EXTENSION**: This document is a draft and subject to change.

**Extension Name**: Playbooks

**Extension Version**: 0.1

**Last Updated**: 2025-12-27

## Overview

In vAgenda terms:
- TodoLists cover **short-term memory** (what to do next).
- Plans cover **medium-term memory** (what/why/how for a piece of work).
- Playbooks cover **long-term memory**: reusable strategies, rules-of-thumb, and warnings that persist across runs.

Playbooks are a way to make an agent’s “working context” improve over time.

The playbook concept in this extension is based on the paper "Agentic Context Engineering: Evolving Contexts for Self-Improving Language Models" (arXiv:2510.04618): https://arxiv.org/abs/2510.04618

If you find these concepts feel difficult to understand, it’s partly because they are, and partly because this spec still has room to improve. Playbooks are a very new and evolving concept, and initial implementations are only just starting to be attempted and tested.


### What playbooks do

Playbooks capture long-term **lessons learned**.

Where TodoLists and Plans primarily record **what** was (or will be) done and **why**, playbooks record higher-level guidance such as:
- what tends to work,
- what tends to fail,
- what to try next,
- and what to avoid.

Importantly, playbooks are designed to be **log-like and reversible**: old guidance is not silently overwritten. Instead, entries are refined, superseded, deduplicated, or quarantined so that tools (and humans) can see how the playbook evolved over time.

Playbooks treat long-term context as a curated set of **entries** that can be:
- appended (growth),
- refined (revision),
- deduplicated,
- and soft-deprecated/quarantined.

This prevents two common failure modes in iterative prompt editing:
- **Context collapse**: repeated rewriting erodes details over time.
- **Brevity bias**: summaries drop “unimportant” details that later turn out to matter.

### How playbooks work (conceptually)

A typical loop:

1. **Execution**
   - Run a task (coding session, workflow, incident response).
2. **Reflection**
   - Record what helped or hurt (increment counters; attach evidence).
3. **Curation**
   - Add new entries, refine existing ones, deduplicate, and quarantine bad advice.
4. **Reuse**
   - Retrieve a relevant subset of entries for the next run.

vAgenda supports this by storing long-term knowledge as Playbook Entries; Entries become an append-only log that preserves history in the playbook.

- Each playbook entry has an `operation` and either creates a new logical entry or updates/deprecates an existing one.
- Updates form a **per-entry linked list** via `prevEventId` (not a single global chain).


## Dependencies

- **Requires**: Extension 2 (Identifiers)
- **Recommended**: Extension 10 (Version Control & Sync)

Notes:
- If Extension 10 is present, tools MAY use the host document’s `sequence` as an optimistic concurrency guard when applying new Playbook Entries.

## Machine-verifiable schema (JSON)

The playbooks extension schema is provided at `schemas/vagenda-extension-playbooks.schema.json`.

## Data model

This extension adds two core concepts:
- `Playbook`: a container for entries and summary metrics.
- `PlaybookEntry`: an **append-only** entry in the playbook log (a create/update/deprecate event).

### New Types (reference)

```javascript
Playbook {
  version: number           # Playbook version (monotonic; increments on update)
  created: datetime         # When playbook was created
  updated: datetime         # Last update time
  entries: PlaybookEntry[]  # Append-only log of playbook entries
  metrics?: PlaybookMetrics # Optional summary stats
}

PlaybookEntry {
  eventId: string           # Unique ID for this event (append-only)
  targetId: string          # Stable ID for the logical entry being evolved
  operation: enum           # "initial" | "append" | "update" | "deprecate"
  prevEventId?: string      # Previous eventId for the same targetId (per-entry linked list)

  kind?: enum               # "strategy" | "learning" | "rule" | "warning" | "note" (required for initial/append)
  title?: string            # Optional short label
  text?: string             # Entry content (required for initial/append; optional for update)
  tags?: string[]
  evidence?: string[]
  confidence?: number       # 0.0-1.0

  delta?: {                 # Merge-safe counters: deltas are commutative and may be accumulated
    helpfulCount?: integer
    harmfulCount?: integer
  }

  feedbackType?: enum       # "humanReview" | "executionOutcome" | "selfReport" | "unknown"

  createdAt: datetime       # When this event was created

  status?: enum             # "active" | "deprecated" | "quarantined" (may be set by update/deprecate)
  deprecatedReason?: string

  supersedes?: string[]     # targetIds that this entry supersedes
  supersededBy?: string     # targetId that supersedes this entry
  duplicateOf?: string      # targetId that this entry duplicates

  reason?: string           # Why this event was added
  metadata?: object         # Extension escape hatch
}

PlaybookMetrics {
  totalEntries: number
  averageConfidence?: number
  lastUpdated?: datetime
}
```

### Attaching a playbook to documents

Playbooks can be attached to either a todo list or a plan:

```javascript
TodoList {
  // Prior extensions...
  playbook?: Playbook
}

Plan {
  // Prior extensions...
  playbook?: Playbook
}
```

## Type guide (with examples)

### Playbook

A `Playbook` is the long-lived container. It holds the entry list (`entries`) plus optional summary metrics.

**JSON example:**

```json
{
  "version": 4,
  "created": "2025-01-10T18:00:00Z",
  "updated": "2025-12-27T08:00:00Z",
  "entries": [],
  "metrics": {
    "totalEntries": 0,
    "lastUpdated": "2025-12-27T08:00:00Z"
  }
}
```

### PlaybookEntry

A `PlaybookEntry` is an **append-only event** in the playbook log.

Guidance:
- Keep it to “one idea per logical entry” (one `targetId`).
- Prefer actionable language.
- Add evidence whenever possible.
- Track feedback via `delta` increments (merge-safe).

#### Example: create (operation = append, kind = strategy)

```json
{
  "eventId": "evt-0100",
  "targetId": "entry-test-first",
  "operation": "append",
  "kind": "strategy",
  "title": "Write a failing test first",
  "text": "Before changing code, write a failing test that reproduces the bug; then implement the minimal fix.",
  "tags": ["testing", "debugging"],
  "confidence": 0.95,
  "feedbackType": "executionOutcome",
  "status": "active",
  "evidence": ["pr:42", "ci:green-run-2025-12-26"],
  "createdAt": "2025-12-27T09:00:00Z"
}
```

#### Example: feedback (delta increment)

```json
{
  "eventId": "evt-0101",
  "targetId": "entry-test-first",
  "operation": "update",
  "prevEventId": "evt-0100",
  "delta": {"helpfulCount": 1},
  "createdAt": "2025-12-27T09:10:00Z",
  "reason": "Bug fix went smoothly with test-first"
}
```

#### Example: refine (operation = update)

```json
{
  "eventId": "evt-0102",
  "targetId": "entry-test-first",
  "operation": "update",
  "prevEventId": "evt-0101",
  "text": "Write a failing test first; then implement the minimal change that makes it pass; finally refactor with tests green.",
  "createdAt": "2025-12-27T09:20:00Z",
  "reason": "Refined wording after repeated use"
}
```

#### Example: supersede (link logical entries)

```json
{
  "eventId": "evt-0200",
  "targetId": "entry-tests-before-fix-v2",
  "operation": "append",
  "kind": "strategy",
  "text": "Write a failing test first; then implement the minimal change that makes it pass; finally refactor with tests green.",
  "supersedes": ["entry-test-first"],
  "createdAt": "2025-12-27T09:30:00Z"
}
```

```json
{
  "eventId": "evt-0201",
  "targetId": "entry-test-first",
  "operation": "update",
  "prevEventId": "evt-0102",
  "supersededBy": "entry-tests-before-fix-v2",
  "createdAt": "2025-12-27T09:30:00Z"
}
```

#### Example: dedup (soft)

```json
{
  "eventId": "evt-0300",
  "targetId": "entry-test-first-duplicate",
  "operation": "append",
  "kind": "strategy",
  "text": "Always start with a failing test.",
  "duplicateOf": "entry-test-first",
  "status": "deprecated",
  "deprecatedReason": "Duplicate entry; keep canonical entry-test-first",
  "createdAt": "2025-12-27T09:40:00Z"
}
```

### PlaybookMetrics

`PlaybookMetrics` are optional summary fields for UI/tooling.

```json
{
  "totalEntries": 27,
  "averageConfidence": 0.86,
  "lastUpdated": "2025-12-27T08:00:00Z"
}
```

### PlaybookEntry operations (event log)

Playbook updates are represented by appending new `PlaybookEntry` objects to `playbook.entries`.

#### initial / append

Create a new logical entry (a new `targetId`). `operation: "initial"` and `operation: "append"` are equivalent; implementations MAY use either.

```json
{
  "eventId": "evt-0001",
  "targetId": "entry-task-first",
  "operation": "append",
  "kind": "rule",
  "text": "For repeatable workflows, add a Task target instead of documenting raw shell commands.",
  "status": "active",
  "feedbackType": "humanReview",
  "createdAt": "2025-12-27T09:00:00Z",
  "reason": "Standardize workflow in this repo"
}
```

#### update

Update an existing logical entry by pointing at the previous event for that `targetId`.

```json
{
  "eventId": "evt-0002",
  "targetId": "entry-task-first",
  "operation": "update",
  "prevEventId": "evt-0001",
  "text": "For repeatable workflows, add a Task target instead of documenting raw shell commands; keep tasks small and declarative.",
  "createdAt": "2025-12-27T09:10:00Z",
  "reason": "Clarify the preferred task style"
}
```

#### delta increments (counters)

Counters are updated via **deltas** (merge-safe).

```json
{
  "eventId": "evt-0003",
  "targetId": "entry-task-first",
  "operation": "update",
  "prevEventId": "evt-0002",
  "delta": {"helpfulCount": 1},
  "createdAt": "2025-12-27T09:20:00Z",
  "reason": "Task target reduced setup time"
}
```

#### deprecate

Soft-deprecate an entry (retain history).

```json
{
  "eventId": "evt-0004",
  "targetId": "entry-test-first-duplicate",
  "operation": "deprecate",
  "prevEventId": "evt-0009",
  "status": "deprecated",
  "deprecatedReason": "Duplicate entry; keep canonical entry-test-first",
  "createdAt": "2025-12-27T09:30:00Z",
  "reason": "Canonicalized into entry-test-first"
}
```

## Playbook invariants (normative)

- Tools MUST update playbooks by **appending** new `PlaybookEntry` events to `playbook.entries`.
- `PlaybookEntry.targetId` MUST be stable once created.
- For a given `targetId`, updates MUST form a per-entry linked list via `prevEventId`.
  - `operation: "append"|"initial"` events MUST NOT set `prevEventId`.
  - `operation: "update"|"deprecate"` events MUST set `prevEventId`.
- Counter updates SHOULD be represented as `delta` increments (commutative / merge-safe).
- Deprecation MUST be soft (retain the entry, mark it non-active).

## Merge semantics (deterministic, non-LLM)

Playbooks are append-only: merging is performed by **set/concat union** of `playbook.entries`.

To compute a “current view” for a given `targetId`, consumers traverse the per-entry linked list (following `prevEventId`) to find the head event and apply its field updates and accumulated `delta` counters.

Concurrent updates may produce multiple heads for the same `targetId`. Implementations MUST either:
- treat this as a conflict, or
- deterministically select a winner using a stable ordering (e.g., higher `createdAt` wins; break ties by lexicographic `eventId`).

Deprecation events SHOULD win over an `active` status unless explicitly reactivated by a later event.

## Grow-and-refine lifecycle

- **Grow**: append new entries (new ids).
- **Refine**: update an entry in place (same id) and link it using `supersedes/supersededBy` when meaningfully revised.
- **Dedup**: mark redundant entries with `duplicateOf` (do not erase history).

## Best practices

- Prefer **append-only** updates (add a new `PlaybookEntry` event) over rewriting `playbook.entries` wholesale.
- Keep entries **atomic** (one idea per entry) to make merge/dedup easier.
- Add **evidence** as soon as you have it (links to PRs, traces, changeLog entries, benchmark results).
- When revising an entry substantially, create a successor entry and connect them via `supersedes/supersededBy` rather than silently editing history.
- Use `duplicateOf` to deduplicate without erasing; keep older entries for provenance.
- Use `status: quarantined` for potentially bad advice instead of deleting; record `deprecatedReason`/notes.
- Treat low-signal feedback (e.g. `feedbackType: selfReport`) as weaker; avoid inflating `confidence` without corroboration.

## Real-world playbook examples

These examples show how a playbook might look in practice for an agentic software repo.

### TRON: playbook embedded in a Plan

```tron
class vAgendaInfo: version
class Plan: id, title, status, narratives, playbook
class Narrative: title, content
class Playbook: version, created, updated, entries, metrics
class PlaybookMetrics: totalEntries, averageConfidence, lastUpdated
class PlaybookEntry:
  eventId, targetId, operation, prevEventId,
  kind, title, text, tags, evidence, confidence,
  delta, feedbackType, createdAt,
  status, deprecatedReason, supersedes, supersededBy, duplicateOf,
  reason

vAgendaInfo: vAgendaInfo("0.2")
plan: Plan(
  "plan-playbooks-realworld-001",
  "Agent workflow rules",
  "inProgress",
  {
    "proposal": Narrative(
      "Overview",
      "Curate reusable agent workflow strategies and warnings; evolve via append-only playbook entries."
    )
  },
  Playbook(
    7,
    "2025-01-10T18:00:00Z",
    "2025-12-27T08:00:00Z",
    [
      PlaybookEntry(
        "evt-0001",
        "entry-task-first",
        "append",
        null,
        "rule",
        "Task-first workflow",
        "For repeatable workflows, add a Task target instead of documenting raw shell commands.",
        ["workflow", "taskfile"],
        ["docs:warp.md"],
        0.9,
        null,
        "humanReview",
        "2025-12-27T09:00:00Z",
        "active",
        null,
        null,
        null,
        null,
        "Standardize workflow in this repo"
      ),
      PlaybookEntry(
        "evt-0002",
        "entry-task-first",
        "update",
        "evt-0001",
        null,
        null,
        null,
        null,
        null,
        null,
        {"helpfulCount": 1},
        "executionOutcome",
        "2025-12-27T09:20:00Z",
        null,
        null,
        null,
        null,
        null,
        "Task target reduced setup time"
      )
    ],
    PlaybookMetrics(1, 0.9, "2025-12-27T09:20:00Z")
  )
)
```

### JSON: playbook embedded in a Plan

```json
{
  "vAgendaInfo": {
    "version": "0.2"
  },
  "plan": {
    "id": "plan-playbooks-realworld-001",
    "title": "Agent workflow rules",
    "status": "inProgress",
    "narratives": {
      "proposal": {
        "title": "Overview",
        "content": "Curate reusable agent workflow strategies and warnings; evolve via append-only playbook entries."
      }
    },
    "playbook": {
      "version": 7,
      "created": "2025-01-10T18:00:00Z",
      "updated": "2025-12-27T09:20:00Z",
      "entries": [
        {
          "eventId": "evt-0001",
          "targetId": "entry-task-first",
          "operation": "append",
          "kind": "rule",
          "title": "Task-first workflow",
          "text": "For repeatable workflows, add a Task target instead of documenting raw shell commands.",
          "tags": ["workflow", "taskfile"],
          "evidence": ["docs:warp.md"],
          "confidence": 0.9,
          "feedbackType": "humanReview",
          "status": "active",
          "createdAt": "2025-12-27T09:00:00Z",
          "reason": "Standardize workflow in this repo"
        },
        {
          "eventId": "evt-0002",
          "targetId": "entry-task-first",
          "operation": "update",
          "prevEventId": "evt-0001",
          "delta": {"helpfulCount": 1},
          "feedbackType": "executionOutcome",
          "createdAt": "2025-12-27T09:20:00Z",
          "reason": "Task target reduced setup time"
        }
      ],
      "metrics": {
        "totalEntries": 1,
        "averageConfidence": 0.9,
        "lastUpdated": "2025-12-27T09:20:00Z"
      }
    }
  }
}
```

## References

- https://arxiv.org/abs/2510.04618
