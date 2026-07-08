"""
Fixture-based integration tests for libxbrief.

Each test loads a real .xbrief.json file from examples/ and exercises the
dict API, class API, validation, and round-trip behaviour against it.
"""

from __future__ import annotations

import json
from pathlib import Path

from libxbrief import XBriefDocument, load_file, loads, validate


# ---------------------------------------------------------------------------
# minimal-plan.xbrief.json — simplest valid v0.8 document
# ---------------------------------------------------------------------------


def test_minimal_plan_is_valid(examples_dir: Path) -> None:
    doc = load_file(examples_dir / "minimal-plan.xbrief.json")

    report = validate(doc)

    assert report.is_valid, report.errors


def test_minimal_plan_model_round_trip(examples_dir: Path) -> None:
    path = examples_dir / "minimal-plan.xbrief.json"
    model = XBriefDocument.from_file(path)

    assert model.plan.title == "Daily Tasks"
    assert model.plan.status == "running"
    assert len(model.plan.items) == 3

    # Round-trip: to_dict should equal the original loaded dict
    original = load_file(path)
    assert model.to_dict() == original


def test_minimal_plan_canonical_output_is_deterministic(examples_dir: Path, tmp_path: Path) -> None:
    model = XBriefDocument.from_file(examples_dir / "minimal-plan.xbrief.json")

    out1 = model.to_json(canonical=True)
    out2 = model.to_json(canonical=True)

    assert out1 == out2
    assert out1.endswith("\n")
    parsed = json.loads(out1)
    keys = list(parsed.keys())
    assert keys == sorted(keys)


# ---------------------------------------------------------------------------
# dag-plan.xbrief.json — optional plan fields: id, edges, narratives, tags
# ---------------------------------------------------------------------------


def test_dag_plan_is_valid(examples_dir: Path) -> None:
    doc = load_file(examples_dir / "dag-plan.xbrief.json")

    report = validate(doc)

    assert report.is_valid, report.errors


def test_dag_plan_optional_fields_preserved(examples_dir: Path) -> None:
    model = XBriefDocument.from_file(examples_dir / "dag-plan.xbrief.json")

    assert model.plan.id == "build-pipeline"
    assert model.plan.tags == ["cicd", "pipeline", "automation"]
    assert model.plan.edges is not None
    assert len(model.plan.edges) == 6

    result = model.to_dict()
    assert result["plan"]["edges"] == model.plan.edges


def test_dag_plan_item_ids_validated(examples_dir: Path) -> None:
    doc = load_file(examples_dir / "dag-plan.xbrief.json")

    report = validate(doc)

    # All item IDs like "lint", "test", "build" are valid hierarchical IDs
    id_errors = [i for i in report.errors if i.code == "invalid_id_format"]
    assert id_errors == []


# ---------------------------------------------------------------------------
# structured-plan.xbrief.json — item-level priority, proposed status
# ---------------------------------------------------------------------------


def test_structured_plan_is_valid(examples_dir: Path) -> None:
    doc = load_file(examples_dir / "structured-plan.xbrief.json")

    report = validate(doc)

    assert report.is_valid, report.errors


def test_structured_plan_item_optional_fields_round_trip(examples_dir: Path) -> None:
    model = XBriefDocument.from_file(examples_dir / "structured-plan.xbrief.json")

    assert model.plan.status == "proposed"
    priorities = [item.priority for item in model.plan.items if item.priority is not None]
    assert "high" in priorities

    result = model.to_dict()
    assert result["plan"]["items"][0]["priority"] == "high"


# ---------------------------------------------------------------------------
# retrospective-plan.xbrief.json — item narrative, completed timestamps
# ---------------------------------------------------------------------------


def test_retrospective_plan_is_valid(examples_dir: Path) -> None:
    doc = load_file(examples_dir / "retrospective-plan.xbrief.json")

    report = validate(doc)

    assert report.is_valid, report.errors


def test_retrospective_plan_item_narrative_and_completed_preserved(examples_dir: Path) -> None:
    model = XBriefDocument.from_file(examples_dir / "retrospective-plan.xbrief.json")

    first = model.plan.items[0]
    assert first.completed is not None
    assert first.narrative is not None

    result = model.to_dict()
    assert result["plan"]["items"][0]["completed"] == first.completed
    assert result["plan"]["items"][0]["narrative"] == first.narrative


# ---------------------------------------------------------------------------
# prd.xbrief.json — v0.8 example migrated from legacy prd.json
# (Previously tested top-level 'type'/'kind' as unknown fields; those were intentionally moved into metadata or removed for v0.8 alignment. General unknown-field preservation is covered in e2e tests.)
# ---------------------------------------------------------------------------


def test_prd_plan_is_valid(examples_dir: Path) -> None:
    doc = load_file(examples_dir / "prd.xbrief.json")

    report = validate(doc)

    assert report.is_valid, report.errors


def test_prd_plan_item_count(examples_dir: Path) -> None:
    model = XBriefDocument.from_file(examples_dir / "prd.xbrief.json")
    assert len(model.plan.items) == 62


# ---------------------------------------------------------------------------
# invalid-cycle.xbrief.json — structurally valid; cycle is DAG-level (out of scope v1)
# ---------------------------------------------------------------------------


def test_invalid_cycle_is_structurally_valid(examples_dir: Path) -> None:
    """DAG cycle detection is out of scope in v1; document must pass libxbrief validation."""
    doc = load_file(examples_dir / "invalid-cycle.xbrief.json")

    report = validate(doc)

    assert report.is_valid, report.errors


# ---------------------------------------------------------------------------
# warp.xbrief.json — v0.4 legacy format; must fail validation
# ---------------------------------------------------------------------------


def test_warp_xbrief_fails_validation_wrong_version(repo_root: Path) -> None:
    doc = load_file(repo_root / "warp.xbrief.json")

    report = validate(doc)

    assert not report.is_valid
    codes = {i.code for i in report.errors}
    assert "invalid_version" in codes


def test_warp_xbrief_fails_validation_missing_plan(repo_root: Path) -> None:
    doc = load_file(repo_root / "warp.xbrief.json")

    report = validate(doc)

    paths = {i.path for i in report.errors}
    assert "plan" in paths


def test_warp_xbrief_loads_leniently(repo_root: Path) -> None:
    """Lenient mode must load without raising even for invalid docs."""
    doc = loads((repo_root / "warp.xbrief.json").read_text(encoding="utf-8"))

    assert doc["xBRIEFInfo"]["version"] == "0.4"
    assert "playbook" in doc
