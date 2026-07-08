# libxbrief-ts
> **Source**: [`xbrief/specification-libxbrief-ts.xbrief.json`](xbrief/specification-libxbrief-ts.xbrief.json) — `status: approved`

## Overview
`libxbrief-ts` is an idiomatic TypeScript port of the local Python `libxbrief` library. It MUST provide full public-API parity with the Python implementation while remaining idiomatic for modern TypeScript consumers.

The library MUST target ESM-only packaging, support Node.js, Bun, Deno, and browsers, and preserve xBRIEF's extension-friendly design by allowing unknown fields to survive parse → model → serialize round-trips. The core package MUST stay universal and runtime-agnostic; file I/O MUST live in a separate Node-oriented entrypoint.

The port SHOULD optimize for three use cases:
- universal parsing, validation, and serialization of xBRIEF v0.5 documents
- use inside modern TypeScript applications and agent runtimes
- cross-language compatibility with Python `libxbrief`

## Requirements
### Functional Requirements
- **FR-1**: The library MUST expose typed `PlanItem`, `Plan`, and `XBriefDocument` model APIs with TypeScript types derived from Zod schemas.
- **FR-2**: Zod schemas MUST preserve unknown fields via passthrough behavior so extension fields survive round-trips.
- **FR-3**: The library MUST provide JSON helpers equivalent to Python `loads`, `dumps`, and MUST provide `loadFile` / `dumpFile` in a separate Node entrypoint.
- **FR-4**: The library MUST implement structural validation equivalent to Python `validate()`, including version, required field, status, ID, duplicate-ID, and `planRef` checks with stable issue codes and paths.
- **FR-5**: The library MUST implement DAG validation equivalent to Python `validate(dag=True)`, including malformed edge detection, dangling edge references, and cycle detection.
- **FR-6**: The library MUST provide full Builder API parity: `PlanBuilder`, `ItemBuilder`, `quickTodo`, `fromItems`, slug generation, strict/non-strict validation behavior, and `PlanItem` status factories.
- **FR-7**: The library MUST export compatibility constants equivalent to the Python compat layer, including `VALID_STATUSES`, regex patterns, and issue code constants.
- **FR-8**: The TypeScript implementation MUST round-trip compatibly with the Python implementation for xBRIEF v0.5 documents and shipped examples.

### Non-Functional Requirements
- **NFR-1**: The implementation MUST use modern TypeScript with Vitest-based automated tests and MUST maintain at least 85% coverage on measurable code.
- **NFR-2**: The package MUST be ESM-only.
- **NFR-3**: The core entrypoint MUST remain universal and MUST NOT depend on Node-specific APIs; Node file I/O MUST be isolated to a separate entrypoint.
- **NFR-4**: The implementation SHOULD remain lightweight and local-package-first; npm publishing is explicitly out of scope for this phase.

## Architecture
### Package layout
The TypeScript port will live in `libxbrief-ts/` within this repository so it can share examples, schema references, and cross-language compatibility tests with the Python implementation.

Proposed structure:
- `libxbrief-ts/src/index.ts` — universal public API
- `libxbrief-ts/src/node.ts` — Node/Bun/Deno file I/O helpers
- `libxbrief-ts/src/schemas.ts` — Zod schemas and inferred types
- `libxbrief-ts/src/models.ts` — model wrappers / helpers
- `libxbrief-ts/src/validation.ts` — validation and DAG logic
- `libxbrief-ts/src/builder.ts` — Builder API
- `libxbrief-ts/src/compat.ts` — statuses, patterns, issue codes
- `libxbrief-ts/tests/` — Vitest suite

### Design decisions
- **ESM-only** keeps packaging simple and aligns with the chosen runtime targets.
- **Zod** provides a single source of truth for runtime parsing and compile-time inference.
- **Universal core + Node entrypoint split** keeps browser/edge compatibility without giving up file I/O parity.
- **Full Python parity** avoids a “partial port” trap and makes `libxbrief-ts` useful for Deft/AgentOS-adjacent consumers immediately.

### Unknown-field strategy
Known fields MUST be represented explicitly in schemas and types. Unknown fields MUST be preserved and surfaced through passthrough parsing and serialization so documents with extension fields such as `type`, `kind`, or future profile-specific fields are not lossy.

## Implementation Plan
### Phase 1: Foundation
Establish the TypeScript package, schema layer, and compatibility constants.

#### Subphase 1.1: Scaffolding
- **Task 1.1.1** — Create `libxbrief-ts/` package scaffolding
  - Dependencies: none
  - Acceptance: `package.json`, `tsconfig.json`, `vitest.config.ts`, `.gitignore`, and baseline source/test directories exist; `npm test` or equivalent succeeds with a smoke test
  - Traces: NFR-1, NFR-2

#### Subphase 1.2: Schema & compatibility core *(depends on: 1.1)*
- **Task 1.2.1** — Define Zod schemas for `PlanItem`, `Plan`, and `XBriefDocument`
  - Dependencies: 1.1.1
  - Acceptance: valid v0.5 documents parse; passthrough preserves unknown fields
  - Traces: FR-1, FR-2
- **Task 1.2.2** — Export TypeScript types inferred from the schemas
  - Dependencies: 1.2.1
  - Acceptance: model types are publicly exported; known fields are strongly typed
  - Traces: FR-1
- **Task 1.2.3** — Port Python compat constants
  - Dependencies: 1.1.1
  - Acceptance: `VALID_STATUSES`, hierarchical ID regex, planRef regex, and issue code constants are available in TS
  - Traces: FR-7

