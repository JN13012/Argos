import { Button } from "../../components/Button";
import { Icon } from "../../components/Icon";
import type { WorkspaceState } from "../workspace/useWorkspace";

export function WorkspaceStatus({
  state,
}: {
  state: Exclude<WorkspaceState, { status: "ready" }>;
}) {
  const title =
    state.status === "loading"
      ? "Chargement du dossier"
      : state.status === "empty"
        ? "Aucune mission disponible"
        : "Dossier indisponible";
  const description =
    state.status === "loading"
      ? "Les informations de la mission sont en cours de chargement."
      : state.status === "empty"
        ? "Aucun dossier de mission n’est disponible dans cet espace."
        : state.reason === "invalid"
          ? "Le dossier est incomplet ou contient des informations incompatibles."
          : "Les données de la mission n’ont pas pu être chargées. Réessayez pour consulter le dossier.";

  return (
    <section
      className="panel workspace-status"
      role="status"
      aria-live="polite"
      aria-labelledby="workspace-status-title"
    >
      <span
        className={`workspace-status-icon ${state.status === "loading" ? "loading" : ""}`}
      >
        <Icon name={state.status === "error" ? "alert" : "folder"} />
      </span>
      <h2 id="workspace-status-title">{title}</h2>
      <p>{description}</p>
      {state.status !== "loading" && (
        <Button onClick={() => location.reload()}>
          Recharger les données <Icon name="arrow" />
        </Button>
      )}
    </section>
  );
}
