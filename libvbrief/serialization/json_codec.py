"""JSON parse/emit helpers for vBRIEF documents."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from libvbrief.types import JSONObject, JSONValue


def parse_json(text: str) -> JSONObject:
    """Parse JSON text into a Python mapping."""
    data = json.loads(text)
    if not isinstance(data, dict):
        raise ValueError("vBRIEF JSON document must be an object")
    return data


def load_json_file(path: str | Path) -> JSONObject:
    """Load and parse a JSON document from disk."""
    content = Path(path).read_text(encoding="utf-8")
    return parse_json(content)


def dumps_json(
    document: Mapping[str, JSONValue] | dict[str, Any],
    *,
    canonical: bool = True,
    preserve_format: bool = False,
) -> str:
    """Serialize a JSON document using canonical or preserve mode."""
    if preserve_format and isinstance(document, Mapping):
        rendered = json.dumps(document, ensure_ascii=False, indent=2, sort_keys=False)
        return f"{rendered}\n"

    rendered = json.dumps(document, ensure_ascii=False, indent=2, sort_keys=canonical)
    return f"{rendered}\n"


def dump_json_file(
    path: str | Path,
    document: Mapping[str, JSONValue] | dict[str, Any],
    *,
    canonical: bool = True,
    preserve_format: bool = False,
) -> None:
    """Write JSON document to disk using configured writer mode."""
    output = dumps_json(document, canonical=canonical, preserve_format=preserve_format)
    Path(path).write_text(output, encoding="utf-8")
