# vBRIEF Extension Proposal: Session Memory & Compression

> **VERY EARLY DRAFT**: This is an initial proposal and subject to significant change. Comments, feedback, and suggestions are strongly encouraged. Please provide input via GitHub issues or discussions.

**Extension Name**: Session Memory & Compression  
**Version**: 0.1 (Draft)  
**Status**: Proposal  
**Author**: Jonathan Taylor (visionik@pobox.com)  
**Date**: 2025-12-27

## Overview

This extension introduces automatic session capture, AI-powered compression, and progressive disclosure of context, inspired by [claude-mem](https://github.com/thedotmack/claude-mem). While Extension 12 (ACE) provides long-term memory, it doesn't address the challenge of **automatic capture** from agent sessions or **intelligent compression** to manage token costs.

Session Memory & Compression enables:
- **Automatic vBRIEF generation** from agent work sessions
- **AI-powered compression** of observations and learnings
- **Progressive disclosure** with explicit token cost visibility
- **Cross-session continuity** without manual documentation
- **Privacy-aware capture** with automatic redaction
- **Semantic search** across historical sessions

## Motivation

**Current limitations:**
- **Manual documentation burden**: Agents must explicitly create vBRIEF documents
- **Token cost explosion**: Long ACE playbooks consume thousands of tokens
- **Loss of context**: Session ends → knowledge vanishes unless manually saved
- **Unstructured memory**: Free-form notes lack queryability
- **No token visibility**: Users don't know cost of loading context

**How Session Memory & Compression helps:**
- **Automatic capture**: Session observations → structured vBRIEF
- **Intelligent compression**: 500-token observation → 50-token summary (90% reduction)
- **Progressive loading**: Load only what's needed, show token costs upfront
- **Semantic retention**: Key insights preserved, boilerplate discarded
- **Privacy by default**: Sensitive data automatically redacted

**Research foundation:**

claude-mem demonstrates that automatic capture + AI compression enables persistent memory without overwhelming context windows. By combining claude-mem's compression with vBRIEF's structure, we get **queryable, reusable, token-efficient memory**.

**Integration goal**: Make vBRIEF the automatic, intelligent memory layer for all agentic systems, not just those with explicit documentation workflows.

## Dependencies

**Required**:
- Core vBRIEF types (vBRIEFInfo, TodoList, TodoItem, Plan)
- Extension 2 (Identifiers) - for session IDs and observation references
- Extension 12 (ACE) - for storing compressed learnings

**Recommended**:
- Extension 1 (Timestamps) - for session temporal tracking
- Extension 9 (Security) - for privacy-aware redaction
- Extension 10 (Version Control) - for tracking compression versions
- MCP Extension - for memory search tools

## Core Concepts

### Session Lifecycle

```
1. Session Active
   └─> Agent performs actions (edit files, run commands, reason)
   
2. Observation Capture
   └─> Each action recorded with: tool, input, output, tokens, timestamp
   
3. Session End
   └─> Trigger compression & vBRIEF generation
   
4. Compression
   └─> AI summarizes observations → key learnings + completed todos
   
5. Storage
   └─> Save compressed vBRIEF document
   
6. Future Session
   └─> Progressive disclosure: load relevant context with token costs
```

### Compression Strategies

**Level 1: Verbatim (No Compression)**
- Store complete observation
- Use for: Critical decisions, security incidents
- Token cost: 100% of original

**Level 2: Semantic Compression**
- Extract key facts, discard boilerplate
- Use for: Routine work, common patterns
- Token cost: 15-30% of original

**Level 3: Aggregation**
- Combine multiple related observations
- Use for: Repeated actions, batch operations
- Token cost: 5-10% of original

**Level 4: Reference Only**
- Store only metadata, retrieve on demand
- Use for: Large outputs, temporary context
- Token cost: <1% of original

### Progressive Disclosure

Context loaded in tiers, with explicit token costs:

```
Tier 0 (Free): Session summary (20 tokens)
  "Fixed OAuth bug, added tests, updated docs"

Tier 1 (50 tokens): Key metrics
  - 3 files edited
  - 5 tests added (all passing)
  - 1 learning: "PKCE flow requires state param"

Tier 2 (200 tokens): TodoList
  - Completed: Fix OAuth PKCE flow
  - Completed: Add integration tests
  - Completed: Update README

Tier 3 (800 tokens): Full Plan
  - Problem model with constraints
  - Detailed implementation phases
  - Validation results

Tier 4 (2000 tokens): Raw observations
  - Complete file diffs
  - Full command outputs
  - Extended reasoning traces
```

Agent loads only what's needed, user sees costs upfront.

## New Types

### SessionInfo

Metadata about a captured session.

```javascript
SessionInfo {
  id: string                       # Unique session identifier
  startTime: datetime              # When session began
  endTime?: datetime               # When session ended
  agent: string                    # Agent identifier (e.g., "claude-3.5-sonnet")
  context: string                  # Session context (e.g., "OAuth implementation")
  totalObservations: number        # Count of captured observations
  compressionRatio: number         # Overall compression achieved (0.0-1.0)
  tokensSaved: number              # Tokens saved via compression
  tools: string[]                  # Tools used in session
  status: enum                     # "active" | "completed" | "abandoned"
}
```

### Observation

A single captured action from the session.

```javascript
Observation {
  id: string                       # Unique observation ID
  sessionId: string                # Parent session
  timestamp: datetime              # When action occurred
  tool: string                     # Tool used (e.g., "edit_files", "run_shell_command")
  input: any                       # Tool input
  output: any                      # Tool output/result
  reasoning?: string               # Agent's reasoning (if captured)
  tokens: number                   # Token cost of this observation
  tags: string[]                   # Semantic tags (e.g., "error-fixed", "test-added")
  compressionLevel: enum           # "verbatim" | "semantic" | "aggregated" | "reference"
  compressed?: CompressedObservation  # If compressed
}
```

### CompressedObservation

AI-compressed version of observation.

```javascript
CompressedObservation {
  summary: string                  # AI-generated summary
  keyFacts: string[]               # Essential information extracted
  originalTokens: number           # Pre-compression token count
  compressedTokens: number         # Post-compression token count
  compressionRatio: number         # Achieved compression (0.0-1.0)
  compressionMethod: string        # "llm-summarize" | "semantic-extract" | "template"
  lossyIndicator: boolean          # True if information was discarded
  reconstructible: boolean         # True if original can be recovered
}
```

### MemoryTier

Tiered context for progressive disclosure.

```javascript
MemoryTier {
  tier: number                     # Tier level (0-4)
  label: string                    # Human-readable tier name
  content: string                  # Content for this tier
  tokenCost: number                # Cost to load this tier
  loaded: boolean                  # Whether tier is currently loaded
  nextTier?: MemoryTier            # Pointer to next tier
}
```

### SessionSnapshot

Complete session state for vBRIEF export.

```javascript
SessionSnapshot {
  sessionInfo: SessionInfo         # Session metadata
  observations: Observation[]      # Captured observations
  generatedTodos?: TodoItem[]      # Auto-extracted todos
  generatedLearnings?: Learning[]  # Auto-extracted learnings
  memoryTiers: MemoryTier[]        # Progressive disclosure tiers
  compressionStats: CompressionStats  # Overall compression metrics
}
```

### CompressionStats

Statistics about compression effectiveness.

```javascript
CompressionStats {
  totalObservations: number
  originalTokens: number           # Pre-compression total
  compressedTokens: number         # Post-compression total
  tokensSaved: number              # originalTokens - compressedTokens
  compressionRatio: number         # compressedTokens / originalTokens
  averageRatioByTier: Record<number, number>  # Compression per tier
  methodUsage: Record<string, number>  # Which compression methods used
}
```

## vBRIEFInfo Extensions

```javascript
vBRIEFInfo {
  // Core fields...
  sessionInfo?: SessionInfo        # If auto-generated from session
  compressionStats?: CompressionStats  # Compression metadata
  autoGenerated: boolean           # True if created automatically
  memoryTiers?: MemoryTier[]       # Progressive disclosure structure
}
```

## TodoItem Extensions

```javascript
TodoItem {
  // Prior extensions...
  sourceObservation?: string       # Observation ID this was extracted from
  inferredFromSession: boolean     # True if auto-detected (vs manually created)
  compressionLevel?: enum          # How much detail preserved
}
```

## PlaybookEntry Extensions (Extension 12)

```javascript
PlaybookEntry {
  // Prior extensions...
  sourceObservations?: string[]    # Observation IDs this learning came from
  compressed: boolean              # Whether content is compressed
  compressionMetadata?: {
    originalTokens: number
    compressedTokens: number
    compressionRatio: number
    method: string                 # "llm-summarize" | "semantic-extract"
    canExpand: boolean             # Can retrieve full detail
    fullContentRef?: string        # Reference to full content
  }
}
```

## Usage Patterns

### Pattern 1: Automatic vBRIEF Generation from Session

**Use case**: Session ends, automatically create vBRIEF document.

```typescript
// Agent session completes
const session: SessionInfo = {
  id: "session-2024-12-27-oauth",
  startTime: "2024-12-27T10:00:00Z",
  endTime: "2024-12-27T12:30:00Z",
  agent: "claude-3.5-sonnet",
  context: "Implement OAuth2 with PKCE",
  totalObservations: 47,
  compressionRatio: 0.12,  // 88% reduction
  tokensSaved: 3850,
  tools: ["edit_files", "run_shell_command", "read_files"],
  status: "completed"
};

// Observations captured during session
const observations: Observation[] = [
  {
    id: "obs-1",
    sessionId: session.id,
    timestamp: "2024-12-27T10:05:00Z",
    tool: "edit_files",
    input: { file: "auth.ts", changes: "..." },
    output: { success: true },
    reasoning: "Added PKCE challenge generation",
    tokens: 450,
    tags: ["oauth", "security", "pkce"],
    compressionLevel: "semantic",
    compressed: {
      summary: "Implemented PKCE challenge/verifier generation in auth.ts",
      keyFacts: [
        "Used crypto.randomBytes for code_verifier",
        "SHA256 hash for code_challenge",
        "Base64URL encoding applied"
      ],
      originalTokens: 450,
      compressedTokens: 68,
      compressionRatio: 0.15,
      compressionMethod: "llm-summarize",
      lossyIndicator: true,
      reconstructible: false
    }
  },
  // ... 46 more observations
];

// Auto-generate vBRIEF
const vBRIEF: VAgendaDocument = await generateFromSession(
  session,
  observations
);

// Result
{
  vBRIEFInfo: {
    version: "0.2",
    author: "claude-3.5-sonnet",
    sessionInfo: session,
    compressionStats: {
      totalObservations: 47,
      originalTokens: 4380,
      compressedTokens: 530,
      tokensSaved: 3850,
      compressionRatio: 0.12,
      averageRatioByTier: {
        0: 0.05,  // Summary
        1: 0.10,  // Key facts
        2: 0.15,  // Todos
        3: 0.30   // Details
      },
      methodUsage: {
        "llm-summarize": 35,
        "semantic-extract": 10,
        "aggregated": 2
      }
    },
    autoGenerated: true
  },
  todoList: {
    items: [
      {
        title: "Implement PKCE challenge generation",
        status: "completed",
        sourceObservation: "obs-1",
        inferredFromSession: true,
        completedAt: "2024-12-27T10:05:00Z"
      },
      {
        title: "Add PKCE integration tests",
        status: "completed",
        sourceObservation: "obs-23",
        inferredFromSession: true
      },
      {
        title: "Update OAuth documentation",
        status: "completed",
        sourceObservation: "obs-41",
        inferredFromSession: true
      }
    ]
  },
  playbook: {
    learnings: [
      {
        category: "patterns",
        title: "PKCE OAuth Implementation",
        content: "PKCE requires code_verifier (random) and code_challenge (SHA256 of verifier, base64url-encoded). State param mandatory for CSRF protection.",
        sourceObservations: ["obs-1", "obs-5", "obs-12"],
        compressed: true,
        compressionMetadata: {
          originalTokens: 1250,
          compressedTokens: 87,
          compressionRatio: 0.07,
          method: "llm-summarize",
          canExpand: true,
          fullContentRef: "sessions/session-2024-12-27-oauth/full"
        }
      }
    ]
  }
}
```

### Pattern 2: Progressive Disclosure in New Session

**Use case**: Agent starts new session, loads context progressively.

```typescript
// New session starts
const newSession = await startSession({
  context: "Add GitHub OAuth provider"
});

// Agent queries memory
const memorySearch = await vbriefMemorySearch({
  query: "oauth implementation",
  includeTokenCosts: true
});

// Response shows tiered context
{
  results: [
    {
      sessionId: "session-2024-12-27-oauth",
      memoryTiers: [
        {
          tier: 0,
          label: "Summary",
          content: "Implemented OAuth2 with PKCE for Google login",
          tokenCost: 15,
          loaded: true  // Auto-loaded (cheap)
        },
        {
          tier: 1,
          label: "Key Facts",
          content: "- PKCE uses code_verifier + code_challenge\n- State param for CSRF\n- Tests added and passing",
          tokenCost: 45,
          loaded: false  // Not loaded yet
        },
        {
          tier: 2,
          label: "Completed Todos",
          content: "[TodoList with 3 items]",
          tokenCost: 180,
          loaded: false
        },
        {
          tier: 3,
          label: "Full Learnings",
          content: "[Detailed playbook entry]",
          tokenCost: 650,
          loaded: false
        }
      ],
      totalAvailableTokens: 890,
      recommendedTier: 1  // Load up to tier 1
    }
  ]
}

// Agent sees prompt
"""
Found relevant session: "OAuth2 with PKCE" (15 tokens loaded)

Summary: Implemented OAuth2 with PKCE for Google login

Need more detail?
- Load Key Facts (+45 tokens)
- Load Completed Todos (+180 tokens)
- Load Full Learnings (+650 tokens)
"""

// Agent decides: load tier 1
await loadMemoryTier(sessionId, 1);

// Now has 60 tokens of context (tier 0 + tier 1)
// Saved 830 tokens by not loading tiers 2-3
```

### Pattern 3: Compression of ACE Playbook

**Use case**: Playbook growing too large, compress old entries.

```typescript
// Current playbook entry (uncompressed)
const entry: PlaybookEntry = {
  category: "gotchas",
  title: "PostgreSQL migration deadlock issues",
  content: `
    During the MySQL→PostgreSQL migration, we encountered several deadlock
    issues when running concurrent migrations. The root cause was...
    
    [2000 tokens of detailed explanation, stack traces, tried solutions, etc.]
  `,
  tags: ["database", "migration", "deadlock"],
  compressed: false
};

// Compress using LLM
const compressed = await compressPlaybookEntry(entry);

// Result
{
  category: "gotchas",
  title: "PostgreSQL migration deadlock issues",
  content: "Concurrent migrations caused deadlocks. Solution: serialize migrations with advisory locks. Use pg_advisory_lock(migration_id) before ALTER TABLE.",
  tags: ["database", "migration", "deadlock"],
  compressed: true,
  sourceObservations: ["obs-847", "obs-901", "obs-920"],
  compressionMetadata: {
    originalTokens: 2100,
    compressedTokens: 87,
    compressionRatio: 0.04,  // 96% compression!
    method: "llm-summarize",
    canExpand: true,
    fullContentRef: "sessions/session-2024-11-15-db-migration/obs-920"
  }
}

// Token savings: 2013 tokens
// Information preserved: Key insight + solution
// Expandable: Yes, can retrieve full detail if needed
```

### Pattern 4: Privacy-Aware Capture

**Use case**: Session contains sensitive data, auto-redact before storage.

```typescript
// Observation captured with sensitive data
const observation: Observation = {
  id: "obs-42",
  sessionId: "session-oauth-config",
  tool: "edit_files",
  input: {
    file: ".env",
    content: `
      OAUTH_CLIENT_ID=abc123xyz
      OAUTH_CLIENT_SECRET=super_secret_key_here
      DATABASE_PASSWORD=admin123
    `
  },
  output: { success: true },
  tokens: 150,
  tags: ["config", "secrets"]
};

// Auto-detect sensitive patterns
const sanitized = await sanitizeObservation(observation);

// Result
{
  id: "obs-42",
  sessionId: "session-oauth-config",
  tool: "edit_files",
  input: {
    file: ".env",
    content: `
      OAUTH_CLIENT_ID=[REDACTED]
      OAUTH_CLIENT_SECRET=[REDACTED]
      DATABASE_PASSWORD=[REDACTED]
    `
  },
  output: { success: true },
  tokens: 80,  // Reduced (redacted content shorter)
  tags: ["config", "secrets", "REDACTED"],
  redactionInfo: {
    type: "remove",
    reason: "sensitive-credentials",
    redactedBy: "auto-privacy-filter",
    redactedAt: "2024-12-27T12:00:00Z",
    patterns: ["OAUTH_.*=.*", ".*PASSWORD.*=.*"],
    recoverable: false
  },
  compressed: {
    summary: "Configured OAuth environment variables",
    keyFacts: [
      "Set OAUTH_CLIENT_ID",
      "Set OAUTH_CLIENT_SECRET", 
      "Set DATABASE_PASSWORD"
    ],
    originalTokens: 150,
    compressedTokens: 45,
    compressionRatio: 0.30,
    compressionMethod: "semantic-extract",
    lossyIndicator: true,
    reconstructible: false
  }
}

// Privacy preserved + compressed
// Original: 150 tokens with secrets exposed
// Result: 45 tokens with secrets redacted
```

### Pattern 5: Cross-Session Learning Accumulation

**Use case**: Multiple sessions tackle similar problems, accumulate learnings.

```typescript
// Session 1: Initial OAuth implementation
const session1Learnings = [
  {
    content: "PKCE requires code_verifier and code_challenge",
    sourceObservations: ["s1-obs-5"]
  }
];

// Session 2: Add refresh tokens
const session2Learnings = [
  {
    content: "Refresh tokens must be rotated on each use for security",
    sourceObservations: ["s2-obs-23"]
  }
];

// Session 3: Handle token expiry
const session3Learnings = [
  {
    content: "Check exp claim before using token to avoid 401 errors",
    sourceObservations: ["s3-obs-67"]
  }
];

// Auto-aggregate into single playbook entry
const aggregated = await aggregateLearnings([
  ...session1Learnings,
  ...session2Learnings,
  ...session3Learnings
], {
  category: "patterns",
  topic: "oauth-implementation"
});

// Result: Compressed, coherent learning
{
  category: "patterns",
  title: "OAuth2 Implementation Best Practices",
  content: `
    1. PKCE: Use code_verifier (random) + code_challenge (SHA256, base64url)
    2. Refresh tokens: Rotate on each use for security
    3. Token validation: Check exp claim before use to avoid errors
  `,
  sourceObservations: ["s1-obs-5", "s2-obs-23", "s3-obs-67"],
  compressed: true,
  compressionMetadata: {
    originalTokens: 450,  // Sum of 3 sessions
    compressedTokens: 95,
    compressionRatio: 0.21,
    method: "llm-aggregation",
    canExpand: true,
    fullContentRef: "aggregated/oauth-learnings-dec-2024"
  },
  aggregatedFrom: [
    "session-2024-12-20-oauth-initial",
    "session-2024-12-22-oauth-refresh",
    "session-2024-12-27-oauth-expiry"
  ]
}

// 3 sessions → 1 coherent learning
// 450 tokens → 95 tokens (79% reduction)
```

### Pattern 6: Memory Search with Token Budgets

**Use case**: Agent has 2000-token budget, search and load optimally.

```typescript
const searchResults = await vbriefMemorySearch({
  query: "authentication implementation issues",
  tokenBudget: 2000,
  optimizeFor: "relevance"  // vs "coverage"
});

// Smart ranking by relevance/token ratio
{
  results: [
    {
      sessionId: "session-oauth-pkce",
      relevanceScore: 0.95,
      tier0: {
        content: "Fixed OAuth PKCE bug",
        tokens: 10,
        relevancePerToken: 0.095  // Excellent ratio
      },
      tier1: {
        content: "PKCE code_challenge must use SHA256, not plain",
        tokens: 40,
        relevancePerToken: 0.024
      }
    },
    {
      sessionId: "session-jwt-validation",
      relevanceScore: 0.87,
      tier0: {
        content: "JWT signature validation failures",
        tokens: 12,
        relevancePerToken: 0.073
      },
      tier1: {
        content: "Use RS256, not HS256, for asymmetric verification",
        tokens: 35,
        relevancePerToken: 0.025
      }
    },
    {
      sessionId: "session-db-auth-migration",
      relevanceScore: 0.42,
      tier0: {
        content: "Database authentication schema changes",
        tokens: 15,
        relevancePerToken: 0.028
      }
      // Lower relevance, skip for now
    }
  ],
  recommendedLoad: [
    { sessionId: "session-oauth-pkce", tiers: [0, 1] },  // 50 tokens
    { sessionId: "session-jwt-validation", tiers: [0, 1] }  // 47 tokens
  ],
  totalTokens: 97,
  budgetRemaining: 1903
}

// Agent loads recommended context (97 tokens)
// High relevance + low token cost
// 1903 tokens remaining for other context
```

### Pattern 7: Expansion on Demand

**Use case**: Compressed summary insufficient, expand to full detail.

```typescript
// Agent sees compressed learning
const compressed = {
  title: "React useEffect cleanup pattern",
  content: "Always return cleanup function from useEffect to prevent memory leaks",
  tokens: 25,
  compressionMetadata: {
    canExpand: true,
    fullContentRef: "sessions/session-react-refactor/obs-234"
  }
};

// Agent needs more detail
const expanded = await expandMemory(compressed.compressionMetadata.fullContentRef);

// Full original observation retrieved
{
  title: "React useEffect cleanup pattern",
  content: `
    When using useEffect with subscriptions, timers, or event listeners,
    always return a cleanup function:
    
    useEffect(() => {
      const timer = setInterval(() => { ... }, 1000);
      
      return () => clearInterval(timer);  // Cleanup
    }, []);
    
    Without cleanup:
    - Memory leaks from orphaned intervals
    - Multiple event listeners on same element
    - Stale closures capturing old state
    
    We fixed 3 memory leaks using this pattern in Dashboard.tsx,
    ProfileView.tsx, and NotificationBell.tsx.
    
    Test coverage: Added LeakDetector test that verifies cleanup runs.
  `,
  tokens: 280,
  originalObservation: "obs-234"
}

// Cost: 25 tokens → 280 tokens
// Benefit: Full context when needed
```

## Implementation Notes

### Compression Algorithm

```typescript
interface CompressionOptions {
  targetRatio: number;              // Desired compression (0.1 = 90% reduction)
  preserveKeyFacts: boolean;        // Keep critical information
  allowLossy: boolean;              // Can discard non-essential content
  method: "llm" | "semantic" | "template";
}

async function compressObservation(
  observation: Observation,
  options: CompressionOptions
): Promise<CompressedObservation> {
  
  if (options.method === "llm") {
    // Use LLM to summarize
    const prompt = `
      Compress this observation to ${options.targetRatio * 100}% of original length.
      Preserve key facts and insights. Discard boilerplate and redundancy.
      
      Observation:
      Tool: ${observation.tool}
      Input: ${JSON.stringify(observation.input)}
      Output: ${JSON.stringify(observation.output)}
      Reasoning: ${observation.reasoning}
      
      Compressed summary:
    `;
    
    const summary = await llm.complete(prompt, {
      maxTokens: Math.floor(observation.tokens * options.targetRatio)
    });
    
    return {
      summary: summary.text,
      keyFacts: await extractKeyFacts(observation),
      originalTokens: observation.tokens,
      compressedTokens: summary.tokens,
      compressionRatio: summary.tokens / observation.tokens,
      compressionMethod: "llm-summarize",
      lossyIndicator: true,
      reconstructible: false
    };
  }
  
  if (options.method === "semantic") {
    // Extract structured facts
    const facts = await extractSemanticFacts(observation);
    const summary = facts.join("; ");
    
    return {
      summary,
      keyFacts: facts,
      originalTokens: observation.tokens,
      compressedTokens: estimateTokens(summary),
      compressionRatio: estimateTokens(summary) / observation.tokens,
      compressionMethod: "semantic-extract",
      lossyIndicator: false,
      reconstructible: true
    };
  }
  
  // Template-based compression
  const template = matchTemplate(observation);
  if (template) {
    return applyTemplate(observation, template);
  }
  
  // Fallback: no compression
  return verbatimObservation(observation);
}

async function extractKeyFacts(observation: Observation): Promise<string[]> {
  // Extract essential information
  const facts: string[] = [];
  
  // What was done?
  facts.push(`Action: ${observation.tool}`);
  
  // What was the outcome?
  if (observation.output.success) {
    facts.push("Result: Success");
  } else {
    facts.push(`Result: Failed - ${observation.output.error}`);
  }
  
  // Any key insights?
  if (observation.reasoning) {
    const insights = await extractInsights(observation.reasoning);
    facts.push(...insights);
  }
  
  return facts;
}
```

### Progressive Disclosure Implementation

```typescript
interface ProgressiveContext {
  sessionId: string;
  tiers: Map<number, MemoryTier>;
  currentTier: number;
  totalTokenBudget: number;
  tokensUsed: number;
}

class ProgressiveMemoryLoader {
  
  async loadOptimal(
    context: ProgressiveContext,
    relevanceThreshold: number = 0.7
  ): Promise<string> {
    let content = "";
    
    // Always load tier 0 (summary) - it's cheap
    const tier0 = await this.loadTier(context, 0);
    content += tier0.content;
    context.tokensUsed += tier0.tokenCost;
    
    // Load subsequent tiers if budget allows
    for (let tier = 1; tier <= 4; tier++) {
      const tierData = context.tiers.get(tier);
      if (!tierData) break;
      
      // Check budget
      if (context.tokensUsed + tierData.tokenCost > context.totalTokenBudget) {
        break;
      }
      
      // Check relevance
      const relevance = await this.estimateRelevance(tierData, context);
      if (relevance < relevanceThreshold) {
        break;
      }
      
      // Load tier
      content += "\n" + tierData.content;
      context.tokensUsed += tierData.tokenCost;
      context.currentTier = tier;
    }
    
    return content;
  }
  
  async loadTier(
    context: ProgressiveContext,
    tier: number
  ): Promise<MemoryTier> {
    const tierData = context.tiers.get(tier);
    if (!tierData) {
      throw new Error(`Tier ${tier} not available`);
    }
    
    if (!tierData.loaded) {
      // Fetch tier content (from file, DB, etc.)
      const content = await this.fetchTierContent(
        context.sessionId,
        tier
      );
      tierData.content = content;
      tierData.loaded = true;
    }
    
    return tierData;
  }
  
  async estimateRelevance(
    tier: MemoryTier,
    context: ProgressiveContext
  ): Promise<number> {
    // Use embedding similarity or LLM to estimate relevance
    // Higher tier = more detailed = potentially less relevant
    
    // Simple heuristic: diminishing relevance per tier
    const baseRelevance = 1.0;
    const tierPenalty = tier * 0.15;
    return Math.max(0, baseRelevance - tierPenalty);
  }
  
  getLoadingSummary(context: ProgressiveContext): string {
    const remaining = context.totalTokenBudget - context.tokensUsed;
    const nextTier = context.currentTier + 1;
    const nextTierData = context.tiers.get(nextTier);
    
    let summary = `Loaded tier ${context.currentTier} (${context.tokensUsed} tokens used)`;
    
    if (nextTierData && remaining >= nextTierData.tokenCost) {
      summary += `\n\nLoad more detail?\n`;
      summary += `- Tier ${nextTier}: ${nextTierData.label} (+${nextTierData.tokenCost} tokens)`;
    } else if (remaining < (nextTierData?.tokenCost || 0)) {
      summary += `\n\nToken budget exhausted (${remaining} remaining)`;
    }
    
    return summary;
  }
}
```

### Privacy Filter

```typescript
const SENSITIVE_PATTERNS = [
  /API[_-]?KEY[=:]\s*[\w-]+/gi,
  /SECRET[=:]\s*[\w-]+/gi,
  /PASSWORD[=:]\s*[\w-]+/gi,
  /Bearer\s+[\w-]+/gi,
  /[A-Za-z0-9]{32,}/g,  // Long random strings (likely tokens)
  /\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b/g  // Emails
];

function sanitizeContent(content: string): {
  sanitized: string;
  redactionInfo?: RedactionInfo;
} {
  let sanitized = content;
  let redactionCount = 0;
  const redactedPatterns: string[] = [];
  
  for (const pattern of SENSITIVE_PATTERNS) {
    const matches = content.match(pattern);
    if (matches) {
      redactionCount += matches.length;
      redactedPatterns.push(pattern.toString());
      sanitized = sanitized.replace(pattern, "[REDACTED]");
    }
  }
  
  if (redactionCount > 0) {
    return {
      sanitized,
      redactionInfo: {
        type: "remove",
        reason: "sensitive-credentials",
        redactedBy: "auto-privacy-filter",
        redactedAt: new Date().toISOString(),
        recoverable: false,
        patterns: redactedPatterns
      }
    };
  }
  
  return { sanitized };
}
```

## Integration with Existing Extensions

### Extension 12 (ACE)

Session Memory enhances ACE with:
- **Automatic capture**: Learnings extracted from sessions
- **Compression**: Playbook entries compressed to save tokens
- **Expansion**: Can retrieve full detail when needed

```javascript
PlaybookEntry {
  // Existing fields...
  sourceObservations?: string[]    # NEW: Link to raw observations
  compressed: boolean              # NEW: Is content compressed?
  compressionMetadata?: { ... }    # NEW: Compression details
}
```

### Extension 9 (Security)

Privacy controls integrated:
- Auto-redaction of sensitive data
- `<private>` tags honored during capture
- Redaction metadata tracked

```javascript
Observation {
  // Existing fields...
  redactionInfo?: RedactionInfo    # NEW: Privacy metadata
}
```

### MCP Extension

New MCP tools for memory:

```typescript
{
  name: "vbrief_memory_search",
  description: "Search session history semantically",
  inputSchema: { ... }
}

{
  name: "vbrief_load_session",
  description: "Load session with progressive disclosure",
  inputSchema: {
    sessionId: string,
    maxTier: number,
    tokenBudget: number
  }
}

{
  name: "vbrief_expand_memory",
  description: "Expand compressed content to full detail",
  inputSchema: {
    contentRef: string
  }
}

{
  name: "vbrief_compress_playbook",
  description: "Compress ACE playbook entries",
  inputSchema: {
    targetRatio: number,  // 0.1 = 90% compression
    categories?: string[]  // Which categories to compress
  }
}
```

### Extension 10 (Version Control)

Track compression versions:
- Compression method versions
- Recompression when methods improve
- Audit trail of compressions

```javascript
vBRIEFInfo {
  // Existing fields...
  compressionVersion?: string      # e.g., "llm-summarize-v2"
}
```

## Benefits and Tradeoffs

### Benefits

**Automatic Capture:**
- No manual documentation burden
- Knowledge preserved even when agent forgets
- Complete session history

**Intelligent Compression:**
- 70-95% token reduction typical
- Key insights preserved
- Expandable when needed

**Progressive Disclosure:**
- Load only what's needed
- Explicit token costs
- User control over context size

**Cross-Session Continuity:**
- Agents remember previous work
- Learnings accumulate automatically
- Context survives session restarts

**Privacy by Default:**
- Automatic redaction of credentials
- Sensitive data never stored
- GDPR-compliant

### Tradeoffs

**Compression is Lossy:**
- Some detail discarded
- May need expansion later
- Quality depends on compression method

**Computational Cost:**
- LLM calls for compression
- Embedding computation for search
- Storage for multiple tiers

**Not All Sessions Valuable:**
- Simple sessions may not warrant capture
- Storage overhead for trivial work
- Need heuristics to filter

**Expansion Latency:**
- Retrieving full content takes time
- May need to fetch from archive
- Network dependency for remote storage

## When to Use Session Memory

**Strongly recommended:**
- Long-running projects (weeks/months)
- Complex domains with many learnings
- Multi-session development workflows
- Teams with multiple agents/developers
- Compliance requirements (audit trails)

**Optional/experimental:**
- Short exploratory sessions
- One-off tasks
- Prototyping phases

**Not recommended:**
- Single-command executions
- Stateless operations
- Privacy-critical contexts without review

## Migration Path

### Phase 1: Manual Capture

- Users manually trigger session export
- Basic compression (semantic extraction)
- File-based storage

### Phase 2: Automatic Capture

- Sessions auto-exported on end
- LLM-based compression
- Progressive disclosure (2 tiers)

### Phase 3: Advanced Features

- Real-time capture during session
- Multi-method compression
- 5-tier progressive disclosure
- Memory search with embeddings

### Phase 4: Intelligence

- Predictive loading (anticipate needs)
- Automatic aggregation across sessions
- Anomaly detection (unusual patterns)
- Compression quality learning

## Open Questions

1. **Compression Triggers**: When to compress? Immediately or batch later?

2. **Expansion Policy**: Should full content expire after N days?

3. **Search Indexing**: Embeddings for semantic search? What model?

4. **Session Boundaries**: How to detect session end automatically?

5. **Multi-Agent Sessions**: How to handle concurrent agents in same session?

6. **Storage Backend**: Files, database, cloud? Hybrid?

7. **Compression Retraining**: As compression improves, recompress old content?

## Community Feedback

We're seeking feedback on:

1. **Compression Ratios**: What's acceptable? 90% reduction too aggressive?
2. **Tier Structure**: 5 tiers too many? Should be simpler?
3. **Privacy Filters**: Which patterns to auto-redact?
4. **Token Budgets**: How should agents decide budget allocation?
5. **Integration**: Should this be part of Extension 12 (ACE) or separate?
6. **Tooling**: What tools most needed (viewer, search, compression UI)?

Please provide feedback via:
- GitHub issues: https://github.com/visionik/vBRIEF/issues
- GitHub discussions: https://github.com/visionik/vBRIEF/discussions
- Email: visionik@pobox.com

## References

### Primary Inspiration
- **claude-mem**: https://github.com/thedotmack/claude-mem
  - Automatic session capture
  - AI-powered compression
  - Progressive disclosure pattern
  - Privacy controls

### vBRIEF Extensions
- **Extension 12 (ACE)**: README.md#extension-12-ace
- **Extension 9 (Security)**: vBRIEF-extension-security.md
- **Extension 10 (Version Control)**: README.md#extension-10-version-control
- **MCP Extension**: vBRIEF-extension-MCP.md

### Compression & Memory
- **Compression in LLMs**: Token efficiency for long-context applications
- **Progressive Summarization**: Tiago Forte's progressive summarization method
- **RAG**: Retrieval-Augmented Generation for context management

## Acknowledgments

This extension is directly inspired by [claude-mem](https://github.com/thedotmack/claude-mem) by @thedotmack. claude-mem pioneered the concepts of automatic capture, AI compression, and progressive disclosure for LLM agents. We bring these patterns to vBRIEF to make them available across all agentic systems, not just Claude Code.

The progressive disclosure pattern elegantly solves the token cost problem that plagues long-term memory systems. By showing costs upfront and loading incrementally, users maintain control while agents access rich historical context.

## Appendix: Compression Examples

### Example 1: File Edit Observation

**Original (450 tokens):**
```
Tool: edit_files
File: src/auth/oauth.ts
Changes:
- Added import crypto from 'crypto'
- Added function generateCodeVerifier(): 
    const buffer = crypto.randomBytes(32)
    return base64URLEncode(buffer.toString('base64'))
- Added function generateCodeChallenge(verifier):
    const hash = crypto.createHash('sha256').update(verifier).digest('base64')
    return base64URLEncode(hash)
- Added helper base64URLEncode(str):
    return str.replace(/\+/g, '-').replace(/\//g, '_').replace(/=/g, '')
- Updated initiateOAuth to call generateCodeVerifier/Challenge
Reasoning: Implementing PKCE (Proof Key for Code Exchange) for OAuth2 
to prevent authorization code interception attacks. PKCE requires a 
code_verifier (random string) and code_challenge (SHA256 hash of verifier).
The base64URL encoding is required per RFC 7636.
Result: Successfully added PKCE support. All existing tests still pass.
```

**Compressed (68 tokens):**
```
Implemented PKCE for OAuth2 in auth/oauth.ts: added generateCodeVerifier() 
using crypto.randomBytes(32) and generateCodeChallenge() using SHA256. 
Base64URL encoding applied per RFC 7636. Tests pass.
```

**Compression ratio: 0.15 (85% reduction)**

### Example 2: Test Execution Observation

**Original (280 tokens):**
```
Tool: run_shell_command
Command: npm test -- auth.test.ts
Output:
 PASS  src/auth/auth.test.ts
  OAuth PKCE
    ✓ generates valid code verifier (3 ms)
    ✓ generates valid code challenge (2 ms)
    ✓ code challenge matches verifier (5 ms)
    ✓ initiateOAuth includes PKCE params (12 ms)
    ✓ completeOAuth validates code_challenge (8 ms)

Test Suites: 1 passed, 1 total
Tests:       5 passed, 5 total
Time:        1.234 s

Reasoning: Validating PKCE implementation with comprehensive tests.
Result: All tests pass, PKCE implementation verified correct.
```

**Compressed (45 tokens):**
```
Ran OAuth PKCE tests: 5/5 passed. Verified code_verifier generation, 
code_challenge computation, and parameter inclusion in OAuth flow.
```

**Compression ratio: 0.16 (84% reduction)**

### Example 3: Error Investigation

**Original (620 tokens):**
```
Tool: read_files
Files: logs/error.log, src/auth/oauth.ts, src/auth/callback.ts
Error log shows: "invalid_grant: code_verifier does not match code_challenge"
Investigated callback.ts: found bug in state parameter handling - was using
a different code_verifier than what was sent in authorization request.
Root cause: code_verifier stored in session but session ID changed between
authorize and callback due to domain mismatch (www.example.com vs example.com).
Solution: Store code_verifier in secure httpOnly cookie instead of session,
or ensure consistent domain for session cookie.
Changed: callback.ts now retrieves code_verifier from cookie, not session.
Tested: OAuth flow now completes successfully.
Learning: PKCE requires careful state management across redirect boundaries.
```

**Compressed (92 tokens):**
```
Fixed OAuth error: code_verifier mismatch caused by session ID change between
authorize/callback (domain mismatch: www vs non-www). Solution: store 
code_verifier in httpOnly cookie instead of session. Learning: PKCE state 
must survive redirects.
```

**Compression ratio: 0.15 (85% reduction)**

These examples demonstrate typical 80-85% compression while preserving essential information: what was done, why, what was learned, and outcome.
