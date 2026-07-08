import { mkdtemp, readFile, rm } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";

import { afterEach, describe, expect, test } from "vitest";

import { PlanBuilder, dumps, loads } from "../src/index.js";
import { dumpFile, loadFile } from "../src/node.js";

describe("io", () => {
  let tempDir: string | undefined;

  afterEach(async () => {
    if (tempDir !== undefined) {
      await rm(tempDir, { recursive: true, force: true });
      tempDir = undefined;
    }
  });

  test("round-trips with canonical and preserve-format modes", () => {
    const input = {
      zeta: 1,
      alpha: 2,
      xBRIEFInfo: { version: "0.8" },
      plan: { title: "Plan", status: "draft", items: [] },
    };

    const canonical = dumps(input);
    const preserved = dumps(input, { preserveFormat: true });

    expect(canonical.indexOf("\"alpha\"")).toBeLessThan(canonical.indexOf("\"zeta\""));
    expect(preserved.indexOf("\"zeta\"")).toBeLessThan(preserved.indexOf("\"alpha\""));
    expect(loads(canonical, { strict: true }).plan).toBeDefined();
  });

  test("supports node file io helpers", async () => {
    tempDir = await mkdtemp(join(tmpdir(), "libxbrief-ts-"));
    const path = join(tempDir, "sample.json");
    const document = new PlanBuilder("Plan").toDocument();

    await dumpFile(document, path);

    const reloaded = await loadFile(path, { strict: true });
    const text = await readFile(path, "utf8");

    expect(reloaded.plan).toEqual({
      title: "Plan",
      status: "draft",
      items: [],
    });
    expect(text.endsWith("\n")).toBe(true);
  });
});
