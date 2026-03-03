# TROY: Token Reduced Object YAML

**Status**: Thought Experiment / Discussion Document

**Date**: 2025-12-28

## Overview

TROY is a hypothetical format that combines TRON's class-based schema approach with YAML's human-friendly syntax. The goal would be to achieve TRON's token efficiency while maintaining YAML's readability and familiarity.

## Core Concept

Like TRON, TROY would allow defining schemas once and then using positional or named shorthand for instances. Unlike TRON's JSON-like syntax, TROY would use YAML's indentation-based structure.

## Syntax Exploration

### Approach 1: Positional Parameters (Most TRON-like)

**Class definitions:**
```yaml
classes:
  vBRIEFInfo: [version, author, description]
  TodoList: [items]
  TodoItem: [title, status]
```

**Instance creation:**
```yaml
vBRIEFInfo: !vBRIEFInfo ["0.4", "Platform Team", "My tasks"]

todoList: !TodoList
  - !TodoItem ["Implement auth", "pending"]
  - !TodoItem ["Write docs", "pending"]
  - !TodoItem ["Deploy", "completed"]
```

**Token count**: ~60 tokens (vs ~98 in pure YAML, ~62 in TRON)

### Approach 2: Named Compact (YAML-friendly)

**Class definitions:**
```yaml
classes:
  vBRIEFInfo:
    fields: [version, author, description]
  TodoItem:
    fields: [title, status]
```

**Instance creation with positional:**
```yaml
vBRIEFInfo: !c ["0.4", "Platform Team", "My tasks"]

todoList:
  items:
    - !TodoItem ["Implement auth", "pending"]
    - !TodoItem ["Write docs", "pending"]
    - !TodoItem ["Deploy", "completed"]
```

### Approach 3: Hybrid (Readable + Compact)

**Class definitions:**
```yaml
@define:
  TodoItem: [title, status]
  vBRIEFInfo: [version, author, description]
```

**Instance creation:**
```yaml
vBRIEFInfo: @vBRIEFInfo
  - "0.4"
  - "Platform Team"
  - "My tasks"

todoList:
  items:
    - @TodoItem ["Implement auth", "pending"]
    - @TodoItem ["Write docs", "pending"]
    - @TodoItem ["Deploy", "completed"]
```

### Approach 4: YAML Tags (Most YAML-native)

Uses YAML's built-in custom type system:

**Class definitions (implied or separate schema file):**
```yaml
# schema.troy.yaml
types:
  !vBRIEFInfo:
    version: string
    author: string
    description: string
  !TodoItem:
    title: string
    status: enum
```

**Instance creation:**
```yaml
vBRIEFInfo: !vBRIEFInfo
  - "0.4"
  - "Platform Team" 
  - "My tasks"

todoList:
  items:
    - !TodoItem ["Implement auth", "pending"]
    - !TodoItem ["Write docs", "pending"]
```

## Complete Example Comparison

### Pure YAML (Baseline)

```yaml
vBRIEFInfo:
  version: "0.4"
  author: "Platform Team"
  description: "Development tasks"

todoList:
  items:
    - title: "Implement authentication"
      status: "inProgress"
      description: "Add JWT-based auth"
      priority: "critical"
      tags: ["backend", "security"]
    - title: "Write documentation"
      status: "pending"
      priority: "medium"
      tags: ["docs"]
    - title: "Deploy to staging"
      status: "completed"
      priority: "high"
      tags: ["deployment"]
```

**Token count**: ~145 tokens

### TRON (Current)

```tron
class vBRIEFInfo: version, author, description
class TodoList: items
class TodoItem: title, status, description, priority, tags

vBRIEFInfo: vBRIEFInfo("0.4", "Platform Team", "Development tasks")

todoList: TodoList([
  TodoItem("Implement authentication", "inProgress", "Add JWT-based auth", "critical", ["backend", "security"]),
  TodoItem("Write documentation", "pending", null, "medium", ["docs"]),
  TodoItem("Deploy to staging", "completed", null, "high", ["deployment"])
])
```

**Token count**: ~95 tokens

### TROY (Proposed - Approach 4)

```yaml
@schema:
  vBRIEFInfo: [version, author, description]
  TodoList: [items]
  TodoItem: [title, status, description, priority, tags]

vBRIEFInfo: !vBRIEFInfo ["0.4", "Platform Team", "Development tasks"]

todoList: !TodoList
  - !TodoItem ["Implement authentication", "inProgress", "Add JWT-based auth", "critical", ["backend", "security"]]
  - !TodoItem ["Write documentation", "pending", null, "medium", ["docs"]]
  - !TodoItem ["Deploy to staging", "completed", null, "high", ["deployment"]]
```

**Token count**: ~100 tokens

### Token Comparison

| Format | Tokens | vs YAML | vs TRON |
|--------|--------|---------|---------|
| YAML | 145 | 0% | +53% |
| TRON | 95 | -34% | 0% |
| TROY | 100 | -31% | +5% |
| JSON | 165 | +14% | +74% |

## Benefits of TROY

### 1. Familiar Syntax
YAML is already widely used and understood. Many developers are more comfortable with YAML than JSON-like syntax.

### 2. Human Readability
YAML's indentation-based structure is often considered more readable than JSON/TRON's braces.

### 3. Built-in Comments
YAML natively supports comments (`#`), unlike JSON (though TRON inherits this limitation).

### 4. Multiline Strings
YAML's native multiline string support (`|` and `>`) could make long content fields more readable:

