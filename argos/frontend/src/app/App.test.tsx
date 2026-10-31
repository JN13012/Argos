import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { App } from "./App";

const healthyResponse = {
  ok: true,
  status: 200,
  json: async () => ({ status: "ok" }),
} as Response;

describe("ARGOS application shell", () => {
  beforeEach(() => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(healthyResponse));
  });

  it("checks the API health endpoint and exposes only implemented navigation", async () => {
    render(<App />);

    expect(await screen.findByRole("status")).toHaveTextContent(
      "API disponible",
    );
    expect(fetch).toHaveBeenCalledWith(
      "/api/v1/health",
      expect.objectContaining({ headers: { Accept: "application/json" } }),
    );
    expect(screen.getByRole("link", { name: "Accueil" })).toHaveAttribute(
      "aria-current",
      "page",
    );
    expect(screen.getByText("ATTACK · à venir")).toHaveAttribute(
      "aria-disabled",
      "true",
    );
    expect(screen.getByText("INTEL · à venir")).toHaveAttribute(
      "aria-disabled",
      "true",
    );
    expect(screen.getByText("DEFEND · à venir")).toHaveAttribute(
      "aria-disabled",
      "true",
    );
  });

  it("reports an unavailable API and allows a retry", async () => {
    const fetchMock = vi
      .fn()
      .mockRejectedValueOnce(new Error("Failed to fetch"))
      .mockResolvedValueOnce(healthyResponse);
    vi.stubGlobal("fetch", fetchMock);
    render(<App />);

    expect(await screen.findByRole("status")).toHaveTextContent(
      "API indisponible",
    );
    expect(screen.getByText(/Failed to fetch/)).toBeVisible();
    fireEvent.click(screen.getByRole("button", { name: "Réessayer" }));

    await waitFor(() =>
      expect(screen.getByRole("status")).toHaveTextContent("API disponible"),
    );
    expect(fetchMock).toHaveBeenCalledTimes(2);
  });

  it("rejects a successful HTTP response with an invalid health contract", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ...healthyResponse,
        json: async () => ({ status: "degraded" }),
      }),
    );
    render(<App />);

    expect(await screen.findByRole("status")).toHaveTextContent(
      "API indisponible",
    );
    expect(
      screen.getByText(/ne respecte pas le contrat de santé/),
    ).toBeVisible();
  });
});
