import type { CompletenessResult, DraftStatus } from "../types/complaint";

const labels: Record<DraftStatus, string> = {
  idle: "Waiting for complaint",
  processing: "Analyzing complaint",
  needs_review: "Review required",
  ready_to_commit: "Ready for human approval",
  committing: "Committing record",
  committed: "Committed to ledger",
  failed: "Action failed",
};

export function WorkflowStatus({
  status,
  completeness,
}: {
  status: DraftStatus;
  completeness: CompletenessResult;
}) {
  return (
    <div className={`workflow-status workflow-status--${status}`} aria-live="polite">
      <span className="status-dot" aria-hidden="true" />
      <div>
        <strong>{labels[status]}</strong>
        {!completeness.is_complete && (
          <p>
            Missing: {completeness.missing_fields.map(prettyField).join(", ")}
          </p>
        )}
      </div>
    </div>
  );
}

function prettyField(field: string): string {
  if (field === "batch_lot_number") return "batch / lot number";
  return field.replaceAll("_", " ");
}
