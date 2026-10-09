import { useEffect, useState } from "react";
import { Badge } from "../../components/Badge";
import { BrandLogo } from "../../components/BrandLogo";
import { Button } from "../../components/Button";
import { Icon } from "../../components/Icon";
import type { IconName } from "../../components/Icon";
import type { WorkspaceSummary } from "../workspace/assessment";
import type { Assessment } from "../workspace/types";

const localTime = new Intl.DateTimeFormat("fr-FR", {
  timeZone: "Europe/Paris",
  hour: "2-digit",
  minute: "2-digit",
  second: "2-digit",
});

function LocalClock() {
  const [now, setNow] = useState(() => new Date());
  useEffect(() => {
    const timer = window.setInterval(() => setNow(new Date()), 1000);
    return () => window.clearInterval(timer);
  }, []);
  return (
    <div className="local-time">
      <span>Heure locale</span>
      <strong>{localTime.format(now)}</strong>
      <small>Europe / Paris</small>
    </div>
  );
}

export function WelcomePanel({
  summary,
  scopeCount,
  onOpenMission,
}: {
  summary: WorkspaceSummary;
  scopeCount: number;
  onOpenMission(): void;
}) {
  return (
    <section className="welcome-panel panel" aria-labelledby="welcome-title">
      <div className="mascot-frame">
        <div className="mascot-aura" />
        <BrandLogo variant="welcome" />
        <div className="mascot-orbit" />
      </div>
      <div className="welcome-content">
        <h2 id="welcome-title">
          Bienvenue dans Argos{" "}
          <span className="welcome-wave" aria-hidden="true">
            ✦
          </span>
        </h2>
        <p className="brand-promise">Observer. Comprendre. Agir.</p>
        <p className="welcome-description">
          Gardez une vue claire sur vos missions et vos preuves.
        </p>
        <div className="welcome-details">
          <LocalClock />
          <div className="review-status">
            <span className="review-status-icon">
              <Icon name="clipboard" />
            </span>
            <div>
              <span>Revue des constats</span>
              <strong>
                {summary.pendingCount
                  ? `${summary.pendingCount} À EXAMINER`
                  : summary.reviewStatus}
              </strong>
              <small>Vos décisions restent au centre du parcours.</small>
            </div>
          </div>
        </div>
      </div>
      <div className="summary-box">
        <div className="summary-title">
          <Icon name="eye-shield" />
          VOTRE POINT DE SITUATION
        </div>
        <p>
          Une mission de démonstration.
          <br />
          {summary.pendingCount} constat{summary.pendingCount === 1 ? "" : "s"}{" "}
          en attente de revue.
          <br />
          {summary.evidenceCount} preuve{summary.evidenceCount === 1 ? "" : "s"}{" "}
          locale{summary.evidenceCount === 1 ? "" : "s"} associée
          {summary.evidenceCount === 1 ? "" : "s"}.
        </p>
        <Button variant="quiet" onClick={onOpenMission}>
          Voir la mission <Icon name="arrow" />
        </Button>
      </div>
      <span className="sr-only">
        {scopeCount} actif{scopeCount === 1 ? "" : "s"} dans le périmètre.
      </span>
    </section>
  );
}

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
