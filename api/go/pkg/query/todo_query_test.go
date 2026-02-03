package query

import (
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/visionik/vBRIEF/api/go/pkg/core"
)

func TestTodoQuery_ByStatus(t *testing.T) {
	items := []core.TodoItem{
		{Title: "Task 1", Status: core.StatusPending},
		{Title: "Task 2", Status: core.StatusInProgress},
		{Title: "Task 3", Status: core.StatusPending},
		{Title: "Task 4", Status: core.StatusCompleted},
	}

	t.Run("filters by pending status", func(t *testing.T) {
		q := NewTodoQuery(items)
		result := q.ByStatus(core.StatusPending).All()

		assert.Len(t, result, 2)
		assert.Equal(t, "Task 1", result[0].Title)
		assert.Equal(t, "Task 3", result[1].Title)
	})

	t.Run("filters by inProgress status", func(t *testing.T) {
		q := NewTodoQuery(items)
		result := q.ByStatus(core.StatusInProgress).All()

		assert.Len(t, result, 1)
		assert.Equal(t, "Task 2", result[0].Title)
	})

	t.Run("returns empty for non-matching status", func(t *testing.T) {
		q := NewTodoQuery(items)
		result := q.ByStatus(core.StatusBlocked).All()

		assert.Empty(t, result)
	})
}

func TestTodoQuery_ByTitle(t *testing.T) {
	items := []core.TodoItem{
		{Title: "Implement authentication", Status: core.StatusPending},
		{Title: "Write tests", Status: core.StatusInProgress},
		{Title: "Implement authorization", Status: core.StatusPending},
		{Title: "Deploy to production", Status: core.StatusPending},
	}

	t.Run("finds items by substring (case-insensitive)", func(t *testing.T) {
		q := NewTodoQuery(items)
		result := q.ByTitle("implement").All()

		assert.Len(t, result, 2)
		assert.Equal(t, "Implement authentication", result[0].Title)
		assert.Equal(t, "Implement authorization", result[1].Title)
	})

	t.Run("case-insensitive search", func(t *testing.T) {
		q := NewTodoQuery(items)
		result := q.ByTitle("IMPLEMENT").All()

		assert.Len(t, result, 2)
	})

	t.Run("returns empty for non-matching title", func(t *testing.T) {
		q := NewTodoQuery(items)
		result := q.ByTitle("nonexistent").All()

		assert.Empty(t, result)
	})
}

func TestTodoQuery_Where(t *testing.T) {
	items := []core.TodoItem{
		{Title: "Short", Status: core.StatusPending},
		{Title: "A much longer title", Status: core.StatusInProgress},
		{Title: "Another long title here", Status: core.StatusPending},
	}

	t.Run("filters with custom predicate", func(t *testing.T) {
		q := NewTodoQuery(items)
		result := q.Where(func(item core.TodoItem) bool {
			return len(item.Title) > 10
		}).All()

		assert.Len(t, result, 2)
		assert.Equal(t, "A much longer title", result[0].Title)
		assert.Equal(t, "Another long title here", result[1].Title)
	})
}

func TestTodoQuery_Chaining(t *testing.T) {
	items := []core.TodoItem{
		{Title: "Implement auth", Status: core.StatusPending},
		{Title: "Write tests for auth", Status: core.StatusPending},
		{Title: "Implement cache", Status: core.StatusInProgress},
		{Title: "Write tests for cache", Status: core.StatusPending},
	}

	t.Run("chains multiple filters", func(t *testing.T) {
		q := NewTodoQuery(items)
		result := q.
			ByStatus(core.StatusPending).
			ByTitle("auth").
			All()

		assert.Len(t, result, 2)
		assert.Equal(t, "Implement auth", result[0].Title)
		assert.Equal(t, "Write tests for auth", result[1].Title)
	})
}

func TestTodoQuery_First(t *testing.T) {
	items := []core.TodoItem{
		{Title: "Task 1", Status: core.StatusPending},
		{Title: "Task 2", Status: core.StatusPending},
	}

	t.Run("returns first item", func(t *testing.T) {
		q := NewTodoQuery(items)
		result := q.First()

		assert.NotNil(t, result)
		assert.Equal(t, "Task 1", result.Title)
	})

	t.Run("returns nil for empty query", func(t *testing.T) {
		q := NewTodoQuery([]core.TodoItem{})
		result := q.First()

		assert.Nil(t, result)
	})

	t.Run("returns first matching item after filter", func(t *testing.T) {
		q := NewTodoQuery(items)
		result := q.ByTitle("Task 2").First()

		assert.NotNil(t, result)
		assert.Equal(t, "Task 2", result.Title)
	})
}

func TestTodoQuery_Count(t *testing.T) {
	items := []core.TodoItem{
		{Title: "Task 1", Status: core.StatusPending},
		{Title: "Task 2", Status: core.StatusInProgress},
		{Title: "Task 3", Status: core.StatusPending},
	}

	t.Run("returns count of all items", func(t *testing.T) {
		q := NewTodoQuery(items)
		assert.Equal(t, 3, q.Count())
	})

	t.Run("returns count after filter", func(t *testing.T) {
		q := NewTodoQuery(items)
		count := q.ByStatus(core.StatusPending).Count()
		assert.Equal(t, 2, count)
	})

	t.Run("returns zero for empty query", func(t *testing.T) {
		q := NewTodoQuery([]core.TodoItem{})
		assert.Equal(t, 0, q.Count())
	})
}

func TestTodoQuery_Any(t *testing.T) {
	items := []core.TodoItem{
		{Title: "Task 1", Status: core.StatusPending},
	}

	t.Run("returns true when items exist", func(t *testing.T) {
		q := NewTodoQuery(items)
		assert.True(t, q.Any())
	})

	t.Run("returns false for empty query", func(t *testing.T) {
		q := NewTodoQuery([]core.TodoItem{})
		assert.False(t, q.Any())
	})

	t.Run("returns false after filter with no matches", func(t *testing.T) {
		q := NewTodoQuery(items)
		hasBlocked := q.ByStatus(core.StatusBlocked).Any()
		assert.False(t, hasBlocked)
	})
}
