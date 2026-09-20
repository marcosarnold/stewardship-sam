"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { fetchAllCommunityMetrics, fetchCommunities } from "@/lib/api";
import type { Community, CommunityMetrics } from "@/lib/types";

type Row = Community & { metrics: CommunityMetrics | null };

type SortKey =
  | "member_count"
  | "historical_giving_rate"
  | "recent_giving_rate"
  | "recent_to_historical_ratio"
  | "recent_interaction_rate"
  | "historical_event_participation"
  | "recent_event_participation"
  | "stewardship_coverage"
  | "assignment_coverage";

const COLUMNS: { key: SortKey; label: string }[] = [
  { key: "member_count", label: "Members" },
  { key: "historical_giving_rate", label: "Ever gave" },
  { key: "recent_giving_rate", label: "Recent giving" },
  { key: "recent_to_historical_ratio", label: "Recent/historical" },
  { key: "recent_interaction_rate", label: "Recent interaction" },
  { key: "historical_event_participation", label: "Ever attended*" },
  { key: "recent_event_participation", label: "Recent attendance*" },
  { key: "stewardship_coverage", label: "Stewardship coverage" },
  { key: "assignment_coverage", label: "Assignment coverage" },
];

function pct(value: number | null | undefined): string {
  return value === null || value === undefined ? "Not on file" : `${Math.round(value * 1000) / 10}%`;
}

function sortValue(row: Row, key: SortKey): number {
  if (key === "member_count") return row.member_count;
  const value = row.metrics?.[key];
  return value === null || value === undefined ? -1 : value;
}

export default function CommunitiesPage() {
  const [rows, setRows] = useState<Row[] | null>(null);
  const [sortKey, setSortKey] = useState<SortKey>("member_count");
  const [sortDesc, setSortDesc] = useState(true);
  const [eventCaveat, setEventCaveat] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    Promise.all([fetchCommunities(), fetchAllCommunityMetrics()])
      .then(([communities, allMetrics]) => {
        const eligible = communities.filter((c) => c.eligible);
        setRows(eligible.map((c) => ({ ...c, metrics: allMetrics[c.id] ?? null })));
        const first = Object.values(allMetrics)[0];
        setEventCaveat(first?.event_data_caveat ?? null);
      })
      .catch(() => setError("Could not reach the Stewardship Sam API. Is the backend running?"));
  }, []);

  function toggleSort(key: SortKey) {
    if (key === sortKey) {
      setSortDesc(!sortDesc);
    } else {
      setSortKey(key);
      setSortDesc(true);
    }
  }

  const sortedRows = rows
    ? [...rows].sort((a, b) => (sortValue(a, sortKey) - sortValue(b, sortKey)) * (sortDesc ? -1 : 1))
    : null;

  return (
    <main>
      <p>
        <Link href="/">&larr; Back to Today</Link>
      </p>

      <header className="today-header">
        <h1>Communities</h1>
        <p>
          An edge is shared institutional context, such as a common activity -- not a direct social
          relationship or friendship.
        </p>
      </header>

      {error ? (
        <p className="error-state">{error}</p>
      ) : sortedRows === null ? (
        <p className="empty-state">Loading&hellip;</p>
      ) : sortedRows.length === 0 ? (
        <p className="empty-state">No eligible communities found.</p>
      ) : (
        <div className="timeline-list" style={{ overflowX: "auto" }}>
          <table className="metrics-table">
            <thead>
              <tr>
                <th>Community</th>
                {COLUMNS.map((col) => (
                  <th key={col.key}>
                    <button type="button" className="timeline-filter-button" onClick={() => toggleSort(col.key)}>
                      {col.label}
                      {sortKey === col.key ? (sortDesc ? " ↓" : " ↑") : ""}
                    </button>
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {sortedRows.map((row) => (
                <tr key={row.id}>
                  <td>
                    <Link href={`/communities/${row.id}`}>{row.name}</Link>
                  </td>
                  <td>{row.member_count}</td>
                  <td>{pct(row.metrics?.historical_giving_rate)}</td>
                  <td>{pct(row.metrics?.recent_giving_rate)}</td>
                  <td>{pct(row.metrics?.recent_to_historical_ratio)}</td>
                  <td>{pct(row.metrics?.recent_interaction_rate)}</td>
                  <td>{pct(row.metrics?.historical_event_participation)}</td>
                  <td>{pct(row.metrics?.recent_event_participation)}</td>
                  <td>{pct(row.metrics?.stewardship_coverage)}</td>
                  <td>{pct(row.metrics?.assignment_coverage)}</td>
                </tr>
              ))}
            </tbody>
          </table>
          {eventCaveat && <p className="held-back-caveat">* {eventCaveat}</p>}
        </div>
      )}
    </main>
  );
}
