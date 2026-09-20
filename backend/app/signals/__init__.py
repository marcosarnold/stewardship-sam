"""Importing this package registers every detector with app.registry.

A new detector (SIG4, SIG6, ...) just needs a line here -- no other
file changes to start appearing on Today (see app/priority_queue.py).
"""

from app.signals import (  # noqa: F401
    broken_commitment,
    community_cooling,
    contact_pressure,
    neglected_relationship,
    relationship_change,
    stewardship_gap,
)
