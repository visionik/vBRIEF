import type { ValidationReport } from "./issues.js";

/**
 * Base exception for library-level failures.
 */
export class LibXBriefError extends Error {}

/**
 * Raised when strict-mode validation fails.
 */
export class ValidationError extends LibXBriefError {
  public readonly report: ValidationReport;

  public constructor(report: ValidationReport) {
    const preview = report.errors
      .slice(0, 3)
      .map((issue) => `${issue.path}: ${issue.message}`)
      .join("; ");
    const summary =
      report.errors.length > 3
        ? `${preview}; ... (${report.errors.length} total errors)`
        : preview || "validation failed";
    super(summary);
    this.name = "ValidationError";
    this.report = report;
  }
}
