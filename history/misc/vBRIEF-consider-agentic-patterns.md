# vBRIEF Extension: Agentic Design Patterns

**Extension Name**: Agentic Patterns

**Version**: 0.2

**Status**: Draft

**Depends on**:
- Extension 2 (Identifiers) - Required
- Extension 10 (Version Control & Sync) - Required for Agent tracking
- Extension 12 (Playbooks) - Recommended

**Last Updated**: 2025-12-27

---

## Overview

This extension adds support for capturing and orchestrating **agentic design patterns** within vBRIEF documents. It enables AI agents and agentic systems to document their workflows, track pattern usage, capture pattern effectiveness, and build institutional knowledge about which patterns work best for different types of tasks.

### Motivation

Modern agentic systems employ sophisticated design patterns such as prompt chaining, routing, reflection, tool use, planning, and multi-agent collaboration. However, there is no standardized way to:

1. **Document which patterns were used** in completing tasks
2. **Track pattern effectiveness** across different contexts
3. **Capture workflow state** for long-running agentic processes
4. **Enable pattern discovery** from historical execution data
5. **Facilitate agent-to-agent learning** about successful approaches

vBRIEF's three-tier memory system (TodoList for short-term, Plan for medium-term, Playbook for long-term) provides the ideal foundation for capturing this agentic workflow metadata.

### Design Philosophy

This extension follows vBRIEF's principle of **capturing the "why" alongside the "what"**. By documenting not just task completion but also the patterns, strategies, and agent reasoning employed, we enable:

- **Reflection and learning** - Agents can analyze what worked and why
- **Pattern reuse** - Successful patterns can be identified and applied to similar tasks
- **Transparency** - Human reviewers can understand agent decision-making
- **Continuous improvement** - Systems get smarter over time through accumulated pattern knowledge

---

## Core Concepts

### The 21 Agentic Design Patterns

Based on "Agentic Design Patterns: A Hands-On Guide to Building Intelligent Systems" (Gulli, 2025), modern agentic systems employ these patterns:

**Part One - Foundational Patterns**:
1. **Prompt Chaining** - Sequential task decomposition
2. **Routing** - Intent-based delegation to specialized agents
3. **Parallelization** - Concurrent execution of independent tasks
4. **Reflection** - Self-critique and iterative refinement
5. **Tool Use** - External function/API invocation
6. **Planning** - Multi-step task decomposition and orchestration
7. **Multi-Agent** - Collaborative systems with specialized agents

**Part Two - Memory & Adaptation**:
8. **Memory Management** - Context handling across time horizons
9. **Learning & Adaptation** - Improvement from experience
10. **Model Context Protocol (MCP)** - Standardized communication
11. **Goal Setting & Monitoring** - Objective tracking and progress measurement

**Part Three - Robustness**:
12. **Exception Handling & Recovery** - Error resilience
13. **Human-in-the-Loop** - Human oversight and intervention
14. **Knowledge Retrieval (RAG)** - Retrieval-augmented generation

**Part Four - Advanced Systems**:
15. **Inter-Agent Communication (A2A)** - Agent-to-agent messaging
16. **Resource-Aware Optimization** - Efficient resource usage
17-21. **Additional advanced patterns** (see full specification)

### The Five-Step Agent Loop

```
Perceive → Plan → Act → Reflect → Adapt
    ↑                              ↓
    └──────────────────────────────┘
```

This extension captures data at each stage:
- **Perceive**: Captured in task descriptions, context narratives
- **Plan**: Captured in Plan documents and PlanItems
- **Act**: Captured in TodoItems and change logs
- **Reflect**: Captured in Playbook entries
- **Adapt**: Captured in pattern effectiveness metrics

---

## Design Principle: Plans ARE Workflows

This extension recognizes that **vBRIEF Plans are natural workflow containers**. Rather than introducing separate workflow types, we extend Plans to capture agentic pattern metadata:

- **Plan** = Workflow container (already has title, status, narratives, timing)
- **PlanItems** = Workflow steps (already ordered, have status, can nest via `subItems`)
- **Narratives** = Reasoning and context (already capture the "why")
- **Existing Extensions** provide Agent tracking, timestamps, participants, etc.

This keeps vBRIEF simple while enabling full pattern capture.

---

## Data Model Extensions

### New Types

#### StepType

