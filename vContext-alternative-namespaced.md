# vContext Alternative: Namespaced Extension Fields

**Status**: Proposal / Discussion Document

**Author**: vContext Project

**Date**: 2025-12-28

## Overview

This document proposes an alternative architecture for vContext where all extension fields must be grouped within their own nested objects, rather than being added directly to core types. This would provide clear namespace separation and better extensibility at the cost of increased verbosity and a breaking change from v0.4.

## Problem Statement

Currently, extension fields are added directly to core types, mixing namespaces and making it unclear which fields come from which extensions. This can lead to:

- Confusion about which fields are core vs extension
- Difficulty detecting which extensions are in use
- Potential naming conflicts between extensions
- Complex validation logic that must know about all extensions

## Current Approach (v0.4)

Extension fields are intermingled with core fields at the same level:

**JSON:**
```json
{
  "vContextInfo": {
    "version": "0.4",
    "author": "Team",
    "description": "...",
    "created": "2025-12-27T17:20:00Z",
    "updated": "2025-12-28T07:35:00Z",
    "timezone": "America/Los_Angeles",
    "metadata": {}
  }
}
```

In this example:
- `version`, `author`, `description`, `metadata` are **Core**
- `created`, `updated`, `timezone` are **Extension 1 (Timestamps)**

**TRON:**
```tron
class vContextInfo: version, author, description, created, updated, timezone, metadata

vContextInfo("0.4", "Team", "...", "2025-12-27T17:20:00Z", "2025-12-28T07:35:00Z", "America/Los_Angeles", {})
```

## Proposed Approach (Namespaced)

Each extension gets its own nested object namespace:

**JSON:**
```json
{
  "vContextInfo": {
    "version": "0.4",
    "author": "Team",
    "description": "...",
    "metadata": {},
    "time": {
      "created": "2025-12-27T17:20:00Z",
      "updated": "2025-12-28T07:35:00Z",
      "timezone": "America/Los_Angeles"
    }
  }
}
```

**TRON:**
```tron
class vContextInfo: version, author, description, metadata, time
class Time: created, updated, timezone

vContextInfo(
  "0.4",
  "Team",
  "...",
  {},
  Time("2025-12-27T17:20:00Z", "2025-12-28T07:35:00Z", "America/Los_Angeles")
)
```

## Extension Namespace Mapping

Each extension would have a designated namespace:

| Extension | Namespace | Fields |
|-----------|-----------|--------|
| Extension 1: Timestamps | `time` | created, updated, timezone, completed, dueDate, startDate |
| Extension 2: Identifiers | `identity` | id, uid, clientId |
| Extension 3: Rich Metadata | `meta` | description, notes, tags, customFields |
| Extension 4: Hierarchical | `hierarchy` | parentId, childItems, subItems, dependencies |
| Extension 5: Workflow | `workflow` | priority, effort, percentComplete, assignee |
| Extension 6: Participants | `participants` | owner, assignees, reviewers, watchers |
| Extension 7: Resources | `resources` | uris, references, attachments |
| Extension 8: Recurring | `recurrence` | recurrence, reminders |
| Extension 9: Security | `security` | classification, visibility, permissions, locks |
| Extension 10: Version Control | `versionControl` | sequence, changeLog, lastModifiedBy |
| Extension 11: Forking | `fork` | fork, mergeStatus |
| Extension 12: Playbooks | `playbook` | Already in separate spec |

## Complete Example Comparison

### TodoItem with Multiple Extensions

**Current (v0.4) - Flat structure:**

**JSON:**
```json
{
  "id": "t1",
  "uid": "8c0d8b2f-2d08-4e4a-a34f-6a21f8f8a0b1",
  "title": "Add authentication",
  "status": "inProgress",
  "description": "Implement JWT-based auth with refresh tokens",
  "created": "2025-12-28T06:55:00Z",
  "updated": "2025-12-28T07:30:00Z",
  "dueDate": "2025-12-29T02:00:00Z",
  "priority": "critical",
  "percentComplete": 40,
  "tags": ["backend", "security"],
  "dependencies": ["t0"],
  "classification": "confidential"
}
```

