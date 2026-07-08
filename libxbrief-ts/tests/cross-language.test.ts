import { execFileSync } from "node:child_process";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

import { describe, expect, test } from "vitest";

import { PlanItem, dumps, loads, quickTodo } from "../src/index.js";

const here = dirname(fileURLToPath(import.meta.url));
const repoRoot = join(here, "..", "..");

function runPython(script: string, input?: string): string {
  return execFileSync("uv", ["run", "python", "-c", script], {
    cwd: repoRoot,
    env: {
      ...process.env,
      PYTHONPATH: repoRoot,
    },
    input,
    encoding: "utf8",
  });
}

describe("cross-language compatibility", () => {
  test("loads Python-generated JSON", () => {
    const script = [
      "from libxbrief import quick_todo, dumps",
      "doc = quick_todo('Sync', ['one', 'two'])",
      "print(dumps(doc), end='')",
    ].join("\n");

    const output = runPython(script);

    const document = loads(output, { strict: true });
    expect(document.xBRIEFInfo).toEqual({ version: "0.8" });
    expect((document.plan as { items: unknown[] }).items).toHaveLength(2);
  });

  test("Python loads TypeScript-generated JSON", () => {
    const text = dumps(quickTodo("Sync", ["one", PlanItem.completed("two", { id: "two" })]));
    const script = [
      "import json, sys",
      "from libxbrief import loads",
      "doc = loads(sys.stdin.read(), strict=True)",
      "print(json.dumps({'version': doc['xBRIEFInfo']['version'], 'count': len(doc['plan']['items'])}), end='')",
    ].join("\n");

    const output = runPython(script, text);

    expect(JSON.parse(output)).toEqual({ version: "0.8", count: 2 });
  });
});
