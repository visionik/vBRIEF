# vBRIEF Go API Library

A Go library for working with vBRIEF documents, providing type-safe operations, format conversion, validation, builders, and query interfaces for TodoLists and Plans.

## Features

- **Type-safe operations** on vBRIEF documents
- **Format conversion** between JSON and TRON
- **Validation** against core schema
- **Builder patterns** for fluent document construction  
- **Query interfaces** for filtering and traversing structures
- **Dual format support**: JSON and [TRON](https://tron-format.github.io/)

## Installation

```bash
go get github.com/visionik/vBRIEF/api/go
```

## Quick Start

### Building a TodoList

```go
package main

import (
    "fmt"
    "github.com/visionik/vBRIEF/api/go/pkg/builder"
    "github.com/visionik/vBRIEF/api/go/pkg/convert"
)

func main() {
    // Build a TodoList using fluent API
    doc := builder.NewTodoList("0.2").
        WithAuthor("agent-alpha").
        AddPendingItem("Implement authentication").
        AddPendingItem("Write API documentation").
        AddInProgressItem("Setup database").
        Build()

    // Convert to JSON
    jsonData, _ := convert.ToJSONIndent(doc, "", "  ")
    fmt.Println(string(jsonData))

    // Convert to TRON (token-efficient format)
    tronData, _ := convert.ToTRON(doc)
    fmt.Println(string(tronData))
}
```

### Building a Plan

```go
planDoc := builder.NewPlan("Add user authentication", "0.2").
    WithAuthor("team-lead").
    WithStatus(core.PlanStatusDraft).
    WithProposal("Implement JWT-based authentication with refresh tokens").
    WithProblem("Current system lacks secure authentication").
    AddPendingPlanItem("Database setup").
    AddInProgressPlanItem("JWT implementation").
    Build()
```

### Parsing and Querying

```go
import (
    "github.com/visionik/vBRIEF/api/go/pkg/parser"
    "github.com/visionik/vBRIEF/api/go/pkg/query"
    "github.com/visionik/vBRIEF/api/go/pkg/core"
)

// Parse from JSON or TRON (auto-detect)
p := parser.NewAutoParser()
doc, err := p.ParseString(content)

// Query pending items
q := query.NewTodoQuery(doc.TodoList.Items)
pendingItems := q.ByStatus(core.StatusPending).All()

// Chain queries
highPriority := q.
    ByStatus(core.StatusPending).
    ByTitle("urgent").
    All()
```

### Validation

```go
import "github.com/visionik/vBRIEF/api/go/pkg/validator"

v := validator.NewValidator()
if err := v.Validate(doc); err != nil {
    fmt.Printf("Validation failed: %v\n", err)
}
```

## Package Structure

```
github.com/visionik/vBRIEF/api/go/
├── pkg/
│   ├── core/           # Core types (Document, TodoList, Plan, etc.)
│   ├── parser/         # JSON/TRON parsing
│   ├── builder/        # Fluent builders
│   ├── validator/      # Schema validation
│   ├── query/          # Query/filter interfaces
│   ├── updater/        # Validated mutations
│   └── convert/        # Format conversion
├── examples/           # Usage examples
└── cmd/va/            # CLI tool (coming soon)
```

## Core Types

### Document
Root vBRIEF document containing metadata and either a TodoList or Plan.

### TodoList
Collection of actionable work items for short-term memory.

### TodoItem
Single actionable task with title and status (`pending`, `inProgress`, `completed`, `blocked`, `cancelled`).

### Plan
Structured design document for medium-term memory with narratives and plan items.

### PlanItem
Stage of work within a plan.


## API Reference

### Builder API

```go
// TodoList builder
builder.NewTodoList(version string) *TodoListBuilder
  .WithAuthor(author string)
  .WithDescription(desc string)
  .AddItem(title string, status core.ItemStatus)
  .AddPendingItem(title string)
  .AddInProgressItem(title string)
  .Build() *core.Document

// Plan builder
builder.NewPlan(title, version string) *PlanBuilder
  .WithAuthor(author string)
  .WithStatus(status core.PlanStatus)
  .WithProposal(content string)
  .WithProblem(content string)
  .WithBackground(content string)  // alias: WithContext(content)
  .AddPlanItem(title string, status core.PlanItemStatus)
  .AddPendingPlanItem(title string)
  .Build() *core.Document
```

### Parser API

```go
// Create parser
parser.NewJSONParser() Parser
parser.NewTRONParser() Parser  
parser.NewAutoParser() Parser  // Auto-detects format

// Parse methods
Parse(r io.Reader) (*core.Document, error)
ParseBytes(data []byte) (*core.Document, error)
ParseString(s string) (*core.Document, error)
```

### Converter API

```go
convert.ToJSON(doc *core.Document) ([]byte, error)
convert.ToJSONIndent(doc, prefix, indent string) ([]byte, error)
convert.ToTRON(doc *core.Document) ([]byte, error)
convert.ToTRONIndent(doc, prefix, indent string) ([]byte, error)
```

### Query API

```go
query.NewTodoQuery(items []core.TodoItem) *TodoQuery
  .ByStatus(status core.ItemStatus)
  .ByTitle(substring string)
  .Where(predicate func(core.TodoItem) bool)
  .All() []core.TodoItem
  .First() *core.TodoItem
  .Count() int
  .Any() bool
```

### Validator API

```go
validator.NewValidator() Validator
  .Validate(doc *core.Document) error
  .ValidateCore(doc *core.Document) error
```

### Mutation API

The library provides two approaches for modifying documents:

#### 1. Direct Mutations

Methods directly on `TodoList` and `Plan` types:

```go
// TodoList mutations
todoList.AddItem(item TodoItem)
todoList.RemoveItem(index int) error
todoList.UpdateItem(index int, updates func(*TodoItem)) error
todoList.FindItem(predicate func(*TodoItem) bool) *TodoItem

// Plan mutations
plan.AddNarrative(key string, content string)
plan.RemoveNarrative(key string)
plan.UpdateNarrative(key string, updates func(*string)) error
plan.AddPlanItem(item PlanItem)
plan.RemovePlanItem(index int) error
plan.UpdatePlanItem(index int, updates func(*PlanItem)) error
```

#### 2. Validated Mutations (Updater)

The `updater` package provides validated mutations that ensure the document remains valid:

```go
import "github.com/visionik/vBRIEF/api/go/pkg/updater"

// Create updater
upd := updater.NewUpdater(doc) // Binds to a single document

// TodoList operations
err := upd.AddItemValidated(core.TodoItem{...})
err := upd.RemoveItemValidated(index)
err := upd.UpdateItemStatus(index, core.StatusCompleted)

// Plan operations
err := upd.UpdatePlanStatus(core.PlanStatusApproved)
err := upd.Transaction(func(u *updater.Updater) error {
  // apply multiple mutations to upd.Document() (todo list / plan)
  return nil
})
```

## Examples

See the [examples](./examples) directory for complete working examples:

- `examples/basic/` - Basic usage demonstrating all features
- `examples/mutations/` - Document mutation operations

To run the examples:

```bash
cd examples/basic
go run main.go

cd examples/mutations
go run main.go
```

## Format Support

### JSON
Standard JSON format with full compatibility.

### TRON
Token Reduced Object Notation for ~35-40% fewer tokens than JSON. Perfect for:
- AI/agent workflows
- Token-constrained scenarios  
- Internal storage
- Agent-to-agent communication

See the [TRON specification](https://tron-format.github.io/) for details.

## Testing

Run tests:
```bash
go test ./...
```

Run tests with coverage:
```bash
go test -cover ./...
```

## Development

This project follows Go best practices:
- All exported symbols have godoc comments
- Table-driven tests using testify
- Coverage ≥75% overall and per-package
- Standard Go project layout

## Contributing

Contributions are welcome! Please ensure:
1. All tests pass (`go test ./...`)
2. Code is formatted (`go fmt ./...`)
3. Code is vetted (`go vet ./...`)
4. Test coverage ≥75%

## License

See the [LICENSE](../../LICENSE) file in the repository root.

## References

- [vBRIEF Specification](https://github.com/visionik/vBRIEF)
- [TRON Format](https://tron-format.github.io/)
- [vBRIEF Extension: Go API](../../vBRIEF-extension-api-go.md)
