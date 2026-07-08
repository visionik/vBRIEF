import { readFileSync, readdirSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

import { describe, expect, test } from "vitest";

import { ISSUE_DAG_CYCLE, ISSUE_INVALID_ID_FORMAT, loads, validate } from "../src/index.js";

const here = dirname(fileURLToPath(import.meta.url));
const repoRoot = join(here, "..", "..");
const examplesDir = join(repoRoot, "examples");
const fixtureFiles = readdirSync(examplesDir).filter((name: string) => name.endsWith(".xbrief.json")).sort();
const knownInvalidFixtures = new Map<string, string>([
  ["invalid-cycle.xbrief.json", ISSUE_DAG_CYCLE],
  ["workflow-invoice-processing.xbrief.json", ISSUE_INVALID_ID_FORMAT],
]);

describe("shared fixtures", () => {
  for (const name of fixtureFiles) {
    test(`parses fixture ${name}`, () => {
      const text = readFileSync(join(examplesDir, name), "utf8");
      const document = loads(text);
      const report = validate(document, { dag: true });
      const expectedCode = knownInvalidFixtures.get(name);
      if (expectedCode !== undefined) {
        expect(report.errors).toEqual(
          expect.arrayContaining([expect.objectContaining({ code: expectedCode })]),
        );
      } else {
        expect(report.isValid).toBe(true);
      }
    });
  }
});
