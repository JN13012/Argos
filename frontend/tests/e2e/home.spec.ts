import { expect, test } from "@playwright/test";
import { readFileSync } from "node:fs";
import { resolve } from "node:path";

test.beforeEach(async ({ page }) => {
  await page.goto("/");
  await expect(page.locator("#main-content")).toHaveAttribute(
    "data-state",
    "ready",
  );
});

test("restores the classic home and serves its assets locally", async ({
  page,
  baseURL,
}) => {
  const requests: string[] = [];
  const errors: string[] = [];
  page.on("request", (request) => requests.push(request.url()));
  page.on("pageerror", (error) => errors.push(error.message));
  await page.reload();
  await expect(
    page.getByRole("heading", { name: "Audit de configuration interne" }),
  ).toBeVisible();
  await expect(
    page.getByRole("link", { name: "Télécharger le rapport" }),
  ).toHaveCount(1);
  await expect(page.locator(".priority-row")).toHaveCount(2);
  await expect(page.locator(".activity-row")).toHaveCount(1);
  await expect(
    page.getByRole("heading", { name: "Bienvenue dans Argos" }),
  ).toHaveCount(0);
  await expect(page.locator(".welcome-panel")).toHaveCount(0);
  await expect(page.getByText("ARGOS / ACCUEIL", { exact: true })).toHaveCount(
    0,
  );
  await expect(
    page.getByRole("heading", { name: "Vue d’ensemble" }),
  ).toHaveCount(0);
  await expect(page.locator(".brand-logo--header")).toHaveAttribute(
    "src",
    /argos-wolf-kraken/,
  );
  await expect(page.locator(".metric-card")).toHaveCount(5);
  await expect(page.locator("#chat-content")).toBeVisible();
  await expect(
    page.getByRole("textbox", { name: "Question sur la mission" }),
  ).toBeVisible();
  const logos = await page.locator(".brand-logo").evaluateAll(async (nodes) => {
    const images = nodes as HTMLImageElement[];
    await Promise.all(images.map((image) => image.decode()));
    return images.map((image) => ({
      width: image.naturalWidth,
      height: image.naturalHeight,
    }));
  });
  expect(logos).toEqual([{ width: 1254, height: 1254 }]);
  expect(
    requests.filter((url) => new URL(url).origin !== new URL(baseURL!).origin),
  ).toEqual([]);
  expect(errors).toEqual([]);
});

test("opens a selected finding with native modal focus and returns to its trigger", async ({
  page,
}) => {
  const trigger = page.getByRole("button", {
    name: "Examiner F-002 : Bannière applicative",
  });
  await trigger.click();
  const dialog = page.getByRole("dialog", { name: "Bannière applicative" });
  await expect(dialog.locator(".finding-card")).toHaveCount(1);
  await expect(dialog.locator(".finding-card")).toBeFocused();
  await expect(dialog.getByText("E-002 · banner.txt")).toBeVisible();
  await page.keyboard.press("Escape");
  await expect(dialog).toBeHidden();
  await expect(trigger).toBeFocused();
  await trigger.click();
  await page.getByRole("button", { name: "Voir toute la mission" }).click();
  await expect(page.locator("#mission-dialog .finding-card")).toHaveCount(2);
  await expect(page.locator("#mission-review-count")).toHaveText(
    "0 / 2 constats revus",
  );
});

test("downloads the corresponding report and logs the request", async ({
  page,
}) => {
  const downloadPromise = page.waitForEvent("download");
  await page.getByRole("link", { name: "Télécharger le rapport" }).click();
  const download = await downloadPromise;
  expect(download.suggestedFilename()).toBe("argos-MIS-001.md");
  expect(readFileSync((await download.path())!)).toEqual(
    readFileSync(resolve("assets/mission-report.md")),
  );
  await expect(page.locator(".activity-text").first()).toHaveText(
    "Téléchargement du rapport demandé.",
  );
});

