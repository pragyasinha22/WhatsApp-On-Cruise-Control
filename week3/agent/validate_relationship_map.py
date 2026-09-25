import json
import re
import sys
from pathlib import Path


MAP_FILE = Path("config/relationship_map.json")

VALID_RELATIONSHIPS = {
    "family",
    "friend",
    "professional",
    "unknown",
}


def main():
    if not MAP_FILE.exists():
        print(f"❌ File not found: {MAP_FILE}")
        sys.exit(1)

    try:
        with open(MAP_FILE, encoding="utf-8") as f:
            relationship_map = json.load(f)
    except json.JSONDecodeError as exc:
        print(f"❌ Invalid JSON: {exc}")
        sys.exit(1)

    issues = []

    if "_default" not in relationship_map:
        issues.append("Missing _default entry.")
    elif relationship_map["_default"] not in VALID_RELATIONSHIPS:
        issues.append(
            f"Invalid _default value: {relationship_map['_default']}"
        )

    for key, relationship in relationship_map.items():
        if key == "_default":
            continue

        if not re.fullmatch(r"\d+", key):
            issues.append(
                f"Invalid phone-number key '{key}': "
                "must contain digits only."
            )
            continue

        if not 8 <= len(key) <= 15:
            issues.append(
                f"Implausible phone-number length for '{key}': "
                f"{len(key)} digits."
            )

        if relationship not in VALID_RELATIONSHIPS:
            issues.append(
                f"Invalid relationship for '{key}': {relationship}"
            )

    print(f"Checked: {MAP_FILE}")
    print(f"Phone-number entries: {len(relationship_map) - 1}")

    if issues:
        print("\n⚠️ Issues found:")
        for issue in issues:
            print(f"  - {issue}")
        print(f"\n⚠️ Validation failed: {len(issues)} issue(s)")
        sys.exit(1)

    print("\n✅ Relationship map validation passed")


if __name__ == "__main__":
    main()