# 002: Contact policy and WAIT (Contact Pressure)

**Type:** AFK

## Parent PRD

`issues/prd.md`

## What to build

Build the contact policy engine as a pure, reusable function, `evaluate_contact(constituent, proposed_action, proposed_channel)`, returning allowed, suppressed, or wait plus machine-readable reasons. Implement SIG5 on top of it.

Rules (constants in Appendix A): deceased and `do_not_solicit` block outreach; a call needs `phone_status = available`; an email needs `email_status = deliverable`; text is unsupported because the dataset has no phone numbers or text history; any outbound interaction within `RECENT_CONTACT_SUPPRESSION_DAYS` suppresses new THANK, RECONNECT, INVITE, and ASK; `CONTACT_PRESSURE_MIN_OUTBOUND` or more outbound interactions within `CONTACT_PRESSURE_WINDOW_DAYS` produces a WAIT signal; an already scheduled future follow-up is noted as a reason.

Apply the policy to the THANK signals from `issues/001-data-layer-stewardship-gap-today.md`. Suppressed signals leave the Today list and appear in a collapsed "Held back today" section with reasons. WAIT signals appear on Today with evidence. Each signal also carries the recommended allowed channel.

## Acceptance criteria

- [ ] Kieran Kaur (12022) appears as WAIT with evidence "5 outbound interactions in the last 60 days" and the most recent date. No THANK is shown for him.
- [ ] Exactly 8 people trigger contact pressure (Appendix B).
- [ ] Valerie Kaur's recommended channel is email, and the evidence says her phone is marked do-not-call (G1).
- [ ] `evaluate_contact` is a pure function with unit tests for: deceased, `do_not_solicit` blocking any solicitation, `do_not_call`, inactive or missing email, the 14-day suppression, the boundary at exactly 60 days and exactly 3 interactions, and an overdue FOLLOW UP being exempt from the 14-day suppression.
- [ ] Every suppressed or WAIT decision carries a reason code and a human-readable reason.
- [ ] Today shows a collapsed "Held back today" list with counts by reason, and each entry links to the person.
- [ ] Docs state that restriction flags are a current snapshot, so past outreach may appear to conflict with them (Appendix C item 8).

## Blocked by

- Blocked by `issues/001-data-layer-stewardship-gap-today.md`

## User stories addressed

The PRD has no numbered user stories, so requirement IDs and success criteria from `issues/prd.md` are cited instead.

- Requirements: SIG5, ACT8, G1, G2
- Success criteria: SC8
