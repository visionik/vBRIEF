# vAgenda Extension Proposal: Go API Library

> **EARLY DRAFT**: This is an initial proposal and subject to change. Comments, feedback, and suggestions are strongly encouraged. Please provide input via GitHub issues or discussions.

**Extension Name**: Go API Library  
**Version**: 0.1 (Draft)  
**Status**: Proposal  
**Author**: Jonathan Taylor (visionik@pobox.com)  
**Date**: 2025-12-27

## Overview

This document describes a Go library implementation for working with vAgenda documents. The library provides idiomatic Go interfaces for creating, parsing, manipulating, and validating vAgenda TodoLists and Plans in both JSON and TRON formats.

The library enables:
- **Type-safe operations** on vAgenda documents
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
- Go's simplicity aligns with vAgenda's design philosophy
- Strong testing culture matches vAgenda's quality standards

**Use cases**:
- Agentic systems written in Go (task orchestrators, memory systems)
- CLI tools for managing vAgenda documents (`va` command)
- Web services providing vAgenda APIs
- Format converters and validators
- Integration with other Go-based tools (Beads, etc.)

## Architecture

### Package Structure

```
github.com/visionik/vagenda-go/
├── pkg/
│   ├── core/           # Core types (TodoList, Plan, Phase, etc.)
│   ├── extensions/     # Extension implementations
│   │   ├── timestamps/
│   │   ├── identifiers/
│   │   ├── metadata/
│   │   ├── hierarchical/
│   │   ├── workflow/
│   │   ├── participants/
│   │   ├── resources/
│   │   ├── recurring/
│   │   ├── security/
│   │   ├── version/
│   │   ├── forking/
│   │   └── ace/
│   ├── parser/         # JSON/TRON parsing
│   ├── builder/        # Fluent builders
│   ├── validator/      # Schema validation
│   ├── query/          # Query/filter interfaces
│   ├── updater/        # Document mutation with validation
│   └── convert/        # Format conversion
├── cmd/
│   └── va/             # CLI tool
├── internal/
│   └── tron/           # TRON parser implementation
└── examples/           # Usage examples
```

## Core API Design

### Core Types

```go
package core

import "time"

// Document represents the root vAgenda document
type Document struct {
    Info     *Info      `json:"vAgendaInfo" tron:"vAgendaInfo"`
    TodoList *TodoList  `json:"todoList,omitempty" tron:"todoList,omitempty"`
    Plan     *Plan      `json:"plan,omitempty" tron:"plan,omitempty"`
}

// Info contains document-level metadata
type Info struct {
    Version     string                 `json:"version" tron:"version"`
    Author      string                 `json:"author,omitempty" tron:"author,omitempty"`
    Description string                 `json:"description,omitempty" tron:"description,omitempty"`
    Metadata    map[string]interface{} `json:"metadata,omitempty" tron:"metadata,omitempty"`
}

// TodoList represents a collection of work items
type TodoList struct {
    Items []TodoItem `json:"items" tron:"items"`
}

// TodoItem represents a single actionable task
type TodoItem struct {
    Title  string     `json:"title" tron:"title"`
    Status ItemStatus `json:"status" tron:"status"`
}

// ItemStatus represents todo item status
type ItemStatus string

const (
    StatusPending    ItemStatus = "pending"
    StatusInProgress ItemStatus = "inProgress"
    StatusCompleted  ItemStatus = "completed"
    StatusBlocked    ItemStatus = "blocked"
    StatusCancelled  ItemStatus = "cancelled"
)

// Plan represents a structured design document
type Plan struct {
    Title      string              `json:"title" tron:"title"`
    Status     PlanStatus          `json:"status" tron:"status"`
    Narratives map[string]Narrative `json:"narratives" tron:"narratives"`
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

// Phase represents a stage of work within a plan
type Phase struct {
    Title  string      `json:"title" tron:"title"`
    Status PhaseStatus `json:"status" tron:"status"`
}

// PhaseStatus represents phase status
type PhaseStatus string

const (
    PhaseStatusPending    PhaseStatus = "pending"
    PhaseStatusInProgress PhaseStatus = "inProgress"
    PhaseStatusCompleted  PhaseStatus = "completed"
    PhaseStatusBlocked    PhaseStatus = "blocked"
    PhaseStatusCancelled  PhaseStatus = "cancelled"
)

// Narrative represents a named documentation block
type Narrative struct {
    Title   string `json:"title" tron:"title"`
    Content string `json:"content" tron:"content"`
}
```