Maps PlanItems to the five-step agent loop.

```javascript
enum StepType {
  "perceive"    // Gather information, understand context
  "plan"        // Determine approach, break down task  
  "act"         // Execute actions, use tools
  "reflect"     // Review results, identify issues
  "adapt"       // Learn from experience, adjust approach
  "delegate"    // Route to specialized agent (routing pattern)
  "synthesize"  // Combine results from multiple sources
  "validate"    // Check correctness, run tests
}
```

#### PatternUsage

Captures the application of a specific pattern within a context.

```javascript
PatternUsage {
  pattern: string                 // Pattern name (from 21 patterns)
  context: PatternContext         // Context where pattern was applied
  effectiveness?: number          // 0-1 score of effectiveness
  confidence?: number             // 0-1 agent confidence in pattern choice
  reasoning?: string              // Why this pattern was chosen
  alternatives?: string[]         // Other patterns considered
  appliedAt: datetime             // When pattern was applied
  outcome: enum                   // "successful" | "partial" | "failed" | "unknown"
  metrics?: PatternMetrics        // Quantitative metrics
}
```

#### PatternContext

Describes the context in which a pattern was applied.

```javascript
PatternContext {
  taskType: string                // Type of task (e.g., "code_generation", "data_analysis")
  complexity: enum                // "simple" | "moderate" | "complex" | "veryComplex"
  domain?: string                 // Domain (e.g., "backend", "frontend", "devops")
  inputSize?: number              // Input size (tokens, lines, records)
  constraintsPresent?: string[]   // Constraints (e.g., ["time", "resources", "dependencies"])
  collaborativeAgents?: number    // Number of agents collaborating
  humanInvolvement?: boolean      // Whether humans were in the loop
}
```

#### PatternMetrics

Quantitative metrics for pattern effectiveness.

```javascript
PatternMetrics {
  executionTime?: number          // Time to complete (seconds)
  iterations?: number             // Number of iterations/refinements
  toolCalls?: number              // Number of tool invocations
  tokenUsage?: number             // Total tokens consumed
  errorRate?: number              // Error rate (0-1)
  userSatisfaction?: number       // User satisfaction score (0-1)
  costEfficiency?: number         // Cost efficiency score (0-1)
}
```

#### RoutingRule

Defines routing logic for directing work to specialized agents.

```javascript
RoutingRule {
  id: string                      // Unique rule identifier
  condition: string               // Natural language or expression describing when to route
  targetAgent: Agent              // Agent to route to
  confidence?: number             // Confidence in routing decision (0-1)
  priority?: number               // Rule priority (higher = evaluated first)
  metadata?: object               // Custom routing metadata
}
```

#### Tool

Represents a tool/function available to agents.

```javascript
Tool {
  id: string                      // Unique tool identifier
  name: string                    // Tool name
  type: enum                      // "function" | "api" | "mcp" | "shell" | "web" | "database" | "external"
  description?: string            // What the tool does
  specification?: object          // Tool schema/signature (e.g., JSON Schema for functions)
  endpoint?: string               // API endpoint or command
  requiresAuth?: boolean          // Whether authentication is needed
  metadata?: object               // Custom tool metadata
}
```

#### ToolResult

Captures the result of a tool invocation.

```javascript
ToolResult {
  toolId: string                  // Reference to Tool.id
  invokedAt: datetime             // When tool was called
  duration?: number               // Execution time (seconds)
  status: enum                    // "success" | "failure" | "timeout" | "unauthorized"
  input?: any                     // Input parameters
  output?: any                    // Output result
  error?: ErrorDetail             // Error details if failed
}
```

#### ErrorDetail

Structured error information.

```javascript
ErrorDetail {
  code?: string                   // Error code
  message: string                 // Error message
  stackTrace?: string             // Stack trace if available
  recoverable?: boolean           // Whether error is recoverable
  recoveryAction?: string         // Suggested recovery action
}
```

---

## Extensions to Core Types

### TodoList Extensions

```javascript
TodoList {
  // Core + existing extensions...
  primaryPattern?: string         // Primary pattern: "routing" | "parallelization" | etc.
  subPatterns?: string[]          // Additional patterns used
  patternRationale?: string       // Why this pattern was chosen
  routingRules?: RoutingRule[]    // Rules for routing items to agents
}
```

