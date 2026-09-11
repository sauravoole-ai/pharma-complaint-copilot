import { afterEach, describe, expect, it, vi } from "vitest";

import { analyzeText, ApiClientError } from "./client";

afterEach(() => vi.unstubAllGlobals());

describe("API response boundary", () => {
  it("rejects a successful response that does not match the draft contract", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(
        new Response(JSON.stringify({ id: "not-a-draft" }), {
          status: 201,
          headers: { "Content-Type": "application/json" },
        }),
      ),
    );

    await expect(analyzeText("complaint")).rejects.toThrow(
      new ApiClientError("The server returned an invalid response"),
    );
  });

  it("uses the safe API error message when a request fails", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(
        new Response(JSON.stringify({ code: "ai_failed", message: "Analysis unavailable" }), {
          status: 502,
          headers: { "Content-Type": "application/json" },
        }),
      ),
    );

    await expect(analyzeText("complaint")).rejects.toThrow("Analysis unavailable");
  });
});
