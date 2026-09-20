"use client";

import Link from "next/link";
import { useState } from "react";
import { askSam } from "@/lib/api";
import type { AskResponse } from "@/lib/types";

function ResultLinks({ intent, results }: { intent: string; results: any }) {
  if (intent === "FOLLOW_UPS") {
    return (
      <div className="ask-sam-results">
        <p>
          <strong>Overdue</strong>
        </p>
        <ul className="community-list">
          {results.overdue.map((r: any) => (
            <li key={r.entity_id} className="community-membership">
              <Link href={`/relationship/${r.entity_id}`} className="community-membership-name">
                {r.entity_name}
              </Link>
            </li>
          ))}
        </ul>
        {results.upcoming.length > 0 && (
          <>
            <p>
              <strong>Upcoming</strong>
            </p>
            <ul className="community-list">
              {results.upcoming.map((r: any) => (
                <li key={r.entity_id} className="community-membership">
                  <Link href={`/relationship/${r.entity_id}`} className="community-membership-name">
                    {r.entity_name}
                  </Link>
                  <span className="community-membership-count">{r.follow_up_date}</span>
                </li>
              ))}
            </ul>
          </>
        )}
      </div>
    );
  }

  if (intent === "UNASSIGNED_MAJOR_DONORS") {
    return (
      <ul className="community-list">
        {results.map((r: any) => (
          <li key={r.entity_id} className="community-membership">
            <Link href={`/relationship/${r.entity_id}`} className="community-membership-name">
              {r.entity_name}
            </Link>
          </li>
        ))}
      </ul>
    );
  }

  if (intent === "DO_NOT_CONTACT_TODAY") {
    return (
      <ul className="community-list">
        {results.wait.map((r: any) => (
          <li key={`wait-${r.entity_id}`} className="community-membership">
            <Link href={`/relationship/${r.entity_id}`} className="community-membership-name">
              {r.entity_name}
            </Link>
            <span className="community-membership-count">WAIT</span>
          </li>
        ))}
        {results.held_back.map((r: any, i: number) => (
          <li key={`held-${r.entity_id}-${i}`} className="community-membership">
            <Link href={`/relationship/${r.entity_id}`} className="community-membership-name">
              {r.entity_name}
            </Link>
            <span className="community-membership-count">{r.reason_code}</span>
          </li>
        ))}
      </ul>
    );
  }

  if (intent === "COOLING_COMMUNITIES") {
    return (
      <ul className="community-list">
        {results.map((r: any) => (
          <li key={r.community_id} className="community-membership">
            <Link href={`/community/${r.community_id}`} className="community-membership-name">
              {r.community_name}
            </Link>
            <span className="community-membership-count">{r.action}</span>
          </li>
        ))}
      </ul>
    );
  }

  if (intent === "LOCATION_ACTIVITY" && results.status === "found") {
    return (
      <ul className="community-list">
        {results.people.map((p: any) => (
          <li key={p.entity_id} className="community-membership">
            <Link href={`/relationship/${p.entity_id}`} className="community-membership-name">
              {p.entity_name}
            </Link>
            <span className="community-membership-count">{p.communities.join(", ")}</span>
          </li>
        ))}
      </ul>
    );
  }

  if (intent === "WHY_PERSON" && results.status === "found") {
    return (
      <p>
        <Link href={`/relationship/${results.entity_id}`}>View relationship</Link>
      </p>
    );
  }

  if (intent === "WHY_PERSON" && results.status === "ambiguous") {
    return (
      <ul className="community-list">
        {results.matches.map((m: any) => (
          <li key={m.entity_id} className="community-membership">
            <Link href={`/relationship/${m.entity_id}`} className="community-membership-name">
              {m.entity_name}
            </Link>
          </li>
        ))}
      </ul>
    );
  }

  return null;
}

export default function AskSam() {
  const [open, setOpen] = useState(false);
  const [question, setQuestion] = useState("");
  const [response, setResponse] = useState<AskResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!question.trim()) return;
    setLoading(true);
    setError(null);
    try {
      const result = await askSam(question);
      setResponse(result);
    } catch {
      setError("Could not reach the Stewardship Sam API. Is the backend running?");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="ask-sam">
      <button type="button" className="ask-sam-toggle" onClick={() => setOpen(!open)}>
        {open ? "Close Ask Sam" : "Ask Sam"}
      </button>
      {open && (
        <div className="ask-sam-panel">
          <form onSubmit={handleSubmit}>
            <input
              type="text"
              className="ask-sam-input"
              placeholder="Who have we promised to follow up with?"
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
            />
            <button type="submit" className="ask-sam-submit" disabled={loading}>
              {loading ? "Asking…" : "Ask"}
            </button>
          </form>
          {error && <p className="error-state">{error}</p>}
          {response && (
            <div className="ask-sam-response">
              <p>{response.answer}</p>
              {response.examples && (
                <ul className="evidence-list">
                  {response.examples.map((ex) => (
                    <li key={ex}>{ex}</li>
                  ))}
                </ul>
              )}
              {response.intent && <ResultLinks intent={response.intent} results={response.results} />}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
