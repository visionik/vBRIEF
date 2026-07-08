/**
 * Shared JSON type aliases for libxbrief-ts.
 */

export type JsonPrimitive = null | boolean | number | string;
export type JsonValue = JsonPrimitive | JsonObject | JsonValue[];
export interface JsonObject {
  [key: string]: JsonValue;
}

export interface RecordLike {
  [key: string]: unknown;
}
