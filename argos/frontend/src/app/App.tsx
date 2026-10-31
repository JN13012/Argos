import { useEffect, useState } from "react";
import "./App.css";

type ApiHealth =
  | { status: "checking" }
  | { status: "available" }
  | { status: "unavailable"; reason: string };

function isHealthyResponse(value: unknown): value is { status: "ok" } {
  return (
    typeof value === "object" &&
    value !== null &&
    "status" in value &&
    value.status === "ok"
  );
}

export function App() {
  const [health, setHealth] = useState<ApiHealth>({ status: "checking" });
  const [retry, setRetry] = useState(0);

  useEffect(() => {
    const controller = new AbortController();
    let active = true;

    async function checkApi() {
      setHealth({ status: "checking" });
      try {
        const response = await fetch("/api/v1/health", {
          headers: { Accept: "application/json" },
          signal: controller.signal,
        });
        if (!response.ok) {
          throw new Error(
            `L’API a répondu avec le statut HTTP ${response.status}.`,
          );
        }

        const payload: unknown = await response.json();
        if (!isHealthyResponse(payload)) {
          throw new Error(
            "La réponse reçue ne respecte pas le contrat de santé.",
          );
        }
        if (active) setHealth({ status: "available" });
      } catch (error: unknown) {
        if (!active || controller.signal.aborted) return;
        const reason =
          error instanceof Error
            ? error.message
            : "Erreur de connexion inconnue.";
        setHealth({ status: "unavailable", reason });
      }
    }

    void checkApi();
    return () => {
      active = false;
      controller.abort();
    };
  }, [retry]);

  const statusText = {
    checking: "Vérification en cours…",
    available: "API disponible",
    unavailable: "API indisponible",
  }[health.status];

  return (
    <div className="app-home">
      <header className="app-header">
        <a className="app-brand" href="/" aria-label="ARGOS — accueil">
          ARGOS
        </a>
        <nav className="app-navigation" aria-label="Navigation principale">
          <a className="current" href="/" aria-current="page">
            Accueil
          </a>
          <span className="future" aria-disabled="true">
            ATTACK · à venir
          </span>
          <span className="future" aria-disabled="true">
            INTEL · à venir
          </span>
          <span className="future" aria-disabled="true">
            DEFEND · à venir
          </span>
        </nav>
      </header>

      <main className="app-main">
        <p className="app-eyebrow">Socle applicatif</p>
        <h1>Bienvenue sur ARGOS</h1>
        <p className="app-intro">
          Les espaces métier apparaîtront ici lorsqu’ils seront réellement
          implémentés. Aucune opération de sécurité n’est disponible dans ce
          socle initial.
        </p>

        <section
          className="api-status"
          aria-live="polite"
          aria-busy={health.status === "checking"}
        >
          <h2 className={`api-state-${health.status}`} role="status">
            {statusText}
          </h2>
          <p>
            {health.status === "checking" &&
              "Connexion au service local de l’API."}
            {health.status === "available" &&
              "Le point de santé répond. Cela ne valide aucune fonctionnalité métier."}
            {health.status === "unavailable" &&
              `Échec de la vérification : ${health.reason}`}
          </p>
          <button
            type="button"
            onClick={() => setRetry((current) => current + 1)}
            disabled={health.status === "checking"}
          >
            Réessayer
          </button>
        </section>

        <p className="app-note">
          ATTACK, INTEL et DEFEND sont des espaces prévus, pas des capacités
          opérationnelles.
        </p>
      </main>
    </div>
  );
}
