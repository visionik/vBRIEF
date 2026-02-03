// Package core provides the core types and interfaces for vBRIEF documents.
package core

import (
	"errors"
	"fmt"
)

// Common errors for document operations.
var (
	// ErrInvalidIndex is returned when an index is out of bounds.
	ErrInvalidIndex = errors.New("invalid index")
	// ErrNarrativeNotFound is returned when a narrative key is not found.
	ErrNarrativeNotFound = errors.New("narrative not found")
	// ErrNoPlan is returned when attempting a Plan operation on a document without a Plan.
	ErrNoPlan = errors.New("document does not contain a plan")
	// ErrNoTodoList is returned when attempting a TodoList operation on a document without a TodoList.
	ErrNoTodoList = errors.New("document does not contain a todoList")
)

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

// TodoList represents a collection of actionable work items for short-term memory.
type TodoList struct {
	Items []TodoItem `json:"items" tron:"items"`
}

// TodoItem represents a single actionable task with status tracking.
type TodoItem struct {
	Title  string     `json:"title" tron:"title"`
	Status ItemStatus `json:"status" tron:"status"`
}

// ItemStatus represents the status of a todo item.
type ItemStatus string

const (
	// StatusPending indicates the item has not been started.
	StatusPending ItemStatus = "pending"
	// StatusInProgress indicates the item is currently being worked on.
	StatusInProgress ItemStatus = "inProgress"
	// StatusCompleted indicates the item has been finished.
	StatusCompleted ItemStatus = "completed"
	// StatusBlocked indicates the item cannot proceed.
	StatusBlocked ItemStatus = "blocked"
	// StatusCancelled indicates the item has been cancelled.
	StatusCancelled ItemStatus = "cancelled"
)

// IsValid returns true if the ItemStatus is a valid value.
func (s ItemStatus) IsValid() bool {
	switch s {
	case StatusPending, StatusInProgress, StatusCompleted, StatusBlocked, StatusCancelled:
		return true
	default:
		return false
	}
}

// Plan represents a structured design document for medium-term memory.
type Plan struct {
	Title      string            `json:"title" tron:"title"`
	Status     PlanStatus        `json:"status" tron:"status"`
	Narratives map[string]string `json:"narratives" tron:"narratives"`
	Items      []PlanItem        `json:"items,omitempty" tron:"items,omitempty"`
}

// PlanStatus represents the status of a plan.
type PlanStatus string

const (
	// PlanStatusDraft indicates the plan is being drafted.
	PlanStatusDraft PlanStatus = "draft"
	// PlanStatusProposed indicates the plan has been proposed for review.
	PlanStatusProposed PlanStatus = "proposed"
	// PlanStatusApproved indicates the plan has been approved.
	PlanStatusApproved PlanStatus = "approved"
	// PlanStatusInProgress indicates the plan is being executed.
	PlanStatusInProgress PlanStatus = "inProgress"
	// PlanStatusCompleted indicates the plan has been completed.
	PlanStatusCompleted PlanStatus = "completed"
	// PlanStatusCancelled indicates the plan has been cancelled.
	PlanStatusCancelled PlanStatus = "cancelled"
)

// IsValid returns true if the PlanStatus is a valid value.
func (s PlanStatus) IsValid() bool {
	switch s {
	case PlanStatusDraft, PlanStatusProposed, PlanStatusApproved,
		PlanStatusInProgress, PlanStatusCompleted, PlanStatusCancelled:
		return true
	default:
		return false
	}
}

// PlanItem represents a stage of work within a plan.
type PlanItem struct {
	Title  string          `json:"title" tron:"title"`
	Status PlanItemStatus `json:"status" tron:"status"`
}

// PlanItemStatus represents the status of a plan item.
type PlanItemStatus string

const (
	// PlanItemStatusPending indicates the plan item has not been started.
	PlanItemStatusPending PlanItemStatus = "pending"
	// PlanItemStatusInProgress indicates the plan item is currently active.
	PlanItemStatusInProgress PlanItemStatus = "inProgress"
	// PlanItemStatusCompleted indicates the plan item has been finished.
	PlanItemStatusCompleted PlanItemStatus = "completed"
	// PlanItemStatusBlocked indicates the plan item cannot proceed.
	PlanItemStatusBlocked PlanItemStatus = "blocked"
	// PlanItemStatusCancelled indicates the plan item has been cancelled.
	PlanItemStatusCancelled PlanItemStatus = "cancelled"
)

// IsValid returns true if the PlanItemStatus is a valid value.
func (s PlanItemStatus) IsValid() bool {
	switch s {
	case PlanItemStatusPending, PlanItemStatusInProgress, PlanItemStatusCompleted,
		PlanItemStatusBlocked, PlanItemStatusCancelled:
		return true
	default:
		return false
	}
}


// TodoList mutation methods

// AddItem adds an item to the TodoList.
func (tl *TodoList) AddItem(item TodoItem) {
	tl.Items = append(tl.Items, item)
}

// RemoveItem removes an item at the specified index.
func (tl *TodoList) RemoveItem(index int) error {
	if index < 0 || index >= len(tl.Items) {
		return fmt.Errorf("%w: index=%d len=%d", ErrInvalidIndex, index, len(tl.Items))
	}
	tl.Items = append(tl.Items[:index], tl.Items[index+1:]...)
	return nil
}

// UpdateItem applies updates to an item at the specified index.
func (tl *TodoList) UpdateItem(index int, updates func(*TodoItem)) error {
	if index < 0 || index >= len(tl.Items) {
		return fmt.Errorf("%w: index=%d len=%d", ErrInvalidIndex, index, len(tl.Items))
	}
	updates(&tl.Items[index])
	return nil
}

// FindItem returns the first item matching the predicate.
func (tl *TodoList) FindItem(predicate func(*TodoItem) bool) *TodoItem {
	for i := range tl.Items {
		if predicate(&tl.Items[i]) {
			return &tl.Items[i]
		}
	}
	return nil
}

// Plan mutation methods

// AddNarrative adds or updates a narrative in the Plan.
func (p *Plan) AddNarrative(key string, content string) {
	if p.Narratives == nil {
		p.Narratives = make(map[string]string)
	}
	p.Narratives[key] = content
}

// RemoveNarrative removes a narrative from the Plan.
func (p *Plan) RemoveNarrative(key string) {
	delete(p.Narratives, key)
}

// UpdateNarrative applies updates to a narrative.
func (p *Plan) UpdateNarrative(key string, updates func(*string)) error {
	content, exists := p.Narratives[key]
	if !exists {
		return fmt.Errorf("%w: key=%q", ErrNarrativeNotFound, key)
	}
	updates(&content)
	p.Narratives[key] = content
	return nil
}

// AddPlanItem adds a plan item to the Plan.
func (p *Plan) AddPlanItem(item PlanItem) {
	p.Items = append(p.Items, item)
}

// RemovePlanItem removes a plan item at the specified index.
func (p *Plan) RemovePlanItem(index int) error {
	if index < 0 || index >= len(p.Items) {
		return fmt.Errorf("%w: index=%d len=%d", ErrInvalidIndex, index, len(p.Items))
	}
	p.Items = append(p.Items[:index], p.Items[index+1:]...)
	return nil
}

// UpdatePlanItem applies updates to a plan item at the specified index.
func (p *Plan) UpdatePlanItem(index int, updates func(*PlanItem)) error {
	if index < 0 || index >= len(p.Items) {
		return fmt.Errorf("%w: index=%d len=%d", ErrInvalidIndex, index, len(p.Items))
	}
	updates(&p.Items[index])
	return nil
}
