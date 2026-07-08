import {
  DOCUMENT_FIELD_ORDER,
  PLAN_FIELD_ORDER,
  PLAN_ITEM_FIELD_ORDER,
} from "./compat.js";
import { ValidationError } from "./errors.js";
import type { ValidationReport } from "./issues.js";
import { dumpsJson, parseJson } from "./json-codec.js";
import { validateDocument } from "./validation.js";
import { entriesExcept, isRecordLike, mergeValues } from "./utils.js";

type OptionalUnknown = unknown;

export interface PlanItemInit extends Record<string, unknown> {
  title?: string;
  status?: string;
  id?: unknown;
  uid?: unknown;
  type?: unknown;
  summary?: unknown;
  narrative?: unknown;
  items?: PlanItem[];
  subItems?: PlanItem[];
  planRef?: unknown;
  planRefs?: unknown;
  tags?: unknown;
  metadata?: unknown;
  created?: unknown;
  updated?: unknown;
  completed?: unknown;
  priority?: unknown;
  dueDate?: unknown;
  startDate?: unknown;
  endDate?: unknown;
  percentComplete?: unknown;
  participants?: unknown;
  location?: unknown;
  uris?: unknown;
  recurrence?: unknown;
  reminders?: unknown;
  classification?: unknown;
  relatedComments?: unknown;
  timezone?: unknown;
  sequence?: unknown;
  lastModifiedBy?: unknown;
  lockedBy?: unknown;
  extras?: Record<string, unknown>;
  _fieldOrder?: string[];
}

export interface PlanInit extends Record<string, unknown> {
  title?: string;
  status?: string;
  items?: PlanItem[];
  id?: unknown;
  uid?: unknown;
  narratives?: unknown;
  edges?: unknown;
  tags?: unknown;
  metadata?: unknown;
  architecture?: unknown;
  created?: unknown;
  updated?: unknown;
  author?: unknown;
  reviewers?: unknown;
  uris?: unknown;
  references?: unknown;
  timezone?: unknown;
  agent?: unknown;
  lastModifiedBy?: unknown;
  changeLog?: unknown;
  sequence?: unknown;
  fork?: unknown;
  extras?: Record<string, unknown>;
  _fieldOrder?: string[];
}

export interface XBriefDocumentInit extends Record<string, unknown> {
  xbriefInfo?: Record<string, unknown>;
  plan?: Plan;
  extras?: Record<string, unknown>;
  _fieldOrder?: string[];
}

export interface DictOptions {
  preserveOrder?: boolean;
}

export interface JsonOptions {
  canonical?: boolean;
  preserveFormat?: boolean;
}

export interface ValidationOptions {
  strict?: boolean;
  dag?: boolean;
}

/**
 * Plan item model with unknown-field preservation.
 */
export class PlanItem {
  public title: string;
  public status: string;
  public id: OptionalUnknown;
  public uid: OptionalUnknown;
  public type: OptionalUnknown;
  public summary: OptionalUnknown;
  public narrative: OptionalUnknown;
  public items: PlanItem[];
  public subItems: PlanItem[];
  public planRef: OptionalUnknown;
  public planRefs: OptionalUnknown;
  public tags: OptionalUnknown;
  public metadata: OptionalUnknown;
  public created: OptionalUnknown;
  public updated: OptionalUnknown;
  public completed: OptionalUnknown;
  public priority: OptionalUnknown;
  public dueDate: OptionalUnknown;
  public startDate: OptionalUnknown;
  public endDate: OptionalUnknown;
  public percentComplete: OptionalUnknown;
  public participants: OptionalUnknown;
  public location: OptionalUnknown;
  public uris: OptionalUnknown;
  public recurrence: OptionalUnknown;
  public reminders: OptionalUnknown;
  public classification: OptionalUnknown;
  public relatedComments: OptionalUnknown;
  public timezone: OptionalUnknown;
  public sequence: OptionalUnknown;
  public lastModifiedBy: OptionalUnknown;
  public lockedBy: OptionalUnknown;
  public extras: Record<string, unknown>;
  public _fieldOrder: string[];