### Parser API

```go
package parser

import "io"

// Parser handles document parsing
type Parser interface {
    // Parse reads a document from reader
    Parse(r io.Reader) (*core.Document, error)
    
    // ParseString parses a document from string
    ParseString(s string) (*core.Document, error)
    
    // ParseBytes parses a document from bytes
    ParseBytes(b []byte) (*core.Document, error)
}

// NewJSONParser creates a JSON parser
func NewJSONParser() Parser {
    return &jsonParser{}
}

// NewTRONParser creates a TRON parser
func NewTRONParser() Parser {
    return &tronParser{}
}

// AutoParser automatically detects format
func AutoParser() Parser {
    return &autoParser{}
}
```

### Builder API

```go
package builder

import (
    "github.com/visionik/vagenda-go/pkg/core"
    "time"
)

// TodoListBuilder provides fluent API for building TodoLists
type TodoListBuilder struct {
    doc  *core.Document
    list *core.TodoList
}

// NewTodoList creates a new TodoList builder
func NewTodoList(version string) *TodoListBuilder {
    return &TodoListBuilder{
        doc: &core.Document{
            Info: &core.Info{Version: version},
            TodoList: &core.TodoList{Items: []core.TodoItem{}},
        },
        list: &core.TodoList{Items: []core.TodoItem{}},
    }
}

// WithAuthor sets the document author
func (b *TodoListBuilder) WithAuthor(author string) *TodoListBuilder {
    b.doc.Info.Author = author
    return b
}

// AddItem adds a todo item
func (b *TodoListBuilder) AddItem(title string, status core.ItemStatus) *TodoListBuilder {
    b.list.Items = append(b.list.Items, core.TodoItem{
        Title:  title,
        Status: status,
    })
    return b
}

// Build returns the constructed document
func (b *TodoListBuilder) Build() *core.Document {
    b.doc.TodoList = b.list
    return b.doc
}

// PlanBuilder provides fluent API for building Plans
type PlanBuilder struct {
    doc  *core.Document
    plan *core.Plan
}

// NewPlan creates a new Plan builder
func NewPlan(version, title string, status core.PlanStatus) *PlanBuilder {
    return &PlanBuilder{
        doc: &core.Document{
            Info: &core.Info{Version: version},
        },
        plan: &core.Plan{
            Title:      title,
            Status:     status,
            Narratives: make(map[string]core.Narrative),
        },
    }
}

// WithNarrative adds a narrative
func (b *PlanBuilder) WithNarrative(key, title, content string) *PlanBuilder {
    b.plan.Narratives[key] = core.Narrative{
        Title:   title,
        Content: content,
    }
    return b
}

// Build returns the constructed document
func (b *PlanBuilder) Build() *core.Document {
    b.doc.Plan = b.plan
    return b.doc
}
```

### Validator API

```go
package validator

import "github.com/visionik/vagenda-go/pkg/core"

// ValidationError represents a validation failure
type ValidationError struct {
    Field   string
    Message string
}

func (e *ValidationError) Error() string {
    return fmt.Sprintf("%s: %s", e.Field, e.Message)
}

// ValidationErrors is a collection of validation errors
type ValidationErrors []ValidationError

func (e ValidationErrors) Error() string {
    var msgs []string
    for _, err := range e {
        msgs = append(msgs, err.Error())
    }
    return strings.Join(msgs, "; ")
}

// Validator validates documents
type Validator interface {
    // Validate checks if document is valid
    Validate(doc *core.Document) error
    
    // ValidateCore checks core requirements only
    ValidateCore(doc *core.Document) error
    
    // ValidateExtensions checks extension requirements
    ValidateExtensions(doc *core.Document, extensions []string) error
}

// NewValidator creates a validator
func NewValidator() Validator {
    return &validator{}
}
```

