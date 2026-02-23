"""High-level dict-first IO API for libvbrief."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

from libvbrief.errors import ValidationError
from libvbrief.issues import ValidationReport
from libvbrief.serialization.json_codec import dump_json_file, dumps_json, load_json_file, parse_json
from libvbrief.validation import validate_document


def loads(text: str, *, strict: bool = False) -> dict[str, Any]:
    """Load a vBRIEF JSON document from a string."""
    document = parse_json(text)
    if strict:
        _raise_on_invalid(document)
    return document


def load_file(path: str | Path, *, strict: bool = False) -> dict[str, Any]:
    """Load a vBRIEF JSON document from a UTF-8 file."""
    document = load_json_file(path)
    if strict:
        _raise_on_invalid(document)
    return document


def dumps(
    document: Mapping[str, Any] | Any,
    *,
    canonical: bool = True,
    preserve_format: bool = False,
) -> str:
    """Serialize a document or model object to JSON text."""
    payload = _coerce_to_dict(document, preserve_order=preserve_format)
    return dumps_json(payload, canonical=canonical, preserve_format=preserve_format)


def dump_file(
    document: Mapping[str, Any] | Any,
    path: str | Path,
    *,
    canonical: bool = True,
    preserve_format: bool = False,
) -> None:
    """Serialize a document or model object to JSON file."""
    payload = _coerce_to_dict(document, preserve_order=preserve_format)
    dump_json_file(path, payload, canonical=canonical, preserve_format=preserve_format)


def validate(document: Mapping[str, Any] | Any) -> ValidationReport:
    """Validate a dict document or model object."""
    return validate_document(document)


def _coerce_to_dict(document: Mapping[str, Any] | Any, *, preserve_order: bool) -> dict[str, Any]:
    if isinstance(document, Mapping):
        return dict(document)

    to_dict = getattr(document, "to_dict", None)
    if callable(to_dict):
        try:
            return to_dict(preserve_order=preserve_order)
        except TypeError:
            return to_dict()

    raise TypeError("document must be a mapping or provide to_dict()")


def _raise_on_invalid(document: Mapping[str, Any]) -> None:
    report = validate_document(document)
    if not report.is_valid:
        raise ValidationError(report)
