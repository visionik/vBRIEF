"""End-to-end tests for libxbrief.

Each test exercises a complete workflow: build → serialize → load →
validate → modify → re-serialize, simulating real-world usage patterns.
"""

from __future__ import annotations

import json
from pathlib import Path

from libxbrief import (
    PlanBuilder,
    PlanItem,
    XBriefDocument,
    dumps,
    from_items,
    loads,
    quick_todo,
)


# ---------------------------------------------------------------------------
# Workflow 1: Build a plan from scratch, validate, persist, reload
# ---------------------------------------------------------------------------


def test_e2e_build_validate_persist_reload(tmp_path: Path) -> None:
    # Build
    builder = PlanBuilder("Sprint 47", status="running", tags=["mvp"])
    auth = builder.add_item("Auth system", id="auth", status="pending")
    auth.add_subitem("JWT tokens", id="auth.jwt", status="completed")
    auth.add_subitem("Refresh flow", id="auth.refresh", status="pending")
    auth.add_narrative("Approach", "Use RS256 asymmetric signing")
    builder.add_item("API endpoints", id="api", status="pending")
    builder.add_edges_from([("auth", "api", "blocks")])
    builder.add_narrative("Goal", "Ship auth before API layer")

    doc = builder.to_document()

    # Validate
    report = doc.validate(dag=True)
    assert report.is_valid, report.errors

    # Persist
    path = tmp_path / "sprint-47.xbrief.json"
    doc.to_file(path)

    # Reload
    loaded_model = XBriefDocument.from_file(path)
    assert loaded_model.plan.title == "Sprint 47"
    assert loaded_model.plan.tags == ["mvp"]
    assert len(loaded_model.plan.items) == 2
    assert loaded_model.plan.items[0].subItems[0].status == "completed"
    assert loaded_model.plan.edges is not None
    assert len(loaded_model.plan.edges) == 1

    # Re-validate after reload
    assert loaded_model.validate(dag=True).is_valid


# ---------------------------------------------------------------------------
# Workflow 2: Load existing file, modify, save, verify round-trip
# ---------------------------------------------------------------------------


def test_e2e_load_modify_save_roundtrip(tmp_path: Path) -> None:
    # Create initial document
    initial = quick_todo("Backlog", ["Task A", "Task B", "Task C"])
    path = tmp_path / "backlog.xbrief.json"
    initial.to_file(path)

    # Load, modify
    model = XBriefDocument.from_file(path)
    model.plan.items[0].status = "completed"
    model.plan.items[0].completed = "2026-03-31T12:00:00Z"
    model.plan.items.append(PlanItem.pending("Task D"))

    # Save modified
    modified_path = tmp_path / "backlog-modified.xbrief.json"
    model.to_file(modified_path)

    # Reload and verify
    reloaded = XBriefDocument.from_file(modified_path)
    assert reloaded.plan.items[0].status == "completed"
    assert reloaded.plan.items[0].completed == "2026-03-31T12:00:00Z"
    assert len(reloaded.plan.items) == 4
    assert reloaded.plan.items[3].title == "Task D"
    assert reloaded.validate().is_valid


# ---------------------------------------------------------------------------
# Workflow 3: Mix builder and factory APIs
# ---------------------------------------------------------------------------


def test_e2e_mixed_builder_and_factory_workflow() -> None:
    # Use factories to create items
    items = [
        PlanItem.completed("Setup CI", id="ci"),
        PlanItem.completed("Configure linting", id="lint"),
        PlanItem.pending("Write core logic", id="core"),
        PlanItem.blocked("Integration tests", id="int-tests"),
        PlanItem.draft("Deploy to staging", id="staging"),
    ]

    # Use from_items to build document
    doc = from_items("Project Alpha", items, status="running")
    assert doc.validate().is_valid
    assert len(doc.plan.items) == 5

    # Serialize and round-trip
    text = dumps(doc)
    rebuilt = XBriefDocument.from_dict(loads(text))
    assert rebuilt.plan.items[2].status == "pending"
    assert rebuilt.plan.items[3].status == "blocked"


# ---------------------------------------------------------------------------
# Workflow 4: DAG with complex dependencies
# ---------------------------------------------------------------------------


def test_e2e_dag_complex_dependencies() -> None:
    builder = PlanBuilder("CI Pipeline", status="approved", id="ci-pipe")
    builder.add_item("Lint", id="lint", status="completed")
    builder.add_item("Unit tests", id="unit", status="completed")
    builder.add_item("Integration tests", id="integ", status="running")
    builder.add_item("Build", id="build", status="pending")
    builder.add_item("Deploy staging", id="staging", status="pending")
    builder.add_item("Deploy prod", id="prod", status="pending")

    builder.add_edges_from([
        ("lint", "build", "blocks"),
        ("unit", "build", "blocks"),
        ("integ", "build", "blocks"),
        ("build", "staging", "blocks"),
        ("staging", "prod", "blocks"),
    ])

    doc = builder.to_document()
    report = doc.validate(dag=True)
    assert report.is_valid, report.errors

    # Verify serialized edges survive round-trip
    text = dumps(doc)
    loaded = loads(text)
    assert len(loaded["plan"]["edges"]) == 5


# ---------------------------------------------------------------------------
# Workflow 5: Strict mode catches errors early
# ---------------------------------------------------------------------------


def test_e2e_strict_mode_catches_duplicate_ids() -> None:
    builder = PlanBuilder("Plan", status="running")
    builder.add_item("Task A", id="dup")

    try:
        builder.add_item("Task B", id="dup")
    except ValueError as exc:
        assert "Duplicate" in str(exc)
    else:
        raise AssertionError("Expected ValueError for duplicate ID")