### TodoItem Extensions

```javascript
TodoItem {
  // Core + existing extensions...
  patternUsage?: PatternUsage[]   // Patterns used to complete this item
  routedTo?: Agent                // Agent this item was routed to
  routingRule?: string            // ID of routing rule that applied
  toolsRequired?: Tool[]          // Tools needed to complete this item
  toolResults?: ToolResult[]      // Results from tool invocations
  reflectionNotes?: string        // Agent's reflection on this item
  iterations?: number             // Number of refinement iterations
}
```

### Plan Extensions

**Plans serve as workflow containers**. Existing Plan structure provides:
- `title` - Workflow name
- `status` - Workflow state (draft → proposed → approved → inProgress → completed | cancelled)
- `narratives` - Approach, reasoning, context (the "why")
- `items` - Workflow steps (PlanItems array, already ordered)
- Extension 1: `created`, `updated` - Timing
- Extension 2: `id` - Unique identifier
- Extension 10: `agent`, `changeLog` - Agent tracking and history

This extension adds pattern metadata:

```javascript
Plan {
  // Core + existing extensions...
  
  // Pattern identification
  primaryPattern?: string         // Main pattern: "promptChaining" | "multiAgent" | "planning" | etc.
  subPatterns?: string[]          // Additional patterns (e.g., ["reflection", "toolUse"])
  patternRationale?: string       // Why this pattern combination was chosen
  
  // Workflow resumability  
  checkpoint?: string             // Resume point (e.g., "phase-3-completed", PlanItem.id)
  
  // Metrics (supplement Extension 1 timestamps)
  totalDuration?: number          // Total execution time in seconds
  routingRules?: RoutingRule[]    // For routing pattern: rules to delegate phases
}
```

**Mapping Plan.status to workflow states**:
- `draft` = Workflow being designed
- `proposed` = Awaiting approval
- `approved` = Ready to execute
- `inProgress` = Currently executing
- `completed` = Successfully finished
- `cancelled` = Terminated

### PlanItem Extensions

**PlanItems serve as workflow steps**. Existing PlanItem structure provides:
- `title` - Step name
- `status` - Step state (pending → inProgress → completed | blocked | cancelled)
- Array index - Execution order
- Extension 2: `id` - Unique step identifier
- Extension 4: `subItems` - Nested sub-steps
- Extension 4: `dependencies` - Execution prerequisites  
- Extension 5: `startDate`, `endDate`, `percentComplete` - Progress
- Extension 6: `participants` - Assigned agents

This extension adds step metadata:

```javascript
PlanItem {
  // Core + existing extensions...
  
  // Step type (five-step agent loop)
  stepType?: StepType             // "perceive" | "plan" | "act" | "reflect" | "adapt" | etc.
  
  // Pattern tracking
  patternUsage?: PatternUsage[]   // Patterns employed in this step
  
  // Tool usage  
  toolsRequired?: Tool[]          // Tools needed
  toolResults?: ToolResult[]      // Tool invocation results
  
  // Execution details
  reasoning?: string              // Agent's reasoning (complements Extension 10 changeLog)
  retries?: number                // Number of retry attempts
  
  // Delegation (for routing pattern)
  delegation?: {                  // If step delegated to specialist
    targetAgent: Agent            // Which agent received the work
    reason: string                // Why this agent was chosen
    status: enum                  // "pending" | "active" | "completed"
  }
}
```

### PlaybookItem Extensions (from Extension 12)

```javascript
PlaybookItem {
  // Core + Extension 12 fields...
  patternsUsed?: string[]         // Patterns employed (from 21 patterns)
  patternEffectiveness?: {        // Effectiveness by pattern
    [patternName: string]: {
      successRate: number         // 0-1 success rate
      avgDuration: number         // Average duration (seconds)
      contexts: PatternContext[]  // Contexts where applied
      confidence: number          // Confidence in effectiveness (0-1)
    }
  }
  applicableContexts?: PatternContext[] // Where this learning applies
  antiPatterns?: string[]         // Patterns to avoid in this context
}
```

---

## Usage Examples

### Example 1: Prompt Chaining Workflow

A multi-step research task using prompt chaining. **The Plan itself is the workflow.**

