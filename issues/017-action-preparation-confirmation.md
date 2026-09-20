# 017: Action preparation and human confirmation

**Type:** AFK

## Parent PRD

`issues/prd.md`

## What to build

**Priority note:** do not start until slices 001 through 016 are solid. This is one of the first cuts if time is short. The hackathon's contribution is judgment about what needs attention, and GiveCampus already has outreach-generation tools (PRD sections 20 and 21).

Add a "Prepare action" panel to the Relationship View from `issues/005-relationship-view-evidence-card.md`: a short brief with the recommended action, the allowed channel from the policy engine in `issues/002-contact-policy-wait.md`, the evidence recap, and 3 to 5 talking points or a checklist (generated through the explanation service if available, with a deterministic fallback). Add explicit confirmation controls ("I'll do this", "Not now", "Dismiss") and an outcome log that records what the fundraiser did, with an optional note, in Sam's own store. Today reflects the outcome. Sam does not send, call, solicit, or change assignments (Section 16). This is not an email writer.

## Acceptance criteria

- [x] The brief includes the action, the allowed channel, the officer who owns the relationship (G3), and evidence bullets.
- [x] No full message drafts are produced (non-goal, Section 20); output is talking points or a checklist.
- [x] Confirmation controls record an outcome with a timestamp, and the Today queue updates accordingly.
- [x] Nothing in the app sends, calls, or writes to GiveCampus data; a test asserts no outbound side effects.
- [x] Restricted channels are never suggested (G1).
- [x] Works with the LLM unavailable via deterministic fallback.

## Blocked by

- Blocked by `issues/002-contact-policy-wait.md`
- Blocked by `issues/005-relationship-view-evidence-card.md`

Planning constraint, not a technical dependency: wait until slices 001 through 016 are solid.

## User stories addressed

The PRD has no numbered user stories, so requirement IDs and success criteria from `issues/prd.md` are cited instead.

- Requirements: Section 16, Section 20 (non-goals), G1, G3
- Success criteria: SC3
