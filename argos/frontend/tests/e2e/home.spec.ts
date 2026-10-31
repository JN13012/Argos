import { expect, test } from "@playwright/test";

test("shows the minimal home and verifies the local API", async ({ page }) => {
  const errors: string[] = [];
  page.on("pageerror", (error) => errors.push(error.message));

  await page.goto("/");

  await expect(
    page.getByRole("heading", { name: "Bienvenue sur ARGOS" }),
  ).toBeVisible();
  await expect(page.getByRole("status")).toHaveText("API disponible");
  await expect(
    page.getByRole("link", { name: "Accueil", exact: true }),
  ).toHaveAttribute("aria-current", "page");
  for (const domain of ["ATTACK", "INTEL", "DEFEND"]) {
    await expect(page.getByText(`${domain} · à venir`)).toHaveAttribute(
      "aria-disabled",
      "true",
    );
  }
  expect(errors).toEqual([]);
});
