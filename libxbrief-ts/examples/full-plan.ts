import { PlanBuilder } from "../src/index.js";

const builder = new PlanBuilder("Launch xBRIEF TypeScript SDK", {
  status: "running",
  id: "launch-ts-sdk",
  tags: ["typescript", "sdk", "launch"],
  metadata: {
    owner: "platform-team",
    quarter: "2026-Q2",
  },
});

builder.addNarrative("Proposal", "Ship a TypeScript SDK with strong parity to the Python library.");
builder.addNarrative("Background", "TypeScript support improves interoperability for modern agent and web runtimes.");
builder.addNarrative("Constraint", "The public API must remain runtime-agnostic except for explicit Node file I/O helpers.");
builder.addNarrative("Risk", "Cross-language drift can appear if builder or validation behavior diverges from Python.");

const architecture = builder.addItem("Architecture and package design", {
  id: "architecture",
  status: "completed",
  narrative: {
    Outcome: "Package layout, entrypoints, and validation approach were approved.",
  },
});
architecture.addSubitem("Define universal entrypoint", {
  id: "architecture.universal-entrypoint",
  status: "completed",
});
architecture.addSubitem("Define node entrypoint", {
  id: "architecture.node-entrypoint",
  status: "completed",
});

const schemas = builder.addItem("Implement schemas", {
  id: "schemas",
  status: "completed",
});
schemas.addSubitem("Add Zod schemas", {
  id: "schemas.zod",
  status: "completed",
});
schemas.addSubitem("Preserve unknown fields", {
  id: "schemas.passthrough",
  status: "completed",
});

const models = builder.addItem("Implement models", {
  id: "models",
  status: "running",
});
models.addSubitem("Add PlanItem model", {
  id: "models.plan-item",
  status: "completed",
});
models.addSubitem("Add Plan and XBriefDocument models", {
  id: "models.plan-document",
  status: "running",
});

const validation = builder.addItem("Implement validation", {
  id: "validation",
  status: "running",
});
validation.addSubitem("Port structural validation", {
  id: "validation.structural",
  status: "completed",
});
validation.addSubitem("Port DAG checks", {
  id: "validation.dag",
  status: "running",
});

const builderApi = builder.addItem("Implement builder API", {
  id: "builder-api",
  status: "running",
});
builderApi.addSubitem("Add PlanBuilder", {
  id: "builder-api.plan-builder",
  status: "completed",
});
builderApi.addSubitem("Add ItemBuilder helpers", {
  id: "builder-api.item-builder",
  status: "running",
});

const docsExamples = builder.addItem("Write docs and examples", {
  id: "docs-examples",
  status: "pending",
});
docsExamples.addSubitem("Document universal API", {
  id: "docs-examples.universal-api",
  status: "pending",
});
docsExamples.addSubitem("Document node file I/O", {
  id: "docs-examples.node-io",
  status: "pending",
});
docsExamples.addSubitem("Add quick start example", {
  id: "docs-examples.quick-start",
  status: "completed",
});
docsExamples.addSubitem("Add full plan example", {
  id: "docs-examples.full-plan",
  status: "pending",
});

const tests = builder.addItem("Add test suite", {
  id: "tests",
  status: "running",
});
tests.addSubitem("Add unit tests", {
  id: "tests.unit",
  status: "completed",
});
tests.addSubitem("Add cross-language tests", {
  id: "tests.cross-language",
  status: "running",
});

const release = builder.addItem("Prepare release candidate", {
  id: "release",
  status: "pending",
  narrative: {
    Goal: "Produce a build artifact and a validated example set for internal adoption.",
  },
});
release.addSubitem("Run typecheck, lint, test, build", {
  id: "release.validation",
  status: "pending",
});
release.addSubitem("Review generated API surface", {
  id: "release.api-review",
  status: "pending",
});

builder.addEdgesFrom([
  ["architecture", "schemas", "blocks"],
  ["architecture", "models", "blocks"],
  ["schemas", "validation", "blocks"],
  ["models", "builder-api", "blocks"],
  ["validation", "tests", "blocks"],
  ["builder-api", "docs-examples", "blocks"],
  ["tests", "release", "blocks"],
  ["docs-examples", "release", "blocks"],
]);

const document = builder.toDocument();

console.log(document.toJson());
