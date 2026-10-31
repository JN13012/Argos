import data from "../fixtures/workspace.json";
import { isAssessment } from "../features/workspace/assessment";
import type { Assessment, Review } from "../features/workspace/types";

export function fixture(): Assessment {
  const copy: unknown = structuredClone(data);
  if (!isAssessment(copy))
    throw new Error("The UI fixture must satisfy the presentation contract.");
  return copy;
}

export function review(decision: Review["decision"]): Review {
  return {
    decision,
    reviewer: "Analyste",
    reason: "Contexte et documents examinés.",
  };
}