  public constructor(init: PlanItemInit = {}) {
    this.title = typeof init.title === "string" ? init.title : "";
    this.status = typeof init.status === "string" ? init.status : "";
    this.id = init.id;
    this.uid = init.uid;
    this.type = init.type;
    this.summary = init.summary;
    this.narrative = init.narrative;
    this.items = Array.isArray(init.items) ? [...init.items] : [];
    this.subItems = Array.isArray(init.subItems) ? [...init.subItems] : [];
    this.planRef = init.planRef;
    this.planRefs = init.planRefs;
    this.tags = init.tags;
    this.metadata = init.metadata;
    this.created = init.created;
    this.updated = init.updated;
    this.completed = init.completed;
    this.priority = init.priority;
    this.dueDate = init.dueDate;
    this.startDate = init.startDate;
    this.endDate = init.endDate;
    this.percentComplete = init.percentComplete;
    this.participants = init.participants;
    this.location = init.location;
    this.uris = init.uris;
    this.recurrence = init.recurrence;
    this.reminders = init.reminders;
    this.classification = init.classification;
    this.relatedComments = init.relatedComments;
    this.timezone = init.timezone;
    this.sequence = init.sequence;
    this.lastModifiedBy = init.lastModifiedBy;
    this.lockedBy = init.lockedBy;
    this.extras = { ...(init.extras ?? {}) };
    this._fieldOrder = [...(init._fieldOrder ?? [])];
  }

  public static pending(title: string, init: Omit<PlanItemInit, "title" | "status"> = {}): PlanItem {
    return new PlanItem({ ...init, title, status: "pending" });
  }

  public static running(title: string, init: Omit<PlanItemInit, "title" | "status"> = {}): PlanItem {
    return new PlanItem({ ...init, title, status: "running" });
  }

  public static completed(title: string, init: Omit<PlanItemInit, "title" | "status"> = {}): PlanItem {
    return new PlanItem({ ...init, title, status: "completed" });
  }

  public static blocked(title: string, init: Omit<PlanItemInit, "title" | "status"> = {}): PlanItem {
    return new PlanItem({ ...init, title, status: "blocked" });
  }

  public static cancelled(title: string, init: Omit<PlanItemInit, "title" | "status"> = {}): PlanItem {
    return new PlanItem({ ...init, title, status: "cancelled" });
  }

  public static draft(title: string, init: Omit<PlanItemInit, "title" | "status"> = {}): PlanItem {
    return new PlanItem({ ...init, title, status: "draft" });
  }

  public static fromDict(data: unknown): PlanItem {
    const mapping = isRecordLike(data) ? data : {};
    const extras = entriesExcept(mapping, PLAN_ITEM_FIELD_ORDER);
    const item = new PlanItem({
      id: mapping.id,
      uid: mapping.uid,
      type: mapping.type,
      summary: mapping.summary,
      title: typeof mapping.title === "string" ? mapping.title : "",
      status: typeof mapping.status === "string" ? mapping.status : "",
      narrative: mapping.narrative,
      planRef: mapping.planRef,
      planRefs: mapping.planRefs,
      tags: mapping.tags,
      metadata: mapping.metadata,
      created: mapping.created,
      updated: mapping.updated,
      completed: mapping.completed,
      priority: mapping.priority,
      dueDate: mapping.dueDate,
      startDate: mapping.startDate,
      endDate: mapping.endDate,
      percentComplete: mapping.percentComplete,
      participants: mapping.participants,
      location: mapping.location,
      uris: mapping.uris,
      recurrence: mapping.recurrence,
      reminders: mapping.reminders,
      classification: mapping.classification,
      relatedComments: mapping.relatedComments,
      timezone: mapping.timezone,
      sequence: mapping.sequence,
      lastModifiedBy: mapping.lastModifiedBy,
      lockedBy: mapping.lockedBy,
      extras,
      _fieldOrder: Object.keys(mapping),
    });

    // items and subItems assigned post-construction to avoid default_factory conflict
    const nestedItems = mapping.items;
    if (Array.isArray(nestedItems)) {
      item.items = nestedItems.filter(isRecordLike).map((entry) => PlanItem.fromDict(entry));
    }

    const subItems = mapping.subItems;
    if (Array.isArray(subItems)) {
      item.subItems = subItems.filter(isRecordLike).map((entry) => PlanItem.fromDict(entry));
    }

    return item;
  }

  public toDict(options: DictOptions = {}): Record<string, unknown> {
    const preserveOrder = options.preserveOrder ?? false;
    const known = knownItemValues(this, preserveOrder);
    return mergeValues(known, this.extras, this._fieldOrder, preserveOrder);
  }
}

