package validator

import (
	"errors"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
	"github.com/visionik/vAgenda/api/go/pkg/core"
)

func TestValidator_ValidateTodoList(t *testing.T) {
	v := NewValidator()

	t.Run("valid TodoList passes validation", func(t *testing.T) {
		doc := &core.Document{
			Info: core.Info{Version: "0.2"},
			TodoList: &core.TodoList{
				Items: []core.TodoItem{
					{Title: "Task 1", Status: core.StatusPending},
				},
			},
		}

		err := v.Validate(doc)
		assert.NoError(t, err)
	})

	t.Run("missing version fails validation", func(t *testing.T) {
		doc := &core.Document{
			Info: core.Info{Version: ""},
			TodoList: &core.TodoList{
				Items: []core.TodoItem{},
			},
		}

		err := v.Validate(doc)
		assert.Error(t, err)
		assert.Contains(t, err.Error(), "version is required")
	})

	t.Run("missing title fails validation", func(t *testing.T) {
		doc := &core.Document{
			Info: core.Info{Version: "0.2"},
			TodoList: &core.TodoList{
				Items: []core.TodoItem{
					{Title: "", Status: core.StatusPending},
				},
			},
		}

		err := v.Validate(doc)
		assert.Error(t, err)
		assert.Contains(t, err.Error(), "title is required")
	})

	t.Run("invalid status fails validation", func(t *testing.T) {
		doc := &core.Document{
			Info: core.Info{Version: "0.2"},
			TodoList: &core.TodoList{
				Items: []core.TodoItem{
					{Title: "Task", Status: core.ItemStatus("invalid")},
				},
			},
		}

		err := v.Validate(doc)
		assert.Error(t, err)
		assert.Contains(t, err.Error(), "invalid status")
	})

	t.Run("document with neither TodoList nor Plan fails", func(t *testing.T) {
		doc := &core.Document{
			Info: core.Info{Version: "0.2"},
		}

		err := v.Validate(doc)
		assert.Error(t, err)
		assert.Contains(t, err.Error(), "must contain either todoList or plan")
	})

	t.Run("document with both TodoList and Plan fails", func(t *testing.T) {
		doc := &core.Document{
			Info:     core.Info{Version: "0.2"},
			TodoList: &core.TodoList{Items: []core.TodoItem{}},
			Plan: &core.Plan{
				Title:      "Plan",
				Status:     core.PlanStatusDraft,
				Narratives: map[string]core.Narrative{},
			},
		}

		err := v.Validate(doc)
		assert.Error(t, err)
		assert.Contains(t, err.Error(), "cannot contain both todoList and plan")
	})
}

func TestValidator_ValidatePlan(t *testing.T) {
	v := NewValidator()

	t.Run("valid Plan passes validation", func(t *testing.T) {
		doc := &core.Document{
			Info: core.Info{Version: "0.2"},
			Plan: &core.Plan{
				Title:  "Test Plan",
				Status: core.PlanStatusDraft,
				Narratives: map[string]core.Narrative{
					"proposal": {Title: "Proposal", Content: "Content"},
				},
			},
		}

		err := v.Validate(doc)
		assert.NoError(t, err)
	})

	t.Run("missing plan title fails validation", func(t *testing.T) {
		doc := &core.Document{
			Info: core.Info{Version: "0.2"},
			Plan: &core.Plan{
				Title:  "",
				Status: core.PlanStatusDraft,
				Narratives: map[string]core.Narrative{
					"proposal": {Title: "Proposal", Content: "Content"},
				},
			},
		}

		err := v.Validate(doc)
		assert.Error(t, err)
		assert.Contains(t, err.Error(), "plan.title")
	})

	t.Run("invalid plan status fails validation", func(t *testing.T) {
		doc := &core.Document{
			Info: core.Info{Version: "0.2"},
			Plan: &core.Plan{
				Title:  "Plan",
				Status: core.PlanStatus("invalid"),
				Narratives: map[string]core.Narrative{
					"proposal": {Title: "Proposal", Content: "Content"},
				},
			},
		}

		err := v.Validate(doc)
		assert.Error(t, err)
		assert.Contains(t, err.Error(), "invalid status")
	})

	t.Run("missing proposal narrative fails validation", func(t *testing.T) {
		doc := &core.Document{
			Info: core.Info{Version: "0.2"},
			Plan: &core.Plan{
				Title:      "Plan",
				Status:     core.PlanStatusDraft,
				Narratives: map[string]core.Narrative{},
			},
		}

		err := v.Validate(doc)
		assert.Error(t, err)
		assert.Contains(t, err.Error(), "proposal narrative is required")
	})

	t.Run("narrative with empty title fails validation", func(t *testing.T) {
		doc := &core.Document{
			Info: core.Info{Version: "0.2"},
			Plan: &core.Plan{
				Title:  "Plan",
				Status: core.PlanStatusDraft,
				Narratives: map[string]core.Narrative{
					"proposal": {Title: "", Content: "Content"},
				},
			},
		}

		err := v.Validate(doc)
		assert.Error(t, err)
		assert.Contains(t, err.Error(), "title is required")
	})

	t.Run("narrative with empty content fails validation", func(t *testing.T) {
		doc := &core.Document{
			Info: core.Info{Version: "0.2"},
			Plan: &core.Plan{
				Title:  "Plan",
				Status: core.PlanStatusDraft,
				Narratives: map[string]core.Narrative{
					"proposal": {Title: "Title", Content: ""},
				},
			},
		}

		err := v.Validate(doc)
		assert.Error(t, err)
		assert.Contains(t, err.Error(), "content is required")
	})
}

