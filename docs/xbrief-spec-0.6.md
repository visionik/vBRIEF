# xBRIEF Specification v0.6

**Status**: Beta  
**Date**: 2026-03-31  
**Author**: Jonathan Taylor  

## Abstract

xBRIEF (Basic Relational Intent Exchange Format) is a structured document format for representing plans, tasks, workflows, and retrospectives. This specification defines the xBRIEF v0.6 data model, serialization rules, and conformance requirements. A xBRIEF document contains exactly one Plan object with optional narrative context, directed acyclic graph (DAG) edges for modeling dependencies, and nested PlanItem hierarchies using `items` as the preferred nesting field while retaining `subItems` as a deprecated compatibility alias.

## Status of This Document

This document specifies a beta release of the xBRIEF format. It is intended for early implementers and feedback. Comments and issues should be filed at <https://github.com/visionik/xBRIEF/issues>.

## Table of Contents

1. [Introduction](#1-introduction)
2. [Document Structure](#2-document-structure)
3. [Plan Object](#3-plan-object)
4. [PlanItem Object](#4-planitem-object)
5. [Status Enum](#5-status-enum)
6. [DAG (Directed Acyclic Graph) Support](#6-dag-directed-acyclic-graph-support)
7. [TRON Encoding](#7-tron-encoding)
8. [Conformance](#8-conformance)
9. [Security Considerations](#9-security-considerations)
10. [References](#10-references)
11. [Appendix A: JSON Schema Reference](#appendix-a-json-schema-reference)
12. [Appendix B: Complete Examples](#appendix-b-complete-examples)

---

## 1. Introduction

### 1.1 Purpose

xBRIEF provides a single, portable format for capturing planning artifacts ranging from simple task lists to complex dependency graphs with retrospective narratives. It is designed for use by both humans and autonomous agents (LLMs), with particular attention to token efficiency in AI context windows.

### 1.2 Terminology

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in [RFC 2119][rfc2119].

### 1.3 Design Goals

1. **Graduated complexity** — A minimal document requires only four fields. Advanced features are strictly additive.
2. **Token efficiency** — The TRON encoding provides 35–40% token reduction over JSON for LLM context windows.
3. **Dependency modeling** — First-class DAG support for blocking relationships, conditional branches, and workflows.
4. **Interoperability** — JSON-native with a formal JSON Schema for validation.
5. **Extensibility** — Unknown fields MUST be preserved; custom edge types and narrative keys are permitted.

---

## 2. Document Structure

### 2.1 Root Object

A xBRIEF document is a JSON object with the following top-level fields:

| Field | Type | Requirement | Description |
|-------|------|-------------|-------------|
| `xBRIEFInfo` | object | REQUIRED | Document metadata including format version. |
| `plan` | object | REQUIRED | Exactly one Plan object. |

A conformant document MUST contain both `xBRIEFInfo` and `plan` at the root level. A conformant document MUST NOT contain more than one `plan` object. Additional root-level fields MAY be present and MUST be preserved by implementations.

### 2.2 xBRIEFInfo Object

| Field | Type | Requirement | Description |
|-------|------|-------------|-------------|
| `version` | string | REQUIRED | Format version. MUST be `"0.6"` for this specification. |
| `created` | string (ISO 8601) | OPTIONAL | Document creation timestamp. |
| `updated` | string (ISO 8601) | OPTIONAL | Document last-modified timestamp. |
| `metadata` | object | OPTIONAL | Arbitrary key-value metadata. |

The `version` field MUST be the string `"0.6"`. Implementations MUST reject documents with unrecognized version strings or MAY handle them with a clear warning.

---

## 3. Plan Object

The `plan` field contains the primary planning artifact.

### 3.1 Required Fields

| Field | Type | Requirement | Description |
|-------|------|-------------|-------------|
| `title` | string | REQUIRED | Human-readable name of the plan. |
| `status` | string | REQUIRED | Current plan status. MUST be a valid Status enum value (see [Section 5](#5-status-enum)). |
| `items` | array | REQUIRED | Array of PlanItem objects. MAY be empty. |

### 3.2 Optional Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Stable semantic identifier for the plan. |
| `uid` | string | Globally unique identifier (e.g., UUID). |
| `narratives` | object | Plan-level narrative context (see [Section 3.3](#33-narratives)). |
| `edges` | array | Array of Edge objects defining dependencies (see [Section 6](#6-dag-directed-acyclic-graph-support)). |
| `tags` | array of strings | Categorization tags. |
| `metadata` | object | Arbitrary key-value metadata. |
| `architecture` | object | Architecture design records for the plan, including system-of-record declarations. |
| `created` | string (ISO 8601) | Plan creation timestamp. |
| `updated` | string (ISO 8601) | Plan last-modified timestamp. |
| `author` | string | Plan author identifier. |
| `reviewers` | array of strings | Reviewer identifiers. |
| `uris` | array of strings | Related URIs. |
| `references` | array | Related document references. |
| `timezone` | string | IANA timezone identifier. |
| `agent` | string | Agent or system that created/manages the plan. |
| `lastModifiedBy` | string | Identifier of last modifier. |
| `changeLog` | array | Array of change records. |
| `sequence` | integer | Monotonically increasing revision counter. |
| `fork` | object | Fork metadata for derived plans. |

### 3.3 Narratives

The `narratives` field is an OPTIONAL object with string keys and string values. Each key represents a narrative category, and each value contains the narrative text.

Keys SHOULD use TitleCase convention.

#### 3.3.1 Recommended Planning Narrative Keys

The following keys are RECOMMENDED for planning documents:

- `Proposal` — What is being proposed
- `Overview` — High-level summary
- `Background` — Context and history
- `Problem` — Problem statement
- `Constraint` — Limitations and boundaries
- `Hypothesis` — Assumptions being tested
- `Alternative` — Other options considered
- `Risk` — Potential issues and mitigations
- `Test` — Validation criteria
- `Action` — Prescribed actions
- `Observation` — Observed outcomes
- `Result` — Measured results
- `Reflection` — Lessons and insights

#### 3.3.2 Recommended Retrospective Narrative Keys

The following keys are RECOMMENDED for retrospective documents:

- `Outcome` — What happened
- `Strengths` — What went well
- `Weaknesses` — What did not go well
- `Lessons` — What to do differently

#### 3.3.3 Custom Keys

Additional narrative keys are permitted. Implementations MUST preserve all narrative keys, including unrecognized ones. Custom keys SHOULD follow TitleCase convention for consistency.

### 3.4 Architecture

The `architecture` field is an OPTIONAL object for design records that apply to the plan as a whole. Implementations MUST preserve all keys in this object, including unrecognized keys.

#### 3.4.1 System of Record

The `architecture.systemOfRecord` field declares the authoritative owner for stateful behavior introduced or modified by the plan. When present, it MUST contain a non-empty `stateSurfaces` array. Each state surface SHOULD include a human-readable `name`, a `classification`, and enough ownership and storage detail for implementation agents or gates to determine whether the declared system of record is appropriate.

Recognized `classification` values are:

| Value | Meaning |
|-------|---------|
| `durable_product_state` | Authoritative product or application state. |
| `auth_session_state` | Identity, authentication, session, or security state. |
| `authorization_state` | Roles, memberships, grants, permissions, or ownership state. |
| `audit_event_state` | Append-only or traceable audit, history, or compliance state. |
| `external_integration_state` | State owned by, synchronized with, or delegated to an external provider. |
| `canonical_artifact` | Source-controlled or user-authored artifact read as evidence, not mutable application persistence. |
| `cache` | Rebuildable, non-authoritative derived state with invalidation rules. |
| `projection` | Derived read model whose source of truth is another state surface. |
| `import_export_artifact` | Temporary transfer artifact, not live application state. |
| `dev_only_fixture` | Test or local-only data excluded from production runtime. |
| `ephemeral_ui_state` | Temporary view state safe to keep in browser or process memory. |

System-of-record records may also include `referenceApplications` when the plan is carrying behavior forward from another application. Each reference application entry SHOULD identify evidence, behavior that must be preserved, and behavior intentionally not carried forward.

**Example:**

```json
{
  "architecture": {
    "systemOfRecord": {
      "stateSurfaces": [
        {
          "name": "Workspace",
          "classification": "durable_product_state",
          "owner": "application database",
          "approvedStorage": "postgres",
          "permissionBoundary": "workspace membership"
        }
      ],
      "referenceApplications": []
    }
  }
}
```

---

## 4. PlanItem Object

A PlanItem represents a single actionable item within a plan.

### 4.1 Required Fields

| Field | Type | Requirement | Description |
|-------|------|-------------|-------------|
| `title` | string | REQUIRED | Human-readable item title. |
| `status` | string | REQUIRED | Current item status. MUST be a valid Status enum value (see [Section 5](#5-status-enum)). |

### 4.2 Optional Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Stable semantic identifier (see [Section 4.3](#43-hierarchical-ids)). |
| `uid` | string | Globally unique identifier. |
| `narrative` | object | Item-level narrative (same structure as plan narratives). |
| `items` | array | Nested array of PlanItem objects. Preferred in v0.6 for hierarchical plans. |
| `subItems` | array | Deprecated legacy alias for `items`. Readers SHOULD accept it for compatibility. |
| `planRef` | string | URI referencing an external plan (see [Section 4.4](#44-plan-references-planref)). |
| `tags` | array of strings | Categorization tags. |
| `metadata` | object | Arbitrary key-value metadata. |
| `created` | string (ISO 8601) | Item creation timestamp. |
| `updated` | string (ISO 8601) | Item last-modified timestamp. |
| `completed` | string (ISO 8601) | Completion timestamp. |
| `priority` | string | Priority level (e.g., `"high"`, `"medium"`, `"low"`). |
| `dueDate` | string (ISO 8601) | Due date. |
| `startDate` | string (ISO 8601) | Planned start date. |
| `endDate` | string (ISO 8601) | Planned end date. |
| `percentComplete` | number | Completion percentage (0–100). |
| `participants` | array of strings | Participant identifiers. |
| `location` | string | Location context. |
| `uris` | array of strings | Related URIs. |
| `recurrence` | object | Recurrence rules. |
| `reminders` | array | Reminder configurations. |
| `classification` | string | Security or sensitivity classification. |
| `relatedComments` | array | Associated comments or discussion. |
| `timezone` | string | IANA timezone identifier. |
| `sequence` | integer | Revision counter. |
| `lastModifiedBy` | string | Identifier of last modifier. |
| `lockedBy` | string | Lock holder identifier. |

### 4.2.1 Nested Items Compatibility

xBRIEF v0.6 standardizes nested PlanItem collections on the `items` field. Implementations SHOULD emit `items` when writing v0.6 documents.

The legacy `subItems` field remains valid for compatibility with v0.5 tooling. Readers SHOULD accept either `items` or `subItems`. If both are present on the same PlanItem, implementations SHOULD treat `items` as canonical and MAY warn or reject the document if the two arrays diverge.

### 4.3 Hierarchical IDs

When the `id` field is present on a PlanItem:

1. IDs MUST be user-assigned, stable, semantic strings. Implementations MUST NOT auto-generate IDs unless explicitly requested.
2. Parent-child relationships MUST use dot notation. For example, an item `"auth"` nested under `"setup"` MUST have the ID `"setup.auth"`.
3. IDs MUST be unique within the scope of a single Plan. Duplicate IDs within one Plan constitute a validation error.

**Example:**

```json
{
  "id": "setup",
  "title": "Project Setup",
  "items": [
    { "id": "setup.auth", "title": "Authentication" },
    { "id": "setup.auth.oauth", "title": "OAuth Integration" }
  ]
}
```

### 4.4 Plan References (planRef)

The `planRef` field contains a URI string referencing another plan or a specific item within a plan. The following URI schemes MUST be supported:

| Syntax | Meaning | Example |
|--------|---------|---------|
| `#<item-id>` | Internal reference within the same plan | `"#setup.auth"` |
| `file://<path>` | Local file reference | `"file://./backend-plan.xbrief.json"` |
| `https://<url>` | Remote URL reference | `"https://example.com/plan.xbrief.json"` |

Fragment syntax (`#`) MAY be appended to `file://` and `https://` URIs to reference a specific item within the target plan. For example: `"file://./plan.xbrief.json#setup.auth"`.

Implementations MUST parse `planRef` URIs correctly. Implementations MAY defer resolution of referenced plans (lazy loading).

---

## 5. Status Enum

### 5.1 Values

Plans and PlanItems share a single universal Status enum. All status values MUST be one of:

| Value | Description |
|-------|-------------|
| `draft` | Initial creation; not yet actionable. |
| `proposed` | Submitted for review or approval. |
| `approved` | Reviewed and approved; ready to begin. |
| `pending` | Queued for execution. |
| `running` | Actively in progress. |
| `completed` | Successfully finished. |
| `blocked` | Cannot proceed due to an impediment but may resume later. |
| `failed` | Ended unsuccessfully due to an unrecoverable error or exhausted retries. |
| `cancelled` | Abandoned intentionally; will not be completed. |

Implementations MUST reject documents containing status values not in this enum, or MUST emit a validation warning.

### 5.2 Lifecycle

The following state transitions represent the RECOMMENDED lifecycle:

```
draft → proposed → approved → pending → running → completed
                                           → blocked → running
                                           → failed
                                           → cancelled
draft → running (quick start)
pending → running → failed
```

Implementations are NOT REQUIRED to enforce transition order. Any status value MAY be assigned directly. The lifecycle diagram is provided as guidance for typical usage patterns.

---

## 6. DAG (Directed Acyclic Graph) Support

The optional `edges` array on the Plan object defines dependency relationships between items, forming a directed acyclic graph.

### 6.1 Edge Object

| Field | Type | Requirement | Description |
|-------|------|-------------|-------------|
| `from` | string | REQUIRED | Source item ID. MUST reference an existing item ID within the plan. |
| `to` | string | REQUIRED | Target item ID. MUST reference an existing item ID within the plan. |
| `type` | string | REQUIRED | Edge type. MUST be one of the core types or a custom string. |

### 6.2 Core Edge Types

Implementations MUST support the following core edge types:

| Type | Semantics |
|------|-----------|
| `blocks` | The target item MUST NOT start until the source item is completed. This is a hard dependency. |
| `informs` | The target item benefits from the source item's context or output. This is NOT a blocking relationship. |
| `invalidates` | Completion of the source item makes the target item unnecessary. Implementations SHOULD mark invalidated items for review. |
| `suggests` | The source item weakly recommends the target item. There is no hard or soft dependency. |

### 6.3 Edge Type Extensibility

Custom edge type strings are permitted beyond the four core types. Implementations MUST support all core types as defined in [Section 6.2](#62-core-edge-types). Implementations SHOULD ignore unknown edge types gracefully (i.e., preserve them without enforcing semantics).

### 6.4 Graph Constraints

1. The set of edges MUST form a valid DAG. Cycles are prohibited. An edge set containing a cycle constitutes a validation error.
2. The `from` and `to` fields of every edge MUST resolve to existing item IDs within the plan. Dangling references constitute a validation error.
3. Implementations MUST validate DAG constraints when edges are present and MUST report violations as errors.

---

## 7. TRON Encoding

### 7.1 Overview

TRON (Token-Reduced Object Notation) is an alternative serialization of xBRIEF documents optimized for LLM context windows. TRON achieves approximately 35–40% token reduction compared to equivalent JSON by using positional class constructors and omitting redundant syntax.

See [tron-encoding.md](tron-encoding.md) for the complete TRON format specification.

### 7.2 Class Definitions

TRON documents begin with class definitions that map positional arguments to field names:

```tron
class Edge: from, to, type
class PlanItem: id, title, status
```

Objects are then instantiated positionally:

```tron
Edge("lint", "build", "blocks")
PlanItem("setup", "Project Setup", "running")
```

The Plan object itself is represented as a standard key-value block, with `items` and `edges` arrays using the defined classes.

### 7.3 Conformance

1. A TRON document MUST be semantically equivalent to its JSON representation. No information MAY be added or lost during encoding.
2. Round-trip conversion (TRON → JSON → TRON) MUST preserve all data.
3. Implementations that support TRON MUST also support JSON. JSON is the canonical serialization; TRON is an optimization.

---

## 8. Conformance

### 8.1 Conformance Criteria

A document is xBRIEF v0.6 conformant if and only if:

1. The root object contains a `xBRIEFInfo` field with `version` equal to `"0.6"`.
2. The root object contains exactly one `plan` field.
3. The `plan` object contains the REQUIRED fields: `title` (string), `status` (valid Status enum value), and `items` (array).
4. All `status` values on the Plan and every PlanItem are valid Status enum values as defined in [Section 5.1](#51-values).
5. If `items` or `subItems` are present on a PlanItem, every nested entry is a valid PlanItem.
6. If `edges` are present, they form a valid DAG with no cycles.
7. If hierarchical IDs are used, they follow dot notation as defined in [Section 4.3](#43-hierarchical-ids).
8. Core edge types (`blocks`, `informs`, `invalidates`, `suggests`) are semantically supported.
9. Unknown fields at any level are preserved.
10. `planRef` URIs follow the syntax defined in [Section 4.4](#44-plan-references-planref).
11. Narrative keys SHOULD use TitleCase convention.

### 8.2 Implementation Requirements

1. Implementations MUST preserve unknown fields when reading and writing xBRIEF documents.
2. Implementations MUST validate that all REQUIRED fields are present.
3. Implementations SHOULD accept either `items` or `subItems` when reading nested PlanItem hierarchies.
4. Implementations SHOULD emit `items` when writing v0.6 documents and MAY emit `subItems` only for backward compatibility.
5. Implementations SHOULD validate DAG constraints when edges are present.
6. Implementations MAY provide auto-correction for common issues (e.g., normalizing status casing) but MUST NOT silently drop data.

---

## 9. Security Considerations

1. **No executable code.** xBRIEF documents MUST NOT contain executable code. Implementations MUST NOT evaluate any field value as code.
2. **URI validation.** Implementations SHOULD validate `planRef` and `uris` values before dereferencing. Remote URIs (`https://`) introduce network dependencies and potential security risks; implementations SHOULD warn users before fetching remote references.
3. **Document size.** Implementations SHOULD enforce reasonable limits on document size to prevent denial-of-service through excessively large documents. A RECOMMENDED maximum is 10 MB for a single document.
4. **Sensitive data.** The `classification` field on PlanItem MAY be used to indicate sensitivity. Implementations SHOULD respect classification values when displaying or transmitting documents.

---

## 10. References

- **[RFC 2119]** Bradner, S., "Key words for use in RFCs to Indicate Requirement Levels", BCP 14, RFC 2119, March 1997.
- **[xBRIEF TRON Encoding Guide]** — [tron-encoding.md](tron-encoding.md)
- **[xBRIEF User Guide]** — [GUIDE.md](GUIDE.md)
- **[xBRIEF JSON Schema]** — [../schemas/xbrief-core-0.6.schema.json](../schemas/xbrief-core-0.6.schema.json)

[rfc2119]: https://www.rfc-editor.org/rfc/rfc2119

---

## Appendix A: JSON Schema Reference

The normative JSON Schema for xBRIEF v0.6 is located at [`schemas/xbrief-core-0.6.schema.json`](../schemas/xbrief-core-0.6.schema.json).

Implementations SHOULD use this schema for validation. The schema defines all REQUIRED fields, enum constraints, and structural rules specified in this document.

---

## Appendix B: Complete Examples

The following examples demonstrate graduated complexity. Each is available in both JSON and TRON format in the [`examples/`](../examples/) directory.

### B.1 Minimal Plan

**JSON** ([`examples/minimal-plan.xbrief.json`](../examples/minimal-plan.xbrief.json)):

```json
{
  "xBRIEFInfo": { "version": "0.6" },
  "plan": {
    "title": "Daily Tasks",
    "status": "running",
    "items": [
      { "title": "Fix authentication bug", "status": "pending" },
      { "title": "Review PR #123", "status": "running" }
    ]
  }
}
```

### B.2 Structured Plan with Narratives

**JSON** ([`examples/structured-plan.xbrief.json`](../examples/structured-plan.xbrief.json)):

```json
{
  "xBRIEFInfo": { "version": "0.6" },
  "plan": {
    "id": "api-migration",
    "title": "API Migration to GraphQL",
    "status": "proposed",
    "narratives": {
      "Proposal": "Migrate REST API to GraphQL for better developer experience.",
      "Problem": "50+ REST endpoints with inconsistent patterns, overfetching.",
      "Risk": "Team learning curve, N+1 query optimization."
    },
    "items": [
      { "id": "research", "title": "Research & POC", "status": "completed" },
      { "id": "schema", "title": "Define GraphQL Schema", "status": "running" },
      { "id": "resolvers", "title": "Implement Resolvers", "status": "pending" }
    ]
  }
}
```

### B.3 Retrospective Plan

See [`examples/retrospective-plan.xbrief.json`](../examples/retrospective-plan.xbrief.json) for a full incident postmortem

### B.4 DAG Plan

**JSON** ([`examples/dag-plan.xbrief.json`](../examples/dag-plan.xbrief.json)):

```json
{
  "xBRIEFInfo": { "version": "0.6" },
  "plan": {
    "id": "ci-pipeline",
    "title": "CI Pipeline",
    "status": "running",
    "items": [
      { "id": "lint", "title": "Lint", "status": "completed" },
      { "id": "test", "title": "Test", "status": "running" },
      { "id": "build", "title": "Build", "status": "pending" },
      { "id": "deploy", "title": "Deploy", "status": "pending" }
    ],
    "edges": [
      { "from": "lint", "to": "build", "type": "blocks" },
      { "from": "test", "to": "build", "type": "blocks" },
      { "from": "build", "to": "deploy", "type": "blocks" },
      { "from": "lint", "to": "test", "type": "informs" }
    ]
  }
}
```

**TRON** ([`examples/dag-plan.xbrief.tron`](../examples/dag-plan.xbrief.tron)):

```tron
class Edge: from, to, type
class PlanItem: id, title, status

xBRIEFInfo: { version: "0.6" }
plan: {
  id: "ci-pipeline",
  title: "CI Pipeline",
  status: "running",
  items: [
    PlanItem("lint", "Lint", "completed"),
    PlanItem("test", "Test", "running"),
    PlanItem("build", "Build", "pending"),
    PlanItem("deploy", "Deploy", "pending")
  ],
  edges: [
    Edge("lint", "build", "blocks"),
    Edge("test", "build", "blocks"),
    Edge("build", "deploy", "blocks"),
    Edge("lint", "test", "informs")
  ]
}
```