/**
 * Plan model with nested items and unknown-field preservation.
 */
export class Plan {
  public title: string;
  public status: string;
  public items: PlanItem[];
  public id: OptionalUnknown;
  public uid: OptionalUnknown;
  public narratives: OptionalUnknown;
  public edges: OptionalUnknown;
  public tags: OptionalUnknown;
  public metadata: OptionalUnknown;
  public architecture: OptionalUnknown;
  public created: OptionalUnknown;
  public updated: OptionalUnknown;
  public author: OptionalUnknown;
  public reviewers: OptionalUnknown;
  public uris: OptionalUnknown;
  public references: OptionalUnknown;
  public timezone: OptionalUnknown;
  public agent: OptionalUnknown;
  public lastModifiedBy: OptionalUnknown;
  public changeLog: OptionalUnknown;
  public sequence: OptionalUnknown;
  public fork: OptionalUnknown;
  public extras: Record<string, unknown>;
  public _fieldOrder: string[];

  public constructor(init: PlanInit = {}) {
    this.title = typeof init.title === "string" ? init.title : "";
    this.status = typeof init.status === "string" ? init.status : "";
    this.items = Array.isArray(init.items) ? [...init.items] : [];
    this.id = init.id;
    this.uid = init.uid;
    this.narratives = init.narratives;
    this.edges = init.edges;
    this.tags = init.tags;
    this.metadata = init.metadata;
    this.architecture = init.architecture;
    this.created = init.created;
    this.updated = init.updated;
    this.author = init.author;
    this.reviewers = init.reviewers;
    this.uris = init.uris;
    this.references = init.references;
    this.timezone = init.timezone;
    this.agent = init.agent;
    this.lastModifiedBy = init.lastModifiedBy;
    this.changeLog = init.changeLog;
    this.sequence = init.sequence;
    this.fork = init.fork;
    this.extras = { ...(init.extras ?? {}) };
    this._fieldOrder = [...(init._fieldOrder ?? [])];
  }

  public static fromDict(data: unknown): Plan {
    const mapping = isRecordLike(data) ? data : {};
    const extras = entriesExcept(mapping, PLAN_FIELD_ORDER);
    const plan = new Plan({
      id: mapping.id,
      uid: mapping.uid,
      title: typeof mapping.title === "string" ? mapping.title : "",
      status: typeof mapping.status === "string" ? mapping.status : "",
      narratives: mapping.narratives,
      edges: mapping.edges,
      tags: mapping.tags,
      metadata: mapping.metadata,
      architecture: mapping.architecture,
      created: mapping.created,
      updated: mapping.updated,
      author: mapping.author,
      reviewers: mapping.reviewers,
      uris: mapping.uris,
      references: mapping.references,
      timezone: mapping.timezone,
      agent: mapping.agent,
      lastModifiedBy: mapping.lastModifiedBy,
      changeLog: mapping.changeLog,
      sequence: mapping.sequence,
      fork: mapping.fork,
      extras,
      _fieldOrder: Object.keys(mapping),
    });

    const items = mapping.items;
    if (Array.isArray(items)) {
      plan.items = items.filter(isRecordLike).map((entry) => PlanItem.fromDict(entry));
    }

    return plan;
  }

  public toDict(options: DictOptions = {}): Record<string, unknown> {
    const preserveOrder = options.preserveOrder ?? false;
    const known = knownPlanValues(this, preserveOrder);
    return mergeValues(known, this.extras, this._fieldOrder, preserveOrder);
  }
}

/**
 * Root xBRIEF document model.
 */
export class XBriefDocument {
  public xbriefInfo: Record<string, unknown>;
  public plan: Plan;
  public extras: Record<string, unknown>;
  public _fieldOrder: string[];

  public constructor(init: XBriefDocumentInit = {}) {
    this.xbriefInfo = { ...(init.xbriefInfo ?? {}) };
    this.plan = init.plan ?? new Plan();
    this.extras = { ...(init.extras ?? {}) };
    this._fieldOrder = [...(init._fieldOrder ?? [])];
  }

