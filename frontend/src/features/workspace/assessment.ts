import type {
  Assessment,
  Evidence,
  Finding,
  Mission,
  Review,
  Severity,
} from "./types";

export const severityLabels: Record<Severity, string> = {
  critical: "Critique",
  high: "Élevée",
  medium: "Moyenne",
  low: "Faible",
  info: "Info",
};

const severityOrder: Record<Severity, number> = {
  critical: 0,
  high: 1,
  medium: 2,
  low: 3,
  info: 4,
};

function isRecord(value: unknown): value is Record<string, unknown> {
  return value !== null && typeof value === "object" && !Array.isArray(value);
}

function isText(value: unknown): value is string {
  return typeof value === "string" && value.trim().length > 0;
}

function isTextList(value: unknown): value is string[] {
  return Array.isArray(value) && value.every(isText);
}

function isMission(value: unknown): value is Mission {
  return (
    isRecord(value) &&
    isText(value.id) &&
    isText(value.title) &&
    isText(value.description) &&
    isTextList(value.scope) &&
    value.scope.length > 0
  );
}

function isEvidence(value: unknown): value is Evidence {
  return (
    isRecord(value) &&
    isText(value.id) &&
    isText(value.path) &&
    isText(value.description) &&
    isText(value.source) &&
    typeof value.sha256 === "string" &&
    /^[0-9a-f]{64}$/.test(value.sha256)
  );
}

function isReview(value: unknown): value is Review {
  return (
    isRecord(value) &&
    (value.decision === "accepted" || value.decision === "rejected") &&
    isText(value.reviewer) &&
    isText(value.reason)
  );
}

function isFinding(value: unknown): value is Finding {
  return (
    isRecord(value) &&
    isText(value.id) &&
    isText(value.title) &&
    isText(value.asset) &&
    isText(value.description) &&
    isText(value.recommendation) &&
    typeof value.severity === "string" &&
    Object.hasOwn(severityLabels, value.severity) &&
    isTextList(value.evidence_ids) &&
    value.evidence_ids.length > 0 &&
    (value.review === null || isReview(value.review))
  );
}

function hasUniqueIds(items: readonly { id: string }[]): boolean {
  return new Set(items.map((item) => item.id)).size === items.length;
}

// Presentation checks only. File access and proof integrity belong to Argos Core.
export function isAssessment(value: unknown): value is Assessment {
  if (
    !isRecord(value) ||
    value.schema_version !== 1 ||
    !isMission(value.mission) ||
    !Array.isArray(value.evidence) ||
    !value.evidence.every(isEvidence) ||
    !Array.isArray(value.findings) ||
    !value.findings.every(isFinding)
  )
    return false;

  const proofIds = new Set(value.evidence.map((proof) => proof.id));
  const scope = value.mission.scope;
  return (
    hasUniqueIds(value.evidence) &&
    hasUniqueIds(value.findings) &&
    value.findings.every(
      (finding) =>
        scope.includes(finding.asset) &&
        finding.evidence_ids.every((id) => proofIds.has(id)),
    )
  );
}

export interface WorkspaceSummary {
  readonly pendingFindings: readonly Finding[];
  readonly pendingCount: number;
  readonly findingCount: number;
  readonly reviewedCount: number;
  readonly evidenceCount: number;
  readonly criticalCount: number;
  readonly reviewStatus: "À revoir" | "Revue terminée" | "Sans constat";
  readonly reviewNote: string;
}

export function summarizeAssessment(assessment: Assessment): WorkspaceSummary {
  const pendingFindings = assessment.findings
    .filter((finding) => finding.review === null)
    .sort(
      (a, b) =>
        severityOrder[a.severity] - severityOrder[b.severity] ||
        a.id.localeCompare(b.id),
    );
  const pendingCount = pendingFindings.length;
  const findingCount = assessment.findings.length;
  return {
    pendingFindings,
    pendingCount,
    findingCount,
    reviewedCount: findingCount - pendingCount,
    evidenceCount: assessment.evidence.length,
    criticalCount: assessment.findings.filter(
      (finding) => finding.severity === "critical",
    ).length,
    reviewStatus: pendingCount
      ? "À revoir"
      : findingCount
        ? "Revue terminée"
        : "Sans constat",
    reviewNote: pendingCount
      ? `${pendingCount} constat${pendingCount === 1 ? " reste" : "s restent"} en attente de revue.`
      : findingCount
        ? "Tous les constats ont reçu une décision de revue."
        : "Aucun constat enregistré dans cette mission.",
  };
}

export type WorkspaceInspection =
  | { status: "empty" }
  | { status: "error"; reason: "missing" | "invalid" }
  | { status: "ready"; assessment: Assessment; summary: WorkspaceSummary };

export function inspectWorkspace(value: unknown): WorkspaceInspection {
  if (value === null) return { status: "empty" };
  if (value === undefined) return { status: "error", reason: "missing" };
  if (!isAssessment(value)) return { status: "error", reason: "invalid" };
  return {
    status: "ready",
    assessment: value,
    summary: summarizeAssessment(value),
  };
}
