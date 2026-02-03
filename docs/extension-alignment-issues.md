# vBRIEF Extension Documentation Alignment Issues

**Date**: 2025-12-28  
**Current Spec Version**: 0.4  
**Status**: Review needed

## Summary

The extension documents have several alignment issues with the current v0.4 spec:

1. **Version string mismatches** in code examples
2. **Outdated terminology** (Phase → PlanItem)
3. **Missing v0.4 updates** in some documents

## Issues by File

### vBRIEF-extension-common.md

**Status**: ❌ Needs updates

**Issues**:
- All examples use version "0.3" instead of "0.4"
- Multiple occurrences in both TRON and JSON examples
- Extensions 1-12 all need version updates

**Examples to fix**:
```
Line references with "0.3":
- TRON: vBRIEFInfo("0.3", ...)
- JSON: "version": "0.3"
```

**Action needed**: Update all version strings from "0.3" to "0.4"

---

### vBRIEF-extension-playbooks.md

**Status**: ❌ Needs updates

**Issues**:
- Examples use version "0.2"
- Document may need review for v0.3→v0.4 changes (Phase → PlanItem renaming)

**Examples to fix**:
```
- vBRIEFInfo("0.2")
- "version": "0.2"
```

**Action needed**: 
1. Update version strings from "0.2" to "0.4"
2. Review for Phase/PlanItem terminology
3. Review for PlaybookEntry → PlaybookItem changes (if any)

---

### vBRIEF-extension-security.md

**Status**: ❌ Needs updates

**Issues**:
- Examples use version "0.2"
- Multiple references to "Phase" that should be "PlanItem"
- References to "phases" array that should be "items"

**Specific issues**:
```
Line content:
- "Core vBRIEF types (vBRIEFInfo, TodoList, TodoItem, Plan, Phase, Narrative)"
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

### vBRIEF-extension-claude.md

**Status**: ❌ Needs updates

**Issues**:
- All examples use version "0.2"
- May need terminology review

**Examples to fix**:
```
- vBRIEFInfo("0.2", "claude-3.5-sonnet")
- vBRIEFInfo("0.2")
```

**Action needed**: Update version strings from "0.2" to "0.4"

---

### vBRIEF-extension-beads.md

**Status**: ❌ Needs updates

**Issues**:
- All examples use version "0.3"

**Examples to fix**:
```
- "vBRIEFInfo": {"version": "0.3"}
```

**Action needed**: Update version strings from "0.3" to "0.4"

---

### vBRIEF-extension-typescript.md

**Status**: ⚠️ Minor issue

**Issues**:
- One example uses version "0.2"

**Example to fix**:
```
- "vBRIEFInfo": {"version": "0.2"}
```

**Action needed**: Update version string from "0.2" to "0.4"

---

### vBRIEF-extension-api-go.md

**Status**: ✅ OK (no version strings in examples found)

---

### vBRIEF-extension-api-python.md

**Status**: ✅ OK (no version strings in examples found)

---

### vBRIEF-extension-MCP.md

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
- vBRIEF-extension-security.md (extensive Phase → PlanItem changes)
- vBRIEF-extension-common.md (review for any Phase references)
- vBRIEF-extension-playbooks.md (review for PlaybookEntry references)

## Recommended Action Plan

### Phase 1: Version String Updates (Quick wins)
- [ ] vBRIEF-extension-common.md: 0.3 → 0.4 (all examples)
- [ ] vBRIEF-extension-playbooks.md: 0.2 → 0.4
- [ ] vBRIEF-extension-claude.md: 0.2 → 0.4
- [ ] vBRIEF-extension-beads.md: 0.3 → 0.4
- [ ] vBRIEF-extension-typescript.md: 0.2 → 0.4
- [ ] vBRIEF-extension-security.md: 0.2 → 0.4

### Phase 2: Terminology Updates (More involved)
- [ ] vBRIEF-extension-security.md: Phase → PlanItem (comprehensive)
- [ ] vBRIEF-extension-common.md: Review for Phase/PlaybookEntry
- [ ] vBRIEF-extension-playbooks.md: Review for PlaybookEntry

### Phase 3: Verification
- [ ] Run grep for any remaining "0\.[0-3]" version strings
- [ ] Run grep for "Phase[^d]" (excluding "phased")
- [ ] Run grep for "PlaybookEntry"
- [ ] Test examples against current spec
- [ ] Update extension-common.md metadata (Last Updated date)

## Commands for Bulk Updates

```bash
# Find all version string occurrences
rg '"version":\s*"0\.[0-3]"|vBRIEFInfo\("0\.[0-3]"' vBRIEF-extension-*.md

# Find Phase terminology
rg -i 'phase[^d]|phases:' vBRIEF-extension-*.md

# Find PlaybookEntry terminology
rg 'PlaybookEntry' vBRIEF-extension-*.md

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
