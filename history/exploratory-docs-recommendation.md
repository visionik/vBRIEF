# Exploratory Documents Review & Recommendations

**Date**: 2025-12-28  
**Reviewer**: Code Review Session  
**Status**: Recommendations

## Overview

The repository contains 8 exploratory documents (6 "consider", 2 "alternative") totaling ~170KB. These are substantial thought pieces exploring future directions for vBRIEF.

## Documents Reviewed

### Consider Documents (Total: ~172KB)
1. `vBRIEF-consider-agentic-patterns.md` (32KB) - Design patterns for AI agents
2. `vBRIEF-consider-experimental-workflows.md` (21KB) - Workflow experiments
3. `vBRIEF-consider-GEPA.md` (20KB) - Goal-Evidence-Plan-Action framework
4. `vBRIEF-consider-model-first-reasoning.md` (25KB) - Model-first design
5. `vBRIEF-consider-session-memory.md` (40KB) - Session memory systems
6. `vBRIEF-consider-system3.md` (34KB) - System 3 thinking

### Alternative Format Documents
7. `vBRIEF-alternative-namespaced.md` (~15KB) - Namespace-based extension architecture
8. `vBRIEF-alternative-TROY.md` (~12KB) - YAML-based token-reduced format

## Recommendations

### Tier 1: Keep & Integrate (High Value)

**`vBRIEF-consider-agentic-patterns.md`**
- **Action**: Move to `docs/proposals/agentic-patterns.md`
- **Rationale**: Highly relevant to vBRIEF's AI agent use case. Well-structured with concrete patterns. Ready for extension development.
- **Next Steps**: Consider as Extension 13 once Extensions 1-12 stabilize

**`vBRIEF-consider-session-memory.md`**
- **Action**: Move to `docs/proposals/session-memory.md`
- **Rationale**: Critical for agent systems. Aligns with vBRIEF's memory tier model (TodoList/Plan/Playbook).
- **Next Steps**: Could inform Extension 14

### Tier 2: Archive to History (Valuable Reference)

**`vBRIEF-alternative-namespaced.md`**
- **Action**: Move to `history/proposals/namespaced-extensions.md`
- **Rationale**: Important architectural decision point. Good to preserve reasoning for why flat structure was chosen over namespacing.
- **Add Note**: "Considered for v0.5 but deferred to maintain simplicity and TRON efficiency per v0.4 design goals."

**`vBRIEF-alternative-TROY.md`**
- **Action**: Move to `history/proposals/troy-format.md`
- **Rationale**: Format exploration was valuable but TRON already chosen. Keep as reference for why YAML hybrid wasn't pursued.
- **Add Note**: "TRON selected as primary token-reduced format for v0.4. TROY would only provide ~5% benefit over TRON with parser complexity costs."

### Tier 3: Decide Later (Needs Owner Review)

**`vBRIEF-consider-experimental-workflows.md`**
- **Action**: Owner decision needed
- **Questions**: 
  - Does this overlap with agentic-patterns doc?
  - Is experimental workflow support needed soon?
- **Suggestion**: If distinct from agentic-patterns, keep in docs/proposals/. Otherwise merge relevant parts into agentic-patterns.

**`vBRIEF-consider-GEPA.md`**
- **Action**: Owner decision needed
- **Questions**: Is GEPA framework still being pursued vs other agentic frameworks?
- **Suggestion**: If active, move to docs/proposals/. If superseded by newer thinking, archive to history/.

**`vBRIEF-consider-model-first-reasoning.md`**
- **Action**: Owner decision needed  
- **Rationale**: Seems like methodology/philosophy document more than concrete feature
- **Suggestion**: Either move to `docs/philosophy/` if foundational, or archive to history/ if exploratory phase complete

**`vBRIEF-consider-system3.md`**
- **Action**: Owner decision needed
- **Rationale**: Similar to model-first - philosophical exploration
- **Suggestion**: Move to `docs/philosophy/` or archive to history/

## Proposed Directory Structure

```
vBRIEF/
├── docs/
│   ├── proposals/           # Active proposals being considered
│   │   ├── agentic-patterns.md
│   │   └── session-memory.md
│   ├── philosophy/          # Design philosophy (if needed)
│   │   └── ...
│   └── ...
├── history/
│   ├── proposals/           # Archived proposals
│   │   ├── namespaced-extensions.md
│   │   ├── troy-format.md
│   │   └── ...
│   └── ...
```

## Benefits

1. **Clearer Intent**: "proposals/" vs "history/" signals which ideas are active
2. **Reduced Root Clutter**: 8 fewer files in root directory
3. **Preserved Knowledge**: Nothing deleted - all thinking preserved
4. **Better Navigation**: Organized by status/purpose

## Implementation

Create task target:
```yaml
docs:organize:
  desc: Organize exploratory documents per recommendations
  cmds:
    - mkdir -p docs/proposals history/proposals
    - git mv vBRIEF-consider-agentic-patterns.md docs/proposals/agentic-patterns.md
    - git mv vBRIEF-consider-session-memory.md docs/proposals/session-memory.md
    - git mv vBRIEF-alternative-namespaced.md history/proposals/namespaced-extensions.md
    - git mv vBRIEF-alternative-TROY.md history/proposals/troy-format.md
    # Add archival notes to history/ files
```

## Decision Needed

Owner should review Tier 3 documents and decide:
- Which are active proposals → `docs/proposals/`
- Which are completed explorations → `history/proposals/`
- Which (if any) are foundational philosophy → `docs/philosophy/`
