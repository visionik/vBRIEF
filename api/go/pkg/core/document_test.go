package core

import (
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

func TestDocument_TodoListMutators(t *testing.T) {
	t.Run("AddTodoItem errors when no todo list", func(t *testing.T) {
		d := &Document{Info: Info{Version: "0.2"}}
		err := d.AddTodoItem(TodoItem{Title: "x", Status: StatusPending})
		assert.ErrorIs(t, err, ErrNoTodoList)
	})

	t.Run("UpdateTodoItemStatus errors when no todo list", func(t *testing.T) {
		d := &Document{Info: Info{Version: "0.2"}}
		err := d.UpdateTodoItemStatus(0, StatusCompleted)
		assert.ErrorIs(t, err, ErrNoTodoList)
	})

	t.Run("RemoveTodoItem errors when no todo list", func(t *testing.T) {
		d := &Document{Info: Info{Version: "0.2"}}
		err := d.RemoveTodoItem(0)
		assert.ErrorIs(t, err, ErrNoTodoList)
	})

	t.Run("UpdateTodoItem updates in-place", func(t *testing.T) {
		d := &Document{
			Info:     Info{Version: "0.2"},
			TodoList: &TodoList{Items: []TodoItem{{Title: "a", Status: StatusPending}}},
		}

		err := d.UpdateTodoItem(0, TodoItem{Title: "b", Status: StatusCompleted})
		require.NoError(t, err)
		assert.Equal(t, "b", d.TodoList.Items[0].Title)
		assert.Equal(t, StatusCompleted, d.TodoList.Items[0].Status)
	})
}

func TestDocument_PlanMutators(t *testing.T) {
	t.Run("AddPhase errors with no plan", func(t *testing.T) {
		d := &Document{Info: Info{Version: "0.2"}}
		err := d.AddPhase(Phase{Title: "p1", Status: PhaseStatusPending})
		assert.ErrorIs(t, err, ErrNoPlan)
	})

	t.Run("AddNarrative errors with no plan", func(t *testing.T) {
		d := &Document{Info: Info{Version: "0.2"}}
		err := d.AddNarrative("proposal", Narrative{Title: "t", Content: "c"})
		assert.ErrorIs(t, err, ErrNoPlan)
	})

	t.Run("UpdatePlanStatus errors with no plan", func(t *testing.T) {
		d := &Document{Info: Info{Version: "0.2"}}
		err := d.UpdatePlanStatus(PlanStatusDraft)
		assert.ErrorIs(t, err, ErrNoPlan)
	})
}
