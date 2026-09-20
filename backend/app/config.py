"""Frozen implementation constants (PRD Appendix A).

Every threshold, window, and "today" reference used anywhere in this
codebase must be imported from here. No other module may hard-code one
of these values or read the system clock.
"""

from datetime import date

# --- Population and dates ---

AS_OF_DATE = date(2026, 8, 31)

POPULATION_ENTITY_TYPE = "individual"

RECEIVED_GIFT_STATUS = "paid"
EXCLUDED_GIFT_TYPE = "recurring_parent"

# --- Signal windows and thresholds ---

RECENT_GIFT_WINDOW_DAYS = 365
STEWARDSHIP_PURPOSES = ("acknowledgement", "stewardship")

CONTACT_PRESSURE_WINDOW_DAYS = 60
CONTACT_PRESSURE_MIN_OUTBOUND = 3

RECENT_CONTACT_SUPPRESSION_DAYS = 14

MAJOR_DONOR_LIFETIME_USD = 10_000

LONG_INTERACTION_GAP_DAYS = 730

RELATIONSHIP_CHANGE_WINDOW_DAYS = 180

RECENT_GIVING_WINDOW_DAYS = 365
RECENT_ENGAGEMENT_WINDOW_DAYS = 730

COMMUNITY_MIN_MEMBERS = 60

TODAY_QUEUE_MAX_ITEMS = 15
COMMUNITY_GRAPH_MAX_NODES = 150
