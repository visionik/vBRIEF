# vBRIEF Extension Proposal: Go API Library

> **EARLY DRAFT**: This is an initial proposal and subject to change. Comments, feedback, and suggestions are strongly encouraged. Please provide input via GitHub issues or discussions.

**Extension Name**: Go API Library  
**Version**: 0.1 (Draft)  
**Status**: Proposal  
**Author**: Jonathan Taylor (visionik@pobox.com)  
**Date**: 2025-12-27

## Overview

This document describes a Go library implementation for working with vBRIEF documents. The library provides idiomatic Go interfaces for creating, parsing, manipulating, and validating vBRIEF TodoLists and Plans in both JSON and TRON formats.

The library enables:
- **Type-safe operations** on vBRIEF documents
- **Format conversion** between JSON and TRON
- **Validation** against core and extension schemas
- **Builder patterns** for constructing complex documents
- **Query interfaces** for filtering and traversing structures
- **Serialization/deserialization** with proper error handling

## Motivation

**Why a Go library?**
- Go is widely used for CLI tools, agents, and backend services
- Type safety prevents common errors when manipulating structured data
- Standard library makes JSON handling straightforward
- Go's simplicity aligns with vBRIEF's design philosophy
- Strong testing culture matches vBRIEF's quality standards

**Use cases**:
- Agentic systems written in Go (task orchestrators, memory systems)
- CLI tools for managing vBRIEF documents (`va` command)
- Web services providing vBRIEF APIs
- Format converters and validators
- Integration with other Go-based tools (Beads, etc.)

## Architecture

### Package Structure

The Go implementation currently lives inside this repo under `api/go`:

```
github.com/visionik/vBRIEF/api/go/
├── pkg/
│   ├── core/           # Core types + mutation helpers
│   ├── parser/         # JSON/TRON parsing (auto-detect supported)
│   ├── builder/        # Fluent builders for TodoList + Plan
│   ├── validator/      # Core validation (extensions not implemented yet)
│   ├── query/          # Query/filter interfaces (TodoList focused)
│   ├── updater/        # Validated mutations (stateful helper)
│   └── convert/        # JSON/TRON conversion helpers
└── examples/           # Usage examples
```

Notes:
- A `cmd/va` CLI is **not** implemented in `api/go` today.
- TRON support is implemented by using the `trongo` library (see `go.mod` replace/require).

## Core API Design

### Core Types

```go
package core

// Document represents the root vBRIEF document.
// A document contains metadata and either a TodoList or a Plan (but not both).
type Document struct {
    Info     Info      `json:"vBRIEFInfo" tron:"vBRIEFInfo"`
    TodoList *TodoList `json:"todoList,omitempty" tron:"todoList,omitempty"`
    Plan     *Plan     `json:"plan,omitempty" tron:"plan,omitempty"`
}

// Info contains document-level metadata that appears once per file.
type Info struct {
    Version     string                 `json:"version" tron:"version"`
    Author      string                 `json:"author,omitempty" tron:"author,omitempty"`
    Description string                 `json:"description,omitempty" tron:"description,omitempty"`
    Metadata    map[string]interface{} `json:"metadata,omitempty" tron:"metadata,omitempty"`
}

type TodoList struct {
    Items []TodoItem `json:"items" tron:"items"`
}

type TodoItem struct {
    Title  string     `json:"title" tron:"title"`
    Status ItemStatus `json:"status" tron:"status"`
}

type ItemStatus string

const (
    StatusPending    ItemStatus = "pending"
    StatusInProgress ItemStatus = "inProgress"
    StatusCompleted  ItemStatus = "completed"
    StatusBlocked    ItemStatus = "blocked"
    StatusCancelled  ItemStatus = "cancelled"
)

type Plan struct {
    Title      string               `json:"title" tron:"title"`
    Status     PlanStatus           `json:"status" tron:"status"`
    Narratives map[string]Narrative `json:"narratives" tron:"narratives"`
    Items      []PlanItem           `json:"items,omitempty" tron:"items,omitempty"`
}

// PlanStatus represents plan status
type PlanStatus string

const (
    PlanStatusDraft      PlanStatus = "draft"
    PlanStatusProposed   PlanStatus = "proposed"
    PlanStatusApproved   PlanStatus = "approved"
    PlanStatusInProgress PlanStatus = "inProgress"
    PlanStatusCompleted  PlanStatus = "completed"
    PlanStatusCancelled  PlanStatus = "cancelled"
)

// PlanItem represents a stage of work within a plan
type PlanItem struct {
    Title  string         `json:"title" tron:"title"`
    Status PlanItemStatus `json:"status" tron:"status"`
}

// PlanItemStatus represents plan item status
type PlanItemStatus string

const (
    PlanItemStatusPending    PlanItemStatus = "pending"
    PlanItemStatusInProgress PlanItemStatus = "inProgress"
    PlanItemStatusCompleted  PlanItemStatus = "completed"
    PlanItemStatusBlocked    PlanItemStatus = "blocked"
    PlanItemStatusCancelled  PlanItemStatus = "cancelled"
)

// Narrative represents a named documentation block
type Narrative struct {
    Title   string `json:"title" tron:"title"`
    Content string `json:"content" tron:"content"`
}
```

