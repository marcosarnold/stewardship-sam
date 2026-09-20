import Link from "next/link";
import { fetchCommunities } from "@/lib/api";

export default async function CommunitiesPage() {
  const communities = await fetchCommunities();
  const eligible = communities.filter((c) => c.eligible);
  const other = communities.filter((c) => !c.eligible);

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

      <section>
        <h2>Eligible communities ({eligible.length})</h2>
        <ul className="community-list">
          {eligible.map((community) => (
            <li key={community.id} className="community-membership">
              <Link href={`/communities/${community.id}`} className="community-membership-name">
                {community.name}
              </Link>
              <span className="community-membership-count">{community.member_count} members</span>
            </li>
          ))}
        </ul>
      </section>

      {other.length > 0 && (
        <section>
          <h2>Below the eligibility threshold ({other.length})</h2>
          <ul className="community-list">
            {other.map((community) => (
              <li key={community.id} className="community-membership">
                <Link href={`/communities/${community.id}`} className="community-membership-name">
                  {community.name}
                </Link>
                <span className="community-membership-count">{community.member_count} members</span>
              </li>
            ))}
          </ul>
        </section>
      )}
    </main>
  );
}
