from __future__ import annotations

from libxbrief.models import PlanItem


def test_plan_item_status_factories_set_expected_status() -> None:
    assert PlanItem.pending("Task").status == "pending"
    assert PlanItem.running("Task").status == "running"
    assert PlanItem.completed("Task").status == "completed"
    assert PlanItem.blocked("Task").status == "blocked"
    assert PlanItem.cancelled("Task").status == "cancelled"
    assert PlanItem.draft("Task").status == "draft"


def test_plan_item_status_factories_pass_kwargs_through() -> None:
    item = PlanItem.pending(
        "Fix bug",
        id="fix",
        priority="high",
        tags=["bugs"],
        metadata={"owner": "alice"},
    )

    assert item.id == "fix"
    assert item.priority == "high"
    assert item.tags == ["bugs"]
    assert item.metadata == {"owner": "alice"}


def test_plan_item_factory_with_empty_title() -> None:
    item = PlanItem.pending("")
    assert item.title == ""
    assert item.status == "pending"


def test_plan_item_factory_sets_title_correctly() -> None:
    for factory in (PlanItem.pending, PlanItem.running, PlanItem.completed,
                    PlanItem.blocked, PlanItem.cancelled, PlanItem.draft):
        item = factory("My Title")
        assert item.title == "My Title"


def test_plan_item_factory_all_optional_fields() -> None:
    item = PlanItem.blocked(
        "Blocked task",
        id="blk-1",
        uid="urn:uuid:abc",
        narrative={"reason": "waiting on API"},
        planRef="#other-plan",
        tags=["infra"],
        metadata={"team": "backend"},
        created="2026-01-01T00:00:00Z",
        updated="2026-01-02T00:00:00Z",
        priority="critical",
        dueDate="2026-02-01",
    )
    assert item.id == "blk-1"
    assert item.uid == "urn:uuid:abc"
    assert item.narrative == {"reason": "waiting on API"}
    assert item.planRef == "#other-plan"
    assert item.tags == ["infra"]
    assert item.priority == "critical"
    assert item.dueDate == "2026-02-01"


def test_plan_item_factory_round_trips_through_dict() -> None:
    item = PlanItem.completed("Ship it", id="ship", tags=["release"])
    d = item.to_dict()
    rebuilt = PlanItem.from_dict(d)
    assert rebuilt.title == "Ship it"
    assert rebuilt.status == "completed"
    assert rebuilt.id == "ship"
    assert rebuilt.tags == ["release"]


def test_plan_item_factory_returns_planitem_type() -> None:
    for factory in (PlanItem.pending, PlanItem.running, PlanItem.completed,
                    PlanItem.blocked, PlanItem.cancelled, PlanItem.draft):
        assert type(factory("x")) is PlanItem