### Parser API

The `parser` package supports JSON, TRON, and auto-detection.

```go
package parser

import "io"

type Parser interface {
    Parse(r io.Reader) (*core.Document, error)
    ParseBytes(data []byte) (*core.Document, error)
    ParseString(s string) (*core.Document, error)
}

type Format string

const (
    FormatJSON Format = "json"
    FormatTRON Format = "tron"
    FormatAuto Format = "auto"
)

func NewJSONParser() Parser
func NewTRONParser() Parser
func NewAutoParser() Parser

// New is a factory that returns a parser for the requested format.
func New(format Format) (Parser, error)
```

### Builder API

The actual `builder` package is intentionally small and focused.

```go
package builder

import "github.com/visionik/vBRIEF/api/go/pkg/core"

// TodoList builder
builder.NewTodoList(version string) *TodoListBuilder
  .WithAuthor(author string)
  .WithDescription(desc string)
  .WithMetadata(key string, value any)
  .AddItem(title string, status core.ItemStatus)
  .AddPendingItem(title string)
  .AddInProgressItem(title string)
  .AddCompletedItem(title string)
  .Build() *core.Document

// Plan builder
builder.NewPlan(title, version string) *PlanBuilder
  .WithAuthor(author string)
  .WithDescription(desc string)
  .WithStatus(status core.PlanStatus)
  .WithProposal(title, content string) // required for valid plans
  .WithProblem(title, content string)
  .WithContext(title, content string)
  .WithAlternatives(title, content string)
  .WithRisks(title, content string)
  .WithTesting(title, content string)
  .AddPlanItem(title string, status core.PlanItemStatus)
  .AddPendingPlanItem(title string)
  .AddInProgressPlanItem(title string)
  .AddCompletedPlanItem(title string)
  .Build() *core.Document

// If you need explicit status at creation time:
builder.NewPlanWithStatus(version, title string, status core.PlanStatus) *PlanBuilder
```

### Validator API

```go
package validator

import "github.com/visionik/vBRIEF/api/go/pkg/core"

type Validator interface {
    Validate(doc *core.Document) error
    ValidateCore(doc *core.Document) error

    // Extensions are not implemented yet.
    // If any extensions are requested, this returns ErrExtensionsNotSupported.
    ValidateExtensions(doc *core.Document, extensions []string) error
}

func NewValidator() Validator
func New() Validator // alias
```

### Query API

```go
package query

import "github.com/visionik/vBRIEF/api/go/pkg/core"

query.NewTodoQuery(items []core.TodoItem) *TodoQuery
  .ByStatus(status core.ItemStatus)
  .ByTitle(substring string)      // case-insensitive
  .Where(fn func(core.TodoItem) bool)
  .All() []core.TodoItem
  .First() *core.TodoItem
  .Count() int
  .Any() bool

// Note: ByTag exists but currently returns an empty result because tag support
// would require an extension that is not implemented yet.
```

### Converter API

