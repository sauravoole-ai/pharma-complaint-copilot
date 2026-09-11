export type DraftStatus =
  | "idle"
  | "processing"
  | "needs_review"
  | "ready_to_commit"
  | "committing"
  | "committed"
  | "failed";

export type SourceType = "text" | "pdf";
export type Severity = "Minor" | "Major" | "Critical";
export type MessageRole = "user" | "assistant" | "system";

export interface ComplaintFields {
  complaint_source: string | null;
  customer_name: string | null;
  product_type: string | null;
  product_name: string | null;
  product_strength: string | null;
  batch_lot_number: string | null;
  affected_quantity: string | null;
  manufacturing_date: string | null;
  expiry_date: string | null;
  originating_site_block: string | null;
  impacted_non_product_materials: string | null;
  complaint_category: string | null;
  complaint_description: string | null;
  customer_requested_action: string | null;
}

export interface CompletenessResult {
  is_complete: boolean;
  missing_fields: string[];
  uncertain_fields: string[];
}

export interface RiskSuggestion {
  severity: Severity;
  next_action: string;
  rationale: string;
}

export interface CopilotMessage {
  role: MessageRole;
  content: string;
}

export interface DraftResponse {
  id: string;
  source_type: SourceType;
  fields: ComplaintFields;
  completeness: CompletenessResult;
  risk: RiskSuggestion;
  summary: string;
  status: DraftStatus;
  messages: CopilotMessage[];
  created_at: string;
  updated_at: string;
}

export interface ComplaintResponse {
  id: string;
  source_draft_id: string;
  fields: ComplaintFields;
  risk: RiskSuggestion;
  summary: string;
  created_at: string;
}