### Query API

```go
package query

import "github.com/visionik/vagenda-go/pkg/core"

// TodoQuery provides filtering for TodoItems
type TodoQuery struct {
    items []core.TodoItem
}

// NewTodoQuery creates a query for items
func NewTodoQuery(items []core.TodoItem) *TodoQuery {
    return &TodoQuery{items: items}
}

// ByStatus filters by status
func (q *TodoQuery) ByStatus(status core.ItemStatus) *TodoQuery {
    var filtered []core.TodoItem
    for _, item := range q.items {
        if item.Status == status {
            filtered = append(filtered, item)
        }
    }
    return &TodoQuery{items: filtered}
}

// ByTag filters by tag (requires Rich Metadata extension)
func (q *TodoQuery) ByTag(tag string) *TodoQuery {
    var filtered []core.TodoItem
    for _, item := range q.items {
        // Implementation depends on extension presence
    }
    return &TodoQuery{items: filtered}
}

// All returns all matching items
func (q *TodoQuery) All() []core.TodoItem {
    return q.items
}

// First returns first matching item
func (q *TodoQuery) First() *core.TodoItem {
    if len(q.items) > 0 {
        return &q.items[0]
    }
    return nil
}

// Count returns number of matching items
func (q *TodoQuery) Count() int {
    return len(q.items)
}
```

### Converter API

```go
package convert

import (
    "io"
    "github.com/visionik/vagenda-go/pkg/core"
)

// Format represents output format
type Format string

const (
    FormatJSON Format = "json"
    FormatTRON Format = "tron"
)

// Converter handles format conversion
type Converter interface {
    // Convert document to specified format
    Convert(doc *core.Document, format Format) ([]byte, error)
    
    // ConvertTo writes document to writer in specified format
    ConvertTo(doc *core.Document, format Format, w io.Writer) error
}

// NewConverter creates a converter
func NewConverter() Converter {
    return &converter{}
}
```

### Mutation API

The library supports document modification through a hybrid approach: direct mutation for simple cases, convenience methods for common operations, and a validated updater for complex scenarios.

#### Core Type Mutations

```go
package core

// TodoList mutation methods
func (tl *TodoList) AddItem(item TodoItem) {
    tl.Items = append(tl.Items, item)
}

func (tl *TodoList) RemoveItem(index int) error {
    if index < 0 || index >= len(tl.Items) {
        return fmt.Errorf("index out of range: %d", index)
    }
    tl.Items = append(tl.Items[:index], tl.Items[index+1:]...)
    return nil
}

func (tl *TodoList) UpdateItem(index int, updates func(*TodoItem)) error {
    if index < 0 || index >= len(tl.Items) {
        return fmt.Errorf("index out of range: %d", index)
    }
    updates(&tl.Items[index])
    return nil
}

func (tl *TodoList) FindItem(predicate func(*TodoItem) bool) *TodoItem {
    for i := range tl.Items {
        if predicate(&tl.Items[i]) {
            return &tl.Items[i]
        }
    }
    return nil
}

// Plan mutation methods
func (p *Plan) AddNarrative(key string, narrative Narrative) {
    if p.Narratives == nil {
        p.Narratives = make(map[string]Narrative)
    }
    p.Narratives[key] = narrative
}

func (p *Plan) RemoveNarrative(key string) {
    delete(p.Narratives, key)
}

func (p *Plan) UpdateNarrative(key string, updates func(*Narrative)) error {
    narrative, exists := p.Narratives[key]
    if !exists {
        return fmt.Errorf("narrative not found: %s", key)
    }
    updates(&narrative)
    p.Narratives[key] = narrative
    return nil
}
```

#### Updater Package

