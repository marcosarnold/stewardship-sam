# 012: Connector analysis (backend)

**Type:** AFK

## Parent PRD

`issues/prd.md`

## What to build

Compute potential connectors for a community from observed membership overlap. Build the person-to-community projection from the graph in `issues/009-graph-construction-community-definitions.md` and calculate, for members of a community, the number of other eligible communities they belong to, degree centrality, and betweenness centrality. Rank connectors and give each a plain-language basis such as "Spans 3 relevant institutional communities: A, B, C". Each connector also carries its policy status from `evaluate_contact` so restricted people are not suggested for outreach. Expose `GET /api/communities/:id/connectors?limit=`.

This slice is intentionally backend-only so it can run in parallel with UI work. It is verifiable through the API and tests; the visual layer arrives in `issues/013-community-network-visualization.md`.

## Acceptance criteria

- [ ] Results for Alumni Board are deterministic and each connector includes overlap count, the two centrality values, the communities spanned, and the basis text.
- [ ] A test scans all generated text and fails on "influential", "influence", "friend", or similar claims (G5).
- [ ] Each connector includes a policy status (allowed, suppressed, or restricted).
- [ ] The analysis runs in under 5 seconds cold and is cached afterward.
- [ ] API docs state that overlap shows shared institutional context, not friendship or influence.
- [ ] Unit tests use a small hand-built graph with known centrality values.

## Blocked by

- Blocked by `issues/009-graph-construction-community-definitions.md`

## User stories addressed

The PRD has no numbered user stories, so requirement IDs and success criteria from `issues/prd.md` are cited instead.

- Requirements: Section 8, G1, G5
- Success criteria: SC6
