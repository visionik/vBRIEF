# libxbrief-ts
`libxbrief-ts` is the ESM-only TypeScript port of the local Python `libxbrief` package for xBRIEF v0.5 documents.

It provides:
- typed model classes for `PlanItem`, `Plan`, and `XBriefDocument`
- `loads`, `dumps`, and `validate` helpers for universal runtimes
- `loadFile` and `dumpFile` in a separate Node entrypoint
- a builder API with `PlanBuilder`, `ItemBuilder`, `quickTodo`, and status factories
- unknown-field preservation so extension fields survive round-trips

## Install
From the repo root:

```bash
npm install ./libxbrief-ts
```

Inside the package during development:

```bash
cd libxbrief-ts
npm install
```

## Development Commands
From the repo root:

```bash
task ts:typecheck
task ts:lint
task ts:test
task ts:build
```

Inside `libxbrief-ts/`:

```bash
npm run typecheck
npm run lint
npm run test
npm run build
```

## Universal API
Use the root entrypoint for browser/Node/Bun/Deno-safe parsing, validation, builders, and serialization.

```ts
import { loads, validate, PlanBuilder } from "libxbrief-ts";

const document = loads(`{
  "xBRIEFInfo": { "version": "0.5" },
  "plan": {
    "title": "Migration Plan",
    "status": "running",
    "items": [
      { "id": "audit", "title": "Audit current usage", "status": "completed" },
      { "id": "port", "title": "Port library", "status": "running" }
    ]
  }
}`);

const report = validate(document);
if (!report.isValid) {
  console.error(report.errors);
}

const builder = new PlanBuilder("Ship libxbrief-ts", { status: "running" });
builder.addNarrative("Proposal", "Port the Python library with full API parity");
builder.addItem("Implement models");
builder.addItem("Write compatibility tests");

const built = builder.toDocument();
console.log(built.toJson());
```

## Node File I/O
Use the `node` entrypoint when you need UTF-8 file helpers.

```ts
import { loadFile, dumpFile, quickTodo } from "libxbrief-ts/node";

const document = await loadFile(new URL("../examples/minimal-plan.xbrief.json", import.meta.url), {
  strict: true,
});

const todo = quickTodo("Release prep", [
  "Publish docs",
  "Verify fixtures",
]);

await dumpFile(todo, new URL("./release-prep.xbrief.json", import.meta.url));
console.log(document.plan.title);
```

## Examples
- `examples/quick-start.ts`
- `examples/node-io.ts`
- `examples/full-plan.ts`
- `examples/full-plan.xbrief.json`

These examples import from the local source tree so they stay aligned with the package during development.
