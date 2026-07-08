"""Fuzz and property-based tests for libxbrief.

Uses stdlib random to generate randomised inputs — no external dependencies.
Each test runs many iterations with varied inputs to surface edge cases.
"""

from __future__ import annotations

import json
import random
import string
from typing import Any

from libxbrief import PlanBuilder, XBriefDocument, dumps, loads, validate
from libxbrief.builder import _slugify
from libxbrief.compat import VALID_STATUSES
from libxbrief.models import PlanItem

_RNG = random.Random(42)  # deterministic seed for reproducibility
_ITERATIONS = 200
_STATUSES = sorted(VALID_STATUSES)


def _random_string(min_len: int = 0, max_len: int = 60) -> str:
    length = _RNG.randint(min_len, max_len)
    chars = string.ascii_letters + string.digits + " !@#$%^&*()-_=+[]{}|;:',.<>?/\\\"\n\t"
    return "".join(_RNG.choice(chars) for _ in range(length))


def _random_status() -> str:
    return _RNG.choice(_STATUSES)


def _random_id() -> str:
    parts = _RNG.randint(1, 4)
    return ".".join(
        "".join(_RNG.choice(string.ascii_lowercase + string.digits + "-_") for _ in range(_RNG.randint(1, 12)))
        for _ in range(parts)
    )


# ---------------------------------------------------------------------------
# Slugify fuzz
# ---------------------------------------------------------------------------


def test_slugify_never_returns_empty_for_nonempty_ascii() -> None:
    for _ in range(_ITERATIONS):
        text = _random_string(1, 80)
        slug = _slugify(text)
        # Slug is either a valid non-empty string or the fallback "item"
        assert len(slug) > 0
        assert slug == slug.lower()
        assert " " not in slug


def test_slugify_idempotent() -> None:
    for _ in range(_ITERATIONS):
        text = _random_string(1, 40)
        first = _slugify(text)
        second = _slugify(first)
        assert first == second


# ---------------------------------------------------------------------------
# PlanItem factory fuzz
# ---------------------------------------------------------------------------


def test_plan_item_factories_always_produce_valid_status() -> None:
    factories = [PlanItem.pending, PlanItem.running, PlanItem.completed,
                 PlanItem.blocked, PlanItem.cancelled, PlanItem.draft]
    for _ in range(_ITERATIONS):
        factory = _RNG.choice(factories)
        title = _random_string(0, 50)
        item = factory(title)
        assert item.status in VALID_STATUSES
        assert item.title == title


# ---------------------------------------------------------------------------
# Builder fuzz — random plans should validate without crashes
# ---------------------------------------------------------------------------


def test_builder_random_plans_do_not_crash() -> None:
    for _ in range(_ITERATIONS // 2):
        builder = PlanBuilder(
            _random_string(1, 30),
            status=_random_status(),
            strict=False,
        )
        num_items = _RNG.randint(0, 8)
        for j in range(num_items):
            item = builder.add_item(
                _random_string(1, 20),
                id=_random_id(),
                status=_random_status(),
            )
            num_subs = _RNG.randint(0, 3)
            for _ in range(num_subs):
                item.add_subitem(
                    _random_string(1, 15),
                    status=_random_status(),
                )

        doc = builder.to_document()
        # Should never raise
        doc.validate()
        doc.validate(dag=True)


# ---------------------------------------------------------------------------
# Validation fuzz — garbage input should never crash, only produce issues
# ---------------------------------------------------------------------------


def _random_garbage() -> Any:
    """Generate a random JSON-compatible value."""
    choice = _RNG.randint(0, 6)
    if choice == 0:
        return None
    if choice == 1:
        return _RNG.randint(-1000, 1000)
    if choice == 2:
        return _random_string(0, 30)
    if choice == 3:
        return [_random_garbage() for _ in range(_RNG.randint(0, 3))]
    if choice == 4:
        return {_random_string(1, 8): _random_garbage() for _ in range(_RNG.randint(0, 3))}
    if choice == 5:
        return _RNG.random()
    return _RNG.choice([True, False])


def test_validate_never_crashes_on_garbage_input() -> None:
    for _ in range(_ITERATIONS):
        garbage = _random_garbage()
        # Must never raise — just return a report
        report = validate(garbage)
        assert report is not None


def test_validate_dict_with_random_xbrief_info() -> None:
    for _ in range(_ITERATIONS):
        doc: dict[str, Any] = {
            "xBRIEFInfo": _random_garbage(),
            "plan": _random_garbage(),
        }
        report = validate(doc)
        assert report is not None


# ---------------------------------------------------------------------------
# Round-trip fuzz — build, serialize, deserialize, compare
# ---------------------------------------------------------------------------


def test_round_trip_preserves_data_for_valid_plans() -> None:
    for _ in range(_ITERATIONS // 2):
        builder = PlanBuilder(
            _random_string(1, 25),
            status=_random_status(),
            strict=False,
        )
        num_items = _RNG.randint(1, 5)
        for _ in range(num_items):
            builder.add_item(
                _random_string(1, 20),
                id=_random_id(),
                status=_random_status(),
            )

        doc = builder.to_document()
        text = dumps(doc)
        loaded = loads(text)
        rebuilt = XBriefDocument.from_dict(loaded)

        assert rebuilt.plan.title == doc.plan.title
        assert rebuilt.plan.status == doc.plan.status
        assert len(rebuilt.plan.items) == len(doc.plan.items)


# ---------------------------------------------------------------------------
# JSON serialization fuzz — ensure no crashes on weird titles
# ---------------------------------------------------------------------------


def test_json_serialization_handles_special_characters() -> None:
    special_titles = [
        'Title with "quotes"',
        "Title with\nnewlines",
        "Title with\ttabs",
        "Title with \\backslashes\\",
        "Title with unicode: 日本語",
        "Title with emoji: 🚀",
        "",
        " " * 100,
        "a" * 1000,
        'nested {"json": true}',
    ]
    for title in special_titles:
        doc = PlanBuilder(title, status="draft", strict=False).to_document()
        text = dumps(doc)
        parsed = json.loads(text)
        assert parsed["plan"]["title"] == title


# ---------------------------------------------------------------------------
# Deep nesting fuzz
# ---------------------------------------------------------------------------


def test_deep_nesting_does_not_crash() -> None:
    builder = PlanBuilder("Deep Plan", status="running")
    current = builder.add_item("Level 0", id="l0", status="pending")
    for depth in range(1, 20):
        current = current.add_subitem(f"Level {depth}", status="pending")

    doc = builder.to_document()
    assert doc.validate().is_valid
    text = dumps(doc)
    loaded = loads(text)
    rebuilt = XBriefDocument.from_dict(loaded)
    assert rebuilt.plan.title == "Deep Plan"