**TRON:**
```tron
class TodoItem: id, uid, title, status, description, created, updated, dueDate, priority, percentComplete, tags, dependencies, classification

TodoItem("t1", "8c0d8b2f-2d08-4e4a-a34f-6a21f8f8a0b1", "Add authentication", "inProgress", "Implement JWT-based auth with refresh tokens", "2025-12-28T06:55:00Z", "2025-12-28T07:30:00Z", "2025-12-29T02:00:00Z", "critical", 40, ["backend", "security"], ["t0"], "confidential")
```

**Proposed - Namespaced structure:**

**JSON:**
```json
{
  "title": "Add authentication",
  "status": "inProgress",
  "identity": {
    "id": "t1",
    "uid": "8c0d8b2f-2d08-4e4a-a34f-6a21f8f8a0b1"
  },
  "meta": {
    "description": "Implement JWT-based auth with refresh tokens",
    "tags": ["backend", "security"]
  },
  "time": {
    "created": "2025-12-28T06:55:00Z",
    "updated": "2025-12-28T07:30:00Z",
    "dueDate": "2025-12-29T02:00:00Z"
  },
  "workflow": {
    "priority": "critical",
    "percentComplete": 40
  },
  "hierarchy": {
    "dependencies": ["t0"]
  },
  "security": {
    "classification": "confidential"
  }
}
```

**TRON:**
```tron
class TodoItem: title, status, identity, meta, time, workflow, hierarchy, security
class Identity: id, uid
class Meta: description, tags
class Time: created, updated, dueDate
class Workflow: priority, percentComplete
class Hierarchy: dependencies
class Security: classification

TodoItem(
  "Add authentication",
  "inProgress",
  Identity("t1", "8c0d8b2f-2d08-4e4a-a34f-6a21f8f8a0b1"),
  Meta("Implement JWT-based auth with refresh tokens", ["backend", "security"]),
  Time("2025-12-28T06:55:00Z", "2025-12-28T07:30:00Z", "2025-12-29T02:00:00Z"),
  Workflow("critical", 40),
  Hierarchy(["t0"]),
  Security("confidential")
)
```

## Benefits

### 1. Clear Namespace Separation
Immediately obvious which fields come from which extension. No ambiguity about field ownership.

### 2. Easier Feature Detection
Can check for extension presence with simple object existence:
```javascript
if (item.time) {
  // Timestamps extension is present
  console.log(item.time.created);
}
```

### 3. Simpler Validation
Each extension can be validated independently:
```javascript
validateTimeExtension(item.time);
validateWorkflowExtension(item.workflow);
```

### 4. Better Documentation
Each extension's fields are self-contained and can be documented as a unit.

### 5. Reduced Naming Conflicts
Extension fields can't accidentally collide with core fields or other extensions. Each namespace is isolated.

### 6. Cleaner TRON Classes
Extensions define their own classes, promoting composition and reusability:
```tron
// Define once, reuse everywhere
class Time: created, updated, dueDate

// Use in TodoItem
class TodoItem: title, status, time
TodoItem("title", "status", Time(...))

// Use in Plan
class Plan: title, status, time
Plan("title", "status", Time(...))
```

### 7. Extensibility Without Conflicts
New extensions can be added without worrying about field name collisions with existing extensions.

## Costs

### 1. Breaking Change
All v0.4 documents would need migration. This would require:
- Major version bump (v1.0 or v0.5)
- Migration tools
- Transition period supporting both formats

### 2. More Verbose JSON
Additional nesting increases token count by approximately 10-15% in JSON format:
- Extra object keys: `"identity": {`, `"time": {`, etc.
- Additional closing braces

### 3. More Complex Access Patterns
Code must use deeper paths:
```javascript
// Current
item.created

// Proposed
item.time.created
```

### 4. TRON Complexity Trade-off
While TRON becomes more compositional, it also requires:
- Defining more classes upfront
- More constructor calls
- Potential increase in verbosity for simple cases

### 5. Backward Compatibility
Cannot maintain backward compatibility with v0.4 documents without transformation layer.

## Token Count Analysis

### JSON Format
Example TodoItem with 6 extensions:

**Current (flat):**
- Base fields: ~180 tokens
- Extension fields: ~120 tokens
- **Total: ~300 tokens**

**Proposed (namespaced):**
- Base fields: ~180 tokens
- Extension namespaces: ~40 tokens (6 objects)
- Extension fields: ~120 tokens
- **Total: ~340 tokens (~13% increase)**

### TRON Format
**Current (flat):**
- Class definition: ~40 tokens
- Instance: ~100 tokens
- **Total: ~140 tokens**

