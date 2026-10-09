import {
  act,
  fireEvent,
  render,
  screen,
  waitFor,
  within,
} from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { bundledWorkspaceSource } from "../features/workspace/bundled-source";
import type {
  WorkspaceDocument,
  WorkspaceSource,
} from "../features/workspace/types";
import { fixture, review } from "../test/fixture";
import { App } from "./App";

function sourceFor(assessment: unknown): WorkspaceSource {
  return {
    async load() {
      return {
        assessment,
        report: (await bundledWorkspaceSource.load()).report,
      };
    },
  };
}

describe("home interactions", () => {
  it("restores the classic home with five metrics, an open chat and one export", async () => {
    render(<App />);
    expect(
      await screen.findByRole("heading", { name: fixture().mission.title }),
    ).toBeVisible();
    expect(
      screen
        .getAllByText(fixture().mission.title)
        .filter((node) => node.closest("dialog") === null),
    ).toHaveLength(1);
    expect(
      screen.getAllByRole("link", { name: "Télécharger le rapport" }),
    ).toHaveLength(1);
    expect(screen.getByText("1 événement")).toBeVisible();
    expect(
      screen.getByRole("heading", { name: "Bienvenue dans Argos" }),
    ).toBeVisible();
    expect(document.querySelectorAll(".metric-card")).toHaveLength(5);
    expect(screen.getByRole("heading", { name: "Agents" })).toBeVisible();
    expect(document.getElementById("chat-content")).toBeVisible();
  });

  it("opens only the chosen finding and its proofs, then the whole mission", async () => {
    render(<App />);
    fireEvent.click(
      await screen.findByRole("button", { name: /Examiner F-002/ }),
    );
    const dialog = screen.getByRole("dialog", { name: "Bannière applicative" });
    expect(dialog.querySelectorAll(".finding-card")).toHaveLength(1);
    expect(within(dialog).getByText(/E-002 · banner.txt/)).toBeVisible();
    expect(within(dialog).queryByText(/E-001 · configuration.txt/)).toBeNull();
    fireEvent.click(
      within(dialog).getByRole("button", { name: "Voir toute la mission" }),
    );
    expect(dialog.querySelectorAll(".finding-card")).toHaveLength(2);
  });

  it("searches without accents and reports an empty result", async () => {
    render(<App />);
    await screen.findByRole("button", { name: /Examiner F-002/ });
    fireEvent.change(screen.getByRole("searchbox"), {
      target: { value: "banniere" },
    });
    expect(
      screen.getByRole("button", { name: /Examiner F-002/ }),
    ).toBeVisible();
    expect(screen.queryByRole("button", { name: /Examiner F-001/ })).toBeNull();
    fireEvent.change(screen.getByRole("searchbox"), {
      target: { value: "aucun-resultat-xyz" },
    });
    expect(
      screen.getByText(
        "Aucun constat ou rapport ne correspond à cette recherche.",
      ),
    ).toBeVisible();
  });

  it("escapes user messages and retains conversation when collapsed", async () => {
    render(<App />);
    await screen.findByRole("button", { name: /Examiner F-001/ });
    const text = '<img src=x onerror="window.argosXss=true">';
    fireEvent.change(
      screen.getByRole("textbox", { name: "Question sur la mission" }),
      { target: { value: text } },
    );
    fireEvent.click(screen.getByRole("button", { name: "Envoyer le message" }));
    expect(screen.getByText(text)).toBeVisible();
    expect(
      document.getElementById("chat-messages")?.querySelector("img"),
    ).toBeNull();
    fireEvent.click(
      screen.getByRole("button", { name: "Réduire la conversation" }),
    );
    expect(screen.getByText(text)).not.toBeVisible();
    fireEvent.click(
      screen.getByRole("button", { name: "Ouvrir la conversation" }),
    );
    expect(screen.getByText(text)).toBeVisible();
  });

  it("limits logs to three rows until expanded and filters by actual actions", async () => {
    render(<App />);
    const open = await screen.findByRole("button", {
      name: "Ouvrir le dossier",
    });
    for (let i = 0; i < 4; i++) {
      fireEvent.click(open);
      fireEvent.click(
        screen.getByRole("button", { name: "Fermer le dossier" }),
      );
    }
    expect(document.querySelectorAll(".activity-row")).toHaveLength(3);
    fireEvent.click(
      screen.getByRole("button", { name: "Développer le journal" }),
    );
    expect(document.querySelectorAll(".activity-row")).toHaveLength(5);
    fireEvent.change(screen.getByRole("combobox"), {
      target: { value: "report" },
    });
    expect(document.querySelectorAll(".activity-row")).toHaveLength(0);
    expect(
      screen.getByText("Aucun événement ne correspond à ce filtre."),
    ).toBeVisible();
  });

  it("keeps loading distinct until the source resolves", async () => {
    let resolve: (document: WorkspaceDocument) => void = () => {};
    const promise = new Promise<WorkspaceDocument>((done) => {
      resolve = done;
    });
    render(<App source={{ load: () => promise }} />);
    expect(
      screen.getByRole("heading", { name: "Chargement du dossier" }),
    ).toBeVisible();
    expect(
      screen.queryByRole("button", { name: "Ouvrir le dossier" }),
    ).toBeNull();
    resolve(await bundledWorkspaceSource.load());
    expect(
      await screen.findByRole("button", { name: "Ouvrir le dossier" }),
    ).toBeVisible();
  });

  it.each([
    [null, "Aucune mission disponible"],
    [undefined, "Dossier indisponible"],
    [{}, "Dossier indisponible"],
  ])(
    "does not replace unavailable input %s with fictional data",
    async (input, title) => {
      render(<App source={sourceFor(input)} />);
      expect(await screen.findByRole("heading", { name: title })).toBeVisible();
      expect(
        screen.queryByRole("button", { name: "Ouvrir le dossier" }),
      ).toBeNull();
      expect(screen.getByRole("searchbox")).toBeDisabled();
      fireEvent.click(
        screen.getAllByRole("button", { name: /À propos d’Argos/ })[0]!,
      );
      expect(
        screen.getByRole("dialog", { name: "À propos de cet espace" }),
      ).toBeVisible();
    },
  );

  it("disables the old report and removes pending priorities after completed reviews", async () => {
    const data = fixture();
    const changed = {
      ...data,
      findings: data.findings.map((finding) => ({
        ...finding,
        review: review("accepted"),
      })),
    };
    render(<App source={sourceFor(changed)} />);
    await waitFor(() =>
      expect(document.getElementById("main-content")).toHaveAttribute(
        "data-state",
        "ready",
      ),
    );
    expect(
      screen.queryByRole("link", { name: "Télécharger le rapport" }),
    ).toBeNull();
    expect(
      screen.getByText("Aucun rapport ne correspond au dossier actuel."),
    ).toBeVisible();
    expect(document.querySelectorAll(".priority-row")).toHaveLength(0);
  });

  it("handles a failed source without exposing a mission", async () => {
    render(
      <App
        source={{
          async load() {
            throw new Error("source unavailable");
          },
        }}
      />,
    );
    expect(
      await screen.findByRole("heading", { name: "Dossier indisponible" }),
    ).toBeVisible();
    expect(
      screen.queryByRole("link", { name: "Télécharger le rapport" }),
    ).toBeNull();
  });

  it("ignores a late response from a source that has been replaced", async () => {
    let resolveOld: (document: WorkspaceDocument) => void = () => {};
    const oldResponse = new Promise<WorkspaceDocument>((resolve) => {
      resolveOld = resolve;
    });
    const { rerender } = render(<App source={{ load: () => oldResponse }} />);
    const data = fixture();
    const next = {
      ...data,
      mission: { ...data.mission, title: "Mission suivante" },
    };
    rerender(<App source={sourceFor(next)} />);
    expect(
      await screen.findByRole("heading", { name: "Mission suivante" }),
    ).toBeVisible();
    await act(async () => {
      resolveOld({ assessment: data, report: null });
    });
    expect(
      screen.getByRole("heading", { name: "Mission suivante" }),
    ).toBeVisible();
    expect(
      screen.queryByRole("heading", { name: data.mission.title }),
    ).toBeNull();
  });
});
