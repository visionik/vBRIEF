from __future__ import annotations

from libxbrief.builder import from_items, quick_todo
from libxbrief.models import PlanItem


def test_quick_todo_coerces_strings_to_pending_items() -> None:
    document = quick_todo("Todo", ["one", "two"])

    assert document.plan.title == "Todo"
    assert [item.status for item in document.plan.items] == ["pending", "pending"]
    assert document.validate().is_valid


def test_quick_todo_supports_mixed_strings_and_plan_items() -> None:
    existing = PlanItem.completed("done", id="done")

    document = quick_todo("Todo", ["next", existing], status="running")

    assert document.plan.status == "running"
    assert document.plan.items[0].title == "next"
    assert document.plan.items[1] is existing
    assert document.validate().is_valid


def test_quick_todo_allows_empty_lists() -> None:
    document = quick_todo("Todo", [])

    assert document.plan.items == []
    assert document.validate().is_valid


def test_from_items_uses_plan_items_without_mutating_them() -> None:
    item = PlanItem.pending("Task", id="task", metadata={"owner": "alice"})
    before = item.to_dict()

    document = from_items("Plan", [item], status="running")

    assert document.plan.items[0] is item
    assert item.to_dict() == before
    assert document.validate().is_valid
