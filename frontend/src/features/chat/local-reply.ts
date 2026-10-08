import { severityLabels } from "../workspace/assessment";
import type { WorkspaceSummary } from "../workspace/assessment";
import { normalizeSearch } from "../workspace/search";
import type { Assessment } from "../workspace/types";

export interface ChatContext {
  assessment: Assessment;
  summary: WorkspaceSummary;
  reportAvailable: boolean;
}

// Deterministic local replies. This is a dossier helper, not a connected model.
export function localReply(
  question: string,
  { assessment, summary, reportAvailable }: ChatContext,
): string {
  const normalized = normalizeSearch(question);
  const {
    pendingCount,
    pendingFindings,
    findingCount,
    evidenceCount,
    criticalCount,
    reviewNote,
  } = summary;

  if (/preuve|evidence|fichier|hash|sha/.test(normalized)) {
    if (!evidenceCount)
      return "Aucune preuve n’est encore référencée dans cette mission.";
    return `${evidenceCount} preuve${evidenceCount === 1 ? " est référencée" : "s sont référencées"} :\n\n${assessment.evidence.map((proof) => `${proof.id} — ${proof.path.split("/").pop()}`).join("\n")}\n\nLes empreintes SHA-256 sont déclarées dans le dossier. Leur intégrité doit être vérifiée dans Argos Core avant export.`;
  }
  if (/critique/.test(normalized))
    return `${criticalCount} constat${criticalCount === 1 ? " critique est" : "s critiques sont"} enregistré${criticalCount === 1 ? "" : "s"} dans cette mission. Ce nombre porte uniquement sur les constats du dossier.`;
  if (/constat|revue|vulnerab|diagnostic/.test(normalized)) {
    if (!pendingCount) return reviewNote;
    return `${pendingCount} constat${pendingCount === 1 ? " attend" : "s attendent"} une revue :\n\n${pendingFindings.map((finding) => `${finding.id} — ${finding.title} (${severityLabels[finding.severity].toLowerCase()}).`).join("\n")}\n\nExaminez chaque preuve et le contexte avant de retenir ou rejeter un constat.`;
  }
  if (/agent|statut|connexion/.test(normalized)) {
    return `Aucun agent ni moteur d’analyse n’est connecté à cet espace. Le dossier peut être consulté.${reportAvailable ? " Son rapport est disponible au téléchargement." : " Aucun rapport correspondant à ce dossier n’est disponible."}`;
  }
  if (/rapport|export|telecharg/.test(normalized)) {
    if (!reportAvailable)
      return "Aucun rapport correspondant au dossier actuel n’est disponible. Vous pouvez consulter ses constats et les métadonnées de ses preuves dans la mission.";
    return `Le rapport « ${assessment.mission.title} » est disponible dans « Rapports & documents ». Il contient ${findingCount} constat${findingCount === 1 ? "" : "s"} et les métadonnées de ${evidenceCount} preuve${evidenceCount === 1 ? "" : "s"}. ${reviewNote}`;
  }
  if (/mission|resum|perimetre|actif|bonjour|aide/.test(normalized)) {
    return `Mission ${assessment.mission.id} — ${assessment.mission.title}.\n\nPérimètre : ${assessment.mission.scope.join(", ")}.\n${findingCount} constat${findingCount === 1 ? "" : "s"} et ${evidenceCount} preuve${evidenceCount === 1 ? "" : "s"} référencée${evidenceCount === 1 ? "" : "s"}.\n${reviewNote}\n\nUtilisez « Ouvrir le dossier » pour consulter les détails.`;
  }
  return "Je peux présenter la mission, lister ses constats, retrouver les preuves et indiquer les rapports disponibles. Précisez votre question ou choisissez l’un des raccourcis de mission.";
}
