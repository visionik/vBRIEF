package main

import (
	"errors"
	"fmt"

	"github.com/visionik/vAgenda/api/go/pkg/convert"
	"github.com/visionik/vAgenda/api/go/pkg/core"
	"github.com/visionik/vAgenda/api/go/pkg/parser"
	"github.com/visionik/vAgenda/api/go/pkg/validator"
)

func main() {
	doc := &core.Document{Info: core.Info{Version: "0.2"}, TodoList: &core.TodoList{Items: []core.TodoItem{}}}

	fmt.Println("=== strict error behavior demo ===")

	// convert: unknown format errors
	if _, err := convert.Convert(doc, convert.Format("unknown")); err != nil {
		fmt.Printf("convert unknown format error: %v\n", err)
		fmt.Printf("errors.Is(ErrUnknownFormat)=%v\n", errors.Is(err, convert.ErrUnknownFormat))
	}

	// parser: unknown format errors
	if _, err := parser.New(parser.Format("unknown")); err != nil {
		fmt.Printf("parser unknown format error: %v\n", err)
		fmt.Printf("errors.Is(ErrUnknownFormat)=%v\n", errors.Is(err, parser.ErrUnknownFormat))
	}

	// validator: extensions not supported
	v := validator.NewValidator()
	if err := v.ValidateExtensions(doc, []string{"timestamps"}); err != nil {
		fmt.Printf("validate extensions error: %v\n", err)
		fmt.Printf("errors.Is(ErrExtensionsNotSupported)=%v\n", errors.Is(err, validator.ErrExtensionsNotSupported))
	}
}
