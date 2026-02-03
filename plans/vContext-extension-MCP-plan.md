# Plan: vBRIEF MCP (Model Context Protocol) Extension

**Status**: Draft  
**Author**: Jonathan Taylor (visionik@pobox.com)  
**Created**: 2025-12-27  
**Purpose**: Plan the structure and content for vBRIEF-extension-MCP.md

## Overview

Create a vBRIEF extension proposal for Model Context Protocol (MCP) integration. MCP is Anthropic's open protocol that enables AI models to securely connect to external data sources and tools. This extension would define how vBRIEF documents are exposed as MCP resources and how vBRIEF operations are exposed as MCP tools.

## Context

**What is MCP?**
- Open protocol by Anthropic for connecting LLMs to external systems
- Provides standardized way to expose resources (data) and tools (operations)
- Supported by Claude, and increasingly by other AI systems
- Enables secure, consistent data access across different AI applications

**Why vBRIEF needs MCP integration:**
- Makes vBRIEF documents natively accessible to Claude and other LLM-based agents
- Standardizes how tools read/write vBRIEF (vs custom implementations)
- Enables discovery - agents can find vBRIEF servers automatically
- Provides security/permission model for multi-user scenarios

**Relationship to existing extensions:**
- **Claude extension** mentioned MCP but didn't define the protocol details
- **Beads extension** uses file-based sync; MCP could provide real-time access
- This extension defines the MCP protocol layer that other extensions can build on

## Document Structure (following Beads/Claude pattern)

### 1. Front Matter
- Very early draft notice
- Extension name: MCP Integration
- Version: 0.1 (Draft)
- Author: Jonathan Taylor
- Date

### 2. Overview
- Brief explanation of MCP (with link to spec)
- How MCP enables AI agents to access vBRIEF
- Integration goal: Make vBRIEF a first-class MCP resource type

### 3. Motivation
**MCP strengths:**
- Standardized protocol for AI-to-data connections
- Server discovery and capability negotiation
- Security/authentication built-in
- Transport agnostic (stdio, SSE, HTTP)

**vBRIEF benefits from MCP:**
- AI agents can discover and use vBRIEF without custom code
- Standardized CRUD operations on todos/plans/playbooks
- Real-time updates (vs polling files)
- Multi-user coordination with permissions

### 4. Dependencies
**Required:**
- Extension 2 (Identifiers) - for referencing specific items
- Core vBRIEF types

**Recommended:**
- Extension 10 (Version Control) - change tracking
- Extension 11 (Forking) - for conflict resolution

### 5. MCP Resources (How vBRIEF is exposed)

Define vBRIEF as MCP resources:

```typescript
// Resources expose vBRIEF documents
resources: [
  {
    uri: "vbrief://todos/current",
    name: "Current Tasks",
    mimeType: "text/x-tron"
  },
  {
    uri: "vbrief://plans/{id}",
    name: "Plan by ID",
    mimeType: "text/x-tron"
  },
  {
    uri: "vbrief://playbook",
    name: "Project Playbook",
    mimeType: "text/x-tron"
  }
]
```

### 6. MCP Tools (How vBRIEF is modified)

Define vBRIEF operations as MCP tools:

```typescript
tools: [
  {
    name: "vbrief_create_todo",
    description: "Create a new todo item",
    inputSchema: { /* JSON schema */ }
  },
  {
    name: "vbrief_update_todo",
    description: "Update todo status/content",
    inputSchema: { /* JSON schema */ }
  },
  {
    name: "vbrief_create_plan",
    description: "Create a new plan document",
    inputSchema: { /* JSON schema */ }
  },
  {
    name: "vbrief_add_learning",
    description: "Add learning to playbook",
    inputSchema: { /* JSON schema */ }
  }
]
```

### 7. MCP Prompts (Optional)

Predefined prompt templates for common vBRIEF workflows:

```typescript
prompts: [
  {
    name: "vbrief_session_start",
    description: "Load vBRIEF context at session start",
    arguments: []
  },
  {
    name: "vbrief_session_end",
    description: "Save vBRIEF state at session end",
    arguments: []
  }
]
```

### 8. Usage Patterns

#### Pattern 1: MCP Server Discovery
Show how AI agents discover and connect to vBRIEF MCP server

#### Pattern 2: Reading vBRIEF via Resources
Examples of agents reading current todos, plans, playbooks

