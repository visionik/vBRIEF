"""DAG validation for xBRIEF plan edges.

Checks that plan.edges form a directed acyclic graph:
  1. Each edge must be a mapping with string 'from' and 'to' fields.
  2. Both 'from' and 'to' must reference an item id that exists in the plan
     (items are collected recursively, including subItems at all depths).
  3. The graph formed by the edges must be acyclic (detected via Kahn's
     topological sort — nodes with non-zero in-degree after BFS form cycles).

This module is called by validation.validate_document when dag=True.
"""

from __future__ import annotations

from collections import deque
from typing import Any, Mapping

from libxbrief.compat import (
    ISSUE_DAG_CYCLE,
    ISSUE_DANGLING_EDGE_REF,
    ISSUE_INVALID_EDGE_STRUCTURE,
)
from libxbrief.issues import ValidationReport


def validate_plan_dag(plan: Mapping[str, Any], report: ValidationReport) -> None:
    """Validate that plan.edges form a DAG with no dangling references."""
    edges = plan.get("edges")
    if not isinstance(edges, list) or not edges:
        return

    # Collect all item IDs available in this plan (recursively)
    valid_ids: set[str] = set()
    _collect_ids(plan.get("items", []), valid_ids)

    # Validate edge structure and accumulate clean (from, to) pairs
    clean_edges: list[tuple[str, str]] = []
    for i, edge in enumerate(edges):
        edge_path = f"plan.edges[{i}]"

        if not isinstance(edge, Mapping):
            report.add_error(
                ISSUE_INVALID_EDGE_STRUCTURE,
                edge_path,
                "Edge must be an object",
            )
            continue

        from_id = edge.get("from")
        to_id = edge.get("to")
        ok = True

        if not isinstance(from_id, str):
            report.add_error(
                ISSUE_INVALID_EDGE_STRUCTURE,
                f"{edge_path}.from",
                "Edge 'from' must be a string",
            )
            ok = False
        elif from_id not in valid_ids:
            report.add_error(
                ISSUE_DANGLING_EDGE_REF,
                f"{edge_path}.from",
                f"Edge 'from' references unknown item id {from_id!r}",
            )
            ok = False

        if not isinstance(to_id, str):
            report.add_error(
                ISSUE_INVALID_EDGE_STRUCTURE,
                f"{edge_path}.to",
                "Edge 'to' must be a string",
            )
            ok = False
        elif to_id not in valid_ids:
            report.add_error(
                ISSUE_DANGLING_EDGE_REF,
                f"{edge_path}.to",
                f"Edge 'to' references unknown item id {to_id!r}",
            )
            ok = False

        if ok:
            clean_edges.append((from_id, to_id))

    if not clean_edges:
        return

    # Kahn's topological sort — detect cycle participants
    # Build adjacency list and in-degree map over all known item IDs
    adj: dict[str, list[str]] = {id_: [] for id_ in valid_ids}
    in_degree: dict[str, int] = {id_: 0 for id_ in valid_ids}

    for frm, to in clean_edges:
        adj[frm].append(to)
        in_degree[to] += 1

    queue: deque[str] = deque(id_ for id_ in valid_ids if in_degree[id_] == 0)
    visited = 0
    while queue:
        node = queue.popleft()
        visited += 1
        for neighbour in adj[node]:
            in_degree[neighbour] -= 1
            if in_degree[neighbour] == 0:
                queue.append(neighbour)

    # Any node whose in-degree is still > 0 is part of a cycle
    cycle_nodes = sorted(id_ for id_ in valid_ids if in_degree[id_] > 0)
    if cycle_nodes:
        report.add_error(
            ISSUE_DAG_CYCLE,
            "plan.edges",
            f"Cycle detected among items: {cycle_nodes}",
        )


def _collect_ids(items: list[Any], ids: set[str]) -> None:
    """Recursively collect item id values from items and their subItems."""
    for item in items:
        if not isinstance(item, Mapping):
            continue
        item_id = item.get("id")
        if isinstance(item_id, str):
            ids.add(item_id)
        sub = item.get("subItems")
        if isinstance(sub, list):
            _collect_ids(sub, ids)
