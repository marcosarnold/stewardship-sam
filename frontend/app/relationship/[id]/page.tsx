import Link from "next/link";
import { fetchRelationship } from "@/lib/api";
import type { CommunityMembership, RelationshipSignal } from "@/lib/types";
import Timeline from "./Timeline";
import PrepareAction from "./PrepareAction";
import PostCallNote from "./PostCallNote";

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

function CommunityRow({ membership }: { membership: CommunityMembership }) {
  return (
    <li className="community-membership">
      <span className="community-membership-name">{membership.name}</span>
      {membership.role && <span className="community-membership-role"> · {membership.role}</span>}
      <span className="community-membership-count">
        {membership.member_count} member{membership.member_count === 1 ? "" : "s"}
      </span>
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
        <h2>Prepare action</h2>
        <p className="relationship-subline">
          Sam never sends, calls, or solicits on your behalf -- this is a brief for you to act on.
        </p>
        <PrepareAction entityId={page.entity_id} />
      </section>

      <section>
        <h2>Post-call note</h2>
        <PostCallNote entityId={page.entity_id} />
      </section>

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

      <section>
        <h2>Relationship timeline</h2>
        <Timeline entityId={page.entity_id} />
      </section>

      <section>
        <h2>Community context</h2>
        {page.community_context.length === 0 ? (
          <p className="empty-state">No community memberships are recorded.</p>
        ) : (
          <ul className="community-list">
            {page.community_context.map((membership) => (
              <CommunityRow key={`${membership.type}-${membership.name}`} membership={membership} />
            ))}
          </ul>
        )}
        <p className="held-back-caveat">
          Community links open once issues/009-graph-construction-community-definitions.md exists.
        </p>
      </section>
    </main>
  );
}
