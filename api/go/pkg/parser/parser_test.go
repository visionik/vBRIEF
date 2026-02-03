package parser

import (
	"bytes"
	"strings"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
	"github.com/visionik/vBRIEF/api/go/pkg/core"
)

const validJSON = `{
  "vBRIEFInfo": {
    "version": "0.2",
    "author": "test-author"
  },
  "todoList": {
    "items": [
      {
        "title": "Task 1",
        "status": "pending"
      },
      {
        "title": "Task 2",
        "status": "inProgress"
      }
    ]
  }
}`

const validPlanJSON = `{
  "vBRIEFInfo": {
    "version": "0.2"
  },
  "plan": {
    "title": "Test Plan",
    "status": "draft",
    "narratives": {
      "proposal": "Test content"
    }
  }
}`

func TestJSONParser(t *testing.T) {
	parser := NewJSONParser()

	t.Run("parses valid TodoList JSON", func(t *testing.T) {
		doc, err := parser.ParseString(validJSON)

		require.NoError(t, err)
		require.NotNil(t, doc)
		assert.Equal(t, "0.2", doc.Info.Version)
		assert.Equal(t, "test-author", doc.Info.Author)
		require.NotNil(t, doc.TodoList)
		assert.Len(t, doc.TodoList.Items, 2)
		assert.Equal(t, "Task 1", doc.TodoList.Items[0].Title)
		assert.Equal(t, core.StatusPending, doc.TodoList.Items[0].Status)
	})

	t.Run("parses valid Plan JSON", func(t *testing.T) {
		doc, err := parser.ParseString(validPlanJSON)

		require.NoError(t, err)
		require.NotNil(t, doc)
		assert.Equal(t, "0.2", doc.Info.Version)
		require.NotNil(t, doc.Plan)
		assert.Equal(t, "Test Plan", doc.Plan.Title)
		assert.Equal(t, core.PlanStatusDraft, doc.Plan.Status)
		assert.Len(t, doc.Plan.Narratives, 1)
	})

	t.Run("parses from reader", func(t *testing.T) {
		reader := strings.NewReader(validJSON)
		doc, err := parser.Parse(reader)

		require.NoError(t, err)
		require.NotNil(t, doc)
		assert.Equal(t, "0.2", doc.Info.Version)
	})

	t.Run("parses from bytes", func(t *testing.T) {
		doc, err := parser.ParseBytes([]byte(validJSON))

		require.NoError(t, err)
		require.NotNil(t, doc)
		assert.Equal(t, "0.2", doc.Info.Version)
	})

	t.Run("returns error for invalid JSON", func(t *testing.T) {
		_, err := parser.ParseString("invalid json")
		assert.Error(t, err)
	})

	t.Run("returns error for empty string", func(t *testing.T) {
		_, err := parser.ParseString("")
		assert.Error(t, err)
	})
}

func TestAutoParser(t *testing.T) {
	parser := NewAutoParser()

	t.Run("detects and parses JSON", func(t *testing.T) {
		doc, err := parser.ParseString(validJSON)

		require.NoError(t, err)
		require.NotNil(t, doc)
		assert.Equal(t, "0.2", doc.Info.Version)
		assert.Equal(t, "test-author", doc.Info.Author)
	})

	t.Run("handles leading whitespace in JSON", func(t *testing.T) {
		jsonWithWhitespace := "  \n  " + validJSON
		doc, err := parser.ParseString(jsonWithWhitespace)

		require.NoError(t, err)
		require.NotNil(t, doc)
		assert.Equal(t, "0.2", doc.Info.Version)
	})

	t.Run("parses from bytes", func(t *testing.T) {
		doc, err := parser.ParseBytes([]byte(validJSON))

		require.NoError(t, err)
		require.NotNil(t, doc)
		assert.Equal(t, "0.2", doc.Info.Version)
	})
}

func TestTRONParser(t *testing.T) {
	parser := NewTRONParser()

	// Note: TRON parsing is tested via integration in examples
	// The trongo library handles TRON format parsing
	t.Run("creates TRON parser", func(t *testing.T) {
		assert.NotNil(t, parser)
	})

	t.Run("returns error for invalid TRON", func(t *testing.T) {
		_, err := parser.ParseString("invalid tron")
		assert.Error(t, err)
	})
}

func TestAutoParser_Parse(t *testing.T) {
	parser := NewAutoParser()

	t.Run("parses from reader detecting JSON", func(t *testing.T) {
		reader := strings.NewReader(validJSON)
		doc, err := parser.Parse(reader)

		require.NoError(t, err)
		require.NotNil(t, doc)
		assert.Equal(t, "0.2", doc.Info.Version)
	})

	t.Run("parses from reader with whitespace", func(t *testing.T) {
		reader := strings.NewReader("  \n" + validJSON)
		doc, err := parser.Parse(reader)

		require.NoError(t, err)
		require.NotNil(t, doc)
		assert.Equal(t, "0.2", doc.Info.Version)
	})

	t.Run("returns error when input exceeds MaxDocumentSize", func(t *testing.T) {
		big := bytes.Repeat([]byte("a"), MaxDocumentSize+1)
		_, err := parser.Parse(bytes.NewReader(big))
		require.Error(t, err)
		assert.ErrorIs(t, err, ErrDocumentTooLarge)
	})
}

func TestTRONParser_Parse_Limits(t *testing.T) {
	p := NewTRONParser()
	big := bytes.Repeat([]byte("a"), MaxDocumentSize+1)
	_, err := p.Parse(bytes.NewReader(big))
	require.Error(t, err)
	assert.ErrorIs(t, err, ErrDocumentTooLarge)
}

func TestNew(t *testing.T) {
	tests := []struct {
		name   string
		format Format
		want   string
	}{
		{"JSON format", FormatJSON, "*parser.JSONParser"},
		{"TRON format", FormatTRON, "*parser.TRONParser"},
		{"Auto format", FormatAuto, "auto"},
		{"Unknown format errors", Format("unknown"), ""},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			p, err := New(tt.format)
			if tt.name == "Unknown format errors" {
				assert.Error(t, err)
				assert.Nil(t, p)
				return
			}
			require.NoError(t, err)
			assert.NotNil(t, p)
		})
	}
}
