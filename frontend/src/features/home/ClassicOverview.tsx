import { Badge } from "../../components/Badge";
import { Icon } from "../../components/Icon";
import type { IconName } from "../../components/Icon";
import type { WorkspaceSummary } from "../workspace/assessment";
import type { Assessment } from "../workspace/types";

function Metric({
  label,
  icon,
  value,
  note,
  tone = "",
  onClick,
}: {
  label: string;
  icon: IconName;
  value: number | string;
  note: string;
  tone?: string;
  onClick?: () => void;
}) {
  const content = (
    <>
      <span className="metric-label">
        <Icon name={icon} />
        {label}
      </span>
      <strong>{value}</strong>
      <span className="metric-note">{note}</span>
      <svg className="metric-decoration" viewBox="0 0 90 38" aria-hidden="true">
        <path d="M1 32H22V24H45V16H67V7H89" />
        <path className="chart-fill" d="M1 32H22V24H45V16H67V7H89V38H1Z" />
      </svg>
    </>
  );
  return onClick ? (
    <button
      type="button"
      className={`metric-card panel ${tone}`}
      onClick={onClick}
    >
      {content}
    </button>
  ) : (
    <div className={`metric-card panel ${tone}`}>{content}</div>
  );
}

export function MetricsPanel({
  assessment,
  summary,
  onOpenMission,
}: {
  assessment: Assessment;
  summary: WorkspaceSummary;
  onOpenMission(): void;
}) {
  return (
    <section className="metrics-grid" aria-label="Indicateurs de démonstration">
      <Metric
        label="MISSIONS"
        icon="target"
        value={1}
        note="Mission de démonstration"
        onClick={onOpenMission}
      />
      <Metric
        label="REVUES EN ATTENTE"
        icon="clipboard"
        value={summary.pendingCount}
        note="Une décision humaine à enregistrer"
        tone="amber"
        onClick={onOpenMission}
      />
      <Metric
        label="ACTIFS DU PÉRIMÈTRE"
        icon="globe"
        value={assessment.mission.scope.length}
        note={assessment.mission.scope.join(", ")}
        onClick={onOpenMission}
      />
      <Metric
        label="CONSTATS CRITIQUES"
        icon="alert"
        value={summary.criticalCount}
        note="Constats enregistrés dans le dossier"
        tone="red"
        onClick={onOpenMission}
      />
      <Metric
        label="AGENTS CONNECTÉS"
        icon="agent"
        value="0 / 0"
        note="Aucun agent connecté"
        tone="agents-metric"
      />
    </section>
  );
}

export function AgentsPanel() {
  const profiles = [
    { label: "Analyse", icon: "agent" },
    { label: "Revue", icon: "clipboard" },
    { label: "Rapport", icon: "file" },
  ] as const;
  return (
    <article
      className="panel detail-panel agents-panel"
      aria-labelledby="agents-title"
    >
      <div className="panel-heading">
        <h2 id="agents-title">Agents</h2>
        <Badge>À venir</Badge>
      </div>
      {profiles.map((profile) => (
        <div className="agent-row" key={profile.label}>
          <span className="agent-icon">
            <Icon name={profile.icon} />
          </span>
          <span>
            <strong>{profile.label}</strong>
            <small>Profil prévu</small>
          </span>
          <span className="agent-status">
            <span className="status-dot inactive" />
            Non connecté
          </span>
        </div>
      ))}
      <div className="agents-footer">
        <span>0 agent connecté</span>
        <Icon name="info" />
      </div>
    </article>
  );
}
