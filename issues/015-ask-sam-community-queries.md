# 015: Ask Sam: community and graph queries

**Type:** AFK

## Parent PRD

`issues/prd.md`

## What to build

Extend the Ask Sam schema and executor from `issues/014-ask-sam-person-queries.md` with graph-aware intents. AQ3 ("Which communities are losing engagement?") returns the SIG6 list from `issues/011-community-cooling-today-and-community-view.md` with metrics, ordered by decline ratio, each linking to its Community View. AQ6 ("Show Boston alumni connected to athletics") combines a location filter (city Boston, MA) with graph membership in communities whose activity type is Athletics, and returns people with the athletic communities that connect them. Optionally link to the connector view from `issues/012-connector-analysis.md`. This slice proves the copilot can query the graph, not only tables.

## Acceptance criteria

- [ ] AQ3 returns the same 12 communities as the Today cooling detection and includes Alumni Board.
- [ ] AQ6's count equals a direct query for Boston, MA constituents with at least one Athletics membership (asserted in a test).
- [ ] AQ6 results show which athletic communities connect each person, worded as shared institutional context (G5).
- [ ] An unmatched location returns a clear "no constituents found in that location" message.
- [ ] Every result links to a Relationship View or Community View and includes a grounded explanation.
- [ ] The schema validator rejects any intent outside the supported list.

## Blocked by

- Blocked by `issues/014-ask-sam-person-queries.md`
- Blocked by `issues/011-community-cooling-today-and-community-view.md`
- Blocked by `issues/012-connector-analysis.md`

## User stories addressed

The PRD has no numbered user stories, so requirement IDs and success criteria from `issues/prd.md` are cited instead.

- Requirements: Section 12, AQ3, AQ6, G5
- Success criteria: SC5, SC6, SC7
