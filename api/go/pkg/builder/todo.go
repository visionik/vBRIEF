// Package builder provides fluent APIs for constructing vBRIEF documents.
package builder

import "github.com/visionik/vBRIEF/api/go/pkg/core"

// TodoListBuilder provides a fluent API for building TodoList documents.
type TodoListBuilder struct {
	doc *core.Document
}

// NewTodoList creates a new TodoList builder with the specified version.
func NewTodoList(version string) *TodoListBuilder {
	return &TodoListBuilder{
		doc: &core.Document{
			Info: core.Info{
				Version: version,
			},
			TodoList: &core.TodoList{
				Items: []core.TodoItem{},
			},
		},
	}
}

// WithAuthor sets the document author.
func (b *TodoListBuilder) WithAuthor(author string) *TodoListBuilder {
	b.doc.Info.Author = author
	return b
}

// WithDescription sets the document description.
func (b *TodoListBuilder) WithDescription(description string) *TodoListBuilder {
	b.doc.Info.Description = description
	return b
}

// WithMetadata sets a metadata value.
func (b *TodoListBuilder) WithMetadata(key string, value interface{}) *TodoListBuilder {
	if b.doc.Info.Metadata == nil {
		b.doc.Info.Metadata = make(map[string]interface{})
	}
	b.doc.Info.Metadata[key] = value
	return b
}

// AddItem adds a todo item to the list.
func (b *TodoListBuilder) AddItem(title string, status core.ItemStatus) *TodoListBuilder {
	item := core.TodoItem{
		Title:  title,
		Status: status,
	}
	b.doc.TodoList.Items = append(b.doc.TodoList.Items, item)
	return b
}

// AddPendingItem adds a pending todo item to the list.
func (b *TodoListBuilder) AddPendingItem(title string) *TodoListBuilder {
	return b.AddItem(title, core.StatusPending)
}

// AddInProgressItem adds an in-progress todo item to the list.
func (b *TodoListBuilder) AddInProgressItem(title string) *TodoListBuilder {
	return b.AddItem(title, core.StatusInProgress)
}

// AddCompletedItem adds a completed todo item to the list.
func (b *TodoListBuilder) AddCompletedItem(title string) *TodoListBuilder {
	return b.AddItem(title, core.StatusCompleted)
}

// Build returns the constructed document.
func (b *TodoListBuilder) Build() *core.Document {
	return b.doc
}
