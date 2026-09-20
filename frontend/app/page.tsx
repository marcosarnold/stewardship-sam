"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { dismissToday, fetchToday, restoreToday } from "@/lib/api";
import type { HeldBack, QueueItem as QueueItemType, TodayResponse } from "@/lib/types";

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

const ACTION_GROUP_LABELS: Record<string, string> = {
  "FOLLOW UP": "Follow-ups",
  THANK: "Stewardship",
  WAIT: "Restraint",
  RECONNECT: "Reconnect",
  ASSIGN: "Assign",
};

function reasonLabel(reasonCode: string): string {
  return REASON_LABELS[reasonCode] ?? reasonCode;
}

function channelLabel(channelHint: string | null): string {
  return channelHint ?? "Not on file";
}

function HeaderSummary({ counts, total }: { counts: Record<string, number>; total: number }) {
  const parts = Object.entries(counts)
    .filter(([, count]) => count > 0)
    .map(([action, count]) => `${count} ${ACTION_GROUP_LABELS[action] ?? action}`);

  return (
    <div className="today-header">
      <h1>Stewardship Sam</h1>
      <p>Where should I spend Tuesday?</p>
      <p className="queue-summary">
        {total} relationship{total === 1 ? "" : "s"} need attention today.
      </p>
      {parts.length > 0 && <p className="queue-summary">{parts.join(" | ")}</p>}
      <p className="queue-summary">
        <Link href="/communities">Communities</Link>
      </p>
    </div>
  );
}

function QueueItemCard({
  item,
  onDismiss,
}: {
  item: QueueItemType;
  onDismiss: (entityId: number | string) => void;
}) {
  const isCommunity = item.entity_type === "community";
  return (
    <li className={`queue-item${isCommunity ? " queue-item-community" : ""}`}>
      <div className="queue-item-header">
        <span className="entity-name">
          {isCommunity && <span className="community-badge">Community</span>}
          {item.entity_name}
        </span>
        <span className="action-pill">{item.action}</span>
      </div>
      <p className="ranking-factor">{item.ranking_factor}</p>
      <ul className="evidence-list">
        {item.evidence.map((line) => (
          <li key={line}>{line}</li>
        ))}
      </ul>
      {!isCommunity && item.action !== "WAIT" && (
        <p className="channel-hint">Allowed channel: {channelLabel(item.channel_hint)}</p>
      )}
      {item.supporting_signals.length > 0 && (
        <div className="supporting-signals">
          {item.supporting_signals.map((s) => (
            <p key={s.action} className="supporting-signal">
              Also: <span className="action-pill action-pill-small">{s.action}</span>{" "}
              {s.evidence.join("; ")}
            </p>
          ))}
        </div>
      )}
      <div className="queue-item-actions">
        <Link className="view-link" href={isCommunity ? `/community/${item.entity_id}` : `/relationship/${item.entity_id}`}>
          {isCommunity ? "Explore community" : "View relationship"}
        </Link>
        <button className="dismiss-button" onClick={() => onDismiss(item.entity_id)}>
          Dismiss
        </button>
      </div>
    </li>
  );
}

function DismissedSection({
  items,
  onRestore,
}: {
  items: QueueItemType[];
  onRestore: (entityId: number | string) => void;
}) {
  if (items.length === 0) {
    return null;
  }

  return (
    <details className="held-back">
      <summary>Dismissed ({items.length})</summary>
      <ul className="held-back-list">
        {items.map((item) => (
          <li key={item.entity_id}>
            <Link href={item.entity_type === "community" ? `/community/${item.entity_id}` : `/relationship/${item.entity_id}`}>
              {item.entity_name}
            </Link>
            <span className="held-back-reason">
              {" "}
              &mdash; {item.dismiss_reason ?? "no reason given"}
            </span>
            <button className="restore-button" onClick={() => onRestore(item.entity_id)}>
              Undo
            </button>
          </li>
        ))}
      </ul>
    </details>
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
          {heldBack.reasons.map((r) => `${reasonLabel(r.reason_code)}: ${r.count}`).join(" · ")}
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

export default function TodayPage() {
  const [data, setData] = useState<TodayResponse | null>(null);
  const [showAll, setShowAll] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const load = (nextShowAll: boolean) => {
    fetchToday(nextShowAll)
      .then((response) => {
        setData(response);
        setError(null);
      })
      .catch(() => {
        setError("Could not reach the Stewardship Sam API. Is the backend running?");
      });
  };

  useEffect(() => {
    load(showAll);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [showAll]);

  const handleDismiss = (entityId: number | string) => {
    dismissToday(entityId, null).then(() => load(showAll));
  };

  const handleRestore = (entityId: number | string) => {
    restoreToday(entityId).then(() => load(showAll));
  };

  if (error) {
    return (
      <main>
        <div className="today-header">
          <h1>Stewardship Sam</h1>
          <p>Where should I spend Tuesday?</p>
        </div>
        <p className="error-state">{error}</p>
      </main>
    );
  }

  if (data === null) {
    return (
      <main>
        <div className="today-header">
          <h1>Stewardship Sam</h1>
          <p>Where should I spend Tuesday?</p>
        </div>
        <p className="empty-state">Loading&hellip;</p>
      </main>
    );
  }

  return (
    <main>
      <HeaderSummary counts={data.counts} total={data.total_count} />

      {data.signals.length === 0 ? (
        <p className="empty-state">Nothing needs attention right now.</p>
      ) : (
        <ul className="queue">
          {data.signals.map((item) => (
            <QueueItemCard key={item.entity_id} item={item} onDismiss={handleDismiss} />
          ))}
        </ul>
      )}

      {!showAll && data.total_count > data.signals.length && (
        <button className="show-all-button" onClick={() => setShowAll(true)}>
          Show all {data.total_count}
        </button>
      )}
      {showAll && (
        <button className="show-all-button" onClick={() => setShowAll(false)}>
          Show fewer
        </button>
      )}

      <DismissedSection items={data.dismissed} onRestore={handleRestore} />
      <HeldBackSection heldBack={data.held_back} />
    </main>
  );
}