**JSON**:
```json
{
  "vBRIEFInfo": {
    "version": "0.3",
    "created": "2025-12-27T10:00:00Z",
    "updated": "2025-12-27T10:04:00Z"
  },
  "plan": {
    "id": "research-plan-001",
    "title": "Research competitor AI features",
    "status": "completed",
    
    "primaryPattern": "promptChaining",
    "subPatterns": ["toolUse"],
    "patternRationale": "Sequential steps with dependencies: each phase builds on previous results",
    
    "agent": {
      "id": "research-agent-1",
      "type": "aiAgent",
      "name": "Research Assistant",
      "model": "claude-3.5-sonnet"
    },
    
    "totalDuration": 240,
    
    "narratives": {
      "proposal": {
        "title": "Research Approach",
        "content": "Use prompt chaining to break research into sequential steps: 1) Identify competitors, 2) Gather feature data, 3) Analyze trends, 4) Synthesize report. Each step feeds into the next."
      }
    },
    
    "items": [
      {
        "id": "phase-1",
        "title": "Identify competitors",
        "status": "completed",
        "stepType": "perceive",
        "reasoning": "Identified 5 key competitors in the AI space",
        "startDate": "2025-12-27T10:00:00Z",
        "endDate": "2025-12-27T10:00:15Z",
        "patternUsage": [
          {
            "pattern": "promptChaining",
            "context": {
              "taskType": "research",
              "complexity": "moderate",
              "domain": "competitive_analysis"
            },
            "effectiveness": 0.95,
            "confidence": 0.9,
            "reasoning": "First link in chain - clear objective with well-defined output",
            "appliedAt": "2025-12-27T10:00:00Z",
            "outcome": "successful",
            "metrics": {
              "executionTime": 15,
              "tokenUsage": 2500
            }
          }
        ]
      },
      {
        "id": "phase-2",
        "title": "Gather feature data",
        "status": "completed",
        "stepType": "act",
        "dependencies": ["phase-1"],
        "reasoning": "Collected public documentation for each competitor",
        "startDate": "2025-12-27T10:00:15Z",
        "endDate": "2025-12-27T10:02:15Z",
        "toolsRequired": [
          {
            "id": "web-search-1",
            "name": "web_search",
            "type": "web",
            "description": "Search the web for information"
          }
        ],
        "toolResults": [
          {
            "toolId": "web-search-1",
            "invokedAt": "2025-12-27T10:00:20Z",
            "duration": 110,
            "status": "success",
            "output": "Retrieved feature pages for 5 competitors"
          }
        ]
      },
      {
        "id": "phase-3",
        "title": "Analyze trends",
        "status": "completed",
        "stepType": "reflect",
        "dependencies": ["phase-2"],
        "reasoning": "Analyzed feature patterns and identified 3 key trends",
        "startDate": "2025-12-27T10:02:15Z",
        "endDate": "2025-12-27T10:03:00Z"
      },
      {
        "id": "phase-4",
        "title": "Synthesize report",
        "status": "completed",
        "stepType": "synthesize",
        "dependencies": ["phase-3"],
        "reasoning": "Created comprehensive comparison report",
        "startDate": "2025-12-27T10:03:00Z",
        "endDate": "2025-12-27T10:04:00Z",
        "uris": [
          {
            "uri": "file://./competitor-analysis.md",
            "type": "text/markdown",
            "description": "Final research report"
          }
        ]
      }
    ]
  }
}
```

### Example 2: Multi-Agent Collaboration with Routing

A development task routed to specialized agents using TodoList.

