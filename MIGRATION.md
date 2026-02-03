# Migration Guide: vBRIEF v0.4 → v0.5

**Date**: 2026-02-03  
**Status**: Final

## Overview

vBRIEF v0.5 represents a major architectural refactor that unifies todos, plans, and playbooks into a single Plan model with DAG capabilities. This guide helps you migrate existing v0.4 documents.

## Breaking Changes Summary

| Change | Impact | Migration Path |
|--------|--------|----------------|
| TodoList removed | All TodoList documents invalid | Convert to minimal Plan |
| Playbook removed | All Playbook documents invalid | Convert to Plan with narratives |
| Plan.narratives optional | No breaking change | Works as-is |
| dependencies field removed | EdgesMigration required if used | Convert to edges with type="blocks" |
| PlanItem.todoList removed | Nested lists broken | Use subItems or planRef |
| inProgress → running | Status enum changed | Update all statuses |
| narratives keys now TitleCase | SHOULD requirement | Rename keys (optional) |

## Quick Migration Checklist

- [ ] Update `vBRIEFInfo.version` from `"0.4"` to `"0.5"`
- [ ] Convert any `todoList` to `plan`
- [ ] Convert any `playbook` to `plan` with retrospective narratives
- [ ] Change all `inProgress` status values to `running`
- [ ] Convert `dependencies` arrays to `edges` with `type: "blocks"`
- [ ] Remove `PlanItem.todoList` fields (use `subItems` or `planRef`)
- [ ] Optionally: Convert narrative keys to TitleCase

## Detailed Migration Steps

### 1. TodoList → Plan

**v0.4 TodoList:**
```json
{
  "vBRIEFInfo": {"version": "0.4"},
  "todoList": {
    "items": [
      {"title": "Fix bug", "status": "pending"},
      {"title": "Review PR", "status": "inProgress"}
    ]
  }
}
```

**v0.5 Plan:**
```json
{
  "vBRIEFInfo": {"version": "0.5"},
  "plan": {
    "title": "Tasks",
    "status": "running",
    "items": [
      {"title": "Fix bug", "status": "pending"},
      {"title": "Review PR", "status": "running"}
    ]
  }
}
```

**Changes:**
- `todoList` → `plan`
- Add required `plan.title` (choose any descriptive name)
- Add required `plan.status` (typically `"running"` or `"draft"`)
- `inProgress` → `running`

### 2. Playbook → Plan with Narratives

**v0.4 Playbook:**
```json
{
  "vBRIEFInfo": {"version": "0.4"},
  "playbook": {
    "title": "Incident Response",
    "items": [
      {
        "title": "Database Outage",
        "status": "completed",
        "content": "We restored service in 45 minutes..."
      }
    ]
  }
}
```

**v0.5 Plan:**
```json
{
  "vBRIEFInfo": {"version": "0.5"},
  "plan": {
    "title": "Incident Response",
    "status": "completed",
    "narratives": {
      "Outcome": "Restored service in 45 minutes",
      "Strengths": "Clear runbook, fast escalation",
      "Weaknesses": "Monitoring gaps",
      "Lessons": "Automate failover"
    },
    "items": [
      {
        "title": "Database Outage",
        "status": "completed"
      }
    ]
  }
}
```

**Changes:**
- `playbook` → `plan`
- Move content to `plan.narratives` with retrospective keys
- Add required `plan.status`
- Use standardized narrative keys: `Outcome`, `Strengths`, `Weaknesses`, `Lessons`

### 3. Status Values

Update all status values:

```
pending     → pending     (no change)
inProgress  → running     (CHANGED)
completed   → completed   (no change)
blocked     → blocked     (no change)
cancelled   → cancelled   (no change)
```

Additional Plan-level statuses (only for `plan.status`, not item status):
- `draft`
- `proposed`
- `approved`

### 4. Dependencies → Edges

**v0.4 with dependencies:**
```json
{
  "plan": {
    "items": [
      {"id": "a", "title": "Task A", "status": "completed"},
      {
        "id": "b",
        "title": "Task B",
        "status": "running",
        "dependencies": ["a"]
      }
    ]
  }
}
```

