"""Builder-style APIs and convenience helpers for libxbrief."""

from __future__ import annotations

import re
from typing import Any, Iterable

from libxbrief.compat import VALID_STATUSES
from libxbrief.models import Plan, PlanItem, XBriefDocument

_NON_ALNUM_RE = re.compile(r"[^a-z0-9]+")
_MULTI_HYPHEN_RE = re.compile(r"-+")


def _slugify(text: str) -> str:
    """Convert text into a stable, lowercase slug."""
    slug = text.strip().lower()
    slug = _NON_ALNUM_RE.sub("-", slug)
    slug = _MULTI_HYPHEN_RE.sub("-", slug)
    slug = slug.strip("-")
    return slug or "item"


class ItemBuilder:
    """Mutable builder wrapper for a PlanItem."""

    def __init__(
        self,
        title: str,
        *,
        id: str | None = None,
        status: str = "pending",
        strict: bool = True,
        id_registry: set[str] | None = None,
        parent_id: str | None = None,
        **kwargs: Any,
    ) -> None:
        self._strict = strict
        self._id_registry = id_registry if id_registry is not None else set()

        self._validate_status(status)
        item_id = self._resolve_id(title=title, item_id=id, parent_id=parent_id)
        self._register_id(item_id)

        self._item = PlanItem(title=title, status=status, id=item_id, **kwargs)

    @property
    def item(self) -> PlanItem:
        """Return the underlying PlanItem instance."""
        return self._item

    def add_narrative(self, key: str, value: Any) -> None:
        """Add an item-level narrative entry."""
        if not isinstance(self._item.narrative, dict):
            self._item.narrative = {}
        self._item.narrative[key] = value

    def add_subitem(
        self,
        title: str,
        *,
        id: str | None = None,
        status: str = "pending",
        **kwargs: Any,
    ) -> ItemBuilder:
        """Add a child item and return its builder."""
        child = ItemBuilder(
            title,
            id=id,
            status=status,
            strict=self._strict,
            id_registry=self._id_registry,
            parent_id=self._item.id if isinstance(self._item.id, str) else None,
            **kwargs,
        )
        self._item.subItems.append(child.item)
        return child

    def to_planitem(self) -> PlanItem:
        """Return the assembled PlanItem."""
        return self._item

    def _resolve_id(self, *, title: str, item_id: str | None, parent_id: str | None) -> str | None:
        if item_id is not None:
            return item_id

        slug = _slugify(title)
        if parent_id:
            return f"{parent_id}.{slug}"
        return slug

    def _register_id(self, item_id: str | None) -> None:
        if item_id is None:
            return
        if self._strict and item_id in self._id_registry:
            raise ValueError(f"Duplicate item id: {item_id!r}")
        self._id_registry.add(item_id)

    def _validate_status(self, status: str) -> None:
        if self._strict and status not in VALID_STATUSES:
            raise ValueError(
                f"Invalid status {status!r}; expected one of {sorted(VALID_STATUSES)}"
            )


class PlanBuilder:
    """Fluent builder for xBRIEF documents."""

    def __init__(
        self,
        title: str,
        *,
        status: str = "draft",
        strict: bool = True,
        **kwargs: Any,
    ) -> None:
        self._strict = strict
        self._id_registry: set[str] = set()
        self._title = title
        self._status = status
        self._plan_kwargs = dict(kwargs)
        self._items: list[PlanItem] = []
        self._narratives: dict[str, Any] = {}
        self._edges: list[Any] = []

        if self._strict and status not in VALID_STATUSES:
            raise ValueError(
                f"Invalid status {status!r}; expected one of {sorted(VALID_STATUSES)}"
            )

    def __enter__(self) -> PlanBuilder:
        return self

    def __exit__(self, exc_type: Any, exc_value: Any, traceback: Any) -> None:
        return None

    def add_narrative(self, key: str, value: Any) -> None:
        """Add a plan-level narrative entry."""
        self._narratives[key] = value

    def add_item(
        self,
        title: str,
        *,
        id: str | None = None,
        status: str = "pending",
        **kwargs: Any,
    ) -> ItemBuilder:
        """Add a top-level item and return its builder."""
        item = ItemBuilder(
            title,
            id=id,
            status=status,
            strict=self._strict,
            id_registry=self._id_registry,
            **kwargs,
        )
        self._items.append(item.item)
        return item

    def add_edges_from(self, edges: Iterable[Any]) -> None:
        """Add edges from an iterable of tuples."""
        for edge in edges:
            normalized = self._normalize_edge(edge)
            if self._strict and isinstance(normalized, dict):
                self._validate_edge_ids(normalized)
            self._edges.append(normalized)

    def to_document(self) -> XBriefDocument:
        """Assemble the final XBriefDocument."""
        plan_kwargs = {
            key: value
            for key, value in self._plan_kwargs.items()
            if key not in {"items", "narratives", "edges"}
        }
        plan = Plan(
            title=self._title,
            status=self._status,
            items=list(self._items),
            narratives=self._narratives or None,
            edges=self._edges or None,
            **plan_kwargs,
        )
        return XBriefDocument(xbrief_info={"version": "0.8"}, plan=plan)

    def _normalize_edge(self, edge: Any) -> Any:
        if isinstance(edge, tuple | list) and len(edge) == 3:
            return {"from": edge[0], "to": edge[1], "type": edge[2]}
        if isinstance(edge, dict):
            return dict(edge)
        if self._strict:
            raise ValueError("Edge entries must be 3-tuples or dicts")
        return edge

    def _validate_edge_ids(self, edge: dict[str, Any]) -> None:
        from_id = edge.get("from")
        to_id = edge.get("to")
        edge_type = edge.get("type")

        if not isinstance(from_id, str) or not isinstance(to_id, str) or not isinstance(edge_type, str):
            raise ValueError("Edge entries must contain string 'from', 'to', and 'type' values")
        if from_id not in self._id_registry:
            raise ValueError(f"Edge references unknown source id: {from_id!r}")
        if to_id not in self._id_registry:
            raise ValueError(f"Edge references unknown target id: {to_id!r}")


def quick_todo(
    title: str,
    items: Iterable[str | PlanItem],
    *,
    status: str = "running",
    **kwargs: Any,
) -> XBriefDocument:
    """Create a minimal xBRIEF todo document from strings or PlanItem objects."""
    plan_items: list[PlanItem] = []
    for item in items:
        if isinstance(item, PlanItem):
            plan_items.append(item)
        elif isinstance(item, str):
            plan_items.append(PlanItem(title=item, status="pending"))
        else:
            raise TypeError("quick_todo items must be strings or PlanItem instances")

    return XBriefDocument(
        xbrief_info={"version": "0.8"},
        plan=Plan(title=title, status=status, items=plan_items, **kwargs),
    )


def from_items(
    title: str,
    items: Iterable[PlanItem],
    *,
    status: str = "running",
    **kwargs: Any,
) -> XBriefDocument:
    """Create a xBRIEF document from PlanItem objects."""
    plan_items = list(items)
    for item in plan_items:
        if not isinstance(item, PlanItem):
            raise TypeError("from_items items must be PlanItem instances")

    return XBriefDocument(
        xbrief_info={"version": "0.8"},
        plan=Plan(title=title, status=status, items=plan_items, **kwargs),
    )
