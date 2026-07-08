"""Core conformance validation for xBRIEF v0.8 JSON documents."""

from __future__ import annotations

from typing import Any, Mapping

from libxbrief.compat import (
    HIERARCHICAL_ID_PATTERN,
    ISSUE_AUTO_STATUS_INVALID,
    ISSUE_DUPLICATE_ITEM_ID,
    ISSUE_INVALID_DOCUMENT_TYPE,
    ISSUE_INVALID_ID_FORMAT,
    ISSUE_INVALID_ITEM_STATUS,
    ISSUE_INVALID_ITEM_TYPE,
    ISSUE_INVALID_ITEM_TYPE_VALUE,
    ISSUE_INVALID_PLANREF,
    ISSUE_INVALID_PLANREFS,
    ISSUE_INVALID_PLAN_FIELD_TYPE,
    ISSUE_INVALID_PLAN_STATUS,
    ISSUE_INVALID_ROOT_FIELD_TYPE,
    ISSUE_INVALID_SUBITEMS_TYPE,
    ISSUE_INVALID_VERSION,
    ISSUE_MISSING_ITEM_FIELD,
    ISSUE_MISSING_PLAN_FIELD,
    ISSUE_MISSING_ROOT_FIELD,
    PLAN_REF_PATTERN,
    VALID_ITEM_TYPES,
    VALID_PLAN_STATUSES,
    VALID_STATUSES,
    VALID_VERSIONS,
)
from libxbrief.issues import ValidationReport


def validate_document(document: Any, *, dag: bool = False) -> ValidationReport:
    """Validate dict or model document and return structured issues.

    Pass ``dag=True`` to also check that plan.edges form a DAG (no dangling
    references and no cycles).  DAG checks are skipped when ``dag=False``
    (the default) to preserve backward compatibility.
    """
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

    if dag:
        plan = data.get("plan")
        if isinstance(plan, Mapping):
            from libxbrief.dag import validate_plan_dag
            validate_plan_dag(plan, report)

    return report


def _validate_root(data: Mapping[str, Any], report: ValidationReport) -> None:
    if "xBRIEFInfo" not in data:
        report.add_error(ISSUE_MISSING_ROOT_FIELD, "xBRIEFInfo", "Missing required root field: xBRIEFInfo")
        xbrief_info = None
    else:
        raw_info = data.get("xBRIEFInfo")
        if not isinstance(raw_info, Mapping):
            report.add_error(
                ISSUE_INVALID_ROOT_FIELD_TYPE,
                "xBRIEFInfo",
                "xBRIEFInfo must be an object",
            )
            xbrief_info = None
        else:
            xbrief_info = raw_info

    if xbrief_info is not None:
        version = xbrief_info.get("version")
        if version not in VALID_VERSIONS:
            report.add_error(
                ISSUE_INVALID_VERSION,
                "xBRIEFInfo.version",
                f"Expected version in {sorted(VALID_VERSIONS)}, got {version!r}",
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
    # Fix (Greptile #2): use VALID_PLAN_STATUSES (excludes "auto") at plan level
    if status is not None and status not in VALID_PLAN_STATUSES:
        report.add_error(
            ISSUE_INVALID_PLAN_STATUS,
            "plan.status",
            f"Invalid plan status {status!r}; expected one of {sorted(VALID_PLAN_STATUSES)}",
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

    _validate_items(items, report, "plan.items", seen_ids=set())


def _validate_items(
    items: list[Any],
    report: ValidationReport,
    path: str,
    *,
    seen_ids: set[str],
) -> None:
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

        # Fix (Greptile #3): reject status="auto" on task-type or childless items
        if status == "auto":
            item_type = item.get("type")
            child_items = item.get("items") or item.get("subItems") or item.get("planRefs")
            if item_type == "task" or not child_items:
                report.add_error(
                    ISSUE_AUTO_STATUS_INVALID,
                    f"{item_path}.status",
                    'status "auto" is only valid on container items (group/milestone/epic) with children',
                )

        item_id = item.get("id")
        if item_id is not None and (not isinstance(item_id, str) or not HIERARCHICAL_ID_PATTERN.match(item_id)):
            report.add_error(
                ISSUE_INVALID_ID_FORMAT,
                f"{item_path}.id",
                "item id must match hierarchical ID pattern",
            )
        elif isinstance(item_id, str):
            if item_id in seen_ids:
                report.add_error(
                    ISSUE_DUPLICATE_ITEM_ID,
                    f"{item_path}.id",
                    f"Duplicate item id {item_id!r}",
                )
            else:
                seen_ids.add(item_id)

        item_type = item.get("type")
        if item_type is not None and item_type not in VALID_ITEM_TYPES:
            report.add_error(
                ISSUE_INVALID_ITEM_TYPE_VALUE,
                f"{item_path}.type",
                f"Invalid item type {item_type!r}; expected one of {sorted(VALID_ITEM_TYPES)}",
            )

        plan_ref = item.get("planRef")
        if plan_ref is not None and (not isinstance(plan_ref, str) or not PLAN_REF_PATTERN.match(plan_ref)):
            report.add_error(
                ISSUE_INVALID_PLANREF,
                f"{item_path}.planRef",
                "planRef must match #..., file://..., or https://...",
            )

        plan_refs = item.get("planRefs")
        if plan_refs is not None:
            if not isinstance(plan_refs, list):
                report.add_error(
                    ISSUE_INVALID_PLANREFS,
                    f"{item_path}.planRefs",
                    "planRefs must be an array",
                )
            else:
                for idx, ref in enumerate(plan_refs):
                    if not isinstance(ref, str) or not PLAN_REF_PATTERN.match(ref):
                        report.add_error(
                            ISSUE_INVALID_PLANREFS,
                            f"{item_path}.planRefs[{idx}]",
                            "planRefs entries must match #..., file://..., or https://...",
                        )

        # Fix (Greptile #1): recurse into both "items" (preferred v0.8) and "subItems" (compat)
        nested_items = item.get("items")
        if nested_items is not None:
            if not isinstance(nested_items, list):
                report.add_error(
                    ISSUE_INVALID_SUBITEMS_TYPE,
                    f"{item_path}.items",
                    "items must be an array",
                )
            else:
                _validate_items(nested_items, report, f"{item_path}.items", seen_ids=seen_ids)

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

        _validate_items(sub_items, report, f"{item_path}.subItems", seen_ids=seen_ids)


def _to_dict(document: Any) -> Any:
    if isinstance(document, Mapping):
        return document

    to_dict = getattr(document, "to_dict", None)
    if callable(to_dict):
        return to_dict(preserve_order=False)

    return document
