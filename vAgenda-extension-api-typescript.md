# vAgenda Extension Proposal: TypeScript/JavaScript API Library

> **EARLY DRAFT**: This is an initial proposal and subject to change. Comments, feedback, and suggestions are strongly encouraged. Please provide input via GitHub issues or discussions.

**Extension Name**: TypeScript/JavaScript API Library  
**Version**: 0.1 (Draft)  
**Status**: Proposal  
**Author**: Jonathan Taylor (visionik@pobox.com)  
**Date**: 2025-12-27

## Overview

This document describes a TypeScript library implementation for working with vAgenda documents. The library provides type-safe interfaces for creating, parsing, manipulating, and validating vAgenda TodoLists and Plans in both JSON and TRON formats, with full JavaScript interoperability.

The library enables:
- **Type-safe operations** with full TypeScript support
- **Format conversion** between JSON and TRON
- **Schema validation** with Zod or similar validators
- **Builder patterns** for fluent document construction
- **Query interfaces** with functional programming patterns
- **Framework integration** (React, Vue, Node.js, Deno, Bun)
- **Zero dependencies** core with optional plugins

## Motivation

**Why a TypeScript library?**
- TypeScript/JavaScript dominates web development and modern tooling
- Type safety prevents errors while maintaining JS flexibility
- NPM ecosystem enables wide distribution
- Works in browser, Node.js, Deno, and Bun environments
- Perfect for web UIs, CLIs, and agentic systems
- Strong integration with modern frameworks

**Use cases**:
- Web-based vAgenda editors and viewers (React, Vue, Svelte)
- Node.js agentic systems and task orchestrators
- CLI tools with modern JS runtimes (Bun, Deno)
- Browser extensions for vAgenda management
- API servers (Express, Fastify, Hono)
- Desktop apps (Electron, Tauri)
- Mobile apps (React Native, Capacitor)

## Architecture

### Package Structure

```
@vagenda/
├── core/                  # Core types and interfaces
│   ├── src/
│   │   ├── types.ts       # Core type definitions
│   │   ├── document.ts    # Document class
│   │   ├── todo.ts        # TodoList/TodoItem classes
│   │   ├── plan.ts        # Plan/Phase/Narrative classes
│   │   └── index.ts       # Exports
│   └── package.json
│
├── parser/                # Parsing and serialization
│   ├── src/
│   │   ├── json.ts        # JSON parser
│   │   ├── tron.ts        # TRON parser
│   │   ├── auto.ts        # Auto-detect format
│   │   └── index.ts
│   └── package.json
│
├── builder/               # Fluent builders
│   ├── src/
│   │   ├── todo-builder.ts
│   │   ├── plan-builder.ts
│   │   └── index.ts
│   └── package.json
│
├── validator/             # Schema validation
│   ├── src/
│   │   ├── schemas.ts     # Zod schemas
│   │   ├── validator.ts   # Validation logic
│   │   └── index.ts
│   └── package.json
│
├── query/                 # Query and filtering
│   ├── src/
│   │   ├── todo-query.ts
│   │   ├── plan-query.ts
│   │   └── index.ts
│   └── package.json
│
├── mutator/               # Direct mutation helpers
│   ├── src/
│   │   ├── todo-mutator.ts
│   │   ├── plan-mutator.ts
│   │   └── index.ts
│   └── package.json
│
├── updater/               # Immutable and validated updates
│   ├── src/
│   │   ├── immutable.ts
│   │   ├── validated.ts
│   │   └── index.ts
│   └── package.json
│
├── extensions/            # Extension implementations
│   ├── timestamps/
│   ├── identifiers/
│   ├── metadata/
│   ├── hierarchical/
│   ├── workflow/
│   ├── participants/
│   ├── resources/
│   ├── recurring/
│   ├── security/
│   ├── version/
│   ├── forking/
│   └── ace/
│
├── react/                 # React hooks and components
│   ├── src/
│   │   ├── hooks/
│   │   ├── components/
│   │   └── index.ts
│   └── package.json
│
├── vue/                   # Vue composables
├── cli/                   # CLI tool (va command)
└── web/                   # Web components (vanilla)
```

## Core API Design

### Core Types

```typescript
// types.ts

/**
 * Root vAgenda document
 */
export interface Document {
  vAgendaInfo: Info;
  todoList?: TodoList;
  plan?: Plan;
}

/**
 * Document-level metadata
 */
export interface Info {
  version: string;
  author?: string;
  description?: string;
  metadata?: Record<string, unknown>;
}

/**
 * Collection of work items
 */
export interface TodoList {
  items: TodoItem[];
}

/**
 * Single actionable task
 */
export interface TodoItem {
  title: string;
  status: ItemStatus;
}

/**
 * Todo item status values
 */
export type ItemStatus = 
  | "pending" 
  | "inProgress" 
  | "completed" 
  | "blocked" 
  | "cancelled";

/**
 * Structured design document
 */
export interface Plan {
  title: string;
  status: PlanStatus;
  narratives: Record<string, Narrative>;
}

/**
 * Plan status values
 */
export type PlanStatus = 
  | "draft" 
  | "proposed" 
  | "approved" 
  | "inProgress" 
  | "completed" 
  | "cancelled";

/**
 * Stage of work within a plan
 */
export interface Phase {
  title: string;
  status: PhaseStatus;
}

/**
 * Phase status values
 */
export type PhaseStatus = 
  | "pending" 
  | "inProgress" 
  | "completed" 
  | "blocked" 
  | "cancelled";

/**
 * Named documentation block
 */
export interface Narrative {
  title: string;
  content: string;
}
```

