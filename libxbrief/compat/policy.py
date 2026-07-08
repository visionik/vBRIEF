"""Compatibility and conformance policy constants."""

from __future__ import annotations

import re
from typing import Final

VALID_STATUSES: Final[set[str]] = {
    "draft",
    "proposed",
    "approved",
    "pending",
    "running",
    "completed",
    "blocked",
    "failed",
    "cancelled",
    "auto",
}

# "auto" is only valid on container PlanItems (group/milestone/epic) with
# children.  It MUST NOT appear at plan level.
VALID_PLAN_STATUSES: Final[set[str]] = VALID_STATUSES - {"auto"}

VALID_ITEM_TYPES: Final[set[str]] = {
    "task",
    "group",
    "milestone",
    "epic",
}

# Current spec version. VALID_VERSIONS is broader for backward-compatible reading
# (the library can parse older documents). Use CURRENT_VERSION when you need to
# enforce that a document conforms to the latest spec.
CURRENT_VERSION: Final[str] = "0.8"

VALID_VERSIONS: Final[set[str]] = {
    "0.5",
    "0.6",
    "0.7",
    "0.8",
}

EXTENSION_PROPERTY_PATTERN: Final[re.Pattern[str]] = re.compile(
    r"^x-[a-z0-9-]+/"
)

HIERARCHICAL_ID_PATTERN: Final[re.Pattern[str]] = re.compile(
    r"^[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+)*$"
)

PLAN_REF_PATTERN: Final[re.Pattern[str]] = re.compile(
    r"^(#[a-zA-Z0-9_.-]+|file://.*|https://.*)$"
)

ISSUE_INVALID_DOCUMENT_TYPE: Final[str] = "invalid_document_type"
ISSUE_MISSING_ROOT_FIELD: Final[str] = "missing_root_field"
ISSUE_INVALID_ROOT_FIELD_TYPE: Final[str] = "invalid_root_field_type"
ISSUE_INVALID_VERSION: Final[str] = "invalid_version"
ISSUE_MISSING_PLAN_FIELD: Final[str] = "missing_plan_field"
ISSUE_INVALID_PLAN_FIELD_TYPE: Final[str] = "invalid_plan_field_type"
ISSUE_INVALID_PLAN_STATUS: Final[str] = "invalid_plan_status"
ISSUE_INVALID_ITEM_TYPE: Final[str] = "invalid_item_type"
ISSUE_MISSING_ITEM_FIELD: Final[str] = "missing_item_field"
ISSUE_INVALID_ITEM_STATUS: Final[str] = "invalid_item_status"
ISSUE_INVALID_ID_FORMAT: Final[str] = "invalid_id_format"
ISSUE_DUPLICATE_ITEM_ID: Final[str] = "duplicate_item_id"
ISSUE_INVALID_PLANREF: Final[str] = "invalid_planref"
ISSUE_INVALID_SUBITEMS_TYPE: Final[str] = "invalid_subitems_type"
ISSUE_INVALID_ITEM_TYPE_VALUE: Final[str] = "invalid_item_type_value"
ISSUE_INVALID_PLANREFS: Final[str] = "invalid_planrefs"
ISSUE_AUTO_STATUS_INVALID: Final[str] = "auto_status_invalid"

# DAG validation issue codes (used when dag=True is passed to validate)
ISSUE_INVALID_EDGE_STRUCTURE: Final[str] = "invalid_edge_structure"
ISSUE_DANGLING_EDGE_REF: Final[str] = "dangling_edge_ref"
ISSUE_DAG_CYCLE: Final[str] = "dag_cycle"
