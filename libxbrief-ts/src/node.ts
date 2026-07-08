import { readFile, writeFile } from "node:fs/promises";

export * from "./index.js";
import { coerceToDict, dumps, loads } from "./io.js";

export interface NodeLoadOptions {
  strict?: boolean;
  dag?: boolean;
}

export interface NodeDumpOptions {
  canonical?: boolean;
  preserveFormat?: boolean;
}

/**
 * Load a xBRIEF JSON document from a UTF-8 file.
 */
export async function loadFile(path: string | URL, options: NodeLoadOptions = {}): Promise<Record<string, unknown>> {
  const text = await readFile(path, "utf8");
  return loads(text, options);
}

/**
 * Serialize a document or model object to a UTF-8 file.
 */
export async function dumpFile(
  document: unknown,
  path: string | URL,
  options: NodeDumpOptions = {},
): Promise<void> {
  const payload = coerceToDict(document, options.preserveFormat ?? false);
  await writeFile(path, dumps(payload, options), "utf8");
}
