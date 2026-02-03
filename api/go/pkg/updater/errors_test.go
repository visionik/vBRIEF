package updater

import (
	"errors"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
	"github.com/visionik/vBRIEF/api/go/pkg/core"
)

func TestUpdater_ErrorSentinels(t *testing.T) {
	t.Run("nil document", func(t *testing.T) {
		u := NewUpdater(nil)
		err := u.UpdateItemStatus(0, core.StatusCompleted)
		require.Error(t, err)
		assert.True(t, errors.Is(err, ErrNilDocument))
	})

	t.Run("no todo list", func(t *testing.T) {
		u := NewUpdater(&core.Document{Info: core.Info{Version: "0.2"}})
		err := u.UpdateItemStatus(0, core.StatusCompleted)
		require.Error(t, err)
		assert.True(t, errors.Is(err, ErrNoTodoList))
	})

	t.Run("no matching items", func(t *testing.T) {
		doc := &core.Document{Info: core.Info{Version: "0.2"}, TodoList: &core.TodoList{Items: []core.TodoItem{{Title: "a", Status: core.StatusPending}}}}
		u := NewUpdater(doc)
		err := u.FindAndUpdate(
			func(item *core.TodoItem) bool { return item.Title == "missing" },
			func(item *core.TodoItem) { item.Status = core.StatusCompleted },
		)
		require.Error(t, err)
		assert.True(t, errors.Is(err, ErrNoMatchingItems))
	})

	t.Run("no plan", func(t *testing.T) {
		u := NewUpdater(&core.Document{Info: core.Info{Version: "0.2"}})
		err := u.UpdatePlanStatus(core.PlanStatusApproved)
		require.Error(t, err)
		assert.True(t, errors.Is(err, ErrNoPlan))
	})
}
