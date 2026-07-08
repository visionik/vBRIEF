from __future__ import annotations

from libxbrief import XBriefDocument, dumps, loads
from libxbrief.builder import PlanBuilder


def _build_plan(*, strict: bool = True) -> PlanBuilder:
    builder = PlanBuilder("Launch Plan", status="running", strict=strict, tags=["mvp"])
    design = builder.add_item("Design Phase", id="design", status="completed")
    design.add_subitem("System Architecture", status="completed")
    builder.add_item("Infrastructure Setup", id="infra", status="completed")
    builder.add_item("Authentication", id="auth", status="pending")
    builder.add_item("API", id="api", status="pending")
    builder.add_narrative("Proposal", "Build and ship")
    builder.add_edges_from(
        [
            ("design", "auth", "blocks"),
            ("infra", "auth", "blocks"),
            ("design", "api", "blocks"),
        ]
    )
    return builder


def test_plan_builder_context_manager_and_plain_object_match() -> None:
    plain = _build_plan().to_document().to_dict()

    with PlanBuilder("Launch Plan", status="running", tags=["mvp"]) as builder:
        design = builder.add_item("Design Phase", id="design", status="completed")
        design.add_subitem("System Architecture", status="completed")
        builder.add_item("Infrastructure Setup", id="infra", status="completed")
        builder.add_item("Authentication", id="auth", status="pending")
        builder.add_item("API", id="api", status="pending")
        builder.add_narrative("Proposal", "Build and ship")
        builder.add_edges_from(
            [
                ("design", "auth", "blocks"),
                ("infra", "auth", "blocks"),
                ("design", "api", "blocks"),
            ]
        )

    contextual = builder.to_document().to_dict()

    assert plain == contextual


def test_plan_builder_plan_narratives_and_validation() -> None:
    document = _build_plan().to_document()

    assert document.plan.narratives == {"Proposal": "Build and ship"}
    assert document.validate(dag=True).is_valid


def test_plan_builder_unknown_edge_id_raises_when_strict_true() -> None:
    builder = PlanBuilder("Plan", status="running")
    builder.add_item("Task", id="task")

    try:
        builder.add_edges_from([("task", "missing", "blocks")])
    except ValueError as exc:
        assert "unknown target id" in str(exc)
    else:
        raise AssertionError("expected unknown edge target to raise")


def test_plan_builder_unknown_edge_id_is_deferred_when_strict_false() -> None:
    builder = PlanBuilder("Plan", status="running", strict=False)
    builder.add_item("Task", id="task")
    builder.add_edges_from([("task", "missing", "blocks")])

    report = builder.to_document().validate(dag=True)

    assert not report.is_valid
    assert any(issue.code == "dangling_edge_ref" for issue in report.errors)


def test_plan_builder_round_trips_through_json_helpers() -> None:
    document = _build_plan().to_document()

    text = dumps(document)
    loaded = loads(text)
    rebuilt = XBriefDocument.from_dict(loaded)

    assert rebuilt.plan.title == "Launch Plan"
    assert rebuilt.plan.tags == ["mvp"]
    assert rebuilt.plan.items[0].subItems[0].title == "System Architecture"


def test_plan_builder_to_document_is_idempotent() -> None:
    builder = _build_plan()

    first = builder.to_document().to_dict()
    second = builder.to_document().to_dict()

    assert first == second
