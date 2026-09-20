import Link from "next/link";
import { fetchToday } from "@/lib/api";
import type { HeldBack, Signal } from "@/lib/types";

const REASON_LABELS: Record<string, string> = {
  recent_contact: "Recent contact already suppresses this",
  scheduled_follow_up: "Another interaction is already scheduled",
  do_not_call: "Phone is marked do-not-call",
  do_not_email: "Email is marked do-not-email",
  phone_unavailable: "Phone is unavailable",
  email_unavailable: "Email is unavailable",
  text_unsupported: "Text is not supported",
  do_not_solicit: "Do-not-solicit restriction",
  deceased: "Recorded as deceased",
  contact_pressure: "Recent contact pressure",
};

function reasonLabel(reasonCode: string): string {
  return REASON_LABELS[reasonCode] ?? reasonCode;
}

function channelLabel(channelHint: string | null): string {
  return channelHint ?? "Not on file";
}

function QueueItem({ signal }: { signal: Signal }) {
  return (
    <li className="queue-item">
      <div className="queue-item-header">
        <span className="entity-name">{signal.entity_name}</span>
        <span className="action-pill">{signal.action}</span>
      </div>
      <ul className="evidence-list">
        {signal.evidence.map((line) => (
          <li key={line}>{line}</li>
        ))}
      </ul>
      {signal.action !== "WAIT" && (
        <p className="channel-hint">Allowed channel: {channelLabel(signal.channel_hint)}</p>
      )}
      <Link className="view-link" href={`/relationship/${signal.entity_id}`}>
        View relationship
      </Link>
    </li>
  );
}

function HeldBackSection({ heldBack }: { heldBack: HeldBack }) {
  if (heldBack.items.length === 0) {
    return null;
  }

  return (
    <details className="held-back">
      <summary>
        Held back today ({heldBack.items.length})
        <span className="held-back-reasons">
          {heldBack.reasons
            .map((r) => `${reasonLabel(r.reason_code)}: ${r.count}`)
            .join(" · ")}
        </span>
      </summary>
      <p className="held-back-caveat">
        Contact-restriction flags are a current snapshot, so some past outreach may appear to
        conflict with them. That is a data caveat, not evidence of a violation.
      </p>
      <ul className="held-back-list">
        {heldBack.items.map((item) => (
          <li key={`${item.entity_id}-${item.reason_code}`}>
            <Link href={`/relationship/${item.entity_id}`}>{item.entity_name}</Link>
            <span className="held-back-reason"> &mdash; {item.reason}</span>
          </li>
        ))}
      </ul>
    </details>
  );
}

export default async function TodayPage() {
  let signals: Signal[] = [];
  let heldBack: HeldBack = { reasons: [], items: [] };
  let error: string | null = null;

  try {
    const data = await fetchToday();
    signals = data.signals;
    heldBack = data.held_back;
  } catch {
    error = "Could not reach the Stewardship Sam API. Is the backend running?";
  }

  return (
    <main>
      <div className="today-header">
        <h1>Stewardship Sam</h1>
        <p>Where should I spend Tuesday?</p>
      </div>

      {error && <p className="error-state">{error}</p>}

      {!error && (
        <>
          <p className="queue-summary">
            {signals.length} relationship{signals.length === 1 ? "" : "s"} need attention today.
          </p>
          {signals.length === 0 ? (
            <p className="empty-state">Nothing needs attention right now.</p>
          ) : (
            <ul className="queue">
              {signals.map((signal) => (
                <QueueItem key={`${signal.signal_id}-${signal.entity_id}`} signal={signal} />
              ))}
            </ul>
          )}

          <HeldBackSection heldBack={heldBack} />
        </>
      )}
    </main>
  );
}
