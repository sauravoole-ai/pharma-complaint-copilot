import { z } from "zod";

import type { ComplaintResponse, DraftResponse } from "../types/complaint";

const fieldsSchema = z
  .object({
    complaint_source: z.string().nullable(),
    customer_name: z.string().nullable(),
    product_type: z.string().nullable(),
    product_name: z.string().nullable(),
    product_strength: z.string().nullable(),
    batch_lot_number: z.string().nullable(),
    affected_quantity: z.string().nullable(),
    manufacturing_date: z.string().nullable(),
    expiry_date: z.string().nullable(),
    originating_site_block: z.string().nullable(),
    impacted_non_product_materials: z.string().nullable(),
    complaint_category: z.string().nullable(),
    complaint_description: z.string().nullable(),
    customer_requested_action: z.string().nullable(),
  })
  .strict();

const riskSchema = z
  .object({
    severity: z.enum(["Minor", "Major", "Critical"]),
    next_action: z.string(),
    rationale: z.string(),
  })
  .strict();

const draftSchema: z.ZodType<DraftResponse> = z
  .object({
    id: z.uuid(),
    source_type: z.enum(["text", "pdf"]),
    fields: fieldsSchema,
    completeness: z
      .object({
        is_complete: z.boolean(),
        missing_fields: z.array(z.string()),
        uncertain_fields: z.array(z.string()),
      })
      .strict(),
    risk: riskSchema,
    summary: z.string(),
    status: z.enum([
      "idle",
      "processing",
      "needs_review",
      "ready_to_commit",
      "committing",
      "committed",
      "failed",
    ]),
    messages: z.array(
      z
        .object({
          role: z.enum(["user", "assistant", "system"]),
          content: z.string(),
        })
        .strict(),
    ),
    created_at: z.string(),
    updated_at: z.string(),
  })
  .strict();

const complaintSchema: z.ZodType<ComplaintResponse> = z
  .object({
    id: z.uuid(),
    source_draft_id: z.uuid(),
    fields: fieldsSchema,
    risk: riskSchema,
    summary: z.string(),
    created_at: z.string(),
  })
  .strict();

const errorSchema = z.object({ message: z.string() }).passthrough();
const apiBase = (import.meta.env.VITE_API_BASE_URL ?? "").replace(/\/$/, "");

export class ApiClientError extends Error {}

async function request<T>(
  path: string,
  schema: z.ZodType<T>,
  init?: RequestInit,
): Promise<T> {
  const response = await fetch(`${apiBase}${path}`, init);
  const body: unknown = await response.json().catch(() => null);
  if (!response.ok) {
    const parsed = errorSchema.safeParse(body);
    throw new ApiClientError(
      parsed.success ? parsed.data.message : `Request failed with status ${response.status}`,
    );
  }
  const parsed = schema.safeParse(body);
  if (!parsed.success) {
    throw new ApiClientError("The server returned an invalid response");
  }
  return parsed.data;
}

const jsonHeaders = { "Content-Type": "application/json" };

export function analyzeText(text: string): Promise<DraftResponse> {
  return request("/api/v1/complaint-drafts/analyze-text", draftSchema, {
    method: "POST",
    headers: jsonHeaders,
    body: JSON.stringify({ text }),
  });
}

export function analyzeFile(file: File): Promise<DraftResponse> {
  const form = new FormData();
  form.append("file", file);
  return request("/api/v1/complaint-drafts/analyze-file", draftSchema, {
    method: "POST",
    body: form,
  });
}

export function sendCorrection(draftId: string, message: string): Promise<DraftResponse> {
  return request(`/api/v1/complaint-drafts/${draftId}/conversation`, draftSchema, {
    method: "PATCH",
    headers: jsonHeaders,
    body: JSON.stringify({ message }),
  });
}

export function commitComplaint(
  draftId: string,
  commitToken: string,
): Promise<ComplaintResponse> {
  return request("/api/v1/complaints", complaintSchema, {
    method: "POST",
    headers: jsonHeaders,
    body: JSON.stringify({ draft_id: draftId, commit_token: commitToken }),
  });
}

export function loadLedger(): Promise<ComplaintResponse[]> {
  return request("/api/v1/complaints", z.array(complaintSchema));
}
