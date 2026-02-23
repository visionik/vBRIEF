from __future__ import annotations

from libvbrief import VBriefDocument, validate


def test_model_from_dict_and_to_dict_preserves_unknown_fields() -> None:
    doc = {
        "vBRIEFInfo": {"version": "0.5", "x-info": "value"},
        "plan": {
            "title": "Plan",
            "status": "running",
            "items": [
                {
                    "title": "Task",
                    "status": "pending",
                    "metadata": {"k": "v"},
                    "x-item": 1,
                }
            ],
            "x-plan": {"hello": True},
        },
        "x-root": [1, 2, 3],
    }

    model = VBriefDocument.from_dict(doc)
    rendered = model.to_dict()

    assert rendered["x-root"] == [1, 2, 3]
    assert rendered["plan"]["x-plan"] == {"hello": True}
    assert rendered["plan"]["items"][0]["x-item"] == 1


def test_model_validation_returns_report() -> None:
    model = VBriefDocument.from_dict(
        {
            "vBRIEFInfo": {"version": "0.5"},
            "plan": {"title": "P", "status": "running", "items": [{"title": "x", "status": "pending"}]},
        }
    )

    report = model.validate()

    assert report.is_valid
    assert validate(model).is_valid


def test_model_preserve_order_uses_original_field_order() -> None:
    source = {
        "vBRIEFInfo": {"version": "0.5"},
        "plan": {
            "title": "P",
            "status": "running",
            "items": [],
            "z": 1,
            "a": 2,
        },
    }

    model = VBriefDocument.from_dict(source)
    text = model.to_json(canonical=False, preserve_format=True)

    assert text.index('"z"') < text.index('"a"')
