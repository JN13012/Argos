import type { ReactNode } from "react";
import { severityLabels } from "../features/workspace/assessment";
import type { WorkspaceSummary } from "../features/workspace/assessment";
import type { Severity } from "../features/workspace/types";

type BadgeTone = "neutral" | "blue" | "amber" | "green" | "red";

const badgeStyles =
  "inline-flex items-center whitespace-nowrap rounded-[5px] border border-solid px-2 py-1 text-[11px] font-medium leading-[1.4]";

const tones: Record<BadgeTone, string> = {
  neutral: "border-badge-border bg-badge text-badge-foreground",
  blue: "border-badge-blue-border bg-badge-blue text-badge-blue-foreground",
  amber: "border-badge-warning-border bg-badge-warning text-warning",
  green: "border-badge-positive-border bg-badge-positive text-positive",
  red: "border-badge-critical-border bg-badge-critical text-critical",
};

export function Badge({
  tone = "neutral",
  children,
}: {
  tone?: BadgeTone;
  children: ReactNode;
}) {
  return (
    <span className={`badge badge--${tone} ${badgeStyles} ${tones[tone]}`}>
      {children}
    </span>
  );
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