### Document Class API

```typescript
// document.ts

export class VAgendaDocument {
  constructor(public data: Document) {}

  /**
   * Create a new TodoList document
   */
  static createTodoList(version: string = "0.2"): VAgendaDocument {
    return new VAgendaDocument({
      vAgendaInfo: { version },
      todoList: { items: [] }
    });
  }

  /**
   * Create a new Plan document
   */
  static createPlan(
    title: string, 
    version: string = "0.2"
  ): VAgendaDocument {
    return new VAgendaDocument({
      vAgendaInfo: { version },
      plan: {
        title,
        status: "draft",
        narratives: {}
      }
    });
  }

  /**
   * Parse from JSON string
   */
  static fromJSON(json: string): VAgendaDocument {
    return new VAgendaDocument(JSON.parse(json));
  }

  /**
   * Parse from TRON string
   */
  static fromTRON(tron: string): VAgendaDocument {
    // Implementation uses TRON parser
    throw new Error("Not implemented");
  }

  /**
   * Auto-detect format and parse
   */
  static parse(content: string): VAgendaDocument {
    // Try JSON first, fall back to TRON
    try {
      return VAgendaDocument.fromJSON(content);
    } catch {
      return VAgendaDocument.fromTRON(content);
    }
  }

  /**
   * Convert to JSON string
   */
  toJSON(pretty: boolean = false): string {
    return JSON.stringify(this.data, null, pretty ? 2 : undefined);
  }

  /**
   * Convert to TRON string
   */
  toTRON(): string {
    // Implementation uses TRON serializer
    throw new Error("Not implemented");
  }

  /**
   * Get TodoList (if present)
   */
  get todoList(): TodoList | undefined {
    return this.data.todoList;
  }

  /**
   * Get Plan (if present)
   */
  get plan(): Plan | undefined {
    return this.data.plan;
  }

  /**
   * Validate document against schema
   */
  validate(): ValidationResult {
    // Implementation uses validator
    throw new Error("Not implemented");
  }
}
```

### Parser API

```typescript
// parser/index.ts

export interface Parser {
  /**
   * Parse a vAgenda document
   */
  parse(content: string): Document;
  
  /**
   * Parse from stream (Node.js)
   */
  parseStream?(stream: ReadableStream): Promise<Document>;
}

/**
 * JSON parser implementation
 */
export class JSONParser implements Parser {
  parse(content: string): Document {
    return JSON.parse(content);
  }
}

/**
 * TRON parser implementation
 */
export class TRONParser implements Parser {
  parse(content: string): Document {
    // TRON parsing logic
    throw new Error("Not implemented");
  }
}

/**
 * Auto-detecting parser
 */
export class AutoParser implements Parser {
  parse(content: string): Document {
    // Detect format and delegate
    const trimmed = content.trim();
    if (trimmed.startsWith('{')) {
      return new JSONParser().parse(content);
    } else {
      return new TRONParser().parse(content);
    }
  }
}

/**
 * Parse helper function
 */
export function parse(
  content: string, 
  format?: "json" | "tron" | "auto"
): Document {
  const parser = format === "json" 
    ? new JSONParser()
    : format === "tron" 
    ? new TRONParser()
    : new AutoParser();
  
  return parser.parse(content);
}
```

### Builder API

```typescript
// builder/todo-builder.ts

export class TodoListBuilder {
  private doc: Document;

  constructor(version: string = "0.2") {
    this.doc = {
      vAgendaInfo: { version },
      todoList: { items: [] }
    };
  }

  /**
   * Set document author
   */
  author(name: string): this {
    this.doc.vAgendaInfo.author = name;
    return this;
  }

  /**
   * Set document description
   */
  description(desc: string): this {
    this.doc.vAgendaInfo.description = desc;
    return this;
  }

  /**
   * Add a todo item
   */
  addItem(title: string, status: ItemStatus = "pending"): this {
    this.doc.todoList!.items.push({ title, status });
    return this;
  }

  /**
   * Add multiple items
   */
  addItems(items: TodoItem[]): this {
    this.doc.todoList!.items.push(...items);
    return this;
  }

  /**
   * Build the document
   */
  build(): Document {
    return this.doc;
  }

  /**
   * Build and wrap in VAgendaDocument
   */
  buildDocument(): VAgendaDocument {
    return new VAgendaDocument(this.build());
  }
}

// builder/plan-builder.ts

export class PlanBuilder {
  private doc: Document;

  constructor(title: string, version: string = "0.2") {
    this.doc = {
      vAgendaInfo: { version },
      plan: {
        title,
        status: "draft",
        narratives: {}
      }
    };
  }

  /**
   * Set plan status
   */
  status(status: PlanStatus): this {
    this.doc.plan!.status = status;
    return this;
  }

  /**
   * Add a narrative
   */
  narrative(key: string, title: string, content: string): this {
    this.doc.plan!.narratives[key] = { title, content };
    return this;
  }

  /**
   * Add proposal narrative (required)
   */
  proposal(title: string, content: string): this {
    return this.narrative("proposal", title, content);
  }

  /**
   * Add problem narrative
   */
  problem(title: string, content: string): this {
    return this.narrative("problem", title, content);
  }

  /**
   * Add context narrative
   */
  context(title: string, content: string): this {
    return this.narrative("context", title, content);
  }

  /**
   * Build the document
   */
  build(): Document {
    return this.doc;
  }

  /**
   * Build and wrap in VAgendaDocument
   */
  buildDocument(): VAgendaDocument {
    return new VAgendaDocument(this.build());
  }
}

// Convenience functions
export function todo(version?: string): TodoListBuilder {
  return new TodoListBuilder(version);
}

export function plan(title: string, version?: string): PlanBuilder {
  return new PlanBuilder(title, version);
}
```

