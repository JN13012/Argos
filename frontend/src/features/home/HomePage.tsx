import { useState } from "react";
import { BrandLogo } from "../../components/BrandLogo";
import { ActivityLog } from "../activity/ActivityLog";
import { appendActivity } from "../activity/activity";
import type { ActivityInput } from "../activity/activity";
import { ChatPanel } from "../chat/ChatPanel";
import { MissionDialog } from "../mission/MissionDialog";
import type { MissionSelection } from "../mission/MissionDialog";
import { severityLabels } from "../workspace/assessment";
import { matchesSearch, normalizeSearch } from "../workspace/search";
import type { WorkspaceState } from "../workspace/useWorkspace";
import { MissionPanel } from "./MissionPanel";
import { ReportsPanel } from "./ReportsPanel";
import "./HomePage.css";

interface HomePageProps {
  workspace: Extract<WorkspaceState, { status: "ready" }>;
  query: string;
  chatFocusRequest: number;
  chatExpanded: boolean;
  onChatExpandedChange(expanded: boolean): void;
  selection: MissionSelection | null;
  onSelectionChange(selection: MissionSelection | null): void;
}

export function HomePage({
  workspace,
  query,
  chatFocusRequest,
  chatExpanded,
  onChatExpandedChange,
  selection,
  onSelectionChange,
}: HomePageProps) {
  const { assessment, summary, report } = workspace;
  const [events, setEvents] = useState(() =>
    appendActivity([], {
      type: "mission",
      text: "Dossier chargé dans l’interface.",
      reference: assessment.mission.id,
    }),
  );
  const missionFields = [
    assessment.mission.id,
    assessment.mission.title,
    ...assessment.mission.scope,
  ];
  const findings = summary.pendingFindings.filter((finding) =>
    matchesSearch(
      query,
      ...missionFields,
      finding.id,
      finding.title,
      finding.asset,
      severityLabels[finding.severity],
    ),
  );
  const reportMatchesQuery = matchesSearch(
    query,
    "rapport markdown",
    ...missionFields,
  );
  const resultCount = findings.length + Number(reportMatchesQuery);

  function recordActivity(input: ActivityInput) {
    setEvents((current) => appendActivity(current, input));
  }

  function openMission(findingId: string | null) {
    onSelectionChange({ findingId });
    recordActivity(
      findingId
        ? {
            type: "review",
            text: `Constat ${findingId} consulté.`,
            reference: `${assessment.mission.id} · ${findingId}`,
          }
        : {
            type: "mission",
            text: "Dossier de mission consulté.",
            reference: assessment.mission.id,
          },
    );
  }

  return (
    <div className="dashboard-grid" id="dashboard-content">
      <section className="welcome-panel" aria-labelledby="welcome-title">
        <div className="mascot-frame">
          <BrandLogo variant="welcome" />
        </div>
        <div className="welcome-content">
          <h2 id="welcome-title">Reprendre votre travail</h2>
          <p>
            {summary.pendingCount
              ? "Choisissez un constat pour poursuivre la revue."
              : summary.findingCount
                ? "Retrouvez les décisions de revue dans le dossier."
                : "Consultez le dossier pour préparer la revue."}
          </p>
        </div>
      </section>
      <MissionPanel
        assessment={assessment}
        summary={summary}
        findings={findings}
        onOpenMission={openMission}
      />
      <ReportsPanel
        mission={assessment.mission}
        report={report}
        matchesQuery={reportMatchesQuery}
        onDownload={() =>
          recordActivity({
            type: "report",
            text: "Téléchargement du rapport demandé.",
            reference: assessment.mission.id,
          })
        }
      />
      {normalizeSearch(query) && (
        <p className="search-feedback" id="search-feedback" role="status">
          {resultCount
            ? `${resultCount} résultat${resultCount === 1 ? "" : "s"} dans les constats et rapports.`
            : "Aucun constat ou rapport ne correspond à cette recherche."}
        </p>
      )}
      <ActivityLog events={events} query={query} />
      <ChatPanel
        context={{ assessment, summary, reportAvailable: report !== null }}
        focusRequest={chatFocusRequest}
        expanded={chatExpanded}
        onExpandedChange={onChatExpandedChange}
      />
      <MissionDialog
        assessment={assessment}
        summary={summary}
        selection={selection}
        onShowAll={() => openMission(null)}
        onClose={() => onSelectionChange(null)}
      />
    </div>
  );
}