```go
package convert

import (
    "io"

    "github.com/visionik/vBRIEF/api/go/pkg/core"
)

type Format string

const (
    FormatJSON Format = "json"
    FormatTRON Format = "tron"
)

type Converter interface {
    Convert(doc *core.Document, format Format) ([]byte, error)
    ConvertTo(doc *core.Document, format Format, w io.Writer) error
}

func NewConverter() Converter

// Convenience helpers:
func ToJSON(doc *core.Document) ([]byte, error)
func ToJSONIndent(doc *core.Document, prefix, indent string) ([]byte, error)
func ToTRON(doc *core.Document) ([]byte, error)
func ToTRONIndent(doc *core.Document, prefix, indent string) ([]byte, error)
```

### Mutation API

There are two mutation styles implemented today:

1) **Direct mutations on core types** (no automatic validation)
- `(*core.TodoList).AddItem`, `RemoveItem`, `UpdateItem`, `FindItem`
- `(*core.Plan).AddNarrative`, `RemoveNarrative`, `UpdateNarrative`, `AddPlanItem`, `RemovePlanItem`, `UpdatePlanItem`
- Convenience methods on `*core.Document` for common operations (e.g. `AddTodoItem`, `UpdateTodoItemStatus`, `AddPlanItem`, `AddNarrative`)

2) **Validated mutations via `updater.Updater`**
- `updater.NewUpdater(doc)` binds an updater to a document and validates after changes.
- Supports single-operation updates (e.g. `UpdateItemStatus`, `AddItemValidated`, `RemoveItemValidated`, `UpdatePlanStatus`) and batch updates via `Transaction(fn)`.

See `api/go/pkg/core` and `api/go/pkg/updater` for the current method set.

## Extension Support

Extension modules are **not implemented** in `api/go` yet.

- The validator exposes `ValidateExtensions`, but currently returns `ErrExtensionsNotSupported` when extensions are requested.
- Some APIs are stubbed with “safe defaults” until an extension layer exists (e.g. `query.ByTag` currently returns an empty result).

## Usage Examples

The canonical examples are kept close to the implementation:
- `api/go/README.md` contains a Quick Start that matches the current API.
- `api/go/examples/` contains runnable examples (`basic`, `mutations`, `strict-errors`).

Future work (not implemented today): a `va` CLI.

## Testing Strategy

Following Go and vBRIEF best practices:

### Unit Tests

Unit tests live alongside the implementation under `api/go/pkg/*` and are primarily table-driven tests using `testify`.

### Integration Tests

The repo includes integration-style tests in `api/go/pkg/*` as well as runnable examples under `api/go/examples/`.

A minimal JSON round-trip example (representative of the existing tests):

```go
package integration_test

import (
    "testing"

    "github.com/stretchr/testify/assert"

    "github.com/visionik/vBRIEF/api/go/pkg/builder"
    "github.com/visionik/vBRIEF/api/go/pkg/convert"
    "github.com/visionik/vBRIEF/api/go/pkg/parser"
    "github.com/visionik/vBRIEF/api/go/pkg/core"
)

func TestRoundTrip_JSON(t *testing.T) {
    original := builder.NewTodoList("0.4").
        AddPendingItem("Task 1").
        Build()

    jsonBytes, err := convert.ToJSONIndent(original, "", "  ")
    assert.NoError(t, err)

    p := parser.NewJSONParser()
    parsed, err := p.ParseBytes(jsonBytes)
    assert.NoError(t, err)

    assert.Equal(t, original, parsed)
}

func TestRoundTrip_TRON(t *testing.T) {
    original := builder.NewTodoList("0.4").
        AddPendingItem("Task 1").
        Build()

    tronBytes, err := convert.ToTRON(original)
    assert.NoError(t, err)

    p := parser.NewTRONParser()
    parsed, err := p.ParseBytes(tronBytes)
    assert.NoError(t, err)

    assert.Equal(t, original, parsed)
}

func TestConversion_JSONToTRON(t *testing.T) {
    original := builder.NewTodoList("0.4").
        AddPendingItem("Task 1").
        Build()

    jsonBytes, err := convert.ToJSON(original)
    assert.NoError(t, err)

    // Parse JSON, then re-emit as TRON
    jsonParsed, err := parser.NewJSONParser().ParseBytes(jsonBytes)
    assert.NoError(t, err)

    tronBytes, err := convert.ToTRON(jsonParsed)
    assert.NoError(t, err)

    // Parse TRON back and compare
    tronParsed, err := parser.NewTRONParser().ParseBytes(tronBytes)
    assert.NoError(t, err)

    assert.Equal(t, original, tronParsed)
}
```

