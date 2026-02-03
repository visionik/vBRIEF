package parser

import (
	"encoding/json"
	"io"

	"github.com/visionik/vBRIEF/api/go/pkg/core"
)

// JSONParser parses documents in JSON format.
type JSONParser struct{}

// NewJSONParser creates a new JSON parser.
func NewJSONParser() Parser {
	return &JSONParser{}
}

// Parse reads and parses a JSON document from a reader.
func (p *JSONParser) Parse(r io.Reader) (*core.Document, error) {
	var doc core.Document
	decoder := json.NewDecoder(r)
	if err := decoder.Decode(&doc); err != nil {
		return nil, err
	}
	return &doc, nil
}

// ParseBytes parses a JSON document from a byte slice.
func (p *JSONParser) ParseBytes(data []byte) (*core.Document, error) {
	var doc core.Document
	if err := json.Unmarshal(data, &doc); err != nil {
		return nil, err
	}
	return &doc, nil
}

// ParseString parses a JSON document from a string.
func (p *JSONParser) ParseString(s string) (*core.Document, error) {
	return p.ParseBytes([]byte(s))
}