func TestValidator_ValidateExtensions(t *testing.T) {
	v := NewValidator()
	doc := &core.Document{Info: core.Info{Version: "0.2"}, TodoList: &core.TodoList{Items: []core.TodoItem{}}}

	t.Run("no extensions requested succeeds", func(t *testing.T) {
		err := v.ValidateExtensions(doc, nil)
		assert.NoError(t, err)
	})

	t.Run("extensions requested returns not supported", func(t *testing.T) {
		err := v.ValidateExtensions(doc, []string{"timestamps"})
		assert.Error(t, err)
		assert.True(t, errors.Is(err, ErrExtensionsNotSupported))
	})
}

func TestValidator_ValidatePhases(t *testing.T) {
	v := NewValidator()

	t.Run("valid phases pass validation", func(t *testing.T) {
		doc := &core.Document{
			Info: core.Info{Version: "0.2"},
			Plan: &core.Plan{
				Title:  "Plan",
				Status: core.PlanStatusDraft,
				Narratives: map[string]core.Narrative{
					"proposal": {Title: "Proposal", Content: "Content"},
				},
				Phases: []core.Phase{
					{Title: "Phase 1", Status: core.PhaseStatusPending},
					{Title: "Phase 2", Status: core.PhaseStatusInProgress},
				},
			},
		}

		err := v.Validate(doc)
		assert.NoError(t, err)
	})

	t.Run("phase with empty title fails validation", func(t *testing.T) {
		doc := &core.Document{
			Info: core.Info{Version: "0.2"},
			Plan: &core.Plan{
				Title:  "Plan",
				Status: core.PlanStatusDraft,
				Narratives: map[string]core.Narrative{
					"proposal": {Title: "Proposal", Content: "Content"},
				},
				Phases: []core.Phase{
					{Title: "", Status: core.PhaseStatusPending},
				},
			},
		}

		err := v.Validate(doc)
		assert.Error(t, err)
		assert.Contains(t, err.Error(), "phases[0]")
		assert.Contains(t, err.Error(), "title is required")
	})

	t.Run("phase with invalid status fails validation", func(t *testing.T) {
		doc := &core.Document{
			Info: core.Info{Version: "0.2"},
			Plan: &core.Plan{
				Title:  "Plan",
				Status: core.PlanStatusDraft,
				Narratives: map[string]core.Narrative{
					"proposal": {Title: "Proposal", Content: "Content"},
				},
				Phases: []core.Phase{
					{Title: "Phase", Status: core.PhaseStatus("invalid")},
				},
			},
		}

		err := v.Validate(doc)
		assert.Error(t, err)
		assert.Contains(t, err.Error(), "invalid status")
	})
}

func TestValidationErrors(t *testing.T) {
	t.Run("ValidationErrors implements error interface", func(t *testing.T) {
		errs := ValidationErrors{
			{Field: "field1", Message: "error1"},
			{Field: "field2", Message: "error2"},
		}

		errStr := errs.Error()
		assert.Contains(t, errStr, "validation failed")
		assert.Contains(t, errStr, "field1: error1")
		assert.Contains(t, errStr, "field2: error2")
	})

	t.Run("empty ValidationErrors returns empty string", func(t *testing.T) {
		errs := ValidationErrors{}
		assert.Equal(t, "", errs.Error())
	})

	t.Run("ValidationError formats correctly", func(t *testing.T) {
		err := ValidationError{Field: "test.field", Message: "test message"}
		assert.Equal(t, "test.field: test message", err.Error())
	})
}

func TestValidator_ValidateCore(t *testing.T) {
	v := NewValidator()

	t.Run("ValidateCore calls Validate", func(t *testing.T) {
		doc := &core.Document{
			Info: core.Info{Version: "0.2"},
			TodoList: &core.TodoList{
				Items: []core.TodoItem{
					{Title: "Task", Status: core.StatusPending},
				},
			},
		}

		err := v.ValidateCore(doc)
		assert.NoError(t, err)
	})
}

func TestValidator_MultipleErrors(t *testing.T) {
	v := NewValidator()

	t.Run("collects multiple validation errors", func(t *testing.T) {
		doc := &core.Document{
			Info: core.Info{Version: ""},
			TodoList: &core.TodoList{
				Items: []core.TodoItem{
					{Title: "", Status: core.ItemStatus("invalid")},
					{Title: "Valid", Status: core.ItemStatus("bad")},
				},
			},
		}

		err := v.Validate(doc)
		require.Error(t, err)

		errStr := err.Error()
		assert.Contains(t, errStr, "version is required")
		assert.Contains(t, errStr, "title is required")
		assert.Contains(t, errStr, "invalid status")
	})
}
