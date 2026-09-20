import type {
  Community,
  CommunityMembers,
  RelationshipPage,
  Timeline,
  TimelineEntryType,
  TodayResponse,
} from "./types";

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

export async function fetchTimeline(
  entityId: string | number,
  options: { types?: TimelineEntryType[]; page?: number } = {}
): Promise<Timeline> {
  const url = new URL(`${API_BASE_URL}/api/relationships/${entityId}/timeline`);
  if (options.types && options.types.length > 0) {
    url.searchParams.set("types", options.types.join(","));
  }
  if (options.page) {
    url.searchParams.set("page", String(options.page));
  }
  const response = await fetch(url, { cache: "no-store" });
  if (!response.ok) {
    throw new Error(`GET /api/relationships/${entityId}/timeline failed with status ${response.status}`);
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

export async function fetchCommunities(): Promise<Community[]> {
  const response = await fetch(`${API_BASE_URL}/api/communities`, { cache: "no-store" });
  if (!response.ok) {
    throw new Error(`GET /api/communities failed with status ${response.status}`);
  }
  const body = await response.json();
  return body.communities;
}

export async function fetchCommunityMembers(
  communityId: string,
  page: number = 1
): Promise<CommunityMembers | null> {
  const response = await fetch(`${API_BASE_URL}/api/communities/${communityId}/members?page=${page}`, {
    cache: "no-store",
  });
  if (response.status === 404) {
    return null;
  }
  if (!response.ok) {
    throw new Error(`GET /api/communities/${communityId}/members failed with status ${response.status}`);
  }
  return response.json();
}
