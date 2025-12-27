package parser

import (
	"errors"
	"fmt"
	"io"
)

const (
	// MaxDocumentSize limits how much data is read from an io.Reader when parsing.
	// This prevents unbounded memory use when parsing from untrusted sources.
	MaxDocumentSize = 10 << 20 // 10 MiB
)

var (
	ErrDocumentTooLarge = errors.New("document too large")
)

func readAllLimited(r io.Reader) ([]byte, error) {
	data, err := io.ReadAll(io.LimitReader(r, MaxDocumentSize+1))
	if err != nil {
		return nil, err
	}
	if len(data) > MaxDocumentSize {
		return nil, fmt.Errorf("%w: max=%d", ErrDocumentTooLarge, MaxDocumentSize)
	}
	return data, nil
}
