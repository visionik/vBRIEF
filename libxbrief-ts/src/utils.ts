import type { JsonObject, JsonValue, RecordLike } from "./types.js";

export function isRecordLike(value: unknown): value is RecordLike {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

export function sortJsonValue(value: JsonValue): JsonValue {
  if (Array.isArray(value)) {
    return value.map((item) => sortJsonValue(item)) as JsonValue;
  }

  if (isRecordLike(value)) {
    const sorted: JsonObject = {};
    for (const key of Object.keys(value).sort()) {
      const nested = value[key];
      if (nested !== undefined) {
        sorted[key] = sortJsonValue(nested);
      }
    }
    return sorted;
  }

  return value;
}

export function mergeValues(
  known: Record<string, unknown>,
  extras: Record<string, unknown>,
  fieldOrder: Iterable<string>,
  preserveOrder: boolean,
): Record<string, unknown> {
  if (!preserveOrder) {
    return { ...known, ...extras };
  }

  const merged: Record<string, unknown> = {};
  const usedExtras = new Set<string>();

  for (const key of fieldOrder) {
    if (Object.hasOwn(known, key)) {
      merged[key] = known[key];
    } else if (Object.hasOwn(extras, key)) {
      merged[key] = extras[key];
      usedExtras.add(key);
    }
  }

  for (const [key, value] of Object.entries(known)) {
    if (!Object.hasOwn(merged, key)) {
      merged[key] = value;
    }
  }

  for (const [key, value] of Object.entries(extras)) {
    if (!usedExtras.has(key) && !Object.hasOwn(merged, key)) {
      merged[key] = value;
    }
  }

  return merged;
}

export function entriesExcept<T extends Record<string, unknown>>(
  input: T,
  excluded: readonly string[],
): Record<string, unknown> {
  const extras: Record<string, unknown> = {};
  for (const [key, value] of Object.entries(input)) {
    if (!excluded.includes(key)) {
      extras[key] = value;
    }
  }
  return extras;
}

export function assertNever(_value: never): never {
  throw new Error("unreachable");
}
