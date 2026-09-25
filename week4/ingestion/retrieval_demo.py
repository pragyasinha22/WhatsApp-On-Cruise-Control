
from ingestion.retrieval import retrieve_similar


QUERIES = {
    "family": [
        "Babu khana kha liya?",
        "Sunday ko ghar aaogi?",
    ],
    "friend": [
        "Movie ka plan hai kya?",
        "Yaar ye photo dekh 😂",
    ],
}


def run_demo():
    for relationship, queries in QUERIES.items():
        for query in queries:
            print()
            print("=" * 70)
            print(f"Relationship: {relationship}")
            print(f"Query: {query}")
            print("=" * 70)

            results = retrieve_similar(
                relationship,
                query,
                k=3,
            )

            if not results:
                print("No results found.")
                continue

            previous_distance = None

            for index, result in enumerate(results, start=1):
                print()
                print(f"Result {index}")
                print(f"Distance: {result['distance']:.3f}")
                print(f"Their message: {result['their_message']}")
                print(f"My reply: {result['my_reply']}")

                if previous_distance is not None:
                    if result["distance"] < previous_distance:
                        print("⚠️ Distance ordering issue detected.")

                previous_distance = result["distance"]

            distances = [result["distance"] for result in results]

            if distances == sorted(distances):
                print()
                print("✅ Distance sanity check: results are ordered correctly.")
            else:
                print()
                print("⚠️ Distance sanity check failed.")

    for relationship in ["professional", "unknown"]:
        try:
            results = retrieve_similar(
                relationship,
                "Test query",
                k=3,
            )
        except Exception as exc:
            print(f"\n⚠️ Could not retrieve {relationship}: {exc}")
            continue

        if not results:
            print(f"\n⚠️ history_{relationship} is empty. Skipping.")


if __name__ == "__main__":
    run_demo()

