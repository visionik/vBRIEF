# vBRIEF Extension Proposal: Claude AI Integration

> **VERY EARLY DRAFT**: This is an initial proposal and subject to significant change. Comments, feedback, and suggestions are strongly encouraged. Please provide input via GitHub issues or discussions.

**Extension Name**: Claude Integration  
**Version**: 0.1 (Draft)  
**Status**: Proposal  
**Author**: Jonathan Taylor (visionik@pobox.com)  
**Date**: 2025-12-27

## Overview

[Claude](https://claude.ai) is Anthropic's family of large language models with strong reasoning capabilities, long context windows (up to 200K tokens), and specialized features for coding assistance. Claude is widely used in agentic coding systems like Aider, Claude Code, Cursor, and Windsurf.

This extension enables Claude to natively read, write, and reason about vBRIEF documents as part of its coding workflow. It provides Claude with structured memory formats optimized for its context window, reasoning patterns, and tool use capabilities.

## Motivation

**Claude's strengths for agentic coding**:
- Long context windows (200K tokens) for holding entire project state
- Strong reasoning about dependencies and task ordering
- Tool use capabilities via function calling
- Artifacts for iterative refinement
- Conversation continuity across sessions

**vBRIEF benefits for Claude**:
- **Token efficiency**: TRON format reduces context consumption by 35-40%
- **Structured memory**: TodoLists, Plans, and playbooks provide clear memory hierarchy
- **Cross-session continuity**: vBRIEF documents persist Claude's reasoning across conversations
- **Multi-agent coordination**: When multiple Claude instances work together, vBRIEF provides shared state
- **Knowledge accumulation**: Playbooks let Claude build institutional knowledge over time

**Integration goal**: Make vBRIEF Claude's native memory format, enabling seamless persistence and retrieval of work state, plans, and accumulated learnings.

## Dependencies

**Required**:
- Extension 2 (Identifiers) - for tracking items across Claude sessions
- Extension 10 (Version Control & Sync) - for Claude's change tracking

**Recommended**:
- Extension 1 (Timestamps) - session tracking
- Extension 4 (Hierarchical) - task dependencies
- Extension 12 (Playbooks) - learning accumulation

## New Fields

### TodoItem Extensions
```javascript
TodoItem {
  // Prior extensions...,
  claudeContext?: ClaudeContext     # Claude-specific execution context
  claudeArtifact?: string           # Link to Claude artifact if task generated one
  claudePrompt?: string             # Prompt template for working on this task
}
```

### Plan Extensions
```javascript
Plan {
  // Prior extensions...,
  claudeConversation?: string       # Conversation ID where plan was created
  claudeThinking?: Narrative        # Claude's reasoning about the plan
  claudePromptTemplate?: string     # Template for agents working on this plan
}
```

### New Types

```javascript
ClaudeContext {
  conversationId?: string           # Claude conversation where work happened
  artifactId?: string               # Claude artifact ID if applicable
  modelVersion?: string             # Claude model used (e.g., "claude-3.5-sonnet")
  tokensUsed?: number               # Approximate tokens consumed for this task
  thinkingSteps?: string[]          # Key reasoning steps Claude took
  codebaseContext?: string[]        # Files Claude had in context
}

ClaudePromptTemplate {
  systemPrompt?: string             # System instructions for this work
  contextFiles?: string[]           # Files to include in context
  toolsEnabled?: string[]           # Which tools Claude should use
  thinkingStyle?: enum              # "thorough" | "quick" | "creative" | "analytical"
}
```

## Usage Patterns

### Pattern 1: Session Continuity

**Problem**: Claude conversations reset context. Work state is lost between sessions.

**Solution**: Export to vBRIEF at end of session, import at start of next session.

**End of session**:
```markdown
# Claude's final message in conversation
I've completed the authentication implementation. Let me create a vBRIEF document 
to preserve this work state:

<create_file>
vBRIEF/session-2025-12-27-auth.tron

class vBRIEFInfo: version, author
class TodoList: items
class TodoItem: id, title, status, claudeContext
class ClaudeContext: conversationId, modelVersion, tokensUsed

vBRIEFInfo: vBRIEFInfo("0.4", "claude-3.5-sonnet")
todoList: TodoList([
  TodoItem(
    "1", 
    "JWT token generation", 
    "completed",
    ClaudeContext("conv-abc123", "claude-3.5-sonnet-20241022", 2800)
  ),
  TodoItem(
    "2",
    "Token refresh endpoint",
    "inProgress", 
    ClaudeContext("conv-abc123", "claude-3.5-sonnet-20241022", 1500)
  ),
  TodoItem(
    "3",
    "Add token expiry tests",
    "pending",
    null
  )
])
</create_file>

To continue this work in a new session, share this vBRIEF file and I'll pick up where I left off.
```

**Start of next session**:
```markdown
# User shares vBRIEF file
I'd like to continue the auth work. Here's the vBRIEF state: [attaches file]

# Claude responds
I can see we completed JWT token generation and are partway through the refresh endpoint.
The pending task is to add token expiry tests. I'll continue with the refresh endpoint first
since it's partially complete. Let me check the current implementation...
```

### Pattern 2: Plan-Driven Development

**Problem**: Complex features need upfront design and coordination across multiple sessions.

**Solution**: Create vBRIEF Plan with Claude's reasoning, use it to guide implementation.

**Planning conversation**:
```markdown
# User
I need to add OAuth2 support. Help me create a plan.

# Claude creates vBRIEF Plan
I'll create a structured plan in vBRIEF format:

class vBRIEFInfo: version
class Plan: title, status, narratives, phases, claudeThinking
class PlanItem: title, status

vBRIEFInfo: vBRIEFInfo("0.4")
plan: Plan(
  "Add OAuth2 Support",
  "draft",
  {
    "proposal": "Add OAuth2 alongside existing JWT, maintain backward compatibility",
    "problem": "Users want Google/GitHub login. Current JWT-only limits adoption.",
    "claudeThinking": "Key decision: Keep JWT for API tokens, use OAuth for user login. This avoids breaking existing API clients while adding user-friendly login options."
  },
  [
    PlanItem("OAuth provider integration", "pending"),
    PlanItem("User model updates", "pending"),
    PlanItem("Login flow UI", "pending"),
    PlanItem("Migration & testing", "pending")
  ]
)
```

### Pattern 3: Multi-Session Learning (Playbooks)

**Problem**: Claude forgets strategies and learnings between projects.

**Solution**: Accumulate Claude's insights into playbooks, reference them in future work.

**End of project**:
```markdown
# Claude reflects on completed work
Let me document what I learned for future projects:

class vBRIEFInfo: version
class Plan: title, status, playbook
class Playbook: version, strategies, learnings
class Strategy: id, title, description, confidence
class Learning: id, content, confidence, discoveredBy
class Agent: id, type, name, model

vBRIEFInfo: vBRIEFInfo("0.4")
plan: Plan(
  "OAuth Implementation Retrospective",
  "completed",
  Playbook(
    1,
    [
      Strategy(
        "strat-oauth-1",
        "Test OAuth flow with mock provider first",
        "Avoids rate limits and API key issues during development. Use a test OAuth 
         provider or mock server before integrating real providers.",
        0.95
      ),
      Strategy(
        "strat-oauth-2", 
        "Store OAuth tokens in separate table",
        "Don't mix OAuth tokens with JWT tokens in schema. Separate tables make it
         easier to implement different refresh/expiry logic.",
        0.85
      )
    ],
    [
      Learning(
        "learn-oauth-1",
        "PKCE is now required for mobile OAuth flows",
        0.9,
        Agent("claude-1", "aiAgent", "Claude", "claude-3.5-sonnet-20241022")
      )
    ]
  )
)
```

**In future project**:
```markdown
# User
I need to add GitHub OAuth to my app.

# Claude references prior playbook
I see we've implemented OAuth before. Let me reference our learnings...
[reads prior playbook]

Based on our previous OAuth work, I recommend:
1. Test with a mock OAuth provider first (strategy strat-oauth-1)
2. Use separate table for OAuth tokens (strategy strat-oauth-2)
3. Implement PKCE for mobile support (learning learn-oauth-1)

Shall I create a plan following these strategies?
```

### Pattern 4: Claude Projects Integration

**Problem**: Claude Projects provide project-specific context, but no structured task memory.

**Solution**: Each Claude Project has an associated vBRIEF document for work tracking.

**Project setup**:
```markdown
# In Claude Project's custom instructions or knowledge
This project uses vBRIEF for structured memory. The project's work state is in:
- vBRIEF/current.tron - Active todos and current work
- vBRIEF/plans/*.tron - Design documents and plans
- vBRIEF/playbook.tron - Accumulated strategies and learnings

When starting work:
1. Read vBRIEF/current.tron to see active tasks
2. Check relevant plans for context
3. Reference playbook for applicable strategies

When ending work:
1. Update vBRIEF/current.tron with progress
2. Document any new learnings in playbook
```

## Implementation Notes

### For Claude (via System Prompts)

```markdown
# Add to Claude's system prompt or project instructions

You have access to vBRIEF documents for structured memory:

**Reading vBRIEF**:
- TodoLists show current work and priorities
- Plans provide design context and reasoning
- Playbooks contain accumulated strategies/learnings

**Writing vBRIEF**:
- Use TRON format (more efficient than JSON)
- Include claudeContext for session continuity
- Document your reasoning in plan narratives
- Extract learnings into playbooks at project milestones

**Format**:
vBRIEF uses TRON (superset of JSON). Example:
```tron
class vBRIEFInfo: version
class TodoList: items
class TodoItem: id, title, status

vBRIEFInfo: vBRIEFInfo("0.4")
todoList: TodoList([
  TodoItem("1", "Fix bug", "completed"),
  TodoItem("2", "Add tests", "pending")
])
```

Prefer TRON over JSON for ~35% token savings.
```

### For Claude-Based Tools (Aider, Cursor, etc.)

**Aider integration**:
```python
# In .aider.conf.yml
vbrief:
  enabled: true
  todo_file: vBRIEF/current.tron
  plans_dir: vBRIEF/plans/
  playbook_file: vBRIEF/playbook.tron
  
# Aider can read these at session start, update at session end
```

**Cursor integration**:
```json
// In .cursor/settings.json
{
  "vbrief.enabled": true,
  "vbrief.autoRead": true,
  "vbrief.autoWrite": true,
  "vbrief.location": "vBRIEF/"
}
```

### For Model Context Protocol (MCP) Servers

```typescript
// MCP server exposing vBRIEF to Claude
import { Server } from "@modelcontextprotocol/sdk/server/index.js";

const server = new Server({
  name: "vbrief-server",
  version: "0.1.0"
}, {
  capabilities: {
    resources: {},
    tools: {}
  }
});

// Resource: current todos
server.setRequestHandler(ListResourcesRequestSchema, async () => ({
  resources: [{
    uri: "vbrief://todos/current",
    name: "Current Tasks",
    description: "Active todo list from vBRIEF",
    mimeType: "text/x-tron"
  }]
}));

// Tool: create todo item
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  if (request.params.name === "vbrief_create_todo") {
    // Parse vBRIEF file, add item, write back
    // Return success message
  }
});
```

## Token Efficiency Analysis

**Why TRON matters for Claude's 200K context**:

Even with Claude's massive context window, token efficiency matters:
- More project files fit in context
- Faster processing (fewer tokens to read)
- Lower API costs
- More headroom for reasoning

**Example**: Tracking 50 tasks in different formats:

**Markdown** (~3,500 tokens):
```markdown
## Current Tasks
- [ ] Implement JWT auth (Status: in-progress, ID: 1, Depends on: none)
- [ ] Add auth tests (Status: pending, ID: 2, Depends on: 1)
- [ ] Setup database (Status: completed, ID: 3, Depends on: none)
[...47 more items...]
```

**JSON** (~2,800 tokens):
```json
{
  "version": "0.4",
  "items": [
    {"id": "1", "title": "Implement JWT auth", "status": "in-progress", "dependencies": []},
    {"id": "2", "title": "Add auth tests", "status": "pending", "dependencies": ["1"]},
    [...48 more items...]
  ]
}
```

**TRON** (~1,700 tokens, 39% reduction):
```tron
class vBRIEFInfo: version
class TodoList: items
class TodoItem: id, title, status, dependencies

vBRIEFInfo: vBRIEFInfo("0.4")
todoList: TodoList([
  TodoItem("1", "Implement JWT auth", "inProgress", []),
  TodoItem("2", "Add auth tests", "pending", ["1"]),
  [...48 more items...]
])
```

**Savings**: ~1,100 tokens = room for 3-4 additional source files in context.

## Relationship to Existing Extensions

**Extension 10 (Version Control & Sync)**:
- Tracks when Claude makes changes to plans/todos
- `claudeContext.conversationId` links changes to specific Claude sessions
- Enables "what did Claude change in this session?" queries

**Extension 12 (Playbooks)**:
- Claude's reflections populate playbooks
- `discoveredBy.model` tracks which Claude version learned each strategy
- Playbooks accumulate across multiple Claude conversations/projects

**Beads Interop Extension**:
- Beads provides execution tracking, Claude provides reasoning/planning
- Claude can read Beads state, add context via vBRIEF Plans
- Claude's learnings feed back into future Beads sessions

## Open Questions

1. **Should Claude auto-generate vBRIEF docs?**
   - Pro: Seamless memory without user intervention
   - Con: User may not want every session persisted
   - **Proposal**: Opt-in via project instructions or explicit user request

2. **How to handle multiple Claude instances working concurrently?**
   - Use Extension 11 (Forking) for parallel work
   - Each Claude instance gets a fork, merge conflicts resolved by human or lead agent
   - **Proposal**: Document multi-Claude workflows in best practices

3. **Should vBRIEF replace Claude Projects' built-in memory?**
   - No - Claude Projects are Anthropic's feature
   - **Proposal**: vBRIEF complements Projects by adding structured task memory

4. **Token budget for vBRIEF in Claude's context?**
   - Recommendation: ~5-10% of context window for vBRIEF
   - For 200K context: 10-20K tokens for vBRIEF state
   - **Proposal**: Document token budgeting guidelines

## Examples

See Usage Patterns section for detailed examples.

## Migration Path

**Phase 1**: Manual vBRIEF usage
- Users create vBRIEF documents by hand
- Claude reads them for context, suggests updates
- No tool integration yet

**Phase 2**: Tool-assisted (current focus)
- Aider, Cursor, other tools auto-read/write vBRIEF
- Claude's responses include vBRIEF updates
- System prompts guide Claude's vBRIEF usage

**Phase 3**: Native integration
- MCP servers expose vBRIEF as resources/tools
- Claude can directly create/update vBRIEF via tool calls
- Anthropic potentially adds vBRIEF awareness to Claude

**Phase 4**: Multi-agent orchestration
- Multiple Claude instances coordinate via shared vBRIEF
- Automatic conflict resolution
- Distributed playbook learning

## Community Feedback

This is a **draft proposal**. Feedback needed:

1. Should Claude auto-detect vBRIEF files in project context?
2. What should default token budget be for vBRIEF in Claude's context?
3. How should Claude handle vBRIEF format errors (invalid TRON)?
4. Should this extension define Claude-specific prompt templates?

**Discuss**: https://github.com/visionik/vBRIEF/discussions

## References

- vBRIEF Specification: https://github.com/visionik/vBRIEF
- Claude: https://claude.ai
- Anthropic Model Context Protocol: https://modelcontextprotocol.io
- Aider: https://github.com/paul-gauthier/aider
- Cursor: https://cursor.sh
- Claude Projects: https://www.anthropic.com/news/projects