**JSON**:
```json
{
  "vBRIEFInfo": {
    "version": "0.3"
  },
  "todoList": {
    "id": "dev-tasks-001",
    "title": "Build authentication system",
    
    "primaryPattern": "multiAgent",
    "subPatterns": ["routing", "toolUse"],
    "patternRationale": "Different specialized skills needed: backend logic and frontend UI",
    
    "routingRules": [
      {
        "id": "route-backend",
        "condition": "Task involves database, API, or server-side logic",
        "targetAgent": {
          "id": "backend-agent",
          "type": "aiAgent",
          "name": "Backend Specialist"
        },
        "confidence": 0.95,
        "priority": 1
      },
      {
        "id": "route-frontend",
        "condition": "Task involves UI, forms, or client-side code",
        "targetAgent": {
          "id": "frontend-agent",
          "type": "aiAgent",
          "name": "Frontend Specialist"
        },
        "confidence": 0.95,
        "priority": 2
      }
    ],
    "items": [
      {
        "id": "item-1",
        "title": "Implement JWT token generation",
        "status": "completed",
        "routedTo": {
          "id": "backend-agent",
          "type": "aiAgent",
          "name": "Backend Specialist"
        },
        "routingRule": "route-backend",
        "patternUsage": [
          {
            "pattern": "toolUse",
            "context": {
              "taskType": "code_generation",
              "complexity": "moderate",
              "domain": "backend"
            },
            "effectiveness": 0.92,
            "outcome": "successful",
            "appliedAt": "2025-12-27T11:00:00Z"
          }
        ],
        "toolsRequired": [
          {
            "id": "code-editor",
            "name": "edit_files",
            "type": "function",
            "description": "Edit source code files"
          },
          {
            "id": "test-runner",
            "name": "run_tests",
            "type": "shell",
            "description": "Execute test suite"
          }
        ],
        "toolResults": [
          {
            "toolId": "code-editor",
            "invokedAt": "2025-12-27T11:05:00Z",
            "duration": 30,
            "status": "success",
            "output": "Created auth/jwt.py with token generation logic"
          },
          {
            "toolId": "test-runner",
            "invokedAt": "2025-12-27T11:10:00Z",
            "duration": 15,
            "status": "success",
            "output": "All 12 tests passed"
          }
        ]
      },
      {
        "id": "item-2",
        "title": "Create login form UI",
        "status": "inProgress",
        "routedTo": {
          "id": "frontend-agent",
          "type": "aiAgent",
          "name": "Frontend Specialist"
        },
        "routingRule": "route-frontend"
      }
    ]
  }
}
```

### Example 3: Reflection Loop for Code Quality

Using reflection pattern to iteratively improve code.

**JSON**:
```json
{
  "vBRIEFInfo": {
    "version": "0.3"
  },
  "todoList": {
    "id": "refactor-001",
    "items": [
      {
        "id": "item-1",
        "title": "Refactor authentication module",
        "status": "completed",
        "iterations": 3,
        "patternUsage": [
          {
            "pattern": "reflection",
            "context": {
              "taskType": "code_refactoring",
              "complexity": "complex",
              "domain": "backend"
            },
            "effectiveness": 0.88,
            "confidence": 0.85,
            "reasoning": "Reflection enabled iterative quality improvements through self-critique",
            "appliedAt": "2025-12-27T14:00:00Z",
            "outcome": "successful",
            "metrics": {
              "executionTime": 180,
              "iterations": 3,
              "tokenUsage": 15000,
              "errorRate": 0.0
            }
          }
        ],
        "reflectionNotes": "Iteration 1: Initial refactor separated concerns but missed edge cases. Iteration 2: Added error handling but tests revealed performance issue. Iteration 3: Optimized database queries, all tests passing, code coverage 95%."
      }
    ]
  }
}
```

### Example 4: Playbook Entry Capturing Pattern Effectiveness

Long-term learning about pattern effectiveness.

