# 014: Ask Sam: person-level queries

**Type:** AFK

## Parent PRD

`issues/prd.md`

## What to build

Add a persistent Ask Sam input on every screen (Section 12). Pipeline: the LLM extracts intent into a strict JSON schema (an intent enum plus filters), the code validates it, a deterministic executor calls the existing engines, and the UI updates with results plus an explanation from `issues/006-grounded-explanations.md`. The LLM receives only the question and the schema, never the dataset. Unsupported or invalid questions get a plain "I can't answer that yet" with the supported examples.

Supported here: AQ1 (who have we promised to follow up with: overdue unresolved commitments and upcoming follow-ups in separate groups), AQ2 (living individuals with lifetime giving of at least $10,000 and no assigned officer), AQ4 (who shouldn't I contact today: WAIT items and held-back people with reasons), and AQ5 ("Why did Valerie surface?" resolves the name, asks the user to choose if it is ambiguous, and returns the evidence-based explanation).

## Acceptance criteria

- [ ] AQ1 returns Nia Chen as overdue and unresolved, lists upcoming follow-ups separately, and can show Isaac Chen's commitment as resolved when asked.
- [ ] AQ2's count equals a direct data query for living individuals with $10,000+ lifetime giving and no assigned officer (asserted in a test).
- [ ] AQ4 lists Kieran Kaur with the contact-pressure reason and the held-back people with their reason codes.
- [ ] AQ5 for "Valerie" resolves to Valerie Kaur or asks which Valerie is meant.
- [ ] Every answer updates the UI (a result list or filtered queue) and includes an explanation grounded in evidence.
- [ ] Tests use a mocked LLM; a keyword fallback handles the four exact phrasings when the API is unavailable.
- [ ] Unsupported questions return the "can't answer yet" response with examples, and never a guess.
- [ ] A prompt-injection test through interaction notes does not change results.

## Blocked by

- Blocked by `issues/002-contact-policy-wait.md`
- Blocked by `issues/003-broken-commitment-follow-up.md`
- Blocked by `issues/004-neglected-relationship-assign-reconnect.md`
- Blocked by `issues/006-grounded-explanations.md`
- Blocked by `issues/007-priority-queue-and-dismissal.md`

## User stories addressed

The PRD has no numbered user stories, so requirement IDs and success criteria from `issues/prd.md` are cited instead.

- Requirements: Section 12, Section 13, AQ1, AQ2, AQ4, AQ5, G1, G4
- Success criteria: SC7
