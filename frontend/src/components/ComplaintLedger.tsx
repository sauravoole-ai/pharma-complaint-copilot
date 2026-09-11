import type { ComplaintResponse } from "../types/complaint";

export function ComplaintLedger({
  complaints,
  loading,
}: {
  complaints: ComplaintResponse[];
  loading: boolean;
}) {
  return (
    <section className="ledger-section" id="ledger" aria-busy={loading}>
      <div className="ledger-heading">
        <div>
          <p className="kicker">Committed records</p>
          <h2>QMS complaint ledger</h2>
        </div>
        <p>
          Prototype records confirmed by a reviewer. This view does not represent an electronic
          signature or validated QMS.
        </p>
      </div>

      {complaints.length === 0 ? (
        <div className="ledger-empty">
          <span aria-hidden="true">◇</span>
          <div>
            <h3>{loading ? "Loading committed records…" : "No complaints have been committed"}</h3>
            <p>Reviewed complaints will appear here after an explicit commit.</p>
          </div>
        </div>
      ) : (
        <div className="ledger-table-wrap">
          <table className="ledger-table">
            <thead>
              <tr>
                <th scope="col">Record</th>
                <th scope="col">Customer</th>
                <th scope="col">Product</th>
                <th scope="col">Batch / lot</th>
                <th scope="col">Suggested severity</th>
                <th scope="col">Committed</th>
              </tr>
            </thead>
            <tbody>
              {complaints.map((complaint) => (
                <tr key={complaint.id} data-testid="ledger-row">
                  <td data-label="Record">
                    <strong>QMS-{complaint.id.slice(0, 8).toUpperCase()}</strong>
                    <span>Human-confirmed record</span>
                  </td>
                  <td data-label="Customer">{complaint.fields.customer_name ?? "—"}</td>
                  <td data-label="Product">
                    {complaint.fields.product_name ?? "—"}
                    {complaint.fields.product_strength && (
                      <span>{complaint.fields.product_strength}</span>
                    )}
                  </td>
                  <td data-label="Batch / lot">{complaint.fields.batch_lot_number ?? "—"}</td>
                  <td data-label="Suggested severity">
                    <span className={`severity severity--${complaint.risk.severity.toLowerCase()}`}>
                      {complaint.risk.severity}
                    </span>
                  </td>
                  <td data-label="Committed">{formatDate(complaint.created_at)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}

function formatDate(value: string): string {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "Unknown";
  return new Intl.DateTimeFormat(undefined, {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(date);
}
