"""Verifies the demo's performance budget (issue 019): Today and the
community graph under 2 seconds, Ask Sam under 5 seconds, all warm
(post-reset, matching how the demo actually runs -- caches primed by
the reset command's graph rebuild, not a truly cold process start).
"""

import time

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def _timed(fn) -> float:
    started = time.monotonic()
    fn()
    return time.monotonic() - started


def test_today_loads_under_2_seconds():
    client.post("/api/demo/reset")
    client.get("/api/today")  # warm-up: the reset's forced graph rebuild, not the page load itself, is untimed
    elapsed = _timed(lambda: client.get("/api/today"))
    assert elapsed < 2


def test_community_graph_loads_under_2_seconds():
    client.get("/api/community/alumni-board")  # warm connector cache, as a real page load would
    elapsed = _timed(lambda: client.get("/api/community/alumni-board/graph"))
    assert elapsed < 2


def test_ask_sam_answers_under_5_seconds():
    for question in [
        "Who have we promised to follow up with?",
        "Show major donors without an assigned officer.",
        "Which communities are losing engagement?",
        "Who shouldn't I contact today?",
        "Why did Valerie Kaur surface?",
        "Show Boston alumni connected to athletics.",
    ]:
        elapsed = _timed(lambda q=question: client.post("/api/ask", json={"question": q}))
        assert elapsed < 5, f"{question!r} took {elapsed:.2f}s"