### Coverage Requirements
- CI enforces a minimum overall statement coverage of **≥75%** for `api/go` via the `task api:go:test:coverage` task.
- Examples are excluded from coverage measurement.

## Current implementation status (what exists in `api/go` today)

Implemented:
- Core types: `core.Document`, `core.TodoList`, `core.TodoItem`, `core.Plan`, `core.PlanItem`, `core.Narrative`
- Builders for TodoLists and Plans
- Parsers: JSON, TRON (via `trongo`), and auto-detection
- Converters: JSON/TRON encode helpers
- Core validator (including “plan must have proposal narrative” rule)
- Basic TodoList query API (status/title/predicate)
- Updater helper for validated mutations

Not implemented (still proposal-level):
- Extension modules (validator exposes `ValidateExtensions` but returns `ErrExtensionsNotSupported` when extensions are requested)
- A `va` CLI under `api/go/cmd`

## Standards and Compliance

Following vBRIEF project guidelines:

### Code Quality
- All exported symbols have godoc comments (complete sentences)
- Table-driven tests using testify
- Coverage gate: ≥75% overall statement coverage (see `task api:go:test:coverage`)
- `task check` before all commits

### Documentation
- The main spec documents live at the repo root.
- The Go API has its own README at `api/go/README.md`.
- Runnable examples live in `api/go/examples/`.

### Task Targets
The repo is task-centric; the actual tasks are already implemented:
- `task quality` (root) delegates to `task api:go:quality`
- `task api:go:test:coverage` enforces the ≥75% coverage gate
- `task api:go:check` runs `fmt`, `vet`, and tests

### Conventional Commits
- `feat(core): add TodoList builder`
- `fix(parser): handle empty narratives`
- `docs(api): update examples`
- `test(validator): add edge cases`

## Open Questions

1. **TRON support strategy**
   - Today: TRON parse/serialize is provided via the `trongo` library (wired via `go.mod`).
   - Question: do we want to stay on `trongo`, or vendor/pin a specific TRON parser interface for long-term stability?

2. **Extension model in Go**
   - Extensions are not implemented yet.
   - Question: when extensions land, should we extend core types via struct embedding, composition + adapters, or a separate “extension payload” map?

3. **Validation ergonomics**
   - Today: core validation is explicit via `validator.NewValidator().Validate(doc)` and enforced by the updater helper.
   - Question: should parsing optionally validate by default (opt-in strict mode), or remain parse-then-validate?

4. **CLI**
   - A `va` CLI is not implemented in `api/go` yet.
   - Question: should it live in this repo (under `api/go/cmd/va`) or in a separate repo once it grows?

## Related Work

- **Go JSON Libraries**: encoding/json (standard), jsoniter (fast)
- **Go CLI Libraries**: cobra, cli, kingpin
- **Similar Projects**: 
  - go-jira (JIRA Go client)
  - gh (GitHub CLI in Go)
  - todolist (various Go implementations)

## References

- vBRIEF Specification: https://github.com/visionik/vBRIEF
- Go Documentation: https://go.dev/doc/comment
- TRON Format: https://tron-format.github.io/
- Testify: https://github.com/stretchr/testify
- vBRIEF Beads Extension: [vBRIEF-extension-beads.md](./vBRIEF-extension-beads.md)

## Community Feedback

This is a **draft proposal**. Feedback needed:

1. Is the package structure appropriate?
2. Are the builder patterns idiomatic Go?
3. Should extensions use embedded structs or interfaces?
4. Is the CLI command structure intuitive?
5. What additional utilities would be valuable?

**Discuss**: https://github.com/visionik/vBRIEF/discussions
