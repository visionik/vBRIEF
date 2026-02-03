package updater

import (
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
	"github.com/visionik/vBRIEF/api/go/pkg/core"
)

func TestNewUpdater_Stateful(t *testing.T) {
	doc := &core.Document{
		Info:     core.Info{Version: "0.2"},
		TodoList: &core.TodoList{Items: []core.TodoItem{}},
	}

	u := NewUpdater(doc)
	require.NotNil(t, u)
	assert.Equal(t, doc, u.Document())
}

func TestUpdater_AddItemValidated(t *testing.T) {
	doc := &core.Document{
		Info:     core.Info{Version: "1.0"},
		TodoList: &core.TodoList{},
	}

	u := NewUpdater(doc)
	err := u.AddItemValidated(core.TodoItem{Title: "Task 1", Status: core.StatusPending})
	require.NoError(t, err)
	assert.Len(t, doc.TodoList.Items, 1)

	err = u.AddItemValidated(core.TodoItem{Title: "Task 2", Status: core.StatusPending})
	require.NoError(t, err)
	assert.Len(t, doc.TodoList.Items, 2)
}

func TestUpdater_AddItemValidatedValidationError(t *testing.T) {
	doc := &core.Document{
		Info:     core.Info{Version: "1.0"},
		TodoList: &core.TodoList{},
		Plan:     &core.Plan{},
	}

	u := NewUpdater(doc)
	err := u.AddItemValidated(core.TodoItem{Title: "Task 1", Status: core.StatusPending})
	assert.Error(t, err)
}

func TestUpdater_RemoveItemValidated(t *testing.T) {
	doc := &core.Document{
		Info: core.Info{Version: "1.0"},
		TodoList: &core.TodoList{Items: []core.TodoItem{
			{Title: "Task 1", Status: core.StatusPending},
			{Title: "Task 2", Status: core.StatusPending},
		}},
	}

	u := NewUpdater(doc)
	err := u.RemoveItemValidated(0)
	require.NoError(t, err)
	assert.Len(t, doc.TodoList.Items, 1)
	assert.Equal(t, "Task 2", doc.TodoList.Items[0].Title)

	err = u.RemoveItemValidated(5)
	assert.Error(t, err)
}

func TestUpdater_UpdateItemStatus(t *testing.T) {
	doc := &core.Document{
		Info:     core.Info{Version: "0.2"},
		TodoList: &core.TodoList{Items: []core.TodoItem{{Title: "a", Status: core.StatusPending}}},
	}

	u := NewUpdater(doc)
	err := u.UpdateItemStatus(0, core.StatusCompleted)
	require.NoError(t, err)
	assert.Equal(t, core.StatusCompleted, doc.TodoList.Items[0].Status)
}

func TestUpdater_FindAndUpdate(t *testing.T) {
	doc := &core.Document{
		Info:     core.Info{Version: "0.2"},
		TodoList: &core.TodoList{Items: []core.TodoItem{{Title: "a", Status: core.StatusPending}}},
	}

	u := NewUpdater(doc)
	err := u.FindAndUpdate(
		func(item *core.TodoItem) bool { return item.Title == "a" },
		func(item *core.TodoItem) { item.Status = core.StatusInProgress },
	)
	require.NoError(t, err)
	assert.Equal(t, core.StatusInProgress, doc.TodoList.Items[0].Status)
}

func TestUpdater_Transaction(t *testing.T) {
	doc := &core.Document{
		Info:     core.Info{Version: "0.2"},
		TodoList: &core.TodoList{Items: []core.TodoItem{}},
	}

	u := NewUpdater(doc)
	err := u.Transaction(func(u *Updater) error {
		return u.AddItemValidated(core.TodoItem{Title: "x", Status: core.StatusPending})
	})
	require.NoError(t, err)
	assert.Len(t, doc.TodoList.Items, 1)
}

func TestUpdater_AddUpdateRemovePlanNarratives(t *testing.T) {
	doc := &core.Document{
		Info: core.Info{Version: "1.0"},
		Plan: &core.Plan{
			Title:  "Test Plan",
			Status: core.PlanStatusDraft,
			Narratives: map[string]string{
				"proposal": "Content",
			},
		},
	}

	u := NewUpdater(doc)
	err := u.Transaction(func(u *Updater) error {
		doc.Plan.AddNarrative("overview", "Content")
		return nil
	})
	require.NoError(t, err)
	assert.Len(t, doc.Plan.Narratives, 2)

	err = u.Transaction(func(u *Updater) error {
		doc.Plan.Narratives["overview"] = "Updated"
		return nil
	})
	require.NoError(t, err)
	assert.Equal(t, "Updated", doc.Plan.Narratives["overview"])

	err = u.Transaction(func(u *Updater) error {
		doc.Plan.RemoveNarrative("overview")
		return nil
	})
	require.NoError(t, err)
	assert.Len(t, doc.Plan.Narratives, 1)
	_, exists := doc.Plan.Narratives["overview"]
	assert.False(t, exists)
}

func TestUpdater_PlanPhaseMutationsViaTransaction(t *testing.T) {
	doc := &core.Document{
		Info: core.Info{Version: "1.0"},
		Plan: &core.Plan{
			Title:      "Test Plan",
			Status:     core.PlanStatusDraft,
			Narratives: map[string]string{"proposal": "Content"},
			Items: []core.PlanItem{
				{Title: "Phase 1", Status: core.PlanItemStatusPending},
				{Title: "Phase 2", Status: core.PlanItemStatusPending},
			},
		},
	}

	u := NewUpdater(doc)

	// Add phase and validate
	err := u.Transaction(func(u *Updater) error {
		doc.Plan.AddPlanItem(core.PlanItem{Title: "Phase 3", Status: core.PlanItemStatusPending})
		return nil
	})
	require.NoError(t, err)
	assert.Len(t, doc.Plan.Items, 3)

	// Update phase and validate
	err = u.Transaction(func(u *Updater) error {
		return doc.Plan.UpdatePlanItem(0, func(p *core.PlanItem) {
			p.Status = core.PlanItemStatusCompleted
		})
	})
	require.NoError(t, err)
	assert.Equal(t, core.PlanItemStatusCompleted, doc.Plan.Items[0].Status)

	// Remove phase and validate
	err = u.Transaction(func(u *Updater) error {
		return doc.Plan.RemovePlanItem(1)
	})
	require.NoError(t, err)
	assert.Len(t, doc.Plan.Items, 2)
}
