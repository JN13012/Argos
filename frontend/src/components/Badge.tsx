import type { ReactNode } from "react";
import { severityLabels } from "../features/workspace/assessment";
import type { WorkspaceSummary } from "../features/workspace/assessment";
import type { Severity } from "../features/workspace/types";

type BadgeTone = "neutral" | "blue" | "amber" | "green" | "red";

export function Badge({
  tone = "neutral",
  children,
}: {
  tone?: BadgeTone;
  children: ReactNode;
}) {
  return <span className={`badge badge--${tone}`}>{children}</span>;
}

const severityTones: Record<Severity, BadgeTone> = {
  critical: "red",
  high: "red",
  medium: "amber",
  low: "blue",
  info: "neutral",
};

export function SeverityBadge({ severity }: { severity: Severity }) {
  return (
    <Badge tone={severityTones[severity]}>{severityLabels[severity]}</Badge>
  );
}

export function ReviewBadge({ summary }: { summary: WorkspaceSummary }) {
  return (
    <Badge
      tone={
        summary.pendingCount
          ? "amber"
          : summary.findingCount
            ? "green"
            : "neutral"
      }
    >
      {summary.reviewStatus}
    </Badge>
  );
}