```yaml
- !PlaybookItem
  - "Test in staging first"
  - "active"
  - |
    Always test database migrations in staging
    before running in production. This catches
    schema conflicts early.
```

### 5. Token Efficiency
Achieves ~31% token reduction vs pure YAML (though 5% more than TRON).

## Challenges with TROY

### 1. YAML Parsing Complexity
YAML parsers are notoriously complex and have edge cases. Adding custom types increases this.

### 2. Custom Type System
Would need to define and standardize the class definition syntax across YAML parsers.

### 3. Less Efficient Than TRON
TROY would likely use ~5-10% more tokens than TRON due to YAML's verbosity (indentation, dashes).

### 4. Tool Support
Would need to build parsers, validators, and converters from scratch.

### 5. YAML Gotchas
YAML has many surprising behaviors:
- Norway problem (`no` becomes `false`)
- Type coercion (dates, numbers)
- Anchor complexity
- Indentation sensitivity

### 6. Limited Adoption Incentive
If you're already using TRON (JSON-based), what's the compelling reason to switch to YAML-based?

## Positional vs Named Parameters

### Positional (More compact)
```yaml
- !TodoItem ["Fix bug", "pending", "critical"]
```
- Fewer tokens
- Less readable
- Fragile (order matters)

### Named (More explicit)
```yaml
- !TodoItem
    title: "Fix bug"
    status: "pending"
    priority: "critical"
```
- More tokens
- More readable
- Robust (order doesn't matter)
- Defeats the purpose of TROY

### Hybrid (Best of both?)
```yaml
- !TodoItem ["Fix bug", "pending"]  # Minimal required fields
    priority: "critical"             # Optional fields named
    tags: ["backend"]
```

## Integration with vBRIEF

If TROY were added to vBRIEF, it might look like:

### vBRIEF v0.5 (Hypothetical)

**Supported formats:**
1. JSON - Maximum compatibility
2. TRON - Maximum token efficiency
3. TROY - Maximum human readability with good token efficiency

**Example vBRIEF document in TROY:**

```yaml
@schema:
  vBRIEFInfo: [version, author, description]
  Playbook: [title, description, items]
  PlaybookItem: [title, status, content]

vBRIEFInfo: !vBRIEFInfo ["0.4", "vBRIEF Project", "Development practices"]

playbook: !Playbook
  - "vBRIEF Development Practices"
  - "Accumulated best practices"
  - 
    - !PlaybookItem
      - "Use task targets"
      - "active"
      - "Always use task targets for repeatable actions"
    - !PlaybookItem
      - "Follow Conventional Commits"
      - "active"
      - "All commits must follow Conventional Commits spec"
```

## Comparison with Existing Formats

### TOON (Token-Oriented Object Notation)
- CSV-like syntax
- Very compact for tabular data
- Less readable for nested structures
- TROY would be more readable but less compact

### JSON5
- JSON with comments and trailing commas
- No schema/class system
- Not focused on token reduction
- More readable than JSON, but not as compact as TROY

### YAML + JSON Schema
- Pure YAML with external schema
- No token reduction
- Standard tooling
- TROY would be more compact with inline schemas

## Recommendation

### Don't Build TROY (Yet)

**Reasons:**
1. **Diminishing returns**: TRON already achieves 35-40% token reduction. TROY's additional readability might not justify the complexity.
2. **YAML complexity**: YAML parsers are heavy and have edge cases. JSON/TRON is simpler.
3. **Ecosystem split**: Adding a third format could fragment the ecosystem.
4. **Tool burden**: Would need parsers, validators, converters for yet another format.
5. **TRON is "good enough"**: Most users who want readability can use JSON; those who want efficiency use TRON.

### If You Were to Build TROY

Wait until:
1. **Proven demand**: Multiple users specifically request YAML-based format
2. **TRON adoption**: TRON is widely adopted first, proving the class-based approach
3. **Resource availability**: Team has capacity to maintain three formats
4. **Clear use case**: Specific scenario where TROY > TRON + JSON

### Alternative: YAML-TRON Converter

Instead of a new format, provide a tool to convert TRON ↔ YAML:
- Users can edit in YAML (familiar)
- Tool converts to TRON for storage/transmission (efficient)
- Best of both worlds without format proliferation

## Conclusion

TROY is an interesting concept that could combine YAML's readability with TRON's efficiency. However, it likely isn't worth implementing because:

1. TRON already provides good token efficiency
2. JSON provides universal compatibility
3. The added complexity of YAML parsing outweighs benefits
4. The 5-10% token difference vs TRON is marginal
5. Format proliferation creates ecosystem fragmentation

**Recommendation**: Stick with JSON + TRON. If YAML support is desired, create converter tools rather than a new format.

---

## Appendix: Syntax Variations

### Option A: Sigils
```yaml
$TodoItem: [title, status]

items:
  - $TodoItem ["Fix bug", "pending"]
```

### Option B: Directives
```yaml
%define TodoItem [title, status]

items:
  - %TodoItem ["Fix bug", "pending"]
```

### Option C: Special Keys
```yaml
_classes:
  TodoItem: [title, status]

items:
  - _type: TodoItem
    _values: ["Fix bug", "pending"]
```

### Option D: YAML Anchors (Ab)use
```yaml
classes:
  TodoItem: &TodoItem [title, status]

items:
  - <<: *TodoItem
    _: ["Fix bug", "pending"]
```

None of these feel natural in YAML, suggesting that YAML might not be the right fit for class-based schemas.
