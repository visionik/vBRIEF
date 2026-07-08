from __future__ import annotations

import json

import pytest

from libxbrief import ValidationError, XBriefDocument, validate


def test_model_from_dict_and_to_dict_preserves_unknown_fields() -> None:
    doc = {
        "xBRIEFInfo": {"version": "0.8", "x-info": "value"},
        "plan": {
            "title": "Plan",
            "status": "running",
            "items": [
                {
                    "title": "Task",
                    "status": "pending",
                    "metadata": {"k": "v"},
                    "x-item": 1,
                }
            ],
            "x-plan": {"hello": True},
        },
        "x-root": [1, 2, 3],
    }

    model = XBriefDocument.from_dict(doc)
    rendered = model.to_dict()

    assert rendered["x-root"] == [1, 2, 3]
    assert rendered["plan"]["x-plan"] == {"hello": True}
    assert rendered["plan"]["items"][0]["x-item"] == 1


def test_model_validation_returns_report() -> None:
    model = XBriefDocument.from_dict(
        {
            "xBRIEFInfo": {"version": "0.8"},
            "plan": {"title": "P", "status": "running", "items": [{"title": "x", "status": "pending"}]},
        }
    )

    report = model.validate()

    assert report.is_valid
    assert validate(model).is_valid


def test_model_preserve_order_uses_original_field_order() -> None:
    source = {
        "xBRIEFInfo": {"version": "0.8"},
        "plan": {
            "title": "P",
            "status": "running",
            "items": [],
            "z": 1,
            "a": 2,
        },
    }

    model = XBriefDocument.from_dict(source)
    text = model.to_json(canonical=False, preserve_format=True)

    assert text.index('"z"') < text.index('"a"')


def test_model_xbrief_info_extras_round_trip() -> None:
    """Unknown keys inside xBRIEFInfo must survive to_dict() and to_json()."""
    doc = {
        "xBRIEFInfo": {"version": "0.8", "x-generator": "myapp", "x-schema": "v1"},
        "plan": {"title": "P", "status": "running", "items": []},
    }

    model = XBriefDocument.from_dict(doc)
    result = model.to_dict()

    assert result["xBRIEFInfo"]["x-generator"] == "myapp"
    assert result["xBRIEFInfo"]["x-schema"] == "v1"
    # Also verify via JSON round-trip
    assert json.loads(model.to_json())["xBRIEFInfo"]["x-generator"] == "myapp"


def test_model_from_dict_strict_raises_on_invalid() -> None:
    with pytest.raises(ValidationError) as exc_info:
        XBriefDocument.from_dict({"xBRIEFInfo": {"version": "0.4"}, "plan": {"title": "x", "status": "oops", "items": []}}, strict=True)

    assert exc_info.value.report is not None
    assert not exc_info.value.report.is_valid


def test_model_from_json_round_trip() -> None:
    text = json.dumps({
        "xBRIEFInfo": {"version": "0.8"},
        "plan": {"title": "Q", "status": "draft", "items": []},
    })

    model = XBriefDocument.from_json(text)

    assert model.plan.title == "Q"
    assert model.plan.status == "draft"


def test_model_from_file_and_to_file_round_trip(tmp_path) -> None:
    source = {
        "xBRIEFInfo": {"version": "0.8"},
        "plan": {"title": "File", "status": "running", "items": [{"title": "T", "status": "pending"}]},
    }
    path = tmp_path / "plan.xbrief.json"
    model = XBriefDocument.from_dict(source)
    model.to_file(path)

    loaded = XBriefDocument.from_file(path)

    assert loaded.plan.title == "File"
    assert loaded.plan.items[0].title == "T"


def test_plan_item_from_dict_with_sub_items() -> None:
    from libxbrief.models import PlanItem

    data = {
        "title": "Parent",
        "status": "pending",
        "subItems": [
            {"title": "Child", "status": "running"},
            42,  # non-Mapping: intentionally skipped
        ],
    }

    item = PlanItem.from_dict(data)

    assert len(item.subItems) == 1
    assert item.subItems[0].title == "Child"


