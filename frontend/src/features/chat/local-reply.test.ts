import { expect, it } from "vitest";
import { summarizeAssessment } from "../workspace/assessment";
import { fixture } from "../../test/fixture";
import { localReply } from "./local-reply";

it("describes proof hashes as declared and directs verification to the core", () => {
  const assessment = fixture();
  const reply = localReply("Voir les preuves", {
    assessment,
    summary: summarizeAssessment(assessment),
    reportAvailable: true,
  });
  expect(reply).toContain("E-001");
  expect(reply).toContain("E-002");
  expect(reply).toContain("déclarées");
  expect(reply).toContain("vérifiée dans Argos Core");
});

it("does not suggest an export when the current dossier has no corresponding report", () => {
  const assessment = fixture();
  const reply = localReply("Exporter le rapport", {
    assessment,
    summary: summarizeAssessment(assessment),
    reportAvailable: false,
  });
  expect(reply).toContain("Aucun rapport correspondant");
});
