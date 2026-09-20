# 011: Community Cooling on Today and Community View header

**Type:** AFK

## Parent PRD

`issues/prd.md`

## What to build

Implement SIG6 with the rule frozen in PRD Appendix A and register it with the queue from `issues/007-priority-queue-and-dismissal.md`. Communities appear on Today as a distinct item type, clearly separate from people. Build the Community View (UX3) at `/community/:id` with the header (member count, historical against recent giving, recent interaction rate), a "Why this community surfaced" explanation, the recommended action (RECONNECT by default, INVITE when an upcoming event exists; ADVOCATE waits for connectors), and an "Explore members" list showing which members have attention signals. If `issues/006-grounded-explanations.md` has merged, use its explanation service; otherwise show the evidence list. The network graph itself arrives in `issues/013-community-network-visualization.md`.

The PRD's Today mock labels this action RE-ENGAGE, which is not in the constrained vocabulary. Use RECONNECT, INVITE, or ADVOCATE as the action; "Re-engage" may appear only as a display group heading.

## Acceptance criteria

- [x] 12 communities are detected as cooling, and Alumni Board is one of them (Appendix B).
- [x] The Alumni Board card shows "59% ever gave" moving to "9% gave in the past year" and "21% had an interaction in the last two years".
- [x] A test confirms a community with high historical giving and steady recent giving is not flagged.
- [x] Community items are visually distinct from people on Today, dismissible, and link to the Community View.
- [x] Explore members lists members with counts of their attention signals and links to each Relationship View.
- [x] The recommended action follows the documented rule, and "RE-ENGAGE" is never used as an action.
- [x] Wording states associations are descriptive, not causal (Section 3 caveat).

## Blocked by

- Blocked by `issues/007-priority-queue-and-dismissal.md`
- Blocked by `issues/010-community-health-metrics.md`

## User stories addressed

The PRD has no numbered user stories, so requirement IDs and success criteria from `issues/prd.md` are cited instead.

- Requirements: SIG6, ACT3, ACT5, UX1, UX3 (header, explanation, explore members)
- Success criteria: SC5
