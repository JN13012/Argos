import reportUrl from "../../../assets/mission-report.md?url";
import fixture from "../../fixtures/workspace.json";
import type { WorkspaceSource } from "./types";

// Fictional dossier, original synthetic proofs. No system has been tested.
export const bundledWorkspaceSource: WorkspaceSource = {
  async load() {
    return {
      assessment: fixture,
      report: {
        url: reportUrl,
        sourceHash:
          "70fcd51e85a047021ebfb575836664839cfeebc804e1af5800f45dc5b3dd208d",
      },
    };
  },
};
