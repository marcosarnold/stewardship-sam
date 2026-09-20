# 001: Data layer and Stewardship Gap on Today (THANK)

**Type:** AFK

## Parent PRD

`issues/prd.md`

## What to build

Tracer bullet through every layer. Set up the project (PRD section 14 suggests FastAPI, DataFrames or SQLite via the provided `schema.sql` and `load_sqlite.py`, and React/Next.js), create the single configuration module holding every constant from PRD Appendix A, normalize the data, define the shared `Signal` record that every later detector returns (entity type and id, signal id, action, evidence list, urgency fields, channel hint), implement SIG1, expose `GET /api/today`, and render a minimal Today page.

The Today page lists THANK items with 1 to 3 evidence points each and a "View relationship" link. Order by gift amount for now; real ranking arrives in `issues/007-priority-queue-and-dismissal.md`. The link target may be a stub until `issues/005-relationship-view-evidence-card.md`.

## Acceptance criteria

- [ ] One config module holds every Appendix A constant, including `AS_OF_DATE`. No other file hard-codes a threshold, and no code reads the system clock for "today".
- [ ] Normalization keeps only individuals who are not deceased, and only gifts with `status = paid` and `gift_type != recurring_parent`. Unit tests cover each rule.
- [ ] SIG1 returns 1,508 signals for the 1,530 individuals with a recent gift (Appendix B).
- [ ] Tests cover a gift exactly 365 days before `AS_OF_DATE` (recent) and a stewardship interaction dated the same day as the gift (counts as subsequent).
- [ ] Valerie Kaur (constituent 2669) appears as THANK with evidence "$25,000 gift on Feb 4, 2026" and "No stewardship interaction is recorded since the gift".
- [ ] No text anywhere says a donor "was never thanked" (G4).
- [ ] `GET /api/today` returns the signals as JSON, and the Today page renders action label and evidence for each.
- [ ] Missing values render as "Not on file", never as blanks or guesses (G4).
- [ ] A README explains how to run the backend, the frontend, and the tests.

## Blocked by

None - can start immediately

## User stories addressed

The PRD has no numbered user stories, so requirement IDs and success criteria from `issues/prd.md` are cited instead.

- Requirements: SIG1, ACT1, UX1 (initial version), G4
- Success criteria: SC1, SC2
