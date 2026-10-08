import { createHash } from "node:crypto";
import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { describe, expect, it, vi } from "vitest";
import { fixture, review } from "../../test/fixture";
import { bundledWorkspaceSource } from "./bundled-source";
import { reportMatches } from "./report";

describe("bundled report consistency", () => {
  it("matches the displayed dossier and ships the corresponding mission report", async () => {
    const document = await bundledWorkspaceSource.load();
    expect(
      await reportMatches(document.assessment, document.report?.sourceHash),
    ).toBe(true);
    const markdown = readFileSync(resolve("assets/mission-report.md"), "utf8");
    expect(markdown).toContain(fixture().mission.title);
    expect(markdown).toContain("intranet\\.example");
  });

  it("disables a stale report after a review or a content change", async () => {
    const data = fixture();
    const hash = (await bundledWorkspaceSource.load()).report?.sourceHash;
    for (const changed of [
      { ...data, mission: { ...data.mission, title: "Autre mission" } },
      {
        ...data,
        mission: {
          ...data.mission,
          scope: [...data.mission.scope, "second.example"],
        },
      },
      {
        ...data,
        findings: data.findings.map((f) => ({
          ...f,
          review: review("accepted"),
        })),
      },
      {
        ...data,
        findings: data.findings.map((f) => ({
          ...f,
          description: f.description + " Complément.",
        })),
      },
      {
        ...data,
        evidence: data.evidence.map((e) => ({ ...e, source: "Autre source" })),
      },
    ])
      expect(await reportMatches(changed, hash)).toBe(false);
  });

  it("ignores object key order while preserving array order", async () => {
    const document = await bundledWorkspaceSource.load();
    const data = fixture();
    expect(
      await reportMatches(
        {
          findings: data.findings,
          evidence: data.evidence,
          mission: data.mission,
          schema_version: 1,
        },
        document.report?.sourceHash,
      ),
    ).toBe(true);
    expect(
      await reportMatches(
        { ...data, findings: [...data.findings].reverse() },
        document.report?.sourceHash,
      ),
    ).toBe(false);
  });

  it("cannot claim report availability without metadata or digest support", async () => {
    expect(await reportMatches(fixture(), undefined)).toBe(false);
    expect(await reportMatches(fixture(), "wrong")).toBe(false);
    const hash = (await bundledWorkspaceSource.load()).report?.sourceHash;
    vi.stubGlobal("crypto", undefined);
    expect(await reportMatches(fixture(), hash)).toBe(false);
  });

  it("preserves French UTF-8 text in the canonical fingerprint", async () => {
    const data = { title: "Évaluation du périmètre", count: 1, notes: null };
    const expected = createHash("sha256")
      .update(
        '{"count":1,"notes":null,"title":"Évaluation du périmètre"}',
        "utf8",
      )
      .digest("hex");
    expect(await reportMatches(data, expected)).toBe(true);
  });
});