**JSON**:
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
        "targetId": "entry-001",
        "operation": "append",
        "kind": "strategy",
        "title": "Use Reflection Pattern for Complex Refactoring",
        "narrative": {
          "Guidance": "When refactoring complex modules (>500 LOC, multiple dependencies), employ reflection pattern with 2-3 iterations.",
          "Iterations": "Iteration 1 focuses on structure, iteration 2 on edge cases, iteration 3 on optimization."
        },
        "confidence": 0.92,
        "status": "active",
        "createdAt": "2025-12-27T00:00:00Z",
        "patternsUsed": ["reflection", "toolUse"],
        "patternEffectiveness": {
          "reflection": {
            "successRate": 0.88,
            "avgDuration": 180,
            "contexts": [
              {
                "taskType": "code_refactoring",
                "complexity": "complex",
                "domain": "backend"
              },
              {
                "taskType": "code_refactoring",
                "complexity": "complex",
                "domain": "frontend"
              }
            ],
            "confidence": 0.9
          }
        },
        "applicableContexts": [
          {
            "taskType": "code_refactoring",
            "complexity": "complex",
            "constraintsPresent": ["dependencies", "backwards_compatibility"]
          }
        ],
        "evidence": [
          {
            "type": "reference",
            "uri": "file://./todos/refactor-001.json#item-1",
            "summary": "Authentication refactor: 3 iterations, 95% coverage"
          }
        ]
      }
    ]
  }
}
```

---

## Integration with Existing Extensions

### Extension 10: Version Control & Sync

The Agent type from Extension 10 is used throughout this extension to track which agents performed which actions.

```javascript
Agent {
  id: string
  type: enum              // "human" | "aiAgent" | "system"
  name?: string
  model?: string          // For AI agents
  version?: string
}
```

### Extension 12: Playbooks

Playbooks serve as the long-term memory for pattern effectiveness. As agents complete tasks using various patterns, they should:

1. Capture `PatternUsage` on TodoItems and PlanItems
2. Reflect on what worked/didn't work
3. Create or update PlaybookItems with pattern effectiveness data
4. Query playbooks before choosing patterns for new tasks

This creates a **virtuous learning cycle**: Execute → Capture → Reflect → Learn → Improve.

### Extension 7: Resources & References

The `Reference` type from Extension 7 is used in WorkflowStep to link inputs and outputs.

---

## Best Practices

### 1. Always Capture Pattern Rationale

When applying a pattern, document **why** it was chosen:

```javascript
{
  "pattern": "promptChaining",
  "reasoning": "Task requires sequential steps where each builds on previous output. Parallel execution not suitable due to data dependencies."
}
```

### 2. Track Metrics for Continuous Improvement

Capture quantitative metrics to enable data-driven pattern selection:

```javascript
{
  "metrics": {
    "executionTime": 120,
    "iterations": 2,
    "tokenUsage": 8000,
    "errorRate": 0.0,
    "userSatisfaction": 0.95
  }
}
```

### 3. Document Context for Pattern Discovery

Rich context enables finding applicable patterns for similar tasks:

```javascript
{
  "context": {
    "taskType": "data_analysis",
    "complexity": "moderate",
    "domain": "finance",
    "inputSize": 50000,
    "constraintsPresent": ["time", "accuracy"]
  }
}
```

### 4. Use Hybrid Patterns

Real-world tasks often combine multiple patterns:

```javascript
{
  "workflow": {
    "pattern": "hybrid",
    "subPatterns": ["routing", "parallelization", "reflection", "toolUse"]
  }
}
```

### 5. Checkpoint Long-Running Workflows

Enable resumability for long workflows:

```javascript
{
  "workflow": {
    "status": "paused",
    "checkpoint": "step-5-completed",
    "steps": [...]
  }
}
```

### 6. Feed Learnings to Playbooks

After task completion, update playbooks with insights:

```javascript
{
  "playbookItem": {
    "title": "Parallelization effective for independent API calls",
    "patternsUsed": ["parallelization"],
    "patternEffectiveness": {
      "parallelization": {
        "successRate": 0.95,
        "avgDuration": 30,  // vs 120 sequential
        "confidence": 0.9
      }
    },
    "evidence": [
      {"uri": "file://./plan-001.json#phase-2"}
    ]
  }
}
```

### 7. Enable Human Review for Critical Patterns

Some patterns should trigger human review:

```javascript
{
  "todoItem": {
    "title": "Deploy database migration",
    "patternUsage": [{
      "pattern": "humanInLoop",
      "reasoning": "Critical operation requires human approval"
    }],
    "participants": [
      {"role": "reviewer", "status": "needsAction"}
    ]
  }
}
```

---

## Pattern Selection Guidelines

### When to Use Each Pattern

| Pattern | Use When | Avoid When |
|---------|----------|------------|
| **Prompt Chaining** | Tasks have clear sequential steps with dependencies | Steps can run in parallel |
| **Routing** | Multiple specialized agents available | Single general agent is sufficient |
| **Parallelization** | Independent subtasks with no data dependencies | Tasks must be sequential |
| **Reflection** | Quality/correctness is critical | Speed is priority over quality |
| **Tool Use** | External APIs/functions can solve subtasks | Pure reasoning task |
| **Planning** | Complex multi-phase work requiring coordination | Simple single-step task |
| **Multi-Agent** | Diverse specialized skills needed | Task scope within single agent capability |
| **Memory Management** | Long conversations or stateful interactions | Stateless operations |
| **Human-in-the-Loop** | High-stakes decisions or creative work | Fully automatable tasks |
| **RAG** | Task requires external knowledge retrieval | All needed info in context |

### Combining Patterns Effectively

Common pattern combinations:

1. **Planning + Routing + Tool Use**
   - Plan breaks down complex project
   - Router delegates phases to specialists
   - Tools execute actions

2. **Prompt Chaining + Reflection**
   - Chain executes sequential steps
   - Reflection validates each output
   - Iterate until quality threshold met

3. **Multi-Agent + Parallelization + Synthesis**
   - Multiple agents work in parallel
   - Results synthesized by coordinator
   - Efficient for independent analyses

4. **Tool Use + Exception Handling**
   - Tools called with error handling
   - Failures trigger recovery logic
   - System remains resilient

---

## Implementation Considerations

### Performance

- **Checkpoint frequently** for long workflows to enable resumption
- **Parallelize when possible** to reduce total execution time
- **Cache pattern effectiveness** lookups in memory
- **Batch similar operations** to reduce overhead

### Storage

- `PatternUsage` arrays can grow large; consider:
  - Archiving old pattern data after time threshold
  - Storing detailed metrics separately with references
  - Aggregating pattern effectiveness in playbooks

### Privacy & Security

- Pattern usage may reveal sensitive information about:
  - Internal system architecture
  - Agent capabilities
  - Business logic
- Use Extension 9 (Security & Privacy) to classify pattern data appropriately
- Redact sensitive information from `reasoning` and `output` fields when sharing

### Interoperability

For maximum compatibility:
- Use standard pattern names from the 21-pattern taxonomy
- Include `patternRationale` for human and cross-system understanding
- Link to canonical pattern documentation when available
- Support both simple (pattern name only) and rich (full PatternUsage) formats

---

## Future Directions

### Pattern Discovery

Future versions may add:
- Automatic pattern recommendation based on task characteristics
- Pattern effectiveness prediction using historical data
- Anomaly detection for pattern failures

### Advanced Analytics

- Cross-agent pattern effectiveness comparison
- Pattern combination optimization
- Cost/benefit analysis for pattern selection

### Standardization

- Align with emerging agentic workflow standards
- Integrate with agent orchestration frameworks (LangChain, LangGraph, CrewAI)
- Support OpenTelemetry for pattern execution tracing

---

## Appendix: Complete Type Reference

### Enums

#### WorkflowPattern
```
"promptChaining" | "routing" | "parallelization" | "reflection" | "toolUse" | 
"planning" | "multiAgent" | "memoryManagement" | "learningAdaptation" | "mcp" | 
"goalMonitoring" | "exceptionHandling" | "humanInLoop" | "rag" | "a2a" | 
"resourceOptimization" | "hybrid"
```

#### WorkflowStatus
```
"pending" | "running" | "paused" | "completed" | "failed" | "cancelled"
```

#### StepType
```
"perceive" | "plan" | "act" | "reflect" | "adapt" | "delegate" | "synthesize" | "validate"
```

#### ToolType
```
"function" | "api" | "mcp" | "shell" | "web" | "database" | "external"
```

#### PatternOutcome
```
"successful" | "partial" | "failed" | "unknown"
```

#### Complexity
```
"simple" | "moderate" | "complex" | "veryComplex"
```

---

## References

- Gulli, A. (2025). *Agentic Design Patterns: A Hands-On Guide to Building Intelligent Systems*. Springer.
- vBRIEF Core Specification v0.3
- Extension 2: Identifiers
- Extension 10: Version Control & Sync
- Extension 12: Playbooks

---

## License

This specification is released under CC BY 4.0.

---

## Changelog

### Version 0.2 (2025-12-27)
- **Breaking change**: Removed AgenticWorkflow and WorkflowStep types
- **Design principle**: Plans ARE workflows, PlanItems ARE steps
- Simplified to only essential new types: StepType, PatternUsage, PatternContext, Tool, ToolResult, RoutingRule, ErrorDetail
- Plans naturally serve as workflow containers using existing structure
- PlanItems map to five-step agent loop via `stepType` field
- Updated all examples to use simplified structure

### Version 0.1 (2025-12-27)
- Initial draft
- 21 pattern taxonomy integration
- Separate AgenticWorkflow/WorkflowStep types (removed in v0.2)
