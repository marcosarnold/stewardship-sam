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

export type TodayResponse = {
  signals: Signal[];
};
