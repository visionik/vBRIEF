// Package query provides filtering and querying capabilities for vBRIEF documents.
package query

import (
	"strings"

	"github.com/visionik/vBRIEF/api/go/pkg/core"
)

// TodoQuery provides filtering for TodoItems.
type TodoQuery struct {
	items []core.TodoItem
}

// NewTodoQuery creates a new query for the given items.
func NewTodoQuery(items []core.TodoItem) *TodoQuery {
	return &TodoQuery{items: items}
}

// ByStatus filters items by status.
func (q *TodoQuery) ByStatus(status core.ItemStatus) *TodoQuery {
	filtered := make([]core.TodoItem, 0, len(q.items))
	for _, item := range q.items {
		if item.Status == status {
			filtered = append(filtered, item)
		}
	}
	return &TodoQuery{items: filtered}
}

// ByTitle filters items by title substring (case-insensitive).
func (q *TodoQuery) ByTitle(substring string) *TodoQuery {
	substr := strings.ToLower(substring)
	filtered := make([]core.TodoItem, 0, len(q.items))
	for _, item := range q.items {
		if strings.Contains(strings.ToLower(item.Title), substr) {
			filtered = append(filtered, item)
		}
	}
	return &TodoQuery{items: filtered}
}

// ByTag filters items by tag.
//
// Tag support requires a metadata/tags extension which is not implemented yet.
// For now this returns an empty result.
func (q *TodoQuery) ByTag(tag string) *TodoQuery {
	_ = tag
	return &TodoQuery{items: nil}
}

// Where filters items using a custom predicate function.
func (q *TodoQuery) Where(predicate func(core.TodoItem) bool) *TodoQuery {
	filtered := make([]core.TodoItem, 0, len(q.items))
	for _, item := range q.items {
		if predicate(item) {
			filtered = append(filtered, item)
		}
	}
	return &TodoQuery{items: filtered}
}

// All returns all matching items.
func (q *TodoQuery) All() []core.TodoItem {
	return q.items
}

// First returns the first matching item, or nil if none match.
func (q *TodoQuery) First() *core.TodoItem {
	if len(q.items) > 0 {
		return &q.items[0]
	}
	return nil
}

// Count returns the number of matching items.
func (q *TodoQuery) Count() int {
	return len(q.items)
}

// Any returns true if there are any matching items.
func (q *TodoQuery) Any() bool {
	return len(q.items) > 0
}
