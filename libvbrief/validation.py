"""Core conformance validation for vBRIEF v0.5 JSON documents."""

from __future__ import annotations

from typing import Any, Mapping

from libvbrief.compat import (
    HIERARCHICAL_ID_PATTERN,
    ISSUE_INVALID_DOCUMENT_TYPE,
    ISSUE_INVALID_ID_FORMAT,
    ISSUE_INVALID_ITEM_STATUS,
    ISSUE_INVALID_ITEM_TYPE,
    ISSUE_INVALID_PLANREF,
    ISSUE_INVALID_PLAN_FIELD_TYPE,
    ISSUE_INVALID_PLAN_STATUS,
    ISSUE_INVALID_ROOT_FIELD_TYPE,
    ISSUE_INVALID_SUBITEMS_TYPE,
    ISSUE_INVALID_VERSION,
    ISSUE_MISSING_ITEM_FIELD,
    ISSUE_MISSING_PLAN_FIELD,
    ISSUE_MISSING_ROOT_FIELD,
    PLAN_REF_PATTERN,
    VALID_STATUSES,
)
from libvbrief.issues import ValidationReport


def validate_document(document: Any) -> ValidationReport:
    """Validate dict or model document and return structured issues."""
    report = ValidationReport()
    data = _to_dict(document)

    if not isinstance(data, Mapping):
        report.add_error(
            ISSUE_INVALID_DOCUMENT_TYPE,
            "$",
            "Document must be an object/dictionary",
        )
        return report

    _validate_root(data, report)
    return report


def _validate_root(data: Mapping[str, Any], report: ValidationReport) -> None:
    if "vBRIEFInfo" not in data:
        report.add_error(ISSUE_MISSING_ROOT_FIELD, "vBRIEFInfo", "Missing required root field: vBRIEFInfo")
        vbrief_info: Mapping[str, Any] | None = None
    else:
        raw_info = data.get("vBRIEFInfo")
        if not isinstance(raw_info, Mapping):
            report.add_error(
                ISSUE_INVALID_ROOT_FIELD_TYPE,
                "vBRIEFInfo",
                "vBRIEFInfo must be an object",
            )
            vbrief_info = None
        else:
            vbrief_info = raw_info

    if vbrief_info is not None:
        version = vbrief_info.get("version")
        if version != "0.5":
            report.add_error(
                ISSUE_INVALID_VERSION,
                "vBRIEFInfo.version",
                f"Expected version '0.5', got {version!r}",
            )

    if "plan" not in data:
        report.add_error(ISSUE_MISSING_ROOT_FIELD, "plan", "Missing required root field: plan")
        return

    plan = data.get("plan")
    if not isinstance(plan, Mapping):
        report.add_error(ISSUE_INVALID_ROOT_FIELD_TYPE, "plan", "plan must be an object")
        return

    _validate_plan(plan, report)


def _validate_plan(plan: Mapping[str, Any], report: ValidationReport) -> None:
    for field_name in ("title", "status", "items"):
        if field_name not in plan:
            report.add_error(
                ISSUE_MISSING_PLAN_FIELD,
                f"plan.{field_name}",
                f"Missing required plan field: {field_name}",
            )

    status = plan.get("status")
    if status is not None and status not in VALID_STATUSES:
        report.add_error(
            ISSUE_INVALID_PLAN_STATUS,
            "plan.status",
            f"Invalid plan status {status!r}; expected one of {sorted(VALID_STATUSES)}",
        )

    plan_id = plan.get("id")
    if plan_id is not None and (not isinstance(plan_id, str) or not HIERARCHICAL_ID_PATTERN.match(plan_id)):
        report.add_error(
            ISSUE_INVALID_ID_FORMAT,
            "plan.id",
            "plan.id must match hierarchical ID pattern",
        )

    items = plan.get("items")
    if items is None:
        return

    if not isinstance(items, list):
        report.add_error(
            ISSUE_INVALID_PLAN_FIELD_TYPE,
            "plan.items",
            "plan.items must be an array",
        )
        return

    _validate_items(items, report, "plan.items")


def _validate_items(items: list[Any], report: ValidationReport, path: str) -> None:
    for index, item in enumerate(items):
        item_path = f"{path}[{index}]"

        if not isinstance(item, Mapping):
            report.add_error(
                ISSUE_INVALID_ITEM_TYPE,
                item_path,
                "Plan item must be an object",
            )
            continue

        if "title" not in item:
            report.add_error(
                ISSUE_MISSING_ITEM_FIELD,
                f"{item_path}.title",
                "Missing required item field: title",
            )

        if "status" not in item:
            report.add_error(
                ISSUE_MISSING_ITEM_FIELD,
                f"{item_path}.status",
                "Missing required item field: status",
            )

        status = item.get("status")
        if status is not None and status not in VALID_STATUSES:
            report.add_error(
                ISSUE_INVALID_ITEM_STATUS,
                f"{item_path}.status",
                f"Invalid item status {status!r}; expected one of {sorted(VALID_STATUSES)}",
            )

        item_id = item.get("id")
        if item_id is not None and (not isinstance(item_id, str) or not HIERARCHICAL_ID_PATTERN.match(item_id)):
            report.add_error(
                ISSUE_INVALID_ID_FORMAT,
                f"{item_path}.id",
                "item id must match hierarchical ID pattern",
            )

        plan_ref = item.get("planRef")
        if plan_ref is not None and (not isinstance(plan_ref, str) or not PLAN_REF_PATTERN.match(plan_ref)):
            report.add_error(
                ISSUE_INVALID_PLANREF,
                f"{item_path}.planRef",
                "planRef must match #..., file://..., or https://...",
            )

        sub_items = item.get("subItems")
        if sub_items is None:
            continue
        if not isinstance(sub_items, list):
            report.add_error(
                ISSUE_INVALID_SUBITEMS_TYPE,
                f"{item_path}.subItems",
                "subItems must be an array",
            )
            continue

        _validate_items(sub_items, report, f"{item_path}.subItems")


def _to_dict(document: Any) -> Any:
    if isinstance(document, Mapping):
        return document

    to_dict = getattr(document, "to_dict", None)
    if callable(to_dict):
        return to_dict(preserve_order=False)

    return document
