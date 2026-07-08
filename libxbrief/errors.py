"""Custom exceptions for libxbrief."""

from __future__ import annotations

from libxbrief.issues import ValidationReport


class LibXBriefError(Exception):
    """Base exception for library-level failures."""


class ValidationError(LibXBriefError):
    """Raised when strict-mode validation fails."""

    def __init__(self, report: ValidationReport) -> None:
        self.report = report
        summary = "; ".join(f"{i.path}: {i.message}" for i in report.errors[:3])
        if len(report.errors) > 3:
            summary = f"{summary}; ... ({len(report.errors)} total errors)"
        super().__init__(summary or "validation failed")
