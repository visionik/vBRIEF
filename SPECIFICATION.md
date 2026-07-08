# libxbrief Phase 2 — Builder & Helpers SPECIFICATION

> **Source**: [`xbrief/specification.xbrief.json`](xbrief/specification.xbrief.json) — `status: approved`

## Overview

Additive `PlanBuilder` API and convenience helpers for libxbrief. Zero new dependencies,
full backward compatibility with existing `XBriefDocument` / `Plan` / `PlanItem` constructors.

## Requirements

### Functional Requirements

- **FR-1**: `PlanBuilder` class MUST accept plan-level fields (`title`, `status`, any optional
  `Plan` field) as constructor kwargs and produce a `XBriefDocument` via `to_document()`.
- **FR-2**: `PlanBuilder` MUST support optional use as a context manager. `__exit__` is a
  no-op. Plain object usage (without `with`) MUST also work.
- **FR-3**: `PlanBuilder.add_item(title, *, id=None, status='pending', **kwargs)` MUST add a
  top-level item and return an `ItemBuilder`.
- **FR-4**: `PlanBuilder.add_narrative(key, value)` MUST add to `plan.narratives`.
- **FR-5**: `PlanBuilder.add_edges_from(edges)` MUST accept an iterable of
  `(from_id, to_id, type)` tuples and append to `plan.edges`.
- **FR-6**: `ItemBuilder.add_subitem(title, *, id=None, status='pending', **kwargs)` MUST
  return a new `ItemBuilder`, enabling unlimited recursive nesting.
- **FR-7**: `ItemBuilder.add_narrative(key, value)` MUST add to the item's `narrative` dict.
- **FR-8**: `ItemBuilder` MUST pass all extra kwargs to the underlying `PlanItem` constructor.
- **FR-9**: When `id` is omitted, the builder MUST auto-generate a slug from the title.
  Sub-items use dot notation: `{parent_id}.{child_slug}`.
- **FR-10**: `PlanBuilder` MUST accept a `strict` parameter (default `True`). `strict=True`
  raises `ValueError` immediately on invalid calls; `strict=False` defers to `validate()`.
- **FR-11**: `quick_todo(title, items, *, status='running', **kwargs)` MUST accept strings or
  `PlanItem` objects and return a `XBriefDocument`. Strings are coerced to
  `PlanItem(title=s, status='pending')`.
- **FR-12**: `from_items(title, items, *, status='running', **kwargs)` MUST accept a list of
  `PlanItem` objects (no coercion) and return a `XBriefDocument`.
- **FR-13**: `PlanItem` MUST gain class method factories: `pending`, `running`, `completed`,
  `blocked`, `cancelled`, `draft`. Each accepts `title` + same kwargs as `PlanItem.__init__`.
- **FR-14**: `PlanBuilder`, `quick_todo`, `from_items` MUST be exported from
  `libxbrief.__init__` and added to `__all__`.

### Non-Functional Requirements

- **NFR-1**: No new runtime dependencies. Standard library and existing libxbrief internals only.
- **NFR-2**: Full backward compatibility. All existing public API unchanged.
- **NFR-3**: Python 3.10+ only. No syntax or stdlib features above 3.10.
- **NFR-4**: All new code MUST have pytest coverage matching the existing suite standard.
  Each phase ends only when its tests pass.

## Architecture

### New file: `libxbrief/builder.py`
Contains `PlanBuilder`, `ItemBuilder`, `quick_todo()`, and `from_items()`. All builder
logic isolated from the core model.

### Modified: `libxbrief/models.py`
Add `PlanItem` class method factories (FR-13). No other changes to existing model logic.

### Modified: `libxbrief/__init__.py`
Export `PlanBuilder`, `quick_todo`, `from_items` (FR-14).

### Key design notes

- `ItemBuilder` holds a reference to the item being built and does NOT hold a reference
  back to `PlanBuilder`.
- `PlanBuilder` maintains a shared `id_registry: set[str]` passed to every `ItemBuilder`
  for duplicate-ID detection when `strict=True`.
- Slug generation: `_slugify(text)` — lowercase, non-alphanumeric → hyphens, collapse
  consecutive hyphens.
- `to_document()` assembles all `ItemBuilder` instances depth-first into a `XBriefDocument`.
- `__enter__` returns `self`; `__exit__` is a no-op.

## Implementation Plan

### Phase 1: Core Builder
*No external dependencies. Can begin immediately.*

#### Subphase 1.1: ItemBuilder

- **Task 1.1.1** — Implement `_slugify()` and `ItemBuilder` class
  `libxbrief/builder.py`
  - `ItemBuilder.__init__(title, *, id, status, strict, id_registry, parent_id, **kwargs)`
  - Auto-slugify `id` when `None`; prefix with `parent_id.` for nested items
  - Register `id` in shared `id_registry`; raise `ValueError` on duplicate when `strict=True`
  - Implement `add_subitem()`, `add_narrative()`, `to_planitem()` (recursive)
  - Dependencies: none
  - Acceptance: unit tests pass for nesting, slug generation, duplicate-ID detection,
    narrative accumulation, kwargs passthrough
  - Traces: FR-3, FR-6, FR-7, FR-8, FR-9, FR-10

