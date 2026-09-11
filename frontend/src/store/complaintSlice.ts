import { createAsyncThunk, createSlice, isAnyOf } from "@reduxjs/toolkit";

import * as api from "../api/client";
import type {
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
}

export const initialState: ComplaintState = {
  activeDraft: null,
  messages: [],
  ledger: [],
  requestStatus: "idle",
  error: null,
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
  commitComplaint.pending,
  loadLedger.pending,
] as const;

const rejectedActions = [
  analyzeText.rejected,
  analyzeFile.rejected,
  sendCorrection.rejected,
  commitComplaint.rejected,
  loadLedger.rejected,
] as const;

const complaintSlice = createSlice({
  name: "complaints",
  initialState,
  reducers: {},
  extraReducers: (builder) => {
    builder
      .addCase(analyzeText.fulfilled, setDraft)
      .addCase(analyzeFile.fulfilled, setDraft)
      .addCase(sendCorrection.fulfilled, setDraft)
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
}

export const selectActiveDraft = (state: { complaints: ComplaintState }) =>
  state.complaints.activeDraft;
export const selectMessages = (state: { complaints: ComplaintState }) =>
  state.complaints.messages;
export const selectLedger = (state: { complaints: ComplaintState }) =>
  state.complaints.ledger;
export const selectRequestStatus = (state: { complaints: ComplaintState }) =>
  state.complaints.requestStatus;
export const selectError = (state: { complaints: ComplaintState }) => state.complaints.error;

export default complaintSlice.reducer;
