
import json
import os

from dotenv import load_dotenv
from google import genai

from ingestion.retrieval import retrieve_similar


load_dotenv()

PERSONA_PATH = "persona/persona.json"

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


def load_persona() -> dict:
    with open(PERSONA_PATH, encoding="utf-8") as f:
        return json.load(f)


def generate_reply(
    incoming_text: str,
    relationship: str,
) -> str:
    """Generate a dry-run reply using persona + retrieved history."""

    persona = load_persona()

    try:
        retrieved = retrieve_similar(
            relationship,
            incoming_text,
            k=3,
        )
    except Exception as exc:
        print(f"[generator] Retrieval error: {exc}")
        retrieved = []

    relationship_info = persona.get("relationships", {}).get(
        relationship,
        {},
    )

    tone = relationship_info.get(
        "tone",
        "Natural, concise, and conversational.",
    )

    examples = relationship_info.get("example_replies", [])

    retrieved_examples = []
    for item in retrieved:
        retrieved_examples.append(
            {
                "their_message": item["their_message"],
                "my_reply": item["my_reply"],
            }
        )

    prompt = f"""You are writing a WhatsApp reply in the user's personal style.

PERSONA IDENTITY:
{persona.get("identity", "")}

WORK AND INTERESTS:
{persona.get("work_and_interests", "")}

RELATIONSHIP:
{relationship}

RELATIONSHIP TONE:
{tone}

PERSONA EXAMPLE REPLIES:
{json.dumps(examples, ensure_ascii=False)}

RETRIEVED MESSAGE-REPLY EXAMPLES FROM HISTORY:
{json.dumps(retrieved_examples, ensure_ascii=False)}

STYLE SIGNALS:
Hinglish ratio: {persona.get("hinglish_ratio", 0)}
Typical message length: {persona.get("avg_message_length_words", 0)} words
Top emojis: {json.dumps(persona.get("top_emojis", []), ensure_ascii=False)}

HARD RULES:
{json.dumps(persona.get("hard_rules", []), ensure_ascii=False)}

INCOMING WHATSAPP MESSAGE:
{incoming_text}

Write only the reply message.

Keep it natural, concise, and consistent with the user's style.
Do not explain your reasoning.
Do not add quotation marks.
"""

    try:
        response = client.models.generate_content(
            model="gemini-3.5-flash",
            contents=prompt,
        )

        reply = (response.text or "").strip()

        if reply:
            return reply

    except Exception as exc:
        print(f"[generator] Gemini API error: {exc}")

    return "Sorry, thoda busy hoon abhi. Baad mein reply karti hoon."


if __name__ == "__main__":
    examples = [
        ("Sunday ko ghar aaogi?", "family"),
        ("Movie ka plan hai kya?", "friend"),
        ("Can we connect tomorrow at 10 AM?", "professional"),
    ]

    for incoming_text, relationship in examples:
        print()
        print("=" * 70)
        print(f"Relationship: {relationship}")
        print(f"Incoming: {incoming_text}")

        reply = generate_reply(
            incoming_text,
            relationship,
        )

        print(f"Generated reply: {reply}")
