import { test, expect } from "@playwright/test";
import { registerAndNavigateToDashboard } from "./fixtures";

test.describe("Settings Page", () => {
  test.beforeEach(async ({ page }) => {
    await registerAndNavigateToDashboard(page);
    await page.getByLabel("Parametres").click();
    await page.waitForURL("/parametres");
  });

  test("shows patient info", async ({ page }) => {
    await expect(page.getByText("Marie Laurent")).toBeVisible();
    await expect(page.getByText(/TEST-001/)).toBeVisible();
  });

  test("shows active consent", async ({ page }) => {
    await expect(page.getByText("Consent for ai-processing")).toBeVisible();
    await expect(page.getByText("Actif")).toBeVisible();
    await expect(page.getByRole("button", { name: "Revoquer" })).toBeVisible();
  });

  test("shows logout button", async ({ page }) => {
    await expect(
      page.getByRole("button", { name: "Se deconnecter" }),
    ).toBeVisible();
  });
});
