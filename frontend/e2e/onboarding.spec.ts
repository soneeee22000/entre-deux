import { test, expect } from "@playwright/test";
import { mockAllApiRoutes } from "./fixtures";

test.describe("Onboarding Flow", () => {
  test("welcome page shows app name and CTA", async ({ page }) => {
    await page.goto("/bienvenue");

    await expect(page.getByText("Entre Deux")).toBeVisible();
    await expect(
      page.getByText("Votre compagnon IA entre les rendez-vous"),
    ).toBeVisible();
    await expect(page.getByRole("button", { name: "Commencer" })).toBeVisible();
  });

  test("clicking Commencer shows registration form", async ({ page }) => {
    await page.goto("/bienvenue");
    await page.getByRole("button", { name: "Commencer" }).click();

    await expect(page.getByText("Creer votre profil")).toBeVisible();
    await expect(page.getByLabel("Prenom")).toBeVisible();
    await expect(page.getByLabel("Nom", { exact: true })).toBeVisible();
    await expect(page.getByLabel("Identifiant patient")).toBeVisible();
  });

  test("registering navigates to dashboard with greeting", async ({ page }) => {
    await mockAllApiRoutes(page);
    await page.goto("/bienvenue");

    await page.getByRole("button", { name: "Commencer" }).click();
    await page.getByLabel("Prenom").fill("Marie");
    await page.getByLabel("Nom", { exact: true }).fill("Laurent");
    await page.getByLabel("Identifiant patient").fill("TEST-001");
    await page.getByRole("button", { name: "Creer mon profil" }).click();

    await page.waitForURL("/");
    await expect(page.getByText("Bonjour, Marie")).toBeVisible();
  });
});
