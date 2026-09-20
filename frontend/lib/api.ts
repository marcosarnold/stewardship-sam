import type { TodayResponse } from "./types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export async function fetchToday(): Promise<TodayResponse> {
  const response = await fetch(`${API_BASE_URL}/api/today`, { cache: "no-store" });
  if (!response.ok) {
    throw new Error(`GET /api/today failed with status ${response.status}`);
  }
  return response.json();
}
