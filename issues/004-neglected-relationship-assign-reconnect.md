# 004: Neglected Relationship (ASSIGN / RECONNECT)

**Type:** AFK

## Parent PRD

`issues/prd.md`

## What to build

Implement SIG3 with the rule frozen in PRD Appendix A. Recommend ASSIGN when the person has no assigned officer and RECONNECT when one exists. Evidence includes lifetime giving, the date of the last recorded interaction (or "No interaction is recorded"), assignment status with the officer's name when assigned (G3), and the count of related opportunities. Route candidates through `evaluate_contact` from `issues/002-contact-policy-wait.md`. This signal never produces ASK.

Today shows these items. Until `issues/007-priority-queue-and-dismissal.md` merges signals per person, a person may appear more than once (for example Valerie Kaur as both THANK and RECONNECT); that is expected and resolved there.

## Acceptance criteria

- [x] 116 living individuals with $10,000+ lifetime giving and no interaction in 730 days (or ever) are detected; 101 get ASSIGN and 15 get RECONNECT (Appendix B).
- [x] Every ASSIGN item states that no fundraiser is assigned; every RECONNECT item names the assigned officer before suggesting action (G3).
- [x] The signal never returns ASK, and a unit test enforces it (G1).
- [x] Evidence says "No interaction is recorded" rather than "never contacted" when there are no interactions (G4).
- [x] `do_not_solicit` people can still receive ASSIGN (an internal action) but the policy result is shown alongside.
- [x] Threshold values come only from the config module.

## Blocked by

- Blocked by `issues/001-data-layer-stewardship-gap-today.md`
- Blocked by `issues/002-contact-policy-wait.md`

## User stories addressed

The PRD has no numbered user stories, so requirement IDs and success criteria from `issues/prd.md` are cited instead.

- Requirements: SIG3, ACT3, ACT4, G1, G3, G4
- Success criteria: SC1, SC3