  public static fromDict(data: unknown, options: ValidationOptions = {}): XBriefDocument {
    const mapping = isRecordLike(data) ? data : {};
    const extras = entriesExcept(mapping, DOCUMENT_FIELD_ORDER);
    const rawInfo = isRecordLike(mapping.xBRIEFInfo) ? mapping.xBRIEFInfo : {};
    const rawPlan = isRecordLike(mapping.plan) ? mapping.plan : {};
    const document = new XBriefDocument({
      xbriefInfo: { ...rawInfo },
      plan: Plan.fromDict(rawPlan),
      extras,
      _fieldOrder: Object.keys(mapping),
    });

    if (options.strict) {
      raiseIfInvalid(document.validate({ dag: options.dag ?? false }));
    }

    return document;
  }

  public static fromJson(text: string, options: ValidationOptions = {}): XBriefDocument {
    return XBriefDocument.fromDict(parseJson(text), options);
  }

  public toDict(options: DictOptions = {}): Record<string, unknown> {
    const preserveOrder = options.preserveOrder ?? false;
    const known = {
      xBRIEFInfo: this.xbriefInfo,
      plan: this.plan.toDict({ preserveOrder }),
    };
    return mergeValues(known, this.extras, this._fieldOrder, preserveOrder);
  }

  public toJson(options: JsonOptions = {}): string {
    const canonical = options.canonical ?? true;
    const preserveFormat = options.preserveFormat ?? false;
    const payload = this.toDict({ preserveOrder: preserveFormat });
    return dumpsJson(payload, { canonical, preserveFormat });
  }

  public toJSON(): Record<string, unknown> {
    return this.toDict();
  }

  public validate(options: { dag?: boolean } = {}): ValidationReport {
    return validateDocument(this, { dag: options.dag ?? false });
  }
}

function knownItemValues(item: PlanItem, preserveOrder: boolean): Record<string, unknown> {
  const values: Record<string, unknown> = {
    title: item.title,
    status: item.status,
  };
  const optionalPairs: Record<string, unknown> = {
    id: item.id,
    uid: item.uid,
    type: item.type,
    summary: item.summary,
    narrative: item.narrative,
    items:
      item.items.length > 0
        ? item.items.map((child) => child.toDict({ preserveOrder }))
        : undefined,
    subItems:
      item.subItems.length > 0
        ? item.subItems.map((subItem) => subItem.toDict({ preserveOrder }))
        : undefined,
    planRef: item.planRef,
    planRefs: item.planRefs,
    tags: item.tags,
    metadata: item.metadata,
    created: item.created,
    updated: item.updated,
    completed: item.completed,
    priority: item.priority,
    dueDate: item.dueDate,
    startDate: item.startDate,
    endDate: item.endDate,
    percentComplete: item.percentComplete,
    participants: item.participants,
    location: item.location,
    uris: item.uris,
    recurrence: item.recurrence,
    reminders: item.reminders,
    classification: item.classification,
    relatedComments: item.relatedComments,
    timezone: item.timezone,
    sequence: item.sequence,
    lastModifiedBy: item.lastModifiedBy,
    lockedBy: item.lockedBy,
  };

  for (const [key, value] of Object.entries(optionalPairs)) {
    if (value !== undefined && value !== null) {
      values[key] = value;
    }
  }

  return values;
}

function knownPlanValues(plan: Plan, preserveOrder: boolean): Record<string, unknown> {
  const values: Record<string, unknown> = {
    title: plan.title,
    status: plan.status,
    items: plan.items.map((item) => item.toDict({ preserveOrder })),
  };
  const optionalPairs: Record<string, unknown> = {
    id: plan.id,
    uid: plan.uid,
    narratives: plan.narratives,
    edges: plan.edges,
    tags: plan.tags,
    metadata: plan.metadata,
    architecture: plan.architecture,
    created: plan.created,
    updated: plan.updated,
    author: plan.author,
    reviewers: plan.reviewers,
    uris: plan.uris,
    references: plan.references,
    timezone: plan.timezone,
    agent: plan.agent,
    lastModifiedBy: plan.lastModifiedBy,
    changeLog: plan.changeLog,
    sequence: plan.sequence,
    fork: plan.fork,
  };

  for (const [key, value] of Object.entries(optionalPairs)) {
    if (value !== undefined && value !== null) {
      values[key] = value;
    }
  }

  return values;
}

function raiseIfInvalid(report: ValidationReport): void {
  if (!report.isValid) {
    throw new ValidationError(report);
  }
}
