/**
 * Validation issue and report models.
 */

export type IssueSeverity = "error" | "warning";

export interface IssueInit {
  code: string;
  path: string;
  message: string;
  severity: IssueSeverity;
}

/**
 * A single validation issue.
 */
export class Issue {
  public readonly code: string;
  public readonly path: string;
  public readonly message: string;
  public readonly severity: IssueSeverity;

  public constructor(init: IssueInit) {
    this.code = init.code;
    this.path = init.path;
    this.message = init.message;
    this.severity = init.severity;
  }
}

/**
 * Structured validation output used by strict and lenient modes.
 */
export class ValidationReport {
  public readonly errors: Issue[] = [];
  public readonly warnings: Issue[] = [];

  public get isValid(): boolean {
    return this.errors.length === 0;
  }

  public addError(code: string, path: string, message: string): void {
    this.errors.push(new Issue({ code, path, message, severity: "error" }));
  }

  public addWarning(code: string, path: string, message: string): void {
    this.warnings.push(new Issue({ code, path, message, severity: "warning" }));
  }

  public extend(issues: Iterable<Issue>): void {
    for (const issue of issues) {
      if (issue.severity === "warning") {
        this.warnings.push(issue);
      } else {
        this.errors.push(issue);
      }
    }
  }
}