### Validator API

```typescript
// validator/schemas.ts (using Zod)

import { z } from "zod";

export const ItemStatusSchema = z.enum([
  "pending",
  "inProgress",
  "completed",
  "blocked",
  "cancelled"
]);

export const TodoItemSchema = z.object({
  title: z.string().min(1),
  status: ItemStatusSchema
});

export const TodoListSchema = z.object({
  items: z.array(TodoItemSchema)
});

export const PlanStatusSchema = z.enum([
  "draft",
  "proposed",
  "approved",
  "inProgress",
  "completed",
  "cancelled"
]);

export const NarrativeSchema = z.object({
  title: z.string(),
  content: z.string()
});

export const PlanSchema = z.object({
  title: z.string().min(1),
  status: PlanStatusSchema,
  narratives: z.record(NarrativeSchema)
});

export const InfoSchema = z.object({
  version: z.string(),
  author: z.string().optional(),
  description: z.string().optional(),
  metadata: z.record(z.unknown()).optional()
});

export const DocumentSchema = z.object({
  vAgendaInfo: InfoSchema,
  todoList: TodoListSchema.optional(),
  plan: PlanSchema.optional()
});

// validator/validator.ts

export interface ValidationResult {
  valid: boolean;
  errors?: ValidationError[];
}

export interface ValidationError {
  path: string;
  message: string;
}

export class Validator {
  /**
   * Validate a document
   */
  validate(doc: Document): ValidationResult {
    const result = DocumentSchema.safeParse(doc);
    
    if (result.success) {
      return { valid: true };
    }
    
    return {
      valid: false,
      errors: result.error.errors.map(err => ({
        path: err.path.join("."),
        message: err.message
      }))
    };
  }

  /**
   * Validate and throw on error
   */
  validateOrThrow(doc: Document): void {
    const result = this.validate(doc);
    if (!result.valid) {
      throw new ValidationError(
        `Validation failed: ${result.errors!.map(e => e.message).join(", ")}`
      );
    }
  }
}

export function validate(doc: Document): ValidationResult {
  return new Validator().validate(doc);
}
```

### Query API

```typescript
// query/todo-query.ts

export class TodoQuery {
  constructor(private items: TodoItem[]) {}

  /**
   * Filter by status
   */
  byStatus(status: ItemStatus): TodoQuery {
    return new TodoQuery(
      this.items.filter(item => item.status === status)
    );
  }

  /**
   * Filter by title pattern
   */
  byTitle(pattern: string | RegExp): TodoQuery {
    const regex = typeof pattern === "string" 
      ? new RegExp(pattern, "i")
      : pattern;
    
    return new TodoQuery(
      this.items.filter(item => regex.test(item.title))
    );
  }

  /**
   * Filter with custom predicate
   */
  where(predicate: (item: TodoItem) => boolean): TodoQuery {
    return new TodoQuery(this.items.filter(predicate));
  }

  /**
   * Map items
   */
  map<T>(fn: (item: TodoItem) => T): T[] {
    return this.items.map(fn);
  }

  /**
   * Get all matching items
   */
  all(): TodoItem[] {
    return this.items;
  }

  /**
   * Get first matching item
   */
  first(): TodoItem | undefined {
    return this.items[0];
  }

  /**
   * Get count of matching items
   */
  count(): number {
    return this.items.length;
  }

  /**
   * Check if any items match
   */
  exists(): boolean {
    return this.items.length > 0;
  }
}

/**
| * Create a query for todo items
| */
export function query(items: TodoItem[]): TodoQuery {
  return new TodoQuery(items);
}
```

### Mutation API

The library supports document modification through multiple patterns: direct mutation (for simple cases), immutable updates (for functional patterns), and validated mutations (for complex scenarios).

#### Direct Mutation Helpers

```typescript
// mutator/todo-mutator.ts

import type { TodoList, TodoItem, ItemStatus } from "@vagenda/core";

/**
 * Helper functions for mutating TodoList
 */
export class TodoListMutator {
  constructor(private list: TodoList) {}

  /**
   * Add an item to the list
   */
  addItem(title: string, status: ItemStatus = "pending"): void {
    this.list.items.push({ title, status });
  }

  /**
   * Remove an item by index
   */
  removeItem(index: number): void {
    if (index < 0 || index >= this.list.items.length) {
      throw new Error(`Index out of range: ${index}`);
    }
    this.list.items.splice(index, 1);
  }

  /**
   * Update an item by index
   */
  updateItem(index: number, updates: Partial<TodoItem>): void {
    if (index < 0 || index >= this.list.items.length) {
      throw new Error(`Index out of range: ${index}`);
    }
    Object.assign(this.list.items[index], updates);
  }

  /**
   * Find and update items matching predicate
   */
  findAndUpdate(
    predicate: (item: TodoItem) => boolean,
    updates: Partial<TodoItem>
  ): number {
    let count = 0;
    for (const item of this.list.items) {
      if (predicate(item)) {
        Object.assign(item, updates);
        count++;
      }
    }
    return count;
  }

  /**
   * Clear all items
   */
  clear(): void {
    this.list.items = [];
  }
}

// mutator/plan-mutator.ts

import type { Plan, Narrative, PlanStatus } from "@vagenda/core";

/**
 * Helper functions for mutating Plan
 */
export class PlanMutator {
  constructor(private plan: Plan) {}

  /**
   * Add or update a narrative
   */
  setNarrative(key: string, narrative: Narrative): void {
    this.plan.narratives[key] = narrative;
  }

  /**
   * Remove a narrative
   */
  removeNarrative(key: string): void {
    delete this.plan.narratives[key];
  }

  /**
   * Update narrative content
   */
  updateNarrative(key: string, updates: Partial<Narrative>): void {
    if (!(key in this.plan.narratives)) {
      throw new Error(`Narrative not found: ${key}`);
    }
    Object.assign(this.plan.narratives[key], updates);
  }

  /**
   * Set plan status
   */
  setStatus(status: PlanStatus): void {
    this.plan.status = status;
  }
}

/**
 * Create a mutator for a TodoList
 */
export function mutateTodoList(list: TodoList): TodoListMutator {
  return new TodoListMutator(list);
}

/**
 * Create a mutator for a Plan
 */
export function mutatePlan(plan: Plan): PlanMutator {
  return new PlanMutator(plan);
}
```

