import { configureStore } from "@reduxjs/toolkit";
import { render, screen } from "@testing-library/react";
import { Provider } from "react-redux";
import userEvent from "@testing-library/user-event";
import { describe, expect, it } from "vitest";

import complaintReducer, { type ComplaintState } from "../store/complaintSlice";
import type { DraftResponse } from "../types/complaint";
import { ComplaintWorkspace } from "./ComplaintWorkspace";

const readyDraft: DraftResponse = {
  id: "00000000-0000-0000-0000-000000000001",
  source_type: "text",
  fields: {
    complaint_source: "Email",
    customer_name: "Northstar Pharmacy",
    product_type: "Capsule",
    product_name: "Amoxicillin",
    product_strength: "500 mg",
    batch_lot_number: "AMX240602",
    affected_quantity: "48 capsules",
    manufacturing_date: null,
    expiry_date: null,
    originating_site_block: null,
    impacted_non_product_materials: null,
    complaint_category: "Product quality",
    complaint_description: "Capsules appeared discolored.",
    customer_requested_action: "Replacement and investigation",
  },
  completeness: { is_complete: true, missing_fields: [], uncertain_fields: [] },
  risk: {
    severity: "Major",
    next_action: "Quarantine and investigate.",
    rationale: "Potential product quality defect.",
  },
  summary: "A pharmacy reported discolored amoxicillin capsules.",
  status: "ready_to_commit",
  messages: [{ role: "assistant", content: "Review every field before committing." }],
  created_at: "2026-09-11T12:00:00Z",
  updated_at: "2026-09-11T12:00:00Z",
};

function renderWorkspace(draft: DraftResponse): void {
  const preloadedState: { complaints: ComplaintState } = {
    complaints: {
      activeDraft: draft,
      messages: draft.messages,
      ledger: [],
      requestStatus: "idle",
      error: null,
      hasUnsavedEdits: false,
    },
  };
  const store = configureStore({ reducer: { complaints: complaintReducer }, preloadedState });
  render(
    <Provider store={store}>
      <ComplaintWorkspace />
    </Provider>,
  );
}

describe("complaint workspace", () => {
  it("populates editable fields and labels AI recommendations", () => {
    renderWorkspace(readyDraft);

    expect(screen.getByDisplayValue("AMX240602")).toBeInTheDocument();
    expect(screen.getByText("AI-suggested severity")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /commit to qms ledger/i })).toBeEnabled();
  });

  it("disables commit while required fields are missing", () => {
    renderWorkspace({
      ...readyDraft,
      status: "needs_review",
      fields: { ...readyDraft.fields, batch_lot_number: null },
      completeness: {
        is_complete: false,
        missing_fields: ["batch_lot_number"],
        uncertain_fields: [],
      },
    });

    expect(screen.getByRole("button", { name: /commit to qms ledger/i })).toBeDisabled();
    expect(screen.getByText("Missing: batch / lot number")).toBeInTheDocument();
  });

  it("blocks commit after a direct edit until form changes are applied", async () => {
    const user = userEvent.setup();
    renderWorkspace(readyDraft);

    await user.clear(screen.getByLabelText("Affected quantity"));
    await user.type(screen.getByLabelText("Affected quantity"), "52 capsules");

    expect(screen.getByRole("button", { name: /apply form edits/i })).toBeEnabled();
    expect(screen.getByRole("button", { name: /commit to qms ledger/i })).toBeDisabled();
    expect(screen.getByText(/form edits are not yet saved/i)).toBeInTheDocument();
  });
});
