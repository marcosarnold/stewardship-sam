"use client";

import { useEffect, useState } from "react";
import { confirmAction, fetchActionBrief } from "@/lib/api";
import type { ActionBrief } from "@/lib/types";

export default function PrepareAction({ entityId }: { entityId: number }) {
  const [brief, setBrief] = useState<ActionBrief | null>(null);
  const [note, setNote] = useState("");
  const [status, setStatus] = useState<string | null>(null);

  function load() {
    fetchActionBrief(entityId).then(setBrief);
  }

  useEffect(load, [entityId]);

  if (!brief) return <p className="empty-state">Loading&hellip;</p>;

  if (!brief.action) {
    return <p className="empty-state">No action is currently recommended for this person.</p>;
  }

  async function handleConfirm(outcome: "done" | "not_now" | "dismissed") {
    await confirmAction(entityId, brief!.action, outcome, note || null);
    setStatus(`Recorded: ${outcome === "done" ? "I'll do this" : outcome === "not_now" ? "Not now" : "Dismissed"}`);
    setNote("");
    load();
  }

  return (
    <div className="action-brief">
      <p className="relationship-subline">
        <span className="action-pill">{brief.action}</span>{" "}
        {brief.channel_hint ? `via ${brief.channel_hint}` : "no allowed channel"}
      </p>
      <p className="relationship-subline">Assigned to: {brief.assigned_officer ?? "Not on file"}</p>

      <ul className="evidence-list">
        {brief.evidence.map((line) => (
          <li key={line}>{line}</li>
        ))}
      </ul>

      <p>
        <strong>Talking points</strong>
      </p>
      <ul className="evidence-list">
        {brief.talking_points.map((point) => (
          <li key={point}>{point}</li>
        ))}
      </ul>

      <textarea
        className="ask-sam-input"
        style={{ width: "100%", marginTop: "0.5rem" }}
        placeholder="Optional note"
        value={note}
        onChange={(e) => setNote(e.target.value)}
      />

      <div className="queue-item-actions">
        <button type="button" className="show-all-button" onClick={() => handleConfirm("done")}>
          I&apos;ll do this
        </button>
        <button type="button" className="show-all-button" onClick={() => handleConfirm("not_now")}>
          Not now
        </button>
        <button type="button" className="dismiss-button" onClick={() => handleConfirm("dismissed")}>
          Dismiss
        </button>
      </div>

      {status && <p className="held-back-caveat">{status}</p>}
      {brief.last_outcome && (
        <p className="held-back-caveat">
          Last recorded: {brief.last_outcome.outcome} on {brief.last_outcome.recorded_at.slice(0, 10)}
          {brief.last_outcome.note ? ` — ${brief.last_outcome.note}` : ""}
        </p>
      )}
    </div>
  );
}
