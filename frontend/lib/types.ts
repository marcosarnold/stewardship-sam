export type Signal = {
  entity_type: string;
  entity_id: number;
  entity_name: string;
  signal_id: string;
  action: string;
  evidence: string[];
  urgency_date: string | null;
  urgency_amount: number | null;
  channel_hint: string | null;
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
