import type { RelationshipPage, TodayResponse } from "./types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export async function fetchToday(): Promise<TodayResponse> {
  const response = await fetch(`${API_BASE_URL}/api/today`, { cache: "no-store" });
  if (!response.ok) {
    throw new Error(`GET /api/today failed with status ${response.status}`);
  }
  return response.json();
}

export async function fetchRelationship(entityId: string): Promise<RelationshipPage | null> {
  const response = await fetch(`${API_BASE_URL}/api/relationships/${entityId}`, {
    cache: "no-store",
  });
  if (response.status === 404) {
    return null;
  }
  if (!response.ok) {
    throw new Error(`GET /api/relationships/${entityId} failed with status ${response.status}`);
  }
  return response.json();
}
