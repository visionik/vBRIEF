// Package validator provides validation logic for vAgenda documents.
package validator

import (
	"errors"
	"fmt"

	"github.com/visionik/vAgenda/api/go/pkg/core"
)

var (
	// ErrExtensionsNotSupported is returned when extensions are requested but not implemented.
	ErrExtensionsNotSupported = errors.New("extensions not supported")
)

// ValidationError represents a single validation error.
type ValidationError struct {
	Field   string
	Message string
}

// Error returns the error message.
func (e ValidationError) Error() string {
	return fmt.Sprintf("%s: %s", e.Field, e.Message)
}

// ValidationErrors is a collection of validation errors.
type ValidationErrors []ValidationError

// Error returns a formatted error message for all validation errors.
func (e ValidationErrors) Error() string {
	if len(e) == 0 {
		return ""
	}
	result := "validation failed:"
	for _, err := range e {
		result += fmt.Sprintf("\n  - %s", err.Error())
	}
	return result
}

// Validator validates vAgenda documents.
type Validator interface {
	// Validate checks if a document is valid.
	Validate(doc *core.Document) error

	// ValidateCore checks only core requirements.
	ValidateCore(doc *core.Document) error

	// ValidateExtensions checks extension requirements.
	//
	// Extensions are not implemented yet, so this currently behaves as a safe no-op
	// beyond core validation.
	ValidateExtensions(doc *core.Document, extensions []string) error
}

type validator struct{}

// NewValidator creates a new validator.
func NewValidator() Validator {
	return &validator{}
}

// New is an alias for NewValidator for convenience.
func New() Validator {
	return NewValidator()
}

// Validate checks if a document is valid.
func (v *validator) Validate(doc *core.Document) error {
	var errors ValidationErrors

	// Validate Info
	if doc.Info.Version == "" {
		errors = append(errors, ValidationError{
			Field:   "vAgendaInfo.version",
			Message: "version is required",
		})
	}

	// Must have either TodoList or Plan, but not both
	if doc.TodoList == nil && doc.Plan == nil {
		errors = append(errors, ValidationError{
			Field:   "document",
			Message: "must contain either todoList or plan",
		})
	}

	if doc.TodoList != nil && doc.Plan != nil {
		errors = append(errors, ValidationError{
			Field:   "document",
			Message: "cannot contain both todoList and plan",
		})
	}

	// Validate TodoList if present
	if doc.TodoList != nil {
		if errs := v.validateTodoList(doc.TodoList); len(errs) > 0 {
			errors = append(errors, errs...)
		}
	}

	// Validate Plan if present
	if doc.Plan != nil {
		if errs := v.validatePlan(doc.Plan); len(errs) > 0 {
			errors = append(errors, errs...)
		}
	}

	if len(errors) > 0 {
		return errors
	}

	return nil
}

// ValidateCore checks only core requirements.
func (v *validator) ValidateCore(doc *core.Document) error {
	return v.Validate(doc)
}

// ValidateExtensions checks extension requirements.
//
// Extensions are not implemented yet. If any extensions are requested, this returns
// ErrExtensionsNotSupported.
func (v *validator) ValidateExtensions(doc *core.Document, extensions []string) error {
	if len(extensions) > 0 {
		return fmt.Errorf("%w: %v", ErrExtensionsNotSupported, extensions)
	}
	return v.Validate(doc)
}

func (v *validator) validateTodoList(list *core.TodoList) ValidationErrors {
	var errors ValidationErrors

	for i, item := range list.Items {
		if errs := v.validateTodoItem(item, i); len(errs) > 0 {
			errors = append(errors, errs...)
		}
	}

	return errors
}

func (v *validator) validateTodoItem(item core.TodoItem, index int) ValidationErrors {
	var errors ValidationErrors
	prefix := fmt.Sprintf("todoList.items[%d]", index)

	if item.Title == "" {
		errors = append(errors, ValidationError{
			Field:   prefix + ".title",
			Message: "title is required",
		})
	}

	if !item.Status.IsValid() {
		errors = append(errors, ValidationError{
			Field:   prefix + ".status",
			Message: fmt.Sprintf("invalid status: %s", item.Status),
		})
	}

	return errors
}

func (v *validator) validatePlan(plan *core.Plan) ValidationErrors {
	var errors ValidationErrors

	if plan.Title == "" {
		errors = append(errors, ValidationError{
			Field:   "plan.title",
			Message: "title is required",
		})
	}

	if !plan.Status.IsValid() {
		errors = append(errors, ValidationError{
			Field:   "plan.status",
			Message: fmt.Sprintf("invalid status: %s", plan.Status),
		})
	}

	// Proposal narrative is required
	if _, ok := plan.Narratives["proposal"]; !ok {
		errors = append(errors, ValidationError{
			Field:   "plan.narratives",
			Message: "proposal narrative is required",
		})
	}

	// Validate all narratives
	for key, narrative := range plan.Narratives {
		if narrative.Title == "" {
			errors = append(errors, ValidationError{
				Field:   fmt.Sprintf("plan.narratives.%s.title", key),
				Message: "title is required",
			})
		}
		if narrative.Content == "" {
			errors = append(errors, ValidationError{
				Field:   fmt.Sprintf("plan.narratives.%s.content", key),
				Message: "content is required",
			})
		}
	}

	// Validate phases
	for i, phase := range plan.Phases {
		if errs := v.validatePhase(phase, i); len(errs) > 0 {
			errors = append(errors, errs...)
		}
	}

	return errors
}

func (v *validator) validatePhase(phase core.Phase, index int) ValidationErrors {
	var errors ValidationErrors
	prefix := fmt.Sprintf("plan.phases[%d]", index)

	if phase.Title == "" {
		errors = append(errors, ValidationError{
			Field:   prefix + ".title",
			Message: "title is required",
		})
	}

	if !phase.Status.IsValid() {
		errors = append(errors, ValidationError{
			Field:   prefix + ".status",
			Message: fmt.Sprintf("invalid status: %s", phase.Status),
		})
	}

	return errors
}
