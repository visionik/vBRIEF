# vBRIEF v0.5 Specification: Unified Plan Model

**Version**: 0.5 (Beta)  
**Status**: Draft for Implementation  
**Date**: 2026-02-03  
**Author**: Generated from structured interview process

## Overview

vBRIEF v0.5 represents a fundamental architectural refactor that unifies todos, plans, playbooks, and prompt-graphs into a single "Plan" object with graduated complexity and DAG (Directed Acyclic Graph) capabilities.

This specification eliminates the separate `TodoList` and `Playbook` container types, creating a unified model where:
- **Simple Plans** function as todo lists (minimal fields)
- **Structured Plans** add narratives and context (planning documents)
- **Retrospective Plans** capture execution outcomes (playbook-style)
- **Graph Plans** use DAG edges for complex workflows (prompt-graph patterns)

## Goals

This refactor MUST:

1. **Unify container types** - Eliminate TodoList and Playbook; Plan becomes the universal container
2. **Support graduated complexity** - Simple use cases stay simple; advanced features available when needed
3. **Enable DAG workflows** - Support typed relationships between items for complex execution patterns
4. **Preserve minimalism** - Core remains lightweight; optional fields support advanced scenarios
5. **Maintain token efficiency** - TRON encoding optimized for LLM context windows
6. **Ensure interoperability** - JSON Schema validation; clear conformance criteria

## Requirements

### Functional Requirements

#### Core Model

- Plan MUST be the only container type
- Plan MUST support items with hierarchical nesting (via `subItems`)
- Plan MUST support optional DAG relationships via `edges` field
- PlanItem MUST unify all TodoItem and PlanItem fields from v0.4
- Narratives MUST be optional (not required)
- Items MUST support both simple task tracking and complex phase management

#### DAG Support

- Edges MUST support typed relationships: `blocks`, `informs`, `invalidates`, `suggests`
- Edge types MAY be extended with custom string values
- Edges MUST reference items using hierarchical IDs (dot notation: `parent.child`)
- Edge references MUST form a valid DAG (no cycles)
- Edge references MUST point to existing item IDs

#### Status Model

- Single universal Status enum MUST be used for all entities
- Status values MUST be: `draft`, `proposed`, `approved`, `pending`, `running`, `completed`, `blocked`, `cancelled`

#### URI References

