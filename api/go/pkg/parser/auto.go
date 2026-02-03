package parser

import (
	"bytes"
	"io"
	"strings"

	"github.com/visionik/vBRIEF/api/go/pkg/core"
)

// autoParser automatically detects the format and parses accordingly.
type autoParser struct{}

// NewAutoParser creates a new auto-detecting parser.
func NewAutoParser() Parser {
	return &autoParser{}
}

// Parse reads and parses a document, auto-detecting the format.
func (p *autoParser) Parse(r io.Reader) (*core.Document, error) {
	data, err := readAllLimited(r)
	if err != nil {
		return nil, err
	}
	return p.ParseBytes(data)
}

// ParseBytes parses a document, auto-detecting the format from a byte slice.
func (p *autoParser) ParseBytes(data []byte) (*core.Document, error) {
	// Try JSON first (starts with '{')
	trimmed := bytes.TrimSpace(data)
	if len(trimmed) > 0 && trimmed[0] == '{' {
		jsonParser := NewJSONParser()
		doc, err := jsonParser.ParseBytes(data)
		if err == nil {
			return doc, nil
		}
	}

	// Fall back to TRON
	tronParser := NewTRONParser()
	return tronParser.ParseBytes(data)
}

// ParseString parses a document, auto-detecting the format from a string.
func (p *autoParser) ParseString(s string) (*core.Document, error) {
	// Try JSON first (starts with '{')
	trimmed := strings.TrimSpace(s)
	if len(trimmed) > 0 && trimmed[0] == '{' {
		jsonParser := NewJSONParser()
		doc, err := jsonParser.ParseString(s)
		if err == nil {
			return doc, nil
		}
	}

	// Fall back to TRON
	tronParser := NewTRONParser()
	return tronParser.ParseString(s)
}
