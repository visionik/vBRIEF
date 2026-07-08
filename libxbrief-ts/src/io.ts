import { ValidationError } from "./errors.js";
import { dumpsJson, parseJson } from "./json-codec.js";
import { validateDocument } from "./validation.js";
import { isRecordLike } from "./utils.js";

export interface LoadOptions {
  strict?: boolean;
  dag?: boolean;
}

export interface DumpOptions {
  canonical?: boolean;
  preserveFormat?: boolean;
}

/**
 * Load a xBRIEF JSON document from a string.
 */
export function loads(text: string, options: LoadOptions = {}): Record<string, unknown> {
  const document = parseJson(text);
  if (options.strict) {
    raiseOnInvalid(document, options.dag ?? false);
  }
  return document;
}

/**
 * Serialize a document or model object to JSON text.
 */
export function dumps(document: unknown, options: DumpOptions = {}): string {
  const payload = coerceToDict(document, options.preserveFormat ?? false);
  return dumpsJson(payload, options);
}

/**
 * Validate a dict document or model object.
 */
export function validate(document: unknown, options: { dag?: boolean } = {}) {
  return validateDocument(document, options);
}

export function coerceToDict(document: unknown, preserveOrder: boolean): Record<string, unknown> {

  if (typeof document === "object" && document !== null) {
    const candidate = document as { toDict?: (options?: { preserveOrder?: boolean }) => unknown };
    if (typeof candidate.toDict === "function") {
      const output = candidate.toDict({ preserveOrder });
      if (isRecordLike(output)) {
        return output;
      }
    }
  }

  if (isRecordLike(document)) {
    return { ...document };
  }

  throw new TypeError("document must be a mapping or provide to_dict()");
}

function raiseOnInvalid(document: Record<string, unknown>, dag: boolean): void {
  const report = validateDocument(document, { dag });
  if (!report.isValid) {
    throw new ValidationError(report);
  }
}
