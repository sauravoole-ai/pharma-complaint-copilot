import { createAsyncThunk, createSlice, isAnyOf } from "@reduxjs/toolkit";

import * as api from "../api/client";
import type {
  ComplaintFields,
  ComplaintResponse,
  CopilotMessage,
  DraftResponse,
} from "../types/complaint";

export type RequestStatus = "idle" | "loading" | "succeeded" | "failed";

export interface ComplaintState {
  activeDraft: DraftResponse | null;
  messages: CopilotMessage[];
  ledger: ComplaintResponse[];
  requestStatus: RequestStatus;
  error: string | null;
  hasUnsavedEdits: boolean;
}

export const initialState: ComplaintState = {
  activeDraft: null,
  messages: [],
  ledger: [],
  requestStatus: "idle",
  error: null,
  hasUnsavedEdits: false,
};

export const analyzeText = createAsyncThunk(
  "complaints/analyzeText",
  async (text: string) => api.analyzeText(text),
);

export const analyzeFile = createAsyncThunk(
  "complaints/analyzeFile",
  async (file: File) => api.analyzeFile(file),
);

export const sendCorrection = createAsyncThunk(
  "complaints/sendCorrection",
  async ({ draftId, message }: { draftId: string; message: string }) =>
    api.sendCorrection(draftId, message),
);

export const saveFields = createAsyncThunk(
  "complaints/saveFields",
  async ({ draftId, fields }: { draftId: string; fields: ComplaintFields }) =>
    api.updateFields(draftId, fields),
);

export const commitComplaint = createAsyncThunk(
  "complaints/commitComplaint",
  async ({ draftId, commitToken }: { draftId: string; commitToken: string }) =>
    api.commitComplaint(draftId, commitToken),
);

export const loadLedger = createAsyncThunk("complaints/loadLedger", api.loadLedger);

const pendingActions = [
  analyzeText.pending,
  analyzeFile.pending,
  sendCorrection.pending,
  saveFields.pending,
  commitComplaint.pending,
  loadLedger.pending,
] as const;

const rejectedActions = [
  analyzeText.rejected,
  analyzeFile.rejected,
  sendCorrection.rejected,
  saveFields.rejected,
  commitComplaint.rejected,
  loadLedger.rejected,
] as const;

const complaintSlice = createSlice({
  name: "complaints",
  initialState,
  reducers: {
    resetWorkflow: () => initialState,
    updateFieldLocally: (
      state,
      action: { payload: { field: keyof ComplaintFields; value: string } },
    ) => {
      if (!state.activeDraft) return;
      state.activeDraft.fields[action.payload.field] = action.payload.value;
      const required: (keyof ComplaintFields)[] = [
        "complaint_source",
        "customer_name",
        "product_name",
        "batch_lot_number",
        "complaint_category",
        "complaint_description",
      ];
      const missing = required.filter(
        (name) => !state.activeDraft?.fields[name]?.trim(),
      );
      state.activeDraft.completeness.is_complete = missing.length === 0;
      state.activeDraft.completeness.missing_fields = missing;
      state.activeDraft.status = missing.length === 0 ? "ready_to_commit" : "needs_review";
      state.hasUnsavedEdits = true;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(analyzeText.fulfilled, setDraft)
      .addCase(analyzeFile.fulfilled, setDraft)
      .addCase(sendCorrection.fulfilled, setDraft)
      .addCase(saveFields.fulfilled, setDraft)
      .addCase(commitComplaint.fulfilled, (state, action) => {
        state.requestStatus = "succeeded";
        state.error = null;
        if (state.activeDraft) state.activeDraft.status = "committed";
        if (!state.ledger.some((item) => item.id === action.payload.id)) {
          state.ledger.unshift(action.payload);
        }
      })
      .addCase(loadLedger.fulfilled, (state, action) => {
        state.ledger = action.payload;
        state.requestStatus = "succeeded";
        state.error = null;
      })
      .addMatcher(isAnyOf(...pendingActions), (state) => {
        state.requestStatus = "loading";
        state.error = null;
      })
      .addMatcher(isAnyOf(...rejectedActions), (state, action) => {
        state.requestStatus = "failed";
        state.error = action.error.message ?? "The request could not be completed";
      });
  },
});

function setDraft(
  state: ComplaintState,
  action: { payload: DraftResponse },
): void {
  state.activeDraft = action.payload;
  state.messages = action.payload.messages;
  state.requestStatus = "succeeded";
  state.error = null;
  state.hasUnsavedEdits = false;
}

export const { resetWorkflow, updateFieldLocally } = complaintSlice.actions;

export const selectActiveDraft = (state: { complaints: ComplaintState }) =>
  state.complaints.activeDraft;
export const selectMessages = (state: { complaints: ComplaintState }) =>
  state.complaints.messages;
export const selectLedger = (state: { complaints: ComplaintState }) =>
  state.complaints.ledger;
export const selectRequestStatus = (state: { complaints: ComplaintState }) =>
  state.complaints.requestStatus;
export const selectError = (state: { complaints: ComplaintState }) => state.complaints.error;
export const selectHasUnsavedEdits = (state: { complaints: ComplaintState }) =>
  state.complaints.hasUnsavedEdits;

export default complaintSlice.reducer;
