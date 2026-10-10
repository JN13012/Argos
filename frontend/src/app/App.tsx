import { useRef, useState } from "react";
import { Button } from "../components/Button";
import { HomePage } from "../features/home/HomePage";
import { WorkspaceStatus } from "../features/home/WorkspaceStatus";
import type { MissionSelection } from "../features/mission/MissionDialog";
import { bundledWorkspaceSource } from "../features/workspace/bundled-source";
import type { WorkspaceSource } from "../features/workspace/types";
import { useWorkspace } from "../features/workspace/useWorkspace";
import { AppShell } from "../layout/AppShell";
import { AboutDialog } from "./AboutDialog";

export function App({
  source = bundledWorkspaceSource,
}: {
  source?: WorkspaceSource;
}) {
  const workspace = useWorkspace(source);
  const [query, setQuery] = useState("");
  const [aboutOpen, setAboutOpen] = useState(false);
  const [selection, setSelection] = useState<MissionSelection | null>(null);
  const [chatExpanded, setChatExpanded] = useState(false);
  const [chatFocusRequest, setChatFocusRequest] = useState(0);
  const searchRef = useRef<HTMLInputElement>(null);

  return (
    <AppShell
      query={query}
      onQueryChange={setQuery}
      ready={workspace.status === "ready"}
      pendingCount={
        workspace.status === "ready" ? workspace.summary.pendingCount : 0
      }
      onOpenMission={() => setSelection({ findingId: null })}
      searchRef={searchRef}
      onOpenChat={() => setChatFocusRequest((current) => current + 1)}
      onAbout={() => setAboutOpen(true)}
      modalOpen={aboutOpen || selection !== null || chatExpanded}
    >
      <main
        className="workspace"
        id="main-content"
        tabIndex={-1}
        data-state={workspace.status}
        aria-busy={workspace.status === "loading"}
      >
        <div className="page-heading">
          <div className="demo-pill">
            <span className="status-dot blue" />
            Données de démonstration
          </div>
        </div>
        {workspace.status === "ready" ? (
          <HomePage
            workspace={workspace}
            query={query}
            chatFocusRequest={chatFocusRequest}
            chatExpanded={chatExpanded}
            onChatExpandedChange={setChatExpanded}
            selection={selection}
            onSelectionChange={setSelection}
          />
        ) : (
          <WorkspaceStatus state={workspace} />
        )}
        <footer className="workspace-footer">
          <span>
            ARGOS <i>·</i> Observer. Comprendre. Agir.
          </span>
          <Button variant="quiet" onClick={() => setAboutOpen(true)}>
            À propos d’Argos
          </Button>
        </footer>
      </main>
      <AboutDialog open={aboutOpen} onClose={() => setAboutOpen(false)} />
    </AppShell>
  );
}
