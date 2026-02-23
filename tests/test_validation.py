from __future__ import annotations

from libvbrief import validate


def test_validate_minimal_document_has_no_errors() -> None:
    doc = {
        "vBRIEFInfo": {"version": "0.5"},
        "plan": {
            "title": "Daily",
            "status": "running",
            "items": [{"title": "Task", "status": "pending"}],
        },
    }

    report = validate(doc)

    assert report.is_valid
    assert report.errors == []


def test_validate_reports_missing_root_fields() -> None:
    report = validate({})

    codes = {issue.code for issue in report.errors}
    assert "missing_root_field" in codes
    assert {issue.path for issue in report.errors} >= {"vBRIEFInfo", "plan"}


def test_validate_reports_plan_and_item_errors() -> None:
    doc = {
        "vBRIEFInfo": {"version": "0.4"},
        "plan": {
            "title": "Bad",
            "status": "inProgress",
            "id": "bad id",
            "items": [
                {
                    "title": "x",
                    "status": "inProgress",
                    "id": "bad id",
                    "planRef": "http://example.com/plan.json",
                },
                {"status": "pending"},
            ],
        },
    }

    report = validate(doc)
    codes = {issue.code for issue in report.errors}

    assert "invalid_version" in codes
    assert "invalid_plan_status" in codes
    assert "invalid_id_format" in codes
    assert "invalid_item_status" in codes
    assert "invalid_planref" in codes
    assert "missing_item_field" in codes
