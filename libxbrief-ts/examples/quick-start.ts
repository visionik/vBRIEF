import { PlanBuilder, XBriefDocument, loads, validate } from "../src/index.js";

const document = loads(`{
  "xBRIEFInfo": { "version": "0.8" },
  "plan": {
    "title": "Quick Start",
    "status": "running",
    "items": [
      { "id": "audit", "title": "Read the docs", "status": "completed" },
      { "id": "build", "title": "Try the builder API", "status": "running" }
    ]
  }
}`);

const report = validate(document);
if (!report.isValid) {
  console.error(report.errors);
}

const typedDocument = XBriefDocument.fromDict(document, { strict: true });

const builder = new PlanBuilder("libxbrief-ts example", { status: "running" });
builder.addNarrative("Proposal", "Demonstrate parsing, validation, and document construction");

const implementation = builder.addItem("Implement package");
implementation.addSubitem("Add schemas");
implementation.addSubitem("Add tests");

builder.addItem("Write docs");
builder.addEdgesFrom([["implement-package", "write-docs", "blocks"]]);

console.log(typedDocument.plan.title);
console.log(builder.toDocument().toJson());
