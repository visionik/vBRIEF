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
    "cancelled",
}

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
ISSUE_INVALID_PLANREF: Final[str] = "invalid_planref"
ISSUE_INVALID_SUBITEMS_TYPE: Final[str] = "invalid_subitems_type"