test("retains messages and draft through chat expansion, traps focus and restores it", async ({
  page,
}) => {
  await page.getByRole("button", { name: "Ouvrir Argos Chat" }).click();
  const input = page.getByRole("textbox", { name: "Question sur la mission" });
  await expect(input).toBeFocused();
  const userText = '<img src=x onerror="window.argosXss=true">';
  await input.fill(userText);
  await input.press("Enter");
  await expect(page.locator(".user-message p")).toHaveText(userText);
  expect(await page.evaluate(() => "argosXss" in window)).toBe(false);
  await input.fill("Brouillon à conserver");
  await page
    .getByRole("button", { name: "Agrandir le panneau de chat" })
    .click();
  const dialog = page.getByRole("dialog", { name: "Argos Chat" });
  await expect(dialog).toBeVisible();
  await expect(dialog.getByRole("textbox")).toHaveValue(
    "Brouillon à conserver",
  );
  await expect(dialog.getByRole("textbox")).toBeFocused();
  for (let i = 0; i < 10; i++) {
    await page.keyboard.press("Tab");
    expect(
      await dialog.evaluate((node) => node.contains(document.activeElement)),
    ).toBe(true);
  }
  await page.keyboard.press("Escape");
  await expect(dialog).toBeHidden();
  await expect(
    page.getByRole("button", { name: "Agrandir le panneau de chat" }),
  ).toBeFocused();
  await expect(input).toHaveValue("Brouillon à conserver");
  await page.getByRole("button", { name: "Réduire la conversation" }).click();
  await expect(page.locator("#chat-content")).toBeHidden();
  await page.getByRole("button", { name: "Ouvrir la conversation" }).click();
  await expect(page.locator(".user-message p")).toHaveText(userText);
});

test("searches via keyboard and filters findings", async ({
  page,
}, testInfo) => {
  test.skip(
    testInfo.project.name === "mobile",
    "The compact header hides desktop search.",
  );
  await page.keyboard.press("Control+k");
  await expect(page.getByRole("searchbox")).toBeFocused();
  await page.getByRole("searchbox").fill("banniere");
  await expect(page.locator(".priority-row")).toHaveCount(1);
  await page.getByRole("searchbox").fill("aucun-resultat-xyz");
  await expect(page.locator("#search-feedback")).toHaveText(
    "Aucun constat ou rapport ne correspond à cette recherche.",
  );
});

test("opens mobile navigation and excludes the closed drawer from keyboard navigation", async ({
  page,
}, testInfo) => {
  test.skip(
    testInfo.project.name !== "mobile",
    "The desktop sidebar stays visible.",
  );
  await expect(page.locator("#sidebar")).toHaveAttribute("inert", "");
  await page.getByRole("button", { name: "Ouvrir la navigation" }).click();
  await expect(
    page.getByRole("navigation", { name: "Espaces Argos" }),
  ).toBeVisible();
  await page.getByRole("link", { name: "Accueil", exact: true }).focus();
  await page.keyboard.press("Escape");
  await expect(
    page.getByRole("button", { name: "Ouvrir la navigation" }),
  ).toBeFocused();
  await expect(page.locator("#sidebar")).toHaveAttribute("inert", "");
});

test("fits all widths with chat beside the overview on desktop and logs below", async ({
  page,
}, testInfo) => {
  test.skip(
    testInfo.project.name !== "desktop",
    "One project covers the responsive width matrix.",
  );
  for (const width of [1920, 1440, 1280, 1024, 920, 768, 700, 390, 320]) {
    await page.setViewportSize({ width, height: 1000 });
    await expect(page.locator(".mobile-menu")).toBeVisible({
      visible: width <= 700,
    });
    await expect(
      page.getByRole("button", { name: /Nouvelle mission/ }),
    ).toBeVisible({ visible: width > 700 });
    expect(
      await page.evaluate(
        () => document.documentElement.scrollWidth > window.innerWidth,
      ),
      `overflow at ${width}px`,
    ).toBe(false);
    const logs = await page.locator(".activity-panel").boundingBox();
    const chat = await page.locator("#chat-panel").boundingBox();
    const overview = await page.locator(".overview-column").boundingBox();
    expect(logs!.y).toBeGreaterThanOrEqual(chat!.y + chat!.height);
    if (width > 920) {
      expect(chat!.x).toBeGreaterThanOrEqual(overview!.x + overview!.width);
      expect(Math.abs(chat!.y - overview!.y)).toBeLessThan(1);
    } else {
      expect(chat!.y).toBeGreaterThanOrEqual(overview!.y + overview!.height);
    }
    await page.getByRole("button", { name: "Réduire la conversation" }).click();
    expect(
      await page.evaluate(
        () => document.documentElement.scrollWidth > window.innerWidth,
      ),
      `collapsed chat overflow at ${width}px`,
    ).toBe(false);
    await page.getByRole("button", { name: "Ouvrir la conversation" }).click();
  }
});