```go
package updater

import (
    "fmt"
    "github.com/visionik/vagenda-go/pkg/core"
    "github.com/visionik/vagenda-go/pkg/validator"
)

// Updater provides validated document mutations
type Updater struct {
    doc       *core.Document
    validator validator.Validator
}

// NewUpdater creates an updater for a document
func NewUpdater(doc *core.Document) *Updater {
    return &Updater{
        doc:       doc,
        validator: validator.NewValidator(),
    }
}

// WithValidator sets a custom validator
func (u *Updater) WithValidator(v validator.Validator) *Updater {
    u.validator = v
    return u
}

// UpdateItemStatus updates an item's status with validation
func (u *Updater) UpdateItemStatus(index int, status core.ItemStatus) error {
    if err := u.doc.TodoList.UpdateItem(index, func(item *core.TodoItem) {
        item.Status = status
    }); err != nil {
        return err
    }
    return u.validator.Validate(u.doc)
}

// FindAndUpdate finds items by predicate and applies updates
func (u *Updater) FindAndUpdate(predicate func(*core.TodoItem) bool, 
                                 update func(*core.TodoItem)) error {
    if u.doc.TodoList == nil {
        return fmt.Errorf("document has no todo list")
    }
    
    found := false
    for i := range u.doc.TodoList.Items {
        if predicate(&u.doc.TodoList.Items[i]) {
            update(&u.doc.TodoList.Items[i])
            found = true
        }
    }
    
    if !found {
        return fmt.Errorf("no matching items found")
    }
    
    return u.validator.Validate(u.doc)
}

// AddItemValidated adds an item with validation
func (u *Updater) AddItemValidated(item core.TodoItem) error {
    if u.doc.TodoList == nil {
        u.doc.TodoList = &core.TodoList{}
    }
    u.doc.TodoList.AddItem(item)
    return u.validator.Validate(u.doc)
}

// RemoveItemValidated removes an item with validation
func (u *Updater) RemoveItemValidated(index int) error {
    if err := u.doc.TodoList.RemoveItem(index); err != nil {
        return err
    }
    return u.validator.Validate(u.doc)
}

// UpdatePlanStatus updates plan status with validation
func (u *Updater) UpdatePlanStatus(status core.PlanStatus) error {
    if u.doc.Plan == nil {
        return fmt.Errorf("document has no plan")
    }
    u.doc.Plan.Status = status
    return u.validator.Validate(u.doc)
}

// Transaction executes multiple operations with validation
func (u *Updater) Transaction(fn func(*Updater) error) error {
    if err := fn(u); err != nil {
        return err
    }
    return u.validator.Validate(u.doc)
}

// Document returns the underlying document
func (u *Updater) Document() *core.Document {
    return u.doc
}
```

## Extension Support

Extensions are implemented as separate packages that extend core types using embedded structs:

```go
package identifiers

import "github.com/visionik/vagenda-go/pkg/core"

// TodoItem extends core.TodoItem with ID
type TodoItem struct {
    core.TodoItem
    ID string `json:"id" tron:"id"`
}

// TodoList extends core.TodoList with ID
type TodoList struct {
    core.TodoList
    ID string `json:"id" tron:"id"`
}

// Plan extends core.Plan with ID
type Plan struct {
    core.Plan
    ID string `json:"id" tron:"id"`
}

// Phase extends core.Phase with ID
type Phase struct {
    core.Phase
    ID string `json:"id" tron:"id"`
}
```

```go
package timestamps

import (
    "time"
    "github.com/visionik/vagenda-go/pkg/core"
)

// Info extends core.Info with timestamps
type Info struct {
    core.Info
    Created  time.Time `json:"created" tron:"created"`
    Updated  time.Time `json:"updated" tron:"updated"`
    Timezone string    `json:"timezone,omitempty" tron:"timezone,omitempty"`
}

// TodoItem extends core.TodoItem with timestamps
type TodoItem struct {
    core.TodoItem
    Created time.Time `json:"created" tron:"created"`
    Updated time.Time `json:"updated" tron:"updated"`
}
```

