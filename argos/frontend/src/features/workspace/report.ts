function canonicalJson(value: unknown): string {
  if (Array.isArray(value)) return `[${value.map(canonicalJson).join(",")}]`;
  if (value !== null && typeof value === "object") {
    return `{${Object.entries(value)
      .sort(([a], [b]) => (a < b ? -1 : a > b ? 1 : 0))
      .map(([key, entry]) => `${JSON.stringify(key)}:${canonicalJson(entry)}`)
      .join(",")}}`;
  }
  const encoded = JSON.stringify(value);
  if (encoded === undefined)
    throw new TypeError("The dossier must be JSON serializable.");
  return encoded;
}

/** Matches the displayed source to the bundled report, not the evidence files. */
export async function reportMatches(
  assessment: unknown,
  sourceHash: unknown,
): Promise<boolean> {
  if (
    typeof sourceHash !== "string" ||
    !/^[0-9a-f]{64}$/.test(sourceHash) ||
    !globalThis.crypto?.subtle
  )
    return false;
  try {
    const source = new TextEncoder().encode(canonicalJson(assessment));
    const digest = await globalThis.crypto.subtle.digest("SHA-256", source);
    const actualHash = Array.from(new Uint8Array(digest), (byte) =>
      byte.toString(16).padStart(2, "0"),
    ).join("");
    return actualHash === sourceHash;
  } catch {
    return false;
  }
}
