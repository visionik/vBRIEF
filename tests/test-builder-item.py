from __future__ import annotations

from libxbrief import validate
from libxbrief.builder import ItemBuilder, PlanBuilder, _slugify


def test_slugify_normalizes_text() -> None:
    assert _slugify("Design Phase") == "design-phase"
    assert _slugify("API   Contract!!!") == "api-contract"
    assert _slugify("   ") == "item"


def test_item_builder_add_subitem_supports_deep_nesting() -> None:
    root = ItemBuilder("Root Task", id="root")
    child = root.add_subitem("Child Task")
    grandchild = child.add_subitem("Grand Child Task")
    great_grandchild = grandchild.add_subitem("Great Grand Child Task")

    item = root.to_planitem()

    assert item.subItems[0].id == "root.child-task"
    assert item.subItems[0].subItems[0].id == "root.child-task.grand-child-task"
    assert great_grandchild.to_planitem().id == "root.child-task.grand-child-task.great-grand-child-task"


def test_item_builder_explicit_id_overrides_slug() -> None:
    root = ItemBuilder("Root", id="root")
    child = root.add_subitem("Ignored Title", id="root.custom")

    assert child.to_planitem().id == "root.custom"


def test_item_builder_add_narrative_accumulates_values() -> None:
    item = ItemBuilder("Task", id="task")

    item.add_narrative("Proposal", "Do the work")
    item.add_narrative("Risk", "Might slip")

    assert item.to_planitem().narrative == {
        "Proposal": "Do the work",
        "Risk": "Might slip",
    }


def test_item_builder_kwargs_round_trip_to_planitem() -> None:
    item = ItemBuilder(
        "Task",
        id="task",
        priority="high",
        tags=["alpha"],
        metadata={"owner": "alice"},
    )

    rendered = item.to_planitem().to_dict()

    assert rendered["priority"] == "high"
    assert rendered["tags"] == ["alpha"]
    assert rendered["metadata"] == {"owner": "alice"}


def test_item_builder_duplicate_id_raises_when_strict_true() -> None:
    root = ItemBuilder("Root", id="root")

    try:
        root.add_subitem("Child", id="root.child")
        root.add_subitem("Child again", id="root.child")
    except ValueError as exc:
        assert "Duplicate item id" in str(exc)
    else:
        raise AssertionError("expected duplicate ID to raise")


def test_item_builder_duplicate_id_is_deferred_when_strict_false() -> None:
    builder = PlanBuilder("Plan", strict=False, status="running")
    builder.add_item("Task", id="duplicate")
    builder.add_item("Task Again", id="duplicate")

    report = validate(builder.to_document())

    assert not report.is_valid
    assert any(issue.code == "duplicate_item_id" for issue in report.errors)


def test_item_builder_invalid_status_raises_when_strict_true() -> None:
    try:
        ItemBuilder("Task", id="task", status="not-a-status")
    except ValueError as exc:
        assert "Invalid status" in str(exc)
    else:
        raise AssertionError("expected invalid status to raise")


def test_plan_builder_invalid_status_raises_when_strict_true() -> None:
    try:
        PlanBuilder("Plan", status="not-a-status")
    except ValueError as exc:
        assert "Invalid status" in str(exc)
    else:
        raise AssertionError("expected invalid plan status to raise")
