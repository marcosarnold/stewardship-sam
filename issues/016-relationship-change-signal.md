# 016: Relationship Change signal (career, events, gifts, affiliations, opportunities)

**Type:** AFK

## Parent PRD

`issues/prd.md`

## What to build

Implement SIG4 as a new detector registered with the queue from `issues/007-priority-queue-and-dismissal.md`. A change is recent when it falls within `RELATIONSHIP_CHANGE_WINDOW_DAYS`: a new role in `career_history`, event attendance, a new received gift, a changed affiliation, or a new opportunity. Recommend RECONNECT, or INVITE when an upcoming event exists. Evidence is neutral ("Started as ... at ... in June") and shown in the Relationship View from `issues/005-relationship-view-evidence-card.md`. A career change is a reason to reconnect, never evidence of wealth (G6). A new gift alone does not duplicate SIG1's THANK.

## Acceptance criteria

- [ ] People with a career change in the last 180 days surface with neutral evidence.
- [ ] A test confirms a career change alone never produces ASK and evidence text never mentions wealth, capacity, or likelihood to give (G6).
- [ ] INVITE is used only when an upcoming event exists; otherwise RECONNECT.
- [ ] Duplicate signals for a person merge into one queue item (relies on slice 007).
- [ ] Policy checks apply, so restricted or recently contacted people are held back with a reason.
- [ ] The window comes from the config module, and the number of detected people is reported in the README.

## Blocked by

- Blocked by `issues/001-data-layer-stewardship-gap-today.md`
- Blocked by `issues/005-relationship-view-evidence-card.md`
- Blocked by `issues/007-priority-queue-and-dismissal.md`

## User stories addressed

The PRD has no numbered user stories, so requirement IDs and success criteria from `issues/prd.md` are cited instead.

- Requirements: SIG4, ACT3, ACT5, G6
- Success criteria: SC1, SC3
