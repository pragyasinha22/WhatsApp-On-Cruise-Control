import json

from agent.router import resolve_relationship


def create_test_map(tmp_path):
    map_file = tmp_path / "relationship_map.json"

    relationship_map = {
        "_default": "unknown",
        "919812345670": "friend",
        "919812345671": "family",
        "919812345672": "professional",
    }

    map_file.write_text(
        json.dumps(relationship_map),
        encoding="utf-8",
    )

    return str(map_file)


def test_known_number_resolves_correctly(tmp_path):
    map_path = create_test_map(tmp_path)

    relationship, collection = resolve_relationship(
        "919812345670@s.whatsapp.net",
        map_path,
    )

    assert relationship == "friend"
    assert collection == "history_friend"


def test_unknown_number_uses_default(tmp_path):
    map_path = create_test_map(tmp_path)

    relationship, collection = resolve_relationship(
        "919999999999@s.whatsapp.net",
        map_path,
    )

    assert relationship == "unknown"
    assert collection == "history_unknown"


def test_group_jid_never_uses_relationship_map(tmp_path):
    map_path = create_test_map(tmp_path)

    relationship, collection = resolve_relationship(
        "120363012345678901@g.us",
        map_path,
    )

    assert relationship == "group"
    assert collection is None


def test_empty_jid_returns_safe_fallback(tmp_path):
    map_path = create_test_map(tmp_path)

    relationship, collection = resolve_relationship(
        "",
        map_path,
    )

    assert relationship == "unknown"
    assert collection == "history_unknown"


def test_malformed_jid_returns_safe_fallback(tmp_path):
    map_path = create_test_map(tmp_path)

    relationship, collection = resolve_relationship(
        "not-a-valid-jid",
        map_path,
    )

    assert relationship == "unknown"
    assert collection == "history_unknown"