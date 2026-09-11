import { readFileSync } from "node:fs";
import { resolve } from "node:path";

import { expect, test } from "@playwright/test";

const sampleComplaint = readFileSync(
  resolve(import.meta.dirname, "../../samples/discoloration-complaint.txt"),
  "utf8",
);

test("analyze, correct, and commit a synthetic complaint", async ({ page }) => {
  await page.goto("/");
  await page.getByLabel("Complaint narrative").fill(sampleComplaint);
  await page.getByRole("button", { name: "Analyze complaint" }).click();

  await expect(page.getByLabel("Batch / lot number")).toHaveValue("AMX240602");
  await expect(page.getByText("AI-suggested severity")).toBeVisible();

  await page.getByLabel("Correct the extracted details").fill(
    "The batch number is BMX240602.",
  );
  await page.getByRole("button", { name: "Send correction" }).click();
  await expect(page.getByLabel("Batch / lot number")).toHaveValue("BMX240602");

  await page.getByRole("button", { name: "Commit to QMS Ledger" }).click();
  await expect(page.getByTestId("ledger-row")).toHaveCount(1);
  await expect(page.getByText("Human-confirmed record")).toBeVisible();
});
