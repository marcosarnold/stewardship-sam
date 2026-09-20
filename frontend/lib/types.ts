export type SupportingSignal = {
  action: string;
  evidence: string[];
};

// A merged Today card: one person, one primary action, ranked by
// app/priority_queue.py (PRD Section 10). Not the same shape as a raw
// Signal -- see RelationshipSignal for that (the unmerged "why" list).
export type QueueItem = {
  entity_type: string;
  entity_id: number;
  entity_name: string;
  action: string;
  evidence: string[];
  channel_hint: string | null;
  assigned_officer: string | null;
  ranking_factor: string;
  supporting_signals: SupportingSignal[];
  dismissed: boolean;
  dismiss_reason: string | null;
  explanation: string;
  explanation_source: "llm" | "template";
};

export type HeldBackItem = {
  entity_type: string;
  entity_id: number;
  entity_name: string;
  action: string;
  reason_code: string;
  reason: string;
};

export type HeldBackReasonCount = {
  reason_code: string;
  count: number;
};

export type HeldBack = {
  reasons: HeldBackReasonCount[];
  items: HeldBackItem[];
};

export type TodayResponse = {
  signals: QueueItem[];
  total_count: number;
  dismissed: QueueItem[];
  counts: Record<string, number>;
  cap: number;
  show_all: boolean;
  held_back: HeldBack;
};

export type RelationshipSignal = {
  entity_type: string;
  entity_id: number;
  entity_name: string;
  signal_id?: string;
  action: string;
  evidence: string[];
  urgency_date?: string | null;
  urgency_amount?: number | null;
  urgency_days?: number | null;
  channel_hint?: string | null;
  assigned_officer?: string | null;
  policy_status: "shown" | "held_back";
  policy_reason_code?: string | null;
  policy_reason?: string | null;
};

export type KeptCommitment = {
  follow_up_date: string;
  resolved_at: string | null;
  note: string;
};

export type RelationshipPage = {
  entity_id: number;
  entity_name: string;
  class_year: number | null;
  degree: string | null;
  activities: string[];
  city: string | null;
  state: string | null;
  assigned_officer: string | null;
  recommended_action: string | null;
  signals: RelationshipSignal[];
  kept_commitments: KeptCommitment[];
};
