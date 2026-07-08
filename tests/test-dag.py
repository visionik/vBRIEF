"""
Unit tests for DAG validation (dag=True mode).

Covers: no-edges early exit, valid DAG, cycle detection, dangling
references, malformed edges, self-loops, deep subItem IDs, and the
strict+dag combination on the class API.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from libxbrief import ValidationError, XBriefDocument, validate


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _doc(plan_extra: dict) -> dict:
    """Build a minimal valid v0.8 document with extra plan fields."""
    return {
        "xBRIEFInfo": {"version": "0.8"},
        "plan": {
            "title": "Test",
            "status": "running",
            "items": [
                {"id": "a", "title": "A", "status": "pending"},
                {"id": "b", "title": "B", "status": "pending"},
                {"id": "c", "title": "C", "status": "pending"},
            ],
            **plan_extra,
        },
    }


# ---------------------------------------------------------------------------
# No edges — DAG checks are skipped cleanly
# ---------------------------------------------------------------------------


def test_dag_no_edges_field_is_valid() -> None:
    doc = _doc({})
    report = validate(doc, dag=True)
    assert report.is_valid


def test_dag_empty_edges_list_is_valid() -> None:
    doc = _doc({"edges": []})
    report = validate(doc, dag=True)
    assert report.is_valid


# ---------------------------------------------------------------------------
# Valid DAG
# ---------------------------------------------------------------------------


def test_dag_linear_chain_is_valid() -> None:
    doc = _doc({"edges": [
        {"from": "a", "to": "b", "type": "blocks"},
        {"from": "b", "to": "c", "type": "blocks"},
    ]})
    report = validate(doc, dag=True)
    assert report.is_valid, report.errors


def test_dag_diamond_is_valid() -> None:
    doc = {
        "xBRIEFInfo": {"version": "0.8"},
        "plan": {
            "title": "T", "status": "running",
            "items": [
                {"id": "a", "title": "A", "status": "pending"},
                {"id": "b", "title": "B", "status": "pending"},
                {"id": "c", "title": "C", "status": "pending"},
                {"id": "d", "title": "D", "status": "pending"},
            ],
            "edges": [
                {"from": "a", "to": "b"},
                {"from": "a", "to": "c"},
                {"from": "b", "to": "d"},
                {"from": "c", "to": "d"},
            ],
        },
    }
    report = validate(doc, dag=True)
    assert report.is_valid, report.errors


# ---------------------------------------------------------------------------
# Cycle detection
# ---------------------------------------------------------------------------


def test_dag_simple_cycle_reports_error() -> None:
    doc = _doc({"edges": [
        {"from": "a", "to": "b"},
        {"from": "b", "to": "c"},
        {"from": "c", "to": "a"},   # closes the cycle
    ]})
    report = validate(doc, dag=True)
    assert not report.is_valid
    codes = {i.code for i in report.errors}
    assert "dag_cycle" in codes


def test_dag_self_loop_reports_cycle() -> None:
    doc = _doc({"edges": [{"from": "a", "to": "a"}]})
    report = validate(doc, dag=True)
    assert not report.is_valid
    assert any(i.code == "dag_cycle" for i in report.errors)


def test_dag_cycle_path_is_plan_edges() -> None:
    doc = _doc({"edges": [
        {"from": "a", "to": "b"},
        {"from": "b", "to": "a"},
    ]})
    report = validate(doc, dag=True)
    cycle_issues = [i for i in report.errors if i.code == "dag_cycle"]
    assert len(cycle_issues) == 1
    assert cycle_issues[0].path == "plan.edges"


def test_dag_cycle_message_names_involved_items() -> None:
    doc = _doc({"edges": [
        {"from": "b", "to": "c"},
        {"from": "c", "to": "b"},
    ]})
    report = validate(doc, dag=True)
    cycle_issue = next(i for i in report.errors if i.code == "dag_cycle")
    assert "b" in cycle_issue.message
    assert "c" in cycle_issue.message


# ---------------------------------------------------------------------------
# Dangling references
# ---------------------------------------------------------------------------


def test_dag_dangling_from_reports_error() -> None:
    doc = _doc({"edges": [{"from": "ghost", "to": "a"}]})
    report = validate(doc, dag=True)
    assert not report.is_valid
    assert any(i.code == "dangling_edge_ref" and "from" in i.path for i in report.errors)


def test_dag_dangling_to_reports_error() -> None:
    doc = _doc({"edges": [{"from": "a", "to": "phantom"}]})
    report = validate(doc, dag=True)
    assert not report.is_valid
    assert any(i.code == "dangling_edge_ref" and "to" in i.path for i in report.errors)


def test_dag_dangling_edge_does_not_contribute_to_cycle_check() -> None:
    """A dangling edge is skipped; remaining valid edges must still be checked."""
    doc = _doc({"edges": [
        {"from": "ghost", "to": "a"},   # dangling — skipped
        {"from": "a", "to": "b"},       # clean
        {"from": "b", "to": "a"},       # clean — forms a cycle
    ]})
    report = validate(doc, dag=True)
    codes = {i.code for i in report.errors}
    assert "dangling_edge_ref" in codes
    assert "dag_cycle" in codes


# ---------------------------------------------------------------------------
# Malformed edge structures
# ---------------------------------------------------------------------------


def test_dag_edge_not_mapping_reports_error() -> None:
    doc = _doc({"edges": ["not-an-object"]})
    report = validate(doc, dag=True)
    assert any(i.code == "invalid_edge_structure" for i in report.errors)


def test_dag_edge_non_string_from_reports_error() -> None:
    doc = _doc({"edges": [{"from": 42, "to": "b"}]})
    report = validate(doc, dag=True)
    assert any(i.code == "invalid_edge_structure" and "from" in i.path for i in report.errors)


def test_dag_edge_missing_to_reports_error() -> None:
    doc = _doc({"edges": [{"from": "a"}]})   # "to" is None → not a string
    report = validate(doc, dag=True)
    assert any(i.code == "invalid_edge_structure" and "to" in i.path for i in report.errors)


# ---------------------------------------------------------------------------
# Nested subItem IDs are resolved
# ---------------------------------------------------------------------------


def test_dag_collect_ids_skips_non_mapping_items() -> None:
    """Non-Mapping entries in plan.items are skipped by _collect_ids (dag.py:122)."""
    doc = {
        "xBRIEFInfo": {"version": "0.8"},
        "plan": {
            "title": "T", "status": "running",
            "items": [42, "bad", None],  # all non-Mapping → skipped
            "edges": [{"from": "ghost", "to": "phantom"}],  # edges needed to invoke _collect_ids
        },
    }
    # Both edge endpoints are dangling (no IDs collected from non-Mapping items)
    report = validate(doc, dag=True)
    assert any(i.code == "dangling_edge_ref" for i in report.errors)


def test_dag_subitems_ids_are_valid_edge_targets() -> None:
    doc = {
        "xBRIEFInfo": {"version": "0.8"},
        "plan": {
            "title": "T", "status": "running",
            "items": [
                {
                    "id": "parent",
                    "title": "Parent", "status": "pending",
                    "subItems": [
                        {"id": "child", "title": "Child", "status": "pending"},
                    ],
                },
            ],
            "edges": [{"from": "parent", "to": "child"}],
        },
    }
    report = validate(doc, dag=True)
    assert report.is_valid, report.errors


# ---------------------------------------------------------------------------
# dag=False (default) does NOT run DAG checks
# ---------------------------------------------------------------------------


def test_dag_cycle_not_reported_when_dag_false() -> None:
    doc = _doc({"edges": [
        {"from": "a", "to": "b"},
        {"from": "b", "to": "a"},
    ]})
    report = validate(doc)   # dag=False by default
    assert report.is_valid


# ---------------------------------------------------------------------------
# Class API: validate(dag=True), from_file(dag=True, strict=True)
# ---------------------------------------------------------------------------


def test_model_validate_with_dag_true_detects_cycle() -> None:
    doc = _doc({"edges": [{"from": "a", "to": "b"}, {"from": "b", "to": "a"}]})
    model = XBriefDocument.from_dict(doc)
    report = model.validate(dag=True)
    assert any(i.code == "dag_cycle" for i in report.errors)


def test_model_from_dict_strict_dag_raises_on_cycle() -> None:
    doc = _doc({"edges": [{"from": "a", "to": "b"}, {"from": "b", "to": "a"}]})
    with pytest.raises(ValidationError) as exc_info:
        XBriefDocument.from_dict(doc, strict=True, dag=True)
    assert any(i.code == "dag_cycle" for i in exc_info.value.report.errors)


def test_model_from_file_strict_dag_raises_on_cycle(tmp_path: Path) -> None:
    import json
    doc = _doc({"edges": [{"from": "a", "to": "b"}, {"from": "b", "to": "a"}]})
    path = tmp_path / "cycle.xbrief.json"
    path.write_text(json.dumps(doc), encoding="utf-8")
    with pytest.raises(ValidationError):
        XBriefDocument.from_file(path, strict=True, dag=True)


# ---------------------------------------------------------------------------
# Fixture files
# ---------------------------------------------------------------------------


def test_dag_plan_example_is_valid_dag(examples_dir: Path) -> None:
    doc = XBriefDocument.from_file(examples_dir / "dag-plan.xbrief.json")
    report = doc.validate(dag=True)
    assert report.is_valid, report.errors


def test_invalid_cycle_example_fails_dag_validation(examples_dir: Path) -> None:
    doc = XBriefDocument.from_file(examples_dir / "invalid-cycle.xbrief.json")
    report = doc.validate(dag=True)
    assert not report.is_valid
    assert any(i.code == "dag_cycle" for i in report.errors)


def test_minimal_plan_with_dag_true_is_valid(examples_dir: Path) -> None:
    """Plans with no edges pass DAG validation trivially."""
    doc = XBriefDocument.from_file(examples_dir / "minimal-plan.xbrief.json")
    report = doc.validate(dag=True)
    assert report.is_valid, report.errors
