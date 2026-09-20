# 005: Relationship View with evidence card

**Type:** AFK

## Parent PRD

`issues/prd.md`

## What to build

Build the Relationship View (UX2) at `/relationship/:id` with `GET /api/relationships/:id`. Header: name, class year and degree from `degrees` where available, relevant activities, city and state, assigned fundraiser (name from `staff`), and the recommended action. Below it, a "Why Sam surfaced this" card lists every current signal for the person with its evidence points, the allowed channel, and the policy status. A "Kept commitments" note lists resolved follow-ups when they exist.

The page renders whatever signals exist through the shared `Signal` record, so detectors from `issues/002-contact-policy-wait.md`, `issues/003-broken-commitment-follow-up.md`, and `issues/004-neglected-relationship-assign-reconnect.md` appear automatically as they merge. Timeline and community sections are placeholders until `issues/008-relationship-timeline-community-context.md`. Drill-down links from Today now resolve here.

## Acceptance criteria

- [x] Valerie Kaur's page shows the $25,000 gift, the THANK recommendation with its evidence, and email as the allowed channel.
- [x] Once slices 002 and 003 are merged, Kieran Kaur's page shows WAIT with its count, Nia Chen's shows FOLLOW UP, and Isaac Chen's shows "No action recommended" plus his kept May 15 commitment.
- [x] The assigned fundraiser is shown before the recommendation (G3).
- [x] Missing fields show "Not on file" (G4).
- [x] Unknown, non-individual, or deceased ids return a clear not-found state.
- [x] The layout reads as a narrative (header, why, context), not a scorecard, and shows no numeric relationship score.
- [x] Every "View relationship" link on Today opens the right person.

## Blocked by

- Blocked by `issues/001-data-layer-stewardship-gap-today.md`

## User stories addressed

The PRD has no numbered user stories, so requirement IDs and success criteria from `issues/prd.md` are cited instead.

- Requirements: UX2, G3, G4
- Success criteria: SC2, SC4
