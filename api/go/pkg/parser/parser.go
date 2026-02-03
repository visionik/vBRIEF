// Package parser provides interfaces and implementations for parsing vBRIEF documents.
package parser

import (
	"errors"
	"fmt"
	"io"

	"github.com/visionik/vBRIEF/api/go/pkg/core"
)

var (
	// ErrUnknownFormat is returned when a parser format is not recognized.
	ErrUnknownFormat = errors.New("unknown format")
)

// Parser handles document parsing from various formats.
type Parser interface {
	// Parse reads a document from a reader.
	Parse(r io.Reader) (*core.Document, error)

	// ParseBytes parses a document from a byte slice.
	ParseBytes(data []byte) (*core.Document, error)

	// ParseString parses a document from a string.
	ParseString(s string) (*core.Document, error)
}

// Format represents the document format type.
type Format string

const (
	// FormatJSON represents JSON format.
	FormatJSON Format = "json"
	// FormatTRON represents TRON format.
	FormatTRON Format = "tron"
	// FormatAuto automatically detects the format.
	FormatAuto Format = "auto"
)

// New creates a new parser for the specified format.
func New(format Format) (Parser, error) {
	switch format {
	case FormatJSON:
		return NewJSONParser(), nil
	case FormatTRON:
		return NewTRONParser(), nil
	case FormatAuto:
		return NewAutoParser(), nil
	default:
		return nil, fmt.Errorf("%w: %q", ErrUnknownFormat, format)
	}
}
