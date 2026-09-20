from app.config import TIMELINE_PAGE_SIZE
from app.timeline import build_timeline


def _timeline(entity_id, gifts, interactions, events, event_attendance, career_history, opportunities, **kwargs):
    return build_timeline(
        entity_id,
        gifts=gifts,
        interactions=interactions,
        events=events,
        event_attendance=event_attendance,
        career_history=career_history,
        opportunities=opportunities,
        **kwargs,
    )


def test_valerie_kaur_timeline_shows_feb_gift_and_no_interactions_recorded(
    gifts, interactions, events, event_attendance, career_history, opportunities
):
    timeline = _timeline(2669, gifts, interactions, events, event_attendance, career_history, opportunities)

    gift_entries = [e for e in timeline["entries"] if e["type"] == "gift"]
    assert any(e["date"] == "2026-02-04" and "25,000" in e["headline"] for e in gift_entries)
    assert timeline["counts"]["interaction"] == 0


def test_isaac_chen_timeline_shows_the_broken_commitment_history_in_order(
    gifts, interactions, events, event_attendance, career_history, opportunities
):
    timeline = _timeline(2548, gifts, interactions, events, event_attendance, career_history, opportunities)

    interaction_dates = [e["date"] for e in timeline["entries"] if e["type"] == "interaction"]
    expected = ["2026-07-22", "2026-06-13", "2026-05-15", "2026-03-18"]
    for date in expected:
        assert date in interaction_dates

    # Newest first.
    positions = [interaction_dates.index(date) for date in expected]
    assert positions == sorted(positions)


def test_type_filter_narrows_entries_and_counts_describe_the_full_history(
    gifts, interactions, events, event_attendance, career_history, opportunities
):
    timeline = _timeline(
        2548, gifts, interactions, events, event_attendance, career_history, opportunities, types=["gift"]
    )

    assert all(e["type"] == "gift" for e in timeline["entries"])
    assert timeline["counts"]["interaction"] > 0  # counts reflect the full history, not the filter


def test_empty_type_reports_zero_count(gifts, interactions, events, event_attendance, career_history, opportunities):
    timeline = _timeline(
        2669, gifts, interactions, events, event_attendance, career_history, opportunities, types=["interaction"]
    )

    assert timeline["entries"] == []
    assert timeline["counts"]["interaction"] == 0


def test_career_change_entry_uses_neutral_wording(
    gifts, interactions, events, event_attendance, career_history, opportunities
):
    timeline = _timeline(2669, gifts, interactions, events, event_attendance, career_history, opportunities)

    career_entries = [e for e in timeline["entries"] if e["type"] == "career_change"]
    assert len(career_entries) == 1
    headline = career_entries[0]["headline"]
    assert headline.startswith("Started as")
    for banned in ("wealth", "capacity", "rich", "afford"):
        assert banned not in headline.lower()
        assert banned not in (career_entries[0]["detail"] or "").lower()


def test_interaction_entries_carry_the_significant_flag(
    gifts, interactions, events, event_attendance, career_history, opportunities
):
    timeline = _timeline(2548, gifts, interactions, events, event_attendance, career_history, opportunities)

    interaction_entries = [e for e in timeline["entries"] if e["type"] == "interaction"]
    assert any(e["significant"] is True for e in interaction_entries)
    assert any(e["significant"] is False for e in interaction_entries)


def test_busiest_timeline_paginates_and_does_not_return_everything_at_once(
    gifts, interactions, events, event_attendance, career_history, opportunities
):
    from collections import Counter

    tally = Counter(gifts["constituent_id"]) + Counter(interactions["constituent_id"])
    tally += Counter(event_attendance["constituent_id"])
    tally += Counter(career_history["constituent_id"])
    tally += Counter(opportunities["constituent_id"])
    busiest_id, busiest_count = tally.most_common(1)[0]
    assert busiest_count > TIMELINE_PAGE_SIZE

    first_page = _timeline(
        int(busiest_id), gifts, interactions, events, event_attendance, career_history, opportunities, page=1
    )
    assert len(first_page["entries"]) == TIMELINE_PAGE_SIZE
    assert first_page["has_more"] is True

    second_page = _timeline(
        int(busiest_id), gifts, interactions, events, event_attendance, career_history, opportunities, page=2
    )
    assert len(second_page["entries"]) == busiest_count - TIMELINE_PAGE_SIZE
    assert second_page["has_more"] is False
