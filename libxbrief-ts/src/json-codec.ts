import type { JsonObject, JsonValue } from "./types.js";
import { isRecordLike, sortJsonValue } from "./utils.js";

/**
 * Parse JSON text into a plain object.
 */
export function parseJson(text: string): JsonObject {
  const data: unknown = JSON.parse(text);
  if (!isRecordLike(data)) {
    throw new Error("xBRIEF JSON document must be an object");
  }
  return data as JsonObject;
}

/**
 * Serialize a document using canonical or preserve mode.
 */
export function dumpsJson(
  document: Record<string, unknown>,
  options: { canonical?: boolean; preserveFormat?: boolean } = {},
): string {
  const canonical = options.canonical ?? true;
  const preserveFormat = options.preserveFormat ?? false;
  const payload =
    preserveFormat ? document : (canonical ? (sortJsonValue(document as JsonValue) as JsonObject) : document);
  return `${JSON.stringify(payload, null, 2)}\n`;
}
