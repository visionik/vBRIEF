import { describe, expect, test } from "vitest";

import {
  ISSUE_DANGLING_EDGE_REF,
  ISSUE_INVALID_DOCUMENT_TYPE,
  ISSUE_INVALID_EDGE_STRUCTURE,
  ISSUE_INVALID_ID_FORMAT,
  ISSUE_INVALID_ITEM_TYPE,
  ISSUE_INVALID_PLAN_FIELD_TYPE,
  ISSUE_INVALID_PLANREF,
  ISSUE_INVALID_ROOT_FIELD_TYPE,
  ISSUE_MISSING_ROOT_FIELD,
  Issue,
  PlanBuilder,
  PlanItem,
  PlanItemSchema,
  ValidationError,
  ValidationReport,
  XBriefDocument,
  XBriefDocumentSchema,
  fromItems,
  loads,
  parseJson,
  quickTodo,
  validate,
  validatePlanDAG,
} from "../src/index.js";
import { coerceToDict } from "../src/io.js";

describe("coverage-oriented negative paths", () => {
  test("parseJson rejects non-object payloads", () => {
    expect(() => parseJson("[]")).toThrow(/must be an object/);
  });

  test("loads strict raises on invalid documents", () => {
    expect(() => loads('{"xBRIEFInfo":{"version":"0.4"},"plan":{"title":"x","status":"draft","items":[]}}', { strict: true })).toThrow(
      ValidationError,
    );
  });

  test("dag validation cleanly handles empty and acyclic graphs", () => {
    const emptyReport = new ValidationReport();
    const acyclicReport = new ValidationReport();

    validatePlanDAG({ items: [], edges: [] }, emptyReport);
    validatePlanDAG(
      {
        items: [
          { id: "a", title: "A", status: "pending" },
          { id: "b", title: "B", status: "pending" },
        ],
        edges: [{ from: "a", to: "b", type: "blocks" }],
      },
      acyclicReport,
    );

    expect(emptyReport.isValid).toBe(true);
    expect(acyclicReport.isValid).toBe(true);
  });

  test("coerceToDict rejects unsupported values", () => {
    expect(() => coerceToDict(42, false)).toThrow(/mapping or provide to_dict/);
  });

  test("validation handles non-object documents and missing root fields", () => {
    const invalidType = validate("bad");
    const missingRoots = validate({});

    expect(invalidType.errors).toEqual(
      expect.arrayContaining([expect.objectContaining({ code: ISSUE_INVALID_DOCUMENT_TYPE })]),
    );
    expect(missingRoots.errors).toEqual(
      expect.arrayContaining([
        expect.objectContaining({ code: ISSUE_MISSING_ROOT_FIELD, path: "xBRIEFInfo" }),
        expect.objectContaining({ code: ISSUE_MISSING_ROOT_FIELD, path: "plan" }),
      ]),
    );
  });

  test("validation reports invalid root and plan field types", () => {
    const report = validate({
      xBRIEFInfo: [],
      plan: {
        title: "Plan",
        status: "draft",
        items: {},
      },
    });

    expect(report.errors).toEqual(
      expect.arrayContaining([
        expect.objectContaining({ code: ISSUE_INVALID_ROOT_FIELD_TYPE, path: "xBRIEFInfo" }),
        expect.objectContaining({ code: ISSUE_INVALID_PLAN_FIELD_TYPE, path: "plan.items" }),
      ]),
    );
  });


  test("validation reports invalid plan root type and detailed item failures", () => {
    const invalidPlan = validate({
      xBRIEFInfo: { version: "0.8" },
      plan: "bad",
    });
    const invalidItems = validate({
      xBRIEFInfo: { version: "0.8" },
      plan: {
        id: "bad:id",
        title: "Plan",
        status: "draft",
        items: ["bad-item", { id: "also:bad", planRef: "ftp://bad" }],
      },
    });

    expect(invalidPlan.errors).toEqual(
      expect.arrayContaining([expect.objectContaining({ code: ISSUE_INVALID_ROOT_FIELD_TYPE, path: "plan" })]),
    );
    expect(invalidItems.errors).toEqual(
      expect.arrayContaining([
        expect.objectContaining({ code: ISSUE_INVALID_ID_FORMAT, path: "plan.id" }),
        expect.objectContaining({ code: ISSUE_INVALID_ITEM_TYPE, path: "plan.items[0]" }),
        expect.objectContaining({ code: ISSUE_INVALID_ID_FORMAT, path: "plan.items[1].id" }),
        expect.objectContaining({ code: ISSUE_INVALID_PLANREF, path: "plan.items[1].planRef" }),
      ]),
    );
  });
  test("dag validation reports malformed and dangling edges", () => {
    const report = new ValidationReport();
    validatePlanDAG(
      {
        items: [{ id: "a", title: "A", status: "pending" }, { title: "No id", status: "pending" }],
        edges: [{ from: "a", to: "missing", type: "blocks" }, { from: 1, to: "a" }, "bad-edge"],
      },
      report,
    );

    expect(report.errors).toEqual(
      expect.arrayContaining([
        expect.objectContaining({ code: ISSUE_DANGLING_EDGE_REF, path: "plan.edges[0].to" }),
        expect.objectContaining({ code: ISSUE_INVALID_EDGE_STRUCTURE, path: "plan.edges[1].from" }),
        expect.objectContaining({ code: ISSUE_INVALID_EDGE_STRUCTURE, path: "plan.edges[2]" }),
      ]),
    );
  });

  test("builder rejects invalid statuses and malformed edges in strict mode", () => {
    expect(() => new PlanBuilder("Bad", { status: "nope" })).toThrow(/Invalid status/);

    const builder = new PlanBuilder("Plan");
    builder.addItem("A", { id: "a" });
    builder.addItem("B", { id: "b" });

    expect(() => builder.addEdgesFrom([{ from: "a", to: "b" }])).toThrow(/string 'from', 'to', and 'type'/);
    expect(() => builder.addEdgesFrom([["a", "missing", "blocks"]])).toThrow(/unknown target id/);
  });

  test("builder helper type errors are surfaced", () => {
    expect(() => quickTodo("Today", ["one", 2 as unknown as PlanItem])).toThrow(/quick_todo/);
    expect(() => fromItems("Imported", [{} as unknown as PlanItem])).toThrow(/from_items/);
  });

  test("non-strict builders accept otherwise-invalid edges", () => {
    const builder = new PlanBuilder("Loose", { strict: false, status: "made-up" });
    builder.addItem("A");
    builder.addEdgesFrom([123 as unknown as Record<string, unknown>]);

    expect(builder.toDocument().plan.edges).toEqual([123]);
  });

  test("validation report warning and extend paths work", () => {
    const report = new ValidationReport();
    report.addWarning("warn", "plan", "warning");
    report.extend([
      new Issue({ code: "error", path: "$", message: "bad", severity: "error" }),
      new Issue({ code: "warn2", path: "$", message: "warn", severity: "warning" }),
    ]);

    expect(report.warnings).toHaveLength(2);
    expect(report.errors).toHaveLength(1);
  });

  test("validation error summary handles empty and long reports", () => {
    const emptyReport = new ValidationReport();
    const longReport = new ValidationReport();
    longReport.addError("a", "a", "one");
    longReport.addError("b", "b", "two");
    longReport.addError("c", "c", "three");
    longReport.addError("d", "d", "four");

    expect(new ValidationError(emptyReport).message).toBe("validation failed");
    expect(new ValidationError(longReport).message).toContain("4 total errors");
  });

  test("schema parsing handles nested items and passthrough fields", () => {
    const item = PlanItemSchema.parse({
      title: "Parent",
      status: "pending",
      extension: true,
      subItems: [{ title: "Child", status: "pending", extra: "x" }],
    });
    const document = XBriefDocumentSchema.parse({
      xBRIEFInfo: { version: "0.8", profile: "custom" },
      plan: {
        title: "Plan",
        status: "draft",
        items: [item],
        workflow: { enabled: true },
      },
      rootExtra: 1,
    });

    expect(item.extension).toBe(true);
    expect(document.rootExtra).toBe(1);
    expect(document.plan.workflow).toEqual({ enabled: true });
  });

  test("model helpers cover lenient parsing and JSON methods", () => {
    const document = XBriefDocument.fromDict({
      xBRIEFInfo: { version: "0.8" },
      plan: {
        title: "Plan",
        status: "draft",
        items: [{ title: "One", status: "pending", subItems: [{ title: "Two", status: "running" }, "skip"] }],
      },
    });

    const json = document.toJson({ preserveFormat: true });
    expect(json).toContain("\"xBRIEFInfo\"");
    expect(document.plan.items[0]?.subItems).toHaveLength(1);
    expect(XBriefDocument.fromJson(json).plan.title).toBe("Plan");
  });

  test("model factories and lenient fallbacks cover optional branches", () => {
    expect(PlanItem.running("Run").status).toBe("running");
    expect(PlanItem.blocked("Blocked").status).toBe("blocked");
    expect(PlanItem.cancelled("Cancelled").status).toBe("cancelled");
    expect(PlanItem.draft("Draft").status).toBe("draft");

    const item = PlanItem.fromDict("bad-input");
    const document = XBriefDocument.fromDict({
      xBRIEFInfo: "bad",
      plan: [],
    });

    expect(item.title).toBe("");
    expect(document.xbriefInfo).toEqual({});
    expect(document.plan.items).toEqual([]);
  });
});
