import { useState } from "react";
import { IntelligenceScene } from "./scene/IntelligenceScene";
import { ActivityLog } from "../activity/ActivityLog";
import { appendActivity } from "../activity/activity";
import type { ActivityInput } from "../activity/activity";
import { ChatPanel } from "../chat/ChatPanel";
import { MissionDialog } from "../mission/MissionDialog";
import type { MissionSelection } from "../mission/MissionDialog";
import { severityLabels } from "../workspace/assessment";
import { matchesSearch, normalizeSearch } from "../workspace/search";
import type { WorkspaceState } from "../workspace/useWorkspace";
import { CurrentMissions } from "./CurrentMissions";
import { MissionPanel } from "./MissionPanel";
import { ReportsPanel } from "./ReportsPanel";
import "./HomePage.css";
import "./scene/IntelligenceScene.css";
import "./DashboardLayout.css";

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
      <div className="dashboard-main">
        <section className="welcome-panel" aria-labelledby="welcome-title">
          <div className="welcome-content">
            <span className="welcome-kicker">SECURITY INTELLIGENCE</span>
            <h2 id="welcome-title">Observez. Comprenez. Agissez.</h2>
            <p>Votre environnement, sous un nouveau regard.</p>
            <span className="welcome-detail">
              <span className="prototype-dot" />
              Dossier de démonstration · Espace local
            </span>
          </div>
          <IntelligenceScene />
        </section>
        <CurrentMissions />
        <div className="workspace-section-heading">
          <h2>Reprendre votre travail</h2>
          <span>Dossier de démonstration</span>
        </div>
        <div className="dashboard-work-panels">
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
        </div>
        {normalizeSearch(query) && (
          <p className="search-feedback" id="search-feedback" role="status">
            {resultCount
              ? `${resultCount} résultat${resultCount === 1 ? "" : "s"} dans les constats et rapports.`
              : "Aucun constat ou rapport ne correspond à cette recherche."}
          </p>
        )}
        <ActivityLog events={events} query={query} />
      </div>
      <aside className="dashboard-chat" aria-label="Assistant Argos">
        <ChatPanel
          defaultOpen
          context={{ assessment, summary, reportAvailable: report !== null }}
          focusRequest={chatFocusRequest}
          expanded={chatExpanded}
          onExpandedChange={onChatExpandedChange}
        />
      </aside>
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
