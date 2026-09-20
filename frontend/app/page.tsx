import Link from "next/link";
import { fetchToday } from "@/lib/api";
import type { Signal } from "@/lib/types";

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
      <p className="channel-hint">Allowed channel: {channelLabel(signal.channel_hint)}</p>
      <Link className="view-link" href={`/relationship/${signal.entity_id}`}>
        View relationship
      </Link>
    </li>
  );
}

export default async function TodayPage() {
  let signals: Signal[] = [];
  let error: string | null = null;

  try {
    const data = await fetchToday();
    signals = data.signals;
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
        </>
      )}
    </main>
  );
}
