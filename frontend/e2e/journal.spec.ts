import { test, expect } from "@playwright/test";
import { registerAndNavigateToDashboard } from "./fixtures";

test.describe("Journal Page", () => {
  test.beforeEach(async ({ page }) => {
    await registerAndNavigateToDashboard(page);
    await page.getByText("Ecrire dans mon journal").click();
    await page.waitForURL("/journal");
  });

  test("shows journal form with textarea and submit button", async ({
    page,
  }) => {
    await expect(page.getByText("Mon journal")).toBeVisible();
    await expect(
      page.getByPlaceholder(/Comment vous sentez-vous/),
    ).toBeVisible();
    await expect(page.getByRole("button", { name: "Envoyer" })).toBeDisabled();
  });

  test("submit button enables when text is entered", async ({ page }) => {
    await page.getByPlaceholder(/Comment vous sentez-vous/).fill("Test entry");
    await expect(page.getByRole("button", { name: "Envoyer" })).toBeEnabled();
  });

  test("submitting entry shows AI response", async ({ page }) => {
    await page
      .getByPlaceholder(/Comment vous sentez-vous/)
      .fill("Je me sens bien");
    await page.getByRole("button", { name: "Envoyer" }).click();

    await expect(
      page.getByText("Merci de partager, c'est formidable !"),
    ).toBeVisible();
  });

  test("shows journal entry history", async ({ page }) => {
    await expect(page.getByText("Historique")).toBeVisible();
    await expect(page.getByText(/Je me sens bien aujourd'hui/)).toBeVisible();
  });
});
