import { describe, expect, it } from "vitest";
import { fixture, review } from "../../test/fixture";
import { inspectWorkspace, summarizeAssessment } from "./assessment";

describe("presentation contract", () => {
  it("derives priorities without modifying the dossier", () => {
    const data = fixture();
    const before = JSON.stringify(data);
    const state = summarizeAssessment(data);
    expect(state).toMatchObject({
      pendingCount: 2,
      reviewedCount: 0,
      evidenceCount: 2,
      criticalCount: 0,
      reviewStatus: "À revoir",
    });
    expect(state.reviewNote).toBe("2 constats restent en attente de revue.");
    expect(JSON.stringify(data)).toBe(before);
  });

  it("orders critical observations before lower severities", () => {
    const data = fixture();
    const state = summarizeAssessment({
      ...data,
      findings: data.findings.map((finding, i) =>
        i === 1 ? { ...finding, severity: "critical" } : finding,
      ),
    });
    expect(state.pendingFindings.map((finding) => finding.id)).toEqual([
      "F-002",
      "F-001",
    ]);
    expect(state.criticalCount).toBe(1);
  });

  it("excludes reviewed findings and uses singular labels", () => {
    const data = fixture();
    const state = summarizeAssessment({
      ...data,
      findings: data.findings.map((finding, i) =>
        i === 0 ? { ...finding, review: review("accepted") } : finding,
      ),
    });
    expect(state.pendingCount).toBe(1);
    expect(state.reviewedCount).toBe(1);
    expect(state.reviewNote).toBe("1 constat reste en attente de revue.");
    expect(state.pendingFindings.map((finding) => finding.id)).toEqual([
      "F-002",
    ]);
  });

  it("treats acceptance and rejection as completed human decisions", () => {
    const data = fixture();
    const state = summarizeAssessment({
      ...data,
      findings: data.findings.map((finding, i) => ({
        ...finding,
        review: review(i ? "rejected" : "accepted"),
      })),
    });
    expect(state.reviewStatus).toBe("Revue terminée");
    expect(state.reviewedCount).toBe(2);
    expect(state.pendingCount).toBe(0);
  });

  it("keeps reviewed critical observations in the registered count", () => {
    const data = fixture();
    const state = summarizeAssessment({
      ...data,
      findings: data.findings.map((finding, i) =>
        i === 0
          ? { ...finding, severity: "critical", review: review("rejected") }
          : finding,
      ),
    });
    expect(state.criticalCount).toBe(1);
  });

  it("does not claim review completion for a mission without findings", () => {
    const state = summarizeAssessment({
      ...fixture(),
      findings: [],
      evidence: [],
    });
    expect(state.reviewStatus).toBe("Sans constat");
    expect(state.reviewNote).toBe(
      "Aucun constat enregistré dans cette mission.",
    );
  });

  it("distinguishes explicitly empty, missing and malformed inputs", () => {
    expect(inspectWorkspace(null)).toEqual({ status: "empty" });
    expect(inspectWorkspace(undefined)).toEqual({
      status: "error",
      reason: "missing",
    });
    for (const value of [{}, [], false, 0, "unavailable"])
      expect(inspectWorkspace(value)).toEqual({
        status: "error",
        reason: "invalid",
      });
  });

  it("rejects incomplete collections, unsupported versions and missing mission fields", () => {
    const data = fixture();
    for (const input of [
      { ...data, schema_version: 2 },
      { ...data, findings: null },
      { ...data, evidence: {} },
      { ...data, mission: { ...data.mission, scope: [] } },
      { ...data, mission: { ...data.mission, title: null } },
    ])
      expect(inspectWorkspace(input)).toEqual({
        status: "error",
        reason: "invalid",
      });
  });

  it("rejects broken references, duplicate ids, invalid reviews and out-of-scope assets", () => {
    const data = fixture();
    const finding = data.findings[0]!;
    const proof = data.evidence[0]!;
    const invalid = [
      { ...data, findings: [finding, finding] },
      { ...data, evidence: [proof, proof] },
      ...[
        { evidence_ids: ["missing"] },
        { review: {} },
        { review: undefined },
        { severity: "constructor" },
        { asset: "outside.example" },
      ].map((fields) => ({ ...data, findings: [{ ...finding, ...fields }] })),
      { ...data, evidence: [{ ...proof, sha256: "unknown" }] },
    ];
    for (const input of invalid)
      expect(inspectWorkspace(input)).toEqual({
        status: "error",
        reason: "invalid",
      });
  });
});
