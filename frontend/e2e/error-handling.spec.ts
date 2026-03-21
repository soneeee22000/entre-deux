import { test, expect } from "@playwright/test";
import { registerAndNavigateToDashboard } from "./fixtures";

test.describe("Error Handling", () => {
  test("shows error banner when API returns 502", async ({ page }) => {
    await registerAndNavigateToDashboard(page);
    await page.getByText("Ecrire dans mon journal").click();
    await page.waitForURL("/journal");

    await page.route("**/api/v1/questionnaire-responses", async (route) => {
      if (route.request().method() === "POST") {
        await route.fulfill({
          status: 502,
          json: {
            detail: "Le service d'IA est temporairement indisponible.",
            code: "AI_UNAVAILABLE",
          },
        });
      } else {
        await route.fallback();
      }
    });

    await page.getByPlaceholder(/Comment vous sentez-vous/).fill("Test entry");
    await page.getByRole("button", { name: "Envoyer" }).click();

    await expect(page.getByText(/temporairement indisponible/)).toBeVisible();
  });

  test("visit brief page strips HTML from sections (XSS prevention)", async ({
    page,
  }) => {
    await registerAndNavigateToDashboard(page);
    await page.getByText("Preparer mon rendez-vous").click();
    await page.waitForURL("/bilan");

    await expect(page.getByText("Bilans precedents")).toBeVisible();
    await page.getByText("Visit Brief").click();

    await expect(page.getByText("HbA1c amelioree")).toBeVisible();

    const pageContent = await page.textContent("body");
    expect(pageContent).not.toContain("<div>HbA1c");
  });
});
