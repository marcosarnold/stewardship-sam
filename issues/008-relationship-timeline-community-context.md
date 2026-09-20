# 008: Relationship timeline and community context

**Type:** AFK

## Parent PRD

`issues/prd.md`

## What to build

Complete the Relationship View from `issues/005-relationship-view-evidence-card.md` with `GET /api/relationships/:id/timeline` and the timeline UI: gifts, interactions (with the `significant` flag), events attended, career changes from `career_history`, and opportunities, newest first with type filters. Add a community-context section listing activities and affiliations with member counts, plus degree and class year. Long timelines paginate. Interaction notes display as plain data and truncate with an expand control. Career changes are shown as neutral facts with no wealth language (G6).

## Acceptance criteria

- [ ] Valerie Kaur's timeline shows the Feb 4, 2026 gift, and the stretch after it is described as "No interactions are recorded".
- [ ] Isaac Chen's timeline shows the Mar 18 reply, the May 15 meeting, and the June and July contacts in order.
- [ ] Type filters work, and empty types say "None recorded" (G4).
- [ ] Career-change entries use neutral wording ("Started as ... at ...") and never mention wealth or capacity (G6).
- [ ] Community context lists each membership and links to the community once `issues/009-graph-construction-community-definitions.md` exists.
- [ ] The busiest timeline in the dataset loads in under 1 second and does not render every row at once.

## Blocked by

- Blocked by `issues/005-relationship-view-evidence-card.md`

## User stories addressed

The PRD has no numbered user stories, so requirement IDs and success criteria from `issues/prd.md` are cited instead.

- Requirements: UX2, G4, G6
- Success criteria: SC4
