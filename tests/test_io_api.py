from __future__ import annotations

import json

import pytest

from libvbrief import ValidationError, dump_file, dumps, load_file, loads


def test_loads_lenient_mode_allows_invalid_doc() -> None:
    text = json.dumps({"vBRIEFInfo": {"version": "0.4"}, "plan": {"title": "x", "status": "oops", "items": []}})

    doc = loads(text, strict=False)

    assert doc["vBRIEFInfo"]["version"] == "0.4"


def test_loads_strict_mode_raises() -> None:
    text = json.dumps({"vBRIEFInfo": {"version": "0.4"}, "plan": {"title": "x", "status": "oops", "items": []}})

    with pytest.raises(ValidationError):
        loads(text, strict=True)


def test_file_io_round_trip(tmp_path) -> None:
    source = {
        "vBRIEFInfo": {"version": "0.5"},
        "plan": {"title": "R", "status": "running", "items": [{"title": "a", "status": "pending"}]},
    }

    path = tmp_path / "doc.vbrief.json"
    dump_file(source, path)

    loaded = load_file(path)
    assert loaded == source


def test_dumps_preserve_mode_keeps_insertion_order() -> None:
    doc = {
        "vBRIEFInfo": {"version": "0.5"},
        "plan": {
            "title": "T",
            "status": "running",
            "items": [],
            "z": 1,
            "a": 2,
        },
    }

    rendered = dumps(doc, canonical=False, preserve_format=True)

    z_index = rendered.index('"z"')
    a_index = rendered.index('"a"')
    assert z_index < a_index
