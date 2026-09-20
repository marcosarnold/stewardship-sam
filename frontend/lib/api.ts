import type { RelationshipPage, TodayResponse } from "./types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export async function fetchToday(showAll: boolean = false): Promise<TodayResponse> {
  const url = new URL(`${API_BASE_URL}/api/today`);
  if (showAll) {
    url.searchParams.set("show_all", "true");
  }
  const response = await fetch(url, { cache: "no-store" });
  if (!response.ok) {
    throw new Error(`GET /api/today failed with status ${response.status}`);
  }
  return response.json();
}

export async function dismissToday(entityId: number, reason: string | null): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/api/today/${entityId}/dismiss`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ reason }),
  });
  if (!response.ok) {
    throw new Error(`POST /api/today/${entityId}/dismiss failed with status ${response.status}`);
  }
}

export async function restoreToday(entityId: number): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/api/today/${entityId}/restore`, {
    method: "POST",
  });
  if (!response.ok) {
    throw new Error(`POST /api/today/${entityId}/restore failed with status ${response.status}`);
  }
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
