# Go API Performance Analysis

**Date**: 2025-12-28  
**Purpose**: Analyze potential bottlenecks in the vBRIEF Go API implementation and identify opportunities for optimization.

## Executive Summary

The Go API implementation shows **solid performance characteristics** with no O(n²) algorithms or significant bottlenecks identified. The codebase follows Go best practices including:
- Pre-allocated slices where capacity is known
- Streaming JSON parsing via `json.Decoder`
- Document size limits to prevent unbounded memory allocation
- Efficient linear-time operations throughout

**No immediate performance work is required.** However, profiling would be beneficial before production deployment at scale.

## Detailed Analysis

### 1. Parser Performance (`pkg/parser/`)

#### JSON Parser (`json.go`)
**Assessment**: ✅ **Excellent**

```go
func (p *JSONParser) Parse(r io.Reader) (*core.Document, error) {
    decoder := json.NewDecoder(r)  // Streaming decoder
    if err := decoder.Decode(&doc); err != nil {
        return nil, err
    }
    return &doc, nil
}
```

**Complexity**: O(n) where n = document size  
**Memory**: O(n) for document structure  

**Strengths**:
- Uses streaming `json.Decoder` instead of `json.Unmarshal` for `io.Reader`
- No unnecessary copies or allocations
- Standard library performance (highly optimized)

#### Size Limits (`limits.go`)
**Assessment**: ✅ **Excellent**

```go
const MaxDocumentSize = 10 << 20 // 10 MiB

func readAllLimited(r io.Reader) ([]byte, error) {
    data, err := io.ReadAll(io.LimitReader(r, MaxDocumentSize+1))
    if len(data) > MaxDocumentSize {
        return nil, fmt.Errorf("%w: max=%d", ErrDocumentTooLarge, MaxDocumentSize)
    }
    return data, nil
}
```

**Complexity**: O(n) with hard cap at 10MB  
**Memory**: O(1) protection against DoS

**Strengths**:
- Prevents unbounded memory allocation
- Graceful error handling
- Reasonable 10MB default limit

**Considerations**:
- For very large plans (thousands of items), 10MB might be restrictive
- Consider making limit configurable: `parser.WithMaxSize(20 << 20)`

### 2. Validator Performance (`pkg/validator/`)

#### Core Validation
**Assessment**: ✅ **Good** (O(n) with some allocation overhead)

```go
func (v *validator) validateTodoList(list *core.TodoList) ValidationErrors {
    var errors ValidationErrors
    for i, item := range list.Items {
        if errs := v.validateTodoItem(item, i); len(errs) > 0 {
            errors = append(errors, errs...)
        }
    }
    return errors
}
```

**Complexity**: O(n) for n items  
**Memory**: O(e) for e validation errors

**Strengths**:
- Single pass through all items
- No nested loops
- Clear error reporting

**Minor optimization opportunity**:
```go
// Current: errors slice may reallocate multiple times
var errors ValidationErrors

// Consider pre-allocating if typical error count is known:
errors := make(ValidationErrors, 0, len(list.Items)/10) // assume ~10% error rate
```

Impact: Minimal (only matters for very large documents with many errors)

#### Narrative Validation
**Assessment**: ✅ **Good**

```go
for key, narrative := range plan.Narratives {
    if narrative.Title == "" { /* ... */ }
    if narrative.Content == "" { /* ... */ }
}
```

**Complexity**: O(k) for k narratives (typically small, <10)  
**Memory**: O(1) per iteration

**Strengths**: Map iteration is efficient in Go

### 3. Query Performance (`pkg/query/`)

#### Filter Operations
**Assessment**: ✅ **Excellent**

```go
func (q *TodoQuery) ByStatus(status core.ItemStatus) *TodoQuery {
    filtered := make([]core.TodoItem, 0, len(q.items)) // Pre-allocated!
    for _, item := range q.items {
        if item.Status == status {
            filtered = append(filtered, item)
        }
    }
    return &TodoQuery{items: filtered}
}
```

**Complexity**: O(n) per filter operation  
**Memory**: O(n) worst case (all items match)

**Strengths**:
- Pre-allocates slice with capacity
- Single pass through items
- Immutable query pattern (returns new query)

