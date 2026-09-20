# Stewardship Sam

Relationship intelligence agent for the GiveCampus HackMIT challenge. Core question: where should I spend Tuesday?

## Start here

- `issues/prd.md` is the canonical PRD, with stable IDs (SC, SIG, ACT, UX, G, AQ) and three appendices: frozen constants, verified data facts, and a change log.
- `issues/001` to `issues/019` are the implementation slices. Each names its blockers, so pick any issue whose blockers are done.

## Build order

| Track | Issues |
| --- | --- |
| Foundation | 001, then 002 / 003 / 004 in parallel, then 007 |
| Individual UX | 005, then 006 and 008 |
| Community | 009, then 010, then 011; 012 in parallel from 009; 013 needs 011 and 012 |
| Copilot | 014, then 015 |
| Enhancement | 016, then 017 (first cut if short on time), 018 optional |
| Finish | 019 |

## Using it with an AI coding agent

Point the agent at one issue file and `issues/prd.md`, for example: "Implement issues/001-data-layer-stewardship-gap-today.md. The parent PRD is issues/prd.md. Constants come from Appendix A."

## Data

The GiveCampus hackathon dataset (CSVs, `schema.sql`, `load_sqlite.py`) lives in `20260919_GiveCampus_MIT_Hackathon/`. The backend builds a SQLite database from it automatically on first run (`20260919_GiveCampus_MIT_Hackathon/givecampus_hackmit.sqlite`, gitignored); delete that file to force a rebuild.

## Running the app

Requires Python 3.11+ and Node 18+.

### Backend (FastAPI)

```sh
cd backend
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/uvicorn app.main:app --reload --port 8000
```

`GET http://localhost:8000/api/today` returns the Today queue as JSON.

Explanations (`explain()`, see `backend/app/explain/`) use OpenAI when `OPENAI_API_KEY` is set in the environment; unset or unreachable, every card falls back to a deterministic template automatically. No key is required to run or test the app.

Dismissing a Today item (`POST /api/today/{id}/dismiss`) is persisted to `backend/var/dismissals.json` (gitignored); delete that file to clear all dismissals.

`GET /api/relationships/{id}/timeline` returns that person's gifts, interactions, events attended, career changes, and opportunities, newest first, with `types` and `page` query params.

`GET /api/communities` and `GET /api/communities/{id}/members` expose the NetworkX relationship graph's communities (an activity with at least `COMMUNITY_MIN_MEMBERS` eligible members). The graph is built once at startup and cached; an edge is shared institutional context, such as a common activity, never a direct social relationship or friendship (G5).

SIG4 (Relationship Change) detects 2,184 people with a career change, event attendance, changed affiliation, or new opportunity within `RELATIONSHIP_CHANGE_WINDOW_DAYS` (180 days) of `AS_OF_DATE`; a new gift alone never triggers it, since that is SIG1's job. 2,147 of those pass contact policy and appear on Today as RECONNECT or INVITE.

### Frontend (Next.js)

```sh
cd frontend
npm install
echo "NEXT_PUBLIC_API_BASE_URL=http://localhost:8000" > .env.local
npm run dev
```

Open http://localhost:3000. The Today page fetches `/api/today` from the backend above.

### Tests

```sh
cd backend
.venv/bin/pytest
```

```sh
cd frontend
npm run build   # type-checks and builds
```

## Demo

1. Start the backend and frontend as above (two terminals).
2. Reset to a clean, deterministic state before rehearsing or presenting: `curl -X POST http://localhost:8000/api/demo/reset` (or `.venv/bin/python -m app.demo_reset` from `backend/`). This clears dismissals, recorded action outcomes, and saved post-call notes, and rebuilds the graph/metrics caches fresh.
3. Walk the script (PRD Section 23, Appendix C): open Today → FOLLOW UP with Nia Chen, and open Isaac Chen's Relationship View as the control whose May 15 commitment was kept → THANK with Valerie Kaur → WAIT with Kieran Kaur → ask Sam "Which communities are we losing touch with?" → open Alumni Board's Community View for its network and connectors → close back on Today.
4. `tests/test_demo_path.py` runs this same walk against the API automatically (`.venv/bin/pytest tests/test_demo_path.py`), and `tests/test_demo_performance.py` / `tests/test_demo_llm_outage.py` verify the performance budget and that everything still works with no `OPENAI_API_KEY` set.

No `OPENAI_API_KEY` is required to run the demo: every explanation, Ask Sam answer, and note extraction has a deterministic fallback (see `backend/app/explain/`, `backend/app/ask_sam/intent.py`, `backend/app/relationship_notes.py`).
