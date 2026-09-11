import { useState, type FormEvent } from "react";

import type { CopilotMessage, RiskSuggestion } from "../types/complaint";

export function CopilotPanel({
  messages,
  risk,
  summary,
  disabled,
  onCorrection,
}: {
  messages: CopilotMessage[];
  risk: RiskSuggestion;
  summary: string;
  disabled: boolean;
  onCorrection: (message: string) => void;
}) {
  const [message, setMessage] = useState("");

  function submit(event: FormEvent) {
    event.preventDefault();
    const value = message.trim();
    if (!value) return;
    onCorrection(value);
    setMessage("");
  }

  return (
    <aside className="copilot-panel" aria-label="Complaint copilot">
      <div className="copilot-heading">
        <div className="copilot-mark" aria-hidden="true">✦</div>
        <div>
          <span>Analysis assistant</span>
          <h2>Complaint Copilot</h2>
        </div>
      </div>

      <div className="copilot-scroll">
        <section className="summary-card">
          <p className="eyebrow">AI-generated summary</p>
          <p>{summary}</p>
        </section>

        <section className="risk-card">
          <div className="risk-heading">
            <p className="eyebrow">AI-suggested severity</p>
            <span className={`severity severity--${risk.severity.toLowerCase()}`}>
              {risk.severity}
            </span>
          </div>
          <h3>Recommended next action</h3>
          <p>{risk.next_action}</p>
          <details>
            <summary>Why this was suggested</summary>
            <p>{risk.rationale}</p>
          </details>
          <p className="disclaimer">Human review required before any quality decision.</p>
        </section>

        <div className="conversation" aria-live="polite">
          {messages.map((item, index) => (
            <div className={`message message--${item.role}`} key={`${item.role}-${index}`}>
              <span>{item.role === "user" ? "You" : "Copilot"}</span>
              <p>{item.content}</p>
            </div>
          ))}
        </div>
      </div>

      <form className="correction-box" onSubmit={submit}>
        <label htmlFor="correction-message">Correct the extracted details</label>
        <div>
          <input
            id="correction-message"
            value={message}
            disabled={disabled}
            placeholder="e.g. Change the batch to BMX240602"
            onChange={(event) => setMessage(event.target.value)}
          />
          <button type="submit" disabled={disabled || !message.trim()} aria-label="Send correction">
            <span aria-hidden="true">↑</span>
          </button>
        </div>
      </form>
    </aside>
  );
}
