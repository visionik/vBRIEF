# libxbrief.py Specification v1

**Version**: 1.0.0-draft
**Status**: Draft for Implementation
**Date**: 2026-02-23
**Author**: Generated from PRD interview

## Overview

`libxbrief.py` is a Python library for reading, writing, and validating xBRIEF v0.5 JSON documents.

This v1 release focuses on a practical core:
- Read/write current v0.5 **Plan JSON** documents
- Provide both **dict-style API** and **class-style API**
- Use **lenient parsing** with explicit validation
- Preserve unknown fields for safe round-tripping

## Scope

### In Scope (v1)

1. Parse and emit v0.5 JSON documents with root `xBRIEFInfo` and `plan`
2. Provide functional API and dataclass object model
3. Validate core structural and conformance rules (non-DAG)
4. Preserve unknown fields at root, plan, and item levels
5. Canonical writer with optional preserve mode
6. Package as local/dev-installable Python package (no PyPI release yet)

### Out of Scope (v1)

1. Legacy format support (`todoList`, `playbook`, root `vSpec`, v0.4 migration)
2. TRON parsing/serialization (planned later via `libtronpy`)
3. CLI commands
4. DAG cycle/reference validation
5. Network fetching, remote schema resolution, or hosted services

## Requirements

### Functional Requirements

#### Document IO

1. The library MUST load documents from file paths and strings.
2. The library MUST dump documents to file paths and strings.
3. File IO MUST use UTF-8.
4. The writer MUST support canonical JSON output.
5. The writer MAY support preserve-mode formatting and key-order behavior.

#### API Surface

1. The library MUST provide dict-first helpers:
   - `load_file(path, *, strict=False)`
   - `loads(text, *, strict=False)`
   - `dump_file(doc, path, *, canonical=True, preserve_format=False)`
   - `dumps(doc, *, canonical=True, preserve_format=False)`
   - `validate(doc)`
2. The library MUST provide class-first model types:
   - `XBriefDocument`
   - `Plan`
   - `PlanItem`
3. The class model MUST provide constructors/from-helpers and serialization methods.
4. Both APIs MUST be interoperable without data loss for supported fields and preserved unknown fields.

#### Validation Behavior

1. Parsing/loading MUST be lenient by default.
2. Validation MUST be explicit via `validate()`.
3. Strict mode MAY be exposed via `strict=True` on load/helpers and MUST raise on validation errors.
4. Validation MUST return structured issues in non-strict mode.
5. Validation MUST check:
   - Required root fields (`xBRIEFInfo`, `plan`)
   - Version exactness (`xBRIEFInfo.version == "0.5"`)
   - Required plan fields (`title`, `status`, `items`)
   - Status enum validity
   - Hierarchical ID format where `id` appears
   - `planRef` URI pattern support (`#...`, `file://...`, `https://...`)
6. Validation MUST NOT include DAG cycle/reference checks in v1.

#### Unknown Field Preservation

1. Unknown fields MUST be preserved at every level.
2. Round-trip (`load -> dump`) MUST NOT drop unknown keys.
3. Unknown fields MUST be accessible in class mode (for example via extension maps/extra fields).

#### Error Model

1. Validation MUST return a structured report object.
2. Each issue MUST include:
   - `code` (stable machine-readable code)
   - `path` (JSONPath-like location)
   - `message`
   - `severity` (`error` or `warning`)
3. The report MUST include separate `errors` and `warnings` collections.

### Non-Functional Requirements

1. Python support MUST be `>=3.10`.
2. The library SHOULD have deterministic canonical output for stable diffs.
3. The library SHOULD avoid heavyweight runtime dependencies.
4. Public API changes before v1.0.0 final SHOULD be minimized.
5. Unit test coverage SHOULD target >=85% for library modules.

## Architecture

### Package Layout

The implementation MUST use a layered package layout:

```text
libxbrief/
  __init__.py
  io.py
  models.py
  validation.py
  errors.py
  issues.py
  types.py
  serialization/
    __init__.py
    json_codec.py
  compat/
    __init__.py
    policy.py
```

### Module Responsibilities

1. `models.py`
   - Dataclasses: `XBriefDocument`, `Plan`, `PlanItem`
   - Extension/unknown-field storage