```go
package metadata

import "github.com/visionik/vagenda-go/pkg/core"

// TodoList extends core.TodoList with metadata
type TodoList struct {
    core.TodoList
    Title       string                 `json:"title,omitempty" tron:"title,omitempty"`
    Description string                 `json:"description,omitempty" tron:"description,omitempty"`
    Metadata    map[string]interface{} `json:"metadata,omitempty" tron:"metadata,omitempty"`
}

// Priority represents item priority
type Priority string

const (
    PriorityLow      Priority = "low"
    PriorityMedium   Priority = "medium"
    PriorityHigh     Priority = "high"
    PriorityCritical Priority = "critical"
)

// TodoItem extends core.TodoItem with metadata
type TodoItem struct {
    core.TodoItem
    Description string                 `json:"description,omitempty" tron:"description,omitempty"`
    Priority    Priority               `json:"priority,omitempty" tron:"priority,omitempty"`
    Tags        []string               `json:"tags,omitempty" tron:"tags,omitempty"`
    Metadata    map[string]interface{} `json:"metadata,omitempty" tron:"metadata,omitempty"`
}
```

## Usage Examples

### Example 1: Creating a TodoList

```go
package main

import (
    "fmt"
    "github.com/visionik/vagenda-go/pkg/builder"
    "github.com/visionik/vagenda-go/pkg/convert"
    "github.com/visionik/vagenda-go/pkg/core"
)

func main() {
    // Build a TodoList
    doc := builder.NewTodoList("0.2").
        WithAuthor("agent-alpha").
        AddItem("Implement authentication", core.StatusPending).
        AddItem("Write API documentation", core.StatusPending).
        Build()

    // Convert to JSON
    converter := convert.NewConverter()
    jsonBytes, err := converter.Convert(doc, convert.FormatJSON)
    if err != nil {
        panic(err)
    }
    
    fmt.Println(string(jsonBytes))

    // Convert to TRON
    tronBytes, err := converter.Convert(doc, convert.FormatTRON)
    if err != nil {
        panic(err)
    }
    
    fmt.Println(string(tronBytes))
}
```

### Example 2: Parsing and Querying

```go
package main

import (
    "fmt"
    "os"
    "github.com/visionik/vagenda-go/pkg/parser"
    "github.com/visionik/vagenda-go/pkg/query"
    "github.com/visionik/vagenda-go/pkg/core"
)

func main() {
    // Auto-detect format and parse
    p := parser.AutoParser()
    file, _ := os.Open("tasks.tron")
    defer file.Close()
    
    doc, err := p.Parse(file)
    if err != nil {
        panic(err)
    }

    // Query pending items
    q := query.NewTodoQuery(doc.TodoList.Items)
    pending := q.ByStatus(core.StatusPending).All()
    
    fmt.Printf("Pending items: %d\n", len(pending))
    for _, item := range pending {
        fmt.Printf("  - %s\n", item.Title)
    }
}
```

### Example 3: Creating a Plan

```go
package main

import (
    "fmt"
    "github.com/visionik/vagenda-go/pkg/builder"
    "github.com/visionik/vagenda-go/pkg/convert"
    "github.com/visionik/vagenda-go/pkg/core"
)

func main() {
    doc := builder.NewPlan("0.2", "Add user authentication", core.PlanStatusDraft).
        WithNarrative("proposal", 
            "Proposed Changes",
            "Implement JWT-based authentication with refresh tokens").
        WithNarrative("problem",
            "Problem Statement", 
            "Current system lacks secure authentication").
        Build()

    converter := convert.NewConverter()
    tronBytes, _ := converter.Convert(doc, convert.FormatTRON)
    
    fmt.Println(string(tronBytes))
}
```

### Example 4: Validation

```go
package main

import (
    "fmt"
    "github.com/visionik/vagenda-go/pkg/parser"
    "github.com/visionik/vagenda-go/pkg/validator"
)

func main() {
    // Parse document
    p := parser.NewJSONParser()
    doc, _ := p.ParseString(`{
        "vAgendaInfo": {"version": "0.2"},
        "todoList": {"items": []}
    }`)

    // Validate
    v := validator.NewValidator()
    if err := v.Validate(doc); err != nil {
        fmt.Printf("Validation errors: %v\n", err)
        return
    }
    
    fmt.Println("Document is valid")
}
```

