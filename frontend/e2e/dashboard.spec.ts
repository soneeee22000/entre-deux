import { test, expect } from "@playwright/test";
import { registerAndNavigateToDashboard } from "./fixtures";

test.describe("Dashboard", () => {
  test.beforeEach(async ({ page }) => {
    await registerAndNavigateToDashboard(page);
  });

  test("shows 3 quick action cards", async ({ page }) => {
    await expect(page.getByText("Analyser mes resultats")).toBeVisible();
    await expect(page.getByText("Ecrire dans mon journal")).toBeVisible();
    await expect(page.getByText("Preparer mon rendez-vous")).toBeVisible();
  });

  test("shows recent activity with timeline items", async ({ page }) => {
    await expect(page.getByText("Activite recente")).toBeVisible();
    await expect(page.getByText(/HbA1c/)).toBeVisible();
  });

  test("navigates to analyses when card is clicked", async ({ page }) => {
    await page.getByText("Analyser mes resultats").click();
    await page.waitForURL("/analyses");
    await expect(page.getByText("Mes analyses")).toBeVisible();
  });

  test("navigates to journal when card is clicked", async ({ page }) => {
    await page.getByText("Ecrire dans mon journal").click();
    await page.waitForURL("/journal");
    await expect(page.getByText("Mon journal")).toBeVisible();
  });

  test("navigates to bilan when card is clicked", async ({ page }) => {
    await page.getByText("Preparer mon rendez-vous").click();
    await page.waitForURL("/bilan");
    await expect(page.getByText("Bilan de visite")).toBeVisible();
  });

  test("settings button navigates to parametres", async ({ page }) => {
    await page.getByLabel("Parametres").click();
    await page.waitForURL("/parametres");
    await expect(page.getByText("Informations du patient")).toBeVisible();
  });
});