#### Pattern 3: Modifying vBRIEF via Tools
Examples of agents creating/updating items through MCP tools

#### Pattern 4: Real-Time Collaboration
Multiple agents/users working on shared vBRIEF through MCP

#### Pattern 5: Integration with Claude Desktop
Specific example of Claude Desktop app using vBRIEF MCP server

### 9. Implementation Notes

#### Server Implementation
- Reference implementation in TypeScript (using @modelcontextprotocol/sdk)
- File-based backend (reads/writes .tron files)
- Optional database backend (SQLite, PostgreSQL)
- Authentication/authorization considerations

#### Client Usage
- How AI agents connect to vBRIEF MCP server
- Configuration examples for different tools
- Error handling and fallbacks

#### Transport Options
- stdio (for local processes)
- SSE (for web-based tools)
- HTTP (for remote access)

### 10. Security Considerations

- Authentication mechanisms
- Permission model (who can read/write what)
- Multi-user scenarios
- Audit logging

### 11. Schema Definitions

Full JSON schemas for:
- Tool input schemas
- Resource response formats
- Error responses

### 12. Relationship to Existing Extensions

- **Claude extension**: This provides the MCP layer Claude extension referenced
- **Beads extension**: Could use MCP instead of file-based sync
- **Extension 10 (Version Control)**: MCP operations generate change events

### 13. Open Questions

1. Should MCP server support both TRON and JSON, or TRON only?
2. How to handle large playbooks that exceed MCP message size limits?
3. Should vBRIEF MCP server be mandatory or optional?
4. How to handle offline scenarios (MCP requires server connection)?

### 14. Examples

Detailed code examples:
- Complete MCP server implementation
- Client connection code
- Tool invocation examples
- Resource fetching examples

### 15. Migration Path

Phase 1: Basic server
- Implement resources for reading todos/plans
- Basic CRUD tools
- stdio transport only

Phase 2: Advanced features
- Real-time updates via SSE
- Multi-user support
- Authentication

Phase 3: Ecosystem integration
- Pre-built servers for popular stacks
- Claude Desktop integration
- Aider/Cursor plugins

### 16. Community Feedback Section

Questions for community:
- What MCP transports are most important?
- Should server handle multiple vBRIEF projects?
- What permission model makes sense?

### 17. References

- MCP specification: https://modelcontextprotocol.io
- MCP SDK: https://github.com/modelcontextprotocol/sdk
- vBRIEF spec
- Claude extension (references MCP)

## Key Differentiators from Claude Extension

The Claude extension showed a brief MCP example but didn't:
- Define the full protocol (resources, tools, prompts)
- Provide complete schemas
- Cover server implementation details
- Address security/multi-user
- Show non-Claude MCP clients

This extension should be **comprehensive and protocol-focused**, serving as the reference for anyone implementing vBRIEF MCP support.

## Technical Decisions Needed

### 1. Resource URI Scheme
Option A: `vbrief://todos/current`, `vbrief://plans/{id}`
Option B: `file:///path/to/vBRIEF/current.tron`
Option C: Both supported

**Recommendation**: Option A (custom scheme) for abstraction, with server handling file mapping internally.

### 2. Format Negotiation
How does client request TRON vs JSON?

**Recommendation**: Use standard HTTP content negotiation:
- `text/x-tron` for TRON
- `application/json` for JSON
- Default to TRON

### 3. Change Notifications
Should server push changes to clients?

**Recommendation**: Yes, via MCP's notification mechanism. Clients subscribe to resources they care about.

### 4. Conflict Resolution
What happens when two clients modify same todo?

**Recommendation**: 
- Use Extension 10 (Version Control) sequence numbers
- Optimistic locking with retry
- Document conflict resolution strategies

## Success Criteria

The extension document should enable:
1. Developer can implement vBRIEF MCP server from spec
2. AI agent can discover and use vBRIEF MCP server
3. Multiple clients can coordinate through vBRIEF MCP
4. Clear migration path from file-based to MCP-based access

## Next Steps

1. Research MCP protocol details (if needed)
2. Draft the extension document following this plan
3. Create example MCP server implementation
4. Test with Claude Desktop
5. Gather community feedback

## Notes

- Keep consistent with Beads/Claude extension style
- Include lots of code examples (both server and client)
- Make it practical - developers should be able to implement from this spec
- Consider that MCP is still evolving - note which MCP version we're targeting
