import { useEffect, useRef } from "react";
import { Badge, ReviewBadge, SeverityBadge } from "../../components/Badge";
import { Button } from "../../components/Button";
import { Icon } from "../../components/Icon";
import { Modal } from "../../components/Modal";
import type { WorkspaceSummary } from "../workspace/assessment";
import type { Assessment, Evidence, Finding } from "../workspace/types";
import "./MissionDialog.css";

export interface MissionSelection {
  findingId: string | null;
}

interface MissionDialogProps {
  assessment: Assessment;
  summary: WorkspaceSummary;
  selection: MissionSelection | null;
  onShowAll(): void;
  onClose(): void;
}

function FindingCard({
  finding,
  evidence,
}: {
  finding: Finding;
  evidence: readonly Evidence[];
}) {
  return (
    <article
      className="finding-card"
      data-finding-id={finding.id}
      tabIndex={-1}
    >
      <div className="finding-heading">
        <span className="finding-id">{finding.id}</span>
        <h3>{finding.title}</h3>
        <SeverityBadge severity={finding.severity} />
        <Badge
          tone={
            finding.review === null
              ? "amber"
              : finding.review.decision === "accepted"
                ? "green"
                : "red"
          }
        >
          {finding.review === null
            ? "À revoir"
            : finding.review.decision === "accepted"
              ? "Accepté"
              : "Rejeté"}
        </Badge>
      </div>
      <p>{finding.description}</p>
      <p>
        <strong>Recommandation :</strong> {finding.recommendation}
      </p>
      <p className="finding-asset">
        Actif : <span>{finding.asset}</span>
      </p>
      {finding.review && (
        <div className="finding-review">
          <strong>Revue par {finding.review.reviewer}</strong>
          <p>{finding.review.reason}</p>
        </div>
      )}
      <div className="finding-proofs">
        {evidence.map((proof) => (
          <div className="finding-evidence" key={proof.id}>
            <Icon name="file" />
            <span>
              {proof.id} · {proof.path.split("/").pop()}
            </span>
            <code title={proof.sha256}>
              SHA-256 déclaré : {proof.sha256.slice(0, 8)}…
              {proof.sha256.slice(-8)}
            </code>
          </div>
        ))}
      </div>
    </article>
  );
}

export function MissionDialog({
  assessment,
  summary,
  selection,
  onShowAll,
  onClose,
}: MissionDialogProps) {
  const contentRef = useRef<HTMLDivElement>(null);
  const finding = assessment.findings.find(
    (item) => item.id === selection?.findingId,
  );
  const visibleFindings = finding ? [finding] : assessment.findings;

  useEffect(() => {
    if (selection && finding)
      contentRef.current
        ?.querySelector<HTMLElement>(".finding-card")
        ?.focus({ preventScroll: true });
  }, [selection, finding]);

  return (
    <Modal
      id="mission-dialog"
      open={selection !== null}
      onClose={onClose}
      closeLabel="Fermer le dossier"
      title={finding?.title ?? assessment.mission.title}
      eyebrow={`MISSION / ${assessment.mission.id}${finding ? ` · CONSTAT / ${finding.id}` : ""}`}
    >
      <p className="dialog-description">{assessment.mission.description}</p>
      <div className="dialog-scope">
        <Icon name="globe" />
        <span>Périmètre</span>
        <span className="scope-value">
          {assessment.mission.scope.join(", ")}
        </span>
        <ReviewBadge summary={summary} />
      </div>
      <div className="dialog-overview">
        <span id="mission-review-count">
          {summary.reviewedCount} / {summary.findingCount} constat
          {summary.findingCount === 1 ? "" : "s"} revu
          {summary.findingCount === 1 ? "" : "s"}
        </span>
        <span data-evidence-count>
          {summary.evidenceCount} preuve{summary.evidenceCount === 1 ? "" : "s"}{" "}
          référencée{summary.evidenceCount === 1 ? "" : "s"}
        </span>
      </div>
      {finding && (
        <Button
          variant="quiet"
          id="show-all-findings"
          className="finding-back"
          onClick={onShowAll}
        >
          Voir toute la mission <Icon name="arrow" />
        </Button>
      )}
      <div ref={contentRef} id="mission-findings">
        {visibleFindings.map((item) => (
          <FindingCard
            key={item.id}
            finding={item}
            evidence={assessment.evidence.filter((proof) =>
              item.evidence_ids.includes(proof.id),
            )}
          />
        ))}
        {!visibleFindings.length && (
          <p className="empty-message">{summary.reviewNote}</p>
        )}
      </div>
      <p className="dialog-footer">
        L’intégrité d’une preuve et la décision de revue sont distinctes de la
        confirmation technique d’une vulnérabilité.
      </p>
    </Modal>
  );
}