#### Immutable Update Helpers

```typescript
// updater/immutable.ts

import type { Document, TodoList, TodoItem, Plan, Narrative, ItemStatus, PlanStatus } from "@vagenda/core";

/**
 * Immutable update helpers using structural sharing
 */
export class ImmutableUpdater {
  /**
   * Add item to TodoList (immutable)
   */
  static addItem(doc: Document, title: string, status: ItemStatus = "pending"): Document {
    if (!doc.todoList) {
      throw new Error("Document has no TodoList");
    }
    
    return {
      ...doc,
      todoList: {
        ...doc.todoList,
        items: [...doc.todoList.items, { title, status }]
      }
    };
  }

  /**
   * Remove item from TodoList (immutable)
   */
  static removeItem(doc: Document, index: number): Document {
    if (!doc.todoList) {
      throw new Error("Document has no TodoList");
    }
    
    return {
      ...doc,
      todoList: {
        ...doc.todoList,
        items: doc.todoList.items.filter((_, i) => i !== index)
      }
    };
  }

  /**
   * Update item in TodoList (immutable)
   */
  static updateItem(
    doc: Document, 
    index: number, 
    updates: Partial<TodoItem>
  ): Document {
    if (!doc.todoList) {
      throw new Error("Document has no TodoList");
    }
    
    return {
      ...doc,
      todoList: {
        ...doc.todoList,
        items: doc.todoList.items.map((item, i) => 
          i === index ? { ...item, ...updates } : item
        )
      }
    };
  }

  /**
   * Find and update items (immutable)
   */
  static findAndUpdate(
    doc: Document,
    predicate: (item: TodoItem) => boolean,
    updates: Partial<TodoItem>
  ): Document {
    if (!doc.todoList) {
      throw new Error("Document has no TodoList");
    }
    
    return {
      ...doc,
      todoList: {
        ...doc.todoList,
        items: doc.todoList.items.map(item =>
          predicate(item) ? { ...item, ...updates } : item
        )
      }
    };
  }

  /**
   * Set narrative in Plan (immutable)
   */
  static setNarrative(
    doc: Document,
    key: string,
    narrative: Narrative
  ): Document {
    if (!doc.plan) {
      throw new Error("Document has no Plan");
    }
    
    return {
      ...doc,
      plan: {
        ...doc.plan,
        narratives: {
          ...doc.plan.narratives,
          [key]: narrative
        }
      }
    };
  }

  /**
   * Update plan status (immutable)
   */
  static setPlanStatus(doc: Document, status: PlanStatus): Document {
    if (!doc.plan) {
      throw new Error("Document has no Plan");
    }
    
    return {
      ...doc,
      plan: {
        ...doc.plan,
        status
      }
    };
  }
}
```

#### Validated Updater

