import { useState } from "react";
import { Icon } from "../../components/Icon";
import type { IconName } from "../../components/Icon";
import { severityLabels } from "../workspace/assessment";
import type { Severity } from "../workspace/types";
import "./CurrentMissions.css";

type TaskState = "running" | "completed" | "approval";
type MissionSeverity = Exclude<Severity, "info">;

interface DemoMission {
  id: string;
  domain: "red" | "blue" | "osint";
  domainLabel: string;
  icon: IconName;
  title: string;
  target: string;
  targetIcon: IconName;
  phase: string;
  exposure?: {
    subdomains: number;
    internalDocuments: number;
    publishedApiKeys: number;
    consultedSources: number;
  };
  pentest?: {
    severities: readonly { severity: MissionSeverity; count: number }[];
    completedChecks: number;
    plannedChecks: number;
  };
  incident?: {
    confirmedCount: number;
    priority: MissionSeverity;
    affectedDevices: number;
    devicesToReview: number;
    pendingAction: string;
    analyzedAlerts: number;
    receivedAlerts: number;
  };
  tasks: readonly {
    title: string;
    state: TaskState;
    description?: string;
  }[];
}

function count(value: number, singular: string, plural: string) {
  return `${value} ${value === 1 ? singular : plural}`;
}

const taskLabels: Record<TaskState, string> = {
  running: "En cours",
  completed: "Terminé",
  approval: "À valider",
};

const demoMissions: readonly DemoMission[] = [
  {
    id: "RED-DEMO-001",
    domain: "red",
    domainLabel: "Red Team",
    icon: "target",
    title: "Test d’intrusion web — Portail bancaire",
    target: "bankportal.example",
    targetIcon: "globe",
    phase: "Recherche de vulnérabilités",
    pentest: {
      severities: [
        { severity: "critical", count: 0 },
        { severity: "high", count: 1 },
        { severity: "medium", count: 2 },
        { severity: "low", count: 1 },
      ],
      completedChecks: 8,
      plannedChecks: 18,
    },
    tasks: [
      {
        title: "Authentification et sessions",
        state: "running",
        description:
          "Vérification de la connexion, des cookies et de l’expiration des sessions.",
      },
      {
        title: "Contrôle des accès",
        state: "running",
        description:
          "Comparaison des permissions entre les comptes et les rôles de test.",
      },
      {
        title: "Validation des entrées",
        state: "running",
        description:
          "Recherche d’injections dans les paramètres et les formulaires identifiés.",
      },
      {
        title: "Logique métier",
        state: "running",
        description:
          "Vérification des plafonds, des virements et des validations multiples.",
      },
    ],
  },
  {
    id: "BLUE-DEMO-001",
    domain: "blue",
    domainLabel: "Blue Team",
    icon: "shield",
    title: "Réponse à incident — Poste comptabilité",
    target: "PC-COMPTA-01",
    targetIcon: "monitor",
    phase: "Investigation",
    incident: {
      confirmedCount: 1,
      priority: "high",
      affectedDevices: 1,
      devicesToReview: 2,
      pendingAction: "Isolement du poste à approuver",
      analyzedAlerts: 6,
      receivedAlerts: 8,
    },
    tasks: [
      {
        title: "Analyse des alertes",
        state: "running",
        description:
          "Qualification et corrélation des alertes, avec examen des journaux.",
      },
      {
        title: "Investigation numérique",
        state: "running",
        description:
          "Examen des fichiers, processus et traces du poste, avec conservation des preuves.",
      },
      {
        title: "Recherche de propagation",
        state: "running",
        description:
          "Recherche des mêmes indices de compromission sur les autres postes du périmètre.",
      },
    ],
  },
  {
    id: "OSINT-DEMO-001",
    domain: "osint",
    domainLabel: "OSINT",
    icon: "globe",
    title: "Analyse d’exposition — Empreinte numérique",
    target: "entreprise.example",
    targetIcon: "globe",
    phase: "Collecte et recoupement",
    exposure: {
      subdomains: 12,
      internalDocuments: 1,
      publishedApiKeys: 1,
      consultedSources: 7,
    },
    tasks: [
      {
        title: "Domaines et sous-domaines",
        state: "running",
        description:
          "Recensement des domaines et sous-domaines associés à l’entreprise à partir de sources publiques.",
      },
      {
        title: "Documents et métadonnées",
        state: "running",
        description:
          "Examen des documents publics et de leurs métadonnées pour repérer les informations sensibles exposées.",
      },
      {
        title: "Personnes et profils professionnels",
        state: "running",
        description:
          "Recoupement des profils publics, fonctions et coordonnées professionnelles associés à l’entreprise.",
      },
    ],
  },
];

export function CurrentMissions() {
  return (
    <section
      className="current-missions"
      aria-labelledby="current-missions-title"
      aria-describedby="current-missions-notice"
    >
      <div className="current-missions-heading">
        <h2 id="current-missions-title">Missions en cours</h2>
        <span id="current-missions-notice">
          Démonstration · Données fictives
        </span>
      </div>
      <div className="current-missions-grid">
        {demoMissions.map((mission) => (
          <MissionCard mission={mission} key={mission.id} />
        ))}
      </div>
    </section>
  );
}

