# vBRIEF Extension Proposal: Model Context Protocol (MCP) Integration

> **VERY EARLY DRAFT**: This is an initial proposal and subject to significant change. Comments, feedback, and suggestions are strongly encouraged. Please provide input via GitHub issues or discussions.

**Extension Name**: MCP Integration  
**Version**: 0.1 (Draft)  
**Status**: Proposal  
**Author**: Jonathan Taylor (visionik@pobox.com)  
**Date**: 2025-12-27

## Overview

[Model Context Protocol (MCP)](https://modelcontextprotocol.io) is an open protocol created by Anthropic that enables AI models to securely connect to external data sources and tools. MCP provides a standardized way for LLMs to access resources (data) and invoke tools (operations) across different systems and applications.

This extension defines how vBRIEF documents are exposed as MCP resources and how vBRIEF operations are exposed as MCP tools. It makes vBRIEF a first-class MCP resource type, enabling AI agents to discover, read, and modify vBRIEF documents through a standardized protocol.

## Motivation

**MCP strengths**:
- Standardized protocol for AI-to-data connections
- Server discovery and capability negotiation
- Built-in security and authentication
- Transport agnostic (stdio, SSE, HTTP)
- Growing ecosystem support (Claude, Cursor, Aider, etc.)

**vBRIEF benefits from MCP**:
- **Discoverability**: AI agents can find and use vBRIEF without custom code
- **Standardization**: CRUD operations on todos/plans follow consistent patterns
- **Real-time access**: Agents get live updates instead of polling files
- **Multi-user coordination**: Multiple agents/humans work on shared vBRIEF with permissions
- **Ecosystem integration**: Works automatically with MCP-enabled tools

**Integration goal**: Make vBRIEF the standard memory format for MCP-enabled agentic systems, providing structured persistence for todos, plans, and accumulated learnings.

## Dependencies

**Required**:
- Extension 2 (Identifiers) - for referencing specific items via MCP tools
- Core vBRIEF types (TodoList, TodoItem, Plan, PlanItem)

**Recommended**:
- Extension 1 (Timestamps) - track when MCP operations occurred
- Extension 10 (Version Control) - change tracking and conflict resolution
- Extension 11 (Multi-Agent Forking) - concurrent modification handling
- Extension 12 (Playbooks) - long-term memory access via MCP

## MCP Resources

Resources are read-only endpoints that expose vBRIEF documents. Clients use MCP's `resources/read` to fetch these.

### Resource URIs

```typescript
// Standard vBRIEF resources
vbrief://todos/current              # Current TodoList
vbrief://todos/{id}                 # Specific TodoList by ID
vbrief://plans/current              # Current Plan
vbrief://plans/{id}                 # Specific Plan by ID
vbrief://playbook                   # Project playbook
vbrief://playbook/{category}        # Playbook section (strategies, decisions, etc.)

// Collection resources
vbrief://todos                      # List all TodoLists
vbrief://plans                      # List all Plans
```

### Resource Schema

```typescript
interface VAgendaResource {
  uri: string                        # Resource URI
  name: string                       # Human-readable name
  description?: string               # Optional description
  mimeType: string                   # "text/x-tron" or "application/json"
}
```

### Example Resource Declaration

```typescript
// MCP server capability declaration
{
  "capabilities": {
    "resources": {
      "supported": true
    }
  },
  "resources": [
    {
      "uri": "vbrief://todos/current",
      "name": "Current Tasks",
      "description": "Active TodoList for this project",
      "mimeType": "text/x-tron"
    },
    {
      "uri": "vbrief://plans/current",
      "name": "Current Plan",
      "description": "Active implementation plan",
      "mimeType": "text/x-tron"
    },
    {
      "uri": "vbrief://playbook",
      "name": "Project Playbook",
      "description": "Accumulated learnings (playbook)",
      "mimeType": "text/x-tron"
    }
  ]
}
```

### Reading Resources

Client requests resource content:

```json
// Request
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "resources/read",
  "params": {
    "uri": "vbrief://todos/current"
  }
}

// Response
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "contents": [
      {
        "uri": "vbrief://todos/current",
        "mimeType": "text/x-tron",
        "text": "class vBRIEFInfo: version\nclass TodoList: items\n..."
      }
    ]
  }
}
```

## MCP Tools

Tools are operations that modify vBRIEF state. Clients use MCP's `tools/call` to invoke them.

### Core Tools

```typescript
// Create a new TodoItem
vbrief_create_todo({
  title: string,
  description?: string,
  status?: TodoStatus,
  todoListId?: string              # Target list, defaults to current
})

// Update a TodoItem
vbrief_update_todo({
  id: string,
  title?: string,
  description?: string,
  status?: TodoStatus,
  assignee?: string
})

// Delete a TodoItem
vbrief_delete_todo({
  id: string
})

// Create a new Plan
vbrief_create_plan({
  title: string,
  status?: PlanStatus,
  narratives?: Record<string, string>,
  items?: PlanItem[]
})

// Update a Plan
vbrief_update_plan({
  id: string,
  title?: string,
  status?: PlanStatus,
  narratives?: Record<string, string>
})

// Add a PlanItem to a Plan
vbrief_add_plan_item({
  planId: string,
  item: PlanItem,
  position?: number                # Insert at position, defaults to end
})

// Update a PlanItem
vbrief_update_plan_item({
  planId: string,
  itemId: string,
  title?: string,
  status?: PlanItemStatus
})

// Add learning to playbook (append-only)
vbrief_add_learning({
  targetId: string,
  kind: "strategy" | "learning" | "rule" | "warning" | "note",
  title?: string,
  narrative: Record<string, string>,
  tags?: string[],
  evidence?: string[],
  confidence?: number
})

// Query playbook learnings
vbrief_query_playbook({
  kind?: "strategy" | "learning" | "rule" | "warning" | "note",
  tags?: string[],
  searchText?: string,
  limit?: number
})
```

### Tool Input Schemas

Full JSON schema example for `vbrief_create_todo`:

```json
{
  "name": "vbrief_create_todo",
  "description": "Create a new todo item in vBRIEF",
  "inputSchema": {
    "type": "object",
    "properties": {
      "title": {
        "type": "string",
        "description": "Title of the todo item"
      },
      "description": {
        "type": "string",
        "description": "Detailed description of the task"
      },
      "status": {
        "type": "string",
        "enum": ["pending", "inProgress", "completed", "blocked", "cancelled"],
        "description": "Current status",
        "default": "pending"
      },
      "todoListId": {
        "type": "string",
        "description": "ID of target TodoList, defaults to current"
      }
    },
    "required": ["title"]
  }
}
```

### Tool Response Format

```json
// Success response
{
  "jsonrpc": "2.0",
  "id": 2,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "Created todo item with ID: todo-abc123"
      }
    ],
    "isError": false
  }
}

// Error response
{
  "jsonrpc": "2.0",
  "id": 2,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "Error: TodoList not found: list-xyz789"
      }
    ],
    "isError": true
  }
}
```

## MCP Prompts

Prompts are pre-defined templates for common vBRIEF workflows. They help AI agents use vBRIEF effectively.

```typescript
// Prompt declarations
{
  "prompts": [
    {
      "name": "vbrief_session_start",
      "description": "Load vBRIEF context at the start of a coding session",
      "arguments": []
    },
    {
      "name": "vbrief_session_end",
      "description": "Save current work state to vBRIEF at session end",
      "arguments": [
        {
          "name": "summary",
          "description": "Brief summary of work completed",
          "required": true
        }
      ]
    },
    {
      "name": "vbrief_plan_review",
      "description": "Review current plan and suggest next steps",
      "arguments": []
    },
    {
      "name": "vbrief_add_learning",
      "description": "Extract a learning from recent work and add to playbook",
      "arguments": [
        {
          "name": "category",
          "description": "Learning category: strategies, decisions, patterns, gotchas",
          "required": true
        }
      ]
    }
  ]
}
```

### Example Prompt Content

When `vbrief_session_start` is invoked, the server returns:

```
You are starting a new coding session. Here is the current vBRIEF context:

## Current Tasks (TodoList)
[reads vbrief://todos/current]

## Current Plan (if any)
[reads vbrief://plans/current]

## Recent Learnings
[reads vbrief://playbook with recent items]

Based on this context, what would you like to work on?
```

## Usage Patterns

### Pattern 1: MCP Server Discovery

AI agent discovers vBRIEF MCP server:

```typescript
// Agent connects to MCP server (via stdio, SSE, or HTTP)
const client = new MCPClient({
  transport: new StdioClientTransport({
    command: "vbrief-mcp-server",
    args: ["--project", "/path/to/project"]
  })
});

await client.connect();

// Discover available resources
const resources = await client.listResources();
// Returns: vbrief://todos/current, vbrief://plans/current, etc.

// Discover available tools
const tools = await client.listTools();
// Returns: vbrief_create_todo, vbrief_update_todo, etc.
```

### Pattern 2: Reading vBRIEF via Resources

Claude reads current tasks at session start:

```typescript
// Claude (via MCP client) reads current todos
const response = await client.readResource({
  uri: "vbrief://todos/current"
});

// Response contains TRON document
const tronContent = response.contents[0].text;

// Claude now has full context of current work
// Can reason about priorities, dependencies, etc.
```

### Pattern 3: Modifying vBRIEF via Tools

Claude completes a task and updates vBRIEF:

```typescript
// Claude invokes tool to mark task completed
const result = await client.callTool({
  name: "vbrief_update_todo",
  arguments: {
    id: "todo-abc123",
    status: "completed"
  }
});

// Tool returns success confirmation
// vBRIEF document is updated
// Other connected agents see the change
```

### Pattern 4: Real-Time Collaboration

Multiple agents working on shared vBRIEF:

```typescript
// Agent A updates todo status
await clientA.callTool({
  name: "vbrief_update_todo",
  arguments: { id: "todo-1", status: "inProgress" }
});

// MCP server sends notification to all subscribers
// (via MCP notification mechanism)
{
  "method": "notifications/resources/updated",
  "params": {
    "uri": "vbrief://todos/current"
  }
}

// Agent B receives notification and re-reads resource
const updated = await clientB.readResource({
  uri: "vbrief://todos/current"
});
// Agent B now sees Agent A's changes
```

### Pattern 5: Integration with Claude Desktop

Claude Desktop app configured to use vBRIEF MCP server:

```json
// claude_desktop_config.json
{
  "mcpServers": {
    "vbrief": {
      "command": "vbrief-mcp-server",
      "args": ["--project", "~/Projects/myapp"],
      "env": {
        "VCONTEXT_FORMAT": "tron"
      }
    }
  }
}
```

When Claude Desktop starts, it automatically connects to vBRIEF server and has access to all resources and tools.

## Implementation Notes

### Server Implementation

Reference implementation using TypeScript and `@modelcontextprotocol/sdk`:

```typescript
import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListResourcesRequestSchema,
  ListToolsRequestSchema,
  ReadResourceRequestSchema,
} from "@modelcontextprotocol/sdk/types.js";

class VAgendaMCPServer {
  private server: Server;
  private projectPath: string;
  
  constructor(projectPath: string) {
    this.projectPath = projectPath;
    this.server = new Server(
      {
        name: "vbrief-mcp-server",
        version: "0.1.0",
      },
      {
        capabilities: {
          resources: { supported: true },
          tools: { supported: true },
          prompts: { supported: true },
        },
      }
    );
    
    this.setupHandlers();
  }
  
  private setupHandlers() {
    // List available resources
    this.server.setRequestHandler(
      ListResourcesRequestSchema,
      async () => ({
        resources: [
          {
            uri: "vbrief://todos/current",
            name: "Current Tasks",
            mimeType: "text/x-tron",
          },
          {
            uri: "vbrief://plans/current",
            name: "Current Plan",
            mimeType: "text/x-tron",
          },
          {
            uri: "vbrief://playbook",
            name: "Project Playbook",
            mimeType: "text/x-tron",
          },
        ],
      })
    );
    
    // Read resource content
    this.server.setRequestHandler(
      ReadResourceRequestSchema,
      async (request) => {
        const uri = request.params.uri;
        const content = await this.readVAgendaResource(uri);
        
        return {
          contents: [
            {
              uri,
              mimeType: "text/x-tron",
              text: content,
            },
          ],
        };
      }
    );
    
    // List available tools
    this.server.setRequestHandler(
      ListToolsRequestSchema,
      async () => ({
        tools: [
          {
            name: "vbrief_create_todo",
            description: "Create a new todo item",
            inputSchema: {
              type: "object",
              properties: {
                title: { type: "string" },
                description: { type: "string" },
                status: {
                  type: "string",
                  enum: ["pending", "inProgress", "completed", "blocked", "cancelled"],
                },
              },
              required: ["title"],
            },
          },
          {
            name: "vbrief_update_todo",
            description: "Update a todo item",
            inputSchema: {
              type: "object",
              properties: {
                id: { type: "string" },
                title: { type: "string" },
                status: { type: "string" },
              },
              required: ["id"],
            },
          },
          // Additional tools...
        ],
      })
    );
    
    // Handle tool calls
    this.server.setRequestHandler(
      CallToolRequestSchema,
      async (request) => {
        const { name, arguments: args } = request.params;
        
        switch (name) {
          case "vbrief_create_todo":
            return await this.createTodo(args);
          case "vbrief_update_todo":
            return await this.updateTodo(args);
          default:
            throw new Error(`Unknown tool: ${name}`);
        }
      }
    );
  }
  
  private async readVAgendaResource(uri: string): Promise<string> {
    // Map URI to file path
    const filePath = this.uriToFilePath(uri);
    
    // Read TRON file
    const fs = await import("fs/promises");
    return await fs.readFile(filePath, "utf-8");
  }
  
  private async createTodo(args: any): Promise<any> {
    // Load current TodoList
    const todoList = await this.loadTodoList();
    
    // Create new TodoItem
    const newItem = {
      id: this.generateId(),
      title: args.title,
      description: args.description,
      status: args.status || "pending",
    };
    
    // Add to list
    todoList.items.push(newItem);
    
    // Save back to file
    await this.saveTodoList(todoList);
    
    // Send notification to subscribers
    await this.notifyResourceChanged("vbrief://todos/current");
    
    return {
      content: [
        {
          type: "text",
          text: `Created todo item with ID: ${newItem.id}`,
        },
      ],
      isError: false,
    };
  }
  
  private async updateTodo(args: any): Promise<any> {
    // Similar implementation...
    // Load, modify, save, notify
  }
  
  async run() {
    const transport = new StdioServerTransport();
    await this.server.connect(transport);
  }
}

// Start server
const projectPath = process.argv[2] || process.cwd();
const server = new VAgendaMCPServer(projectPath);
server.run().catch(console.error);
```

### Client Usage

AI agents connect to vBRIEF MCP server:

```typescript
import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StdioClientTransport } from "@modelcontextprotocol/sdk/client/stdio.js";

// Create client
const transport = new StdioClientTransport({
  command: "vbrief-mcp-server",
  args: ["--project", "/path/to/project"],
});

const client = new Client(
  {
    name: "my-ai-agent",
    version: "1.0.0",
  },
  {
    capabilities: {},
  }
);

// Connect
await client.connect(transport);

// Read current todos
const response = await client.request(
  {
    method: "resources/read",
    params: {
      uri: "vbrief://todos/current",
    },
  },
  ReadResourceResultSchema
);

console.log(response.contents[0].text);

// Create a new todo
await client.request(
  {
    method: "tools/call",
    params: {
      name: "vbrief_create_todo",
      arguments: {
        title: "Fix authentication bug",
        status: "pending",
      },
    },
  },
  CallToolResultSchema
);
```

### Backend Storage Options

#### Option 1: File-based (Simplest)

```typescript
class FileBackend {
  constructor(private rootPath: string) {}
  
  async readTodos(): Promise<string> {
    return fs.readFile(
      path.join(this.rootPath, "vBRIEF", "current.tron"),
      "utf-8"
    );
  }
  
  async writeTodos(content: string): Promise<void> {
    await fs.writeFile(
      path.join(this.rootPath, "vBRIEF", "current.tron"),
      content
    );
  }
}
```

#### Option 2: Database-backed (Multi-user)

```typescript
class DatabaseBackend {
  constructor(private db: Database) {}
  
  async readTodos(): Promise<string> {
    const row = await this.db.get(
      "SELECT content FROM vbrief_documents WHERE uri = ?",
      "vbrief://todos/current"
    );
    return row.content;
  }
  
  async writeTodos(content: string): Promise<void> {
    await this.db.run(
      "UPDATE vbrief_documents SET content = ?, updated_at = ? WHERE uri = ?",
      content,
      Date.now(),
      "vbrief://todos/current"
    );
  }
}
```

### Transport Options

#### stdio (Local processes)

Best for: Single-user, local development

```bash
# Start server
vbrief-mcp-server --project ~/Projects/myapp

# Client connects via stdin/stdout
```

#### SSE (Server-Sent Events)

Best for: Web-based tools, real-time updates

```typescript
const transport = new SSEClientTransport(
  new URL("http://localhost:3000/mcp/sse")
);
```

#### HTTP (Remote access)

Best for: Multi-user, distributed systems

```typescript
const transport = new HTTPClientTransport(
  new URL("https://vbrief.example.com/mcp")
);
```

## Security Considerations

### Authentication

MCP doesn't define authentication, but implementations should add it:

```typescript
// Example: API key authentication
class AuthenticatedVAgendaServer extends VAgendaMCPServer {
  constructor(projectPath: string, private apiKey: string) {
    super(projectPath);
  }
  
  protected async authenticate(request: any): Promise<boolean> {
    const providedKey = request.headers?.["x-api-key"];
    return providedKey === this.apiKey;
  }
}
```

### Permission Model

Define who can read/write what:

```typescript
interface VAgendaPermissions {
  user: string;
  canReadTodos: boolean;
  canWriteTodos: boolean;
  canReadPlans: boolean;
  canWritePlans: boolean;
  canReadPlaybook: boolean;
  canWritePlaybook: boolean;
}

class PermissionedVAgendaServer extends VAgendaMCPServer {
  private permissions = new Map<string, VAgendaPermissions>();
  
  protected async checkPermission(
    user: string,
    operation: "read" | "write",
    resourceType: "todos" | "plans" | "playbook"
  ): Promise<boolean> {
    const perms = this.permissions.get(user);
    if (!perms) return false;
    
    const key = `can${operation === "read" ? "Read" : "Write"}${
      resourceType.charAt(0).toUpperCase() + resourceType.slice(1)
    }` as keyof VAgendaPermissions;
    
    return perms[key] as boolean;
  }
}
```

### Multi-User Scenarios

Handle concurrent modifications:

```typescript
// Use Extension 10 (Version Control) sequence numbers
interface VAgendaDocument {
  vBRIEFInfo: {
    version: string;
    sequence: number;        // Increment on each modification
  };
  // ... rest of document
}

class ConcurrencySafeServer extends VAgendaMCPServer {
  protected async updateTodo(args: any): Promise<any> {
    // Optimistic locking
    const currentSeq = args.expectedSequence;
    const doc = await this.loadDocument();
    
    if (doc.vBRIEFInfo.sequence !== currentSeq) {
      return {
        content: [{
          type: "text",
          text: `Conflict: document was modified (expected seq ${currentSeq}, actual ${doc.vBRIEFInfo.sequence})`
        }],
        isError: true
      };
    }
    
    // Perform update
    // ...
    doc.vBRIEFInfo.sequence++;
    await this.saveDocument(doc);
    
    return { content: [{ type: "text", text: "Success" }], isError: false };
  }
}
```

### Audit Logging

Track all MCP operations:

```typescript
class AuditedVAgendaServer extends VAgendaMCPServer {
  private async logOperation(
    user: string,
    operation: string,
    args: any,
    success: boolean
  ): Promise<void> {
    await this.db.run(
      `INSERT INTO audit_log (timestamp, user, operation, args, success)
       VALUES (?, ?, ?, ?, ?)`,
      Date.now(),
      user,
      operation,
      JSON.stringify(args),
      success
    );
  }
}
```

## Format Negotiation

Clients can request TRON or JSON format:

```typescript
// Client specifies preferred format via Accept-like mechanism
const response = await client.readResource({
  uri: "vbrief://todos/current",
  // Custom parameter (not in MCP spec, but could be added)
  format: "json"  // or "tron"
});

// Server implementation
private async readVAgendaResource(
  uri: string,
  format: "tron" | "json" = "tron"
): Promise<string> {
  const data = await this.loadDocument(uri);
  
  if (format === "json") {
    return JSON.stringify(data, null, 2);
  } else {
    return this.serializeToTron(data);
  }
}
```

## Change Notifications

Server pushes updates to subscribed clients:

```typescript
// Client subscribes to resource
await client.request({
  method: "resources/subscribe",
  params: {
    uri: "vbrief://todos/current"
  }
});

// Server sends notification when resource changes
server.sendNotification({
  method: "notifications/resources/updated",
  params: {
    uri: "vbrief://todos/current"
  }
});

// Client handles notification
client.setNotificationHandler(
  "notifications/resources/updated",
  async (params) => {
    console.log(`Resource updated: ${params.uri}`);
    // Re-read resource
    const updated = await client.readResource({ uri: params.uri });
    // Handle updated content...
  }
);
```

## Relationship to Existing Extensions

### Claude Extension (vBRIEF-extension-claude.md)

The Claude extension mentioned MCP briefly but didn't define the protocol. This extension provides:
- Full MCP resource/tool definitions that Claude extension referenced
- Server implementation that Claude clients can connect to
- Standard way for Claude to access vBRIEF (vs custom file reading)

### Beads Extension (vBRIEF-extension-beads.md)

Beads currently uses file-based sync. With MCP:
- Beads could expose its data via MCP server
- vBRIEF MCP server could import/export Beads format
- Real-time sync between Beads and vBRIEF via MCP notifications

### Extension 10 (Version Control)

MCP operations should generate version control events:
- Each tool call increments sequence number
- Changes tracked via Extension 10 metadata
- Enables conflict resolution in multi-user scenarios

### Extension 11 (Multi-Agent Forking)

When multiple agents access vBRIEF via MCP:
- Each agent can fork for independent exploration
- MCP tools for creating/merging forks
- Notification mechanism for fork events

### Extension 12 (Playbooks)

MCP makes playbooks accessible:
- `vbrief://playbook` resource for reading learnings
- `vbrief_add_learning` tool for accumulating knowledge
- `vbrief_query_playbook` tool for semantic search
- Agents automatically build institutional memory via MCP

## Complete Tool Schema Definitions

### vbrief_create_todo

```json
{
  "name": "vbrief_create_todo",
  "description": "Create a new todo item in the current or specified TodoList",
  "inputSchema": {
    "type": "object",
    "properties": {
      "title": {
        "type": "string",
        "description": "Title of the todo item"
      },
      "description": {
        "type": "string",
        "description": "Detailed description of what needs to be done"
      },
      "status": {
        "type": "string",
        "enum": ["pending", "inProgress", "completed", "blocked", "cancelled"],
        "description": "Initial status of the todo item",
        "default": "pending"
      },
      "assignee": {
        "type": "string",
        "description": "Person or agent assigned to this task"
      },
      "dependencies": {
        "type": "array",
        "items": { "type": "string" },
        "description": "IDs of todos that must be completed first (requires Extension 4)"
      },
      "todoListId": {
        "type": "string",
        "description": "Target TodoList ID, defaults to current"
      }
    },
    "required": ["title"]
  }
}
```

### vbrief_update_todo

```json
{
  "name": "vbrief_update_todo",
  "description": "Update an existing todo item",
  "inputSchema": {
    "type": "object",
    "properties": {
      "id": {
        "type": "string",
        "description": "ID of the todo item to update"
      },
      "title": {
        "type": "string",
        "description": "New title"
      },
      "description": {
        "type": "string",
        "description": "New description"
      },
      "status": {
        "type": "string",
        "enum": ["pending", "inProgress", "completed", "blocked", "cancelled"],
        "description": "New status"
      },
      "assignee": {
        "type": "string",
        "description": "New assignee"
      },
      "expectedSequence": {
        "type": "number",
        "description": "Expected sequence number for optimistic locking (requires Extension 10)"
      }
    },
    "required": ["id"]
  }
}
```

### vbrief_create_plan

```json
{
  "name": "vbrief_create_plan",
  "description": "Create a new implementation plan",
  "inputSchema": {
    "type": "object",
    "properties": {
      "title": {
        "type": "string",
        "description": "Title of the plan"
      },
      "status": {
        "type": "string",
        "enum": ["draft", "active", "completed", "cancelled"],
        "description": "Initial status",
        "default": "draft"
      },
      "narratives": {
        "type": "object",
        "description": "Named narratives (problem, proposal, decision, etc.) as keyed markdown strings",
        "additionalProperties": {"type": "string"}
      },
      "phases": {
        "type": "array",
        "description": "Implementation phases",
        "items": {
          "type": "object",
          "properties": {
            "title": { "type": "string" },
            "status": {
              "type": "string",
              "enum": ["pending", "inProgress", "completed", "cancelled"],
              "default": "pending"
            }
          },
          "required": ["title"]
        }
      }
    },
    "required": ["title"]
  }
}
```

### vbrief_add_learning

```json
{
  "name": "vbrief_add_learning",
  "description": "Append a new PlaybookItem event (requires Extension 12)",
  "inputSchema": {
    "type": "object",
    "properties": {
      "targetId": {
        "type": "string",
        "description": "Stable ID for this learning (targetId)"
      },
      "kind": {
        "type": "string",
        "enum": ["strategy", "learning", "rule", "warning", "note"],
        "description": "Kind of playbook entry"
      },
      "title": {
        "type": "string",
        "description": "Optional title"
      },
      "narrative": {
        "type": "object",
        "minProperties": 1,
        "additionalProperties": {"type": "string"},
        "description": "Named narrative blocks as keyed markdown strings"
      },
      "tags": {
        "type": "array",
        "items": {"type": "string"}
      },
      "evidence": {
        "type": "array",
        "items": {"type": "string"}
      },
      "confidence": {
        "type": "number",
        "minimum": 0,
        "maximum": 1
      }
    },
    "required": ["targetId", "kind", "narrative"]
  }
}
```

### vbrief_query_playbook

```json
{
  "name": "vbrief_query_playbook",
  "description": "Search the playbook for relevant entries (requires Extension 12)",
  "inputSchema": {
    "type": "object",
    "properties": {
      "kind": {
        "type": "string",
        "enum": ["strategy", "learning", "rule", "warning", "note"],
        "description": "Filter by kind"
      },
      "tags": {
        "type": "array",
        "items": {"type": "string"},
        "description": "Filter by tags (AND logic)"
      },
      "searchText": {
        "type": "string",
        "description": "Full-text search query"
      },
      "limit": {
        "type": "number",
        "description": "Maximum number of results",
        "default": 10
      }
    }
  }
}
```

## Examples

### Example 1: Complete MCP Server Session

```bash
# Terminal 1: Start vBRIEF MCP server
$ vbrief-mcp-server --project ~/Projects/myapp
[INFO] vBRIEF MCP Server v0.1.0
[INFO] Project: /Users/me/Projects/myapp
[INFO] Listening on stdio
```

```typescript
// Terminal 2: Client connects and interacts
import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StdioClientTransport } from "@modelcontextprotocol/sdk/client/stdio.js";

async function main() {
  // Connect to server
  const transport = new StdioClientTransport({
    command: "vbrief-mcp-server",
    args: ["--project", "~/Projects/myapp"],
  });
  
  const client = new Client(
    { name: "example-client", version: "1.0.0" },
    { capabilities: {} }
  );
  
  await client.connect(transport);
  console.log("Connected to vBRIEF MCP server");
  
  // List resources
  const resources = await client.request({
    method: "resources/list",
  });
  console.log("Available resources:", resources.resources.map(r => r.uri));
  
  // Read current todos
  const todosResponse = await client.request({
    method: "resources/read",
    params: { uri: "vbrief://todos/current" },
  });
  console.log("Current todos:");
  console.log(todosResponse.contents[0].text);
  
  // Create a new todo
  const createResponse = await client.request({
    method: "tools/call",
    params: {
      name: "vbrief_create_todo",
      arguments: {
        title: "Add MCP integration tests",
        description: "Write comprehensive tests for MCP server",
        status: "pending",
      },
    },
  });
  console.log(createResponse.content[0].text);
  // Output: "Created todo item with ID: todo-abc123"
  
  // Update the todo
  const updateResponse = await client.request({
    method: "tools/call",
    params: {
      name: "vbrief_update_todo",
      arguments: {
        id: "todo-abc123",
        status: "inProgress",
      },
    },
  });
  console.log(updateResponse.content[0].text);
  // Output: "Updated todo item: todo-abc123"
  
  // Add a learning
  await client.request({
    method: "tools/call",
    params: {
      name: "vbrief_add_learning",
      arguments: {
        category: "patterns",
        title: "MCP server stdio transport pattern",
        content: "Using stdio transport for MCP servers works well for single-user local dev",
        tags: ["mcp", "architecture"],
      },
    },
  });
  
  await client.close();
}

main().catch(console.error);
```

### Example 2: Claude Desktop Integration

```json
// ~/Library/Application Support/Claude/claude_desktop_config.json
{
  "mcpServers": {
    "vbrief": {
      "command": "npx",
      "args": [
        "-y",
        "@vbrief/mcp-server",
        "--project",
        "/Users/me/Projects/myapp"
      ],
      "env": {
        "VCONTEXT_FORMAT": "tron"
      }
    }
  }
}
```

When Claude Desktop starts, it automatically connects to the vBRIEF MCP server. Now Claude can:

```
User: What tasks do I have pending?

Claude: Let me check your current vBRIEF tasks.
[calls resources/read on vbrief://todos/current]

You have 3 pending tasks:
1. "Add MCP integration tests" - High priority
2. "Update documentation" - Medium priority
3. "Review PR #42" - Low priority

Would you like me to help with any of these?

---

User: Start working on the MCP integration tests

Claude: I'll mark that task as in progress and begin working on it.
[calls tools/call with vbrief_update_todo]

Updated task status to inProgress. Let me review the current codebase...
[continues with implementation]
```

### Example 3: Aider Integration

```python
# aider_vbrief.py - Aider plugin for vBRIEF MCP
from mcp import Client, StdioClientTransport

class VAgendaIntegration:
    def __init__(self, project_path):
        self.client = Client(
            {"name": "aider", "version": "1.0.0"},
            {"capabilities": {}}
        )
        self.transport = StdioClientTransport(
            command="vbrief-mcp-server",
            args=["--project", project_path]
        )
    
    async def start_session(self):
        await self.client.connect(self.transport)
        
        # Read current context
        response = await self.client.request({
            "method": "resources/read",
            "params": {"uri": "vbrief://todos/current"}
        })
        
        todos_content = response["contents"][0]["text"]
        return f"Current vBRIEF context:\n{todos_content}"
    
    async def complete_task(self, task_id):
        await self.client.request({
            "method": "tools/call",
            "params": {
                "name": "vbrief_update_todo",
                "arguments": {
                    "id": task_id,
                    "status": "completed"
                }
            }
        })
    
    async def add_learning(self, category, title, content):
        await self.client.request({
            "method": "tools/call",
            "params": {
                "name": "vbrief_add_learning",
                "arguments": {
                    "category": category,
                    "title": title,
                    "content": content
                }
            }
        })

# Usage in Aider
vbrief = VAgendaIntegration("/path/to/project")
await vbrief.start_session()
# Aider now has full vBRIEF context
```

### Example 4: Multi-Agent Coordination

```typescript
// Two agents working on same project
// Agent A (implementing feature)
const agentA = new Client(...);
await agentA.connect(...);

// Agent A creates todo
await agentA.request({
  method: "tools/call",
  params: {
    name: "vbrief_create_todo",
    arguments: {
      title: "Implement OAuth login",
      status: "inProgress",
      assignee: "agent-a"
    }
  }
});

// Agent B (code review)
const agentB = new Client(...);
await agentB.connect(...);

// Agent B subscribes to updates
await agentB.setNotificationHandler(
  "notifications/resources/updated",
  async (params) => {
    if (params.uri === "vbrief://todos/current") {
      console.log("Tasks updated, checking for review work...");
      const todos = await agentB.request({
        method: "resources/read",
        params: { uri: "vbrief://todos/current" }
      });
      // Agent B sees Agent A's work and can review
    }
  }
);

// When Agent A completes OAuth implementation
await agentA.request({
  method: "tools/call",
  params: {
    name: "vbrief_update_todo",
    arguments: {
      id: "todo-oauth",
      status: "completed"
    }
  }
});

// Agent B receives notification and creates review task
await agentB.request({
  method: "tools/call",
  params: {
    name: "vbrief_create_todo",
    arguments: {
      title: "Review OAuth implementation",
      assignee: "agent-b",
      dependencies: ["todo-oauth"]
    }
  }
});
```

## Migration Path

### Phase 1: Basic Server (v0.1)

**Goals**:
- Implement core resources (todos, plans, playbook)
- Implement core tools (create/update/delete)
- Support stdio transport only
- File-based backend

**Deliverables**:
- `vbrief-mcp-server` npm package
- Basic documentation
- Example integrations for Claude Desktop

**Timeline**: 1-2 months

### Phase 2: Advanced Features (v0.2)

**Goals**:
- Add SSE transport for web tools
- Implement change notifications
- Add authentication layer
- Support database backend (SQLite)

**Deliverables**:
- Multi-transport server
- Permission system
- Audit logging
- Real-time collaboration support

**Timeline**: 2-3 months

### Phase 3: Ecosystem Integration (v1.0)

**Goals**:
- Pre-built servers for common stacks (Node.js, Python, Go)
- Native integrations (Aider, Cursor, Claude Projects)
- MCP extension marketplace listing
- Production-grade reliability

**Deliverables**:
- Multi-language server implementations
- Plugin/extension packages for popular tools
- Comprehensive test suite
- Production deployment guides

**Timeline**: 3-4 months

## Open Questions

### 1. Format Support

**Question**: Should MCP server support both TRON and JSON, or TRON only?

**Options**:
- A: TRON only (simplest, forces standardization)
- B: Both TRON and JSON (more flexible, gradual adoption)
- C: JSON only initially, add TRON later (lowest barrier)

**Recommendation**: Option B. Use content negotiation to let clients choose. Default to TRON for efficiency, support JSON for compatibility.

### 2. Message Size Limits

**Question**: How to handle large playbooks that exceed MCP message size limits?

**Options**:
- A: Paginate results (multiple requests)
- B: Compress content (gzip)
- C: Return summaries with links to full content
- D: Split into smaller resources (e.g., `vbrief://playbook/strategies`)

**Recommendation**: Option D + C. Split playbook into category-specific resources, provide summary resource with links.

### 3. Server Scope

**Question**: Should vBRIEF MCP server be mandatory or optional?

**Options**:
- A: Mandatory - all vBRIEF tools must use MCP
- B: Optional - file-based and MCP both supported
- C: Recommended - MCP preferred but not required

**Recommendation**: Option C. MCP provides significant benefits but shouldn't block adoption.

### 4. Offline Support

**Question**: How to handle offline scenarios (MCP requires server connection)?

**Options**:
- A: Fall back to file-based access when server unavailable
- B: Client-side caching with sync on reconnection
- C: Hybrid mode - read from cache, queue writes
- D: No offline support (require server)

**Recommendation**: Option C. Implement offline-capable MCP client that queues operations and syncs when connected.

## Community Feedback

We're seeking feedback on:

1. **Transport priorities**: Which transports are most important? (stdio, SSE, HTTP)
2. **Multi-project support**: Should one MCP server handle multiple vBRIEF projects?
3. **Permission model**: What permission granularity makes sense?
4. **Tool set**: Are there additional MCP tools we should include?
5. **Discovery**: How should clients discover vBRIEF MCP servers?
6. **Interop**: Should vBRIEF MCP server support other formats (Beads, markdown)?

Please provide feedback via:
- GitHub issues: https://github.com/visionik/vBRIEF/issues
- GitHub discussions: https://github.com/visionik/vBRIEF/discussions
- Email: visionik@pobox.com

## References

- **MCP Specification**: https://modelcontextprotocol.io
- **MCP TypeScript SDK**: https://github.com/modelcontextprotocol/typescript-sdk
- **MCP Python SDK**: https://github.com/modelcontextprotocol/python-sdk
- **vBRIEF Core Specification**: SPEC-v2.md
- **vBRIEF Claude Extension**: vBRIEF-extension-claude.md
- **vBRIEF Beads Extension**: vBRIEF-extension-beads.md
- **Claude Desktop MCP Setup**: https://modelcontextprotocol.io/quickstart/user

## Appendix: MCP Protocol Basics

For those unfamiliar with MCP, here's a quick primer:

### MCP Architecture

```
┌─────────────────┐         ┌──────────────────┐
│   AI Client     │◄───────►│   MCP Server     │
│  (Claude, etc)  │   MCP   │  (vBRIEF, etc)  │
└─────────────────┘ Protocol└──────────────────┘
                               │
                               ▼
                         ┌──────────────┐
                         │  Data Store  │
                         │ (files, DB)  │
                         └──────────────┘
```

### Core MCP Concepts

**Resources**: Read-only data endpoints
- Example: `vbrief://todos/current`
- Accessed via `resources/read`
- Can be files, API responses, database queries

**Tools**: Operations that modify state
- Example: `vbrief_create_todo`
- Invoked via `tools/call`
- Can have side effects

**Prompts**: Pre-defined templates
- Example: `vbrief_session_start`
- Help AI agents use the system correctly

### MCP Request/Response Flow

```
Client                          Server
  │                               │
  ├──────resources/list ─────────►│
  │◄──────list of resources───────┤
  │                               │
  ├──────resources/read ─────────►│
  │      (uri: vbrief://todos)   │
  │◄──────TRON content ───────────┤
  │                               │
  ├──────tools/call ─────────────►│
  │      (name: vbrief_create_todo)
  │◄──────success response────────┤
  │                               │
  ◄──notifications/resources/updated─
         (uri: vbrief://todos)
```

This extension leverages MCP's standardized protocol to make vBRIEF universally accessible to AI agents.
