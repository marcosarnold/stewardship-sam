# 013: Community network visualization

**Type:** HITL

## Parent PRD

`issues/prd.md`

## What to build

Add the signature visualization to the Community View from `issues/011-community-cooling-today-and-community-view.md` using Cytoscape.js or D3. The community sits at the center, member nodes around it (capped at `COMMUNITY_GRAPH_MAX_NODES`, prioritizing connectors and members with attention signals, with the remainder shown as "+N more"), and other communities as bridge nodes. Connectors from `issues/012-connector-analysis.md` are highlighted, with their basis shown on hover or click. Clicking a person opens the Relationship View. Include a legend, the "shared context, not friendship" note (G5), and a keyboard-accessible list alternative.

**Human checkpoints:** (1) review a sketch of node, edge, and color encoding before building; (2) review the finished screen against the 30-second comprehension goal with someone who has not seen it.

## Acceptance criteria

- [ ] Alumni Board renders in under 2 seconds with connectors visibly highlighted.
- [ ] Hover or click on a connector shows the basis text from the connectors API.
- [ ] Clicking a person opens their Relationship View; clicking a bridge community opens its Community View.
- [ ] Node cap works and the omitted count is shown.
- [ ] A legend and the G5 note are visible, and a list view offers the same information without the graph.
- [ ] Both human checkpoints are recorded with outcome and any changes made.
- [ ] The screen supports a decision (who to talk to about this community) and is not a decorative homepage graph (Section 11).

## Blocked by

- Blocked by `issues/011-community-cooling-today-and-community-view.md`
- Blocked by `issues/012-connector-analysis.md`

## User stories addressed

The PRD has no numbered user stories, so requirement IDs and success criteria from `issues/prd.md` are cited instead.

- Requirements: UX3, Section 8, G5
- Success criteria: SC5, SC6