- PlanItem MAY reference external Plans via `planRef` field
- URI syntax MUST support: `#item-id` (internal), `file://...` (local), `https://...` (remote)
- Fragment syntax (#) MUST refer to specific items within Plans

#### Narrative Conventions

- Narrative keys SHOULD use TitleCase convention
- Planning narratives SHOULD use: `Proposal`, `Overview`, `Background`, `Problem`, `Constraint`, `Hypothesis`, `Alternative`, `Risk`, `Test`, `Action`, `Observation`, `Result`, `Reflection`
- Retrospective narratives SHOULD use: `Outcome`, `Strengths`, `Weaknesses`, `Lessons`
- Custom narrative keys are allowed via `additionalProperties`

### Non-Functional Requirements

#### Performance

- TRON encoding MUST reduce tokens by 35-40% vs JSON for typical documents
- DAG validation MUST complete in O(V+E) time complexity
- Schema validation MUST be implementable in all target languages (Go, Python, TypeScript)

#### Compatibility

- JSON Schema MUST validate all conformant documents
- Implementations MUST preserve unknown fields when rewriting documents
- TRON format MUST be parseable by existing TRON libraries

#### Extensibility

- Core fields promoted from extensions: `id`, `uid`, `tags`, `metadata`, `created`, `updated`
- Additional extension fields MAY be added without breaking conformance
- Edge types MAY be extended by community; core types MUST be supported

## Architecture

### Document Structure

```
vBRIEF Document (v0.5)
├── vBRIEFInfo (required)
│   ├── version: "0.5" (required)
│   ├── created, updated (optional, promoted to core)
│   └── metadata (optional, promoted to core)
└── plan (required, one per document)
    ├── title (required)
    ├── status (required)
    ├── items (required, can be empty array)
    ├── narratives (optional)
    ├── edges (optional, for DAG)
    ├── id, uid (optional, promoted to core)
    ├── tags (optional, promoted to core)
    ├── created, updated (optional, promoted to core)
    └── metadata (optional, promoted to core)
```

### PlanItem Structure

```
PlanItem
├── id (optional, hierarchical: "parent.child")
├── uid (optional, globally unique)
├── title (required)
├── status (required)
├── narrative (optional, object with TitleCase keys)
├── subItems (optional, array of PlanItem)
├── planRef (optional, URI to external Plan)
├── tags (optional, promoted to core)
├── metadata (optional, promoted to core)
├── created, updated (optional, promoted to core)
├── priority (optional, from TodoItem)
├── dueDate, completed (optional, from TodoItem)
├── percentComplete (optional)
├── startDate, endDate (optional, from v0.4 PlanItem)
├── participants (optional, Extension)
├── location (optional, Extension)
├── uris (optional, Extension)
├── recurrence, reminders (optional, Extension)
└── classification (optional, Extension)
```

### Edge Structure

```tron
class Edge: from, to, type

plan.edges: [
  Edge("item-1", "item-2", "blocks"),
  Edge("item-1", "item-3", "informs")
]
```

**Edge Types (core):**
- `blocks` - Target cannot start until source completes
- `informs` - Target benefits from source context but not blocked
- `invalidates` - Source completion makes target unnecessary
- `suggests` - Weak recommendation, no hard dependency

### Hierarchical ID System

- IDs MUST be user-assigned, stable, semantic strings
- Parent-child relationships MUST be encoded via dot notation
- Examples: `setup`, `setup.auth`, `setup.auth.oauth`, `deployment.prod`
- IDs MUST be unique within Plan scope
- Edges reference items using these hierarchical IDs

### Graduated Complexity Examples

**Minimal Plan (todo-like):**
```json
{
  "vBRIEFInfo": {"version": "0.5"},
  "plan": {
    "title": "Daily Tasks",
    "status": "running",
    "items": [
      {"title": "Fix bug", "status": "pending"},
      {"title": "Review PR", "status": "running"}
    ]
  }
}
```

**Structured Plan (with narratives):**
```json
{
  "vBRIEFInfo": {"version": "0.5"},
  "plan": {
    "title": "API Redesign",
    "status": "proposed",
    "narratives": {
      "Proposal": "Refactor REST API to GraphQL",
      "Background": "Current API has 50+ endpoints...",
      "Problem": "Overfetching and maintenance burden"
    },
    "items": [...]
  }
}
```

**Retrospective Plan (playbook):**
```json
{
  "vBRIEFInfo": {"version": "0.5"},
  "plan": {
    "title": "Incident Response: DB Outage",
    "status": "completed",
    "narratives": {
      "Outcome": "Restored service in 45 minutes",
      "Strengths": "Clear runbook, fast escalation",
      "Weaknesses": "Monitoring gaps, manual failover",
      "Lessons": "Automate failover, add canary queries"
    },
    "items": [...]
  }
}
```

**Graph Plan (with DAG):**
```tron
class Edge: from, to, type

vBRIEFInfo: {version: "0.5"}
plan: {
  title: "Build Pipeline",
  status: "running",
  items: [
    {id: "lint", title: "Lint code", status: "completed"},
    {id: "test", title: "Run tests", status: "running"},
    {id: "build", title: "Build artifacts", status: "pending"},
    {id: "deploy", title: "Deploy to staging", status: "pending"}
  ],
  edges: [
    Edge("lint", "build", "blocks"),
    Edge("test", "build", "blocks"),
    Edge("build", "deploy", "blocks"),
    Edge("lint", "test", "informs")
  ]
}
```

## Conformance

A document is **vBRIEF v0.5 conformant** if and only if:

1. Contains `vBRIEFInfo` with `version: "0.5"`
2. Contains exactly one `plan` object (no `todoList` or `playbook`)
3. Plan has required fields: `title`, `status`, `items`
4. All `status` values use defined enum: `draft`, `proposed`, `approved`, `pending`, `running`, `completed`, `blocked`, `cancelled`
5. If `edges` present, they form a valid DAG (acyclic, valid item references)
6. Hierarchical IDs (if present) follow dot notation (e.g., `parent.child`)
7. Edge types are strings; core types (`blocks`, `informs`, `invalidates`, `suggests`) MUST be supported
8. Unknown fields MUST be preserved by implementations
9. `planRef` URIs (if present) MUST follow syntax: `#item-id`, `file://...`, or `https://...`
10. Narrative object keys (if present) SHOULD use TitleCase convention

## Implementation Plan

### Phase 1: Core Schema and Data Model

**Goal**: Establish unified Plan model with schema validation

#### Subphase 1.1: Schema Definition

- **Task 1.1.1**: Create unified `vbrief-core.schema.json`
  - Dependencies: None
  - Acceptance: Single schema file validates Plan with all core fields
  - Details: Remove TodoList, Playbook; merge PlanItem/TodoItem fields

- **Task 1.1.2**: Define Status enum
  - Dependencies: None
  - Acceptance: Universal Status type with 8 values (draft → cancelled)
  - Details: Single enum for Plan and PlanItem status

- **Task 1.1.3**: Define Edge schema structure
  - Dependencies: None
  - Acceptance: Edge type with from/to/type fields; validation rules
  - Details: Edge class in TRON, object in JSON

- **Task 1.1.4**: Add promoted core fields
  - Dependencies: Task 1.1.1
  - Acceptance: id, uid, tags, metadata, created, updated in core schema
  - Details: Optional fields on Plan and PlanItem

**Testing**: Schema validates minimal Plan, structured Plan, Plan with edges

#### Subphase 1.2: Data Type Definitions (depends on: 1.1)

- **Task 1.2.1**: Define PlanItem with merged fields
  - Dependencies: Task 1.1.1, 1.1.2
  - Acceptance: PlanItem includes all TodoItem fields (priority, dueDate, etc.)
  - Details: Single unified item type

- **Task 1.2.2**: Implement hierarchical ID validation
  - Dependencies: Task 1.2.1
  - Acceptance: Validator accepts dot-notation IDs, enforces uniqueness
  - Details: Regex pattern, uniqueness checker

- **Task 1.2.3**: Define URI reference syntax
  - Dependencies: Task 1.2.1
  - Acceptance: planRef accepts #fragment, file://, https://
  - Details: URI parser for internal/external references

**Testing**: All data types validate correctly; hierarchical IDs work across nesting levels

### Phase 2: DAG Support (depends on: Phase 1)

**Goal**: Implement typed edges with cycle detection

#### Subphase 2.1: Edge Types and Storage

- **Task 2.1.1**: Implement core edge types
  - Dependencies: Phase 1 complete
  - Acceptance: blocks, informs, invalidates, suggests defined with semantics
  - Details: Documentation of each type's meaning

- **Task 2.1.2**: Add edges field to Plan
  - Dependencies: Task 2.1.1
  - Acceptance: Plan.edges as array of Edge; stored at Plan level only
  - Details: Not on PlanItem; centralized graph structure

- **Task 2.1.3**: Implement edge type extensibility
  - Dependencies: Task 2.1.1
  - Acceptance: Unknown edge types allowed, consumers ignore gracefully
  - Details: Open string type with core type documentation

**Testing**: Edges serialize/deserialize correctly in JSON and TRON

#### Subphase 2.2: Graph Validation (depends on: 2.1)

- **Task 2.2.1**: Implement cycle detection algorithm
  - Dependencies: Subphase 2.1 complete
  - Acceptance: Validator detects cycles, rejects invalid graphs
  - Details: DFS-based cycle detection, O(V+E) complexity

- **Task 2.2.2**: Implement reference validation
  - Dependencies: Task 2.2.1
  - Acceptance: All edge from/to references resolve to existing items
  - Details: ID resolution across hierarchical structure

- **Task 2.2.3**: Add validation to schema/tooling
  - Dependencies: Task 2.2.1, 2.2.2
  - Acceptance: Conformance checker validates DAG constraints
  - Details: Reference implementation in primary language

**Testing**: Cycle detection works; dangling references rejected; valid DAGs accepted

### Phase 3: TRON Encoding (depends on: Phase 2)

**Goal**: Optimize token efficiency with TRON format

#### Subphase 3.1: TRON Class Definitions

- **Task 3.1.1**: Define Edge class for TRON
  - Dependencies: Phase 2 complete
  - Acceptance: `class Edge: from, to, type` with positional encoding
  - Details: Compact tuple representation

- **Task 3.1.2**: Define PlanItem class for TRON
  - Dependencies: Phase 2 complete
  - Acceptance: Efficient TRON encoding of all PlanItem fields
  - Details: Common fields in positional args, optional in named

- **Task 3.1.3**: Create TRON encoding examples
  - Dependencies: Task 3.1.1, 3.1.2
  - Acceptance: Examples showing 35-40% token reduction
  - Details: Side-by-side JSON/TRON comparisons

**Testing**: TRON parses correctly; token counts verify savings

#### Subphase 3.2: TRON Parser Integration (depends on: 3.1)

- **Task 3.2.1**: Integrate TRON library (per language)
  - Dependencies: Subphase 3.1 complete
  - Acceptance: Go, Python, TypeScript parsers handle vBRIEF TRON
  - Details: Import/configure TRON libraries

- **Task 3.2.2**: Implement TRON ↔ JSON conversion
  - Dependencies: Task 3.2.1
  - Acceptance: Bidirectional conversion without data loss
  - Details: Preserve unknown fields, maintain structure

**Testing**: Round-trip conversion preserves data; both formats validate

### Phase 4: Documentation (depends on: Phase 3)

**Goal**: Comprehensive, layered documentation for v0.5

#### Subphase 4.1: Core Documentation

- **Task 4.1.1**: Write SPECIFICATION.md
  - Dependencies: Phase 3 complete
  - Acceptance: Formal spec with conformance criteria
  - Details: This document, refined from interview

- **Task 4.1.2**: Update README.md
  - Dependencies: Task 4.1.1
  - Acceptance: Overview, quick start, goals, core concepts
  - Details: User-friendly introduction to v0.5

- **Task 4.1.3**: Create GUIDE.md
  - Dependencies: Task 4.1.1
  - Acceptance: Usage patterns, examples, best practices
  - Details: How-to documentation for common scenarios

**Testing**: Documentation review by stakeholders

#### Subphase 4.2: Migration and Examples (depends on: 4.1)

- **Task 4.2.1**: Write MIGRATION.md
  - Dependencies: Subphase 4.1 complete
  - Acceptance: v0.4 → v0.5 migration guide
  - Details: TodoList → Plan, Playbook → Plan conversions

- **Task 4.2.2**: Create use case examples
  - Dependencies: Task 4.2.1
  - Acceptance: 5 examples showing graduated complexity
  - Details: Simple task list, sprint plan, technical design, retrospective, prompt graph

- **Task 4.2.3**: Update extension documentation
  - Dependencies: Task 4.2.1
  - Acceptance: Extension docs reflect promoted core fields
  - Details: Remove redundant extensions; document remaining ones

**Testing**: Examples validate against schema; migration guide tested

### Phase 5: API Implementations (depends on: Phase 4)

**Goal**: Reference implementations in target languages

#### Subphase 5.1: Go API

- **Task 5.1.1**: Define Go structs for Plan model
  - Dependencies: Phase 4 complete
  - Acceptance: Plan, PlanItem, Edge structs with JSON tags
  - Details: Idiomatic Go naming, struct tags for JSON/TRON

- **Task 5.1.2**: Implement DAG validation in Go
  - Dependencies: Task 5.1.1
  - Acceptance: CycleDetector, ReferenceValidator functions
  - Details: Efficient Go implementation

- **Task 5.1.3**: Add TRON support to Go API
  - Dependencies: Task 5.1.2
  - Acceptance: Marshal/Unmarshal TRON format
  - Details: Integrate TRON-go library

**Testing**: Go API validates all conformant documents; rejects invalid ones

#### Subphase 5.2: Python API (depends on: 5.1, can run in parallel)

- **Task 5.2.1**: Define Pydantic models
  - Dependencies: Phase 4 complete
  - Acceptance: Plan, PlanItem, Edge models with validation
  - Details: Use Pydantic for schema validation

- **Task 5.2.2**: Implement DAG validation in Python
  - Dependencies: Task 5.2.1
  - Acceptance: NetworkX-based or custom cycle detection
  - Details: Pythonic implementation

- **Task 5.2.3**: Add TRON support to Python API
  - Dependencies: Task 5.2.2
  - Acceptance: Parse/emit TRON format
  - Details: Integrate TRON-py library

**Testing**: Python API matches Go behavior; all tests pass

#### Subphase 5.3: TypeScript API (depends on: 5.1, can run in parallel)

- **Task 5.3.1**: Define TypeScript interfaces
  - Dependencies: Phase 4 complete
  - Acceptance: Plan, PlanItem, Edge types with Zod schemas
  - Details: Type-safe TypeScript definitions

- **Task 5.3.2**: Implement DAG validation in TypeScript
  - Dependencies: Task 5.3.1
  - Acceptance: Cycle detection using graphlib or custom
  - Details: Modern JavaScript implementation

- **Task 5.3.3**: Add TRON support to TypeScript API
  - Dependencies: Task 5.3.2
  - Acceptance: Parse/stringify TRON format
  - Details: Integrate TRON-ts library

**Testing**: TypeScript API type-checks correctly; runtime validation works

### Phase 6: Tooling and Validation (depends on: Phase 5)

**Goal**: Developer tools for working with v0.5 documents

#### Subphase 6.1: CLI Validator

- **Task 6.1.1**: Build vbrief-validate CLI tool
  - Dependencies: Phase 5 complete
  - Acceptance: CLI validates JSON/TRON files against v0.5 schema
  - Details: Reports conformance errors with line numbers

- **Task 6.1.2**: Add --fix option for common issues
  - Dependencies: Task 6.1.1
  - Acceptance: Auto-fix TitleCase narrative keys, normalize IDs
  - Details: Non-destructive fixes with diff preview

**Testing**: Validator catches all conformance violations

#### Subphase 6.2: Visualization Tools (depends on: 6.1)

- **Task 6.2.1**: Build DAG visualizer
  - Dependencies: Subphase 6.1 complete
  - Acceptance: Generate graph diagrams from edges
  - Details: Graphviz/Mermaid output formats

- **Task 6.2.2**: Create Plan explorer TUI
  - Dependencies: Task 6.2.1
  - Acceptance: Interactive TUI to browse Plan structure
  - Details: Navigate items, view edges, display narratives

**Testing**: Visualizations accurate; TUI usable

### Phase 7: Release and Community (depends on: Phase 6)

**Goal**: Launch v0.5 with community support

#### Subphase 7.1: Release Preparation

- **Task 7.1.1**: Tag v0.5-beta release
  - Dependencies: Phase 6 complete
  - Acceptance: Git tag, GitHub release with artifacts
  - Details: Schemas, docs, examples packaged

- **Task 7.1.2**: Publish API packages
  - Dependencies: Task 7.1.1
  - Acceptance: Go module, PyPI package, npm package published
  - Details: Versioned as 0.5.0-beta

- **Task 7.1.3**: Update vbrief.dev website
  - Dependencies: Task 7.1.1
  - Acceptance: Website reflects v0.5 as current version
  - Details: Update docs, examples, download links

**Testing**: All published packages install and work correctly

#### Subphase 7.2: Community Engagement (depends on: 7.1)

- **Task 7.2.1**: Write announcement blog post
  - Dependencies: Subphase 7.1 complete
  - Acceptance: Post explaining v0.5 vision and changes
  - Details: Highlight unified model, DAG support, token efficiency

- **Task 7.2.2**: Create migration support channels
  - Dependencies: Task 7.2.1
  - Acceptance: GitHub Discussions, Discord/Slack for support
  - Details: Community can ask questions, share feedback

- **Task 7.2.3**: Solicit early adopter feedback
  - Dependencies: Task 7.2.1
  - Acceptance: 5+ external users testing v0.5
  - Details: Iterate based on real-world usage

**Testing**: Community engagement metrics; issue triage

## Testing Strategy

### Unit Testing

- Schema validation for all conformance criteria
- DAG cycle detection edge cases (self-loops, complex cycles)
- Hierarchical ID parsing and resolution
- URI reference parsing
- Status enum validation
- TRON encoding/decoding round-trips

### Integration Testing

- Multi-language API interoperability (Go ↔ Python ↔ TypeScript)
- File format conversions (JSON ↔ TRON)
- Large document performance (1000+ items, 5000+ edges)
- Cross-document references (planRef to external files)

### Validation Testing

- Conformant documents pass all validators
- Non-conformant documents rejected with clear errors
- Edge cases: empty Plans, deeply nested items, complex DAGs
- Malformed documents handled gracefully

### Example Testing

- All documentation examples validate
- Use case examples demonstrate graduated complexity
- TRON examples achieve target token reduction (35-40%)

## Deployment

### Package Distribution

- **Go**: `github.com/visionik/vBRIEF` module
- **Python**: `vbrief` package on PyPI
- **TypeScript**: `@vbrief/core` package on npm
- **Schemas**: Hosted at `https://vbrief.dev/schemas/`

### Documentation Hosting

- Primary docs at `https://vbrief.dev/`
- Versioned docs (v0.4, v0.5) available
- Schema files available via CDN for validation tools

### Backward Compatibility

- v0.4 documents NOT automatically compatible
- MIGRATION.md provides conversion guidance
- No automated migration tool (no existing implementations)
- Parsers SHOULD detect v0.4 and provide upgrade message

## Rationale and Tradeoffs

### Key Decisions

**Immediate TodoList/Playbook removal**: No implementations exist yet, so no migration burden. Clean break enables coherent v0.5 story.

**Graduated complexity over modes**: Making fields optional is more flexible than explicit mode flags. Users naturally adopt features as needed.

**Plan-level edges only**: Centralized graph structure simplifies validation and visualization. Hierarchical IDs handle nesting.

**Stable user-assigned IDs**: More maintainable than positional IDs. Semantic names (e.g., "auth.setup") self-document.

**Universal Status enum**: Plan and item lifecycles differ, but shared statuses (running, completed) reduce complexity.

**Promote common fields to core**: id, uid, tags, metadata, timestamps are universally useful. Reduces extension overhead.

**TitleCase narrative convention (SHOULD)**: Encourages consistency without being prescriptive. Custom keys still allowed.

**Open edge type extensibility**: Community can experiment with new relationship types. Successful patterns inform future specs.

### Tradeoffs

**Complexity vs Power**: DAG edges add conceptual complexity. Mitigated by: optional field, graduated examples, clear docs.

**Breaking changes**: v0.4 incompatibility is significant. Justified by: no implementations yet, cleaner long-term architecture.

**Single container vs multiple**: Loses explicit type distinction. Gained: simplicity, unified tooling, clear mental model.

## Appendix: Interview Questions and Answers

<details>
<summary>Complete Interview Log</summary>

**Q1: Core Unification Strategy**  
A: Option 2 - Graduated Complexity (keep Plan as only container, make fields optional)

**Q2: DAG Relationship Semantics**  
A: Option 3 - Hybrid Approach (simple dependencies array + optional edges field)

**Q3: Container Elimination Strategy**  
A: Option 4 - Immediate Removal (drop TodoList now in v0.5-beta)

**Q4: Playbook Integration Strategy**  
A: Option 5 - Implement playbook via Plan + DAG semantics (narratives capture retrospective)

**Q5: Playbook Representation via Plan+DAG**  
A: Option 3 - Narrative-Based Approach (use narrative object with conventional keys)

**Q6: Retrospective Narrative Key Names**  
A: Option 6 - Custom: `Outcome`, `Strengths`, `Weaknesses`, `Lessons`

**Q7: Advanced DAG Features (edges field)**  
A: Option 1 - Minimal Typed Edges (with future Option 4 for data flow)

**Q8: Edge Relationship Types**  
A: Option 3 - Semantic Set (`blocks`, `informs`, `invalidates`, `suggests`)

**Q9: Plan Minimalism (Replacing TodoList)**  
A: Option 2 - Make Narratives Optional (only title, status, items required)

**Q10: PlanItem vs TodoItem Unification**  
A: Option 1 - Eliminate TodoItem (merge all fields into PlanItem)

**Q11: Schema Breaking Changes and Versioning**  
A: Option 1 - v0.5 (Beta) (continue incremental versioning)

**Q12: Migration Tooling**  
A: Option 5 - No tooling needed (no implementations exist yet)

**Q13: Extension System Impact**  
A: Option 3 - Consolidate Extensions (merge/eliminate based on new core)

**Q14: TRON Encoding for New Structures**  
A: Option 1 - Class-Based Edges (self-documenting field names)

**Q15: Narrative Key Conventions**  
A: Option 2 - Schema Enumeration (document known keys in schema)

**Q16: Validation and DAG Cycle Detection**  
A: Option 2 - Spec-Level Requirements (MUST form valid DAG, provide algorithm)

**Q17: Nested PlanItems and Edge Scope**  
A: Option 2 - Path-Based References (hierarchical IDs, cross-level edges allowed)

**Q18: Simple dependencies vs edges Coexistence**  
A: Option 4 - Dependencies Deprecated (remove dependencies field, use edges only)

**Q19: Edge Storage Location**  
A: Option 1 - Plan-Level Only (centralized edges array)

**Q20: Status Enums After Unification**  
A: Option 2 - Universal Status Enum (but change `inProgress` to `running`)

**Q21: Hierarchical ID Assignment Strategy**  
A: Option 2 - Stable User-Assigned (semantic IDs with dot notation)

**Q22: Items Array Requirement**  
A: Option 2 - Items Required (Can Be Empty)

**Q23: Documentation Structure**  
A: Option 2 - Layered Documentation (README, SPECIFICATION, GUIDE, MIGRATION)

**Q24: Edge Type Extensibility**  
A: Option 2 - Open String with Core Types (allow custom, recommend core)

**Q25: Testing and Validation Examples**  
A: Option 2 - Use Case Spectrum (demonstrate graduated complexity)

**Q26: Embedded TodoList in PlanItems**  
A: Option 4 - Make it a Plan Reference (planRef URI field, internal reference syntax)

**Q27: Plan Container Required Fields (Final Check)**  
A: Option 1 - Approve as-is (title, status, items only)

**Q28: Schema File Organization**  
A: Option 1 - Single Schema File (merge into vbrief-core.schema.json)

**Q29: Implementation Timeline and Phasing**  
A: Option 1 - Single Release (v0.5) (all changes together)

**Q30: Extension Consolidation Strategy**  
A: Option 1 - Promote Common Features to Core (id, uid, tags, metadata, timestamps)

**Q31: Core Fields to Promote from Extensions**  
A: Option 2 - Identity + Metadata + Tags (id, uid, tags, metadata, created, updated)

**Q32: Final Conformance Requirements**  
A: Options 1 & 2 & 3 (base criteria + URI validation + TitleCase SHOULD)

</details>

---

**Next Steps**: Type `implement SPECIFICATION.md` to begin implementation.
