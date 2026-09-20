# 013: Community network visualization

**Type:** HITL

## Parent PRD

`issues/prd.md`

## What to build

Add the signature visualization to the Community View from `issues/011-community-cooling-today-and-community-view.md` using Cytoscape.js or D3. The community sits at the center, member nodes around it (capped at `COMMUNITY_GRAPH_MAX_NODES`, prioritizing connectors and members with attention signals, with the remainder shown as "+N more"), and other communities as bridge nodes. Connectors from `issues/012-connector-analysis.md` are highlighted, with their basis shown on hover or click. Clicking a person opens the Relationship View. Include a legend, the "shared context, not friendship" note (G5), and a keyboard-accessible list alternative.

**Human checkpoints:** (1) review a sketch of node, edge, and color encoding before building; (2) review the finished screen against the 30-second comprehension goal with someone who has not seen it.

**Checkpoint 1 outcome:** approved as proposed (2026-09-20) — center community node, member dots around it, connectors highlighted larger with an accent border and hover/click basis text, bridge communities as diamonds on the outer ring, capped at `COMMUNITY_GRAPH_MAX_NODES` with a "+N more" node. No changes requested.

**Checkpoint 2 outcome:** given the project deadline, no outside naive-user reviewer was available; the user reviewed the finished screenshot directly against the 30-second comprehension goal instead of a blind third party (2026-09-20) and approved it as-is. No changes requested. This substitution is a documented deviation from the literal checkpoint instruction, made under explicit time pressure.

## Acceptance criteria

- [x] Alumni Board renders in under 2 seconds with connectors visibly highlighted. (Verified against a production build — `npm run build && npm start` — at ~1.56s; the Next.js dev server's compile/HMR overhead made this criterion unmeasurable in dev mode.)
- [x] Hover or click on a connector shows the basis text from the connectors API.
- [x] Clicking a person opens their Relationship View; clicking a bridge community opens its Community View.
- [x] Node cap works and the omitted count is shown.
- [x] A legend and the G5 note are visible, and a list view offers the same information without the graph.
- [x] Both human checkpoints are recorded with outcome and any changes made.
- [x] The screen supports a decision (who to talk to about this community) and is not a decorative homepage graph (Section 11).

## Blocked by

- Blocked by `issues/011-community-cooling-today-and-community-view.md`
- Blocked by `issues/012-connector-analysis.md`

## User stories addressed

The PRD has no numbered user stories, so requirement IDs and success criteria from `issues/prd.md` are cited instead.

- Requirements: UX3, Section 8, G5
- Success criteria: SC5, SC6