**Proposed (namespaced):**
- Class definitions (7 classes): ~50 tokens
- Instance: ~110 tokens
- **Total: ~160 tokens (~14% increase)**

However, with class reuse across multiple items, the amortized cost is lower:
- 10 items current: ~1,040 tokens
- 10 items namespaced: ~1,100 tokens (~6% increase with reuse)

## Migration Strategy

### If This Proposal Is Adopted

1. **Version 0.5 or 1.0**: Release with namespaced extensions
2. **Migration Tool**: Provide automated converter from v0.4 → v0.5/v1.0
3. **Dual Support Period**: Libraries support both formats for 6-12 months
4. **Documentation**: Clear migration guide with examples
5. **Deprecation**: Eventually deprecate v0.4 support

### Migration Tool Example

```javascript
function migrateToNamespaced(v04doc) {
  const v05doc = {
    vContextInfo: {
      version: "0.5",
      author: v04doc.vContextInfo.author,
      description: v04doc.vContextInfo.description,
      metadata: v04doc.vContextInfo.metadata
    }
  };
  
  // Migrate timestamp fields to time namespace
  if (v04doc.vContextInfo.created) {
    v05doc.vContextInfo.time = {
      created: v04doc.vContextInfo.created,
      updated: v04doc.vContextInfo.updated,
      timezone: v04doc.vContextInfo.timezone
    };
  }
  
  // ... migrate other extensions ...
  
  return v05doc;
}
```

## Open Questions

### 1. Commonly-Used Extensions
Should frequently-used extensions like timestamps remain flat for convenience, or does that defeat the purpose?

### 2. Optional Extension Fields
How do we handle optional fields within extension namespaces?
- Include empty objects: `"time": {}`?
- Omit entirely (cleaner but harder to detect extension intent)?

### 3. Core Metadata Field
Should the core `metadata` field be renamed to avoid confusion with the `meta` extension namespace?
- Rename to `custom`?
- Rename to `userDefined`?
- Keep as `metadata`?

### 4. Cross-Extension Consistency
Some extensions add fields to multiple types (e.g., timestamps on vContextInfo, TodoItem, Plan). Should the namespace name be consistent?
- Yes: Always `time` everywhere
- Context-aware: `documentTime` vs `itemTime`?

### 5. Ecosystem Disruption
Is the clarity and maintainability benefit worth disrupting the early ecosystem?
- Wait until v1.0 (after broader adoption)?
- Do it now while ecosystem is small (v0.5)?
- Never (keep flat structure)?

## Comparison with Other Standards

### iCalendar (RFC 5545)
Uses flat property structure:
```
BEGIN:VEVENT
UID:123
DTSTART:20251228T120000Z
DTEND:20251228T130000Z
SUMMARY:Meeting
END:VEVENT
```

### vCard (RFC 6350)
Also uses flat structure:
```
BEGIN:VCARD
VERSION:4.0
FN:John Doe
EMAIL:john@example.com
END:VCARD
```

### JSON Schema
Supports both patterns:
- Flat: Simple, direct
- Nested: With `$defs` and composition

### OpenAPI 3.0
Uses mixed approach:
- Core fields flat
- Extensions prefixed with `x-`
- Some grouping (e.g., `components`)

## Recommendation

### Conservative Path (Recommended)
**Keep flat structure for v0.4+**, document this alternative for consideration in v1.0 after:
- More real-world usage data
- Community feedback
- Implementation experience
- Token cost analysis with actual documents

### Progressive Path (Alternative)
**Adopt namespacing in v0.5** while the ecosystem is small:
- Easier to migrate now than later
- Sets better precedent for future extensions
- Clearer architecture from the start

## Conclusion

Namespaced extension fields offer significant benefits for clarity, maintainability, and extensibility. However, they come at the cost of increased verbosity and a breaking change. The decision should be made based on:

1. **Current adoption level**: How many implementations exist?
2. **Community preference**: What do early adopters prefer?
3. **Long-term vision**: Is vContext targeting maximum simplicity or maximum clarity?
4. **Token budget**: How critical is token efficiency for the target use case?

This document serves as a basis for community discussion and should be refined based on feedback from implementers and users.

---

## Appendix: Full TodoList Example

### Current (v0.4)

See Appendix A1 in README.md for the full v0.4 TodoList example.

### Proposed (Namespaced)

A full rewrite of A1 with namespaced extensions would be provided here if this proposal moves forward.