```typescript
// updater/validated.ts

import type { Document, TodoItem, ItemStatus, PlanStatus, Narrative } from "@vagenda/core";
import { Validator, type ValidationResult } from "@vagenda/validator";

export interface UpdateResult {
  success: boolean;
  document?: Document;
  validation?: ValidationResult;
}

/**
 * Validated updater with automatic validation after mutations
 */
export class ValidatedUpdater {
  private validator: Validator;

  constructor(private doc: Document, validator?: Validator) {
    this.validator = validator ?? new Validator();
  }

  /**
   * Get the current document
   */
  getDocument(): Document {
    return this.doc;
  }

  /**
   * Validate current state
   */
  validate(): ValidationResult {
    return this.validator.validate(this.doc);
  }

  /**
   * Add item with validation
   */
  addItem(title: string, status: ItemStatus = "pending"): UpdateResult {
    if (!this.doc.todoList) {
      return {
        success: false,
        validation: {
          valid: false,
          errors: [{ path: "todoList", message: "Document has no TodoList" }]
        }
      };
    }

    this.doc.todoList.items.push({ title, status });
    const validation = this.validate();
    
    if (!validation.valid) {
      // Rollback
      this.doc.todoList.items.pop();
      return { success: false, validation };
    }
    
    return { success: true, document: this.doc };
  }

  /**
   * Update item with validation
   */
  updateItem(index: number, updates: Partial<TodoItem>): UpdateResult {
    if (!this.doc.todoList) {
      return {
        success: false,
        validation: {
          valid: false,
          errors: [{ path: "todoList", message: "Document has no TodoList" }]
        }
      };
    }

    const item = this.doc.todoList.items[index];
    if (!item) {
      return {
        success: false,
        validation: {
          valid: false,
          errors: [{ path: `todoList.items[${index}]`, message: "Item not found" }]
        }
      };
    }

    // Save original for rollback
    const original = { ...item };
    Object.assign(item, updates);
    
    const validation = this.validate();
    
    if (!validation.valid) {
      // Rollback
      Object.assign(item, original);
      return { success: false, validation };
    }
    
    return { success: true, document: this.doc };
  }

  /**
   * Find and update with validation
   */
  findAndUpdate(
    predicate: (item: TodoItem) => boolean,
    updates: Partial<TodoItem>
  ): UpdateResult {
    if (!this.doc.todoList) {
      return {
        success: false,
        validation: {
          valid: false,
          errors: [{ path: "todoList", message: "Document has no TodoList" }]
        }
      };
    }

    // Save originals for rollback
    const originals = new Map<number, TodoItem>();
    const indices: number[] = [];
    
    this.doc.todoList.items.forEach((item, i) => {
      if (predicate(item)) {
        originals.set(i, { ...item });
        indices.push(i);
        Object.assign(item, updates);
      }
    });

    if (indices.length === 0) {
      return {
        success: false,
        validation: {
          valid: false,
          errors: [{ path: "todoList.items", message: "No matching items found" }]
        }
      };
    }
    
    const validation = this.validate();
    
    if (!validation.valid) {
      // Rollback all changes
      indices.forEach(i => {
        Object.assign(this.doc.todoList!.items[i], originals.get(i)!);
      });
      return { success: false, validation };
    }
    
    return { success: true, document: this.doc };
  }

  /**
   * Remove item with validation
   */
  removeItem(index: number): UpdateResult {
    if (!this.doc.todoList) {
      return {
        success: false,
        validation: {
          valid: false,
          errors: [{ path: "todoList", message: "Document has no TodoList" }]
        }
      };
    }

    const removed = this.doc.todoList.items.splice(index, 1);
    if (removed.length === 0) {
      return {
        success: false,
        validation: {
          valid: false,
          errors: [{ path: `todoList.items[${index}]`, message: "Item not found" }]
        }
      };
    }
    
    const validation = this.validate();
    
    if (!validation.valid) {
      // Rollback
      this.doc.todoList.items.splice(index, 0, removed[0]);
      return { success: false, validation };
    }
    
    return { success: true, document: this.doc };
  }

  /**
   * Set plan narrative with validation
   */
  setNarrative(key: string, narrative: Narrative): UpdateResult {
    if (!this.doc.plan) {
      return {
        success: false,
        validation: {
          valid: false,
          errors: [{ path: "plan", message: "Document has no Plan" }]
        }
      };
    }

    const original = this.doc.plan.narratives[key];
    this.doc.plan.narratives[key] = narrative;
    
    const validation = this.validate();
    
    if (!validation.valid) {
      // Rollback
      if (original) {
        this.doc.plan.narratives[key] = original;
      } else {
        delete this.doc.plan.narratives[key];
      }
      return { success: false, validation };
    }
    
    return { success: true, document: this.doc };
  }

  /**
   * Execute multiple operations in a transaction
   */
  transaction(fn: (updater: ValidatedUpdater) => UpdateResult): UpdateResult {
    // Create a deep clone for rollback
    const snapshot = JSON.parse(JSON.stringify(this.doc));
    
    const result = fn(this);
    
    if (!result.success) {
      // Rollback to snapshot
      this.doc = snapshot;
    }
    
    return result;
  }
}

/**
 * Create a validated updater
 */
export function createUpdater(doc: Document, validator?: Validator): ValidatedUpdater {
  return new ValidatedUpdater(doc, validator);
}
```

## Extension Support

Extensions use TypeScript declaration merging and module augmentation:

```typescript
// extensions/identifiers/types.ts

declare module "@vagenda/core" {
  interface TodoList {
    id?: string;
  }

  interface TodoItem {
    id?: string;
  }

  interface Plan {
    id?: string;
  }

  interface Phase {
    id?: string;
  }
}

// extensions/timestamps/types.ts

declare module "@vagenda/core" {
  interface Info {
    created?: string;
    updated?: string;
    timezone?: string;
  }

  interface TodoItem {
    created?: string;
    updated?: string;
  }
}

// extensions/metadata/types.ts

export type Priority = "low" | "medium" | "high" | "critical";

declare module "@vagenda/core" {
  interface TodoList {
    title?: string;
    description?: string;
    metadata?: Record<string, unknown>;
  }

  interface TodoItem {
    description?: string;
    priority?: Priority;
    tags?: string[];
    metadata?: Record<string, unknown>;
  }
}
```

## Usage Examples

### Example 1: Creating a TodoList

```typescript
import { todo } from "@vagenda/builder";

const doc = todo("0.2")
  .author("agent-alpha")
  .addItem("Implement authentication", "pending")
  .addItem("Write API documentation", "pending")
  .buildDocument();

// Convert to JSON
console.log(doc.toJSON(true));

// Convert to TRON
console.log(doc.toTRON());
```

### Example 2: Parsing and Querying

