package updater

import (
	"errors"

	"github.com/visionik/vAgenda/api/go/pkg/core"
	"github.com/visionik/vAgenda/api/go/pkg/validator"
)

var (
	ErrNilDocument     = errors.New("document is nil")
	ErrNoTodoList      = errors.New("document has no todo list")
	ErrNoPlan          = errors.New("document has no plan")
	ErrNoMatchingItems = errors.New("no matching items found")
)

// Updater provides validated document mutations.
//
// Updater is stateful: it is bound to a single document instance.
type Updater struct {
	doc       *core.Document
	validator validator.Validator
}

// NewUpdater creates an updater bound to a document.
func NewUpdater(doc *core.Document) *Updater {
	return &Updater{
		doc:       doc,
		validator: validator.NewValidator(),
	}
}

// WithValidator sets a custom validator.
func (u *Updater) WithValidator(v validator.Validator) *Updater {
	if v == nil {
		v = validator.NewValidator()
	}
	u.validator = v
	return u
}

// Document returns the underlying document.
func (u *Updater) Document() *core.Document {
	return u.doc
}

// Transaction executes multiple operations and validates the document once at the end.
func (u *Updater) Transaction(fn func(*Updater) error) error {
	if u.doc == nil {
		return ErrNilDocument
	}
	if err := fn(u); err != nil {
		return err
	}
	return u.validator.Validate(u.doc)
}

// UpdateItemStatus updates a todo item's status with validation.
func (u *Updater) UpdateItemStatus(index int, status core.ItemStatus) error {
	if u.doc == nil {
		return ErrNilDocument
	}
	if u.doc.TodoList == nil {
		return ErrNoTodoList
	}
	if err := u.doc.TodoList.UpdateItem(index, func(item *core.TodoItem) {
		item.Status = status
	}); err != nil {
		return err
	}
	return u.validator.Validate(u.doc)
}

// FindAndUpdate finds items by predicate and applies updates, then validates.
func (u *Updater) FindAndUpdate(predicate func(*core.TodoItem) bool, update func(*core.TodoItem)) error {
	if u.doc == nil {
		return ErrNilDocument
	}
	if u.doc.TodoList == nil {
		return ErrNoTodoList
	}

	found := false
	for i := range u.doc.TodoList.Items {
		if predicate(&u.doc.TodoList.Items[i]) {
			update(&u.doc.TodoList.Items[i])
			found = true
		}
	}

	if !found {
		return ErrNoMatchingItems
	}

	return u.validator.Validate(u.doc)
}

// AddItemValidated adds an item and validates.
func (u *Updater) AddItemValidated(item core.TodoItem) error {
	if u.doc == nil {
		return ErrNilDocument
	}
	if u.doc.TodoList == nil {
		u.doc.TodoList = &core.TodoList{}
	}
	u.doc.TodoList.AddItem(item)
	return u.validator.Validate(u.doc)
}

// RemoveItemValidated removes an item and validates.
func (u *Updater) RemoveItemValidated(index int) error {
	if u.doc == nil {
		return ErrNilDocument
	}
	if u.doc.TodoList == nil {
		return ErrNoTodoList
	}
	if err := u.doc.TodoList.RemoveItem(index); err != nil {
		return err
	}
	return u.validator.Validate(u.doc)
}

// UpdatePlanStatus updates plan status with validation.
func (u *Updater) UpdatePlanStatus(status core.PlanStatus) error {
	if u.doc == nil {
		return ErrNilDocument
	}
	if u.doc.Plan == nil {
		return ErrNoPlan
	}
	u.doc.Plan.Status = status
	return u.validator.Validate(u.doc)
}