def test_e2e_strict_mode_catches_bad_edge_refs() -> None:
    builder = PlanBuilder("Plan", status="running")
    builder.add_item("Task A", id="a")

    try:
        builder.add_edges_from([("a", "nonexistent", "blocks")])
    except ValueError as exc:
        assert "unknown target" in str(exc)
    else:
        raise AssertionError("Expected ValueError for dangling edge")


# ---------------------------------------------------------------------------
# Workflow 6: Non-strict deferred validation
# ---------------------------------------------------------------------------


def test_e2e_nonstrict_defers_to_validate() -> None:
    builder = PlanBuilder("Plan", status="running", strict=False)
    builder.add_item("A", id="dup")
    builder.add_item("B", id="dup")  # duplicate — no error in non-strict

    doc = builder.to_document()
    report = doc.validate()
    assert not report.is_valid
    assert any(i.code == "duplicate_item_id" for i in report.errors)


# ---------------------------------------------------------------------------
# Workflow 7: quick_todo end-to-end with file I/O
# ---------------------------------------------------------------------------


def test_e2e_quick_todo_file_roundtrip(tmp_path: Path) -> None:
    doc = quick_todo("Shopping", ["Milk", "Eggs", "Bread"])
    path = tmp_path / "shopping.xbrief.json"
    doc.to_file(path)

    # Verify file is valid JSON
    raw = json.loads(path.read_text(encoding="utf-8"))
    assert raw["xBRIEFInfo"]["version"] == "0.8"
    assert raw["plan"]["title"] == "Shopping"
    assert len(raw["plan"]["items"]) == 3

    # Reload via class API
    reloaded = XBriefDocument.from_file(path)
    assert reloaded.validate().is_valid
    assert reloaded.plan.items[1].title == "Eggs"


# ---------------------------------------------------------------------------
# Workflow 8: Unknown/extension fields survive full lifecycle
# ---------------------------------------------------------------------------


def test_e2e_unknown_fields_survive_full_lifecycle(tmp_path: Path) -> None:
    # Manually create a doc with extension fields
    raw = {
        "xBRIEFInfo": {"version": "0.8"},
        "plan": {
            "title": "Extended Plan",
            "status": "running",
            "type": "custom-extension",
            "items": [
                {
                    "title": "Item with extras",
                    "status": "pending",
                    "kind": "requirement",
                    "customField": {"nested": True},
                }
            ],
        },
        "topLevelExtra": "preserved",
    }

    # Load → model → serialize → reload
    model = XBriefDocument.from_dict(raw)
    assert model.plan.extras["type"] == "custom-extension"
    assert model.plan.items[0].extras["kind"] == "requirement"
    assert model.extras["topLevelExtra"] == "preserved"

    path = tmp_path / "extended.xbrief.json"
    model.to_file(path)

    reloaded_raw = json.loads(path.read_text(encoding="utf-8"))
    assert reloaded_raw["plan"]["type"] == "custom-extension"
    assert reloaded_raw["plan"]["items"][0]["kind"] == "requirement"
    assert reloaded_raw["plan"]["items"][0]["customField"] == {"nested": True}
    assert reloaded_raw["topLevelExtra"] == "preserved"


# ---------------------------------------------------------------------------
# Workflow 9: Canonical vs. preserve-format serialization
# ---------------------------------------------------------------------------


def test_e2e_canonical_output_has_sorted_keys() -> None:
    doc = quick_todo("Plan", ["A", "B"])
    canonical = doc.to_json(canonical=True)
    parsed = json.loads(canonical)
    assert list(parsed.keys()) == sorted(parsed.keys())


def test_e2e_preserve_format_keeps_original_key_order(tmp_path: Path) -> None:
    # Create with specific key order (plan before xBRIEFInfo)
    raw = '{"plan": {"title": "T", "status": "running", "items": []}, "xBRIEFInfo": {"version": "0.8"}}'
    model = XBriefDocument.from_json(raw)
    preserved = model.to_json(preserve_format=True, canonical=False)
    parsed = json.loads(preserved)
    keys = list(parsed.keys())
    assert keys.index("plan") < keys.index("xBRIEFInfo")


# ---------------------------------------------------------------------------
# Workflow 10: XBriefDocument.from_json / from_file strict + dag
# ---------------------------------------------------------------------------


def test_e2e_from_json_strict_raises_on_invalid() -> None:
    bad_json = '{"xBRIEFInfo": {"version": "0.8"}, "plan": {"title": "T"}}'

    try:
        XBriefDocument.from_json(bad_json, strict=True)
    except Exception:
        pass  # Expected — missing status and items
    else:
        raise AssertionError("Expected strict mode to raise on missing fields")


def test_e2e_from_file_strict_dag_validates_fully(tmp_path: Path) -> None:
    doc = {
        "xBRIEFInfo": {"version": "0.8"},
        "plan": {
            "title": "T",
            "status": "running",
            "items": [
                {"title": "A", "status": "pending", "id": "a"},
                {"title": "B", "status": "pending", "id": "b"},
            ],
            "edges": [{"from": "a", "to": "b"}, {"from": "b", "to": "a"}],
        },
    }
    path = tmp_path / "cycle.xbrief.json"
    path.write_text(json.dumps(doc), encoding="utf-8")

    try:
        XBriefDocument.from_file(path, strict=True, dag=True)
    except Exception:
        pass  # Expected — DAG cycle
    else:
        raise AssertionError("Expected strict+dag to raise on cycle")
