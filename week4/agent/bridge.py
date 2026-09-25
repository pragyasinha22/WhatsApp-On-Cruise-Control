from datetime import datetime, timezone
import json
from pathlib import Path

from flask import Flask, jsonify, request

from agent.router import resolve_relationship
from agent.decision_engine import should_reply
from agent.generator import generate_reply
from ingestion.retrieval import retrieve_similar

app = Flask(__name__)

LOG_PATH = Path("logs/console_feed.jsonl")


def append_console_log(
    jid: str,
    relationship: str,
    decision: str,
    reason: str,
    reply: str | None,
    retrieval_trace: list,
) -> None:
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "jid": jid,
        "relationship": relationship,
        "decision": decision,
        "reason": reason,
        "reply": reply,
        "retrieval_trace": retrieval_trace,
    }

    with LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


@app.post("/process")
def process_message():
    data = request.get_json(silent=True) or {}

    jid = data.get("jid", "")
    text = data.get("text", "")
    message_type = data.get("message_type", "text")
    is_forwarded = bool(data.get("is_forwarded", False))
    from_me = bool(data.get("from_me", False))

    relationship, _ = resolve_relationship(jid)

    message = {
        "jid": jid,
        "text": text,
        "message_type": message_type,
        "is_forwarded": is_forwarded,
        "from_me": from_me,
    }

    should_send, reason = should_reply(message, relationship)

    reply = None
    retrieval_trace = []

    if reason == "media_ack":
        should_send = True

        media_replies = {
            "image": "Got your image, will look at it properly and get back to you 🙂",
            "audio": "Got your voice note, will listen to it properly and get back to you 🙂",
            "video": "Got your video, will look at it properly and get back to you 🙂",
        }

        reply = media_replies.get(
            message_type,
            "Got it, will check it properly and get back to you 🙂",
        )

    elif should_send:
        try:
            retrieval_trace = retrieve_similar(
                relationship,
                text,
                k=3,
            )
        except Exception:
            retrieval_trace = []

        reply = generate_reply(text, relationship)

    append_console_log(
        jid=jid,
        relationship=relationship,
        decision="reply" if should_send else "ignore",
        reason=reason,
        reply=reply,
        retrieval_trace=retrieval_trace,
    )

    return jsonify(
        {
            "should_reply": should_send,
            "reply": reply,
            "relationship": relationship,
            "reason": reason,
        }
    )


if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5001,
        debug=False,
    )