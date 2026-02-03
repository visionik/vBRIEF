package convert

import (
	"bytes"
	"errors"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
	"github.com/visionik/vBRIEF/api/go/pkg/core"
)

func TestConvert_Helper(t *testing.T) {
	doc := &core.Document{Info: core.Info{Version: "0.2"}, TodoList: &core.TodoList{Items: []core.TodoItem{}}}

	t.Run("FormatJSON matches converter", func(t *testing.T) {
		c := NewConverter()
		want, err := c.Convert(doc, FormatJSON)
		require.NoError(t, err)

		got, err := Convert(doc, FormatJSON)
		require.NoError(t, err)
		assert.Equal(t, want, got)
	})

	t.Run("unknown format returns ErrUnknownFormat", func(t *testing.T) {
		_, err := Convert(doc, Format("bogus"))
		require.Error(t, err)
		assert.True(t, errors.Is(err, ErrUnknownFormat))
	})
}

func TestConvertTo_Helper(t *testing.T) {
	doc := &core.Document{Info: core.Info{Version: "0.2"}, TodoList: &core.TodoList{Items: []core.TodoItem{}}}

	t.Run("FormatJSON writes output", func(t *testing.T) {
		var buf bytes.Buffer
		err := ConvertTo(doc, FormatJSON, &buf)
		require.NoError(t, err)
		assert.NotEmpty(t, buf.String())
	})

	t.Run("unknown format returns ErrUnknownFormat", func(t *testing.T) {
		var buf bytes.Buffer
		err := ConvertTo(doc, Format("bogus"), &buf)
		require.Error(t, err)
		assert.True(t, errors.Is(err, ErrUnknownFormat))
	})
}
