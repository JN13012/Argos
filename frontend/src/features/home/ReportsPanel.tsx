import { Badge } from "../../components/Badge";
import { Icon } from "../../components/Icon";
import type { Mission, ReportArtifact } from "../workspace/types";

interface ReportsPanelProps {
  mission: Mission;
  report: ReportArtifact | null;
  matchesQuery: boolean;
  onDownload(): void;
}

export function ReportsPanel({
  mission,
  report,
  matchesQuery,
  onDownload,
}: ReportsPanelProps) {
  return (
    <article
      className="panel reports-panel"
      id="reports-panel"
      aria-labelledby="reports-title"
    >
      <div className="panel-heading">
        <h2 id="reports-title">Rapports & documents</h2>
        <Icon name="folder" />
      </div>
      {matchesQuery && (
        <div className="report-document">
          <div className="document-heading">
            <span className="document-icon">
              <Icon name="file" />
            </span>
            <Badge>Markdown</Badge>
          </div>
          <h3>Rapport de mission</h3>
          <p id="report-description">
            {report ? `argos-${mission.id}.md` : "Rapport indisponible"}
          </p>
          {report ? (
            <a
              className="button button--secondary document-download"
              data-report-link
              href={report.url}
              download={`argos-${mission.id}.md`}
              onClick={onDownload}
            >
              <Icon name="download" />
              Télécharger le rapport
            </a>
          ) : (
            <p className="report-unavailable" id="report-unavailable">
              Aucun rapport ne correspond au dossier actuel.
            </p>
          )}
        </div>
      )}
      {!matchesQuery && (
        <p className="empty-message">
          Aucun document ne correspond à cette recherche.
        </p>
      )}
    </article>
  );
}