**Chain complexity**:
```go
query.ByStatus(StatusPending).ByTitle("test").Count()
// O(n) + O(m) where m ≤ n
// Total: O(n) linear with original size
```

#### String Search
**Assessment**: ✅ **Good**

```go
func (q *TodoQuery) ByTitle(substring string) *TodoQuery {
    substr := strings.ToLower(substring)  // Convert once
    for _, item := range q.items {
        if strings.Contains(strings.ToLower(item.Title), substr) {
            // ...
        }
    }
}
```

**Complexity**: O(n×m) where m = average title length  
**Memory**: O(n) for allocations in `ToLower`

**Strengths**:
- Converts query substring once (not per item)
- Case-insensitive matching

**Potential optimization**:
For very large lists (>10k items) with frequent queries, consider:
- Pre-computed lowercase title cache
- Full-text search index (e.g., using `bleve`)
- Only beneficial if profiling shows this as a bottleneck

### 4. Updater Performance (`pkg/updater/`)

#### Update Operations
**Assessment**: ✅ **Excellent**

```go
func (u *Updater) UpdateItemStatus(index int, status core.ItemStatus) error {
    // Direct index access: O(1)
    if err := u.doc.TodoList.UpdateItem(index, func(item *core.TodoItem) {
        item.Status = status
    }); err != nil {
        return err
    }
    return u.validator.Validate(u.doc)  // O(n) validation
}
```

**Complexity**: O(1) for update + O(n) for validation  
**Memory**: O(1)

**Strengths**:
- Direct index access (no search)
- In-place mutation
- Full validation after change

#### Transaction Pattern
**Assessment**: ✅ **Excellent**

```go
func (u *Updater) Transaction(fn func(*Updater) error) error {
    if err := fn(u); err != nil {
        return err
    }
    return u.validator.Validate(u.doc)  // Validate once at end
}
```

**Complexity**: O(k) operations + O(n) single validation  
**Memory**: O(1)

**Strengths**:
- Validates once instead of k times
- Reduces validation overhead for batch updates
- Excellent design pattern

#### FindAndUpdate
**Assessment**: ✅ **Good**

```go
func (u *Updater) FindAndUpdate(predicate func(*core.TodoItem) bool, update func(*core.TodoItem)) error {
    found := false
    for i := range u.doc.TodoList.Items {  // No copies
        if predicate(&u.doc.TodoList.Items[i]) {
            update(&u.doc.TodoList.Items[i])
            found = true
        }
    }
    return u.validator.Validate(u.doc)
}
```

**Complexity**: O(n) scan + O(u) updates + O(n) validation = O(n)  
**Memory**: O(1) (operates on pointers)

**Strengths**:
- Single pass through items
- No allocations in hot path
- Pointer usage avoids copies

### 5. Core Document Operations (`pkg/core/document.go`)

#### Add/Remove Operations
**Assessment**: ⚠️ **Good** (one minor concern)

```go
// Efficient add (amortized O(1))
func (d *Document) AddPlanItem(item PlanItem) error {
    d.Plan.Items = append(d.Plan.Items, item)
    return nil
}

// Less efficient remove (O(n))
func (d *Document) RemovePlanItem(index int) error {
    d.Plan.Items = append(d.Plan.Items[:index], d.Plan.Items[index+1:]...)
    return nil
}
```

**Complexity**:
- Add: O(1) amortized
- Remove: O(n) due to slice re-slicing

**Memory**:
- Add: O(1) unless slice needs reallocation
- Remove: O(n) for new slice allocation

**Analysis**:
- Remove operation creates new backing array
- For frequent removals from large slices, this could be O(n²)
- **However**: TodoLists/Plans are typically small (<1000 items)
- This is the correct Go idiom for slice element removal

**When this could matter**:
- Removing many items sequentially from large list
- Example: Removing 100 items from 1000-item list = ~50k operations

**Potential optimization** (only if profiling shows bottleneck):
```go
// Mark-and-sweep approach for bulk deletes
func (d *Document) RemovePlanItems(indices []int) error {
    // Sort indices in descending order, remove back-to-front
    // Reduces reallocations
}
```

### 6. Memory Allocation Patterns

#### Builder Pattern
**Assessment**: ✅ **Excellent**

