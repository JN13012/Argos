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
      className="panel detail-panel mission-panel"
      id="missions-panel"
      aria-labelledby="mission-panel-title"
    >
      <div className="panel-heading">
        <h2 id="mission-panel-title">Mission à examiner</h2>
        <ReviewBadge summary={summary} />
      </div>
      <div className="mission-row">
        <span className="mission-icon">
          <Icon name="target" />
        </span>
        <div className="mission-content">
          <h3 id="mission-title">{assessment.mission.title}</h3>
          <small>
            {assessment.mission.id} · {assessment.mission.scope.join(", ")}
          </small>
        </div>
      </div>
      <div className="mission-progress">
        <div>
          <span>Revue des constats</span>
          <strong>
            {summary.reviewedCount} <span>/ {summary.findingCount}</span>
          </strong>
        </div>
        <div
          className="progress-track"
          role="progressbar"
          aria-label="Constats revus"
          aria-valuemin={0}
          aria-valuemax={Math.max(summary.findingCount, 1)}
          aria-valuenow={summary.reviewedCount}
        >
          <span
            style={{
              width: `${summary.findingCount ? (summary.reviewedCount / summary.findingCount) * 100 : 0}%`,
            }}
          />
        </div>
      </div>
      <div className="mission-tags">
        <span>
          <Icon name="folder" />
          {summary.evidenceCount} preuves
        </span>
        <span>
          <Icon name="globe" />
          {assessment.mission.scope.length} actif
          {assessment.mission.scope.length === 1 ? "" : "s"}
        </span>
        <span>
          <span className="status-dot" />
          Hors ligne
        </span>
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
      <Button
        variant="quiet"
        className="panel-footer-link"
        onClick={() => onOpenMission(null)}
        data-open-mission
      >
        Ouvrir le dossier <Icon name="arrow" />
      </Button>
    </article>
  );
}
