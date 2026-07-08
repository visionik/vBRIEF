# xBRIEF Extension Documentation Alignment Issues

**Date**: 2025-12-28  
**Current Spec Version**: 0.4  
**Status**: Review needed

## Summary

The extension documents have several alignment issues with the current v0.4 spec:

1. **Version string mismatches** in code examples
2. **Outdated terminology** (Phase → PlanItem)
3. **Missing v0.4 updates** in some documents

## Issues by File

### xBRIEF-extension-common.md

**Status**: ❌ Needs updates

**Issues**:
- All examples use version "0.3" instead of "0.4"
- Multiple occurrences in both TRON and JSON examples
- Extensions 1-12 all need version updates

**Examples to fix**:
```
Line references with "0.3":
- TRON: xBRIEFInfo("0.3", ...)
- JSON: "version": "0.3"
```

**Action needed**: Update all version strings from "0.3" to "0.4"

---

### xBRIEF-extension-playbooks.md

**Status**: ❌ Needs updates

**Issues**:
- Examples use version "0.2"
- Document may need review for v0.3→v0.4 changes (Phase → PlanItem renaming)

**Examples to fix**:
```
- xBRIEFInfo("0.2")
- "version": "0.2"
```

**Action needed**: 
1. Update version strings from "0.2" to "0.4"
2. Review for Phase/PlanItem terminology
3. Review for PlaybookEntry → PlaybookItem changes (if any)

---

### xBRIEF-extension-security.md

**Status**: ❌ Needs updates

**Issues**:
- Examples use version "0.2"
- Multiple references to "Phase" that should be "PlanItem"
- References to "phases" array that should be "items"

**Specific issues**:
```
Line content:
- "Core xBRIEF types (xBRIEFInfo, TodoList, TodoItem, Plan, Phase, Narrative)"
  Should be: "... Plan, PlanItem, Narrative)"

- "## Phase Extensions"
  Should be: "## PlanItem Extensions"

- "Phase {"
  Should be: "PlanItem {"

- "phases: [...]"
  Should be: "items: [...]"

- "filtered.plan.phases?.filter(phase => {"
  Should be: "filtered.plan.items?.filter(item => {"
```

**Action needed**:
1. Update version strings from "0.2" to "0.4"
2. Replace all "Phase" with "PlanItem"
3. Replace "phases" array references with "items"
4. Update variable names in code examples (phase → item)

---

### xBRIEF-extension-claude.md

**Status**: ❌ Needs updates

**Issues**:
- All examples use version "0.2"
- May need terminology review

**Examples to fix**:
```
- xBRIEFInfo("0.2", "claude-3.5-sonnet")
- xBRIEFInfo("0.2")
```

**Action needed**: Update version strings from "0.2" to "0.4"

---

### xBRIEF-extension-beads.md

**Status**: ❌ Needs updates

**Issues**:
- All examples use version "0.3"

**Examples to fix**:
```
- "xBRIEFInfo": {"version": "0.3"}
```

**Action needed**: Update version strings from "0.3" to "0.4"

---

### xBRIEF-extension-typescript.md

**Status**: ⚠️ Minor issue

**Issues**:
- One example uses version "0.2"

**Example to fix**:
```
- "xBRIEFInfo": {"version": "0.2"}
```

**Action needed**: Update version string from "0.2" to "0.4"

---

### xBRIEF-extension-api-go.md

**Status**: ✅ OK (no version strings in examples found)

---

### xBRIEF-extension-api-python.md

**Status**: ✅ OK (no version strings in examples found)

---

### xBRIEF-extension-MCP.md

**Status**: ✅ OK (no version strings in examples found)

---

## Terminology Changes (v0.3 → v0.4)

Per the spec changelog, these terms were renamed:

| Old Term (v0.3) | New Term (v0.4) | Location |
|-----------------|-----------------|----------|
| Phase | PlanItem | Plan container |
| PlaybookEntry | PlaybookItem | Playbook container |
| phases (array) | items (array) | Plan.items |

**Files needing terminology updates**:
- xBRIEF-extension-security.md (extensive Phase → PlanItem changes)
- xBRIEF-extension-common.md (review for any Phase references)
- xBRIEF-extension-playbooks.md (review for PlaybookEntry references)

## Recommended Action Plan

### Phase 1: Version String Updates (Quick wins)
- [ ] xBRIEF-extension-common.md: 0.3 → 0.4 (all examples)
- [ ] xBRIEF-extension-playbooks.md: 0.2 → 0.4
- [ ] xBRIEF-extension-claude.md: 0.2 → 0.4
- [ ] xBRIEF-extension-beads.md: 0.3 → 0.4
- [ ] xBRIEF-extension-typescript.md: 0.2 → 0.4
- [ ] xBRIEF-extension-security.md: 0.2 → 0.4

### Phase 2: Terminology Updates (More involved)
- [ ] xBRIEF-extension-security.md: Phase → PlanItem (comprehensive)
- [ ] xBRIEF-extension-common.md: Review for Phase/PlaybookEntry
- [ ] xBRIEF-extension-playbooks.md: Review for PlaybookEntry

### Phase 3: Verification
- [ ] Run grep for any remaining "0\.[0-3]" version strings
- [ ] Run grep for "Phase[^d]" (excluding "phased")
- [ ] Run grep for "PlaybookEntry"
- [ ] Test examples against current spec
- [ ] Update extension-common.md metadata (Last Updated date)

## Commands for Bulk Updates

```bash
# Find all version string occurrences
rg '"version":\s*"0\.[0-3]"|xBRIEFInfo\("0\.[0-3]"' xBRIEF-extension-*.md

# Find Phase terminology
rg -i 'phase[^d]|phases:' xBRIEF-extension-*.md

# Find PlaybookEntry terminology
rg 'PlaybookEntry' xBRIEF-extension-*.md

# Bulk replace (after review)
# Use sed or manual editing with care
```

## Notes

- The spec header says "Last Updated: 2025-12-28T00:00:00Z" and "Version: 0.4"
- Extension-common.md says "Version: 0.4" but examples use "0.3"
- This suggests examples were not updated when the version was bumped
- Security extension has the most work needed due to Phase → PlanItem changes

---

**Next Steps**: Create todo items or plan for systematic updates to all affected files.
