export type Signal = {
  entity_type: string;
  entity_id: number;
  entity_name: string;
  signal_id: string;
  action: string;
  evidence: string[];
  urgency_date: string | null;
  urgency_amount: number | null;
  urgency_days: number | null;
  channel_hint: string | null;
  assigned_officer: string | null;
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
  signals: Signal[];
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
