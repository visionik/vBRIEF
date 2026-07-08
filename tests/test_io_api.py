from __future__ import annotations

import json

import pytest

from libxbrief import ValidationError, dump_file, dumps, load_file, loads


def test_loads_lenient_mode_allows_invalid_doc() -> None:
    text = json.dumps({"xBRIEFInfo": {"version": "0.4"}, "plan": {"title": "x", "status": "oops", "items": []}})

    doc = loads(text, strict=False)

    assert doc["xBRIEFInfo"]["version"] == "0.4"


def test_loads_strict_mode_raises() -> None:
    text = json.dumps({"xBRIEFInfo": {"version": "0.4"}, "plan": {"title": "x", "status": "oops", "items": []}})

    with pytest.raises(ValidationError):
        loads(text, strict=True)


def test_file_io_round_trip(tmp_path) -> None:
    source = {
        "xBRIEFInfo": {"version": "0.8"},
        "plan": {"title": "R", "status": "running", "items": [{"title": "a", "status": "pending"}]},
    }

    path = tmp_path / "doc.xbrief.json"
    dump_file(source, path)

    loaded = load_file(path)
    assert loaded == source


def test_load_file_strict_raises(tmp_path) -> None:
    bad = {"xBRIEFInfo": {"version": "0.4"}, "plan": {"title": "x", "status": "oops", "items": []}}
    path = tmp_path / "bad.xbrief.json"
    dump_file(bad, path)

    with pytest.raises(ValidationError):
        load_file(path, strict=True)


def test_dumps_with_model_object() -> None:
    from libxbrief import XBriefDocument

    model = XBriefDocument.from_dict({
        "xBRIEFInfo": {"version": "0.8"},
        "plan": {"title": "M", "status": "draft", "items": []},
    })

    text = dumps(model)

    assert json.loads(text)["plan"]["title"] == "M"


def test_dumps_preserve_mode_keeps_insertion_order() -> None:
    doc = {
        "xBRIEFInfo": {"version": "0.8"},
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


def test_dumps_coerce_to_dict_no_preserve_order_kwarg() -> None:
    """Object whose to_dict() doesn't accept preserve_order falls back gracefully (io.py:69-70)."""
    class NoKwarg:
        def to_dict(self) -> dict:  # noqa: ANN001
            return {
                "xBRIEFInfo": {"version": "0.8"},
                "plan": {"title": "NK", "status": "running", "items": []},
            }

    text = dumps(NoKwarg())

    assert json.loads(text)["plan"]["title"] == "NK"


def test_dumps_coerce_to_dict_no_to_dict_raises_type_error() -> None:
    """Object with no to_dict() raises TypeError (io.py:72)."""
    with pytest.raises(TypeError, match="document must be a mapping or provide to_dict"):
        dumps(object())


def test_parse_json_non_dict_raises_value_error() -> None:
    """parse_json raises ValueError when the root JSON value is not an object (json_codec.py:16)."""
    from libxbrief.serialization.json_codec import parse_json

    with pytest.raises(ValueError, match="xBRIEF JSON document must be an object"):
        parse_json("[1, 2, 3]")
