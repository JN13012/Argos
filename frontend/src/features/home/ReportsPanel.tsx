import { Badge } from "../../components/Badge";
import { Icon } from "../../components/Icon";
import type { WorkspaceSummary } from "../workspace/assessment";
import type { Mission, ReportArtifact } from "../workspace/types";

interface ReportsPanelProps {
  mission: Mission;
  report: ReportArtifact | null;
  matchesQuery: boolean;
  summary: WorkspaceSummary;
  onOpenMission(): void;
  onDownload(): void;
}

export function ReportsPanel({
  mission,
  report,
  matchesQuery,
  summary,
  onOpenMission,
  onDownload,
}: ReportsPanelProps) {
  return (
    <article
      className="panel detail-panel reports-panel"
      id="reports-panel"
      aria-labelledby="reports-title"
    >
      <div className="panel-heading">
        <h2 id="reports-title">Rapports & documents</h2>
        <span className="muted-count">
          {report ? 2 : 1} document{report ? "s" : ""}
        </span>
      </div>
      {matchesQuery && (
        <>
          {report ? (
            <a
              className="document-row"
              data-report-link
              aria-label="Télécharger le rapport"
              href={report.url}
              download={`argos-${mission.id}.md`}
              onClick={onDownload}
            >
              <span className="document-icon">
                <Icon name="file" />
                <small>MD</small>
              </span>
              <span className="document-content">
                <strong>Rapport de mission</strong>
                <small>argos-{mission.id}.md</small>
              </span>
              <Badge tone="blue">MD</Badge>
              <Icon name="download" className="row-action" />
            </a>
          ) : (
            <p className="report-unavailable" id="report-unavailable">
              Aucun rapport ne correspond au dossier actuel.
            </p>
          )}
          <button
            type="button"
            className="document-row"
            onClick={onOpenMission}
          >
            <span className="document-icon json-icon">
              <Icon name="folder" />
            </span>
            <span className="document-content">
              <strong>Dossier de mission</strong>
              <small>{mission.id} · Données structurées</small>
            </span>
            <Badge>JSON</Badge>
            <Icon name="chevron" className="row-action" />
          </button>
          <p className="document-note">
            <Icon name="clipboard" />
            {summary.evidenceCount} preuves locales référencées
          </p>
        </>
      )}
      {!matchesQuery && (
        <p className="empty-message">
          Aucun document ne correspond à cette recherche.
        </p>
      )}
      <button
        type="button"
        className="panel-footer-link"
        onClick={onOpenMission}
      >
        Consulter les documents
        <Icon name="arrow" />
      </button>
    </article>
  );
}
