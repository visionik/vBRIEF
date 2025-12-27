# vAgenda Extension Proposal: Model-First Reasoning (MFR)

> **VERY EARLY DRAFT**: This is an initial proposal and subject to significant change. Comments, feedback, and suggestions are strongly encouraged. Please provide input via GitHub issues or discussions.

**Extension Name**: Model-First Reasoning (MFR)  
**Version**: 0.1 (Draft)  
**Status**: Proposal  
**Author**: Jonathan Taylor (visionik@pobox.com)  
**Date**: 2025-12-27

## Overview

This extension introduces explicit problem modeling to vAgenda, inspired by the Model-First Reasoning (MFR) paradigm described in [Kumar & Rana (2025)](https://arxiv.org/abs/2512.14474). MFR argues that many LLM planning failures arise not from reasoning deficiencies but from **implicit and unstable problem representations**. By requiring agents to explicitly construct a problem model—defining entities, state variables, actions with preconditions and effects, and constraints—before generating plans, we dramatically reduce hallucinations, constraint violations, and long-horizon inconsistencies.

This extension adds structured problem models to vAgenda Plans, enabling:
- **Explicit constraint definition and verification**
- **Reduced hallucinations** through grounded reasoning
- **Long-horizon consistency** via stable state representations
- **Automated plan validation** against stated constraints
- **Reusable problem templates** in ACE playbooks

## Motivation

**Current LLM agent limitations:**
- **Implicit state tracking**: Agents maintain state in latent representations, prone to drift and omission
- **Constraint violations**: Rules are inferred rather than explicitly enforced
- **Unstated assumptions**: Critical variables or constraints are omitted
- **Brittle long-horizon plans**: Solutions break under minor changes

**How Model-First Reasoning helps:**
- **Explicit representation**: Forces externalization of problem structure before reasoning
- **Soft symbolic grounding**: Provides structured scaffold without rigid formalism
- **Verifiable constraints**: Enables automated checking of plan validity
- **Interpretable reasoning**: Clear separation between "what is the problem" and "how to solve it"

**Research foundation:**

Kumar & Rana (2025) demonstrate that separating modeling from reasoning substantially reduces constraint violations and improves solution quality compared to Chain-of-Thought (CoT) and ReAct strategies. The key insight: **hallucinations are representational failures, not inferential failures**.

**Integration goal**: Enable vAgenda to support rigorous, constraint-driven planning for complex, safety-critical, or correctness-critical domains while maintaining flexibility for simpler use cases.

## Dependencies

**Required**:
- Core vAgenda types (vAgendaInfo, Plan, Phase, TodoItem)
- Extension 2 (Identifiers) - for referencing entities and actions

**Recommended**:
- Extension 3 (Rich Metadata) - for model annotations
- Extension 4 (Hierarchical) - for nested state structures
- Extension 12 (ACE) - for storing reusable problem models
- Extension 10 (Version Control) - for tracking model evolution

## Core Concepts

### Two-Phase Planning

MFR introduces a two-phase approach:

**Phase 1: Model Construction**
- Agent explicitly defines problem structure
- Entities, state variables, actions, constraints are formalized
- No solution steps generated yet

**Phase 2: Reasoning & Planning**
- Agent generates solution **strictly within the defined model**
- Each action must respect preconditions
- Each state transition must follow defined effects
- All constraints must be satisfied at every step

This separation provides a **representational scaffold** that constrains subsequent reasoning.

### Problem Model Components

A problem model consists of:

1. **Entities**: Objects or agents in the problem space
2. **State Variables**: Properties that can change over time
3. **Actions**: Operations that modify state, with preconditions and effects
4. **Constraints**: Invariants that must always be satisfied
5. **Goals**: Desired end states

## New Types

### ProblemModel

Top-level problem representation for a Plan.

```javascript
ProblemModel {
  entities: Entity[]           # Objects/agents in problem domain
  stateVariables: StateVar[]   # Properties that change
  actions: Action[]            # Operations with semantics
  constraints: Constraint[]    # Invariants to enforce
  goals: Goal[]               # Desired outcomes
  assumptions?: string[]       # Explicit assumptions made
}
```

### Entity

An object or agent in the problem space.

```javascript
Entity {
  id: string                   # Unique identifier
  type: string                 # Entity type (e.g., "User", "Resource", "Task")
  description?: string         # Human-readable description
  properties?: Record<string, any>  # Static properties
}
```

### StateVar

A property of an entity that can change during plan execution.

```javascript
StateVar {
  id: string                   # Unique identifier (e.g., "user.isAuthenticated")
  entity: string               # Which entity this belongs to
  name: string                 # Variable name
  type: enum                   # "boolean" | "number" | "string" | "enum" | "set" | "datetime"
  possibleValues?: any[]       # For enum types
  initialValue?: any           # Starting state
  description?: string
}
```

### Action

An operation that modifies state.

```javascript
Action {
  id: string                   # Unique identifier
  name: string                 # Action name
  description?: string         # What this action does
  parameters?: Parameter[]     # Action parameters
  preconditions: Condition[]   # Must be true before execution
  effects: Effect[]            # How state changes
  duration?: duration          # ISO 8601 duration (e.g., "PT30M")
  cost?: number                # Resource cost
}
```

### Parameter

A parameter for an action.

```javascript
Parameter {
  name: string
  type: string                 # "string" | "number" | "entity" | etc.
  required: boolean
  description?: string
}
```

### Condition

A logical condition on state variables.

```javascript
Condition {
  variable: string             # State variable ID
  operator: enum               # "==" | "!=" | ">" | ">=" | "<" | "<=" | "in" | "contains"
  value: any                   # Value to compare against
  description?: string
}
```

### Effect

A state change caused by an action.

```javascript
Effect {
  variable: string             # State variable ID
  change: enum                 # "set" | "add" | "remove" | "increment" | "decrement"
  value?: any                  # New value or delta
  description?: string
}
```

### Constraint

An invariant that must be maintained.

```javascript
Constraint {
  id: string
  description: string          # Human-readable constraint
  type: enum                   # "hard" | "soft" | "temporal"
  priority?: number            # For soft constraints
  conditions: Condition[]      # Logical conditions
  scope?: enum                 # "global" | "phase" | "action"
  violation?: string           # What happens if violated
}
```

### Goal

A desired end state.

```javascript
Goal {
  id: string
  description: string
  conditions: Condition[]      # Conditions that define success
  priority: number             # Goal importance (1=highest)
  optional: boolean            # Must achieve or nice-to-have?
}
```

### ValidationResult

Result of validating a plan against its problem model.

```javascript
ValidationResult {
  valid: boolean
  constraintViolations: ConstraintViolation[]
  preconditionViolations: PreconditionViolation[]
  effectInconsistencies: EffectInconsistency[]
  goalsAchieved: string[]      # Goal IDs achieved
  goalsUnmet: string[]         # Goal IDs not achieved
  warnings: string[]
}
```

### ConstraintViolation

A constraint that was violated.

```javascript
ConstraintViolation {
  constraint: Constraint
  violatedAt: string           # Phase ID or step number
  actualState: Record<string, any>
  description: string
}
```

### PreconditionViolation

An action executed without satisfying preconditions.

```javascript
PreconditionViolation {
  action: Action
  executedAt: string           # Phase ID or step number
  unsatisfiedConditions: Condition[]
  actualState: Record<string, any>
}
```

### EffectInconsistency

An effect that wasn't properly applied.

```javascript
EffectInconsistency {
  action: Action
  effect: Effect
  executedAt: string
  expectedState: any
  actualState: any
  description: string
}
```

## Plan Extensions

```javascript
Plan {
  // Core fields...
  problemModel?: ProblemModel        # MFR explicit problem model
  modelingApproach?: string          # How model was constructed
  validationResults?: ValidationResult[]  # Results of validation checks
}
```

## Phase Extensions

```javascript
Phase {
  // Prior extensions...
  requiredActions?: string[]         # Action IDs from problem model
  stateTransitions?: StateTransition[]  # Expected state changes
  preconditionState?: Record<string, any>  # State before phase
  postconditionState?: Record<string, any>  # State after phase
}
```

### StateTransition

```javascript
StateTransition {
  variable: string               # State variable ID
  from: any                      # Value before
  to: any                        # Value after
  via: string                    # Action ID that caused change
}
```

## TodoItem Extensions

```javascript
TodoItem {
  // Prior extensions...
  actionId?: string              # Reference to Action in problem model
  requiredPreconditions?: Condition[]  # What must be true before
  expectedEffects?: Effect[]     # What should change
  stateSnapshot?: Record<string, any>  # State when task was created
}
```

## ACE Playbook Extensions

For Extension 12 (ACE), store reusable problem models:

```javascript
PlaybookEntry {
  // Prior extensions...
  problemModelTemplate?: ProblemModel  # Reusable model
  applicabilityConditions?: string[]   # When to use this template
  successRate?: number                 # How often this model worked
  commonPitfalls?: string[]           # Known issues with this model
}
```

## Usage Patterns

### Pattern 1: OAuth Implementation with Explicit Model

**Use case**: Add OAuth support with explicit problem modeling.

```tron
class ProblemModel: entities, stateVariables, actions, constraints, goals
class Entity: id, type, description, properties
class StateVar: id, entity, name, type, initialValue
class Action: id, name, preconditions, effects
class Condition: variable, operator, value
class Effect: variable, change, value
class Constraint: id, description, type, conditions
class Goal: id, description, conditions, priority, optional

vAgendaInfo: vAgendaInfo("0.2", "alice@example.com")

plan: Plan(
  "Add OAuth2 Support",
  "proposed",
  {
    problem: Narrative(
      "Problem Context",
      "Users want Google/GitHub login. Current JWT-only limits adoption."
    ),
    proposal: Narrative(
      "Proposed Approach",
      "Add OAuth2 alongside JWT. OAuth for user login, JWT for API tokens."
    )
  },
  [
    Phase("OAuth provider integration", "pending", null, 1),
    Phase("User model updates", "pending", null, 2),
    Phase("Token management", "pending", null, 3),
    Phase("Testing & validation", "pending", null, 4)
  ],
  # Problem Model
  ProblemModel(
    # Entities
    [
      Entity("user", "User", "Application user account", {hasEmail: true}),
      Entity("session", "Session", "User authentication session", {}),
      Entity("oauthProvider", "OAuthProvider", "External OAuth provider", {})
    ],
    # State Variables
    [
      StateVar("user-1", "user", "isAuthenticated", "boolean", false),
      StateVar("user-2", "user", "authMethod", "enum", null, ["jwt", "oauth"]),
      StateVar("session-1", "session", "active", "boolean", false),
      StateVar("session-2", "session", "tokenExpiry", "datetime", null),
      StateVar("session-3", "session", "provider", "string", null),
      StateVar("oauth-1", "oauthProvider", "configured", "boolean", false)
    ],
    # Actions
    [
      Action(
        "configure-provider",
        "Configure OAuth provider",
        null,
        [Condition("oauth-1", "==", false)],
        [Effect("oauth-1", "set", true)]
      ),
      Action(
        "initiate-oauth-flow",
        "User starts OAuth login",
        null,
        [
          Condition("oauth-1", "==", true),
          Condition("user-1", "==", false)
        ],
        [Effect("session-1", "set", "pending")]
      ),
      Action(
        "complete-oauth",
        "OAuth callback completes",
        null,
        [Condition("session-1", "==", "pending")],
        [
          Effect("user-1", "set", true),
          Effect("user-2", "set", "oauth"),
          Effect("session-1", "set", true),
          Effect("session-2", "set", "now+24h")
        ]
      ),
      Action(
        "logout",
        "User logs out",
        null,
        [Condition("session-1", "==", true)],
        [
          Effect("user-1", "set", false),
          Effect("session-1", "set", false)
        ]
      )
    ],
    # Constraints
    [
      Constraint(
        "c1",
        "Token must expire within 24 hours",
        "hard",
        1,
        [Condition("session-2", "<=", "now+24h")],
        "global"
      ),
      Constraint(
        "c2",
        "User can have max 1 active session",
        "hard",
        1,
        [Condition("count(session.active=true)", "<=", 1)],
        "global"
      ),
      Constraint(
        "c3",
        "OAuth must be configured before use",
        "hard",
        1,
        [Condition("oauth-1", "==", true)],
        "action"
      ),
      Constraint(
        "c4",
        "Backward compatibility with JWT",
        "soft",
        2,
        [Condition("user-2", "in", ["jwt", "oauth"])],
        "global"
      )
    ],
    # Goals
    [
      Goal(
        "g1",
        "Users can login with Google OAuth",
        [
          Condition("oauth-1", "==", true),
          Condition("session-3", "==", "google"),
          Condition("user-1", "==", true)
        ],
        1,
        false
      ),
      Goal(
        "g2",
        "Users can login with GitHub OAuth",
        [
          Condition("oauth-1", "==", true),
          Condition("session-3", "==", "github"),
          Condition("user-1", "==", true)
        ],
        1,
        false
      ),
      Goal(
        "g3",
        "JWT auth still works",
        [
          Condition("user-2", "==", "jwt"),
          Condition("user-1", "==", true)
        ],
        2,
        false
      )
    ],
    # Assumptions
    [
      "OAuth providers support PKCE flow",
      "Users have existing Google/GitHub accounts",
      "Frontend can handle redirect flows"
    ]
  )
)
```

### Pattern 2: Model-Driven TodoList Generation

**Use case**: Generate todos from problem model actions.

```typescript
// Agent constructs problem model first
const model: ProblemModel = {
  entities: [...],
  stateVariables: [...],
  actions: [
    {
      id: "act-1",
      name: "configure-provider",
      preconditions: [...],
      effects: [...]
    },
    {
      id: "act-2",
      name: "initiate-oauth-flow",
      preconditions: [...],
      effects: [...]
    }
  ],
  constraints: [...],
  goals: [...]
};

// Then generates todos that implement each action
const todoList: TodoList = {
  items: model.actions.map(action => ({
    title: action.name,
    description: action.description,
    status: "pending",
    actionId: action.id,
    requiredPreconditions: action.preconditions,
    expectedEffects: action.effects
  }))
};
```

### Pattern 3: Plan Validation

**Use case**: Validate that a plan satisfies all constraints.

```typescript
function validatePlan(plan: Plan): ValidationResult {
  if (!plan.problemModel) {
    return {
      valid: false,
      constraintViolations: [],
      preconditionViolations: [],
      effectInconsistencies: [],
      goalsAchieved: [],
      goalsUnmet: plan.problemModel?.goals.map(g => g.id) || [],
      warnings: ["No problem model defined"]
    };
  }
  
  const model = plan.problemModel;
  const violations: ConstraintViolation[] = [];
  const precondViolations: PreconditionViolation[] = [];
  
  // Simulate plan execution
  let state = initializeState(model.stateVariables);
  
  for (const phase of plan.phases || []) {
    // Check if phase actions can execute
    for (const actionId of phase.requiredActions || []) {
      const action = model.actions.find(a => a.id === actionId);
      if (!action) continue;
      
      // Check preconditions
      const unsatisfied = action.preconditions.filter(
        cond => !evaluateCondition(cond, state)
      );
      
      if (unsatisfied.length > 0) {
        precondViolations.push({
          action,
          executedAt: phase.id!,
          unsatisfiedConditions: unsatisfied,
          actualState: {...state}
        });
      }
      
      // Apply effects
      for (const effect of action.effects) {
        state[effect.variable] = applyEffect(effect, state);
      }
    }
    
    // Check constraints after phase
    for (const constraint of model.constraints) {
      if (constraint.type === "hard") {
        const satisfied = constraint.conditions.every(
          cond => evaluateCondition(cond, state)
        );
        
        if (!satisfied) {
          violations.push({
            constraint,
            violatedAt: phase.id!,
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
    .filter(goal => !goalsAchieved.includes(goal.id))
    .map(g => g.id);
  
  return {
    valid: violations.length === 0 && precondViolations.length === 0,
    constraintViolations: violations,
    preconditionViolations: precondViolations,
    effectInconsistencies: [],
    goalsAchieved,
    goalsUnmet,
    warnings: []
  };
}
```

### Pattern 4: ACE Playbook with Reusable Models

**Use case**: Store successful problem models for future projects.

```tron
class PlaybookEntry: category, title, content, tags, problemModelTemplate

playbook: Playbook([
  PlaybookEntry(
    "patterns",
    "OAuth2 Integration Pattern",
    "Standard approach for adding OAuth2 to existing auth system",
    ["oauth", "authentication", "security"],
    ProblemModel(
      # Template entities
      [
        Entity("user", "User", "Application user", {}),
        Entity("session", "Session", "Auth session", {}),
        Entity("oauthProvider", "OAuthProvider", "OAuth provider", {})
      ],
      # Template state variables
      [
        StateVar("user-auth", "user", "isAuthenticated", "boolean", false),
        StateVar("session-active", "session", "active", "boolean", false)
      ],
      # Template actions
      [
        Action("configure-provider", "Setup OAuth", null, [], []),
        Action("oauth-login", "User OAuth login", null, [], []),
        Action("oauth-callback", "Handle callback", null, [], [])
      ],
      # Template constraints
      [
        Constraint("token-expiry", "Tokens expire <24h", "hard", 1, [], "global")
      ],
      [],
      ["OAuth provider supports PKCE"]
    )
  )
])
```

When agent encounters similar task:
```
1. Query ACE playbook for "oauth authentication"
2. Retrieve problemModelTemplate
3. Adapt template to specific requirements
4. Construct plan using adapted model
5. Validate plan against model
```

### Pattern 5: Incremental Model Refinement

**Use case**: Start with simple model, refine as issues discovered.

```typescript
// Initial simple model
let model: ProblemModel = {
  entities: [
    { id: "user", type: "User", description: "Application user" }
  ],
  stateVariables: [
    { id: "user-auth", entity: "user", name: "isAuthenticated", 
      type: "boolean", initialValue: false }
  ],
  actions: [
    { id: "login", name: "login", preconditions: [], 
      effects: [{ variable: "user-auth", change: "set", value: true }] }
  ],
  constraints: [],
  goals: []
};

// Validation reveals missing constraint
const result = validatePlan(plan);
if (result.constraintViolations.length > 0) {
  // Agent adds missing constraint to model
  model.constraints.push({
    id: "rate-limit",
    description: "Max 5 login attempts per hour",
    type: "hard",
    priority: 1,
    conditions: [
      { variable: "login-attempts", operator: "<=", value: 5 }
    ],
    scope: "global"
  });
  
  // Add missing state variable
  model.stateVariables.push({
    id: "login-attempts",
    entity: "user",
    name: "loginAttempts",
    type: "number",
    initialValue: 0
  });
}
```

### Pattern 6: Multi-Agent Coordination via Shared Model

**Use case**: Multiple agents work on same plan using shared problem model.

```typescript
// Agent A defines problem model
const sharedPlan: Plan = {
  title: "Distributed System Deployment",
  problemModel: {
    entities: [
      { id: "service-a", type: "Service", description: "Auth service" },
      { id: "service-b", type: "Service", description: "API service" },
      { id: "database", type: "Database", description: "PostgreSQL" }
    ],
    stateVariables: [
      { id: "db-ready", entity: "database", name: "ready", 
        type: "boolean", initialValue: false },
      { id: "service-a-deployed", entity: "service-a", name: "deployed",
        type: "boolean", initialValue: false }
    ],
    actions: [...],
    constraints: [
      {
        id: "dependency-order",
        description: "Database must be ready before services deploy",
        type: "hard",
        conditions: [
          { variable: "db-ready", operator: "==", value: true }
        ],
        scope: "action"
      }
    ],
    goals: [...]
  },
  phases: [...]
};

// Agent B validates their work against shared model
const agentBTodo: TodoItem = {
  title: "Deploy service-a",
  actionId: "deploy-service-a",
  status: "pending"
};

// Check preconditions before executing
const action = sharedPlan.problemModel.actions.find(
  a => a.id === agentBTodo.actionId
);

if (action) {
  const canExecute = action.preconditions.every(
    cond => currentState[cond.variable] === cond.value
  );
  
  if (!canExecute) {
    console.log("Cannot execute: preconditions not met");
    // Wait for Agent A to complete database setup
  }
}
```

### Pattern 7: Constraint-Driven Debugging

**Use case**: Plan fails, use model to identify root cause.

```typescript
const plan: Plan = {
  title: "Failed OAuth Implementation",
  problemModel: {...},
  phases: [...],
  validationResults: [
    {
      valid: false,
      constraintViolations: [
        {
          constraint: {
            id: "c1",
            description: "OAuth must be configured before use",
            type: "hard",
            conditions: [
              { variable: "oauth-configured", operator: "==", value: true }
            ]
          },
          violatedAt: "phase-2",
          actualState: { "oauth-configured": false },
          description: "Tried to use OAuth before configuration"
        }
      ],
      preconditionViolations: [],
      effectInconsistencies: [],
      goalsAchieved: [],
      goalsUnmet: ["g1", "g2"],
      warnings: []
    }
  ]
};

// Debug message for agent/human
console.log(`
Plan validation failed:
- Constraint violated: "OAuth must be configured before use"
- Occurred at: Phase 2 ("User login implementation")
- Root cause: oauth-configured = false when action executed
- Fix: Add Phase 1 to configure OAuth provider first
`);
```

## Implementation Notes

### Prompt Structure for MFR

To use MFR with LLM agents:

**Phase 1 Prompt (Model Construction):**
```
Given this project requirement: [DESCRIPTION]

First, construct an explicit problem model by defining:
1. Entities: What objects/agents are involved?
2. State Variables: What properties can change?
3. Actions: What operations are possible? (with preconditions and effects)
4. Constraints: What rules must always be satisfied?
5. Goals: What are we trying to achieve?

Output the model in vAgenda TRON format.
Do NOT propose a solution yet.
```

**Phase 2 Prompt (Reasoning):**
```
Using ONLY the problem model defined above, generate a step-by-step plan.

Ensure:
- Every action respects its preconditions
- All state transitions follow defined effects  
- All constraints remain satisfied at every step
- All goals are achieved

Output the plan in vAgenda TRON format.
```

### Validation Algorithm

```typescript
interface ValidationContext {
  model: ProblemModel;
  currentState: Record<string, any>;
  executionTrace: ExecutionStep[];
}

interface ExecutionStep {
  phaseId: string;
  actionId: string;
  stateBefore: Record<string, any>;
  stateAfter: Record<string, any>;
}

function validatePlanExecution(
  plan: Plan,
  trace: ExecutionStep[]
): ValidationResult {
  if (!plan.problemModel) {
    throw new Error("Plan has no problem model");
  }
  
  const violations: ConstraintViolation[] = [];
  const precondViolations: PreconditionViolation[] = [];
  const model = plan.problemModel;
  
  // Check each step in execution trace
  for (const step of trace) {
    const action = model.actions.find(a => a.id === step.actionId);
    if (!action) continue;
    
    // 1. Verify preconditions were satisfied
    for (const precond of action.preconditions) {
      if (!evaluateCondition(precond, step.stateBefore)) {
        precondViolations.push({
          action,
          executedAt: step.phaseId,
          unsatisfiedConditions: [precond],
          actualState: step.stateBefore
        });
      }
    }
    
    // 2. Verify effects were applied correctly
    for (const effect of action.effects) {
      const expected = applyEffect(effect, step.stateBefore);
      const actual = step.stateAfter[effect.variable];
      
      if (expected !== actual) {
        // Effect inconsistency detected
      }
    }
    
    // 3. Verify constraints still hold
    for (const constraint of model.constraints) {
      if (constraint.type === "hard") {
        const satisfied = constraint.conditions.every(
          c => evaluateCondition(c, step.stateAfter)
        );
        
        if (!satisfied) {
          violations.push({
            constraint,
            violatedAt: step.phaseId,
            actualState: step.stateAfter,
            description: `Constraint violated: ${constraint.description}`
          });
        }
      }
    }
  }
  
  return {
    valid: violations.length === 0 && precondViolations.length === 0,
    constraintViolations: violations,
    preconditionViolations: precondViolations,
    effectInconsistencies: [],
    goalsAchieved: [],
    goalsUnmet: [],
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
    case "increment": return current + (effect.value || 1);
    case "decrement": return current - (effect.value || 1);
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

### Model Templates

Problem models can be templatized for reuse:

```typescript
interface ProblemModelTemplate {
  name: string;
  description: string;
  category: string;
  parameters: TemplateParameter[];
  template: ProblemModel;
}

interface TemplateParameter {
  name: string;
  type: string;
  description: string;
  defaultValue?: any;
}

// Example: OAuth template
const oauthTemplate: ProblemModelTemplate = {
  name: "oauth-integration",
  description: "Add OAuth2 to existing system",
  category: "authentication",
  parameters: [
    {
      name: "providers",
      type: "string[]",
      description: "OAuth providers to support",
      defaultValue: ["google", "github"]
    },
    {
      name: "tokenExpiry",
      type: "duration",
      description: "Token expiration time",
      defaultValue: "24h"
    }
  ],
  template: {
    entities: [
      { id: "user", type: "User", description: "Application user" },
      { id: "session", type: "Session", description: "Auth session" },
      { id: "provider", type: "OAuthProvider", description: "OAuth provider" }
    ],
    // ... rest of template
  }
};

// Instantiate template
function instantiateTemplate(
  template: ProblemModelTemplate,
  params: Record<string, any>
): ProblemModel {
  // Replace template parameters with actual values
  const model = JSON.parse(JSON.stringify(template.template));
  
  // Customize based on params
  // ...
  
  return model;
}
```

## Integration with Existing Extensions

### Extension 2 (Identifiers)

Entities, actions, state variables all require unique IDs:
- Entity IDs reference specific objects
- Action IDs link TodoItems to problem model
- State variable IDs used in conditions and effects

### Extension 4 (Hierarchical)

Problem models can be hierarchical:
- Entities can have nested sub-entities
- Actions can be composed of sub-actions
- State variables can reference nested properties

### Extension 10 (Version Control)

Track evolution of problem models:
- Model refinements tracked as versions
- Changes to constraints, actions logged
- Validation results tied to model version

### Extension 12 (ACE)

Store successful models as institutional knowledge:
- Playbook entries include `problemModelTemplate`
- Agents query playbook before constructing models
- Success rate tracked for each template

### MCP Extension

Expose MFR validation via MCP tools:

```typescript
// MCP tool definitions
{
  name: "vagenda_validate_plan",
  description: "Validate plan against its problem model",
  inputSchema: {
    type: "object",
    properties: {
      planId: { type: "string" }
    },
    required: ["planId"]
  }
}

{
  name: "vagenda_check_preconditions",
  description: "Check if action preconditions are satisfied",
  inputSchema: {
    type: "object",
    properties: {
      actionId: { type: "string" },
      currentState: { type: "object" }
    },
    required: ["actionId", "currentState"]
  }
}

{
  name: "vagenda_verify_constraints",
  description: "Verify all constraints are satisfied",
  inputSchema: {
    type: "object",
    properties: {
      planId: { type: "string" },
      atPhaseIndex: { type: "number" }
    },
    required: ["planId"]
  }
}
```

## Benefits and Tradeoffs

### Benefits

**Reduced Hallucinations:**
- Explicit models prevent unstated assumptions
- Agents can't fabricate entities or actions
- Clear boundary between known and unknown

**Improved Consistency:**
- Long-horizon plans stay coherent
- State changes follow defined semantics
- Constraints enforced throughout execution

**Verifiability:**
- Plans can be automatically validated
- Violations surfaced as specific constraint breaks
- Debugging identifies exact failure point

**Reusability:**
- Successful models stored in ACE playbooks
- Templates reduce modeling effort
- Domain knowledge captured explicitly

**Interpretability:**
- Clear separation: what is problem vs how to solve
- Stakeholders can review models independently
- Non-technical users can understand structure

### Tradeoffs

**Increased Verbosity:**
- Problem models add significant content
- TRON encoding mitigates but doesn't eliminate
- Token overhead for model construction

**Modeling Overhead:**
- Requires upfront effort to build model
- May be overkill for simple tasks
- Effectiveness depends on model quality

**Not All Tasks Benefit:**
- Best for constraint-driven, structured planning
- Less useful for open-ended creative tasks
- May be unnecessary for short-horizon work

**Model Accuracy Matters:**
- Incorrect model leads to invalid plans
- Garbage in, garbage out
- Requires validation of model itself

## When to Use MFR

**Strongly recommended:**
- Safety-critical systems (healthcare, infrastructure)
- Correctness-critical domains (financial, legal)
- Complex scheduling or resource allocation
- Multi-step procedural execution
- Long-horizon planning (>10 steps)
- Multiple interacting constraints

**Optional/experimental:**
- Medium complexity planning (5-10 steps)
- Exploratory or creative tasks
- Rapid prototyping phases

**Not recommended:**
- Simple task lists (<5 items)
- Unconstrained brainstorming
- Purely narrative documentation
- Real-time reactive systems

## Migration Path

### Phase 1: Optional Extension (Current)

- MFR available as Extension 13
- Plans can optionally include problemModel
- No breaking changes to existing vAgenda
- Agents can adopt incrementally

### Phase 2: Tooling Support

- Validation tools for problem models
- MCP endpoints for constraint checking
- Templates in ACE playbooks
- IDE/editor support for MFR

### Phase 3: Best Practices

- Document when to use MFR
- Provide model templates for common domains
- Build validation into agent workflows
- Track success metrics

### Phase 4: Advanced Features

- Automated model synthesis from examples
- Model diff and merge for collaboration
- Formal verification integration
- Machine learning on model patterns

## Open Questions

1. **Model Granularity**: How detailed should models be? When is "good enough" sufficient?

2. **Model Synthesis**: Can we automatically generate models from existing plans or code?

3. **Validation Performance**: For large models (100+ state variables), validation could be expensive. How to optimize?

4. **Model Evolution**: How to handle model changes mid-project? Versioning? Migration?

5. **Formal Methods**: Should we integrate formal verification tools (TLA+, Alloy)?

6. **Partial Models**: Can agents start with partial models and refine iteratively?

7. **Model Sharing**: Standard format for exchanging models between organizations?

## Community Feedback

We're seeking feedback on:

1. **Complexity**: Is the type system too complex? Should we simplify?
2. **Granularity**: What level of detail is practical for real-world use?
3. **Tooling**: What validation tools are most needed?
4. **Templates**: Which domains should have standard templates?
5. **Integration**: How should MFR integrate with existing tools (Aider, Cursor, etc.)?
6. **Performance**: Is token overhead acceptable given benefits?

Please provide feedback via:
- GitHub issues: https://github.com/visionik/vAgenda/issues
- GitHub discussions: https://github.com/visionik/vAgenda/discussions
- Email: visionik@pobox.com

## References

### Primary Research
- **Kumar, G. & Rana, A.** (2025). "Model-First Reasoning LLM Agents: Reducing Hallucinations through Explicit Problem Modeling". arXiv:2512.14474. https://arxiv.org/abs/2512.14474

### Classical AI Planning
- **Fikes, R. & Nilsson, N.** (1971). "STRIPS: A New Approach to the Application of Theorem Proving to Problem Solving". *Artificial Intelligence*.
- **McDermott, D. et al.** (1998). "PDDL - The Planning Domain Definition Language". *AIPS-98 Planning Competition Committee*.

### Cognitive Science
- **Johnson-Laird, P.N.** (1983). *Mental Models: Towards a Cognitive Science of Language, Inference, and Consciousness*. Harvard University Press.

### LLM Reasoning
- **Wei, J. et al.** (2022). "Chain-of-Thought Prompting Elicits Reasoning in Large Language Models". arXiv preprint.
- **Yao, S. et al.** (2022). "ReAct: Synergizing Reasoning and Acting in Language Models". arXiv preprint.

### vAgenda
- **Core Specification**: README.md
- **Extension 2 (Identifiers)**: README.md#extension-2-identifiers
- **Extension 4 (Hierarchical)**: README.md#extension-4-hierarchical
- **Extension 10 (Version Control)**: README.md#extension-10-version-control
- **Extension 12 (ACE)**: README.md#extension-12-ace
- **MCP Extension**: vAgenda-extension-MCP.md

## Acknowledgments

This extension is directly inspired by the work of Gaurav Kumar and Annu Rana on Model-First Reasoning. Their research demonstrates that **explicit problem modeling is foundational to reliable agentic AI systems**, a principle we bring to the vAgenda specification.

We also acknowledge the classical AI planning tradition (STRIPS, PDDL) and cognitive science research on mental models, which established the importance of explicit representations decades before LLMs existed.

## Appendix: Example Domains

### A. Medical Scheduling

```javascript
// Problem: Schedule patient appointments with constraints
{
  entities: [
    { id: "patient", type: "Patient", properties: { needsTests: true } },
    { id: "doctor", type: "Doctor", properties: { specialty: "cardiology" } },
    { id: "room", type: "Room", properties: { equipment: ["ecg", "ultrasound"] } }
  ],
  stateVariables: [
    { id: "patient-seen", entity: "patient", name: "hasAppointment", 
      type: "boolean", initialValue: false },
    { id: "doctor-available", entity: "doctor", name: "available",
      type: "boolean", initialValue: true },
    { id: "room-occupied", entity: "room", name: "occupied",
      type: "boolean", initialValue: false }
  ],
  constraints: [
    {
      description: "Room must be available before booking",
      conditions: [{ variable: "room-occupied", operator: "==", value: false }]
    },
    {
      description: "Doctor must be available",
      conditions: [{ variable: "doctor-available", operator: "==", value: true }]
    },
    {
      description: "Patient appointments must be >=30min apart",
      conditions: [{ variable: "time-since-last", operator: ">=", value: 30 }]
    }
  ]
}
```

### B. Database Migration

```javascript
{
  entities: [
    { id: "old-db", type: "Database", properties: { vendor: "MySQL" } },
    { id: "new-db", type: "Database", properties: { vendor: "PostgreSQL" } },
    { id: "application", type: "Application", properties: { downtime: "prohibited" } }
  ],
  stateVariables: [
    { id: "old-db-state", entity: "old-db", name: "status",
      type: "enum", possibleValues: ["active", "readonly", "offline"], 
      initialValue: "active" },
    { id: "new-db-state", entity: "new-db", name: "status",
      type: "enum", possibleValues: ["empty", "syncing", "ready"],
      initialValue: "empty" },
    { id: "app-state", entity: "application", name: "usingDb",
      type: "string", initialValue: "old-db" }
  ],
  constraints: [
    {
      description: "Application must have at least one DB available",
      conditions: [
        { variable: "old-db-state", operator: "!=", value: "offline" },
        { variable: "new-db-state", operator: "!=", value: "empty" }
      ]
    },
    {
      description: "Must verify data consistency before cutover",
      conditions: [
        { variable: "data-verified", operator: "==", value: true }
      ]
    }
  ],
  goals: [
    {
      description: "Application using new DB successfully",
      conditions: [
        { variable: "app-state", operator: "==", value: "new-db" },
        { variable: "new-db-state", operator: "==", value: "ready" }
      ],
      priority: 1,
      optional: false
    }
  ]
}
```

### C. CI/CD Pipeline

```javascript
{
  entities: [
    { id: "code", type: "CodeRepository", properties: { branch: "main" } },
    { id: "tests", type: "TestSuite", properties: { coverage: 0 } },
    { id: "staging", type: "Environment", properties: { url: "staging.example.com" } },
    { id: "production", type: "Environment", properties: { url: "example.com" } }
  ],
  stateVariables: [
    { id: "code-built", entity: "code", name: "buildStatus",
      type: "enum", possibleValues: ["pending", "success", "failure"],
      initialValue: "pending" },
    { id: "tests-passed", entity: "tests", name: "testStatus",
      type: "enum", possibleValues: ["pending", "passed", "failed"],
      initialValue: "pending" },
    { id: "staging-deployed", entity: "staging", name: "deployed",
      type: "boolean", initialValue: false },
    { id: "prod-deployed", entity: "production", name: "deployed",
      type: "boolean", initialValue: false }
  ],
  actions: [
    {
      name: "build",
      preconditions: [],
      effects: [{ variable: "code-built", change: "set", value: "success" }]
    },
    {
      name: "test",
      preconditions: [{ variable: "code-built", operator: "==", value: "success" }],
      effects: [{ variable: "tests-passed", change: "set", value: "passed" }]
    },
    {
      name: "deploy-staging",
      preconditions: [{ variable: "tests-passed", operator: "==", value: "passed" }],
      effects: [{ variable: "staging-deployed", change: "set", value: true }]
    },
    {
      name: "deploy-production",
      preconditions: [
        { variable: "staging-deployed", operator: "==", value: true },
        { variable: "tests-passed", operator: "==", value: "passed" }
      ],
      effects: [{ variable: "prod-deployed", change: "set", value: true }]
    }
  ],
  constraints: [
    {
      description: "Cannot deploy to production without staging verification",
      type: "hard",
      conditions: [{ variable: "staging-deployed", operator: "==", value: true }],
      scope: "action"
    },
    {
      description: "All tests must pass before any deployment",
      type: "hard",
      conditions: [{ variable: "tests-passed", operator: "==", value: "passed" }],
      scope: "global"
    }
  ]
}
```

These examples demonstrate how MFR's explicit modeling captures domain-specific logic that would otherwise remain implicit and error-prone in natural language plans.
