# vBRIEF Extension: Experimental Workflows

**Extension Name**: Experimental Workflows

**Version**: 0.2

**Status**: Draft

**Last Updated**: 2025-12-27

## Overview

This extension adds support for **hypothesis-driven development** and **constraint-based execution** to vBRIEF. It formalizes the iterative refinement loop: hypothesis → experiment → critique → revision.

### Motivation

Modern AI-assisted development increasingly relies on:
1. **Constraint Stacks** - Pre-defining boundaries for outputs rather than hoping for quality
2. **Iterative Refinement** - Multi-step processes: generate → critique → revise
3. **Experimental Validation** - Testing hypotheses with real data before committing to approaches

Traditional project management tools treat work as deterministic. This extension acknowledges that many technical decisions require experimentation, especially when:
- Working with novel technologies or architectures
- Optimizing performance where trade-offs are unclear
- Using AI/LLM assistance where output quality varies
- Making architectural decisions with multiple viable approaches

### What this extension adds

**Constraints** - Structured requirements that define success criteria and boundaries
**Experiments** - Hypothesis testing with tracked outcomes and confidence levels
**Critiques** - Structured review and reflection on work
**Iterative Narratives** - Expanded narrative types supporting the refinement loop

## Dependencies

- **Requires**: Core vBRIEF
- **Recommended**: Extension 3 (Rich Metadata), Extension 7 (Resources & References)

## Data Model

### New Types

```javascript
Constraint {
  id?: string              # Unique identifier (Extension 2)
  type: enum               # "output" | "performance" | "style" | "security" | "resource" | "quality"
  rule: string             # Human-readable constraint description
  rationale?: string       # Why this constraint exists
  priority: enum           # "must" | "should" | "could" | "wont"
  validation?: string      # How to verify (test command, metric, etc.)
  metadata?: object        # Extension fields
}

Experiment {
  id?: string              # Unique identifier (Extension 2)
  hypothesis: string       # What we expect to happen
  methodology: string      # How we'll test it
  expectedOutcome: string  # Predicted result
  actualOutcome?: string   # What actually happened
  measurements?: {         # Quantitative results (inline)
    metric: string         # What was measured (e.g., "latency", "accuracy")
    value: number          # Measured value
    unit?: string          # Unit of measurement
    baseline?: number      # Comparison baseline
    timestamp?: datetime   # When measured
    context?: string       # Conditions during measurement
  }[]
  confidence?: number      # 0-100: confidence in conclusions
  conclusion?: string      # Interpretation and next steps
  status: enum             # "planned" | "running" | "completed" | "failed" | "invalidated"
  startDate?: datetime     # When experiment began
  endDate?: datetime       # When experiment concluded
  metadata?: object        # Extension fields
}

Critique {
  author?: string          # Who performed the critique
  timestamp?: datetime     # When critique was performed
  scope: enum              # "technical" | "security" | "performance" | "usability" | "completeness"
  findings: {              # Identified issues or improvements (inline)
    severity: enum         # "critical" | "major" | "minor" | "suggestion"
    category: string       # Type of finding (e.g., "security", "performance")
    description: string    # What was found
    location?: string      # Where the issue exists (file, line, component)
    recommendation?: string # How to address it
    status?: enum          # "open" | "resolved" | "wont-fix" | "deferred"
  }[]
  overallAssessment?: string  # Summary judgment
  recommendations?: string[]  # Suggested next steps
}
```

### Extensions to Core Types

#### Plan Extensions

```javascript
Plan {
  // Core fields...
  constraints?: Constraint[]  # Requirements and boundaries
  experiments?: Experiment[]  # Hypothesis testing results
  narratives: {
    proposal: Narrative,      # Required (core)
    problem?: Narrative,      # Optional (core)
    context?: Narrative,      # Optional (core)
    
    // New experimental workflow narratives:
    constraints?: Narrative,  # Boundary definitions and requirements
    hypotheses?: Narrative,   # Initial assumptions and predictions
    critique?: Narrative,     # Review and self-assessment
    revision?: Narrative,     # Changes based on critique
    learnings?: Narrative,    # What was learned through experimentation
    
    // Existing optional narratives:
    alternatives?: Narrative,
    risks?: Narrative,
    testing?: Narrative,
    rollout?: Narrative,
    custom?: Narrative[]
  }
}
```

#### PlanItem Extensions

```javascript
PlanItem {
  // Core fields...
  constraints?: Constraint[]   # Item-specific requirements
  experiment?: Experiment      # Experimental work in this phase
  critique?: Critique          # Review of this phase's work
}
```

#### TodoItem Extensions

```javascript
TodoItem {
  // Core fields...
  constraints?: Constraint[]   # Task-specific requirements
  experiment?: Experiment      # If this task involves experimentation
}
```

