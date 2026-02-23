from __future__ import annotations

from libvbrief import validate


def test_validation_paths_are_specific_for_nested_items() -> None:
    doc = {
        "vBRIEFInfo": {"version": "0.5"},
        "plan": {
            "title": "Nested",
            "status": "running",
            "items": [
                {
                    "title": "Parent",
                    "status": "pending",
                    "subItems": [{"title": "Child", "status": "bad-status"}],
                }
            ],
        },
    }

    report = validate(doc)

    paths = {issue.path for issue in report.errors}
    assert "plan.items[0].subItems[0].status" in paths