2. `io.py`
   - File/string entry points
   - High-level load/dump orchestration
3. `validation.py`
   - Core rule checks
   - Structured issue generation
4. `issues.py` + `errors.py`
   - Issue/report classes
   - Strict-mode exceptions
5. `serialization/json_codec.py`
   - JSON parse/emit
   - Canonical formatting and preserve mode hooks
6. `compat/policy.py`
   - Compatibility constants and policy toggles for future extensions

### Data Model Contracts

#### `XBriefDocument`

Required fields:
- `xbrief_info: dict`
- `plan: Plan`

Optional/internal:
- `extras: dict[str, object]` for unknown root-level fields

#### `Plan`

Required fields:
- `title: str`
- `status: str`
- `items: list[PlanItem]`

Optional known fields:
- `id`, `uid`, `narratives`, `edges`, `tags`, `metadata`, `created`, `updated`, `author`, `reviewers`, `uris`, `references`, `timezone`, `agent`, `lastModifiedBy`, `changeLog`, `sequence`, `fork`

Unknown fields:
- preserved in plan-level extras

#### `PlanItem`

Required fields:
- `title: str`
- `status: str`

Optional known fields:
- `id`, `uid`, `narrative`, `subItems`, `planRef`, `tags`, `metadata`, `created`, `updated`, `completed`, `priority`, `dueDate`, `startDate`, `endDate`, `percentComplete`, `participants`, `location`, `uris`, `recurrence`, `reminders`, `classification`, `relatedComments`, `timezone`, `sequence`, `lastModifiedBy`, `lockedBy`

Unknown fields:
- preserved in item-level extras

### Serialization Rules

#### Canonical Mode (`canonical=True`)

1. Output MUST be UTF-8 JSON text.
2. Indentation MUST be 2 spaces.
3. A trailing newline MUST be included.
4. Key ordering MUST be deterministic.

#### Preserve Mode (`preserve_format=True`)

1. Writer SHOULD preserve input ordering/shape when possible.
2. If preservation metadata is unavailable, writer MUST fall back to canonical mode.

## Component Interfaces

### Dict API

```python
from libxbrief import load_file, loads, dump_file, dumps, validate
```

Behavior:
1. `load_file` / `loads` return plain dict documents.
2. `dump_file` / `dumps` accept dict documents.
3. `validate` accepts dict or model objects and returns a report.
4. `strict=True` MUST raise validation exception on errors.

### Class API

```python
from libxbrief import XBriefDocument, Plan, PlanItem
```

Behavior:
1. `XBriefDocument.from_file(path, *, strict=False)`
2. `XBriefDocument.from_json(text, *, strict=False)`
3. `obj.to_dict()` / `obj.to_json(...)` / `obj.to_file(...)`
4. `obj.validate()` returns structured report; strict path raises.

## Implementation Plan

### Phase 1: Package Foundation (depends on: None)

**Goal**: Establish package skeleton, typing baseline, and shared contracts.

#### Subphase 1.1: Repository Setup (depends on: None)

- Task 1.1.1: Create layered package structure
  - Dependencies: None
  - Acceptance: Package modules and init files exist per architecture
- Task 1.1.2: Add `pyproject.toml` for Python 3.10+
  - Dependencies: None
  - Acceptance: Editable install works
- Task 1.1.3: Add baseline test scaffolding
  - Dependencies: Task 1.1.1
  - Acceptance: Test runner executes empty suite successfully

**Subphase 1.1 Testing (MUST pass before next subphase)**:
- Import smoke tests for package modules
- Editable install test (`pip install -e .`)

#### Subphase 1.2: Shared Types and Issue Contracts (depends on: 1.1)

- Task 1.2.1: Implement issue/report dataclasses
  - Dependencies: Task 1.1.1
  - Acceptance: `Issue`, `ValidationReport` types with required fields
- Task 1.2.2: Implement strict-mode exception hierarchy
  - Dependencies: Task 1.2.1
  - Acceptance: Validation exceptions include report context
- Task 1.2.3: Add stable issue code registry
  - Dependencies: Task 1.2.1
  - Acceptance: Documented code constants used by validator

