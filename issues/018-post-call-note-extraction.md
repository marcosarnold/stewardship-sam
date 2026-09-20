# 018: Post-call note extraction (voice optional)

**Type:** AFK

## Parent PRD

`issues/prd.md`

## What to build

Optional. Let a fundraiser dictate or type a post-call note on the Relationship View and turn it into structured relationship memory: interest, communication preference, solicitation status, and follow-up date (Section 15). Transcription uses a configurable provider or the browser speech API, and typed notes work with no audio at all. The extraction returns strict JSON, unsupported fields stay null, and the fundraiser reviews and edits before anything is saved.

Saved memory appears on the Relationship View and has effects. A solicitation status of "not currently interested" is read by the policy engine from `issues/002-contact-policy-wait.md` and blocks ASK. A follow-up date becomes a tracked commitment that SIG2 from `issues/003-broken-commitment-follow-up.md` evaluates. Use the PRD's example note as the test fixture. Depends on the confirmation and outcome flow from `issues/017-action-preparation-confirmation.md`.

## Acceptance criteria

- [ ] The PRD example note produces: interest = Boston alumni events, communication preference = text, solicitation status = not currently interested, follow-up = November.
- [ ] Nothing is saved until the fundraiser confirms the extracted fields.
- [ ] Missing information stays null and is never guessed (G4).
- [ ] "Not currently interested" makes `evaluate_contact` block ASK for that person, with a test.
- [ ] A saved follow-up date is picked up by SIG2 once due and unresolved.
- [ ] A visible indicator shows whenever audio is being recorded, and typed input works without microphone permission.
- [ ] The text preference is stored even though text outreach is unsupported in the dataset, and is labeled as a preference only.

## Blocked by

- Blocked by `issues/002-contact-policy-wait.md`
- Blocked by `issues/003-broken-commitment-follow-up.md`
- Blocked by `issues/017-action-preparation-confirmation.md`

## User stories addressed

The PRD has no numbered user stories, so requirement IDs and success criteria from `issues/prd.md` are cited instead.

- Requirements: Section 15, Section 16, G1, G4
- Success criteria: SC3 (optional feature)
