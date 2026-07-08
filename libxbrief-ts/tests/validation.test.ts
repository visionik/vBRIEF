import { describe, expect, test } from "vitest";

import {
  ISSUE_DAG_CYCLE,
  ISSUE_DUPLICATE_ITEM_ID,
  ISSUE_INVALID_ITEM_STATUS,
  ISSUE_INVALID_PLANREF,
  ISSUE_INVALID_SUBITEMS_TYPE,
  ISSUE_INVALID_VERSION,
  ValidationError,
  XBriefDocument,
  validate,
} from "../src/index.js";

describe("validation", () => {
  test("reports structural validation issues with stable codes and paths", () => {
    const report = validate({
      xBRIEFInfo: { version: "0.4" },
      plan: {
        title: "Plan",
        status: "bogus",
        items: [
          {
            id: "alpha",
            title: "First",
            status: "pending",
            subItems: "oops",
          },
          {
            id: "alpha",
            title: "Second",
            status: "bad",
            planRef: "ftp://invalid",
          },
        ],
      },
    });

    expect(report.isValid).toBe(false);
    expect(report.errors).toEqual(
      expect.arrayContaining([
        expect.objectContaining({ code: ISSUE_INVALID_VERSION, path: "xBRIEFInfo.version" }),
        expect.objectContaining({ code: ISSUE_INVALID_ITEM_STATUS, path: "plan.items[1].status" }),
        expect.objectContaining({ code: ISSUE_DUPLICATE_ITEM_ID, path: "plan.items[1].id" }),
        expect.objectContaining({ code: ISSUE_INVALID_PLANREF, path: "plan.items[1].planRef" }),
        expect.objectContaining({ code: ISSUE_INVALID_SUBITEMS_TYPE, path: "plan.items[0].subItems" }),
      ]),
    );
  });

  test("supports DAG validation with cycle detection", () => {
    const report = validate(
      {
        xBRIEFInfo: { version: "0.8" },
        plan: {
          title: "Plan",
          status: "running",
          items: [
            { id: "a", title: "A", status: "pending" },
            { id: "b", title: "B", status: "pending" },
          ],
          edges: [
            { from: "a", to: "b", type: "blocks" },
            { from: "b", to: "a", type: "blocks" },
          ],
        },
      },
      { dag: true },
    );

    expect(report.errors).toEqual(
      expect.arrayContaining([
        expect.objectContaining({
          code: ISSUE_DAG_CYCLE,
          path: "plan.edges",
        }),
      ]),
    );
  });

  test("strict document creation raises ValidationError", () => {
    expect(() =>
      XBriefDocument.fromDict(
        {
          xBRIEFInfo: { version: "0.4" },
          plan: { title: "Plan", status: "draft", items: [] },
        },
        { strict: true },
      ),
    ).toThrow(ValidationError);
  });
});
