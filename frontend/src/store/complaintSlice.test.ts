import { describe, expect, it } from "vitest";

import type { DraftResponse } from "../types/complaint";
import reducer, {
  analyzeText,
  commitComplaint,
  initialState,
} from "./complaintSlice";

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
  completeness: {
    is_complete: true,
    missing_fields: [],
    uncertain_fields: [],
  },
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

describe("complaint workflow reducer", () => {
  it("moves an analyzed draft into ready_to_commit", () => {
    const state = reducer(
      initialState,
      analyzeText.fulfilled(readyDraft, "r1", "sample complaint"),
    );

    expect(state.activeDraft?.status).toBe("ready_to_commit");
    expect(state.messages).toEqual(readyDraft.messages);
    expect(state.error).toBeNull();
  });

  it("preserves the draft when commit fails", () => {
    const stateWithReadyDraft = { ...initialState, activeDraft: readyDraft };
    const payload = { draftId: readyDraft.id, commitToken: "token-1" };

    const state = reducer(
      stateWithReadyDraft,
      commitComplaint.rejected(new Error("network unavailable"), "r2", payload),
    );

    expect(state.activeDraft?.id).toBe(readyDraft.id);
    expect(state.requestStatus).toBe("failed");
    expect(state.error).toContain("network unavailable");
  });
});