**Subphase 1.2 Testing (MUST pass before Phase 2)**:
- Unit tests for report serialization and exception behavior

### Phase 2: Core Models and Serialization (depends on: Phase 1)

**Goal**: Build dataclass model and JSON codec with unknown-field preservation.

#### Subphase 2.1: Dataclass Models (depends on: 1.2)

- Task 2.1.1: Implement `PlanItem` dataclass + extras handling
  - Dependencies: Phase 1 complete
  - Acceptance: Known and unknown fields round-trip in-memory
- Task 2.1.2: Implement `Plan` dataclass + nested items support
  - Dependencies: Task 2.1.1
  - Acceptance: Nested item trees parse/serialize correctly
- Task 2.1.3: Implement `XBriefDocument` dataclass
  - Dependencies: Task 2.1.2
  - Acceptance: Root + plan + extras represented losslessly

**Subphase 2.1 Testing (MUST pass before next subphase)**:
- Model construction tests
- Unknown-field preservation tests at all levels

#### Subphase 2.2: JSON Codec (depends on: 2.1)

- Task 2.2.1: Implement dict <-> model conversion
  - Dependencies: Task 2.1.3
  - Acceptance: Round-trip equality for known+unknown fields
- Task 2.2.2: Implement canonical JSON writer
  - Dependencies: Task 2.2.1
  - Acceptance: Deterministic output formatting and key order
- Task 2.2.3: Implement preserve-format mode fallback policy
  - Dependencies: Task 2.2.2
  - Acceptance: Preserve attempt or canonical fallback works predictably

**Subphase 2.2 Testing (MUST pass before Phase 3)**:
- Snapshot tests for canonical output
- Preserve-mode behavior tests

### Phase 3: Validation Engine (depends on: Phase 2)

**Goal**: Implement explicit conformance validation with structured issues.

#### Subphase 3.1: Rule Validators (depends on: 2.2)

- Task 3.1.1: Required field and version checks
  - Dependencies: Phase 2 complete
  - Acceptance: Missing/invalid root-plan fields produce stable error codes
- Task 3.1.2: Status enum validation (plan and item recursion)
  - Dependencies: Task 3.1.1
  - Acceptance: Invalid statuses produce path-aware issues
- Task 3.1.3: ID and `planRef` URI checks
  - Dependencies: Task 3.1.1
  - Acceptance: Pattern violations produce path-aware issues

**Subphase 3.1 Testing (MUST pass before next subphase)**:
- Parametric tests for each rule
- Recursive nested-item validation tests

#### Subphase 3.2: Report and Strict Mode Integration (depends on: 3.1)

- Task 3.2.1: Aggregate issues into report object
  - Dependencies: Task 3.1.3
  - Acceptance: Report separates errors/warnings deterministically
- Task 3.2.2: Wire strict mode to raise exceptions
  - Dependencies: Task 3.2.1
  - Acceptance: `strict=True` load paths raise on errors
- Task 3.2.3: Ensure DAG checks are excluded in v1
  - Dependencies: Task 3.2.1
  - Acceptance: Validator does not perform cycle/reference checks

**Subphase 3.2 Testing (MUST pass before Phase 4)**:
- Strict vs lenient behavior tests
- Golden tests for issue codes and paths

### Phase 4: Public APIs (depends on: Phase 3)

**Goal**: Expose stable dict and class interfaces.

#### Subphase 4.1: Dict API (depends on: 3.2)

- Task 4.1.1: Implement `load_file` and `loads`
  - Dependencies: Phase 3 complete
  - Acceptance: Functional API loads valid and invalid docs in lenient mode
- Task 4.1.2: Implement `dump_file` and `dumps`
  - Dependencies: Task 4.1.1
  - Acceptance: Canonical and preserve modes available
- Task 4.1.3: Implement top-level `validate`
  - Dependencies: Task 4.1.1
  - Acceptance: Returns `ValidationReport` for dict/model inputs

**Subphase 4.1 Testing (MUST pass before next subphase)**:
- Functional API contract tests
- File IO error handling tests

#### Subphase 4.2: Class API (depends on: 3.2, can run in parallel with 4.1)

