import {
  ISSUE_DAG_CYCLE,
  ISSUE_DANGLING_EDGE_REF,
  ISSUE_INVALID_EDGE_STRUCTURE,
} from "./compat.js";
import type { ValidationReport } from "./issues.js";
import { isRecordLike } from "./utils.js";

/**
 * Validate that `plan.edges` forms a DAG with no dangling references.
 */
export function validatePlanDAG(plan: Record<string, unknown>, report: ValidationReport): void {
  const edges = plan.edges;
  if (!Array.isArray(edges) || edges.length === 0) {
    return;
  }

  const validIds = new Set<string>();
  collectIds(plan.items, validIds);

  const cleanEdges: Array<[string, string]> = [];
  for (const [index, edge] of edges.entries()) {
    const edgePath = `plan.edges[${index}]`;
    if (!isRecordLike(edge)) {
      report.addError(ISSUE_INVALID_EDGE_STRUCTURE, edgePath, "Edge must be an object");
      continue;
    }

    const fromId = edge.from;
    const toId = edge.to;
    let ok = true;

    if (typeof fromId !== "string") {
      report.addError(ISSUE_INVALID_EDGE_STRUCTURE, `${edgePath}.from`, "Edge 'from' must be a string");
      ok = false;
    } else if (!validIds.has(fromId)) {
      report.addError(
        ISSUE_DANGLING_EDGE_REF,
        `${edgePath}.from`,
        `Edge 'from' references unknown item id ${JSON.stringify(fromId)}`,
      );
      ok = false;
    }

    if (typeof toId !== "string") {
      report.addError(ISSUE_INVALID_EDGE_STRUCTURE, `${edgePath}.to`, "Edge 'to' must be a string");
      ok = false;
    } else if (!validIds.has(toId)) {
      report.addError(
        ISSUE_DANGLING_EDGE_REF,
        `${edgePath}.to`,
        `Edge 'to' references unknown item id ${JSON.stringify(toId)}`,
      );
      ok = false;
    }

    if (ok) {
      cleanEdges.push([fromId as string, toId as string]);
    }
  }

  if (cleanEdges.length === 0) {
    return;
  }

  const adjacency = new Map<string, string[]>();
  const inDegree = new Map<string, number>();
  for (const id of validIds) {
    adjacency.set(id, []);
    inDegree.set(id, 0);
  }

  for (const [fromId, toId] of cleanEdges) {
    adjacency.get(fromId)?.push(toId);
    inDegree.set(toId, (inDegree.get(toId) ?? 0) + 1);
  }

  const queue: string[] = [];
  for (const id of validIds) {
    if ((inDegree.get(id) ?? 0) === 0) {
      queue.push(id);
    }
  }

  while (queue.length > 0) {
    const node = queue.shift();
    if (node === undefined) {
      break;
    }

    for (const neighbour of adjacency.get(node) ?? []) {
      const nextDegree = (inDegree.get(neighbour) ?? 0) - 1;
      inDegree.set(neighbour, nextDegree);
      if (nextDegree === 0) {
        queue.push(neighbour);
      }
    }
  }

  const cycleNodes = [...validIds].filter((id) => (inDegree.get(id) ?? 0) > 0).sort();
  if (cycleNodes.length > 0) {
    report.addError(ISSUE_DAG_CYCLE, "plan.edges", `Cycle detected among items: ${JSON.stringify(cycleNodes)}`);
  }
}

function collectIds(items: unknown, ids: Set<string>): void {
  if (!Array.isArray(items)) {
    return;
  }

  for (const item of items) {
    if (!isRecordLike(item)) {
      continue;
    }
    if (typeof item.id === "string") {
      ids.add(item.id);
    }
    collectIds(item.subItems, ids);
  }
}
