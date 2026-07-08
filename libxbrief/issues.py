"""Validation issue and report models."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, List


@dataclass(frozen=True)
class Issue:
    """A single validation issue."""

    code: str
    path: str
    message: str
    severity: str


@dataclass
class ValidationReport:
    """Structured validation output used by strict and lenient modes."""

    errors: List[Issue] = field(default_factory=list)
    warnings: List[Issue] = field(default_factory=list)

    @property
    def is_valid(self) -> bool:
        """True when no errors were produced."""
        return not self.errors

    def add_error(self, code: str, path: str, message: str) -> None:
        """Append an error issue."""
        self.errors.append(Issue(code=code, path=path, message=message, severity="error"))

    def add_warning(self, code: str, path: str, message: str) -> None:
        """Append a warning issue."""
        self.warnings.append(Issue(code=code, path=path, message=message, severity="warning"))

    def extend(self, issues: Iterable[Issue]) -> None:
        """Append pre-built issues into report buckets by severity."""
        for issue in issues:
            if issue.severity == "warning":
                self.warnings.append(issue)
            else:
                self.errors.append(issue)
