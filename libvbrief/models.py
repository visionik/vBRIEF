"""Dataclass object model for vBRIEF v0.5 documents."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable, Mapping

from libvbrief.errors import ValidationError
from libvbrief.issues import ValidationReport
from libvbrief.serialization.json_codec import dump_json_file, dumps_json, load_json_file, parse_json

_PLAN_ITEM_FIELD_ORDER = [
    "id",
    "uid",
    "title",
    "status",
    "narrative",
    "subItems",
    "planRef",
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

_DOCUMENT_FIELD_ORDER = ["vBRIEFInfo", "plan"]


@dataclass
class PlanItem:
    """Plan item model with unknown-field preservation."""

    title: Any = ""
    status: Any = ""
    id: Any = None
    uid: Any = None
    narrative: Any = None
    subItems: list[PlanItem] = field(default_factory=list)
    planRef: Any = None
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
    def from_dict(cls, data: Mapping[str, Any]) -> PlanItem:
        """Create a PlanItem from a mapping."""
        if not isinstance(data, Mapping):
            data = {}

        extras = {k: v for k, v in data.items() if k not in _PLAN_ITEM_FIELD_ORDER}
        item = cls(
            id=data.get("id"),
            uid=data.get("uid"),
            title=data.get("title", ""),
            status=data.get("status", ""),
            narrative=data.get("narrative"),
            planRef=data.get("planRef"),
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

        sub_items = data.get("subItems")
        if isinstance(sub_items, list):
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


@dataclass
class Plan:
    """Plan model with nested items and unknown-field preservation."""

    title: Any = ""
    status: Any = ""
    items: list[PlanItem] = field(default_factory=list)
    id: Any = None
    uid: Any = None
    narratives: Any = None
    edges: Any = None
    tags: Any = None
    metadata: Any = None
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
class VBriefDocument:
    """Root vBRIEF document model."""

    vbrief_info: dict[str, Any] = field(default_factory=dict)
    plan: Plan = field(default_factory=Plan)
    extras: dict[str, Any] = field(default_factory=dict)
    _field_order: list[str] = field(default_factory=list, repr=False)

    @classmethod
    def from_dict(cls, data: Mapping[str, Any], *, strict: bool = False) -> VBriefDocument:
        """Create document from dict and optionally validate in strict mode."""
        if not isinstance(data, Mapping):
            data = {}

        extras = {k: v for k, v in data.items() if k not in _DOCUMENT_FIELD_ORDER}

        vbrief_info = data.get("vBRIEFInfo")
        if not isinstance(vbrief_info, dict):
            vbrief_info = {}

        plan_raw = data.get("plan")
        plan = Plan.from_dict(plan_raw if isinstance(plan_raw, Mapping) else {})

        doc = cls(
            vbrief_info=vbrief_info,
            plan=plan,
            extras=extras,
            _field_order=list(data.keys()),
        )

        if strict:
            report = doc.validate()
            _raise_if_invalid(report)

        return doc

    @classmethod
    def from_json(cls, text: str, *, strict: bool = False) -> VBriefDocument:
        """Create document from JSON string."""
        data = parse_json(text)
        return cls.from_dict(data, strict=strict)

    @classmethod
    def from_file(cls, path: str | Path, *, strict: bool = False) -> VBriefDocument:
        """Create document from JSON file."""
        data = load_json_file(path)
        return cls.from_dict(data, strict=strict)

    def to_dict(self, *, preserve_order: bool = False) -> dict[str, Any]:
        """Convert model to dict while preserving extras."""
        known = {
            "vBRIEFInfo": self.vbrief_info,
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

    def validate(self) -> ValidationReport:
        """Validate this document and return structured issues."""
        from libvbrief.validation import validate_document

        return validate_document(self)


def _known_item_values(item: PlanItem, *, preserve_order: bool) -> dict[str, Any]:
    values: dict[str, Any] = {
        "title": item.title,
        "status": item.status,
    }
    optional_pairs = {
        "id": item.id,
        "uid": item.uid,
        "narrative": item.narrative,
        "subItems": [sub.to_dict(preserve_order=preserve_order) for sub in item.subItems]
        if item.subItems
        else None,
        "planRef": item.planRef,
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
