from __future__ import annotations

from libxbrief import (
    PlanBuilder,
    PlanItem,
    XBriefDocument,
    dump_file,
    dumps,
    from_items,
    load_file,
    loads,
    quick_todo,
)


def test_public_exports_are_available() -> None:
    builder = PlanBuilder("Plan", status="running")
    document = quick_todo("Todo", ["one"])
    from_items_document = from_items("Plan", [PlanItem.pending("Task", id="task")])

    assert builder.to_document().plan.title == "Plan"
    assert document.plan.items[0].title == "one"
    assert from_items_document.plan.items[0].id == "task"


def test_plan_builder_round_trip_via_public_api() -> None:
    builder = PlanBuilder("Launch Plan", status="running", tags=["mvp"])
    design = builder.add_item("Design Phase", id="design", status="completed")
    design.add_subitem("System Architecture", status="completed")
    builder.add_item("Authentication", id="auth", status="pending")
    builder.add_item("API", id="api", status="pending")
    builder.add_narrative("Proposal", "Build and ship")
    builder.add_edges_from([("design", "auth", "blocks"), ("design", "api", "blocks")])

    document = builder.to_document()
    assert document.validate(dag=True).is_valid

    text = dumps(document)
    rebuilt = XBriefDocument.from_dict(loads(text))

    assert rebuilt.to_dict() == document.to_dict()


def test_public_api_supports_mixing_builder_and_direct_plan_items() -> None:
    builder = PlanBuilder("Mixed Plan", status="running")
    built = builder.add_item("Built Task", id="built", status="completed")
    built.add_subitem("Nested Built Task")
    document = builder.to_document()

    manual_item = PlanItem.pending("Manual Task", id="manual")
    mixed_document = from_items(
        "Mixed Plan",
        [*document.plan.items, manual_item],
        status="running",
        tags=["mixed"],
    )

    assert mixed_document.validate(dag=True).is_valid
    assert mixed_document.plan.items[-1] is manual_item
    assert mixed_document.plan.tags == ["mixed"]


def test_quick_todo_round_trips_through_file_io(tmp_path) -> None:
    document = quick_todo("Todo", ["one", "two"])
    path = tmp_path / "todo.xbrief.json"

    dump_file(document, path)
    loaded = load_file(path)

    assert loaded["plan"]["title"] == "Todo"
    assert loaded["plan"]["items"][0]["title"] == "one"