```go
func (b *TodoListBuilder) AddItem(title string, status core.ItemStatus) *TodoListBuilder {
    b.doc.TodoList.Items = append(b.doc.TodoList.Items, core.TodoItem{
        Title:  title,
        Status: status,
    })
    return b
}
```

**Strengths**:
- Fluent API doesn't allocate extra builders
- Returns self pointer (no copies)
- Items appended directly to slice

**Consideration**: If typical list size is known, could pre-allocate:
```go
func NewTodoList(version string, capacity int) *TodoListBuilder {
    items := make([]TodoItem, 0, capacity)
    // ...
}
```

## Algorithmic Complexity Summary

| Operation | Complexity | Memory | Notes |
|-----------|-----------|--------|-------|
| Parse JSON | O(n) | O(n) | n = document bytes |
| Validate document | O(n) | O(e) | n = items, e = errors |
| Filter by status | O(n) | O(m) | m = matching items |
| Filter by title | O(n×k) | O(n) | k = avg title length |
| Update by index | O(1) | O(1) | Plus O(n) validation |
| Find and update | O(n) | O(1) | Pointer-based |
| Add item | O(1)† | O(1) | †amortized |
| Remove item | O(n) | O(n) | Slice re-slicing |
| Transaction (k ops) | O(k×f + n) | O(1) | f = per-op, n = validation |

**No O(n²) algorithms identified.**

## Benchmarking Recommendations

While no critical issues were found, profiling would provide concrete data:

### 1. CPU Profiling
```bash
go test -cpuprofile=cpu.prof -bench=. ./...
go tool pprof cpu.prof
```

**Focus areas**:
- JSON parsing for 10MB documents
- Validation with 10k+ items
- Query chains with multiple filters
- Bulk update operations

### 2. Memory Profiling
```bash
go test -memprofile=mem.prof -bench=. ./...
go tool pprof mem.prof
```

**Focus areas**:
- Allocations in query chains
- ValidationErrors slice growth
- Builder pattern overhead

### 3. Benchmark Scenarios
```go
func BenchmarkParseDocument(b *testing.B)
func BenchmarkValidate1kItems(b *testing.B)
func BenchmarkValidate10kItems(b *testing.B)
func BenchmarkQueryChain(b *testing.B)
func BenchmarkBulkUpdate(b *testing.B)
func BenchmarkTransaction100Ops(b *testing.B)
```

### 4. Stress Test Cases
- 10k todo items
- 1k plan items with 100 narratives each
- 1000 concurrent document parses
- 10MB TRON document parsing

## Optimization Opportunities (By Priority)

### Low Priority (Nice to have)

1. **Configurable size limits**
   ```go
   parser.WithMaxSize(20 << 20)
   parser.WithMaxItems(100_000)
   ```

2. **Pre-allocate validation errors**
   ```go
   errors := make(ValidationErrors, 0, estimatedErrors)
   ```

3. **Builder capacity hints**
   ```go
   NewTodoListWithCapacity(version, expectedItems)
   ```

4. **Bulk delete optimization**
   ```go
   RemovePlanItems(indices []int) // Back-to-front removal
   ```

### Not Recommended (Unless Profiling Shows Bottleneck)

- ❌ Custom JSON parser (stdlib is highly optimized)
- ❌ Search index for title queries (overhead not worth it for <10k items)
- ❌ Object pooling (Go GC is efficient for these workloads)
- ❌ Unsafe pointer tricks (breaks API safety guarantees)

## Conclusion

**The Go API has excellent performance characteristics:**
- ✅ All operations are O(n) or better
- ✅ No algorithmic bottlenecks
- ✅ Pre-allocation used where beneficial
- ✅ Document size limits prevent DoS
- ✅ Transaction pattern optimizes batch operations

**Recommendations**:
1. Run benchmark suite before v1.0 release
2. Add CPU/memory profiling to CI for regression detection
3. Document performance expectations in API docs (e.g., "suitable for documents up to 10k items")
4. Consider adding configurable size limits for power users

**Estimated performance** (based on analysis, not profiling):
- Parse 1MB document: <10ms
- Validate 1000 items: <1ms
- Query 10k items: <5ms
- Update operation: <1ms (plus validation)

**No performance work is blocking for production use.**