### Example 5: Using Extensions

```go
package main

import (
    "time"
    "github.com/visionik/vagenda-go/pkg/core"
    "github.com/visionik/vagenda-go/pkg/extensions/identifiers"
    "github.com/visionik/vagenda-go/pkg/extensions/timestamps"
    "github.com/visionik/vagenda-go/pkg/extensions/metadata"
)

func main() {
    // Create extended TodoItem with multiple extensions
    now := time.Now()
    
    item := struct {
        identifiers.TodoItem
        timestamps.TodoItem
        metadata.TodoItem
    }{
        TodoItem: identifiers.TodoItem{
            TodoItem: core.TodoItem{
                Title:  "Complete API documentation",
                Status: core.StatusInProgress,
            },
            ID: "item-001",
        },
        TodoItem: timestamps.TodoItem{
            Created: now,
            Updated: now,
        },
        TodoItem: metadata.TodoItem{
            Description: "Document all REST endpoints",
            Priority:    metadata.PriorityHigh,
            Tags:        []string{"docs", "api"},
        },
    }
    
    // Use the item...
}
```

### Example 6: Simple Mutations

```go
package main

import (
    "fmt"
    "os"
    "github.com/visionik/vagenda-go/pkg/parser"
    "github.com/visionik/vagenda-go/pkg/convert"
    "github.com/visionik/vagenda-go/pkg/core"
)

func main() {
    // Parse existing document
    p := parser.AutoParser()
    file, _ := os.Open("tasks.tron")
    doc, _ := p.Parse(file)
    file.Close()
    
    // Direct mutation for simple changes
    doc.TodoList.AddItem(core.TodoItem{
        Title:  "New urgent task",
        Status: core.StatusPending,
    })
    
    // Update existing item
    doc.TodoList.UpdateItem(0, func(item *core.TodoItem) {
        item.Status = core.StatusCompleted
    })
    
    // Add narrative to plan
    if doc.Plan != nil {
        doc.Plan.AddNarrative("implementation", core.Narrative{
            Title:   "Implementation Details",
            Content: "Use JWT for authentication",
        })
    }
    
    // Save back
    outFile, _ := os.Create("tasks.tron")
    defer outFile.Close()
    converter := convert.NewConverter()
    converter.ConvertTo(doc, convert.FormatTRON, outFile)
}
```

### Example 7: Validated Updates

```go
package main

import (
    "fmt"
    "os"
    "github.com/visionik/vagenda-go/pkg/parser"
    "github.com/visionik/vagenda-go/pkg/updater"
    "github.com/visionik/vagenda-go/pkg/convert"
    "github.com/visionik/vagenda-go/pkg/core"
)

func main() {
    // Parse document
    p := parser.AutoParser()
    file, _ := os.Open("tasks.tron")
    doc, _ := p.Parse(file)
    file.Close()
    
    // Create updater with validation
    upd := updater.NewUpdater(doc)
    
    // Find and update items matching criteria
    err := upd.FindAndUpdate(
        func(item *core.TodoItem) bool {
            return item.Status == core.StatusPending
        },
        func(item *core.TodoItem) {
            item.Status = core.StatusInProgress
        },
    )
    if err != nil {
        fmt.Printf("Update failed: %v\n", err)
        return
    }
    
    // Update with validation
    if err := upd.UpdateItemStatus(0, core.StatusCompleted); err != nil {
        fmt.Printf("Validation failed: %v\n", err)
        return
    }
    
    // Save validated document
    outFile, _ := os.Create("tasks.tron")
    defer outFile.Close()
    converter := convert.NewConverter()
    converter.ConvertTo(upd.Document(), convert.FormatTRON, outFile)
}
```

### Example 8: Transactional Updates

