# vBRIEF Extension: Model-First Reasoning (MFR)

**Extension Name**: Model-First Reasoning (MFR)  
**Version**: 0.2 (Simplified)  
**Status**: Draft  
**Author**: Jonathan Taylor (visionik@pobox.com)  
**Date**: 2025-12-27

---

## Overview

This extension adds explicit problem modeling to vBRIEF Plans, inspired by [Kumar & Rana (2025)](https://arxiv.org/abs/2512.14474). Model-First Reasoning (MFR) argues that LLM planning failures arise from **implicit and unstable problem representations**. By requiring explicit models—defining entities, state, actions with preconditions/effects, and constraints—before generating plans, we dramatically reduce hallucinations and constraint violations.

**Key insight**: **PlanItems are already actions.** Rather than creating separate workflow types, we extend Plans and PlanItems to capture problem model semantics directly.

## Motivation

**Current limitations:**
- Agents maintain state in latent representations (prone to drift)
- Constraints are inferred rather than enforced
- Critical variables or constraints are omitted
- Long-horizon plans break under minor changes

**How MFR helps:**
- Forces externalization of problem structure before reasoning
- Provides structured scaffold without rigid formalism
- Enables automated constraint checking
- Creates interpretable, verifiable plans

## Dependencies

**Required:**
- vBRIEF Core (Plan, PlanItem)
- Extension 2 (Identifiers) - for referencing entities

**Recommended:**
- Extension 3 (Rich Metadata) - for annotations
- Extension 4 (Hierarchical) - for nested structures
- Extension 12 (Playbooks) - for reusable templates

---

## Design Principle: Plans Contain Their Models

Rather than introducing separate `ProblemModel` and `Action` types, we recognize that:

- **Plan** = The solution approach (already has narratives, items, status)
- **Plan.problemModel** = The explicit problem structure (new field)
- **PlanItems** = The actions to execute (already ordered, have status, dependencies)
- **PlanItem preconditions/effects** = Action semantics (new fields)

This keeps vBRIEF simple while enabling full MFR validation.

---

## Data Model Extensions

### Supporting Types

#### Entity

An object or agent in the problem domain.

```javascript
Entity {
  id: string                   // Unique identifier
  type: string                 // Entity type (e.g., "User", "Resource")
  description?: string         // Human-readable description
  properties?: object          // Static properties
}
```

#### StateVar

A property that can change during plan execution.

```javascript
StateVar {
  id: string                   // Unique identifier (e.g., "user.isAuthenticated")
  entity: string               // Which entity this belongs to
  name: string                 // Variable name
  type: enum                   // "boolean" | "number" | "string" | "enum" | "datetime"
  possibleValues?: any[]       // For enum types
  initialValue?: any           // Starting state
  description?: string
}
```

#### Condition

A logical condition on state variables.

```javascript
Condition {
  variable: string             // State variable ID
  operator: enum               // "==" | "!=" | ">" | ">=" | "<" | "<=" | "in" | "contains"
  value: any                   // Value to compare against
  description?: string
}
```

#### Effect

A state change caused by an action.

```javascript
Effect {
  variable: string             // State variable ID
  change: enum                 // "set" | "add" | "remove" | "increment" | "decrement"
  value?: any                  // New value or delta
  description?: string
}
```

#### Constraint

An invariant that must be maintained.

```javascript
Constraint {
  id: string
  description: string          // Human-readable constraint
  type: enum                   // "hard" | "soft"
  priority?: number            // For soft constraints (lower = higher priority)
  conditions: Condition[]      // Logical conditions that define the constraint
  scope?: enum                 // "global" | "phase" | "action"
  violation?: string           // What happens if violated
}
```

#### Goal

A desired end state.

```javascript
Goal {
  id: string
  description: string
  conditions: Condition[]      // Conditions that define success
  priority: number             // Goal importance (1=highest)
  optional: boolean            // Must achieve or nice-to-have?
}
```

#### ProblemModel

The explicit problem structure for a Plan.

```javascript
ProblemModel {
  entities: Entity[]           // Objects/agents in problem domain
  stateVariables: StateVar[]   // Properties that change
  constraints: Constraint[]    // Invariants to enforce
  goals: Goal[]                // Desired outcomes
  assumptions?: string[]       // Explicit assumptions made
}
```

**Note**: Actions are NOT in the problem model—**PlanItems are the actions.**

#### ValidationResult

Result of validating a plan against its problem model.

```javascript
ValidationResult {
  valid: boolean
  timestamp: datetime
  constraintViolations: ConstraintViolation[]
  preconditionViolations: PreconditionViolation[]
  goalsAchieved: string[]      // Goal IDs achieved
  goalsUnmet: string[]         // Goal IDs not achieved
  warnings: string[]
}
```

#### ConstraintViolation

```javascript
ConstraintViolation {
  constraintId: string
  violatedAt: string           // PlanItem ID
  actualState: object
  description: string
}
```

#### PreconditionViolation

```javascript
PreconditionViolation {
  planItemId: string
  unsatisfiedConditions: Condition[]
  actualState: object
}
```

---

## Plan Extensions

**Plans contain the problem model as a first-class field:**

```javascript
Plan {
  // Core + existing extensions...
  
  // MFR: Explicit problem model
  problemModel?: ProblemModel       // The problem structure
  
  // MFR: Validation results
  validationResults?: ValidationResult[]  // History of validation checks
  
  // MFR: Modeling metadata
  modelingApproach?: string         // How model was constructed (e.g., "manual", "template", "synthesized")
}
```

**Key insight**: The Plan's `items` array contains PlanItems, which ARE the actions that solve the problem.

---

## PlanItem Extensions

**PlanItems are actions with preconditions and effects:**

```javascript
PlanItem {
  // Core + existing extensions...
  
  // MFR: Action semantics
  preconditions?: Condition[]       // What must be true before executing this action
  effects?: Effect[]                // How this action changes state
  
  // MFR: State tracking
  stateBefore?: object              // State snapshot before execution
  stateAfter?: object               // State snapshot after execution
}
```

**Execution flow:**
1. Check `preconditions` against current state
2. If satisfied, execute the PlanItem
3. Apply `effects` to update state
4. Record `stateBefore` and `stateAfter`
5. Verify `constraints` still hold

---

## PlaybookItem Extensions

**Store reusable problem model templates:**

```javascript
PlaybookItem {
  // Core + Extension 12 fields...
  
  // MFR: Reusable templates
  problemModelTemplate?: ProblemModel  // Template for similar problems
  applicabilityConditions?: string[]   // When to use this template
  templateParameters?: TemplateParam[] // Customization points
}
```

#### TemplateParam

```javascript
TemplateParam {
  name: string
  type: string                 // "string" | "number" | "string[]" | etc.
  description: string
  defaultValue?: any
}
```

---

## Usage Examples

### Example 1: OAuth Implementation with MFR

**The Plan contains the problem model and PlanItems are the actions:**

```json
{
  "vBRIEFInfo": {
    "version": "0.3"
  },
  "plan": {
    "id": "oauth-plan-001",
    "title": "Add OAuth2 Support",
    "status": "proposed",
    
    "narratives": {
      "problem": {
        "title": "Problem Context",
        "content": "Users want Google/GitHub login. Current JWT-only limits adoption."
      },
      "proposal": {
        "title": "Proposed Approach",
        "content": "Add OAuth2 alongside JWT. OAuth for user login, JWT for API tokens."
      }
    },
    
    "problemModel": {
      "entities": [
        {
          "id": "user",
          "type": "User",
          "description": "Application user account",
          "properties": {"hasEmail": true}
        },
        {
          "id": "session",
          "type": "Session",
          "description": "User authentication session"
        },
        {
          "id": "oauthProvider",
          "type": "OAuthProvider",
          "description": "External OAuth provider (Google/GitHub)"
        }
      ],
      
      "stateVariables": [
        {
          "id": "user.isAuthenticated",
          "entity": "user",
          "name": "isAuthenticated",
          "type": "boolean",
          "initialValue": false
        },
        {
          "id": "user.authMethod",
          "entity": "user",
          "name": "authMethod",
          "type": "enum",
          "possibleValues": ["jwt", "oauth"],
          "initialValue": null
        },
        {
          "id": "session.active",
          "entity": "session",
          "name": "active",
          "type": "boolean",
          "initialValue": false
        },
        {
          "id": "session.tokenExpiry",
          "entity": "session",
          "name": "tokenExpiry",
          "type": "datetime",
          "initialValue": null
        },
        {
          "id": "oauth.configured",
          "entity": "oauthProvider",
          "name": "configured",
          "type": "boolean",
          "initialValue": false
        }
      ],
      
      "constraints": [
        {
          "id": "c1",
          "description": "Token must expire within 24 hours",
          "type": "hard",
          "priority": 1,
          "conditions": [
            {"variable": "session.tokenExpiry", "operator": "<=", "value": "now+24h"}
          ],
          "scope": "global"
        },
        {
          "id": "c2",
          "description": "OAuth must be configured before use",
          "type": "hard",
          "priority": 1,
          "conditions": [
            {"variable": "oauth.configured", "operator": "==", "value": true}
          ],
          "scope": "action"
        },
        {
          "id": "c3",
          "description": "Backward compatibility with JWT",
          "type": "soft",
          "priority": 2,
          "conditions": [
            {"variable": "user.authMethod", "operator": "in", "value": ["jwt", "oauth"]}
          ],
          "scope": "global"
        }
      ],
      
      "goals": [
        {
          "id": "g1",
          "description": "Users can login with Google OAuth",
          "conditions": [
            {"variable": "oauth.configured", "operator": "==", "value": true},
            {"variable": "user.isAuthenticated", "operator": "==", "value": true},
            {"variable": "user.authMethod", "operator": "==", "value": "oauth"}
          ],
          "priority": 1,
          "optional": false
        },
        {
          "id": "g2",
          "description": "JWT auth still works",
          "conditions": [
            {"variable": "user.authMethod", "operator": "==", "value": "jwt"},
            {"variable": "user.isAuthenticated", "operator": "==", "value": true}
          ],
          "priority": 2,
          "optional": false
        }
      ],
      
      "assumptions": [
        "OAuth providers support PKCE flow",
        "Users have existing Google/GitHub accounts",
        "Frontend can handle redirect flows"
      ]
    },
    
    "items": [
      {
        "id": "phase-1",
        "title": "Configure OAuth provider",
        "status": "completed",
        "description": "Setup OAuth credentials and endpoints",
        
        "preconditions": [
          {"variable": "oauth.configured", "operator": "==", "value": false}
        ],
        "effects": [
          {"variable": "oauth.configured", "change": "set", "value": true}
        ],
        
        "stateBefore": {
          "oauth.configured": false
        },
        "stateAfter": {
          "oauth.configured": true
        }
      },
      {
        "id": "phase-2",
        "title": "Implement OAuth flow",
        "status": "inProgress",
        "dependencies": ["phase-1"],
        
        "preconditions": [
          {"variable": "oauth.configured", "operator": "==", "value": true},
          {"variable": "user.isAuthenticated", "operator": "==", "value": false}
        ],
        "effects": [
          {"variable": "user.isAuthenticated", "change": "set", "value": true},
          {"variable": "user.authMethod", "change": "set", "value": "oauth"},
          {"variable": "session.active", "change": "set", "value": true},
          {"variable": "session.tokenExpiry", "change": "set", "value": "now+24h"}
        ]
      },
      {
        "id": "phase-3",
        "title": "Test OAuth login",
        "status": "pending",
        "dependencies": ["phase-2"],
        
        "preconditions": [
          {"variable": "session.active", "operator": "==", "value": true}
        ],
        "effects": []
      }
    ],
    
    "validationResults": [
      {
        "valid": true,
        "timestamp": "2025-12-27T10:00:00Z",
        "constraintViolations": [],
        "preconditionViolations": [],
        "goalsAchieved": ["g1", "g2"],
        "goalsUnmet": [],
        "warnings": []
      }
    ]
  }
}
```

### Example 2: Playbook Template for OAuth

**Store successful problem models for reuse:**

```json
{
  "vBRIEFInfo": {"version": "0.4"},
  "playbook": {
    "version": 1,
    "created": "2025-12-27T00:00:00Z",
    "updated": "2025-12-27T00:00:00Z",
    "items": [
      {
        "eventId": "evt-0001",
        "targetId": "oauth-pattern",
        "operation": "append",
        "kind": "strategy",
        "title": "OAuth2 Integration Pattern",
        "narrative": {"Summary": "Standard approach for adding OAuth2 to existing authentication systems"},
        "status": "active",
        "tags": ["oauth", "authentication", "security"],
        "createdAt": "2025-12-27T00:00:00Z",
        
        "problemModelTemplate": {
          "entities": [
            {"id": "user", "type": "User", "description": "Application user"},
            {"id": "session", "type": "Session", "description": "Auth session"},
            {"id": "oauthProvider", "type": "OAuthProvider", "description": "OAuth provider"}
          ],
          "stateVariables": [
            {
              "id": "user.isAuthenticated",
              "entity": "user",
              "name": "isAuthenticated",
              "type": "boolean",
              "initialValue": false
            },
            {
              "id": "oauth.configured",
              "entity": "oauthProvider",
              "name": "configured",
              "type": "boolean",
              "initialValue": false
            }
          ],
          "constraints": [
            {
              "id": "token-expiry",
              "description": "Tokens must expire within {expiryHours} hours",
              "type": "hard",
              "conditions": [
                {"variable": "session.tokenExpiry", "operator": "<=", "value": "now+{expiryHours}h"}
              ],
              "scope": "global"
            }
          ],
          "goals": [
            {
              "id": "oauth-working",
              "description": "Users can authenticate via OAuth",
              "conditions": [
                {"variable": "user.isAuthenticated", "operator": "==", "value": true}
              ],
              "priority": 1,
              "optional": false
            }
          ]
        },
        
        "templateParameters": [
          {
            "name": "expiryHours",
            "type": "number",
            "description": "Token expiry time in hours",
            "defaultValue": 24
          },
          {
            "name": "providers",
            "type": "string[]",
            "description": "OAuth providers to support",
            "defaultValue": ["google", "github"]
          }
        ],
        
        "applicabilityConditions": [
          "Adding OAuth to existing authentication",
          "Need to support multiple OAuth providers",
          "Security-conscious environment"
        ]
      }
    ]
  }
}
```

### Example 3: Validation Workflow

**Validate plan against its problem model:**

```typescript
function validatePlan(plan: Plan): ValidationResult {
  if (!plan.problemModel) {
    return {
      valid: false,
      timestamp: new Date().toISOString(),
      constraintViolations: [],
      preconditionViolations: [],
      goalsAchieved: [],
      goalsUnmet: [],
      warnings: ["No problem model defined"]
    };
  }
  
  const model = plan.problemModel;
  const violations: ConstraintViolation[] = [];
  const precondViolations: PreconditionViolation[] = [];
  
  // Initialize state from model
  let state: Record<string, any> = {};
  for (const stateVar of model.stateVariables) {
    state[stateVar.id] = stateVar.initialValue;
  }
  
  // Simulate plan execution through PlanItems
  for (const item of plan.items || []) {
    // Check preconditions
    if (item.preconditions) {
      const unsatisfied = item.preconditions.filter(
        cond => !evaluateCondition(cond, state)
      );
      
      if (unsatisfied.length > 0) {
        precondViolations.push({
          planItemId: item.id!,
          unsatisfiedConditions: unsatisfied,
          actualState: {...state}
        });
      }
    }
    
    // Apply effects
    if (item.effects) {
      for (const effect of item.effects) {
        state[effect.variable] = applyEffect(effect, state);
      }
    }
    
    // Check constraints
    for (const constraint of model.constraints) {
      if (constraint.type === "hard") {
        const satisfied = constraint.conditions.every(
          cond => evaluateCondition(cond, state)
        );
        
        if (!satisfied) {
          violations.push({
            constraintId: constraint.id,
            violatedAt: item.id!,
            actualState: {...state},
            description: `Constraint "${constraint.description}" violated`
          });
        }
      }
    }
  }
  
  // Check goal achievement
  const goalsAchieved = model.goals
    .filter(goal => goal.conditions.every(c => evaluateCondition(c, state)))
    .map(g => g.id);
  
  const goalsUnmet = model.goals
    .filter(goal => !goalsAchieved.includes(goal.id) && !goal.optional)
    .map(g => g.id);
  
  return {
    valid: violations.length === 0 && precondViolations.length === 0 && goalsUnmet.length === 0,
    timestamp: new Date().toISOString(),
    constraintViolations: violations,
    preconditionViolations: precondViolations,
    goalsAchieved,
    goalsUnmet,
    warnings: []
  };
}

function evaluateCondition(cond: Condition, state: Record<string, any>): boolean {
  const actual = state[cond.variable];
  
  switch (cond.operator) {
    case "==": return actual === cond.value;
    case "!=": return actual !== cond.value;
    case ">": return actual > cond.value;
    case ">=": return actual >= cond.value;
    case "<": return actual < cond.value;
    case "<=": return actual <= cond.value;
    case "in": return Array.isArray(cond.value) && cond.value.includes(actual);
    case "contains": return Array.isArray(actual) && actual.includes(cond.value);
    default: return false;
  }
}

function applyEffect(effect: Effect, state: Record<string, any>): any {
  const current = state[effect.variable];
  
  switch (effect.change) {
    case "set": return effect.value;
    case "increment": return (current || 0) + (effect.value || 1);
    case "decrement": return (current || 0) - (effect.value || 1);
    case "add": 
      return Array.isArray(current) 
        ? [...current, effect.value] 
        : [effect.value];
    case "remove":
      return Array.isArray(current)
        ? current.filter(v => v !== effect.value)
        : null;
    default: return current;
  }
}
```

---

## Two-Phase MFR Workflow

### Phase 1: Model Construction

Agent builds the problem model BEFORE planning:

```
PROMPT:
Given this requirement: "Add OAuth2 support to our authentication system"

First, construct an explicit problem model:
1. Entities: What objects/agents are involved?
2. State Variables: What properties can change?
3. Constraints: What rules must always be satisfied?
4. Goals: What are we trying to achieve?

Output the model in JSON format for the Plan.problemModel field.
DO NOT generate PlanItems yet.
```

### Phase 2: Solution Planning

Agent generates PlanItems that solve the model:

```
PROMPT:
Using ONLY the problem model defined above, generate PlanItems (actions).

For each PlanItem, specify:
- preconditions: What must be true before execution
- effects: How this action changes state

Ensure:
- Every action respects its preconditions
- All state transitions follow defined effects
- All constraints remain satisfied at every step
- All goals are achieved

Output as Plan.items array.
```

---

## Integration with Existing Extensions

### Extension 2: Identifiers
- Entity IDs, StateVar IDs, Constraint IDs all use Extension 2
- PlanItem IDs link to validation results

### Extension 4: Hierarchical
- PlanItems can have nested `subItems` representing sub-actions
- State variables can reference nested properties

### Extension 5: Workflow & Scheduling
- `startDate`/`endDate` on PlanItems show when actions executed
- `duration` can be compared against expected action costs

### Extension 6: Participants & Collaboration
- Different agents can work on different PlanItems
- Shared `problemModel` ensures consistency

### Extension 10: Version Control
- Track evolution of problem models over time
- `changeLog` records model refinements

### Extension 12: Playbooks
- Store successful `problemModelTemplate` in PlaybookItems
- Agents query playbooks before constructing models

---

## Benefits

### Reduced Hallucinations
- Explicit models prevent unstated assumptions
- Agents can't fabricate entities or actions
- Clear boundary between known and unknown

### Improved Consistency
- Long-horizon plans stay coherent via stable state representation
- State changes follow defined semantics
- Constraints enforced throughout execution

### Verifiability
- Plans can be automatically validated
- Violations surfaced as specific constraint breaks
- Debugging identifies exact failure point

### Reusability
- Successful models stored in Playbooks
- Templates reduce modeling effort for similar problems
- Domain knowledge captured explicitly

### Transparency
- Clear separation: "what is the problem" vs "how to solve it"
- Stakeholders can review models independently
- Non-technical users can understand structure

---

## When to Use MFR

**Strongly recommended:**
- Safety-critical systems (healthcare, infrastructure)
- Correctness-critical domains (financial, legal)
- Complex scheduling or resource allocation
- Multi-step procedural execution
- Long-horizon planning (>10 steps)
- Multiple interacting constraints

**Optional:**
- Medium complexity planning (5-10 steps)
- When debugging constraint violations
- When reusing similar problem patterns

**Not recommended:**
- Simple task lists (<5 items)
- Unconstrained brainstorming
- Purely narrative documentation
- Real-time reactive systems

---

## Comparison: v0.1 vs v0.2

### v0.1 (Original - 1450 lines)
- Separate `ProblemModel` top-level type
- Separate `Action` type with full semantics
- `Phase.requiredActions` linked to `Action` objects
- Problem model and actions duplicated across structures

### v0.2 (Simplified - this version)
- `Plan.problemModel` as first-class field (not in metadata)
- **PlanItems ARE the actions** - no separate Action type
- `PlanItem.preconditions` and `effects` define action semantics
- Single source of truth: PlanItems in execution order

**Token savings**: ~40% reduction in TRON encoding due to eliminating duplication.

---

## References

### Primary Research
- **Kumar, G. & Rana, A.** (2025). "Model-First Reasoning LLM Agents: Reducing Hallucinations through Explicit Problem Modeling". arXiv:2512.14474. https://arxiv.org/abs/2512.14474

### Classical AI Planning
- **Fikes, R. & Nilsson, N.** (1971). "STRIPS: A New Approach to the Application of Theorem Proving to Problem Solving".
- **McDermott, D. et al.** (1998). "PDDL - The Planning Domain Definition Language".

### vBRIEF
- vBRIEF Core Specification v0.3
- Extension 2: Identifiers
- Extension 4: Hierarchical Structures
- Extension 12: Playbooks

---

## License

This specification is released under CC BY 4.0.

---

## Changelog

### Version 0.2 (2025-12-27) - Simplified
- **Breaking change**: Remove separate `ProblemModel` top-level type
- **Design principle**: PlanItems ARE actions, not separate entities
- `Plan.problemModel` is now first-class field (not in metadata)
- `Plan.validationResults` is first-class field
- PlanItems get `preconditions`, `effects`, `stateBefore`, `stateAfter` fields
- Removed: separate `Action` type, `Phase.requiredActions`, `StateTransition`
- ~60% reduction in document size (1450 → 580 lines)
- ~40% reduction in token usage due to eliminating duplication

### Version 0.1 (2025-12-27) - Original
- Initial draft with separate ProblemModel and Action types
- Complex type hierarchy with duplication
