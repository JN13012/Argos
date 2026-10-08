/** Mirrors schema_version 1 in schemas/assessment.schema.json. */
export type Severity = "critical" | "high" | "medium" | "low" | "info";

export interface Mission {
  readonly id: string;
  readonly title: string;
  readonly description: string;
  readonly scope: readonly string[];
}

export interface Evidence {
  readonly id: string;
  readonly path: string;
  readonly sha256: string;
  readonly description: string;
  readonly source: string;
}

export interface Review {
  readonly decision: "accepted" | "rejected";
  readonly reviewer: string;
  readonly reason: string;
}

export interface Finding {
  readonly id: string;
  readonly title: string;
  readonly severity: Severity;
  readonly asset: string;
  readonly description: string;
  readonly recommendation: string;
  readonly evidence_ids: readonly string[];
  readonly review: Review | null;
}

export interface Assessment {
  readonly schema_version: 1;
  readonly mission: Mission;
  readonly evidence: readonly Evidence[];
  readonly findings: readonly Finding[];
}

export interface ReportArtifact {
  readonly url: string;
  readonly sourceHash: string;
}

export interface WorkspaceDocument {
  readonly assessment: unknown;
  readonly report: ReportArtifact | null;
}

/** Data boundary: a future local adapter can implement this without changing the UI. */
export interface WorkspaceSource {
  load(): Promise<WorkspaceDocument>;
}