```go
package main

import (
    "fmt"
    "github.com/visionik/vagenda-go/pkg/builder"
    "github.com/visionik/vagenda-go/pkg/updater"
    "github.com/visionik/vagenda-go/pkg/core"
)

func main() {
    // Create initial document
    doc := builder.NewTodoList("0.2").
        AddItem("Task 1", core.StatusPending).
        Build()
    
    // Perform multiple updates atomically
    upd := updater.NewUpdater(doc)
    err := upd.Transaction(func(u *updater.Updater) error {
        // Add multiple items
        if err := u.AddItemValidated(core.TodoItem{
            Title:  "Task 2",
            Status: core.StatusPending,
        }); err != nil {
            return err
        }
        
        if err := u.AddItemValidated(core.TodoItem{
            Title:  "Task 3",
            Status: core.StatusPending,
        }); err != nil {
            return err
        }
        
        // Update first item
        return u.UpdateItemStatus(0, core.StatusInProgress)
    })
    
    if err != nil {
        fmt.Printf("Transaction failed: %v\n", err)
        return
    }
    
    fmt.Println("All updates completed successfully")
}
```

## CLI Tool Design

The `va` command provides command-line access to the library:

```bash
# Create a new TodoList
va create todo --version 0.2 --output tasks.tron

# Add an item
va add item tasks.tron "Implement auth" --status pending

# List items
va list tasks.tron

# Filter by status
va list tasks.tron --status pending

# Update item status
va update tasks.tron item-1 --status completed

# Convert formats
va convert tasks.tron tasks.json --format json

# Validate document
va validate tasks.tron

# Query with filters
va query tasks.tron --status pending --priority high

# Create a plan
va create plan --title "Auth Implementation" --output plan.tron

# Add narrative
va add narrative plan.tron proposal "Proposed Changes" "Use JWT tokens..."

# Add phase
va add phase plan.tron "Database setup" --status pending

# Export/Import (for integration)
va export tasks.tron --format vagenda > output.tron
va import input.tron --target tasks.tron
```

## Testing Strategy

Following Go and vAgenda best practices:

### Unit Tests
```go
package core_test

import (
    "testing"
    "github.com/stretchr/testify/assert"
    "github.com/visionik/vagenda-go/pkg/core"
)

func TestTodoItem_Status(t *testing.T) {
    tests := []struct {
        name   string
        status core.ItemStatus
        valid  bool
    }{
        {"pending is valid", core.StatusPending, true},
        {"inProgress is valid", core.StatusInProgress, true},
        {"invalid status", "invalid", false},
    }
    
    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            item := core.TodoItem{
                Title:  "Test",
                Status: tt.status,
            }
            
            err := validateStatus(item.Status)
            if tt.valid {
                assert.NoError(t, err)
            } else {
                assert.Error(t, err)
            }
        })
    }
}
```

### Integration Tests
```go
package integration_test

import (
    "testing"
    "github.com/stretchr/testify/assert"
    "github.com/visionik/vagenda-go/pkg/builder"
    "github.com/visionik/vagenda-go/pkg/parser"
    "github.com/visionik/vagenda-go/pkg/convert"
    "github.com/visionik/vagenda-go/pkg/core"
)

func TestRoundTrip_JSON(t *testing.T) {
    // Build document
    original := builder.NewTodoList("0.2").
        AddItem("Task 1", core.StatusPending).
        Build()
    
    // Convert to JSON
    converter := convert.NewConverter()
    jsonBytes, err := converter.Convert(original, convert.FormatJSON)
    assert.NoError(t, err)
    
    // Parse back
    p := parser.NewJSONParser()
    parsed, err := p.ParseBytes(jsonBytes)
    assert.NoError(t, err)
    
    // Verify equality
    assert.Equal(t, original, parsed)
}

func TestRoundTrip_TRON(t *testing.T) {
    // Similar to JSON round-trip test
}

func TestConversion_JSONToTRON(t *testing.T) {
    // Test JSON → TRON → JSON round-trip
}
```