**v0.5 with edges:**
```json
{
  "plan": {
    "items": [
      {"id": "a", "title": "Task A", "status": "completed"},
      {"id": "b", "title": "Task B", "status": "running"}
    ],
    "edges": [
      {"from": "a", "to": "b", "type": "blocks"}
    ]
  }
}
```

**Changes:**
- Remove `dependencies` field from items
- Add `plan.edges` array
- Each dependency becomes an edge with `type: "blocks"`
- Note the direction: if B depends on A, edge goes from A to B

### 5. Nested TodoLists → SubItems or PlanRef

**v0.4 with embedded todoList:**
```json
{
  "plan": {
    "items": [
      {
        "id": "phase1",
        "title": "Phase 1",
        "status": "running",
        "todoList": {
          "items": [
            {"title": "Subtask 1", "status": "completed"},
            {"title": "Subtask 2", "status": "pending"}
          ]
        }
      }
    ]
  }
}
```

**v0.5 Option A - Use subItems:**
```json
{
  "plan": {
    "items": [
      {
        "id": "phase1",
        "title": "Phase 1",
        "status": "running",
        "subItems": [
          {"id": "phase1.task1", "title": "Subtask 1", "status": "completed"},
          {"id": "phase1.task2", "title": "Subtask 2", "status": "pending"}
        ]
      }
    ]
  }
}
```

**v0.5 Option B - Use planRef (external Plan):**
```json
{
  "plan": {
    "items": [
      {
        "id": "phase1",
        "title": "Phase 1",
        "status": "running",
        "planRef": "file://./phase1-tasks.vbrief.json"
      }
    ]
  }
}
```

Where `phase1-tasks.vbrief.json` is a separate Plan document.

### 6. Narrative Key Casing (Optional)

v0.5 recommends TitleCase for narrative keys:

**v0.4 (lowercase):**
```json
{
  "narratives": {
    "proposal": "Refactor the API",
    "background": "Current API is complex"
  }
}
```

**v0.5 (TitleCase - recommended):**
```json
{
  "narratives": {
    "Proposal": "Refactor the API",
    "Background": "Current API is complex"
  }
}
```

This is a **SHOULD** requirement (warning, not error). Old documents still work but will generate warnings.

## Field Mapping Reference

### TodoItem → PlanItem

All TodoItem fields are now available on PlanItem:

| v0.4 TodoItem Field | v0.5 PlanItem Field | Notes |
|---------------------|---------------------|-------|
| id | id | No change |
| uid | uid | No change |
| title | title | No change |
| status | status | Update `inProgress` → `running` |
| narrative | narrative | No change |
| priority | priority | No change |
| tags | tags | Promoted to core |
| metadata | metadata | Promoted to core |
| created | created | Promoted to core |
| updated | updated | Promoted to core |
| completed | completed | No change |
| dueDate | dueDate | No change |
| percentComplete | percentComplete | No change |
| timezone | timezone | No change |
| dependencies | *(removed)* | Use `plan.edges` instead |
| participants | participants | No change |
| relatedComments | relatedComments | No change |
| uris | uris | No change |
| recurrence | recurrence | No change |
| reminders | reminders | No change |
| classification | classification | No change |

### PlanItem → PlanItem

| v0.4 PlanItem Field | v0.5 PlanItem Field | Notes |
|---------------------|---------------------|-------|
| id | id | No change, now supports hierarchical IDs |
| uid | uid | No change |
| title | title | No change |
| status | status | Update `inProgress` → `running` |
| narrative | narrative | No change |
| tags | tags | Promoted to core |
| metadata | metadata | Promoted to core |
| dependencies | *(removed)* | Use `plan.edges` instead |
| subItems | subItems | No change |
| todoList | *(removed)* | Use `subItems` or `planRef` |
| participants | participants | No change |
| location | location | No change |
| uris | uris | No change |
| startDate | startDate | No change |
| endDate | endDate | No change |
| percentComplete | percentComplete | No change |
| *(new)* | planRef | New: Reference external Plans |
| *(new)* | priority | Merged from TodoItem |
| *(new)* | dueDate | Merged from TodoItem |
| *(new)* | completed | Merged from TodoItem |
| *(new)* | recurrence | Merged from TodoItem |
| *(new)* | reminders | Merged from TodoItem |
| *(new)* | relatedComments | Merged from TodoItem |

