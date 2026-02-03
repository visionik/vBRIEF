package convert

import (
	"bytes"
	"errors"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
	"github.com/visionik/vBRIEF/api/go/pkg/core"
)

func TestConverter_Convert(t *testing.T) {
	conv := NewConverter()

	doc := &core.Document{
		Info: core.Info{Version: "0.2", Author: "test"},
		TodoList: &core.TodoList{
			Items: []core.TodoItem{
				{Title: "Task 1", Status: core.StatusPending},
			},
		},
	}

	t.Run("converts to JSON", func(t *testing.T) {
		data, err := conv.Convert(doc, FormatJSON)

		require.NoError(t, err)
		require.NotEmpty(t, data)
		assert.Contains(t, string(data), "vBRIEFInfo")
		assert.Contains(t, string(data), "0.2")
		assert.Contains(t, string(data), "Task 1")
	})

	t.Run("converts to TRON", func(t *testing.T) {
		data, err := conv.Convert(doc, FormatTRON)

		require.NoError(t, err)
		require.NotEmpty(t, data)
		// TRON format should be more compact
		assert.Less(t, len(data), 500)
	})

	t.Run("returns error for unknown format", func(t *testing.T) {
		_, err := conv.Convert(doc, Format("unknown"))
		require.Error(t, err)
		assert.True(t, errors.Is(err, ErrUnknownFormat))
	})
}

type errorWriter struct{}

func (w errorWriter) Write(p []byte) (int, error) {
	_ = p
	return 0, assert.AnError
}

func TestConverter_ConvertTo(t *testing.T) {
	conv := NewConverter()

	doc := &core.Document{
		Info: core.Info{Version: "0.2"},
		TodoList: &core.TodoList{
			Items: []core.TodoItem{
				{Title: "Task", Status: core.StatusPending},
			},
		},
	}

	t.Run("writes JSON to writer", func(t *testing.T) {
		var buf bytes.Buffer
		err := conv.ConvertTo(doc, FormatJSON, &buf)

		require.NoError(t, err)
		assert.Contains(t, buf.String(), "vBRIEFInfo")
		assert.Contains(t, buf.String(), "Task")
	})

	t.Run("writes TRON to writer", func(t *testing.T) {
		var buf bytes.Buffer
		err := conv.ConvertTo(doc, FormatTRON, &buf)

		require.NoError(t, err)
		assert.NotEmpty(t, buf.String())
	})

	t.Run("returns wrapped write error", func(t *testing.T) {
		err := conv.ConvertTo(doc, FormatJSON, errorWriter{})
		require.Error(t, err)
		assert.True(t, errors.Is(err, assert.AnError))
	})
}

func TestToJSON(t *testing.T) {
	doc := &core.Document{
		Info: core.Info{Version: "0.2"},
		TodoList: &core.TodoList{
			Items: []core.TodoItem{
				{Title: "Task", Status: core.StatusPending},
			},
		},
	}

	t.Run("converts to JSON", func(t *testing.T) {
		data, err := ToJSON(doc)

		require.NoError(t, err)
		require.NotEmpty(t, data)
		assert.Contains(t, string(data), "vBRIEFInfo")
		assert.Contains(t, string(data), "todoList")
	})
}

func TestToJSONIndent(t *testing.T) {
	doc := &core.Document{
		Info: core.Info{Version: "0.2"},
		TodoList: &core.TodoList{
			Items: []core.TodoItem{
				{Title: "Task", Status: core.StatusPending},
			},
		},
	}

	t.Run("converts to indented JSON", func(t *testing.T) {
		data, err := ToJSONIndent(doc, "", "  ")

		require.NoError(t, err)
		require.NotEmpty(t, data)
		// Indented JSON should have newlines
		assert.Contains(t, string(data), "\n")
		assert.Contains(t, string(data), "  ")
	})
}

func TestToTRON(t *testing.T) {
	doc := &core.Document{
		Info: core.Info{Version: "0.2"},
		TodoList: &core.TodoList{
			Items: []core.TodoItem{
				{Title: "Task", Status: core.StatusPending},
			},
		},
	}

	t.Run("converts to TRON", func(t *testing.T) {
		data, err := ToTRON(doc)

		require.NoError(t, err)
		require.NotEmpty(t, data)
	})
}

func TestToTRONIndent(t *testing.T) {
	doc := &core.Document{
		Info: core.Info{Version: "0.2"},
		TodoList: &core.TodoList{
			Items: []core.TodoItem{
				{Title: "Task", Status: core.StatusPending},
			},
		},
	}

	t.Run("converts to indented TRON", func(t *testing.T) {
		data, err := ToTRONIndent(doc, "", "  ")

		require.NoError(t, err)
		require.NotEmpty(t, data)
	})
}

func TestRoundTrip_JSON(t *testing.T) {
	original := &core.Document{
		Info: core.Info{
			Version: "0.2",
			Author:  "test-author",
		},
		TodoList: &core.TodoList{
			Items: []core.TodoItem{
				{Title: "Task 1", Status: core.StatusPending},
				{Title: "Task 2", Status: core.StatusInProgress},
			},
		},
	}

	t.Run("JSON round-trip preserves data", func(t *testing.T) {
		// Convert to JSON
		jsonData, err := ToJSON(original)
		require.NoError(t, err)

		// This would be parsed back - we're just testing conversion works
		assert.Contains(t, string(jsonData), "Task 1")
		assert.Contains(t, string(jsonData), "Task 2")
		assert.Contains(t, string(jsonData), "test-author")
	})
}

func TestConverter_Plan(t *testing.T) {
	conv := NewConverter()

	doc := &core.Document{
		Info: core.Info{Version: "0.2"},
		Plan: &core.Plan{
			Title:  "Test Plan",
			Status: core.PlanStatusDraft,
			Narratives: map[string]string{
				"proposal": "Content",
			},
		},
	}

	t.Run("converts Plan to JSON", func(t *testing.T) {
		data, err := conv.Convert(doc, FormatJSON)

		require.NoError(t, err)
		assert.Contains(t, string(data), "plan")
		assert.Contains(t, string(data), "Test Plan")
		assert.Contains(t, string(data), "proposal")
	})

	t.Run("converts Plan to TRON", func(t *testing.T) {
		data, err := conv.Convert(doc, FormatTRON)

		require.NoError(t, err)
		require.NotEmpty(t, data)
	})
}
