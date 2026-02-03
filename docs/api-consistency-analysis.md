# API Consistency Analysis: Go, Python, and TypeScript

**Date**: 2025-12-28  
**Purpose**: Document inconsistencies across the three vBRIEF API implementations (Go, Python, TypeScript) and provide recommendations for alignment.

## Executive Summary

All three API documentation files contain **critical type naming inconsistencies** related to the Phase→PlanItem refactoring that was completed in the Go implementation but not reflected in the documentation. Additionally, there are architectural and naming differences that should be harmonized for better cross-language consistency.

## Critical Issues (Must Fix)

### 1. Type Name Inconsistencies in All Three Docs

**Go API (`vBRIEF-extension-api-go.md`)**:
- Line 108: Uses `Phases []PlanItem` (incorrect field name - should be `Items`)
- Line 126: `Status PhaseStatus` (references non-existent type)
- Line 130: `type PlanItemStatus string` (declares wrong type name)
- Lines 133-138: Constants use `PhaseStatus` prefix instead of `PlanItemStatus`
- Lines 209-212: Builder methods use `AddPhase`, `AddPendingPhase` etc. (should be `AddPlanItem`, `AddPendingPlanItem`)

**Python API (`vBRIEF-extension-api-python.md`)**:
- Line 140: Declares `PlanItemStatus` enum (correct)
- Line 186: `status: PhaseStatus` (references wrong type, should be `PlanItemStatus`)

**TypeScript API (`vBRIEF-extension-api-typescript.md`)**:
- Line 203: `status: PhaseStatus` (references wrong type)
- Line 209: Declares `type PlanItemStatus` (correct name but inconsistent usage)

**Root cause**: Documentation was not updated during the Phase→PlanItem refactoring.

### 2. Missing Plan.items Field in Python

The Python API doc shows `Plan` without the `items` field that should contain the list of `PlanItem` objects. Go and TypeScript both show this (though Go uses incorrect name `Phases`).

## Architectural Differences (Consider Harmonizing)

### 1. Package/Module Structure

**Go** (actual implementation):
```
pkg/
├── core/           # Core types + mutation helpers
├── parser/         # JSON/TRON parsing
├── builder/        # Fluent builders
├── validator/      # Validation
├── query/          # Query/filter interfaces
├── updater/        # Validated mutations
└── convert/        # JSON/TRON conversion
```

**Python** (proposed):
```
vbrief/
├── core/           # Core types and models
├── extensions/     # Extension implementations (13 modules)
├── parser/         # Parsing
├── builder/        # Builders
├── validator/      # Validation
├── query/          # Querying
├── mutator/        # Direct mutation helpers
├── updater/        # Immutable and validated updates
└── integrations/   # Framework integrations (FastAPI, Django, etc.)
```

**TypeScript** (proposed):
```
@vbrief/
├── core/           # Core types
├── parser/         # Parsing
├── builder/        # Builders
├── validator/      # Validation
├── query/          # Querying
├── mutator/        # Mutation helpers
├── updater/        # Immutable and validated updates
├── extensions/     # Extension implementations (13 modules)
├── react/          # React hooks
├── vue/            # Vue composables
└── cli/            # CLI tool
```