### Coverage Requirements
- Overall coverage: ≥75%
- Per-package coverage: ≥75%
- Critical paths: 100% (parser, validator)
- Exclude: main(), examples/

## Implementation Phases

### Phase 1: Core Foundation
- Core types (Document, TodoList, TodoItem, Plan, Phase, Narrative)
- JSON parser
- Basic builder
- Core validator
- CLI skeleton (`va create`, `va list`)

### Phase 2: Extensions
- Extension 1: Timestamps
- Extension 2: Identifiers
- Extension 3: Rich Metadata
- Extension 4: Hierarchical
- Extended validators

### Phase 3: TRON Support
- TRON parser implementation
- TRON serializer
- Format auto-detection
- Conversion utilities
- CLI: `va convert`

### Phase 4: Advanced Features
- Query interface
- Remaining extensions (5-12)
- Advanced CLI commands
- Format converters for other systems

### Phase 5: Integration
- Beads interop (if Extension Beads is accepted)
- Web API server
- Additional tooling
- Performance optimization

## Standards and Compliance

Following vAgenda project guidelines:

### Code Quality
- All exported symbols have godoc comments (complete sentences)
- Table-driven tests using testify
- Coverage ≥75% overall and per-package
- `task check` before all commits

### Documentation
- All documentation in `docs/` directory
- README with quick start
- Package-level documentation
- Example code in `examples/`

### Task Targets
```yaml
# Taskfile.yml additions
tasks:
  vagenda:go:build:
    desc: Build vAgenda Go library
    cmds:
      - go build ./...

  vagenda:go:test:
    desc: Run vAgenda tests
    cmds:
      - go test -v ./pkg/...

  vagenda:go:coverage:
    desc: Check test coverage
    cmds:
      - go test -cover -coverprofile=coverage.out ./pkg/...
      - go tool cover -func=coverage.out

  vagenda:cli:build:
    desc: Build va CLI tool
    cmds:
      - go build -o bin/va ./cmd/va

  vagenda:cli:install:
    desc: Install va CLI tool
    cmds:
      - go install ./cmd/va
```

### Conventional Commits
- `feat(core): add TodoList builder`
- `fix(parser): handle empty narratives`
- `docs(api): update examples`
- `test(validator): add edge cases`

## Open Questions

1. **TRON Parser Implementation**
   - Should we implement a full TRON parser or use a library?
   - **Proposal**: Start with library if available, implement minimal parser otherwise

2. **Extension Composition**
   - How to handle multiple extensions cleanly in Go?
   - Current approach uses embedded structs - is this idiomatic?
   - **Proposal**: Use struct embedding but provide helper functions for common combinations

3. **Validation Strategy**
   - Validate at parse time or on-demand?
   - **Proposal**: Validate on-demand to allow partial documents during construction

4. **CLI vs Library**
   - Should CLI be separate repository?
   - **Proposal**: Same repo, separate module for now; split if it grows large

5. **Performance Requirements**
   - What are acceptable parse/serialize times for large documents?
   - **Proposal**: Define benchmarks once we have real-world usage data

## Related Work

- **Go JSON Libraries**: encoding/json (standard), jsoniter (fast)
- **Go CLI Libraries**: cobra, cli, kingpin
- **Similar Projects**: 
  - go-jira (JIRA Go client)
  - gh (GitHub CLI in Go)
  - todolist (various Go implementations)

## References

- vAgenda Specification: https://github.com/visionik/vAgenda
- Go Documentation: https://go.dev/doc/comment
- TRON Format: https://tron-format.github.io/
- Testify: https://github.com/stretchr/testify
- vAgenda Beads Extension: [vAgenda-extension-beads.md](./vAgenda-extension-beads.md)

## Community Feedback

This is a **draft proposal**. Feedback needed:

1. Is the package structure appropriate?
2. Are the builder patterns idiomatic Go?
3. Should extensions use embedded structs or interfaces?
4. Is the CLI command structure intuitive?
5. What additional utilities would be valuable?

**Discuss**: https://github.com/visionik/vAgenda/discussions
