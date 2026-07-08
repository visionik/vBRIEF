import { XBriefDocument, dumpFile, loadFile, quickTodo } from "../src/node.js";

const inputUrl = new URL("../../examples/minimal-plan.xbrief.json", import.meta.url);
const outputUrl = new URL("./release-prep.xbrief.json", import.meta.url);

const existing = XBriefDocument.fromDict(await loadFile(inputUrl, { strict: true }), { strict: true });

const generated = quickTodo("Release prep", [
  "Run task ts:test",
  "Review generated API docs",
  "Validate shared fixtures",
]);

await dumpFile(generated, outputUrl);

console.log(existing.plan.title);
console.log(`Wrote ${outputUrl.pathname}`);
