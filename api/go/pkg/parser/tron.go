package parser

import (
	"io"

	"github.com/tron-format/trongo/pkg/tron"
	"github.com/visionik/vAgenda/api/go/pkg/core"
)

// TRONParser parses documents in TRON format.
type TRONParser struct{}

// NewTRONParser creates a new TRON parser.
func NewTRONParser() Parser {
	return &TRONParser{}
}

// Parse reads and parses a TRON document from a reader.
func (p *TRONParser) Parse(r io.Reader) (*core.Document, error) {
	data, err := readAllLimited(r)
	if err != nil {
		return nil, err
	}
	return p.ParseBytes(data)
}

// ParseBytes parses a TRON document from a byte slice.
func (p *TRONParser) ParseBytes(data []byte) (*core.Document, error) {
	var doc core.Document
	if err := tron.Unmarshal(data, &doc); err != nil {
		return nil, err
	}
	return &doc, nil
}

// ParseString parses a TRON document from a string.
func (p *TRONParser) ParseString(s string) (*core.Document, error) {
	return p.ParseBytes([]byte(s))
}
