import { useEffect, useState } from "react";
import { inspectWorkspace } from "./assessment";
import type { WorkspaceSummary } from "./assessment";
import { reportMatches } from "./report";
import type { Assessment, ReportArtifact, WorkspaceSource } from "./types";

export type WorkspaceState =
  | { status: "loading" }
  | { status: "empty" }
  | { status: "error"; reason: "missing" | "invalid" }
  | {
      status: "ready";
      assessment: Assessment;
      summary: WorkspaceSummary;
      report: ReportArtifact | null;
    };

export function useWorkspace(source: WorkspaceSource): WorkspaceState {
  const [state, setState] = useState<WorkspaceState>({ status: "loading" });

  useEffect(() => {
    let cancelled = false;
    setState({ status: "loading" });

    async function load() {
      try {
        const document = await source.load();
        const inspection = inspectWorkspace(document.assessment);
        if (inspection.status !== "ready") {
          if (!cancelled) setState(inspection);
          return;
        }
        const report =
          document.report &&
          (await reportMatches(
            inspection.assessment,
            document.report.sourceHash,
          ))
            ? document.report
            : null;
        if (!cancelled) setState({ ...inspection, report });
      } catch {
        if (!cancelled) setState({ status: "error", reason: "missing" });
      }
    }

    void load();
    return () => {
      cancelled = true;
    };
  }, [source]);

  return state;
}
