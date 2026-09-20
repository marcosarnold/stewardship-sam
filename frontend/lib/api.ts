import type {
  ActionBrief,
  ActionOutcome,
  AskResponse,
  Community,
  ExtractedNote,
  SavedNote,
  CommunityGraph,
  CommunityMembers,
  CommunityMetrics,
  CommunityView,
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

export async function dismissToday(entityId: number | string, reason: string | null): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/api/today/${entityId}/dismiss`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ reason }),
  });
  if (!response.ok) {
    throw new Error(`POST /api/today/${entityId}/dismiss failed with status ${response.status}`);
  }
}

export async function restoreToday(entityId: number | string): Promise<void> {
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

export async function fetchActionBrief(entityId: string | number): Promise<ActionBrief | null> {
  const response = await fetch(`${API_BASE_URL}/api/relationships/${entityId}/prepare-action`, {
    cache: "no-store",
  });
  if (response.status === 404) {
    return null;
  }
  if (!response.ok) {
    throw new Error(`GET /api/relationships/${entityId}/prepare-action failed with status ${response.status}`);
  }
  return response.json();
}

export async function confirmAction(
  entityId: string | number,
  action: string | null,
  outcome: "done" | "not_now" | "dismissed",
  note: string | null
): Promise<ActionOutcome> {
  const response = await fetch(`${API_BASE_URL}/api/relationships/${entityId}/confirm-action`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ action, outcome, note }),
  });
  if (!response.ok) {
    throw new Error(`POST /api/relationships/${entityId}/confirm-action failed with status ${response.status}`);
  }
  return response.json();
}

export async function extractNote(entityId: string | number, note: string): Promise<ExtractedNote> {
  const response = await fetch(`${API_BASE_URL}/api/relationships/${entityId}/notes/extract`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ note }),
  });
  if (!response.ok) {
    throw new Error(`POST /api/relationships/${entityId}/notes/extract failed with status ${response.status}`);
  }
  return response.json();
}

export async function saveNote(
  entityId: string | number,
  fields: ExtractedNote,
  rawNote: string
): Promise<SavedNote> {
  const response = await fetch(`${API_BASE_URL}/api/relationships/${entityId}/notes`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ ...fields, raw_note: rawNote }),
  });
  if (!response.ok) {
    throw new Error(`POST /api/relationships/${entityId}/notes failed with status ${response.status}`);
  }
  return response.json();
}

export async function fetchLatestNote(entityId: string | number): Promise<SavedNote | null> {
  const response = await fetch(`${API_BASE_URL}/api/relationships/${entityId}/notes/latest`, {
    cache: "no-store",
  });
  if (response.status === 404) {
    return null;
  }
  if (!response.ok) {
    throw new Error(`GET /api/relationships/${entityId}/notes/latest failed with status ${response.status}`);
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

export async function fetchCommunityMetrics(communityId: string): Promise<CommunityMetrics> {
  const response = await fetch(`${API_BASE_URL}/api/communities/${communityId}/metrics`, { cache: "no-store" });
  if (!response.ok) {
    throw new Error(`GET /api/communities/${communityId}/metrics failed with status ${response.status}`);
  }
  return response.json();
}

export async function fetchCommunityView(communityId: string): Promise<CommunityView | null> {
  const response = await fetch(`${API_BASE_URL}/api/community/${communityId}`, { cache: "no-store" });
  if (response.status === 404) {
    return null;
  }
  if (!response.ok) {
    throw new Error(`GET /api/community/${communityId} failed with status ${response.status}`);
  }
  return response.json();
}

export async function fetchCommunityGraph(communityId: string): Promise<CommunityGraph | null> {
  const response = await fetch(`${API_BASE_URL}/api/community/${communityId}/graph`, { cache: "no-store" });
  if (response.status === 404) {
    return null;
  }
  if (!response.ok) {
    throw new Error(`GET /api/community/${communityId}/graph failed with status ${response.status}`);
  }
  return response.json();
}

export async function fetchAllCommunityMetrics(): Promise<Record<string, CommunityMetrics>> {
  const response = await fetch(`${API_BASE_URL}/api/communities/metrics`, { cache: "no-store" });
  if (!response.ok) {
    throw new Error(`GET /api/communities/metrics failed with status ${response.status}`);
  }
  return response.json();
}

export async function askSam(question: string): Promise<AskResponse> {
  const response = await fetch(`${API_BASE_URL}/api/ask`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question }),
  });
  if (!response.ok) {
    throw new Error(`POST /api/ask failed with status ${response.status}`);
  }
  return response.json();
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
