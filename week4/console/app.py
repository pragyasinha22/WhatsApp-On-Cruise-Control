import json
import os
from pathlib import Path

import streamlit as st
from streamlit_autorefresh import st_autorefresh


BASE_DIR = Path(__file__).resolve().parents[1]

LOG_PATH = BASE_DIR / "logs" / "console_feed.jsonl"
SETTINGS_PATH = BASE_DIR / "config" / "settings.json"
KILL_SWITCH_PATH = BASE_DIR / "kill_switch.flag"

DEFAULT_SETTINGS = {
    "dry_run": True,
    "min_delay_seconds": 3,
    "max_delay_seconds": 12,
}


st.set_page_config(
    page_title="WhatsApp Cruise Control",
    page_icon="💬",
    layout="wide",
)


st_autorefresh(
    interval=2000,
    key="console_refresh",
)


def load_logs(limit=20):
    if not LOG_PATH.exists():
        return []

    records = []

    try:
        with LOG_PATH.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()

                if not line:
                    continue

                try:
                    records.append(json.loads(line))
                except json.JSONDecodeError:
                    continue

    except OSError:
        return []

    return records[-limit:][::-1]


def load_settings():
    try:
        with SETTINGS_PATH.open("r", encoding="utf-8") as f:
            data = json.load(f)

        if not isinstance(data, dict):
            return DEFAULT_SETTINGS.copy()

        settings = DEFAULT_SETTINGS.copy()
        settings.update(data)

        return settings

    except (
        FileNotFoundError,
        json.JSONDecodeError,
        OSError,
        TypeError,
    ):
        return DEFAULT_SETTINGS.copy()


def save_settings(settings):
    SETTINGS_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    temp_path = SETTINGS_PATH.with_suffix(
        ".tmp"
    )

    temp_path.write_text(
        json.dumps(
            settings,
            indent=2,
        ),
        encoding="utf-8",
    )

    os.replace(
        temp_path,
        SETTINGS_PATH,
    )


def relationship_badge(relationship):
    styles = {
        "family": ("🟢", "Family"),
        "friend": ("🔵", "Friend"),
        "professional": ("🟣", "Professional"),
        "unknown": ("⚪", "Unknown"),
        "group": ("⚪", "Group"),
    }

    return styles.get(
        relationship,
        ("⚪", relationship.title()),
    )


def kill_switch_active():
    return KILL_SWITCH_PATH.exists()


def activate_kill_switch():
    KILL_SWITCH_PATH.touch()


def clear_kill_switch():
    try:
        KILL_SWITCH_PATH.unlink()
    except FileNotFoundError:
        pass


st.title("💬 WhatsApp Cruise Control")
st.caption(
    "Live message feed and AI reply decisions"
)


logs = load_logs(limit=20)
settings = load_settings()

dry_run = bool(
    settings.get("dry_run", True)
)

try:
    min_delay = int(
        settings.get(
            "min_delay_seconds",
            3,
        )
    )
except (TypeError, ValueError):
    min_delay = 3

try:
    max_delay = int(
        settings.get(
            "max_delay_seconds",
            12,
        )
    )
except (TypeError, ValueError):
    max_delay = 12


with st.sidebar:
    st.header("Cruise Control")

    st.metric(
        "Messages processed",
        len(logs),
    )

    replies_sent = sum(
        1
        for item in logs
        if item.get("decision") == "reply"
        and item.get("reply")
    )

    st.metric(
        "Replies generated",
        replies_sent,
    )

    st.divider()

    st.subheader("Mode")

    live_mode = st.toggle(
        "LIVE",
        value=not dry_run,
        help=(
            "OFF = DRY RUN. "
            "ON = LIVE sending."
        ),
    )

    new_dry_run = not live_mode

    if new_dry_run != dry_run:
        settings["dry_run"] = new_dry_run
        save_settings(settings)
        st.rerun()

    if new_dry_run:
        st.info("🧪 DRY RUN")
        st.caption(
            "Replies are generated but never sent."
        )
    else:
        st.warning("🔴 LIVE")
        st.caption(
            "Real WhatsApp replies can be sent."
        )

    st.divider()

    st.subheader("Send Delay")

    new_min_delay = st.number_input(
        "Minimum delay (seconds)",
        min_value=1,
        max_value=300,
        value=max(1, min_delay),
        step=1,
    )

    new_max_delay = st.number_input(
        "Maximum delay (seconds)",
        min_value=1,
        max_value=600,
        value=max(1, max_delay),
        step=1,
    )

    if new_min_delay >= new_max_delay:
        st.error(
            "Minimum delay must be less than maximum delay."
        )
    else:
        if (
            new_min_delay != min_delay
            or new_max_delay != max_delay
        ):
            settings[
                "min_delay_seconds"
            ] = int(new_min_delay)

            settings[
                "max_delay_seconds"
            ] = int(new_max_delay)

            save_settings(settings)
            st.rerun()

    st.divider()

    st.subheader("Safety")

    if kill_switch_active():
        st.error(
            "🛑 KILL SWITCH ACTIVE"
        )

        st.caption(
            "All incoming messages are being skipped."
        )

        if st.button(
            "Clear kill switch",
            type="secondary",
            use_container_width=True,
        ):
            clear_kill_switch()
            st.rerun()

    else:
        if st.button(
            "🛑 KILL SWITCH",
            type="primary",
            use_container_width=True,
        ):
            activate_kill_switch()
            st.rerun()


if kill_switch_active():
    st.error(
        "🛑 KILL SWITCH ACTIVE — "
        "WhatsApp processing is disabled."
    )


if not logs:
    st.info(
        "Waiting for first message..."
    )

else:
    st.subheader("Recent Messages")

    for index, item in enumerate(logs):
        relationship = item.get(
            "relationship",
            "unknown",
        )

        icon, relationship_name = (
            relationship_badge(
                relationship
            )
        )

        decision = item.get(
            "decision",
            "ignore",
        )

        reason = item.get(
            "reason",
            "",
        )

        reply = item.get(
            "reply"
        )

        timestamp = item.get(
            "timestamp",
            "",
        )

        jid = item.get(
            "jid",
            "",
        )

        with st.container(
            border=True
        ):
            col1, col2, col3 = (
                st.columns(
                    [2, 2, 1]
                )
            )

            with col1:
                st.markdown(
                    f"**{icon} {relationship_name}**"
                )

            with col2:
                if decision == "reply":
                    st.success(
                        "Decision: REPLY"
                    )
                else:
                    st.warning(
                        "Decision: IGNORE"
                    )

            with col3:
                st.caption(
                    timestamp
                )

            st.caption(
                f"JID: {jid}"
            )

            st.markdown(
                f"**Reason:** {reason}"
            )

            if reply:
                st.markdown(
                    "**Generated reply:**"
                )

                st.info(reply)

            else:
                st.markdown(
                    "**Generated reply:** —"
                )

            retrieval_trace = item.get(
                "retrieval_trace",
                [],
            )

            with st.expander(
                f"Retrieval trace ({len(retrieval_trace)} results)"
            ):
                if retrieval_trace:
                    for result in retrieval_trace:
                        st.json(result)
                else:
                    st.caption(
                        "No retrieval results for this message."
                    )