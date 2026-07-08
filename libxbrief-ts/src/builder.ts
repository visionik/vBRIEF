import { VALID_STATUSES } from "./compat.js";
import { Plan, PlanItem, XBriefDocument, type PlanItemInit } from "./models.js";
import { isRecordLike } from "./utils.js";

const NON_ALNUM_RE = /[^a-z0-9]+/g;
const MULTI_HYPHEN_RE = /-+/g;

export type EdgeInput = [unknown, unknown, unknown] | Record<string, unknown>;

/**
 * Convert text into a stable lowercase slug.
 */
export function slugify(text: string): string {
  const normalized = text.trim().toLowerCase().replaceAll(NON_ALNUM_RE, "-").replaceAll(MULTI_HYPHEN_RE, "-");
  const trimmed = normalized.replace(/^-+/, "").replace(/-+$/, "");
  return trimmed || "item";
}

/**
 * Mutable builder wrapper for a PlanItem.
 */
export class ItemBuilder {
  private readonly strict: boolean;
  private readonly idRegistry: Set<string>;
  private readonly itemModel: PlanItem;

  public constructor(
    title: string,
    options: Omit<PlanItemInit, "title" | "status" | "subItems"> & {
      id?: string;
      status?: string;
      strict?: boolean;
      idRegistry?: Set<string>;
      parentId?: string;
    } = {},
  ) {
    this.strict = options.strict ?? true;
    this.idRegistry = options.idRegistry ?? new Set<string>();

    const status = options.status ?? "pending";
    this.validateStatus(status);
    const itemId = this.resolveId(title, options.id, options.parentId);
    this.registerId(itemId);

    const rest: Record<string, unknown> = { ...options };
    delete rest.strict;
    delete rest.idRegistry;
    delete rest.parentId;
    const extras = isRecordLike(rest.extras) ? rest.extras : {};
    const init: PlanItemInit = {
      ...rest,
      title,
      status,
      id: itemId,
      extras: { ...extras },
    };
    this.itemModel = new PlanItem(init);
  }

  public get item(): PlanItem {
    return this.itemModel;
  }

  public addNarrative(key: string, value: unknown): void {
    if (!isRecordLike(this.itemModel.narrative)) {
      this.itemModel.narrative = {};
    }
    const narrative = this.itemModel.narrative as Record<string, unknown>;
    narrative[key] = value;
  }

  public addSubitem(
    title: string,
    options: Omit<PlanItemInit, "title" | "status" | "subItems"> & {
      id?: string;
      status?: string;
    } = {},
  ): ItemBuilder {
    const child = new ItemBuilder(title, {
      ...options,
      strict: this.strict,
      idRegistry: this.idRegistry,
      parentId: typeof this.itemModel.id === "string" ? this.itemModel.id : undefined,
    });
    this.itemModel.subItems.push(child.item);
    return child;
  }

  public toPlanItem(): PlanItem {
    return this.itemModel;
  }

  private resolveId(title: string, itemId: string | undefined, parentId: string | undefined): string | undefined {
    if (itemId !== undefined) {
      return itemId;
    }

    const slug = slugify(title);
    return parentId ? `${parentId}.${slug}` : slug;
  }

  private registerId(itemId: string | undefined): void {
    if (itemId === undefined) {
      return;
    }
    if (this.strict && this.idRegistry.has(itemId)) {
      throw new Error(`Duplicate item id: ${JSON.stringify(itemId)}`);
    }
    this.idRegistry.add(itemId);
  }

  private validateStatus(status: string): void {
    if (this.strict && !VALID_STATUSES.has(status)) {
      throw new Error(`Invalid status ${JSON.stringify(status)}; expected one of ${JSON.stringify([...VALID_STATUSES].sort())}`);
    }
  }
}

/**
 * Fluent builder for xBRIEF documents.
 */
export class PlanBuilder {
  private readonly strict: boolean;
  private readonly idRegistry = new Set<string>();
  private readonly title: string;
  private readonly status: string;
  private readonly planOptions: Record<string, unknown>;
  private readonly items: PlanItem[] = [];
  private readonly narratives: Record<string, unknown> = {};
  private readonly edges: unknown[] = [];