function MissionCard({ mission }: { mission: DemoMission }) {
  const [open, setOpen] = useState(false);
  const runningTasks = mission.tasks.filter((task) => task.state === "running");
  const tasksId = `current-mission-${mission.domain}-tasks`;

  return (
    <article
      className={`panel current-mission-card current-mission-card--${mission.domain}${open ? " current-mission-card--open" : ""}`}
      aria-labelledby={`current-mission-${mission.domain}`}
    >
      <div className="current-mission-art" aria-hidden="true" />
      <div className="current-mission-main">
        <div className="current-mission-topline">
          <span className="current-mission-domain">
            <Icon name={mission.icon} />
            {mission.domainLabel}
          </span>
          <span className="current-mission-state">En cours</span>
        </div>
        <div className="current-mission-copy">
          <h3 id={`current-mission-${mission.domain}`}>{mission.title}</h3>
          <p className="current-mission-target">
            <Icon name={mission.targetIcon} />
            {mission.target}
          </p>
          <p className="current-mission-phase">
            <span>Phase&nbsp;:</span> {mission.phase.toLowerCase()}
          </p>
          <div className="current-mission-agent-summary">
            <Icon name="agent" />
            {count(runningTasks.length, "agent", "agents")} au travail
          </div>
          <div className="current-mission-overview">
            {mission.pentest && (
              <>
                <div className="current-mission-results">
                  <strong>
                    {count(
                      mission.pentest.severities.reduce(
                        (total, item) => total + item.count,
                        0,
                      ),
                      "vulnérabilité confirmée",
                      "vulnérabilités confirmées",
                    )}
                  </strong>
                  <dl
                    className="current-mission-severities"
                    aria-label="Répartition par sévérité"
                  >
                    {mission.pentest.severities.map((item) => (
                      <div key={item.severity} data-severity={item.severity}>
                        <dt>{severityLabels[item.severity]}</dt>
                        <dd
                          className={
                            item.count > 0
                              ? `current-mission-severity--${item.severity}`
                              : "current-mission-count--empty"
                          }
                        >
                          {item.count}
                        </dd>
                      </div>
                    ))}
                  </dl>
                </div>
                <p className="current-mission-progress">
                  {mission.pentest.completedChecks} contrôles terminés sur{" "}
                  {mission.pentest.plannedChecks} prévus
                </p>
              </>
            )}
            {mission.incident && (
              <>
                <div className="current-mission-results">
                  <strong>
                    {count(
                      mission.incident.confirmedCount,
                      "incident confirmé",
                      "incidents confirmés",
                    )}
                    {" · "}
                    <span
                      className={`current-mission-severity--${mission.incident.priority}`}
                    >
                      Priorité{" "}
                      {severityLabels[mission.incident.priority].toLowerCase()}
                    </span>
                  </strong>
                  <p className="current-mission-impact">
                    {count(
                      mission.incident.affectedDevices,
                      "poste affecté",
                      "postes affectés",
                    )}
                    {" · "}
                    {count(
                      mission.incident.devicesToReview,
                      "poste à examiner",
                      "postes à examiner",
                    )}
                  </p>
                </div>
                <p className="current-mission-action">
                  <Icon name="clock" />
                  {mission.incident.pendingAction}
                </p>
                <p className="current-mission-progress">
                  {mission.incident.analyzedAlerts} alertes analysées sur{" "}
                  {mission.incident.receivedAlerts} reçues
                </p>
              </>
            )}
            {mission.exposure && (
              <>
                <div className="current-mission-results">
                  <strong>
                    {count(
                      mission.exposure.internalDocuments +
                        mission.exposure.publishedApiKeys,
                      "information sensible exposée",
                      "informations sensibles exposées",
                    )}
                  </strong>
                  <p className="current-mission-impact">
                    {count(
                      mission.exposure.internalDocuments,
                      "document interne",
                      "documents internes",
                    )}
                    {" · "}
                    {count(
                      mission.exposure.publishedApiKeys,
                      "clé API",
                      "clés API",
                    )}
                  </p>
                </div>
                <p className="current-mission-progress">
                  {count(
                    mission.exposure.subdomains,
                    "sous-domaine recensé",
                    "sous-domaines recensés",
                  )}
                  {" · "}
                  {count(
                    mission.exposure.consultedSources,
                    "source publique consultée",
                    "sources publiques consultées",
                  )}
                </p>
              </>
            )}
          </div>
          <button
            type="button"
            className="current-mission-toggle"
            aria-expanded={open}
            aria-controls={tasksId}
            onClick={() => setOpen((current) => !current)}
          >
            {open ? "Masquer les détails" : "Voir les détails de la mission"}
            <Icon name="chevron" />
          </button>
        </div>
      </div>
      <ul
        className="current-mission-tasks"
        id={tasksId}
        hidden={!open}
        aria-label={`Agents de la mission ${mission.domainLabel}`}
      >
        {mission.tasks.map((task) => (
          <li key={task.title}>
            <div className="current-task-copy">
              <span>{task.title}</span>
              {task.description && <p>{task.description}</p>}
            </div>
            <span
              className={`current-task-state current-task-state--${task.state}`}
            >
              {taskLabels[task.state]}
            </span>
          </li>
        ))}
      </ul>
    </article>
  );
}
