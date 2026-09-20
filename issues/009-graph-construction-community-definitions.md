# 009: Graph construction and community definitions

**Type:** AFK

## Parent PRD

`issues/prd.md`

## What to build

Build the graph engine's data layer with NetworkX. Create nodes and edges for the types in PRD section 6 from the available tables: constituents, activities and affiliations, degrees (major and class year), events, employers from `career_history`, and funds and campaigns from gifts. Define a *community* for the MVP as an activity with at least 60 eligible members (`COMMUNITY_MIN_MEMBERS`). Expose `GET /api/communities` (id, name, type, member count, eligibility) and `GET /api/communities/:id/members` (paginated), and add a simple Communities list page. The page carries the note that an edge is shared institutional context, not friendship (G5).

Build the graph once at startup and cache it.

## Acceptance criteria

- [ ] Node and edge counts match the source CSV row counts (tests compare them per type).
- [ ] 79 communities are eligible, and Alumni Board has 180 eligible members (Appendix B).
- [ ] Members and communities exclude organizations and deceased constituents.
- [ ] The members endpoint paginates and returns ids that open the Relationship View.
- [ ] Cold graph build takes under 30 seconds and is cached afterward.
- [ ] The Communities page and API docs state that edges are shared context, not friendship (G5).

## Blocked by

- Blocked by `issues/001-data-layer-stewardship-gap-today.md`

## User stories addressed

The PRD has no numbered user stories, so requirement IDs and success criteria from `issues/prd.md` are cited instead.

- Requirements: Sections 5 and 6, G5
- Success criteria: SC5
