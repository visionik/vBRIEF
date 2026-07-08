from __future__ import annotations

import json
from pathlib import Path
from typing import Any


SOR_SHARED_DEFS = (
    "Architecture",
    "SystemOfRecord",
    "StateSurface",
    "StateClassification",
    "StorageDeclaration",
    "ReferenceApplication",
)


def _load_schema(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def test_system_of_record_schema_requires_at_least_one_state_surface(repo_root: Path) -> None:
    schema = _load_schema(repo_root / "schemas" / "xbrief-core.schema.json")
    system_of_record = schema["$defs"]["SystemOfRecord"]

    state_surfaces = system_of_record["properties"]["stateSurfaces"]

    assert state_surfaces["minItems"] == 1


def test_system_of_record_defs_stay_consistent_across_core_schemas(repo_root: Path) -> None:
    current = _load_schema(repo_root / "schemas" / "xbrief-core.schema.json")
    versioned = [
        _load_schema(repo_root / "schemas" / "xbrief-core-0.6.schema.json"),
        _load_schema(repo_root / "schemas" / "xbrief-core-0.7.schema.json"),
        _load_schema(repo_root / "schemas" / "xbrief-core-0.8.schema.json"),
    ]

    for schema in versioned:
        for def_name in SOR_SHARED_DEFS:
            assert schema["$defs"][def_name] == current["$defs"][def_name]


def test_plan_architecture_schema_ref_stays_consistent_across_core_schemas(repo_root: Path) -> None:
    current = _load_schema(repo_root / "schemas" / "xbrief-core.schema.json")
    versioned = [
        _load_schema(repo_root / "schemas" / "xbrief-core-0.6.schema.json"),
        _load_schema(repo_root / "schemas" / "xbrief-core-0.7.schema.json"),
        _load_schema(repo_root / "schemas" / "xbrief-core-0.8.schema.json"),
    ]

    for schema in versioned:
        assert schema["$defs"]["Plan"]["properties"]["architecture"] == current["$defs"]["Plan"]["properties"]["architecture"]
        assert "architecture" not in schema["$defs"]["xBRIEFInfo"]["properties"]
