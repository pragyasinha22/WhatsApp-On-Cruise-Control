import json
import os

from google import genai
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

with open("persona/persona.json", "r", encoding="utf-8") as f:
    persona = json.load(f)

# test_prompts = [
#     ("friends", "I am going to be late today, can you pick me up?"),
#     ("family", "Diwali pe ghar aaoge kya?"),
#     ("professional", "I have a new video ready. When can we connect?"),
# ]
test_prompts = [
    ("friends", "I am going to be late today, can you pick me up?"),
    ("family", "Diwali pe ghar aaoge kya?"),
    ("professional", "I have a new video ready. When can we connect?"),
    ("friends", "Coffee chale this evening?"),
    ("family", "Dinner mein kya khana hai?"),
]

for relationship, incoming in test_prompts:
    tone = persona["relationships"][relationship]["tone"]
    examples = persona["relationships"][relationship]["example_replies"]

    prompt = f"""You are texting as: {persona['identity']}
Tone for {relationship}: {tone}
Example replies in this tone: {examples}
Hinglish ratio to match: {persona['hinglish_ratio']}
Incoming message: "{incoming}"
Reply in character, one short WhatsApp-style message only."""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    print(f"[{relationship}] {incoming} -> {response.text.strip()}")