**Differences**:
- Go has `convert` package (others integrate into parser)
- Python/TypeScript have separate `mutator` package (Go integrates into core)
- Python/TypeScript propose separate extension implementations (Go doesn't)
- TypeScript proposes framework-specific packages (React, Vue)

**Recommendation**: The architectural differences are appropriate for each language ecosystem. However, the **core conceptual layers** should be consistent:
- Core types
- Parser (with format conversion)
- Builder (fluent API)
- Validator (schema validation)
- Query (filtering/traversal)
- Updater (mutation with validation)

### 2. Document Wrapper Class Naming

- **Go**: No wrapper class (direct `core.Document` struct)
- **Python**: `VAgendaDocument` class
- **TypeScript**: `VAgendaDocument` class

**Issue**: "VAgenda" is not defined anywhere in the vBRIEF spec. This appears to be a legacy name.

**Recommendation**: Either:
1. Use `VContextDocument` for consistency with the spec name, or
2. Use language-idiomatic approaches:
   - Go: Continue with plain `core.Document` (idiomatic)
   - Python: `VContextDocument` or just export types directly
   - TypeScript: `VContextDocument` or export interfaces directly

### 3. Builder Method Naming

**Go**:
```go
builder.NewTodoList(version string)
  .AddItem(title, status)
  .AddPendingItem(title)
```

**Python** (implied from structure):
```python
builder.TodoListBuilder(version)
  .add_item(title, status)
  .add_pending_item(title)
```

**TypeScript** (implied):
```typescript
new TodoListBuilder(version)
  .addItem(title, status)
  .addPendingItem(title)
```

**Assessment**: Naming follows language conventions appropriately:
- Go: PascalCase methods
- Python: snake_case methods  
- TypeScript: camelCase methods

**Recommendation**: Keep language-specific naming. Document the conceptual mapping in a cross-reference table.

## Minor Inconsistencies

### 1. Optional Features Documented Differently

- **Go**: States "extensions not implemented yet" in validator
- **Python**: Shows full extension module structure (13 extensions)
- **TypeScript**: Shows full extension module structure (13 extensions)

**Recommendation**: Clarify implementation status for each language. If Python/TypeScript are proposals, mark them clearly.

### 2. Integration Features

- **Python**: Proposes integrations with FastAPI, Django, LangChain, Jupyter
- **TypeScript**: Proposes React, Vue, CLI packages
- **Go**: No framework integrations proposed

**Recommendation**: Framework integrations are appropriate and language-specific. No changes needed.

## Recommendations

### Immediate (Required)

1. **Fix all Phase/PhaseStatus references in all three docs**:
   - Replace `PhaseStatus` → `PlanItemStatus` everywhere
   - Replace `AddPhase` methods → `AddPlanItem`
   - Fix `Plan.Phases` → `Plan.Items` in Go doc
   - Add missing `items: List[PlanItem]` field to Python Plan class

2. **Review actual Go implementation alignment**:
   - Verify the Go code matches what's documented (post Phase→PlanItem refactor)
   - The doc shows code that looks outdated

3. **Clarify implementation status**:
   - Mark Python and TypeScript as "Proposal" if not implemented
   - Mark Go as "Implemented" with link to actual code

### Short-term (Recommended)

4. **Rename VAgendaDocument → VContextDocument** (or remove wrapper):
   - Update Python doc
   - Update TypeScript doc
   - Add rationale to docs

5. **Create cross-language reference table**:
   - Map equivalent concepts across languages
   - Show naming conventions (PascalCase vs snake_case vs camelCase)
   - Link from each API doc

6. **Standardize package/module organization descriptions**:
   - Use consistent terminology for equivalent packages
   - Clarify which features are "core" vs "optional" vs "framework-specific"

### Long-term (Consider)

7. **Shared schema/validation files**:
   - All three languages could reference the same JSON schemas
   - Consider generating type definitions from schemas

8. **Consistent error types and messages**:
   - Document error handling patterns for each language
   - Ensure validation errors use consistent terminology

9. **Cross-language testing matrix**:
   - Ensure all three implementations handle the same edge cases
   - Document behavioral differences when they exist

10. **Unified examples**:
    - Create the same example use case in all three languages
    - Show equivalent operations side-by-side

## Naming Convention Cross-Reference

| Concept | Go | Python | TypeScript |
|---------|-----|--------|------------|
| Package prefix | `core.` | `vbrief.` | `@vbrief/` |
| Constructor | `builder.NewTodoList()` | `TodoListBuilder()` | `new TodoListBuilder()` |
| Add method | `.AddItem()` | `.add_item()` | `.addItem()` |
| Status const | `StatusPending` | `ItemStatus.PENDING` | `"pending"` (literal type) |
| Field access | `doc.TodoList.Items` | `doc.todo_list.items` | `doc.todoList?.items` |

## Files to Update

1. `/Users/visionik/Projects/vBRIEF/vBRIEF-extension-api-go.md`
   - Lines 108, 126, 130, 133-138, 209-212

2. `/Users/visionik/Projects/vBRIEF/vBRIEF-extension-api-python.md`
   - Line 186 (status type reference)
   - Add missing `items` field to `Plan` class

3. `/Users/visionik/Projects/vBRIEF/vBRIEF-extension-api-typescript.md`
   - Line 203 (status type reference)

## Conclusion

The primary issue is **outdated documentation that doesn't reflect the Phase→PlanItem refactoring**. This is critical to fix for consistency with the v0.4 spec.

The architectural differences between languages are mostly appropriate and reflect language-specific idioms. However, establishing a clear **conceptual mapping** and **cross-reference documentation** would significantly improve the multi-language API story.

**Estimated effort**:
- Critical fixes: 1-2 hours
- Cross-reference table: 2-4 hours  
- Full harmonization: 1-2 days
