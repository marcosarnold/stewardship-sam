from app.signals import contact_pressure, stewardship_gap


def test_sig5_matches_appendix_b_count(context):
    signals = contact_pressure.detect(context)

    assert len(signals) == 8


def test_kieran_kaur_surfaces_as_wait_with_expected_evidence(context):
    signals = contact_pressure.detect(context)
    by_id = {s.entity_id: s for s in signals}

    kieran = by_id[12022]

    assert kieran.action == "WAIT"
    assert kieran.evidence[0] == "5 outbound interactions in the last 60 days"
    assert kieran.evidence[1] == "Most recent: Aug 19, 2026"


def test_kieran_kaur_has_no_thank_signal(context):
    thank_signals = stewardship_gap.detect(context)

    assert all(s.entity_id != 12022 for s in thank_signals)
