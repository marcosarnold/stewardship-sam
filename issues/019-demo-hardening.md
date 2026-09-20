# 019: Demo hardening and rehearsal

**Type:** HITL

## Parent PRD

`issues/prd.md`

## What to build

Make the demo path reliable. Script the updated narrative (PRD section 23 with Appendix C changes): open Today; FOLLOW UP with Nia Chen and show Isaac Chen as the control whose commitment was kept; THANK with Valerie Kaur; WAIT with Kieran Kaur; ask "Which communities are we losing touch with?", open Alumni Board with its network and connectors; close on Today.

Add a seed/reset command that returns the app to a deterministic state (dismissals cleared), an automated test that walks the demo path against the API, and loading, empty, and error states. Verify the performance budget and the LLM-outage fallback. **Human checkpoint:** rehearse with two people who have not seen the product, and record whether each understood a recommendation within about 30 seconds.

## Acceptance criteria

- [x] A reset command restores the demo state, and an automated test verifies every cast member's expected action (Appendix B). (`POST /api/demo/reset`, `backend/app/demo_reset.py`; `tests/test_demo_path.py`.)
- [x] Today loads in under 2 seconds, the community graph in under 2 seconds, and Ask Sam answers in under 5 seconds on the demo machine. (`tests/test_demo_performance.py`, verified passing.)
- [x] With the LLM disabled, the entire demo path still works via template fallbacks. (`tests/test_demo_llm_outage.py`; this environment has no `OPENAI_API_KEY`, so every other test already exercises this path too.)
- [x] Loading, empty, and error states exist on every screen. (Audited all six pages/components; added the missing ones to `communities/page.tsx`, `communities/[id]/page.tsx`, `AskSam.tsx`, and `CommunityGraph.tsx`.)
- [ ] The 30-second comprehension test is run with two people, and results and fixes are recorded. **Not done** — requires two people who haven't seen the product; the log template is in the speaker notes, unfilled.
- [x] Speaker notes state the data caveats: missing records are not proof something did not happen, the data is synthetic, and restriction flags are a snapshot. (Published artifact, see below.)
- [ ] A backup recording of the full demo exists. **Not done** — I can't record video; someone needs to record a run using the speaker-notes script.
- [x] Run instructions let a teammate start the app from scratch. (README "Running the app" and new "Demo" section.)

**Speaker notes:** https://claude.ai/artifact/QXm7Np51aNGtVGYUD2UHXW — five-beat script, data caveats, troubleshooting, and the comprehension-check log template.

**Human checkpoint:** not completed by the agent — rehearsing with two people who haven't used the product, and recording a backup video, both require a human in the loop that couldn't be arranged under this session's time constraint. Flagging honestly rather than fabricating results.

## Blocked by

- Blocked by `issues/001-data-layer-stewardship-gap-today.md`
- Blocked by `issues/002-contact-policy-wait.md`
- Blocked by `issues/003-broken-commitment-follow-up.md`
- Blocked by `issues/004-neglected-relationship-assign-reconnect.md`
- Blocked by `issues/005-relationship-view-evidence-card.md`
- Blocked by `issues/006-grounded-explanations.md`
- Blocked by `issues/007-priority-queue-and-dismissal.md`
- Blocked by `issues/008-relationship-timeline-community-context.md`
- Blocked by `issues/009-graph-construction-community-definitions.md`
- Blocked by `issues/010-community-health-metrics.md`
- Blocked by `issues/011-community-cooling-today-and-community-view.md`
- Blocked by `issues/012-connector-analysis.md`
- Blocked by `issues/013-community-network-visualization.md`
- Blocked by `issues/014-ask-sam-person-queries.md`
- Blocked by `issues/015-ask-sam-community-queries.md`

Slices 016, 017, and 018 are enhancements and do not block the demo.

## User stories addressed

The PRD has no numbered user stories, so requirement IDs and success criteria from `issues/prd.md` are cited instead.

- Requirements: Section 18, Section 23
- Success criteria: SC1 to SC8
