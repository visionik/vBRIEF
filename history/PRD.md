# Product Requirements Document: libxbrief.py

**Generated**: 2026-02-23
**Status**: Ready for AI Interview

## Initial Input

**Project Description**: python implementation of a simple, sane, idiompotic, python library to read and write xBRIEF files

**I want to build libxbrief.py that has the following features:**

---

# Specification Generation

Agent workflow for creating project specifications via structured interview.

Legend (from RFC2119): !=MUST, ~=SHOULD, ≉=SHOULD NOT, ⊗=MUST NOT, ?=MAY.

## Input Template

```
I want to build libxbrief.py that has the following features:
1. [feature]
2. [feature]
...
N. [feature]
```

## Interview Process

- ~ Use Claude AskInterviewQuestion when available (emulate it if not available)
- ! If Input Template fields are empty: ask overview, then features, then details
- ! Ask **ONE** focused, non-trivial question per step
- ⊗ ask more than one question per step; or try to sneak-in "also" questions
- ~ Provide numbered answer options when appropriate
- ! Include "other" option for custom/unknown responses
- ! make it clear which option you feel is RECOMMENDED
- ! when you are done, append to the end of this file all questions asked and answers given.

**Question Areas:**

- ! Missing decisions (language, framework, deployment)
- ! Edge cases (errors, boundaries, failure modes)
- ! Implementation details (architecture, patterns, libraries)
- ! Requirements (performance, security, scalability)
- ! UX/constraints (users, timeline, compatibility)
- ! Tradeoffs (simplicity vs features, speed vs safety)

**Completion:**

- ! Continue until little ambiguity remains
- ! Ensure spec is comprehensive enough to implement

## Output Generation

- ! Generate as SPECIFICATION.md
- ! follow all relevant deft guidelines
- ! use RFC2119 MUST, SHOULD, MAY, SHOULD NOT, MUST NOT wording
- ! Break into phases, subphases, tasks
- ! end of each phase/subphase must implement and run testing until it passes
- ! Mark all dependencies explicitly: "Phase 2 (depends on: Phase 1)"
- ! Design for parallel work (multiple agents)
- ⊗ Write code (specification only)

## Afterwards

- ! let user know to type "implement SPECIFICATION.md" to start implementation

**Structure:**

```markdown
# Project Name

## Overview

## Requirements

## Architecture

## Implementation Plan

### Phase 1: Foundation

#### Subphase 1.1: Setup

- Task 1.1.1: (description, dependencies, acceptance criteria)

#### Subphase 1.2: Core (depends on: 1.1)

### Phase 2: Features (depends on: Phase 1)

## Testing Strategy

## Deployment
```

## Best Practices

- ! Detailed enough to implement without guesswork
- ! Clear scope boundaries (in vs out)
- ! Include rationale for major decisions
- ~ Size tasks for 1-4 hours
- ! Minimize inter-task dependencies
- ! Define clear component interfaces

## Anti-Patterns

- ⊗ Multiple questions at once
- ⊗ Assumptions without clarifying
- ⊗ Vague requirements
- ⊗ Missing dependencies
- ⊗ Sequential tasks that could be parallel


---

## Interview Log (Appended)

**Q1: v1 scope for libxbrief.py**
- Option selected: 1 (Plan JSON core only)
- Answer: Use current v0.5 Plan JSON core; ignore old formats; TRON deferred.

**Q2: API style for v1**
- Option selected: 3 (both dict helpers and class model)
- Answer: Provide both functional dict API and object model API.

**Q3: Validation behavior on load/save**
- Option selected: B (lenient load + explicit validate)
- Answer: Parsing is lenient; caller uses `validate()` for conformance checks.

**Q4: Internal model implementation approach**
- Option selected: A (`dataclasses` + custom validators)
- Answer: Use dataclasses, not pydantic, for v1 core.

**Q5: Package/module layout depth**
- Option selected: C (full layered package now)
- Answer: Build layered package layout in v1.

**Q6: Python version support target**
- Option selected: A (Python 3.10+)
- Answer: Support Python >=3.10.

**Q7: `validate()` error reporting contract**
- Option selected: A (structured issues list)
- Answer: Return structured errors/warnings with code/path/message/severity.

**Q8: Unknown-field handling policy**
- Option selected: A (preserve all unknown fields at every level)
- Answer: Preserve unknown keys at root, plan, and item levels.

**Q9: Write/formatting policy**
- Option selected: A (canonical writer + optional preserve mode)
- Answer: Canonical output by default; optional preserve formatting mode.

**Q10: CLI scope for v1**
- Option selected: A (library-only)
- Answer: No CLI in v1.

**Q11: Conformance scope for v1 validation**
- Option selected: A (core structural + conformance only)
- Answer: No DAG cycle/reference checks in v1.

**Q12: Release target for v1**
- Option selected: A (local/dev package first)
- Answer: Local package deliverable first; publish later.

**Additional statement captured**
- TRON support is planned later via `libtronpy` from `~/Projects/...`.