  public constructor(
    title: string,
    options: {
      status?: string;
      strict?: boolean;
      [key: string]: unknown;
    } = {},
  ) {
    this.strict = options.strict ?? true;
    this.title = title;
    this.status = typeof options.status === "string" ? options.status : "draft";
    this.planOptions = { ...options };
    delete this.planOptions.status;
    delete this.planOptions.strict;

    if (this.strict && !VALID_STATUSES.has(this.status)) {
      throw new Error(
        `Invalid status ${JSON.stringify(this.status)}; expected one of ${JSON.stringify([...VALID_STATUSES].sort())}`,
      );
    }
  }

  public addNarrative(key: string, value: unknown): void {
    this.narratives[key] = value;
  }

  public addItem(
    title: string,
    options: Omit<PlanItemInit, "title" | "status" | "subItems"> & {
      id?: string;
      status?: string;
    } = {},
  ): ItemBuilder {
    const item = new ItemBuilder(title, {
      ...options,
      strict: this.strict,
      idRegistry: this.idRegistry,
    });
    this.items.push(item.item);
    return item;
  }

  public addEdgesFrom(edges: Iterable<EdgeInput>): void {
    for (const edge of edges) {
      const normalized = this.normalizeEdge(edge);
      if (this.strict && isRecordLike(normalized)) {
        this.validateEdgeIds(normalized);
      }
      this.edges.push(normalized);
    }
  }

  public toDocument(): XBriefDocument {
    const plan = new Plan({
      title: this.title,
      status: this.status,
      items: [...this.items],
      narratives: Object.keys(this.narratives).length > 0 ? { ...this.narratives } : undefined,
      edges: this.edges.length > 0 ? [...this.edges] : undefined,
      ...this.planOptions,
    });
    return new XBriefDocument({
      xbriefInfo: { version: "0.8" },
      plan,
    });
  }

  private normalizeEdge(edge: EdgeInput): unknown {
    if (Array.isArray(edge) && edge.length === 3) {
      return {
        from: edge[0],
        to: edge[1],
        type: edge[2],
      };
    }
    if (isRecordLike(edge)) {
      return { ...edge };
    }
    if (this.strict) {
      throw new Error("Edge entries must be 3-tuples or dicts");
    }
    return edge;
  }

  private validateEdgeIds(edge: Record<string, unknown>): void {
    const fromId = edge.from;
    const toId = edge.to;
    const edgeType = edge.type;

    if (typeof fromId !== "string" || typeof toId !== "string" || typeof edgeType !== "string") {
      throw new Error("Edge entries must contain string 'from', 'to', and 'type' values");
    }
    if (!this.idRegistry.has(fromId)) {
      throw new Error(`Edge references unknown source id: ${JSON.stringify(fromId)}`);
    }
    if (!this.idRegistry.has(toId)) {
      throw new Error(`Edge references unknown target id: ${JSON.stringify(toId)}`);
    }
  }
}

/**
 * Create a minimal xBRIEF todo document from strings or PlanItem objects.
 */
export function quickTodo(
  title: string,
  items: Iterable<string | PlanItem>,
  options: {
    status?: string;
    [key: string]: unknown;
  } = {},
): XBriefDocument {
  const planItems: PlanItem[] = [];
  for (const item of items) {
    if (item instanceof PlanItem) {
      planItems.push(item);
    } else if (typeof item === "string") {
      planItems.push(new PlanItem({ title: item, status: "pending" }));
    } else {
      throw new TypeError("quick_todo items must be strings or PlanItem instances");
    }
  }

  const { status = "running", ...planOptions } = options;
  return new XBriefDocument({
    xbriefInfo: { version: "0.8" },
    plan: new Plan({
      title,
      status,
      items: planItems,
      ...planOptions,
    }),
  });
}

/**
 * Create a xBRIEF document from PlanItem objects.
 */
export function fromItems(
  title: string,
  items: Iterable<PlanItem>,
  options: {
    status?: string;
    [key: string]: unknown;
  } = {},
): XBriefDocument {
  const planItems = [...items];
  for (const item of planItems) {
    if (!(item instanceof PlanItem)) {
      throw new TypeError("from_items items must be PlanItem instances");
    }
  }

  const { status = "running", ...planOptions } = options;
  return new XBriefDocument({
    xbriefInfo: { version: "0.8" },
    plan: new Plan({
      title,
      status,
      items: planItems,
      ...planOptions,
    }),
  });
}
