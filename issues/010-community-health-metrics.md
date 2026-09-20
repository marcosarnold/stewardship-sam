# 010: Community health metrics

**Type:** AFK

## Parent PRD

`issues/prd.md`

## What to build

Compute the SIG6 inputs per community and show them: member count, historical giving rate, recent giving rate (`RECENT_GIVING_WINDOW_DAYS`), recent-to-historical ratio, recent interaction rate (`RECENT_ENGAGEMENT_WINDOW_DAYS`), historical and recent event participation, stewardship coverage (share of recent donors with a stewardship record), and assignment coverage (share of members with an assigned officer). Expose `GET /api/communities/:id/metrics` and add the metrics as sortable columns on the Communities page from `issues/009-graph-construction-community-definitions.md`. Show a visible note that event data covers only September 2025 to June 2026.

## Acceptance criteria

- [ ] Alumni Board shows about 58.9% ever gave, 8.9% gave in the last 365 days, and 20.6% had an interaction in the last 730 days (Appendix B), within rounding.
- [ ] Every metric's numerator and denominator are documented and computed only in code.
- [ ] A test on a small synthetic dataset verifies each definition, including the window boundaries.
- [ ] The Communities page sorts by each metric.
- [ ] The event-data limitation is shown next to event metrics (G4).
- [ ] Metrics for all 79 communities compute in under 5 seconds and are cached.

## Blocked by

- Blocked by `issues/009-graph-construction-community-definitions.md`

## User stories addressed

The PRD has no numbered user stories, so requirement IDs and success criteria from `issues/prd.md` are cited instead.

- Requirements: SIG6 inputs, UX3 (metrics)
- Success criteria: SC5
