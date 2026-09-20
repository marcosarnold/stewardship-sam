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