```typescript
import { VAgendaDocument } from "@vagenda/core";
import { query } from "@vagenda/query";
import { readFile } from "fs/promises";

// Parse document
const content = await readFile("tasks.tron", "utf-8");
const doc = VAgendaDocument.parse(content);

// Query pending items
const pending = query(doc.todoList!.items)
  .byStatus("pending")
  .all();

console.log(`Pending items: ${pending.length}`);
pending.forEach(item => console.log(`  - ${item.title}`));
```

### Example 3: Creating a Plan

```typescript
import { plan } from "@vagenda/builder";

const doc = plan("Add user authentication", "0.2")
  .status("draft")
  .proposal(
    "Proposed Changes",
    "Implement JWT-based authentication with refresh tokens"
  )
  .problem(
    "Problem Statement",
    "Current system lacks secure authentication"
  )
  .buildDocument();

console.log(doc.toTRON());
```

### Example 4: Validation

```typescript
import { VAgendaDocument } from "@vagenda/core";
import { validate } from "@vagenda/validator";

const doc = VAgendaDocument.fromJSON(`{
  "vAgendaInfo": {"version": "0.2"},
  "todoList": {"items": []}
}`);

const result = validate(doc.data);

if (result.valid) {
  console.log("Document is valid");
} else {
  console.error("Validation errors:");
  result.errors!.forEach(err => {
    console.error(`  ${err.path}: ${err.message}`);
  });
}
```

### Example 5: React Integration

```typescript
// react/hooks/useTodoList.ts

import { useState, useCallback } from "react";
import { Document, TodoItem, ItemStatus } from "@vagenda/core";

export function useTodoList(initialDoc: Document) {
  const [doc, setDoc] = useState(initialDoc);

  const addItem = useCallback((title: string, status: ItemStatus = "pending") => {
    setDoc(prev => ({
      ...prev,
      todoList: {
        ...prev.todoList!,
        items: [...prev.todoList!.items, { title, status }]
      }
    }));
  }, []);

  const updateItemStatus = useCallback((index: number, status: ItemStatus) => {
    setDoc(prev => ({
      ...prev,
      todoList: {
        ...prev.todoList!,
        items: prev.todoList!.items.map((item, i) => 
          i === index ? { ...item, status } : item
        )
      }
    }));
  }, []);

  const removeItem = useCallback((index: number) => {
    setDoc(prev => ({
      ...prev,
      todoList: {
        ...prev.todoList!,
        items: prev.todoList!.items.filter((_, i) => i !== index)
      }
    }));
  }, []);

  return {
    doc,
    items: doc.todoList?.items ?? [],
    addItem,
    updateItemStatus,
    removeItem
  };
}

// Usage in component
import { useTodoList } from "@vagenda/react";

function TodoListComponent() {
  const { items, addItem, updateItemStatus } = useTodoList({
    vAgendaInfo: { version: "0.2" },
    todoList: { items: [] }
  });

  return (
    <div>
      {items.map((item, i) => (
        <div key={i}>
          <span>{item.title}</span>
          <button onClick={() => updateItemStatus(i, "completed")}>
            Complete
          </button>
        </div>
      ))}
      <button onClick={() => addItem("New task")}>Add</button>
    </div>
  );
}
```

### Example 6: Vue Integration

```typescript
// vue/composables/useTodoList.ts

import { ref, computed } from "vue";
import type { Document, TodoItem, ItemStatus } from "@vagenda/core";

export function useTodoList(initialDoc: Document) {
  const doc = ref(initialDoc);

  const items = computed(() => doc.value.todoList?.items ?? []);

  const addItem = (title: string, status: ItemStatus = "pending") => {
    doc.value.todoList!.items.push({ title, status });
  };

  const updateItemStatus = (index: number, status: ItemStatus) => {
    doc.value.todoList!.items[index].status = status;
  };

  const removeItem = (index: number) => {
    doc.value.todoList!.items.splice(index, 1);
  };

  return {
    doc,
    items,
    addItem,
    updateItemStatus,
    removeItem
  };
}
```

### Example 7: Direct Mutations

```typescript
import { VAgendaDocument } from "@vagenda/core";
import { mutateTodoList } from "@vagenda/mutator";
import { readFile, writeFile } from "fs/promises";

// Parse existing document
const content = await readFile("tasks.tron", "utf-8");
const doc = VAgendaDocument.parse(content);

// Use mutator for direct changes
const mutator = mutateTodoList(doc.todoList!);

// Add new item
mutator.addItem("New urgent task", "pending");

// Update first item
mutator.updateItem(0, { status: "completed" });

// Find and update multiple items
const updated = mutator.findAndUpdate(
  item => item.status === "pending",
  { status: "inProgress" }
);
console.log(`Updated ${updated} items`);

// Save back
await writeFile("tasks.tron", doc.toTRON());
```

### Example 8: Immutable Updates

```typescript
import { VAgendaDocument } from "@vagenda/core";
import { ImmutableUpdater } from "@vagenda/updater";
import { readFile } from "fs/promises";

// Parse document
const content = await readFile("tasks.tron", "utf-8");
const doc = VAgendaDocument.parse(content);

// Immutable updates (functional style)
let updated = doc.data;

// Add item (returns new document)
updated = ImmutableUpdater.addItem(updated, "New task", "pending");

// Update first item (returns new document)
updated = ImmutableUpdater.updateItem(updated, 0, { status: "completed" });

// Find and update (returns new document)
updated = ImmutableUpdater.findAndUpdate(
  updated,
  item => item.status === "pending",
  { status: "inProgress" }
);

// Original doc.data is unchanged
console.log("Original:", doc.data.todoList?.items.length);
console.log("Updated:", updated.todoList?.items.length);

// Create new document from updated data
const newDoc = new VAgendaDocument(updated);
console.log(newDoc.toJSON(true));
```

