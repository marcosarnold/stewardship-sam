"""Returns the app to a deterministic demo state: dismissals, action
outcomes, and saved relationship memory cleared, and the graph/metrics/
connector caches rebuilt fresh (issue 019).

Run directly: `python -m app.demo_reset` (or POST /api/demo/reset).
"""

from app import connectors as connectors_module
from app import community_metrics as community_metrics_module
from app.action_outcomes import clear_all as clear_action_outcomes
from app.dismissals import clear_all as clear_dismissals
from app.graph import get_graph
from app.relationship_memory import clear_all as clear_relationship_memory


def reset_demo_state() -> dict:
    clear_dismissals()
    clear_action_outcomes()
    clear_relationship_memory()

    connectors_module._CACHE.clear()
    community_metrics_module._METRICS_CACHE = None
    get_graph(force_rebuild=True)

    return {"status": "reset"}


if __name__ == "__main__":
    reset_demo_state()
    print("Demo state reset: dismissals, action outcomes, and relationship memory cleared; caches rebuilt.")
