from __future__ import annotations

from libxbrief import validate
from libxbrief.issues import ValidationReport


def test_validate_minimal_document_has_no_errors() -> None:
    doc = {
        "xBRIEFInfo": {"version": "0.8"},
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
    assert {issue.path for issue in report.errors} >= {"xBRIEFInfo", "plan"}


def test_validate_reports_plan_and_item_errors() -> None:
    doc = {
        "xBRIEFInfo": {"version": "0.4"},
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


def test_validate_non_mapping_document_returns_error() -> None:
    report = validate([1, 2, 3])

    assert not report.is_valid
    assert any(i.code == "invalid_document_type" for i in report.errors)


def test_validate_xbrief_info_not_dict_reports_error() -> None:
    doc = {"xBRIEFInfo": "not-a-dict", "plan": {"title": "T", "status": "running", "items": []}}

    report = validate(doc)

    assert any(i.code == "invalid_root_field_type" and "xBRIEFInfo" in i.path for i in report.errors)


def test_validate_plan_not_dict_reports_error() -> None:
    doc = {"xBRIEFInfo": {"version": "0.8"}, "plan": "not-a-dict"}

    report = validate(doc)

    assert any(i.code == "invalid_root_field_type" and i.path == "plan" for i in report.errors)


def test_validate_plan_missing_required_fields() -> None:
    doc = {"xBRIEFInfo": {"version": "0.8"}, "plan": {}}

    report = validate(doc)
    codes = {i.code for i in report.errors}

    assert "missing_plan_field" in codes
    paths = {i.path for i in report.errors}
    assert {"plan.title", "plan.status", "plan.items"} <= paths


def test_validate_items_not_list_reports_error() -> None:
    doc = {
        "xBRIEFInfo": {"version": "0.8"},
        "plan": {"title": "T", "status": "running", "items": "not-a-list"},
    }

    report = validate(doc)

    assert any(i.code == "invalid_plan_field_type" and i.path == "plan.items" for i in report.errors)


def test_validate_item_not_mapping_reports_error() -> None:
    doc = {
        "xBRIEFInfo": {"version": "0.8"},
        "plan": {"title": "T", "status": "running", "items": [42]},
    }

    report = validate(doc)

    assert any(i.code == "invalid_item_type" for i in report.errors)


def test_validate_item_missing_status_reports_error() -> None:
    doc = {
        "xBRIEFInfo": {"version": "0.8"},
        "plan": {"title": "T", "status": "running", "items": [{"title": "x"}]},
    }

    report = validate(doc)

    paths = {i.path for i in report.errors}
    assert "plan.items[0].status" in paths


def test_validate_subitems_not_list_reports_error() -> None:
    doc = {
        "xBRIEFInfo": {"version": "0.8"},
        "plan": {
            "title": "T",
            "status": "running",
            "items": [{"title": "x", "status": "pending", "subItems": "bad"}],
        },
    }

    report = validate(doc)

    assert any(i.code == "invalid_subitems_type" for i in report.errors)


def test_validation_report_add_warning_and_extend() -> None:
    report = ValidationReport()
    report.add_warning("some_code", "some.path", "a warning")

    assert len(report.warnings) == 1
    assert report.warnings[0].severity == "warning"
    assert report.is_valid  # warnings don't invalidate

    report2 = ValidationReport()
    report2.extend(report.warnings + report.errors)

    assert len(report2.warnings) == 1


def test_validation_report_extend_with_error_issue() -> None:
    """extend() with an error-severity issue appends to errors (issues.py:45)."""
    from libxbrief.issues import Issue

    report = ValidationReport()
    error_issue = Issue(code="some_error", path="p", message="m", severity="error")
    report.extend([error_issue])

    assert len(report.errors) == 1
    assert report.errors[0].code == "some_error"
    assert not report.is_valid


def test_validation_error_summary_truncates_many_errors() -> None:
    from libxbrief.errors import ValidationError

    report = ValidationReport()
    for i in range(5):
        report.add_error("some_code", f"path.{i}", f"error {i}")

    exc = ValidationError(report)

    assert "5 total errors" in str(exc)
