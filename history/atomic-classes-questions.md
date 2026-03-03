# Atomic Classes: Open Questions & Decisions

**Date**: 2025-12-27

## Question 1: Common Name for Contained Items

### The Pattern

Three types follow a "contained item" pattern:
- **TodoItem** - contained in TodoList
- **Phase** - contained in Plan
- **PlaybookEntry** - contained in Playbook

All are:
- Titled + Statused (core atomics)
- Discrete units that can be acted upon
- Children of a parent container
- The "many" in a one-to-many relationship

### Naming Options

#### Option A: Introduce Abstract "Entry" Concept

Rename everything to use "Entry":
```tron
# Abstract base
class ContainerEntry: Titled, Statused

# Concrete types
class TodoEntry: ContainerEntry, ...       # Rename TodoItem → TodoEntry
class PlanEntry: ContainerEntry, ...       # Rename Phase → PlanEntry  
class PlaybookEntry: ContainerEntry, ...   # Already named correctly
```

**Pros**: Consistent naming, clear abstraction
**Cons**: Breaking change, "Phase" is more intuitive than "PlanEntry"

#### Option B: Keep Names, Document Pattern

Keep existing names (TodoItem, Phase, PlaybookEntry) but document that they share a common "contained item" pattern.

Add to spec:
```markdown
### Contained Item Pattern

TodoItem, Phase, and PlaybookEntry all follow the "contained item" pattern:
- They are Titled + Statused
- They exist within a parent container
- They represent discrete, actionable units
- They can be independently referenced (when Identifiable)

All contained items share the same core atomic composition.
```

**Pros**: No breaking changes, preserves intuitive names
**Cons**: Less explicit abstraction

#### Option C: Introduce "Item" Superclass

Use "Item" as the abstract base:
```tron
# Abstract base for all contained, actionable entities
class Item: Titled, Statused

# Concrete types compose from Item
class TodoItem: Item, ...              # Already correct
class PlanItem: Item, ...              # Rename Phase → PlanItem
class PlaybookItem: Item, ...          # Rename PlaybookEntry → PlaybookItem
```

**Pros**: "Item" is intuitive, TodoItem stays the same
**Cons**: "PlaybookItem" less clear than "PlaybookEntry", "PlanItem" loses semantic meaning of "Phase"

#### Option D: Type-Specific Names with Documented Commonality

Keep all current names but add TRON inheritance:
```tron
# Define the pattern (not a concrete class, just documentation)
# ContainedItem pattern: Titled + Statused + type-specific fields

# Concrete types that follow the pattern
class TodoItem: Titled, Statused, ...
class Phase: Titled, Statused, ...
class PlaybookEntry: Titled, Statused, EventIdentifiable, ...
```

Add semantic metadata:
```tron
# Tag types that follow contained item pattern
TodoItem.pattern = "ContainedItem"
Phase.pattern = "ContainedItem"
PlaybookEntry.pattern = "ContainedItem"
```

**Pros**: No breaking changes, explicit pattern documentation
**Cons**: Not enforced at type level

### Recommendation: Option B (Keep Names, Document Pattern)

**Rationale**:
1. Existing names are semantically meaningful:
   - "TodoItem" is well understood
   - "Phase" conveys temporal/sequential meaning better than "PlanEntry"
   - "PlaybookEntry" is correct for append-only log semantics

2. Breaking changes are costly:
   - Existing implementations would need migration
   - Documentation and examples need updates
   - User confusion during transition

3. Pattern can be documented without renaming:
   - Add "Contained Item Pattern" section to spec
   - Show TRON composition for all three
   - Explain they share Titled + Statused atomics

4. Flexibility for future types:
   - New container types can use any name that fits
   - Pattern documented, not enforced by naming convention

**Implementation**:
Add to atomic classes proposal:

```markdown
## Contained Item Pattern

TodoItem, Phase, and PlaybookEntry follow a common "contained item" pattern:

**Shared characteristics:**
- MUST be Titled + Statused (core atomics)
- Exist as children of parent containers
- Represent discrete, actionable or knowledge units
- Can be independently referenced when Identifiable

**Composition:**
```tron
# All follow this base pattern
class ContainedItemBase: Titled, Statused

# Then add type-specific fields
class TodoItem: Titled, Statused, [type-specific fields]
class Phase: Titled, Statused, [type-specific fields]
class PlaybookEntry: Titled, Statused, EventIdentifiable, [type-specific fields]
```

**Containers and their items:**
- TodoList → contains → TodoItem[]
- Plan → contains → Phase[]
- Playbook → contains → PlaybookEntry[]
```

---

## Question 2: Add Tagged Atomic

### Decision: APPROVED ✓

Added `Tagged` atomic to Extension Tier (Extension 3).

### Definition

```tron
class Tagged: tags
```

**Fields**:
- `tags: string[]` (optional) - Array of categorical labels

### Applied To

ALL vBRIEF entities MAY be Tagged via Extension 3:
- TodoList
- TodoItem
- Plan
- Phase
- Playbook
- PlaybookEntry
- ProblemModel (and its children: Entity, StateVar, Action, Constraint, Goal)

### Usage Examples

```tron
# TodoItem with tags
TodoItem("Fix auth bug", "inProgress", ["security", "p0", "backend"])

# Plan with tags
Plan("Microservices", "approved", {...}, ["architecture", "q1-2025", "migration"])

# Phase with tags
Phase("Database Setup", "completed", ["infrastructure", "postgres", "migration"])

# PlaybookEntry with tags
PlaybookEntry("Test First", "active", "e1", "t1", "append", ["testing", "tdd", "best-practice"])

# Playbook with tags
Playbook("Backend Patterns", [...], ["backend", "patterns", "go"])

# ProblemModel with tags
ProblemModel("OAuth Flow", [...], ["security", "authentication", "oauth2"])
```

### Rationale

1. **Universal need**: All entities benefit from categorization
2. **Flexible filtering**: Enable queries like "show all 'security' related items"
3. **Organizational tool**: Group related entities across documents
4. **Search enablement**: Tags are primary search dimension
5. **Simple pattern**: String array is universally understood

### Integration

Tagged is part of Extension 3 (Rich Metadata), alongside:
- `Extensible` (metadata field)
- `Prioritized` (priority field)
- Type-specific fields (author, reviewers, etc.)

When Extension 3 is active, entities gain:
```tron
class EntityWithExt3: Titled, Statused, Tagged, Extensible, ...
```

### Migration

**Before** (Extension 3 without Tagged):
```javascript
TodoItem {
  title, status, description, priority, metadata
  // tags were in metadata: {"tags": ["security"]}
}
```

**After** (Extension 3 with Tagged):
```javascript
TodoItem {
  title, status, description, priority, tags, metadata
  // tags are first-class: tags: ["security", "p0"]
}
```

Legacy documents with tags in metadata remain valid; tools can migrate:
```typescript
function migrateTags(item: TodoItem) {
  if (!item.tags && item.metadata?.tags) {
    item.tags = item.metadata.tags;
    delete item.metadata.tags;
  }
}
```

---

## Summary of Decisions

1. **Contained Item Pattern**: Keep existing names (TodoItem, Phase, PlaybookEntry), document the pattern
2. **Tagged Atomic**: Added to Extension Tier, applies to ALL entities

## Next Steps

1. Update atomic-classes-proposal.md with "Contained Item Pattern" section
2. Show Tagged in all Full composition examples
3. Add tags to example TRON instances
4. Update JSON Schema to include tags in Extension 3
5. Document migration path from tags-in-metadata to first-class tags