def test_plan_with_optional_fields_round_trips() -> None:
    doc = {
        "xBRIEFInfo": {"version": "0.8"},
        "plan": {
            "id": "proj.2026",
            "title": "Quarterly",
            "status": "running",
            "author": "alice",
            "tags": ["q1"],
            "items": [],
        },
    }

    model = XBriefDocument.from_dict(doc)
    result = model.to_dict()

    assert result["plan"]["id"] == "proj.2026"
    assert result["plan"]["author"] == "alice"
    assert result["plan"]["tags"] == ["q1"]


def test_plan_architecture_system_of_record_round_trips_as_known_field() -> None:
    architecture = {
        "systemOfRecord": {
            "stateSurfaces": [
                {
                    "name": "Workspace",
                    "classification": "durable_product_state",
                    "owner": "application database",
                    "approvedStorage": "postgres",
                    "permissionBoundary": "workspace membership",
                }
            ],
            "referenceApplications": [
                {
                    "name": "reference-app",
                    "evidence": ["database schema", "auth/session flow"],
                    "mustPreserve": ["database-backed records"],
                    "intentionallyNotCarriedForward": [],
                }
            ],
        }
    }
    doc = {
        "xBRIEFInfo": {"version": "0.8"},
        "plan": {
            "title": "Stateful feature",
            "status": "draft",
            "items": [],
            "architecture": architecture,
        },
    }

    model = XBriefDocument.from_dict(doc)
    result = model.to_dict()

    assert model.plan.architecture == architecture
    assert "architecture" not in model.plan.extras
    assert result["plan"]["architecture"] == architecture


def test_merge_values_includes_fields_added_after_parse() -> None:
    """Known fields set after from_dict (not in original _field_order) still appear in preserve-order output."""
    source = {
        "xBRIEFInfo": {"version": "0.8"},
        "plan": {"title": "P", "status": "running", "items": []},
    }
    model = XBriefDocument.from_dict(source)
    model.plan.author = "bob"  # set after parse; not in _field_order

    result = model.to_dict(preserve_order=True)

    assert result["plan"]["author"] == "bob"


# ---------------------------------------------------------------------------
# from_dict with non-Mapping input (lenient fallback to empty dict)
# ---------------------------------------------------------------------------


def test_plan_item_from_dict_non_mapping_returns_empty_item() -> None:
    """PlanItem.from_dict with a non-Mapping falls back to empty dict (models.py:110)."""
    from libxbrief.models import PlanItem

    item = PlanItem.from_dict(None)  # type: ignore[arg-type]

    assert item.title == ""
    assert item.status == ""
    assert item.subItems == []


def test_plan_from_dict_non_mapping_returns_empty_plan() -> None:
    """Plan.from_dict with a non-Mapping falls back to empty dict (models.py:195)."""
    from libxbrief.models import Plan

    plan = Plan.from_dict(42)  # type: ignore[arg-type]

    assert plan.title == ""
    assert plan.items == []


def test_xbrief_document_from_dict_non_mapping_returns_empty_doc() -> None:
    """XBriefDocument.from_dict with a non-Mapping falls back to empty dict (models.py:257)."""
    doc = XBriefDocument.from_dict(None)  # type: ignore[arg-type]

    assert doc.plan.title == ""
    assert doc.xbrief_info == {}


def test_xbrief_document_from_dict_non_dict_xbrief_info_becomes_empty() -> None:
    """When xBRIEFInfo is not a dict, it is silently replaced with {} (models.py:263)."""
    doc = XBriefDocument.from_dict(
        {"xBRIEFInfo": "not-a-dict", "plan": {"title": "T", "status": "running", "items": []}}
    )

    assert doc.xbrief_info == {}


def test_merge_values_extras_added_after_parse_appear_in_preserve_order_output() -> None:
    """Extras added programmatically (not in _field_order) are still emitted (models.py:431)."""
    model = XBriefDocument.from_dict(
        {"xBRIEFInfo": {"version": "0.8"}, "plan": {"title": "T", "status": "running", "items": []}}
    )
    model.extras["runtime_key"] = "runtime_value"  # not in _field_order

    result = model.to_dict(preserve_order=True)

    assert result["runtime_key"] == "runtime_value"