## Usage Patterns

### Pattern 1: Constraint-Driven Development

Define explicit boundaries before starting work:

**JSON Example:**
```json
{
  "vBRIEFInfo": {"version": "0.3"},
  "plan": {
    "title": "API Response Optimization",
    "status": "inProgress",
    "constraints": [
      {
        "type": "performance",
        "rule": "P95 latency must be under 200ms",
        "priority": "must",
        "validation": "Run load test: npm run perf-test"
      },
      {
        "type": "output",
        "rule": "Response size must not exceed 10KB",
        "priority": "should",
        "rationale": "Mobile client bandwidth constraints"
      },
      {
        "type": "security",
        "rule": "No PII in logs or error messages",
        "priority": "must",
        "validation": "Security scan: npm run security-audit"
      }
    ],
    "narratives": {
      "proposal": {
        "title": "Approach",
        "content": "Implement caching layer with Redis..."
      },
      "constraints": {
        "title": "Requirements",
        "content": "## Performance\n- P95 latency < 200ms\n- Response size < 10KB\n\n## Security\n- No PII exposure\n- Rate limiting enabled"
      }
    }
  }
}
```

### Pattern 2: Hypothesis Testing

Track experiments and their outcomes:

**JSON Example:**
```json
{
  "vBRIEFInfo": {"version": "0.3"},
  "plan": {
    "title": "Database Query Optimization",
    "status": "inProgress",
    "experiments": [
      {
        "id": "exp-001",
        "hypothesis": "Adding an index on user_id will reduce query time by 50%",
        "methodology": "Create index, run benchmark suite 100 times, compare median query time",
        "expectedOutcome": "Query time reduces from 500ms to 250ms",
        "actualOutcome": "Query time reduced from 503ms to 178ms",
        "measurements": [
          {
            "metric": "query_time_p50",
            "value": 178,
            "unit": "ms",
            "baseline": 503,
            "timestamp": "2025-12-27T10:00:00Z"
          },
          {
            "metric": "index_size",
            "value": 45,
            "unit": "MB",
            "context": "Additional storage overhead"
          }
        ],
        "confidence": 95,
        "conclusion": "Hypothesis confirmed. Index provides 64% improvement with acceptable storage cost.",
        "status": "completed",
        "startDate": "2025-12-27T09:00:00Z",
        "endDate": "2025-12-27T10:30:00Z"
      }
    ],
    "narratives": {
      "proposal": {
        "title": "Optimization Strategy",
        "content": "Database queries on user_id are the primary bottleneck..."
      },
      "hypotheses": {
        "title": "Performance Hypotheses",
        "content": "## H1: Indexing Impact\nAdding B-tree index on user_id should reduce lookup time...\n\n## H2: Cache Hit Rate\nImplementing Redis cache should handle 80% of requests..."
      },
      "learnings": {
        "title": "Results and Insights",
        "content": "Index exceeded expectations (64% vs predicted 50%). Storage overhead (45MB) is acceptable..."
      }
    }
  }
}
```

### Pattern 3: Iterative Refinement Loop

Generate → Critique → Revise:

**JSON Example:**
```json
{
  "vBRIEFInfo": {"version": "0.3"},
  "plan": {
    "title": "Authentication System Design",
    "status": "inProgress",
    "items": [
      {
        "title": "Initial Design",
        "status": "completed",
        "description": "First pass at auth architecture"
      },
      {
        "title": "Design Critique",
        "status": "completed",
        "critique": {
          "author": "security-team",
          "timestamp": "2025-12-27T11:00:00Z",
          "scope": "security",
          "findings": [
            {
              "severity": "critical",
              "category": "security",
              "description": "JWT tokens have no expiration",
              "recommendation": "Add 1-hour expiration with refresh token mechanism",
              "status": "open"
            },
            {
              "severity": "major",
              "category": "security",
              "description": "Password reset tokens sent in URL",
              "recommendation": "Use POST body for sensitive tokens",
              "status": "open"
            }
          ],
          "overallAssessment": "Design has fundamental security issues that must be addressed",
          "recommendations": [
            "Implement token expiration",
            "Review OWASP guidelines for password reset",
            "Add rate limiting to auth endpoints"
          ]
        }
      },
      {
        "title": "Revised Design",
        "status": "inProgress",
        "description": "Addressing security findings from critique",
        "constraints": [
          {
            "type": "security",
            "rule": "All JWT tokens must expire within 1 hour",
            "priority": "must"
          },
          {
            "type": "security",
            "rule": "Password reset tokens sent only in POST body",
            "priority": "must"
          }
        ]
      }
    ],
    "narratives": {
      "proposal": "JWT-based authentication with email/password...",
      "critique": "## Critical Issues\n1. Token expiration missing\n2. Reset tokens in URL\n\n## Recommendations\nSee revised design phase...",
      "revision": "Based on security review:\n- Added 1hr JWT expiration\n- Implemented refresh token rotation\n- Moved reset tokens to POST body\n- Added rate limiting (10 req/min)"
    }
  }
}
```

