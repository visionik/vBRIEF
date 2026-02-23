"""Shared type aliases for libvbrief."""

from __future__ import annotations

from typing import Any, Dict, List, TypeAlias, Union

JSONPrimitive: TypeAlias = Union[None, bool, int, float, str]
JSONValue: TypeAlias = Union[JSONPrimitive, Dict[str, "JSONValue"], List["JSONValue"]]
JSONObject: TypeAlias = Dict[str, JSONValue]

AnyMapping: TypeAlias = Dict[str, Any]