- **Task 1.1.2** — Tests for `ItemBuilder` (`tests/test_builder_item.py`)
  - Dependencies: 1.1.1
  - Acceptance: all pass — 3+ level nesting, slug override, dot notation, narrative
    accumulation, kwargs round-trip, strict/non-strict duplicate ID
  - Traces: FR-6, FR-7, FR-8, FR-9, FR-10

#### Subphase 1.2: PlanBuilder *(depends on: 1.1)*

- **Task 1.2.1** — Implement `PlanBuilder` class
  `libxbrief/builder.py`
  - `PlanBuilder(title, *, status='draft', strict=True, **kwargs)`
  - Implement `add_item()`, `add_narrative()`, `add_edges_from()` (validates IDs when
    `strict=True`), `to_document()`, `__enter__()`, `__exit__()` (no-op)
  - Dependencies: 1.1.1
  - Acceptance: full round-trip — build → `to_document()` → `validate(dag=True)` is valid
  - Traces: FR-1, FR-2, FR-3, FR-4, FR-5, FR-10

- **Task 1.2.2** — Tests for `PlanBuilder` (`tests/test_builder_plan.py`)
  - Dependencies: 1.2.1 (blocks), 1.1.2 (informs)
  - Acceptance: all pass — CM vs plain object, narratives, edges (valid + invalid with
    strict), `to_document()` validity, `strict=False` deferral, JSON round-trip
  - Traces: FR-1, FR-2, FR-4, FR-5, FR-10

---

### Phase 2: Helpers
*Subphase 2.1 is independent and can run in parallel with Phase 1.*
*Subphase 2.2 depends on Phase 1.*

#### Subphase 2.1: PlanItem Status Factories *(no dependencies)*

- **Task 2.1.1** — Add `PlanItem` class method factories to `libxbrief/models.py`
  - `pending`, `running`, `completed`, `blocked`, `cancelled`, `draft`
  - Each delegates to `cls(title=title, status='<value>', **kwargs)`
  - Dependencies: none
  - Acceptance: `PlanItem.pending('Fix bug', id='fix', priority='high')` produces a
    correctly populated `PlanItem` with `status='pending'`
  - Traces: FR-13

- **Task 2.1.2** — Tests for `PlanItem` factories (`tests/test_models_factories.py`)
  - Dependencies: 2.1.1
  - Acceptance: each factory sets the correct status; all `PlanItem` kwargs pass through
  - Traces: FR-13

#### Subphase 2.2: Standalone Helper Functions *(depends on: Phase 1)*

- **Task 2.2.1** — Implement `quick_todo()` in `libxbrief/builder.py`
  - Dependencies: 1.2.1
  - Acceptance: returns valid `XBriefDocument`; strings coerced to pending `PlanItem`s
  - Traces: FR-11

- **Task 2.2.2** — Implement `from_items()` in `libxbrief/builder.py`
  - Dependencies: 1.2.1
  - Acceptance: returns valid `XBriefDocument`; `PlanItem` objects used as-is, not mutated
  - Traces: FR-12

- **Task 2.2.3** — Tests for helpers (`tests/test_builder_helpers.py`)
  - Dependencies: 2.2.1, 2.2.2
  - Acceptance: `quick_todo` with string list, mixed list, empty list; `from_items` with
    `PlanItem`s; both `validate().is_valid == True`
  - Traces: FR-11, FR-12

---

### Phase 3: Integration & Export *(depends on: Phase 1 and Phase 2)*

- **Task 3.1.1** — Export `PlanBuilder`, `quick_todo`, `from_items` from
  `libxbrief/__init__.py`
  - Dependencies: 1.2.2, 2.1.2, 2.2.3
  - Acceptance: `from libxbrief import PlanBuilder, quick_todo, from_items` works without error
  - Traces: FR-14

- **Task 3.1.2** — Integration tests (`tests/test_builder_integration.py`)
  - Dependencies: 3.1.1
  - Acceptance: full round-trip `PlanBuilder` → `validate(dag=True)` → `dumps` → `loads` →
    `from_dict` field equality; builder + direct `PlanItem` mixed; `quick_todo` file I/O
    round-trip
  - Traces: FR-1, FR-11, FR-12, FR-14

- **Task 3.1.3** — Run full test suite and verify no regressions
  - Dependencies: 3.1.2
  - Acceptance: `task test` (or `pytest tests/`) exits 0; all pre-existing tests still pass
  - Traces: NFR-2, NFR-4

## Testing Strategy

- All new test files live in `tests/` alongside existing files.
- No phase/task is complete until its tests pass — tests are the acceptance gate.
- No mocking of libxbrief internals; tests build real documents and validate them.
- Edge cases required across all tests:
  - Empty plan (no items, no edges)
  - Item with no ID used in `add_edges_from` (strict and non-strict modes)
  - Slug collision when two items share the same slugified title
  - Deep nesting (5+ levels) via `add_subitem()`
  - `to_document()` called multiple times on the same builder (idempotent)

## Deployment

No new package dependencies. Version bump to `0.7.0` in `pyproject.toml` after all phases
pass. No PyPI publish required (local dev package for now).