### Example 9: Validated Updates

```typescript
import { VAgendaDocument } from "@vagenda/core";
import { createUpdater } from "@vagenda/updater";
import { readFile, writeFile } from "fs/promises";

// Parse document
const content = await readFile("tasks.tron", "utf-8");
const doc = VAgendaDocument.parse(content);

// Create validated updater
const updater = createUpdater(doc.data);

// Add item with validation
const result1 = updater.addItem("New task", "pending");
if (!result1.success) {
  console.error("Validation failed:", result1.validation?.errors);
}

// Find and update with validation
const result2 = updater.findAndUpdate(
  item => item.status === "pending",
  { status: "inProgress" }
);

if (result2.success) {
  console.log("All updates validated successfully");
  const updated = new VAgendaDocument(updater.getDocument());
  await writeFile("tasks.tron", updated.toTRON());
} else {
  console.error("Updates rolled back:", result2.validation?.errors);
}
```

### Example 10: Transactional Updates

```typescript
import { todo } from "@vagenda/builder";
import { createUpdater } from "@vagenda/updater";

// Create initial document
const doc = todo("0.2")
  .addItem("Task 1", "pending")
  .build();

// Perform multiple updates atomically
const updater = createUpdater(doc);
const result = updater.transaction(u => {
  // All these operations happen together
  let r = u.addItem("Task 2", "pending");
  if (!r.success) return r;
  
  r = u.addItem("Task 3", "pending");
  if (!r.success) return r;
  
  r = u.updateItem(0, { status: "inProgress" });
  if (!r.success) return r;
  
  return { success: true, document: u.getDocument() };
});

if (result.success) {
  console.log("Transaction completed");
  console.log(result.document!.todoList?.items.length); // 3 items
} else {
  console.log("Transaction rolled back");
  console.log(doc.todoList?.items.length); // Still 1 item
}
```

## CLI Tool Design

```bash
# Install globally
npm install -g @vagenda/cli
# or
pnpm add -g @vagenda/cli
# or
bun add -g @vagenda/cli

# Create a new TodoList
va create todo --version 0.2 --output tasks.tron

# Add an item
va add item tasks.tron "Implement auth" --status pending

# List items
va list tasks.tron

# Filter by status
va list tasks.tron --status pending

# Update item status
va update tasks.tron 0 --status completed

# Convert formats
va convert tasks.tron tasks.json --format json

# Validate document
va validate tasks.tron

# Query with filters
va query tasks.tron --status pending --priority high

# Create a plan
va create plan --title "Auth Implementation" --output plan.tron

# Add narrative
va add narrative plan.tron proposal "Proposed Changes" "Use JWT tokens..."

# Watch file and validate on change
va watch tasks.tron --validate

# Serve web UI
va serve tasks.tron --port 3000
```

## Testing Strategy

### Unit Tests (Vitest)

```typescript
// __tests__/todo-builder.test.ts

import { describe, it, expect } from "vitest";
import { TodoListBuilder } from "@vagenda/builder";

describe("TodoListBuilder", () => {
  it("creates a valid document", () => {
    const doc = new TodoListBuilder("0.2")
      .author("test-author")
      .addItem("Task 1", "pending")
      .build();

    expect(doc.vAgendaInfo.version).toBe("0.2");
    expect(doc.vAgendaInfo.author).toBe("test-author");
    expect(doc.todoList?.items).toHaveLength(1);
    expect(doc.todoList?.items[0].title).toBe("Task 1");
  });

  it("supports method chaining", () => {
    const builder = new TodoListBuilder("0.2");
    const result = builder
      .author("author")
      .addItem("Item 1")
      .addItem("Item 2");

    expect(result).toBe(builder);
  });
});
```

### Integration Tests

```typescript
// __tests__/integration/round-trip.test.ts

import { describe, it, expect } from "vitest";
import { todo } from "@vagenda/builder";
import { VAgendaDocument } from "@vagenda/core";

describe("Round-trip conversion", () => {
  it("JSON -> parse -> JSON preserves data", () => {
    const original = todo("0.2")
      .addItem("Task 1", "pending")
      .buildDocument();

    const json = original.toJSON();
    const parsed = VAgendaDocument.fromJSON(json);
    const reparsed = parsed.toJSON();

    expect(reparsed).toBe(json);
  });

  it("TRON -> parse -> TRON preserves data", () => {
    const original = todo("0.2")
      .addItem("Task 1", "pending")
      .buildDocument();

    const tron = original.toTRON();
    const parsed = VAgendaDocument.fromTRON(tron);
    const reparsed = parsed.toTRON();

    expect(reparsed).toBe(tron);
  });
});
```

### Coverage Requirements
- Overall coverage: ≥80% (TypeScript standard)
- Per-package coverage: ≥80%
- Critical paths: 100% (parser, validator)
- Exclude: examples/, CLI UI code

## Implementation Phases

### Phase 1: Core Foundation
- Core types and interfaces
- JSON parser/serializer
- Basic builder patterns
- Core validation (Zod schemas)
- npm package setup

### Phase 2: Extensions
- Extension 1: Timestamps
- Extension 2: Identifiers
- Extension 3: Rich Metadata
- Extension 4: Hierarchical
- Extended validation

### Phase 3: TRON Support
- TRON parser implementation
- TRON serializer
- Format auto-detection
- Conversion utilities

