from app.signals.community_cooling import detect


def test_12_communities_are_cooling_including_alumni_board(context):
    signals = detect(context)

    assert len(signals) == 12
    alumni = next(s for s in signals if s.entity_name == "Alumni Board")
    assert alumni.entity_type == "community"
    assert alumni.evidence[0] == "59% ever gave -> 9% gave in the past year"
    assert alumni.evidence[1] == "21% had an interaction in the last two years"


def test_action_is_never_re_engage(context):
    signals = detect(context)

    for signal in signals:
        assert signal.action != "RE-ENGAGE"
        assert signal.action in ("RECONNECT", "INVITE", "ADVOCATE")


def test_high_historical_and_steady_recent_giving_is_not_flagged(context, monkeypatch):
    """A community with strong historical giving whose recent giving kept
    pace (a high recent-to-historical ratio) should never be flagged,
    even though its historical rate alone would clear the median gate.
    """
    from app import community_metrics as cm

    real_compute = cm.compute_all_metrics

    def steady_metrics(graph, gifts, interactions, event_attendance, staff, force_rebuild=False):
        result = real_compute(graph, gifts, interactions, event_attendance, staff, force_rebuild=True)
        # Alumni Board, real-world cooling, is made steady here: recent
        # giving now matches historical giving almost exactly.
        result["alumni-board"] = {
            **result["alumni-board"],
            "historical_giving_rate": 0.9,
            "recent_giving_rate": 0.85,
            "recent_to_historical_ratio": round(0.85 / 0.9, 4),
        }
        return result

    monkeypatch.setattr(cm, "compute_all_metrics", steady_metrics)
    import app.signals.community_cooling as module

    monkeypatch.setattr(module, "compute_all_metrics", steady_metrics)

    signals = detect(context)
    assert not any(s.entity_name == "Alumni Board" for s in signals)
