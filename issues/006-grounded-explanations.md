# 006: Grounded explanations (LLM with validation and fallback)

**Type:** AFK

## Parent PRD

`issues/prd.md`

## What to build

Build the explanation service used by every later screen: `explain(payload)` returns a short "why" for a signal or query result. The payload is structured evidence produced by deterministic code. The LLM (OpenAI, per PRD section 14) never sees the raw dataset.

Wire it into the Today cards and the "Why Sam surfaced this" card from `issues/005-relationship-view-evidence-card.md`. Validate every response: each date, number, and name in the text must appear in the payload; banned phrasings (Appendix A language rules) are rejected. Fall back to deterministic templates when the API is unavailable, unconfigured, slow, or returns invalid output. Treat interaction notes as untrusted data, never as instructions. Cache by evidence hash and put the client behind an interface so tests use a mock.

## Acceptance criteria

- [ ] Explanations use only the evidence payload; a test injects a fabricated fact into a mocked LLM reply and the validator rejects it and falls back.
- [ ] Banned phrasings are rejected: "never thanked", "influential", "friends with", and any wealth or capacity inference from a career change (G4, G5, G6).
- [ ] Missing data is described as missing, for example "No stewardship interaction is recorded".
- [ ] A prompt-injection test (an interaction note that says to ignore instructions) does not change output.
- [ ] With no API key or a simulated outage, every card still shows a correct template explanation.
- [ ] Golden-file tests cover Valerie Kaur (THANK) and any other cast member whose detector has merged.
- [ ] The service exposes one interface that Ask Sam and Community View reuse.

## Blocked by

- Blocked by `issues/005-relationship-view-evidence-card.md`

## User stories addressed

The PRD has no numbered user stories, so requirement IDs and success criteria from `issues/prd.md` are cited instead.

- Requirements: Section 13 (AI vs deterministic), G4, G5, G6
- Success criteria: SC2
