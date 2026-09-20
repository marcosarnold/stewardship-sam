# 003: Broken Commitment (FOLLOW UP)

**Type:** AFK

## Parent PRD

`issues/prd.md`

## What to build

Implement SIG2 using the resolution rule frozen in PRD Appendix A, and emit FOLLOW UP signals with days-overdue as an urgency field. Add `GET /api/followups?include_resolved=true`, which lists all 40 due commitments with their resolution status and the interaction that resolved each one. That endpoint is what lets the demo show the control case (Isaac Chen) and later feeds Ask Sam.

The rule: a commitment is resolved when a later interaction with the same constituent occurs on or after the promised follow-up date, or when the source data explicitly marks it completed or cancelled. This dataset has no such field, so only the first clause applies; leave a documented hook for the second.

## Acceptance criteria

- [ ] Exactly 1 due commitment is unresolved: Nia Chen (14456). Evidence: "Follow-up was due May 1, 2026", "No subsequent follow-up is recorded", and the prior outcome (no_response on a Mar 15 solicitation call).
- [ ] Nia's evidence shows her assigned officer (G3) and that a call is the allowed channel (email is inactive).
- [ ] Isaac Chen (2548) does NOT appear as FOLLOW UP. `include_resolved=true` shows his May 15 commitment as resolved by the May 15 meeting.
- [ ] Follow-up dates after `AS_OF_DATE` (such as Isaac's 2026-12-01) are classified as upcoming, never overdue.
- [ ] Boundary tests: an interaction on the follow-up date resolves it; an interaction the day before does not.
- [ ] A documented hook exists for an explicit completed/cancelled indicator and currently reports "not available in this dataset".
- [ ] Nothing in the UI or API says a promise was "broken" or "missed" as fact; it says what is and is not recorded (G4).

## Blocked by

- Blocked by `issues/001-data-layer-stewardship-gap-today.md`

## User stories addressed

The PRD has no numbered user stories, so requirement IDs and success criteria from `issues/prd.md` are cited instead.

- Requirements: SIG2, ACT2, G3, G4
- Success criteria: SC1, SC3
