# Stewardship Sam

Relationship intelligence agent for the GiveCampus HackMIT challenge. Core question: where should I spend Tuesday?

## Sources of truth

- `issues/prd.md`: the PRD. Appendix A holds the frozen constants, Appendix B the verified data facts and demo cast, Appendix C the changes from the original PDF. Where an appendix conflicts with the body, the appendix wins.
- `issues/001` to `issues/019`: implementation slices. Each lists its blockers and acceptance criteria.
- `20260919_GiveCampus_MIT_Hackathon/`: GiveCampus data (CSVs in `data/`, plus `schema.sql`, `load_sqlite.py`, and the data dictionary). The backend builds a SQLite database from this automatically; see `backend/app/db.py`.

## Hard rules

- All thresholds and windows live in one config module (PRD Appendix A). Never hard-code them anywhere else.
- "Today" is `AS_OF_DATE` (2026-08-31). Never read the system clock.
- Population: individuals who are not deceased. Gifts: `status = paid` and `gift_type != recurring_parent`.
- Sam never sends messages, calls, solicits, or changes assignments. A fundraiser confirms every donor-facing action.
- Missing data is shown as missing ("Not on file", "No interaction is recorded"). Never write "never thanked" or "was never contacted".
- Never call anyone "influential" or "friends with" anyone. A career change is never evidence of wealth or capacity.
- The LLM never sees the raw dataset. It receives structured evidence only. Every LLM feature has a deterministic fallback and a mockable client.
- No opaque numeric relationship score in the UI. Show the evidence that caused a recommendation.
- Explicit contact restrictions (do-not-solicit, do-not-call, deceased) override every recommendation.
- Contact-restriction flags are a current snapshot: past outreach may appear to conflict with them. Treat that as a data caveat, not evidence of a violation (Appendix C item 8).

## Stack (PRD section 14)

FastAPI, pandas or SQLite (built with `load_sqlite.py`), NetworkX, React/Next.js, Cytoscape or D3, OpenAI.

## Workflow

- One issue at a time. Check its "Blocked by" list first and stop if a blocker is not done.
- Give a short plan and wait for approval before writing code.
- Work test-first: write failing tests for the acceptance criteria, then implement.
- Tick a checkbox in the issue file only when a test or manual check proves it.
- Stop at each human checkpoint in HITL issues (013 and 019) and ask before continuing.
- When finished, summarize what changed, how each criterion was verified, and any place the PRD conflicted with the data.

## Demo cast (for fixtures and tests)

| Person | ID | Expected behavior |
| --- | --- | --- |
| Valerie Kaur | 2669 | THANK, email is the allowed channel |
| Nia Chen | 14456 | FOLLOW UP, the only unresolved commitment |
| Isaac Chen | 2548 | No action; his May 15 commitment was kept |
| Kieran Kaur | 12022 | WAIT, 5 outbound interactions in 60 days |
| Alumni Board | n/a | Cooling community |

## Commands

- Backend: `cd backend && .venv/bin/uvicorn app.main:app --reload --port 8000`
- Backend tests: `cd backend && .venv/bin/pytest`
- Frontend: `cd frontend && npm run dev` (needs `NEXT_PUBLIC_API_BASE_URL` in `.env.local`, see root README)
- Frontend build/typecheck: `cd frontend && npm run build`

See the root `README.md` for full setup instructions.