### Pattern 4: AI-Assisted Work with Constraints

Using constraints to control LLM output quality:

**JSON Example:**
```json
{
  "vBRIEFInfo": {"version": "0.3"},
  "todoList": {
    "items": [
      {
        "title": "Generate API documentation",
        "status": "inProgress",
        "constraints": [
          {
            "type": "output",
            "rule": "Each endpoint description must be under 280 characters",
            "priority": "must",
            "rationale": "Fits in preview pane"
          },
          {
            "type": "style",
            "rule": "Include exactly one code example per endpoint",
            "priority": "must"
          },
          {
            "type": "style",
            "rule": "Use imperative mood for descriptions (e.g., 'Returns' not 'Will return')",
            "priority": "should"
          },
          {
            "type": "quality",
            "rule": "Avoid marketing jargon: 'revolutionary', 'game-changing', 'seamless'",
            "priority": "must",
            "rationale": "Technical documentation should be precise, not promotional"
          }
        ],
        "description": "Use LLM to generate OpenAPI docs with quality constraints enforced"
      }
    ]
  }
}
```

## Integration with Playbooks

Constraints and experimental outcomes can inform Playbook entries:

**Example workflow:**
1. Run experiment with constraints
2. Document outcomes in Plan
3. Extract learnings to Playbook as reusable strategies

**JSON Example (Playbook Entry from Experiment):**
```json
{
  "eventId": "evt-0155",
  "targetId": "entry-db-indexing",
  "operation": "append",
  "kind": "learning",
  "title": "Database indexing typically exceeds predictions",
  "narrative": {
    "Learning": "B-tree indexes on high-cardinality columns consistently perform 15-30% better than predicted. Factor this into estimates."
  },
  "tags": ["database", "performance", "indexing"],
  "evidence": ["exp-001", "exp-007", "exp-023"],
  "confidence": 0.85,
  "feedbackType": "executionOutcome",
  "status": "active",
  "createdAt": "2025-12-27T15:00:00Z"
}
```

## Best Practices

### Constraints
- **Be specific**: "Under 200ms" not "fast"
- **Be measurable**: Include validation method when possible
- **Prioritize**: Use must/should/could to guide trade-offs
- **Document rationale**: Explain why the constraint exists

### Experiments
- **One hypothesis per experiment**: Keep experiments focused
- **Measure quantitatively**: Use Measurement objects for data
- **Record baselines**: Always compare against something
- **Document methodology**: Make experiments reproducible
- **Update confidence**: Reflect uncertainty in conclusions

### Critiques
- **Be systematic**: Review security, performance, completeness
- **Categorize findings**: Use severity levels appropriately
- **Provide recommendations**: Don't just identify problems
- **Track resolution**: Update finding status as addressed

### Iterative Refinement
- **Separate phases**: Initial → Critique → Revision as distinct PlanItems
- **Link narratives**: Use proposal → critique → revision narrative flow
- **Preserve history**: Don't delete initial approaches
- **Document learnings**: Capture what changed and why

## Example: Complete Experimental Workflow