### Phase 4: Framework Integration
- React hooks and components
- Vue composables
- Svelte stores
- Solid.js primitives
- Web components

### Phase 5: Tooling
- CLI tool (@vagenda/cli)
- VSCode extension
- Web-based editor
- Documentation site

### Phase 6: Advanced Features
- Query interface with LINQ-style API
- Remaining extensions (5-12)
- Performance optimization
- Beads interop (if accepted)

## Package Configuration

### Core Package (package.json)

```json
{
  "name": "@vagenda/core",
  "version": "0.1.0",
  "description": "Core types and interfaces for vAgenda",
  "type": "module",
  "main": "./dist/index.cjs",
  "module": "./dist/index.js",
  "types": "./dist/index.d.ts",
  "exports": {
    ".": {
      "import": "./dist/index.js",
      "require": "./dist/index.cjs",
      "types": "./dist/index.d.ts"
    }
  },
  "files": ["dist"],
  "scripts": {
    "build": "tsup src/index.ts --format esm,cjs --dts",
    "test": "vitest",
    "test:coverage": "vitest --coverage",
    "typecheck": "tsc --noEmit",
    "lint": "eslint src",
    "prepublishOnly": "pnpm build"
  },
  "dependencies": {},
  "devDependencies": {
    "@types/node": "^20.0.0",
    "tsup": "^8.0.0",
    "typescript": "^5.3.0",
    "vitest": "^1.0.0"
  },
  "keywords": [
    "vagenda",
    "todo",
    "plan",
    "agenda",
    "task",
    "memory",
    "agent"
  ],
  "license": "MIT"
}
```

### Monorepo Setup (pnpm workspaces)

```yaml
# pnpm-workspace.yaml
packages:
  - "packages/*"
```

## Standards and Compliance

### Code Quality
- TypeScript strict mode enabled
- ESLint with recommended rules
- Prettier for formatting
- Vitest for testing (≥80% coverage)
- Conventional commits

### Documentation
- TSDoc comments for all public APIs
- README in each package
- Examples directory
- API documentation with TypeDoc

### Build Configuration

```typescript
// tsconfig.json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "ESNext",
    "lib": ["ES2022"],
    "moduleResolution": "bundler",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "declaration": true,
    "declarationMap": true,
    "sourceMap": true,
    "outDir": "./dist",
    "rootDir": "./src"
  },
  "include": ["src"],
  "exclude": ["node_modules", "dist", "__tests__"]
}
```

### Task Targets

```yaml
# Taskfile.yml additions
tasks:
  vagenda:ts:install:
    desc: Install dependencies
    cmds:
      - pnpm install

  vagenda:ts:build:
    desc: Build all packages
    cmds:
      - pnpm -r build

  vagenda:ts:test:
    desc: Run tests
    cmds:
      - pnpm -r test

  vagenda:ts:coverage:
    desc: Check test coverage
    cmds:
      - pnpm -r test:coverage

  vagenda:ts:lint:
    desc: Lint code
    cmds:
      - pnpm -r lint

  vagenda:ts:typecheck:
    desc: Type check
    cmds:
      - pnpm -r typecheck

  vagenda:cli:run:
    desc: Run CLI locally
    cmds:
      - pnpm --filter @vagenda/cli dev
```

## Runtime Support

The library targets:
- **Node.js**: ≥18.0.0
- **Deno**: ≥1.37.0
- **Bun**: ≥1.0.0
- **Browsers**: Modern browsers (ES2022)

## Open Questions

1. **TRON Parser Strategy**
   - Implement in TypeScript or use WASM?
   - **Proposal**: Start with TypeScript, optimize later if needed

2. **Reactivity System**
   - Use proxies for automatic change tracking?
   - **Proposal**: Optional reactivity package for those who need it

3. **Bundle Size**
   - Target size for core package?
   - **Proposal**: <10KB gzipped for core, tree-shakeable

4. **Framework Support Priority**
   - Which frameworks to support first?
   - **Proposal**: React first (largest userbase), then Vue, then others

5. **Server-Side Support**
   - Should we optimize for SSR/SSG?
   - **Proposal**: Yes, ensure all packages work in Node.js

## Related Work

- **TypeScript Libraries**: zod, io-ts, yup (validation)
- **CLI Libraries**: commander, yargs, cleye
- **Build Tools**: tsup, unbuild, pkgroll
- **Test Frameworks**: vitest, jest
- **Similar Projects**:
  - @microsoft/todo (Microsoft To Do SDK)
  - node-todoist (Todoist API client)
  - Various task management libraries

## References

- vAgenda Specification: https://github.com/visionik/vAgenda
- TypeScript Handbook: https://www.typescriptlang.org/docs/
- TRON Format: https://tron-format.github.io/
- Zod: https://zod.dev/
- Vitest: https://vitest.dev/
- vAgenda Go API: [vAgenda-extension-api-go.md](./vAgenda-extension-api-go.md)
- vAgenda Beads Extension: [vAgenda-extension-beads.md](./vAgenda-extension-beads.md)

## Community Feedback

This is a **draft proposal**. Feedback needed:

1. Is the package structure appropriate for a monorepo?
2. Should we use declaration merging for extensions or a different pattern?
3. Is Zod the right choice for validation?
4. Should React/Vue packages be separate or part of core?
5. What additional framework integrations would be valuable?
6. Should we provide a web component library for framework-agnostic usage?

**Discuss**: https://github.com/visionik/vAgenda/discussions
