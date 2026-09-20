"use client";

import { useEffect, useState } from "react";
import { fetchTimeline } from "@/lib/api";
import type { TimelineEntry, TimelineEntryType } from "@/lib/types";

const TYPE_LABELS: Record<TimelineEntryType, string> = {
  gift: "Gifts",
  interaction: "Interactions",
  event: "Events attended",
  career_change: "Career changes",
  opportunity: "Opportunities",
};

const ALL_TYPES = Object.keys(TYPE_LABELS) as TimelineEntryType[];

const NOTE_TRUNCATE_LENGTH = 160;

function emptyMessage(type: TimelineEntryType): string {
  return type === "interaction" ? "No interactions are recorded" : "None recorded";
}

function EntryDetail({ type, detail }: { type: TimelineEntryType; detail: string | null }) {
  const [expanded, setExpanded] = useState(false);
  if (!detail) return null;

  // Only interaction notes get plain-data + expand treatment (UX2); other
  // types' detail strings are already short, formatted facts.
  if (type !== "interaction" || detail.length <= NOTE_TRUNCATE_LENGTH) {
    return <p className="timeline-entry-detail">{detail}</p>;
  }

  return (
    <p className="timeline-entry-detail">
      {expanded ? detail : `${detail.slice(0, NOTE_TRUNCATE_LENGTH)}…`}{" "}
      <button type="button" className="timeline-expand-button" onClick={() => setExpanded(!expanded)}>
        {expanded ? "Show less" : "Show more"}
      </button>
    </p>
  );
}

function TimelineRow({ entry }: { entry: TimelineEntry }) {
  return (
    <li className="timeline-entry">
      <div className="timeline-entry-header">
        <span className="timeline-entry-date">{entry.date}</span>
        <span className="timeline-entry-type">{TYPE_LABELS[entry.type]}</span>
        {entry.significant && <span className="action-pill action-pill-small">Significant</span>}
      </div>
      <p className="timeline-entry-headline">{entry.headline}</p>
      <EntryDetail type={entry.type} detail={entry.detail} />
    </li>
  );
}

export default function Timeline({ entityId }: { entityId: number }) {
  const [activeTypes, setActiveTypes] = useState<TimelineEntryType[]>(ALL_TYPES);
  const [page, setPage] = useState(1);
  const [entries, setEntries] = useState<TimelineEntry[]>([]);
  const [counts, setCounts] = useState<Record<TimelineEntryType, number> | null>(null);
  const [hasMore, setHasMore] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError(false);
    fetchTimeline(entityId, { types: activeTypes, page })
      .then((timeline) => {
        if (cancelled) return;
        setEntries(timeline.entries);
        setCounts(timeline.counts);
        setHasMore(timeline.has_more);
      })
      .catch(() => {
        if (!cancelled) setError(true);
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [entityId, activeTypes, page]);

  function toggleType(type: TimelineEntryType) {
    setPage(1);
    setActiveTypes((current) =>
      current.includes(type) ? current.filter((t) => t !== type) : [...current, type]
    );
  }

  const singleFilteredType = activeTypes.length === 1 ? activeTypes[0] : null;

  return (
    <div>
      <div className="timeline-filters">
        {ALL_TYPES.map((type) => (
          <button
            key={type}
            type="button"
            className={`timeline-filter-button${activeTypes.includes(type) ? " timeline-filter-active" : ""}`}
            onClick={() => toggleType(type)}
          >
            {TYPE_LABELS[type]}
            {counts !== null && ` (${counts[type]})`}
          </button>
        ))}
      </div>

      {error && <p className="error-state">The timeline could not be loaded.</p>}

      {!error && loading && entries.length === 0 && <p className="empty-state">Loading…</p>}

      {!error && !loading && entries.length === 0 && (
        <p className="empty-state">
          {singleFilteredType ? emptyMessage(singleFilteredType) : "No timeline entries are recorded."}
        </p>
      )}

      {entries.length > 0 && (
        <ul className="timeline-list">
          {entries.map((entry, index) => (
            <TimelineRow key={`${entry.type}-${entry.date}-${index}`} entry={entry} />
          ))}
        </ul>
      )}

      <div className="timeline-pagination">
        {page > 1 && (
          <button type="button" className="show-all-button" onClick={() => setPage((p) => p - 1)}>
            Newer
          </button>
        )}
        {hasMore && (
          <button type="button" className="show-all-button" onClick={() => setPage((p) => p + 1)}>
            Older
          </button>
        )}
      </div>
    </div>
  );
}
