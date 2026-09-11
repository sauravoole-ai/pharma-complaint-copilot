import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import type { ComplaintResponse } from "../types/complaint";
import { ComplaintLedger } from "./ComplaintLedger";

const committedComplaint: ComplaintResponse = {
  id: "00000000-0000-0000-0000-000000000010",
  source_draft_id: "00000000-0000-0000-0000-000000000001",
  fields: {
    complaint_source: "Email",
    customer_name: "Northstar Pharmacy",
    product_type: "Capsule",
    product_name: "Amoxicillin",
    product_strength: "500 mg",
    batch_lot_number: "BMX240602",
    affected_quantity: "48 capsules",
    manufacturing_date: null,
    expiry_date: null,
    originating_site_block: null,
    impacted_non_product_materials: null,
    complaint_category: "Product quality",
    complaint_description: "Capsules appeared discolored.",
    customer_requested_action: "Replacement and investigation",
  },
  risk: {
    severity: "Major",
    next_action: "Quarantine and investigate.",
    rationale: "Potential product quality defect.",
  },
  summary: "A pharmacy reported discolored amoxicillin capsules.",
  created_at: "2026-09-11T12:00:00Z",
};

describe("complaint ledger", () => {
  it("shows one human-confirmed committed record", () => {
    render(<ComplaintLedger complaints={[committedComplaint]} loading={false} />);

    expect(screen.getAllByTestId("ledger-row")).toHaveLength(1);
    expect(screen.getByText("BMX240602")).toBeInTheDocument();
    expect(screen.getByText("Human-confirmed record")).toBeInTheDocument();
  });

  it("shows an honest empty state", () => {
    render(<ComplaintLedger complaints={[]} loading={false} />);

    expect(screen.getByText(/no complaints have been committed/i)).toBeInTheDocument();
  });
});
