import { ReviewBadge, SeverityBadge } from "../../components/Badge";
import { Button } from "../../components/Button";
import { Icon } from "../../components/Icon";
import type { WorkspaceSummary } from "../workspace/assessment";
import type { Assessment, Finding } from "../workspace/types";

interface MissionPanelProps {
  assessment: Assessment;
  summary: WorkspaceSummary;
  findings: readonly Finding[];
  onOpenMission(findingId: string | null): void;
}

export function MissionPanel({
  assessment,
  summary,
  findings,
  onOpenMission,
}: MissionPanelProps) {
  return (
    <article
      className="panel mission-panel"
      id="missions-panel"
      aria-labelledby="mission-title"
    >
      <div className="mission-heading">
        <div className="mission-identity">
          <span className="eyebrow" id="mission-reference">
            MISSION · {assessment.mission.id}
          </span>
          <h2 id="mission-title">{assessment.mission.title}</h2>
          <div className="mission-context">
            <span className="mission-scope">
              <Icon name="globe" />
              {assessment.mission.scope.join(", ")}
            </span>
            <span className="review-caption">Revue</span>
            <ReviewBadge summary={summary} />
          </div>
        </div>
        <Button onClick={() => onOpenMission(null)} data-open-mission>
          Ouvrir le dossier <Icon name="arrow" />
        </Button>
      </div>
      <section id="priorities-panel" aria-labelledby="priority-title">
        <div className="priority-heading">
          <h3 id="priority-title">
            {summary.pendingCount ? "Constats à examiner" : "Constats"}
          </h3>
          {summary.pendingCount > 0 && (
            <span className="priority-count" id="priority-count">
              {summary.pendingCount}
            </span>
          )}
        </div>
        <div className="priority-list" id="priority-list">
          {findings.map((finding) => (
            <button
              type="button"
              className={`priority-row severity-${finding.severity}`}
              key={finding.id}
              data-open-finding={finding.id}
              aria-label={`Examiner ${finding.id} : ${finding.title}`}
              onClick={() => onOpenMission(finding.id)}
            >
              <span className="priority-icon">
                <Icon name="clipboard" />
              </span>
              <span className="priority-content">
                <strong>{finding.title}</strong>
                <small>
                  {finding.id} · {finding.evidence_ids.length} preuve
                  {finding.evidence_ids.length === 1 ? "" : "s"}
                </small>
              </span>
              <SeverityBadge severity={finding.severity} />
              <Icon name="chevron" className="priority-chevron" />
            </button>
          ))}
          {summary.pendingCount === 0 && (
            <p className="empty-message">
              {summary.findingCount
                ? "Les constats revus et leurs décisions sont consultables dans le dossier."
                : "Les constats importés apparaîtront ici."}
            </p>
          )}
        </div>
      </section>
    </article>
  );
}