### Phase 2: Core parsing, serialization, and validation *(depends on: Phase 1)*
Implement universal JSON helpers, Node file I/O, and validation parity.

#### Subphase 2.1: Serialization & public helpers *(depends on: 1.2)*
- **Task 2.1.1** — Implement canonical and preserve-format JSON serialization
  - Dependencies: 1.2.2
  - Acceptance: canonical output sorts keys deterministically; preserve-format retains original key ordering where available
  - Traces: FR-3
- **Task 2.1.2** — Implement `loads` and `dumps`
  - Dependencies: 2.1.1
  - Acceptance: `loads`/`dumps` round-trip valid documents and preserve extension fields
  - Traces: FR-3
- **Task 2.1.3** — Implement universal `validate()`
  - Dependencies: 1.2.2, 1.2.3
  - Acceptance: returns structured validation issues matching Python behavior and codes
  - Traces: FR-4

#### Subphase 2.2: Node entrypoint *(depends on: 2.1)*
- **Task 2.2.1** — Implement `loadFile` / `dumpFile` in `src/node.ts`
  - Dependencies: 2.1.2
  - Acceptance: file I/O works in Node-compatible runtimes; core entrypoint remains free of Node APIs
  - Traces: FR-3, NFR-3

#### Subphase 2.3: Validation parity *(depends on: 1.2 and 2.1)*
- **Task 2.3.1** — Port structural validation rules
  - Dependencies: 1.2.3, 2.1.3
  - Acceptance: version, missing field, status, ID format, duplicate ID, and `planRef` checks match Python issue codes and paths
  - Traces: FR-4, FR-7
- **Task 2.3.2** — Implement DAG edge validation
  - Dependencies: 2.3.1
  - Acceptance: malformed edges and dangling references are reported correctly
  - Traces: FR-5
- **Task 2.3.3** — Implement DAG cycle detection
  - Dependencies: 2.3.2
  - Acceptance: cyclic graphs produce `dag_cycle`; acyclic graphs validate cleanly
  - Traces: FR-5

### Phase 3: Builder API parity *(depends on: Phase 2)*
Port the ergonomic construction API from Python.

#### Subphase 3.1: Builder primitives *(depends on: 2.1 and 2.3)*
- **Task 3.1.1** — Implement `_slugify` equivalent
  - Dependencies: 2.1.2
  - Acceptance: behavior matches Python slug generation exactly, including fallback behavior
  - Traces: FR-6
- **Task 3.1.2** — Implement `ItemBuilder`
  - Dependencies: 3.1.1, 2.3.1
  - Acceptance: supports nested subitems, item narratives, strict/non-strict ID validation, and dot-notation child IDs
  - Traces: FR-6

#### Subphase 3.2: Plan construction *(depends on: 3.1)*
- **Task 3.2.1** — Implement `PlanBuilder`
  - Dependencies: 3.1.2, 2.3.2
  - Acceptance: supports plan narratives, items, edges, strict/non-strict validation, and document generation
  - Traces: FR-6
- **Task 3.2.2** — Implement `quickTodo` and `fromItems`
  - Dependencies: 3.2.1
  - Acceptance: helpers mirror Python coercion and non-mutation behavior
  - Traces: FR-6
- **Task 3.2.3** — Implement `PlanItem` status factories
  - Dependencies: 1.2.2
  - Acceptance: `pending`, `running`, `completed`, `blocked`, `cancelled`, and `draft` constructors are exposed and behave like Python
  - Traces: FR-6

### Phase 4: Cross-language verification and project integration *(depends on: Phase 3)*
Verify parity, ship shared examples, and wire repeatable tasks into the repo workflow.

#### Subphase 4.1: Compatibility and fixtures *(depends on: 2.3 and 3.2)*
- **Task 4.1.1** — Add cross-language round-trip tests
  - Dependencies: 2.1.2, 3.2.3
  - Acceptance: Python-generated JSON loads in TypeScript and vice versa with field equality
  - Traces: FR-8
- **Task 4.1.2** — Validate all example fixture files in the TS suite
  - Dependencies: 2.3.3
  - Acceptance: `examples/*.xbrief.json` pass TypeScript validation
  - Traces: FR-4, FR-8

#### Subphase 4.2: Workflow integration *(depends on: 4.1)*
- **Task 4.2.1** — Add Taskfile targets for TypeScript workflows
  - Dependencies: 4.1.1, 4.1.2
  - Acceptance: `task ts:test`, `task ts:lint`, and `task ts:build` exist and run cleanly
  - Traces: NFR-1

## Testing Strategy
- The TypeScript package MUST use Vitest.
- Coverage MUST be at least 85% on measurable code.
- Tests MUST be split across:
  - **unit tests** for schemas, constants, validation primitives, slug generation, builders, and factories
  - **fixture/integration tests** using the shared `examples/*.xbrief.json` documents
  - **cross-language compatibility tests** validating Python ↔ TypeScript parity
  - **round-trip tests** ensuring unknown fields and ordering behavior are preserved
  - **DAG-specific tests** for malformed edges, dangling references, and cycles
- The package SHOULD include fuzz/property-style tests for random valid/invalid documents where practical.
- No phase is complete until its corresponding tests pass.

## Deployment
This phase explicitly targets a **local package only**. npm publishing is out of scope.

The package MUST be consumable from the repo as a subdirectory package and SHOULD be ready for later publication if desired, but no registry publishing workflow will be added in this spec.
