"""Dataclass object model for xBRIEF v0.8 documents."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable, Mapping

from libxbrief.errors import ValidationError
from libxbrief.issues import ValidationReport
from libxbrief.serialization.json_codec import dump_json_file, dumps_json, load_json_file, parse_json

_PLAN_ITEM_FIELD_ORDER = [
    "id",
    "uid",
    "type",
    "summary",
    "title",
    "status",
    "narrative",
    "items",
    "subItems",
    "planRef",
    "planRefs",
    "tags",
    "metadata",
    "created",
    "updated",
    "completed",
    "priority",
    "dueDate",
    "startDate",
    "endDate",
    "percentComplete",
    "participants",
    "location",
    "uris",
    "recurrence",
    "reminders",
    "classification",
    "relatedComments",
    "timezone",
    "sequence",
    "lastModifiedBy",
    "lockedBy",
]

_PLAN_FIELD_ORDER = [
    "id",
    "uid",
    "title",
    "status",
    "items",
    "narratives",
    "edges",
    "tags",
    "metadata",
    "architecture",
    "created",
    "updated",
    "author",
    "reviewers",
    "uris",
    "references",
    "timezone",
    "agent",
    "lastModifiedBy",
    "changeLog",
    "sequence",
    "fork",
]

_DOCUMENT_FIELD_ORDER = ["xBRIEFInfo", "plan"]


@dataclass
class PlanItem:
    """Plan item model with unknown-field preservation."""

    title: str = ""
    status: str = ""
    id: Any = None
    uid: Any = None
    type: Any = None
    summary: Any = None
    narrative: Any = None
    items: list[PlanItem] = field(default_factory=list)
    subItems: list[PlanItem] = field(default_factory=list)
    planRef: Any = None
    planRefs: Any = None
    tags: Any = None
    metadata: Any = None
    created: Any = None
    updated: Any = None
    completed: Any = None
    priority: Any = None
    dueDate: Any = None
    startDate: Any = None
    endDate: Any = None
    percentComplete: Any = None
    participants: Any = None
    location: Any = None
    uris: Any = None
    recurrence: Any = None
    reminders: Any = None
    classification: Any = None
    relatedComments: Any = None
    timezone: Any = None
    sequence: Any = None
    lastModifiedBy: Any = None
    lockedBy: Any = None
    extras: dict[str, Any] = field(default_factory=dict)
    _field_order: list[str] = field(default_factory=list, repr=False)

    @classmethod
    def pending(cls, title: str, **kwargs: Any) -> PlanItem:
        """Create a PlanItem with status='pending'."""
        return cls(title=title, status="pending", **kwargs)

    @classmethod
    def running(cls, title: str, **kwargs: Any) -> PlanItem:
        """Create a PlanItem with status='running'."""
        return cls(title=title, status="running", **kwargs)

    # NOTE: PlanItem.completed() factory is defined AFTER the class body to
    # avoid shadowing the dataclass ``completed`` field default.  See below.

    @classmethod
    def blocked(cls, title: str, **kwargs: Any) -> PlanItem:
        """Create a PlanItem with status='blocked'."""
        return cls(title=title, status="blocked", **kwargs)

    @classmethod
    def cancelled(cls, title: str, **kwargs: Any) -> PlanItem:
        """Create a PlanItem with status='cancelled'."""
        return cls(title=title, status="cancelled", **kwargs)

    @classmethod
    def draft(cls, title: str, **kwargs: Any) -> PlanItem:
        """Create a PlanItem with status='draft'."""
        return cls(title=title, status="draft", **kwargs)

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> PlanItem:
        """Create a PlanItem from a mapping."""
        if not isinstance(data, Mapping):
            data = {}

        extras = {k: v for k, v in data.items() if k not in _PLAN_ITEM_FIELD_ORDER}
        item = cls(
            id=data.get("id"),
            uid=data.get("uid"),
            type=data.get("type"),
            summary=data.get("summary"),
            title=data.get("title", ""),
            status=data.get("status", ""),
            narrative=data.get("narrative"),
            planRef=data.get("planRef"),
            planRefs=data.get("planRefs"),
            tags=data.get("tags"),
            metadata=data.get("metadata"),
            created=data.get("created"),
            updated=data.get("updated"),
            completed=data.get("completed"),
            priority=data.get("priority"),
            dueDate=data.get("dueDate"),
            startDate=data.get("startDate"),
            endDate=data.get("endDate"),
            percentComplete=data.get("percentComplete"),
            participants=data.get("participants"),
            location=data.get("location"),
            uris=data.get("uris"),
            recurrence=data.get("recurrence"),
            reminders=data.get("reminders"),
            classification=data.get("classification"),
            relatedComments=data.get("relatedComments"),
            timezone=data.get("timezone"),
            sequence=data.get("sequence"),
            lastModifiedBy=data.get("lastModifiedBy"),
            lockedBy=data.get("lockedBy"),
            extras=extras,
            _field_order=list(data.keys()),
        )

        # items and subItems are assigned after construction (not via cls(...)) because
        # passing them as constructor kwargs would conflict with the dataclass field
        # default_factory — the factory would run first, then be immediately overwritten.
        # This matches the subItems pattern below and is intentional.
        items_field = data.get("items")
        if isinstance(items_field, list):
            item.items = [cls.from_dict(x) for x in items_field if isinstance(x, Mapping)]

        sub_items = data.get("subItems")
        if isinstance(sub_items, list):
            # Non-Mapping entries are intentionally skipped (lenient parse);
            # validation will flag them via ISSUE_INVALID_ITEM_TYPE.
            item.subItems = [cls.from_dict(x) for x in sub_items if isinstance(x, Mapping)]
        return item


    def to_dict(self, *, preserve_order: bool = False) -> dict[str, Any]:
        """Convert item to dict while preserving unknown fields."""
        known = _known_item_values(self, preserve_order=preserve_order)
        return _merge_values(
            known=known,
            extras=self.extras,
            field_order=self._field_order,
            preserve_order=preserve_order,
        )


def _plan_item_completed(cls: type[PlanItem], title: str, **kwargs: Any) -> PlanItem:
    """Create a PlanItem with status='completed'."""
    return cls(title=title, status="completed", **kwargs)


# Attach as classmethod AFTER @dataclass has processed the field defaults,
# so the ``completed`` timestamp field keeps its ``None`` default.
PlanItem.completed = classmethod(_plan_item_completed)  # type: ignore[assignment]


@dataclass
class Plan:
    """Plan model with nested items and unknown-field preservation."""

    title: str = ""
    status: str = ""
    items: list[PlanItem] = field(default_factory=list)
    id: Any = None
    uid: Any = None
    narratives: Any = None
    edges: Any = None
    tags: Any = None
    metadata: Any = None
    architecture: Any = None
    created: Any = None
    updated: Any = None
    author: Any = None
    reviewers: Any = None
    uris: Any = None
    references: Any = None
    timezone: Any = None
    agent: Any = None
    lastModifiedBy: Any = None
    changeLog: Any = None
    sequence: Any = None
    fork: Any = None
    extras: dict[str, Any] = field(default_factory=dict)
    _field_order: list[str] = field(default_factory=list, repr=False)

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> Plan:
        """Create a Plan from a mapping."""
        if not isinstance(data, Mapping):
            data = {}

        extras = {k: v for k, v in data.items() if k not in _PLAN_FIELD_ORDER}
        plan = cls(
            id=data.get("id"),
            uid=data.get("uid"),
            title=data.get("title", ""),
            status=data.get("status", ""),
            narratives=data.get("narratives"),
            edges=data.get("edges"),
            tags=data.get("tags"),
            metadata=data.get("metadata"),
            architecture=data.get("architecture"),
            created=data.get("created"),
            updated=data.get("updated"),
            author=data.get("author"),
            reviewers=data.get("reviewers"),
            uris=data.get("uris"),
            references=data.get("references"),
            timezone=data.get("timezone"),
            agent=data.get("agent"),
            lastModifiedBy=data.get("lastModifiedBy"),
            changeLog=data.get("changeLog"),
            sequence=data.get("sequence"),
            fork=data.get("fork"),
            extras=extras,
            _field_order=list(data.keys()),
        )

        items = data.get("items")
        if isinstance(items, list):
            plan.items = [PlanItem.from_dict(x) for x in items if isinstance(x, Mapping)]
        return plan

    def to_dict(self, *, preserve_order: bool = False) -> dict[str, Any]:
        """Convert plan to dict while preserving unknown fields."""
        known = _known_plan_values(self, preserve_order=preserve_order)
        return _merge_values(
            known=known,
            extras=self.extras,
            field_order=self._field_order,
            preserve_order=preserve_order,
        )


@dataclass
class XBriefDocument:
    """Root xBRIEF document model."""

    xbrief_info: dict[str, Any] = field(default_factory=dict)
    plan: Plan = field(default_factory=Plan)
    extras: dict[str, Any] = field(default_factory=dict)
    _field_order: list[str] = field(default_factory=list, repr=False)

    @classmethod
    def from_dict(cls, data: Mapping[str, Any], *, strict: bool = False, dag: bool = False) -> XBriefDocument:
        """Create document from a plain dict.

        This is a supported public convenience helper alongside ``from_file``
        and ``from_json``.  Pass ``strict=True`` to raise on validation errors.
        Pass ``dag=True`` to also validate that plan.edges form a DAG.
        """
        if not isinstance(data, Mapping):
            data = {}

        extras = {k: v for k, v in data.items() if k not in _DOCUMENT_FIELD_ORDER}

        xbrief_info = data.get("xBRIEFInfo")
        if not isinstance(xbrief_info, dict):
            xbrief_info = {}

        plan_raw = data.get("plan")
        plan = Plan.from_dict(plan_raw if isinstance(plan_raw, Mapping) else {})

        doc = cls(
            xbrief_info=xbrief_info,
            plan=plan,
            extras=extras,
            _field_order=list(data.keys()),
        )

        if strict:
            report = doc.validate(dag=dag)
            _raise_if_invalid(report)

        return doc

    @classmethod
    def from_json(cls, text: str, *, strict: bool = False, dag: bool = False) -> XBriefDocument:
        """Create document from JSON string."""
        data = parse_json(text)
        return cls.from_dict(data, strict=strict, dag=dag)

    @classmethod
    def from_file(cls, path: str | Path, *, strict: bool = False, dag: bool = False) -> XBriefDocument:
        """Create document from JSON file."""
        data = load_json_file(path)
        return cls.from_dict(data, strict=strict, dag=dag)

    def to_dict(self, *, preserve_order: bool = False) -> dict[str, Any]:
        """Convert model to dict while preserving extras."""
        known = {
            "xBRIEFInfo": self.xbrief_info,
            "plan": self.plan.to_dict(preserve_order=preserve_order),
        }
        return _merge_values(
            known=known,
            extras=self.extras,
            field_order=self._field_order,
            preserve_order=preserve_order,
        )

    def to_json(self, *, canonical: bool = True, preserve_format: bool = False) -> str:
        """Serialize model to JSON text."""
        payload = self.to_dict(preserve_order=preserve_format)
        return dumps_json(payload, canonical=canonical, preserve_format=preserve_format)

    def to_file(
        self,
        path: str | Path,
        *,
        canonical: bool = True,
        preserve_format: bool = False,
    ) -> None:
        """Serialize model to JSON file."""
        payload = self.to_dict(preserve_order=preserve_format)
        dump_json_file(path, payload, canonical=canonical, preserve_format=preserve_format)

    def validate(self, *, dag: bool = False) -> ValidationReport:
        """Validate this document and return structured issues.

        Pass ``dag=True`` to also check that plan.edges form a DAG.
        """
        from libxbrief.validation import validate_document

        return validate_document(self, dag=dag)


def _known_item_values(item: PlanItem, *, preserve_order: bool) -> dict[str, Any]:
    values: dict[str, Any] = {
        "title": item.title,
        "status": item.status,
    }
    optional_pairs = {
        "id": item.id,
        "uid": item.uid,
        "type": item.type,
        "summary": item.summary,
        "narrative": item.narrative,
        "items": [sub.to_dict(preserve_order=preserve_order) for sub in item.items]
        if item.items
        else None,
        "subItems": [sub.to_dict(preserve_order=preserve_order) for sub in item.subItems]
        if item.subItems
        else None,
        "planRef": item.planRef,
        "planRefs": item.planRefs,
        "tags": item.tags,
        "metadata": item.metadata,
        "created": item.created,
        "updated": item.updated,
        "completed": item.completed,
        "priority": item.priority,
        "dueDate": item.dueDate,
        "startDate": item.startDate,
        "endDate": item.endDate,
        "percentComplete": item.percentComplete,
        "participants": item.participants,
        "location": item.location,
        "uris": item.uris,
        "recurrence": item.recurrence,
        "reminders": item.reminders,
        "classification": item.classification,
        "relatedComments": item.relatedComments,
        "timezone": item.timezone,
        "sequence": item.sequence,
        "lastModifiedBy": item.lastModifiedBy,
        "lockedBy": item.lockedBy,
    }
    for key, value in optional_pairs.items():
        if value is not None:
            values[key] = value
    return values


def _known_plan_values(plan: Plan, *, preserve_order: bool) -> dict[str, Any]:
    values: dict[str, Any] = {
        "title": plan.title,
        "status": plan.status,
        "items": [item.to_dict(preserve_order=preserve_order) for item in plan.items],
    }
    optional_pairs = {
        "id": plan.id,
        "uid": plan.uid,
        "narratives": plan.narratives,
        "edges": plan.edges,
        "tags": plan.tags,
        "metadata": plan.metadata,
        "architecture": plan.architecture,
        "created": plan.created,
        "updated": plan.updated,
        "author": plan.author,
        "reviewers": plan.reviewers,
        "uris": plan.uris,
        "references": plan.references,
        "timezone": plan.timezone,
        "agent": plan.agent,
        "lastModifiedBy": plan.lastModifiedBy,
        "changeLog": plan.changeLog,
        "sequence": plan.sequence,
        "fork": plan.fork,
    }
    for key, value in optional_pairs.items():
        if value is not None:
            values[key] = value
    return values


def _merge_values(
    *,
    known: dict[str, Any],
    extras: dict[str, Any],
    field_order: Iterable[str],
    preserve_order: bool,
) -> dict[str, Any]:
    if not preserve_order:
        return {**known, **extras}

    merged: dict[str, Any] = {}
    used_extras: set[str] = set()

    for key in field_order:
        if key in known:
            merged[key] = known[key]
        elif key in extras:
            merged[key] = extras[key]
            used_extras.add(key)

    for key, value in known.items():
        if key not in merged:
            merged[key] = value

    for key, value in extras.items():
        if key not in used_extras and key not in merged:
            merged[key] = value

    return merged


def _raise_if_invalid(report: ValidationReport) -> None:
    if not report.is_valid:
        raise ValidationError(report)


class _StatusFactory:
    """Descriptor providing PlanItem.<status>(...) factories without shadowing fields."""

    def __init__(self, status: str) -> None:
        self._status = status

    def __get__(self, obj: Any, owner: type[PlanItem] | None = None) -> Any:
        if owner is None:
            owner = PlanItem

        def factory(title: str, **kwargs: Any) -> PlanItem:
            return owner(title=title, status=self._status, **kwargs)

        return factory


PlanItem.pending = _StatusFactory("pending")
PlanItem.running = _StatusFactory("running")
PlanItem.completed = _StatusFactory("completed")
PlanItem.blocked = _StatusFactory("blocked")
PlanItem.cancelled = _StatusFactory("cancelled")
PlanItem.draft = _StatusFactory("draft")
