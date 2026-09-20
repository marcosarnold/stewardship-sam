import Link from "next/link";
import { fetchCommunityView } from "@/lib/api";
import CommunityGraph from "./CommunityGraph";

function pct(value: number): string {
  return `${Math.round(value * 1000) / 10}%`;
}

export default async function CommunityViewPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const view = await fetchCommunityView(id);

  if (view === null) {
    return (
      <main>
        <p>
          <Link href="/communities">&larr; Back to Communities</Link>
        </p>
        <h1>No community record</h1>
        <p className="empty-state">Community {id} is unknown.</p>
      </main>
    );
  }

  return (
    <main>
      <p>
        <Link href="/communities">&larr; Back to Communities</Link>
      </p>

      <header className="relationship-header">
        <span className="community-badge">Community</span>
        <h1>{view.name}</h1>
        <p className="relationship-subline">{view.member_count} eligible members</p>
        <p className="relationship-subline">
          {pct(view.historical_giving_rate)} ever gave, {pct(view.recent_giving_rate)} gave in the past year
        </p>
        <p className="relationship-subline">
          {pct(view.recent_interaction_rate)} had an interaction in the last two years
        </p>
        <p className="relationship-recommendation">
          {view.recommended_action ? (
            <span className="action-pill">{view.recommended_action}</span>
          ) : (
            "No action recommended"
          )}
        </p>
      </header>

      <section>
        <h2>Why this community surfaced</h2>
        {view.why_surfaced.length === 0 ? (
          <p className="empty-state">This community is not currently cooling.</p>
        ) : (
          <ul className="evidence-list">
            {view.why_surfaced.map((line) => (
              <li key={line}>{line}</li>
            ))}
          </ul>
        )}
        <p className="held-back-caveat">{view.wording_note}</p>
      </section>

      <section>
        <h2>Network</h2>
        <CommunityGraph communityId={view.id} />
      </section>

      <section>
        <h2>Explore members</h2>
        <p className="relationship-subline">
          An edge is shared institutional context, not friendship -- membership here does not imply any
          direct relationship between members.
        </p>
        <ul className="community-list">
          {view.explore_members.map((member) => (
            <li key={member.entity_id} className="community-membership">
              <Link href={`/relationship/${member.entity_id}`} className="community-membership-name">
                {member.entity_name}
              </Link>
              <span className="community-membership-count">
                {member.signal_count} attention signal{member.signal_count === 1 ? "" : "s"}
              </span>
            </li>
          ))}
        </ul>
      </section>
    </main>
  );
}
