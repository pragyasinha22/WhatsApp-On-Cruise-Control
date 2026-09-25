import json


VALID_RELATIONSHIPS = {
    "family",
    "friend",
    "professional",
    "unknown",
}


def resolve_relationship(
    jid: str,
    map_path: str = "config/relationship_map.json",
) -> tuple[str, str | None]:
    # Empty or malformed JID should safely fall back to unknown.
    if not jid or "@" not in jid:
        return "unknown", "history_unknown"

    # Groups are NEVER looked up in the relationship map.
    if jid.endswith("@g.us"):
        return "group", None

    # Works for both @s.whatsapp.net and @lid.
    number = jid.split("@", 1)[0]

    try:
        with open(map_path, encoding="utf-8") as f:
            relationship_map = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return "unknown", "history_unknown"

    relationship = relationship_map.get(
        number,
        relationship_map.get("_default", "unknown"),
    )

    # Protect against an invalid relationship value in the map.
    if relationship not in VALID_RELATIONSHIPS:
        relationship = "unknown"

    return relationship, f"history_{relationship}"