package query

import (
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/visionik/vAgenda/api/go/pkg/core"
)

func TestTodoQuery_ByTitle_CaseInsensitive(t *testing.T) {
	items := []core.TodoItem{
		{Title: "Fix Bug", Status: core.StatusPending},
		{Title: "write docs", Status: core.StatusPending},
	}

	q := NewTodoQuery(items)
	got := q.ByTitle("fix").All()
	assert.Len(t, got, 1)
	assert.Equal(t, "Fix Bug", got[0].Title)

	got = q.ByTitle("DOCS").All()
	assert.Len(t, got, 1)
	assert.Equal(t, "write docs", got[0].Title)
}

func TestTodoQuery_ByTag_CurrentlyEmpty(t *testing.T) {
	items := []core.TodoItem{{Title: "a", Status: core.StatusPending}}
	q := NewTodoQuery(items)
	assert.Empty(t, q.ByTag("any").All())
}
