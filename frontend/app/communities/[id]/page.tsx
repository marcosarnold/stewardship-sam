"use client";

import Link from "next/link";
import { use, useEffect, useState } from "react";
import { fetchCommunityMembers } from "@/lib/api";
import type { CommunityMembers } from "@/lib/types";

export default function CommunityMembersPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const [page, setPage] = useState(1);
  const [data, setData] = useState<CommunityMembers | null>(null);
  const [notFound, setNotFound] = useState(false);

  useEffect(() => {
    let cancelled = false;
    fetchCommunityMembers(id, page).then((result) => {
      if (cancelled) return;
      if (result === null) {
        setNotFound(true);
      } else {
        setData(result);
      }
    });
    return () => {
      cancelled = true;
    };
  }, [id, page]);

  if (notFound) {
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

      <header className="today-header">
        <h1>{data?.community_name ?? "Loading…"}</h1>
        {data && <p className="queue-summary">{data.total} eligible members</p>}
      </header>

      {data && (
        <>
          <ul className="community-list">
            {data.members.map((member) => (
              <li key={member.entity_id} className="community-membership">
                <Link href={`/relationship/${member.entity_id}`} className="community-membership-name">
                  {member.entity_name}
                </Link>
              </li>
            ))}
          </ul>

          <div className="timeline-pagination">
            {page > 1 && (
              <button type="button" className="show-all-button" onClick={() => setPage((p) => p - 1)}>
                Previous
              </button>
            )}
            {data.has_more && (
              <button type="button" className="show-all-button" onClick={() => setPage((p) => p + 1)}>
                Next
              </button>
            )}
          </div>

          <p className="held-back-caveat">{data.note}</p>
        </>
      )}
    </main>
  );
}