## Automated Migration

No automated migration tool is provided since no v0.4 implementations exist in the wild. Manual migration is straightforward following this guide.

If you need to migrate many documents, consider:

1. **JSON transformation script** using jq or Python
2. **Schema-based converter** using the v0.4 and v0.5 schemas
3. **LLM-assisted migration** by providing this guide to an AI coding assistant

## Validation

After migration, validate your documents:

```bash
python3 validation/vbrief_validator.py your-migrated-file.vbrief.json
```

The validator checks:
- Schema compliance
- Conformance criteria (10 rules)
- DAG validity (no cycles, valid references)
- Narrative key conventions

## Examples

See `examples/` directory for complete v0.5 documents:
- `minimal-plan.vbrief.json` - Simple task list (was TodoList in v0.4)
- `structured-plan.vbrief.json` - Plan with narratives
- `retrospective-plan.vbrief.json` - Playbook-style (was Playbook in v0.4)
- `dag-plan.vbrief.json` - Plan with DAG edges (replaces dependencies)
- `dag-plan.vbrief.tron` - TRON format for token efficiency

## Common Migration Patterns

### Pattern 1: Simple Todo List

**v0.4:**
```json
{"vBRIEFInfo": {"version": "0.4"}, "todoList": {"items": [...]}}
```

**v0.5:**
```json
{"vBRIEFInfo": {"version": "0.5"}, "plan": {"title": "Tasks", "status": "running", "items": [...]}}
```

### Pattern 2: Plan with Dependencies

**v0.4:**
```json
{"plan": {"items": [{"id": "a", ...}, {"id": "b", "dependencies": ["a"], ...}]}}
```

**v0.5:**
```json
{"plan": {"items": [{"id": "a", ...}, {"id": "b", ...}], "edges": [{"from": "a", "to": "b", "type": "blocks"}]}}
```

### Pattern 3: Incident Playbook

**v0.4:**
```json
{"playbook": {"title": "Incident X", "items": [{"title": "Step 1", "content": "...", ...}]}}
```

**v0.5:**
```json
{"plan": {"title": "Incident X", "status": "completed", "narratives": {"Outcome": "...", "Lessons": "..."}, "items": [{"title": "Step 1", ...}]}}
```

## Getting Help

- **Validation errors**: Run `vbrief_validator.py` for detailed error messages
- **Schema questions**: See `schemas/vbrief-core.schema.json`
- **Conformance criteria**: See `SPECIFICATION.md` section on Conformance
- **Examples**: See `examples/` directory

## FAQ

**Q: Do I need to migrate immediately?**  
A: No implementations of v0.4 exist in the wild, so this is primarily for reference.

**Q: Can I keep using v0.4?**  
A: v0.4 is deprecated. v0.5 is the current specification.

**Q: Will there be migration tools?**  
A: Not officially. The changes are straightforward enough for manual migration or custom scripts.

**Q: What about extensions?**  
A: Extension documents will be updated separately. Core fields (id, uid, tags, metadata, created, updated) are now in core, reducing the need for some extensions.

**Q: Can I use both TodoList and Plan?**  
A: No. v0.5 only supports Plan. Use Plan with minimal fields for todo-like documents.

**Q: What if I have a cycle in my edges?**  
A: Cycles are invalid in v0.5. The validator will detect and report them. Restructure your DAG to eliminate cycles.

## Next Steps

1. Update your documents following this guide
2. Run validation: `python3 validation/vbrief_validator.py file.vbrief.json`
3. Consider TRON format for token efficiency (see `docs/tron-encoding.md`)
4. Read the full specification: `SPECIFICATION.md`
5. Explore examples: `examples/` directory
