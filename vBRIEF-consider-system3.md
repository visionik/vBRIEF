# vBRIEF Extension: System 3 Meta-Cognitive Layer

**Extension Name**: System 3 Meta-Cognitive Layer

**Version**: 0.1

**Status**: Draft

**Based on**: ["Sophia: A Persistent Agent Framework of Artificial Life"](https://arxiv.org/abs/2512.18202) (Sun, Hong, Zhang, 2025)

**Last Updated**: 2025-12-28

---

## Overview

This extension introduces a **System 3 meta-cognitive layer** to vBRIEF, enabling AI agents to maintain persistent identity, self-awareness, and autonomous learning across extended operation periods. Inspired by the Sophia framework, it adds user modeling (Theory of Mind), self-modeling (meta-cognition), and intrinsic motivation to vBRIEF's existing TodoList/Plan/Playbook memory hierarchy.

### Motivation

Modern AI agents excel at perception (System 1) and deliberation (System 2) but lack a persistent meta-layer for:

1. **Identity continuity** - Maintaining coherent self-concept across sessions
2. **Self-directed learning** - Generating own goals from detected capability gaps
3. **User understanding** - Building dynamic models of user beliefs, preferences, and needs
4. **Intrinsic motivation** - Balancing external tasks with curiosity-driven exploration
5. **Meta-cognitive monitoring** - Real-time coherence checking and self-assessment

vBRIEF's three-tier memory system (TodoList/Plan/Playbook) provides the foundation for System 3:
- **TodoList** → Short-term/working memory (System 1 reactive tasks)
- **Plan** → Medium-term episodic memory (System 2 deliberate reasoning)
- **Playbook** → Long-term autobiographical memory (System 3 narrative identity)

This extension completes the architecture by adding meta-cognitive oversight.

---

## Core Concepts

### The Four Psychological Pillars

Based on decades of cognitive psychology research, System 3 integrates:

1. **Meta-Cognition** ([Shaughnessy et al., 2008](https://doi.org/10.4135/9781412956802); [Dunlosky & Metcalfe, 2008](https://doi.org/10.4135/9781412950640))
   - Self-reflective monitoring of thought processes
   - Detection of logical fallacies and inconsistencies
   - Assessment of own capabilities and confidence
   - Real-time coherence checking

2. **Theory of Mind** ([Frith & Frith, 2005](https://doi.org/10.1016/j.neuron.2005.03.011); [Wellman, 2018](https://doi.org/10.1146/annurev-psych-010416-044139))
   - Modeling others' beliefs, desires, and intentions
   - Anticipating user needs and reactions
   - Collaborative reasoning about shared goals
   - Social relationship tracking

3. **Intrinsic Motivation** ([Fishbach & Woolley, 2022](https://doi.org/10.1146/annurev-psych-020821-103621))
   - Curiosity-driven exploration (information seeking)
   - Mastery goals (competence development)
   - Autonomy striving (self-directed behavior)
   - Internal reward generation

4. **Episodic Memory** ([Tulving, 2002](https://doi.org/10.1146/annurev.psych.53.100901.135114); [Ezzyat & Davachi, 2011](https://doi.org/10.1037/a0021558))
   - Autobiographical experience storage
   - Contextualized event retrieval
   - Narrative identity construction
   - Long-horizon credit assignment

**Note**: vBRIEF's existing Plan narratives and Playbook evidence already provide episodic memory. This extension adds the other three pillars.

### The Autonomous Cognitive Cycle

```
┌──────────────────────────────────────────────────────┐
│              System 3: Meta-Cognitive Monitor         │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐    │
│  │   Theory    │ │    Self     │ │  Intrinsic  │    │
│  │  of Mind    │ │   Model     │ │ Motivation  │    │
│  │ (UserModel) │ │(Capabilities)│ │  (Rewards)  │    │
│  └──────┬──────┘ └──────┬──────┘ └──────┬──────┘    │
│         └────────────┬───────────────────┘           │
│                      ↓                                │
│         ┌────────────────────────┐                   │
│         │ Executive Oversight     │                   │
│         │ • Goal Generation       │                   │
│         │ • Coherence Checking    │                   │
│         │ • Resource Allocation   │                   │
│         └────────────┬───────────┘                   │
└──────────────────────┼───────────────────────────────┘
                       ↓
         ┌─────────────────────────┐
         │ System 2: Deliberation  │
         │ (Plans)                 │
         └────────┬────────────────┘
                  ↓
         ┌─────────────────────────┐
         │ System 1: Perception    │
         │ (TodoLists)             │
         └─────────────────────────┘
```

The System 3 layer:
1. **Monitors** execution in Systems 1 and 2
2. **Detects** capability gaps, user needs, coherence issues
3. **Generates** new learning goals and experiments
4. **Updates** user models, self-models, and reward functions
5. **Directs** future planning and task prioritization

---

## Design Principle: Extending Existing Containers

Following vBRIEF's philosophy of extending existing types rather than creating new ones, System 3 fields are added directly to Plan, TodoList, and Playbook:

- **Plan.system3** - Meta-cognitive state for a specific project/goal
- **TodoList.system3** - Active working memory and immediate context
- **Playbook.system3** - Long-term identity, values, and accumulated knowledge
- **PlanItem/TodoItem.system3** - Action-level meta-data (confidence, intrinsic reward)

This enables System 3 oversight without disrupting existing workflows.

---

## Data Model Extensions

### Supporting Types

#### UserModel

Models a user's mental state for Theory of Mind.

```javascript
UserModel {
  userId?: string                  // User identifier (Extension 2)
  beliefs: object                  // What user knows/believes
                                   // e.g., {"pythonSkill": "intermediate", "projectGoal": "build API"}
  preferences: object              // User preferences and style
                                   // e.g., {"communicationStyle": "concise", "testingApproach": "TDD"}
  goals: string[]                  // User's stated/inferred goals
  emotionalState?: enum            // "focused" | "stressed" | "exploratory" | "blocked" | "calm"
  relationshipState: enum          // "stranger" | "new" | "established" | "trusted" | "collaborative"
  interactionHistory?: {           // Recent interaction patterns
    successfulPatterns: string[]   // What worked well with this user
    avoidPatterns: string[]        // What to avoid
    lastInteractionAt?: datetime
    totalInteractions?: number
  }
  trustLevel?: number              // 0-1: agent's confidence in understanding user
  uncertainties?: string[]         // Aspects of user state that are unclear
  metadata?: object
}
```

#### SelfModel

Agent's model of its own capabilities and identity.

```javascript
SelfModel {
  capabilities: Capability[]       // What the agent can do
  identityGoal?: string            // Terminal creed/core values
                                   // e.g., "Help users build robust software through clear communication"
  narrativeIdentity?: string       // Coherent self-concept across time
                                   // e.g., "I am a thoughtful coding assistant who values clarity and testing"
  coreValues?: string[]            // Guiding principles
                                   // e.g., ["transparency", "thoroughness", "adaptability"]
  coherenceScore?: number          // 0-1: consistency of behavior with identity
  lastSelfReviewAt?: datetime      // When capabilities were last assessed
  knowledgeGaps: KnowledgeGap[]    // Detected limitations
  strengths?: string[]             // Known areas of competence
  metadata?: object
}
```

#### Capability

A specific skill or ability the agent possesses.

```javascript
Capability {
  id: string                       // Unique capability identifier
  name: string                     // Human-readable name
  domain: string                   // Domain (e.g., "backend", "testing", "architecture")
  confidence: number               // 0-1: agent's confidence in this capability
  evidenceCount?: number           // Number of successful applications
  lastUsedAt?: datetime            // When capability was last exercised
  successRate?: number             // 0-1: historical success rate
  learnedFrom?: string             // PlaybookItem ID or source
  prerequisites?: string[]         // Other capability IDs required
  relatedCapabilities?: string[]   // Similar/adjacent capabilities
  metadata?: object
}
```

#### KnowledgeGap

A detected limitation or area for learning.

```javascript
KnowledgeGap {
  id: string
  description: string              // What is not known/understood
  domain: string                   // Domain of gap
  priority: enum                   // "critical" | "high" | "medium" | "low"
  detectedAt: datetime             // When gap was discovered
  detectedBy: enum                 // "self-reflection" | "failure" | "user-feedback" | "comparison"
  impactArea?: string              // What this gap affects
  proposedLearning?: string        // How to address the gap
  addressedBy?: string             // PlanItem ID or PlaybookItem ID attempting to close gap
  status: enum                     // "identified" | "learning" | "resolved" | "deferred"
  metadata?: object
}
```

#### IntrinsicReward

Internal motivation signals beyond external task success.

```javascript
IntrinsicReward {
  curiosity?: number               // 0-1: novel information gained
  mastery?: number                 // 0-1: skill development achieved
  autonomy?: number                // 0-1: self-directed behavior maintained
  coherence?: number               // 0-1: consistency with identity/values
  novelty?: number                 // 0-1: exposure to new patterns/domains
  competenceGrowth?: number        // 0-1: measurable capability improvement
  totalReward?: number             // Weighted combination
  reasoning?: string               // Why these rewards were assigned
}
```

#### MetaCognitiveState

Real-time self-monitoring state.

```javascript
MetaCognitiveState {
  currentFocus?: string            // What agent is currently working on
  confidenceLevel?: number         // 0-1: confidence in current approach
  uncertainties?: string[]         // Known unknowns in current context
  alternativesConsidered?: string[] // Other approaches evaluated
  coherenceIssues?: string[]       // Detected inconsistencies
  lastReflectionAt?: datetime      // When last self-assessment occurred
  thinkingMode?: enum              // "fast" | "deliberate" | "exploratory" | "validating"
  attentionAllocation?: object     // Where cognitive resources are focused
  metadata?: object
}
```

---

### Extended Core Types

#### Plan (Extended)

```javascript
Plan {
  // ... existing Plan fields ...
  
  system3?: {
    userModel?: UserModel          // Understanding of user for this plan
    selfModel?: SelfModel          // Agent capabilities relevant to plan
    intrinsicGoals?: string[]      // Self-generated learning goals
                                   // e.g., ["Learn GraphQL schema design", "Master async error handling"]
    metaCognitive?: MetaCognitiveState  // Current meta-cognitive state
    autoGenerated?: boolean        // Was this plan self-initiated?
    generatedFrom?: string         // KnowledgeGap ID or intrinsic motivation
    coherenceRationale?: string    // How this plan aligns with identity/values
    forwardLearningSource?: string // PlaybookItem ID being reused
    reflectionLog?: {              // Self-assessment entries
      timestamp: datetime
      observation: string
      action?: string              // What was adjusted
    }[]
  }
}
```

#### PlanItem (Extended)

```javascript
PlanItem {
  // ... existing PlanItem fields ...
  
  system3?: {
    confidence?: number            // 0-1: confidence in this action
    intrinsicReward?: IntrinsicReward  // Internal motivation signals
    alternativesConsidered?: string[]  // Other actions evaluated
    uncertainties?: string[]       // Known risks or unknowns
    capabilityUsed?: string        // Capability ID exercised
    capabilityDeveloped?: string   // Capability ID being learned
    reusedFrom?: string            // PlaybookItem ID if reusing prior solution
    forwardLearning?: boolean      // Is this reusing validated approach?
    selfCritique?: string          // Agent's self-assessment of action
  }
}
```

#### TodoList (Extended)

```javascript
TodoList {
  // ... existing TodoList fields ...
  
  system3?: {
    userModel?: UserModel          // Current user context
    activeGoals?: string[]         // Self-generated immediate goals
    metaCognitive?: MetaCognitiveState  // Working memory state
    routingRules?: RoutingRule[]   // How to delegate items (from Agentic Patterns)
  }
}
```

#### TodoItem (Extended)

```javascript
TodoItem {
  // ... existing TodoItem fields ...
  
  system3?: {
    confidence?: number            // 0-1: confidence in approach
    intrinsicReward?: IntrinsicReward  // Internal motivation
    uncertainties?: string[]       // Known unknowns
  }
}
```

#### Playbook (Extended)

```javascript
Playbook {
  // ... existing Playbook fields ...
  
  system3?: {
    selfModel?: SelfModel          // Long-term identity and capabilities
    userPersonas?: UserModel[]     // Models of different user types
    coreValues?: string[]          // Stable guiding principles
    evolutionLog?: {               // How agent has changed over time
      timestamp: datetime
      milestone: string
      capabilitiesAdded?: string[]
      knowledgeGapsResolved?: string[]
    }[]
    forwardLearningMetrics?: {     // Efficiency gains from reuse
      totalReuses: number
      averageReasoningReduction: number  // e.g., 0.80 = 80% reduction
      patternsReused: object       // { patternName: count }
    }
  }
}
```

#### PlaybookItem (Extended)

```javascript
PlaybookItem {
  // ... existing PlaybookItem fields ...
  
  system3?: {
    capabilityRequired?: string[]  // Capability IDs needed to apply this
    capabilityDeveloped?: string[] // Capability IDs gained from this
    userPersonaFit?: string[]      // Which user personas this works for
    intrinsicValue?: number        // 0-1: how valuable for learning
    reuseCount?: number            // Times this has been reapplied
    averageConfidence?: number     // 0-1: typical confidence when reusing
    lastReusedAt?: datetime
  }
}
```

---

## Integration with Other Extensions

### Agentic Patterns Extension
- **System 3 generates patterns**: Intrinsic motivation drives pattern exploration
- **Reflection pattern**: Meta-cognition enables the reflect → adapt cycle
- **User modeling**: Theory of Mind guides routing and human-in-the-loop patterns
- `Plan.system3.intrinsicGoals` can spawn Plans using specific agentic patterns

### Model-First Reasoning Extension
- **Self-model = capability constraints**: `SelfModel.capabilities` inform problem model constraints
- **User model = user constraints**: `UserModel.preferences` shape problem constraints
- **Knowledge gaps drive experiments**: Detected gaps become MFR hypotheses
- `Plan.problemModel.constraints` can reference `Plan.system3.selfModel.capabilities`

### Experimental Workflows Extension
- **Intrinsic motivation drives experiments**: Curiosity generates hypotheses
- **Knowledge gaps = experiment targets**: Learning needs become experiment goals
- **Meta-cognition validates outcomes**: Self-assessment evaluates experiment success
- `Experiment.hypothesis` can address `KnowledgeGap`

### Playbooks Extension
- **Self-model accumulates in Playbook**: Long-term capability tracking
- **User personas stored as templates**: Reusable user models
- **Forward learning tracked explicitly**: `PlaybookItem.system3.reuseCount`
- **Identity evolution logged**: `Playbook.system3.evolutionLog`

---

## Key Workflows

### 1. Autonomous Goal Generation

When agent detects capability gap:

```javascript
// Step 1: Detect gap during execution
{
  "selfModel": {
    "knowledgeGaps": [{
      "id": "gap-1",
      "description": "Limited understanding of WebSocket lifecycle",
      "domain": "backend",
      "priority": "high",
      "detectedAt": "2025-12-28T10:30:00Z",
      "detectedBy": "failure",
      "status": "identified"
    }]
  }
}

// Step 2: Generate learning goal
{
  "intrinsicGoals": [
    "Learn WebSocket connection handling and error recovery"
  ]
}

// Step 3: Auto-create Plan
Plan {
  title: "Study: WebSocket Lifecycle Management"
  system3: {
    autoGenerated: true
    generatedFrom: "gap-1"
    intrinsicGoals: ["Master WebSocket patterns"]
  }
  items: [
    PlanItem("Research WebSocket RFC", ...),
    PlanItem("Study error handling patterns", ...),
    PlanItem("Build test implementation", ...)
  ]
}
```

### 2. User Model Evolution

As agent interacts with user:

```javascript
// Initial state (stranger)
TodoList {
  system3: {
    userModel: {
      userId: "user-alice"
      relationshipState: "stranger"
      trustLevel: 0.3
      beliefs: {}
      preferences: {}
    }
  }
}

// After several interactions (established)
TodoList {
  system3: {
    userModel: {
      userId: "user-alice"
      relationshipState: "established"
      trustLevel: 0.8
      beliefs: {
        "pythonSkill": "advanced",
        "projectGoal": "migrate to microservices",
        "timeConstraint": "tight deadline"
      }
      preferences: {
        "communicationStyle": "direct",
        "testingApproach": "comprehensive",
        "documentationLevel": "thorough"
      }
      interactionHistory: {
        successfulPatterns: ["detailed explanations", "concrete examples"]
        avoidPatterns: ["overly concise responses"]
      }
    }
  }
}
```

### 3. Forward Learning (Reusing Prior Solutions)

When similar task arises:

```javascript
// Agent recognizes pattern from Playbook
PlanItem {
  title: "Implement JWT authentication"
  system3: {
    confidence: 0.95  // High confidence due to prior success
    reusedFrom: "playbook-item-auth-jwt"
    forwardLearning: true
    intrinsicReward: {
      mastery: 0.8     // Reinforcing known capability
      autonomy: 0.9    // Independent application
      coherence: 0.95  // Consistent with past behavior
    }
  }
}

// Metrics tracked in Playbook
Playbook {
  system3: {
    forwardLearningMetrics: {
      totalReuses: 47
      averageReasoningReduction: 0.82  // 82% fewer reasoning steps
      patternsReused: {
        "jwt-auth": 8,
        "oauth2-flow": 5,
        "api-versioning": 12
      }
    }
  }
}
```

### 4. Meta-Cognitive Coherence Checking

During planning:

```javascript
Plan {
  title: "Implement real-time notifications"
  system3: {
    selfModel: {
      identityGoal: "Build maintainable, tested systems",
      narrativeIdentity: "I prioritize clarity and robustness",
      coherenceScore: 0.75  // Lower due to detected issue
    }
    metaCognitive: {
      coherenceIssues: [
        "PlanItem 'Quick and dirty WebSocket setup' conflicts with value 'tested systems'",
        "Skipping error handling contradicts identity goal 'robustness'"
      ]
      uncertainties: [
        "User's deadline pressure vs. quality standards",
        "Is this a prototype or production feature?"
      ]
    }
  }
  narratives: [{
    type: "reflection"
    text: "Detected coherence issue: proposed approach skips testing due to time pressure, but this conflicts with core value of robustness. Need to clarify requirements with user."
  }]
}
```

---

## Examples

### Complete Plan with System 3

```javascript
Plan {
  id: "plan-migrate-auth"
  title: "Migrate authentication to OAuth2"
  status: "inProgress"
  
  system3: {
    userModel: {
      userId: "user-alice"
      beliefs: {
        "securityPriority": "high",
        "migrationExperience": "moderate",
        "teamSize": "small"
      }
      preferences: {
        "riskTolerance": "conservative",
        "documentationLevel": "thorough"
      }
      goals: ["Zero-downtime migration", "Maintain user sessions"]
      relationshipState: "trusted"
      trustLevel: 0.9
    }
    
    selfModel: {
      capabilities: [
        {
          id: "cap-oauth2",
          name: "OAuth2 implementation",
          domain: "backend-auth",
          confidence: 0.85,
          evidenceCount: 12,
          successRate: 0.90
        },
        {
          id: "cap-session-migration",
          name: "Session migration",
          domain: "backend-auth",
          confidence: 0.65,
          evidenceCount: 3,
          successRate: 0.67
        }
      ]
      identityGoal: "Build secure, maintainable systems through careful planning",
      narrativeIdentity: "I am thorough, security-conscious, and user-focused",
      coherenceScore: 0.92
      knowledgeGaps: [
        {
          id: "gap-jwt-refresh",
          description: "Token refresh strategies at scale",
          domain: "backend-auth",
          priority: "medium",
          detectedAt: "2025-12-27T14:20:00Z",
          detectedBy: "self-reflection",
          status: "learning"
        }
      ]
    }
    
    intrinsicGoals: [
      "Master token refresh patterns",
      "Understand session state migration"
    ]
    
    metaCognitive: {
      currentFocus: "Planning migration phases",
      confidenceLevel: 0.78,
      uncertainties: [
        "Best approach for dual-authentication period",
        "Rollback strategy if OAuth2 provider fails"
      ],
      alternativesConsidered: [
        "Big-bang migration",
        "Feature-flag gradual rollout",
        "Shadow authentication"
      ]
      thinkingMode: "deliberate"
    }
    
    autoGenerated: false
    coherenceRationale: "Conservative phased approach aligns with user's risk tolerance and my identity as thorough planner"
    
    reflectionLog: [
      {
        timestamp: "2025-12-28T09:15:00Z",
        observation: "Initial plan lacked rollback strategy - inconsistent with security focus",
        action: "Added PlanItem for rollback testing"
      }
    ]
  }
  
  items: [
    PlanItem {
      id: "phase-1"
      title: "Set up OAuth2 provider integration"
      status: "completed"
      system3: {
        confidence: 0.90
        capabilityUsed: "cap-oauth2"
        reusedFrom: "playbook-oauth-setup"
        forwardLearning: true
        intrinsicReward: {
          mastery: 0.8
          autonomy: 0.9
          coherence: 0.95
          totalReward: 0.88
        }
      }
    },
    PlanItem {
      id: "phase-2"
      title: "Implement token refresh mechanism"
      status: "inProgress"
      system3: {
        confidence: 0.60  // Lower due to knowledge gap
        capabilityDeveloped: "cap-jwt-refresh"
        uncertainties: [
          "Optimal refresh token expiry duration",
          "Handling concurrent refresh requests"
        ]
        intrinsicReward: {
          curiosity: 0.9    // High learning opportunity
          novelty: 0.8
          competenceGrowth: 0.85
          totalReward: 0.85
        }
      }
    },
    PlanItem {
      id: "phase-3"
      title: "Migrate existing sessions"
      status: "pending"
      system3: {
        confidence: 0.65
        capabilityUsed: "cap-session-migration"
        uncertainties: [
          "Session data format compatibility",
          "Handling active sessions during migration"
        ]
      }
    }
  ]
  
  narratives: [
    {
      type: "approach",
      text: "Phased migration with backward compatibility period to minimize risk..."
    },
    {
      type: "reflection",
      text: "This plan leverages my strong OAuth2 capability while addressing my gap in token refresh patterns through deliberate learning in Phase 2."
    }
  ]
}
```

### Playbook with Long-Term Identity

```javascript
Playbook {
  id: "playbook-backend-auth"
  title: "Backend Authentication Patterns"
  domain: "backend"
  
  system3: {
    selfModel: {
      capabilities: [
        {
          id: "cap-oauth2",
          name: "OAuth2 implementation",
          domain: "backend-auth",
          confidence: 0.90,
          evidenceCount: 47,
          successRate: 0.92,
          lastUsedAt: "2025-12-28T10:00:00Z"
        },
        {
          id: "cap-jwt",
          name: "JWT token management",
          domain: "backend-auth",
          confidence: 0.88,
          evidenceCount: 34
        },
        {
          id: "cap-session-migration",
          name: "Session migration",
          domain: "backend-auth",
          confidence: 0.75,
          evidenceCount: 8,
          successRate: 0.80
        }
      ]
      
      identityGoal: "Build secure, maintainable authentication systems"
      
      narrativeIdentity: "I am a security-conscious backend specialist who values thorough testing, clear documentation, and conservative migration strategies. I prioritize user safety and system reliability over speed."
      
      coreValues: [
        "security-first",
        "test-driven",
        "gradual-migration",
        "comprehensive-documentation"
      ]
      
      coherenceScore: 0.93
      
      strengths: [
        "OAuth2 implementation",
        "API security patterns",
        "Phased rollout strategies"
      ]
      
      knowledgeGaps: []  // All identified gaps resolved
    }
    
    userPersonas: [
      {
        userId: "persona-conservative",
        beliefs: {
          "riskTolerance": "low",
          "securityPriority": "critical"
        },
        preferences: {
          "migrationStyle": "phased",
          "documentationLevel": "thorough"
        },
        relationshipState: "established"
      },
      {
        userId: "persona-agile",
        beliefs: {
          "speed": "high-priority",
          "iterationCycle": "fast"
        },
        preferences: {
          "migrationStyle": "feature-flag",
          "documentationLevel": "minimal"
        },
        relationshipState: "established"
      }
    ]
    
    coreValues: [
      "security-first",
      "user-safety",
      "maintainability",
      "thorough-testing"
    ]
    
    evolutionLog: [
      {
        timestamp: "2025-11-15T00:00:00Z",
        milestone: "Initial authentication capability established",
        capabilitiesAdded: ["cap-basic-auth", "cap-jwt"]
      },
      {
        timestamp: "2025-12-01T00:00:00Z",
        milestone: "OAuth2 mastery achieved",
        capabilitiesAdded: ["cap-oauth2"],
        knowledgeGapsResolved: ["gap-oauth-flows", "gap-token-validation"]
      },
      {
        timestamp: "2025-12-27T00:00:00Z",
        milestone: "Session migration competence developed",
        capabilitiesAdded: ["cap-session-migration"],
        knowledgeGapsResolved: ["gap-session-state"]
      }
    ]
    
    forwardLearningMetrics: {
      totalReuses: 89,
      averageReasoningReduction: 0.83,  // 83% fewer steps for known patterns
      patternsReused: {
        "oauth2-setup": 23,
        "jwt-implementation": 31,
        "token-refresh": 18,
        "session-migration": 8,
        "api-security": 9
      }
    }
  }
  
  items: [
    PlaybookItem {
      id: "pattern-oauth-setup"
      title: "OAuth2 Provider Integration"
      category: "authentication"
      
      system3: {
        capabilityRequired: ["cap-oauth2"]
        userPersonaFit: ["persona-conservative", "persona-agile"]
        intrinsicValue: 0.85,
        reuseCount: 23,
        averageConfidence: 0.88,
        lastReusedAt: "2025-12-28T10:00:00Z"
      }
      
      evidence: [...]
      antiPatterns: [...]
    }
  ]
}
```

---

## Quantitative Benefits (From Sophia Paper)

The original Sophia framework demonstrated:

1. **80% reduction in reasoning steps** for recurring operations via forward learning
2. **40% improvement in success rate** for high-complexity tasks via meta-cognitive persistence
3. **Autonomous goal generation** - agent independently initiated 100+ intrinsic learning tasks during 24-hour deployment
4. **Identity coherence** - maintained consistent narrative across extended operation

vBRIEF + System 3 enables similar capabilities:
- **Forward learning**: `PlaybookItem.system3.reuseCount` and `forwardLearningMetrics` track efficiency gains
- **Meta-cognitive monitoring**: `coherenceScore` and `coherenceIssues` enable real-time self-correction
- **Autonomous learning**: `KnowledgeGap` detection → `intrinsicGoals` → auto-generated Plans
- **Identity persistence**: `Playbook.system3.selfModel` and `evolutionLog` maintain autobiographical continuity

---

## Implementation Guidance

### Minimal Adoption

Start with just:
1. `Plan.system3.userModel` - Track user context for better planning
2. `SelfModel.knowledgeGaps` - Detect learning needs
3. `PlanItem.system3.confidence` - Track agent certainty

### Full Adoption

For persistent, autonomous agents:
1. Maintain `Playbook.system3.selfModel` with complete capability inventory
2. Track `forwardLearningMetrics` to measure efficiency gains
3. Auto-generate Plans from `KnowledgeGap` detection
4. Use `IntrinsicReward` to balance external tasks with learning
5. Store `UserModel` templates as personas in Playbook
6. Log `evolutionLog` to maintain identity continuity across reboots

### Integration with Existing Tools

System 3 fields are optional metadata - existing vBRIEF tools can:
- **Ignore System 3 fields** - Documents remain valid without them
- **Read for display** - Show agent confidence, learning goals, etc.
- **Preserve on rewrite** - Keep unknown fields per spec

---

## Future Directions

1. **Executable Self-Model**: Enable agents to verify capabilities via actual execution
2. **Multi-Agent Coordination**: Share user models and capabilities across agent instances
3. **Curiosity Metrics**: Formalize information gain and novelty calculations
4. **Identity Templates**: Reusable personality/value configurations
5. **Automatic Coherence Repair**: Self-healing when inconsistencies detected
6. **Social Dynamics**: Model agent-agent relationships beyond agent-user

---

## Compatibility

This extension is fully backward compatible with vBRIEF v0.3. All System 3 fields are optional.

Tools that don't understand this extension should:
- Ignore `system3` fields on all types
- Preserve `system3` fields when rewriting documents
- Treat System 3-generated Plans as normal Plans

---

## References

### Primary Source

- **Sun, M., Hong, F., & Zhang, W.** (2025). *Sophia: A Persistent Agent Framework of Artificial Life*. arXiv preprint arXiv:2512.18202. https://arxiv.org/abs/2512.18202

### Psychological Foundations

- **Dunlosky, J., & Metcalfe, J.** (2008). *Metacognition*. Sage Publications. https://doi.org/10.4135/9781412950640
- **Ezzyat, Y., & Davachi, L.** (2011). What constitutes an episode in episodic memory? *Psychological Science*, 22(2), 243-252. https://doi.org/10.1037/a0021558
- **Fishbach, A., & Woolley, K.** (2022). The structure of intrinsic motivation. *Annual Review of Organizational Psychology and Organizational Behavior*, 9, 339-363. https://doi.org/10.1146/annurev-psych-020821-103621
- **Frith, C. D., & Frith, U.** (2005). Theory of mind. *Current Biology*, 15(17), R644-R645. https://doi.org/10.1016/j.neuron.2005.03.011
- **Shaughnessy, M. F., Veenman, M. V., & Kleyn-Kennedy, C.** (Eds.). (2008). *Meta-cognition: A recent review of research, theory, and perspectives*. Nova Science Publishers. https://doi.org/10.4135/9781412956802
- **Tulving, E.** (2002). Episodic memory: From mind to brain. *Annual Review of Psychology*, 53(1), 1-25. https://doi.org/10.1146/annurev.psych.53.100901.135114
- **Wellman, H. M.** (2018). Theory of mind: The state of the art. *European Journal of Developmental Psychology*, 15(6), 728-755. https://doi.org/10.1146/annurev-psych-010416-044139

### Related vBRIEF Extensions

- **vBRIEF Core Specification v0.3**: README.md
- **Extension 2 (Identifiers)**: README.md#extension-2-identifiers
- **Extension 3 (Rich Metadata)**: README.md#extension-3-rich-metadata
- **Extension 12 (Playbooks)**: vBRIEF-extension-playbooks.md
- **Agentic Patterns Extension**: vBRIEF-extension-agentic-patterns.md
- **Model-First Reasoning Extension**: vBRIEF-extension-model-first-reasoning.md
- **Experimental Workflows Extension**: vBRIEF-extension-experimental-workflows.md

---

## License

This specification is released under CC BY 4.0.

---

## Changelog

### Version 0.1 (2025-12-28)
- Initial draft based on Sophia framework
- Four psychological pillars: Meta-cognition, Theory of Mind, Intrinsic Motivation, Episodic Memory
- System 3 extensions to Plan, PlanItem, TodoList, TodoItem, Playbook, PlaybookItem
- UserModel, SelfModel, Capability, KnowledgeGap, IntrinsicReward types
- Forward learning metrics and identity evolution tracking
- Integration with Agentic Patterns, MFR, Experimental Workflows, and Playbooks extensions