**JSON Example (Full cycle):**
```json
{
  "vBRIEFInfo": {
    "version": "0.3",
    "description": "Caching layer implementation with experimental validation"
  },
  "plan": {
    "title": "Implement Redis Caching Layer",
    "status": "completed",
    "constraints": [
      {
        "type": "performance",
        "rule": "Cache hit rate must exceed 70%",
        "priority": "must",
        "validation": "Monitor cache_hit_rate metric for 24 hours"
      },
      {
        "type": "performance",
        "rule": "Cache lookup latency under 5ms",
        "priority": "must"
      },
      {
        "type": "resource",
        "rule": "Memory usage under 2GB",
        "priority": "should"
      }
    ],
    "experiments": [
      {
        "id": "exp-cache-001",
        "hypothesis": "LRU eviction with 1GB memory will achieve 75% hit rate",
        "methodology": "Deploy to staging, replay production traffic for 24hr, measure hit rate",
        "expectedOutcome": "Hit rate: 75%, P95 latency: 3ms",
        "actualOutcome": "Hit rate: 82%, P95 latency: 2.1ms",
        "measurements": [
          {
            "metric": "cache_hit_rate",
            "value": 82.3,
            "unit": "percent",
            "baseline": 0
          },
          {
            "metric": "p95_latency",
            "value": 2.1,
            "unit": "ms",
            "baseline": 150.0
          }
        ],
        "confidence": 90,
        "conclusion": "LRU caching exceeded expectations. Ready for production.",
        "status": "completed",
        "startDate": "2025-12-25T10:00:00Z",
        "endDate": "2025-12-26T10:00:00Z"
      }
    ],
    "items": [
      {
        "title": "Initial Implementation",
        "status": "completed",
        "description": "Set up Redis, implement cache wrapper"
      },
      {
        "title": "Performance Testing",
        "status": "completed",
        "experiment": {
          "id": "exp-cache-001"
        }
      },
      {
        "title": "Code Review",
        "status": "completed",
        "critique": {
          "scope": "technical",
          "findings": [
            {
              "severity": "minor",
              "category": "reliability",
              "description": "No circuit breaker for Redis failures",
              "recommendation": "Add fallback to direct DB queries",
              "status": "resolved"
            }
          ],
          "overallAssessment": "Good implementation, minor reliability improvement needed"
        }
      },
      {
        "title": "Production Deployment",
        "status": "completed",
        "constraints": [
          {
            "type": "performance",
            "rule": "Gradual rollout: 10% → 50% → 100% over 3 days",
            "priority": "must"
          }
        ]
      }
    ],
    "narratives": {
      "proposal": {
        "title": "Caching Strategy",
        "content": "Implement Redis-based LRU cache for frequently accessed user data..."
      },
      "hypotheses": {
        "title": "Performance Predictions",
        "content": "Expect 75% cache hit rate based on access patterns analysis..."
      },
      "critique": {
        "title": "Review Findings",
        "content": "Code review identified missing circuit breaker pattern..."
      },
      "learnings": {
        "title": "Results",
        "content": "Cache performed better than predicted (82% vs 75% hit rate). LRU eviction was optimal choice."
      }
    }
  }
}
```

## TRON Examples

### Constraint Definition (TRON)
```tron
class Constraint: type, rule, priority, validation

[
  Constraint("performance", "P95 latency < 200ms", "must", "npm run perf-test"),
  Constraint("security", "No PII in logs", "must", "npm run security-audit"),
  Constraint("output", "Response size < 10KB", "should", null)
]
```

### Experiment (TRON)
```tron
class Experiment: hypothesis, methodology, expectedOutcome, actualOutcome, confidence, status
class Measurement: metric, value, unit, baseline

Experiment(
  "Index will reduce query time 50%",
  "Benchmark 100 runs with/without index",
  "500ms → 250ms",
  "503ms → 178ms",
  95,
  "completed"
)
```

## Integration with Other Extensions

### Agentic Patterns Extension
- Experiments map to the **reflection** pattern (hypothesis → test → reflect → adapt)
- Constraints guide the **planning** pattern
- Critiques enable the **reflection** pattern's self-assessment

### Model-First Reasoning Extension
- Constraints can map to MFR's `Constraint` type in `problemModel`
- Experiments validate problem model assumptions
- Both extensions support hypothesis-driven work

### Playbooks Extension
- Experimental outcomes feed PlaybookItems as evidence
- Successful constraint patterns become reusable strategies
- Critique findings inform anti-patterns in playbooks

## Compatibility

This extension is fully backward compatible with core vBRIEF v0.3. Documents without experimental workflow fields remain valid.

Tools that don't understand this extension should:
- Ignore `constraints`, `experiments`, and `critique` fields
- Treat new narrative types (`constraints`, `hypotheses`, `critique`, `revision`, `learnings`) as custom narratives
- Preserve unknown fields when rewriting documents

## Future Considerations

Potential future additions:
- **Statistical confidence intervals** for measurements
- **A/B test frameworks** with control/treatment tracking
- **Experiment dependencies** (this experiment requires that one first)
- **Automated constraint validation** via executable assertions
- **Constraint inheritance** from parent items to children
- **Experiment templates** for common testing patterns

---

## References

- **vBRIEF Core Specification v0.3**: README.md
- **Extension 3 (Rich Metadata)**: README.md#extension-3-rich-metadata
- **Extension 7 (Resources & References)**: README.md#extension-7-resources-references
- **Extension 12 (Playbooks)**: vBRIEF-extension-playbooks.md
- **Agentic Patterns Extension**: vBRIEF-extension-agentic-patterns.md
- **Model-First Reasoning Extension**: vBRIEF-extension-model-first-reasoning.md

---

## License

This specification is released under CC BY 4.0.

---

## Changelog

### Version 0.2 (2025-12-27)
- Updated to vBRIEF v0.3 terminology
- Embedded `Measurement` as inline object in `Experiment` (not separate type)
- Embedded `Finding` as inline object in `Critique` (not separate type)
- Added integration section showing relationship to Agentic Patterns, MFR, and Playbooks
- Minor clarifications to examples and best practices

### Version 0.1 (2025-12-27)
- Initial draft
- Separate Measurement and Finding types
