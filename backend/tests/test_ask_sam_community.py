import pandas as pd

from app.ask_sam.executor import cooling_communities_query, location_activity_query
from app.ask_sam.intent import INTENT_COOLING_COMMUNITIES, INTENT_LOCATION_ACTIVITY, extract_intent
from app.ask_sam.service import ask
from app.db import load_table
from app.normalize import population
from app.signals.community_cooling import detect as detect_cooling


def test_aq3_returns_the_same_12_communities_as_today(context):
    results = cooling_communities_query(context)
    today_cooling = detect_cooling(context)

    assert {r["community_id"] for r in results} == {s.entity_id for s in today_cooling}
    assert len(results) == 12
    assert any(r["community_name"] == "Alumni Board" for r in results)


def test_aq3_is_ordered_by_decline_ratio_worst_first(context):
    results = cooling_communities_query(context)

    ratios = [r["recent_to_historical_ratio"] for r in results]
    assert ratios == sorted(ratios)


def test_aq6_count_matches_a_direct_query(context):
    results = location_activity_query("Boston", "Athletics", context)

    constituents = load_table("constituents")
    activities = load_table("activities")
    pop = population(constituents)
    boston = pop[(pop["city"] == "Boston") & (pop["state"] == "MA")]
    athletics_ids = set(activities[activities["activity_type"] == "Athletics"]["constituent_id"])
    expected = boston[boston["id"].isin(athletics_ids)]

    assert results["status"] == "found"
    assert len(results["people"]) == len(expected)


def test_aq6_each_person_shows_the_connecting_communities(context):
    results = location_activity_query("Boston", "Athletics", context)

    for person in results["people"]:
        assert len(person["communities"]) > 0
        for name in person["communities"]:
            assert "Varsity" in name  # every Athletics activity in this dataset is a Varsity team


def test_aq6_unmatched_location_returns_a_clear_message(context):
    results = location_activity_query("Nowhereville", "Athletics", context)

    assert results["status"] == "no_location_matches"
    assert results["people"] == []


def test_intent_extraction_for_aq3_and_aq6():
    assert extract_intent("Which communities are losing engagement?") == {"intent": INTENT_COOLING_COMMUNITIES}
    assert extract_intent("Show Boston alumni connected to athletics.") == {
        "intent": INTENT_LOCATION_ACTIVITY,
        "city": "boston",
        "activity_type": "athletics",
    }


def test_schema_validator_rejects_unsupported_intent():
    class FakeClient:
        def complete(self, system_prompt, user_prompt):
            return '{"intent": "DELETE_EVERYTHING"}'

    # Falls through to the keyword fallback, which also won't match this
    # nonsense question -- proving the invalid LLM intent was rejected.
    assert extract_intent("asdkjaslkdj random text", client=FakeClient()) is None


def test_ask_aq3_and_aq6_link_and_are_grounded(context, degrees, activities, affiliations):
    cooling = ask("Which communities are losing engagement?", context, degrees, activities, affiliations)
    assert cooling["intent"] == INTENT_COOLING_COMMUNITIES
    assert cooling["results"]
    for r in cooling["results"]:
        assert r["community_id"]  # usable to link to /community/{id}

    boston = ask("Show Boston alumni connected to athletics.", context, degrees, activities, affiliations)
    assert boston["intent"] == INTENT_LOCATION_ACTIVITY
    assert boston["results"]["status"] == "found"
    for p in boston["results"]["people"]:
        assert p["entity_id"]  # usable to link to /relationship/{id}
