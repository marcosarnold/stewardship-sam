# 007: Priority queue, signal registry, and dismissal

**Type:** AFK

## Parent PRD

`issues/prd.md`

## What to build

Turn the detectors into one prioritized Today queue (UX1). Create a signal registry so detectors plug in with a small interface (`detect(context) -> Signal[]`); later signals (SIG4, SIG6) must register without touching ranking code.

The queue merges signals per constituent into one item with a primary action and supporting evidence, sends every signal through `evaluate_contact`, and ranks by the transparent factors in PRD section 10 (urgency, relationship history, attention deficit, community context, contact pressure) using documented, deterministic ordering. WAIT overrides other actions for the same person. Broken commitments rank high. The UI shows the action label, 1 to 3 evidence points, and the factor that placed the item (for example "Promised follow-up is overdue"), never a numeric score. Add header summary counts by action group, a cap of `TODAY_QUEUE_MAX_ITEMS` with "Show all", an optional officer filter, and dismissal with an optional reason that persists and can be restored.

## Acceptance criteria

- [x] Adding a dummy detector to the registry in a test changes the queue without editing ranking code.
- [x] Valerie Kaur appears once, with THANK as the primary action and the neglected-relationship evidence attached.
- [x] Kieran Kaur appears once as WAIT, and none of his other signals appear as actions.
- [x] Nia Chen's FOLLOW UP ranks above every THANK, ASSIGN, and RECONNECT item (SIG2: broken commitments rank highly).
- [x] Header counts match the items shown, and every item links to its Relationship View.
- [x] Dismissing an item hides it, survives a reload, can be undone, and does not delete the underlying signal.
- [x] No numeric score appears in the UI or in API fields meant for display; internal sort keys are allowed.
- [x] Ranking is deterministic, with tie-breakers, and covered by a fixture test.
- [x] Every signal type passes through `evaluate_contact` before ranking; suppressed items go to "Held back today".

## Blocked by

- Blocked by `issues/002-contact-policy-wait.md`
- Blocked by `issues/003-broken-commitment-follow-up.md`
- Blocked by `issues/004-neglected-relationship-assign-reconnect.md`

## User stories addressed

The PRD has no numbered user stories, so requirement IDs and success criteria from `issues/prd.md` are cited instead.

- Requirements: Section 10, UX1, G1, G2, G3
- Success criteria: SC1, SC3, SC8
