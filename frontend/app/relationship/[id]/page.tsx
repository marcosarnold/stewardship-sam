import Link from "next/link";
import { fetchRelationship } from "@/lib/api";
import type { RelationshipSignal } from "@/lib/types";

function notOnFile(value: string | number | null): string {
  return value === null || value === undefined ? "Not on file" : String(value);
}

function classAndDegree(classYear: number | null, degree: string | null): string {
  if (classYear === null && degree === null) return "Not on file";
  if (classYear !== null && degree !== null) return `Class of ${classYear}, ${degree}`;
  if (classYear !== null) return `Class of ${classYear}`;
  return degree as string;
}

function locationLabel(city: string | null, state: string | null): string {
  if (city && state) return `${city}, ${state}`;
  if (city) return city;
  if (state) return state;
  return "Not on file";
}

function SignalCard({ signal }: { signal: RelationshipSignal }) {
  const heldBack = signal.policy_status === "held_back";
  return (
    <li className={`signal-card${heldBack ? " signal-card-held-back" : ""}`}>
      <div className="signal-card-header">
        <span className="action-pill">{signal.action}</span>
        {heldBack && <span className="held-back-tag">Held back</span>}
      </div>
      <ul className="evidence-list">
        {signal.evidence.map((line) => (
          <li key={line}>{line}</li>
        ))}
      </ul>
      {heldBack ? (
        <p className="signal-policy-note">{signal.policy_reason}</p>
      ) : (
        <>
          {signal.channel_hint !== undefined && (
            <p className="channel-hint">Allowed channel: {notOnFile(signal.channel_hint ?? null)}</p>
          )}
          {signal.assigned_officer !== undefined && signal.assigned_officer !== null && (
            <p className="signal-policy-note">Assigned to {signal.assigned_officer}</p>
          )}
        </>
      )}
    </li>
  );
}

export default async function RelationshipPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const page = await fetchRelationship(id);

  if (page === null) {
    return (
      <main>
        <p>
          <Link href="/">&larr; Back to Today</Link>
        </p>
        <h1>No relationship record</h1>
        <p className="empty-state">
          Constituent {id} is unknown, not an individual, or recorded as deceased.
        </p>
      </main>
    );
  }

  return (
    <main>
      <p>
        <Link href="/">&larr; Back to Today</Link>
      </p>

      <header className="relationship-header">
        <h1>{page.entity_name}</h1>
        <p className="relationship-subline">{classAndDegree(page.class_year, page.degree)}</p>
        {page.activities.length > 0 && (
          <p className="relationship-subline">{page.activities.join(" · ")}</p>
        )}
        <p className="relationship-subline">{locationLabel(page.city, page.state)}</p>
        <p className="relationship-subline">Assigned to: {notOnFile(page.assigned_officer)}</p>
        <p className="relationship-recommendation">
          {page.recommended_action ? (
            <span className="action-pill">{page.recommended_action}</span>
          ) : (
            "No action recommended"
          )}
        </p>
      </header>

      <section>
        <h2>Why Sam surfaced this</h2>
        {page.signals.length === 0 ? (
          <p className="empty-state">No current signal for this person.</p>
        ) : (
          <ul className="signal-list">
            {page.signals.map((signal, index) => (
              <SignalCard key={`${signal.action}-${index}`} signal={signal} />
            ))}
          </ul>
        )}
      </section>

      {page.kept_commitments.length > 0 && (
        <section>
          <h2>Kept commitments</h2>
          <ul className="kept-commitments-list">
            {page.kept_commitments.map((commitment) => (
              <li key={commitment.follow_up_date}>{commitment.note}</li>
            ))}
          </ul>
        </section>
      )}

      <section className="placeholder-section">
        <h2>Relationship timeline</h2>
        <p className="empty-state">Coming in issues/008-relationship-timeline-community-context.md.</p>
      </section>

      <section className="placeholder-section">
        <h2>Community context</h2>
        <p className="empty-state">Coming in issues/008-relationship-timeline-community-context.md.</p>
      </section>
    </main>
  );
}
