# Interview: libxbrief-ts

**Generated**: 2026-03-31
**Status**: Ready for AI Interview
**Strategy**: interview
**Path**: Light (Interview → SPECIFICATION)
**Specification Output**: /Users/visionik/Projects/xBRIEF/SPECIFICATION-libxbrief-ts.md

## Initial Input

**Project Description**: make an idiomatic typscript port of the local libxbrief for python

**I want to build libxbrief-ts that has the following features:**

---

## Instructions for AI

! Read `deft/strategies/interview.md` and follow the **Light path**.
! Conduct a structured interview, then generate SPECIFICATION.md with
embedded Requirements section (FR-1, NFR-1). No separate PRD needed.

# Specification Generation

Agent workflow for creating project specifications via structured interview.
This template implements [strategies/interview.md](../strategies/interview.md).
See that file for the full canonical strategy including the sizing gate,
Light/Full paths, and transition criteria.

Legend (from RFC2119): !=MUST, ~=SHOULD, ≉=SHOULD NOT, ⊗=MUST NOT, ?=MAY.

## Input Template

```
I want to build libxbrief-ts that has the following features:
1. [feature]
2. [feature]
...
N. [feature]
```

## Sizing Gate

! Before starting the interview, determine project complexity per
[strategies/interview.md](../strategies/interview.md#sizing-gate).

- ! Check `PROJECT.md` for `**Process**: Light` or `**Process**: Full` — if declared, use that path
- ! If not declared, propose a size and **wait for the user to confirm** before proceeding
- ⊗ Combine the sizing proposal with the first interview question

**Light** (small/medium): Interview → SPECIFICATION with embedded Requirements.
**Full** (large/complex): Interview → PRD (approval gate) → SPECIFICATION with traceability.

## Interview Process

- ~ Use Claude AskInterviewQuestion when available (emulate it if not available)
- ! If Input Template fields are empty: ask overview, then features, then details
- ! Ask **ONE** focused, non-trivial question per step
- ⊗ Ask more than one question per step; or try to sneak-in "also" questions
- ~ Provide numbered answer options when appropriate
- ! Include "other" option for custom/unknown responses
- ! Make it clear which option you feel is RECOMMENDED
- ! When you are done, append to the end of this file all questions asked and answers given

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

### Full Path: PRD Generation

Only on the **Full** path — generate `PRD.md` before the specification:

```markdown
# [Project Name] PRD

## Problem Statement
What problem does this solve? Who has this problem?

## Goals
- Primary goal
- Secondary goals
- Non-goals (explicitly out of scope)

## User Stories
As a [user type], I want [capability] so that [benefit].

## Requirements

### Functional Requirements
- FR-1: [requirement]
- FR-2: [requirement]

### Non-Functional Requirements
- NFR-1: Performance — [requirement]
- NFR-2: Security — [requirement]

## Success Metrics
How do we know this succeeded?

## Open Questions
Any remaining decisions deferred to implementation.
```

- ! Focus on WHAT, not HOW
- ! Use RFC 2119 language (MUST, SHOULD, MAY)
- ! Number all requirements for traceability
- ! User MUST review and approve PRD before specification generation begins

### Specification Flow (both paths)

1. ! Write `./xbrief/specification.xbrief.json` with `status: draft`
2. ! Summarize what was decided and ask the user to review
3. ! On user approval, update `status` to `approved` in the xbrief file
4. ! Run `task spec:render` (or generate `SPECIFICATION.md` directly if task unavailable)
5. ? For add-on specs: write `./xbrief/specification-{name}.xbrief.json` → `SPECIFICATION-{name}.md`

! The xBRIEF file MUST use this exact top-level structure:

```json
{
  "xBRIEFInfo": { "version": "0.5" },
  "plan": {
    "title": "Project Name SPECIFICATION",
    "status": "draft",
    "items": [
      {
        "id": "1.1.1",
        "title": "Task description",
        "status": "pending",
        "narrative": { "Acceptance": "...", "Traces": "FR-1" }
      }
    ]
  }
}
```

~ See [xbrief/xbrief.md](../xbrief/xbrief.md) for full schema documentation and [xbrief/schemas/xbrief-core.schema.json](../xbrief/schemas/xbrief-core.schema.json) for the JSON Schema.

- ⊗ Write `SPECIFICATION.md` directly — it is generated from the xbrief source
- ! Follow all relevant deft guidelines
- ! Use RFC 2119 MUST, SHOULD, MAY, SHOULD NOT, MUST NOT wording
- ! Break into phases, subphases, tasks
- ! End of each phase/subphase must implement and run testing until it passes
- ! Mark all dependencies explicitly: "Phase 2 (depends on: Phase 1)"
- ! Design for parallel work (multiple agents)
- ⊗ Write code (specification only)

## Afterwards

- ! Let user know to type "implement SPECIFICATION.md" to start implementation

**SPECIFICATION Structure (Light path — embedded Requirements):**

```markdown
# Project Name

## Overview

## Requirements

### Functional Requirements
- FR-1: [requirement]
- FR-2: [requirement]

### Non-Functional Requirements
- NFR-1: [requirement]
- NFR-2: [requirement]

## Architecture

## Implementation Plan

### Phase 1: Foundation

#### Subphase 1.1: Setup

- Task 1.1.1: (description, traces: FR-1, dependencies, acceptance criteria)

#### Subphase 1.2: Core (depends on: 1.1)

### Phase 2: Features (depends on: Phase 1)

## Testing Strategy

## Deployment
```

**SPECIFICATION Structure (Full path — references PRD):**

```markdown
# Project Name

## Overview
Brief summary and link to PRD.

## Architecture

## Implementation Plan

### Phase 1: Foundation

#### Subphase 1.1: Setup

- Task 1.1.1: (description, traces: FR-1, dependencies, acceptance criteria)

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
- ! Each task SHOULD reference which FR/NFR it implements via `(traces: FR-N)`

## Anti-Patterns

- ⊗ Multiple questions at once
- ⊗ Assumptions without clarifying
- ⊗ Vague requirements
- ⊗ Missing dependencies
- ⊗ Sequential tasks that could be parallel
- ⊗ Creating PRD.md on the Light path
- ⊗ Skipping the sizing gate
## Interview Transcript

### Question 1: Module system
Which module/package target should we use?
- 1. ESM-only (recommended)
- 2. Dual CJS + ESM
- 3. CJS-only
- 4. Other
Answer: 1

### Question 2: Runtime targets
Which runtimes should the port support?
- 1. Node.js 18+ only
- 2. Node.js 18+ and modern browsers (recommended)
- 3. Universal (Node, Bun, Deno, browsers)
- 4. Other
Answer: 3

### Question 3: API parity scope
Should the TypeScript port achieve full parity with the Python libxbrief API?
- 1. Full parity (recommended)
- 2. Core only
- 3. Core + Builder, skip DAG
- 4. Other
Answer: 1

### Question 4: Type strictness and unknown field handling
How should the TypeScript port handle typing and unknown fields?
- 1. Strict interfaces with index signature
- 2. Strict interfaces with separate extras map (recommended)
- 3. Loose Record<string, unknown> throughout
- 4. Zod schemas with passthrough
- 5. Other
Answer: use zod

### Question 5: Test framework
Which test framework should be used?
- 1. Vitest (recommended)
- 2. Jest
- 3. node:test
- 4. Other
Answer: 1

### Question 6: Package location and structure
Where should the TypeScript port live?
- 1. Subdirectory in this repo (recommended)
- 2. Separate repo
- 3. Workspace monorepo
- 4. Other
Answer: 1

### Question 7: npm package name and publishing
How should publishing be handled?
- 1. libxbrief
- 2. @xbrief/core
- 3. @deftai/libxbrief
- 4. Don't publish yet
- 5. Other
Answer: 4

### Question 8: File I/O entrypoint
How should file I/O be handled for universal runtime support?
- 1. Separate entrypoint (recommended)
- 2. Dynamic import with runtime detection
- 3. Skip file I/O entirely
- 4. Other
Answer: 1