- Task 4.2.1: Implement class constructors/from helpers
  - Dependencies: Phase 3 complete
  - Acceptance: `from_file`/`from_json` available and tested
- Task 4.2.2: Implement class serialization helpers
  - Dependencies: Task 4.2.1
  - Acceptance: `to_dict`/`to_json`/`to_file` available
- Task 4.2.3: Implement class `validate`
  - Dependencies: Task 4.2.1
  - Acceptance: Matches dict API behavior and report shape

**Subphase 4.2 Testing (MUST pass before Phase 5)**:
- Class API parity tests vs dict API
- Round-trip tests through both API surfaces

### Phase 5: Documentation and Local Release (depends on: Phase 4)

**Goal**: Ship a developer-ready local package with clear docs.

#### Subphase 5.1: Documentation (depends on: 4.1 and 4.2)

- Task 5.1.1: Write README with quick-start for both APIs
  - Dependencies: Phase 4 complete
  - Acceptance: Copy-paste examples run in tests/docs checks
- Task 5.1.2: Write validation/error reference
  - Dependencies: Task 5.1.1
  - Acceptance: All issue codes documented
- Task 5.1.3: Write scope statement for deferred TRON support
  - Dependencies: Task 5.1.1
  - Acceptance: Explicit note: TRON deferred to future `libtronpy` integration

**Subphase 5.1 Testing (MUST pass before next subphase)**:
- Doctest or example execution checks

#### Subphase 5.2: Local Release Readiness (depends on: 5.1)

- Task 5.2.1: Build sdist/wheel locally
  - Dependencies: Subphase 5.1 complete
  - Acceptance: Artifacts build without errors
- Task 5.2.2: Install artifacts in clean environment
  - Dependencies: Task 5.2.1
  - Acceptance: Import and core operations pass smoke tests
- Task 5.2.3: Tag v1 local milestone plan
  - Dependencies: Task 5.2.2
  - Acceptance: Version and changelog entry prepared (no PyPI publish)

**Subphase 5.2 Testing (MUST pass before completion)**:
- Full test suite
- Packaging smoke tests

## Parallelization Plan

1. Phase 4 subphases 4.1 and 4.2 SHOULD run in parallel after Phase 3.
2. In Phase 2, model work (2.1) and fixture/test authoring MAY overlap after interfaces are drafted.
3. Validation rule implementation (3.1) and issue-code documentation draft MAY run in parallel.

## Testing Strategy

### Unit Tests

1. Model constructors and extras preservation
2. JSON codec canonical/preserve behavior
3. Validation rule-by-rule checks
4. Report object and strict exception behavior

### Integration Tests

1. Dict API end-to-end load/validate/dump
2. Class API end-to-end load/validate/dump
3. Interoperability between dict and class APIs
4. Round-trip tests with unknown fields

### Regression Fixtures

1. Minimal valid v0.5 plan
2. Invalid status examples
3. Missing required field examples
4. Invalid `planRef` URI examples
5. Deeply nested `subItems` examples

### Quality Gates

1. All tests MUST pass before phase completion.
2. New public API behavior MUST include tests.
3. Issue codes and messages SHOULD remain backward compatible after introduction.

## Deployment

### Packaging

1. Use `pyproject.toml` with Python 3.10+ classifiers.
2. Produce local sdist/wheel artifacts.
3. Local installation MUST be documented and tested.

### Release Policy (v1)

1. v1 targets local/dev usage only (no immediate PyPI publish).
2. A future phase MAY add PyPI release automation.

## Future Work (Post-v1)

1. TRON support via `libtronpy` integration
2. DAG validation (cycle/reference checks)
3. Optional CLI (`validate`, `format`, `info`)
4. Compatibility/import tools for non-core historical formats

## Rationale and Tradeoffs

1. **Lenient parse + explicit validate** favors tooling and real-world editing workflows.
2. **Both dict and class APIs** improve adoption across scripting and typed app use.
3. **Dataclasses over heavy validators** keep core runtime simple and explicit.
4. **Unknown-field preservation** protects forward compatibility.
5. **No legacy/TRON in v1** keeps scope controlled and implementation tractable.

## Completion Signal

When this specification is accepted and implemented, the user can proceed with:

`implement SPECIFICATION.md`
