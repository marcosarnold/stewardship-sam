from app.communities import find_community, get_community_members, list_communities
from app.db import load_table
from app.graph import build_graph

_graph = None


def graph():
    global _graph
    if _graph is None:
        _graph = build_graph()
    return _graph


def test_79_communities_are_eligible():
    communities = list_communities(graph())

    eligible = [c for c in communities if c["eligible"]]
    assert len(eligible) == 79


def test_alumni_board_has_180_eligible_members():
    communities = list_communities(graph())

    alumni_board = next(c for c in communities if c["name"] == "Alumni Board")
    assert alumni_board["member_count"] == 180
    assert alumni_board["eligible"] is True


def test_members_exclude_organizations_and_deceased():
    community = find_community(graph(), "alumni-board")

    all_members = []
    page = 1
    while True:
        chunk = get_community_members(graph(), community["id"], page=page)
        all_members.extend(chunk["members"])
        if not chunk["has_more"]:
            break
        page += 1

    assert len(all_members) == 180  # matches Appendix B's eligible-member count exactly

    constituents = load_table("constituents")
    ids = {m["entity_id"] for m in all_members}
    matched = constituents[constituents["id"].isin(ids)]
    assert (matched["entity_type"] == "individual").all()
    assert (matched["deceased"] == 0).all()


def test_members_endpoint_paginates():
    result = get_community_members(graph(), "alumni-board", page=1)

    assert len(result["members"]) == 50  # COMMUNITY_MEMBERS_PAGE_SIZE
    assert result["has_more"] is True
    assert result["total"] == 180


def test_unknown_community_returns_none():
    assert get_community_members(graph(), "not-a-real-community", page=1) is None
    assert find_community(graph(), "not-a-real-community") is None


def test_edge_note_says_shared_context_not_friendship():
    result = get_community_members(graph(), "alumni-board", page=1)

    note = result["note"].lower()
    assert "shared institutional context" in note
    assert "not a direct social relationship or friendship" in note
