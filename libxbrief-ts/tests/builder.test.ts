import { describe, expect, test } from "vitest";

import { PlanItem, PlanBuilder, fromItems, quickTodo, slugify } from "../src/index.js";

describe("builder api", () => {
  test("slugify mirrors python behavior", () => {
    expect(slugify("  Hello, World!  ")).toBe("hello-world");
    expect(slugify("***")).toBe("item");
  });

  test("builds nested documents with generated hierarchical ids", () => {
    const builder = new PlanBuilder("Ship release", { status: "running" });
    builder.addNarrative("Proposal", "Ship in phases");
    const prep = builder.addItem("Prep work");
    prep.addNarrative("Notes", "Gather dependencies");
    prep.addSubitem("Write checklist");
    builder.addItem("Deploy");
    builder.addEdgesFrom([
      ["prep-work", "deploy", "blocks"],
    ]);

    const document = builder.toDocument();

    expect(document.plan.items[0]?.id).toBe("prep-work");
    expect(document.plan.items[0]?.subItems[0]?.id).toBe("prep-work.write-checklist");
    expect(document.plan.edges).toEqual([{ from: "prep-work", to: "deploy", type: "blocks" }]);
  });

  test("validates duplicate ids in strict mode", () => {
    const builder = new PlanBuilder("Plan");
    builder.addItem("Alpha", { id: "alpha" });

    expect(() => builder.addItem("Another", { id: "alpha" })).toThrow(/Duplicate item id/);
  });

  test("quickTodo and fromItems preserve provided PlanItem instances", () => {
    const done = PlanItem.completed("Done", { id: "done" });
    const todo = quickTodo("Today", ["First", done]);
    const from = fromItems("Imported", [done]);

    expect(todo.plan.items[1]).toBe(done);
    expect(from.plan.items[0]).toBe(done);
  });
});
