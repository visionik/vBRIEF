// Package convert provides format conversion utilities for vBRIEF documents.
package convert

import (
	"encoding/json"
	"errors"
	"fmt"
	"io"

	"github.com/tron-format/trongo/pkg/tron"
	"github.com/visionik/vBRIEF/api/go/pkg/core"
)

var (
	// ErrUnknownFormat is returned when a converter format is not recognized.
	ErrUnknownFormat = errors.New("unknown format")
)

// Format represents an output format.
type Format string

const (
	// FormatJSON represents JSON format.
	FormatJSON Format = "json"
	// FormatTRON represents TRON format.
	FormatTRON Format = "tron"
)

// Converter handles format conversion for documents.
type Converter interface {
	// Convert converts a document to the specified format.
	Convert(doc *core.Document, format Format) ([]byte, error)

	// ConvertTo writes a document to a writer in the specified format.
	ConvertTo(doc *core.Document, format Format, w io.Writer) error
}

type converter struct{}

// NewConverter creates a new converter.
func NewConverter() Converter {
	return &converter{}
}

// Convert converts a document to the specified format.
func (c *converter) Convert(doc *core.Document, format Format) ([]byte, error) {
	switch format {
	case FormatJSON:
		return json.Marshal(doc)
	case FormatTRON:
		return tron.Marshal(doc)
	default:
		return nil, fmt.Errorf("%w: %q", ErrUnknownFormat, format)
	}
}

// ConvertTo writes a document to a writer in the specified format.
func (c *converter) ConvertTo(doc *core.Document, format Format, w io.Writer) error {
	data, err := c.Convert(doc, format)
	if err != nil {
		return err
	}
	if _, err := w.Write(data); err != nil {
		return fmt.Errorf("write: %w", err)
	}
	return nil
}

// Convert is a convenience helper that converts a document to the specified format.
func Convert(doc *core.Document, format Format) ([]byte, error) {
	return NewConverter().Convert(doc, format)
}

// ConvertTo is a convenience helper that writes a document to the specified format.
func ConvertTo(doc *core.Document, format Format, w io.Writer) error {
	return NewConverter().ConvertTo(doc, format, w)
}

// ToJSON converts a document to JSON bytes.
func ToJSON(doc *core.Document) ([]byte, error) {
	return Convert(doc, FormatJSON)
}

// ToJSONIndent converts a document to indented JSON bytes.
func ToJSONIndent(doc *core.Document, prefix, indent string) ([]byte, error) {
	return json.MarshalIndent(doc, prefix, indent)
}

// ToTRON converts a document to TRON bytes.
func ToTRON(doc *core.Document) ([]byte, error) {
	return Convert(doc, FormatTRON)
}

// ToTRONIndent converts a document to indented TRON bytes.
func ToTRONIndent(doc *core.Document, prefix, indent string) ([]byte, error) {
	return tron.MarshalIndent(doc, prefix, indent)
}
