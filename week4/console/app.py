import base64
import html
import json
import os
import textwrap
from pathlib import Path

import streamlit as st
from streamlit_autorefresh import st_autorefresh


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[1]

LOG_PATH = BASE_DIR / "logs" / "console_feed.jsonl"
SETTINGS_PATH = BASE_DIR / "config" / "settings.json"
KILL_SWITCH_PATH = BASE_DIR / "kill_switch.flag"


# ============================================================
# DEFAULT SETTINGS
# ============================================================

DEFAULT_SETTINGS = {
    "dry_run": True,
    "min_delay_seconds": 3,
    "max_delay_seconds": 12,
}


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="WhatsApp Cruise Control",
    page_icon="💬",
    layout="wide",
)


# ============================================================
# AUTO REFRESH
# ============================================================

# st_autorefresh(
#     interval=2000,
#     key="console_refresh",
# )


# ============================================================
# CSS
# ============================================================
st.markdown(
    """
<style>

/* ============================================================
   DASHBOARD HEADER
   ============================================================ */

.dashboard-header {
    width: 100% !important;
    margin: 0 !important;
    padding: 0 !important;
    box-sizing: border-box !important;
}

[data-testid="stElementContainer"]:has(.dashboard-header) {
    position: sticky !important;
    top: 12px !important;
    z-index: 999991 !important;
    width: 400px !important;
    max-width: calc(100% - 12px) !important;
    margin-top: 40px !important;
    background-color: inherit !important;
}

.dashboard-title-row {
    display: flex !important;
    align-items: center !important;

    width: 100% !important;

    margin: 0 !important;
    padding: 0 !important;

    gap: 10px !important;

    min-height: 38px !important;

    box-sizing: border-box !important;
}

.dashboard-title-icon {
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;

    width: 34px !important;
    height: 34px !important;

    min-width: 34px !important;
    min-height: 34px !important;

    flex: 0 0 34px !important;
}

.dashboard-title-icon svg {
    display: block !important;

    width: 34px !important;
    height: 34px !important;
}

.dashboard-title-icon img {
    display: block !important;

    width: 34px !important;
    height: 34px !important;

    object-fit: contain !important;
}

.dashboard-title-text {
    display: block !important;

    color: var(--text-color) !important;

    font-size: 30px !important;
    font-weight: 750 !important;

    line-height: 1.2 !important;
    letter-spacing: -0.4px !important;

    margin: 0 !important;
    padding: 0 !important;

    white-space: nowrap !important;

    visibility: visible !important;
    opacity: 1 !important;
}

.dashboard-subtitle {
    display: block !important;

    color: var(--text-color) !important;

    font-size: 14px !important;
    font-weight: 400 !important;

    line-height: 1.4 !important;

    opacity: 0.68 !important;

    margin: 2px 0 12px 0 !important;
    padding: 0 !important;

    white-space: nowrap !important;

    visibility: visible !important;
}

.recent-title {
    display: block !important;

    color: var(--text-color) !important;

    font-size: 20px !important;
    font-weight: 700 !important;

    line-height: 1.3 !important;

    margin: 0 0 8px 0 !important;
    padding: 0 !important;

    visibility: visible !important;
}

/* ============================================================
   SIDEBAR TITLE
   ============================================================ */

.sidebar-title {
    font-size: 25px;
    font-weight: 700;
    line-height: 38px;

    min-height: 38px;

    white-space: nowrap;
    overflow: visible;

    margin: 0 !important;
    padding: 0 !important;
}


/* ============================================================
   MESSAGE CARDS
   ============================================================ */

.message-card {
    width: 100%;
    box-sizing: border-box;

    border: 1px solid color-mix(
        in srgb,
        var(--text-color) 12%,
        transparent
    );

    border-radius: 8px;

    padding: 10px 12px;

    margin: 0 0 7px 0 !important;

    background: var(--secondary-background-color);
    box-shadow: 0 1px 2px color-mix(
        in srgb,
        var(--text-color) 5%,
        transparent
    );
}


/* ============================================================
   SENDER SECTION
   ============================================================ */

.sender-section {
    display: flex;
    align-items: center;

    width: 100%;
    min-width: 0;

    gap: 7px;

    overflow: visible;
}


/* ============================================================
   RELATIONSHIP DOT
   ============================================================ */

.relationship-dot {
    width: 8px;
    height: 8px;

    min-width: 8px;
    flex: 0 0 8px;

    border-radius: 50%;

    display: inline-block;
}


/* ------------------------------------------------------------
   RELATIONSHIP DOT COLORS
   ------------------------------------------------------------ */

.dot-family {
    background: #7c3aed;
}

.dot-friend {
    background: #16a34a;
}

.dot-professional {
    background: #2563eb;
}

.dot-unknown {
    background: #6b7280;
}

.dot-group {
    background: #d97706;
}


/* ============================================================
   RELATIONSHIP BACKGROUND
   ============================================================ */

.relationship-pill {
    display: inline-flex;
    align-items: center;
    justify-content: center;

    flex: 0 0 auto;

    padding: 4px 9px;

    border-radius: 999px;

    font-size: 12px;
    font-weight: 700;
    line-height: 1.2;

    white-space: nowrap;
}


/* FAMILY */

.pill-family {
    background: #2563eb;
    color: #ffffff;
}


/* FRIEND */

.pill-friend {
    background: #15803d;
    color: #ffffff;
}


/* PROFESSIONAL */

.pill-professional {
    background: #6d28d9;
    color: #ffffff;
}


/* UNKNOWN */

.pill-unknown {
    background: #6b7280;
    color: #ffffff;
}


/* GROUP */

.pill-group {
    background: #0f766e;
    color: #ffffff;
}


/* ============================================================
   WHATSAPP JID SEPARATOR
   ============================================================ */

.jid-separator {
    flex: 0 0 auto;

    color: var(--text-color);
    opacity: 0.45;

    font-size: 13px;
}


/* ============================================================
   WHATSAPP JID
   ============================================================ */

.jid {
    display: block;

    flex: 1 1 auto;
    min-width: 0;

    color: var(--text-color);
    opacity: 0.8;

    font-size: 13px;
    line-height: 1.5;

    white-space: normal;

    overflow: visible;
    overflow-wrap: anywhere;
    word-break: break-word;
}


.message-top-row {
    display: flex !important;
    align-items: center !important;
    justify-content: space-between !important;
    gap: 12px !important;
    width: 100% !important;
    flex-wrap: nowrap !important;
}

.sender-section {
    display: flex !important;
    align-items: center !important;
    gap: 7px !important;
    min-width: 0 !important;
    flex: 1 1 auto !important;
}

.message-status-section {
    display: flex !important;
    align-items: center !important;
    justify-content: flex-end !important;
    gap: 8px !important;
    flex: 0 0 auto !important;
    white-space: nowrap !important;
}

.decision-pill {
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
    flex: 0 0 auto !important;
    padding: 3px 8px !important;
    border-radius: 6px !important;
    font-size: 11px !important;
    font-weight: 700 !important;
    line-height: 1.2 !important;
    white-space: nowrap !important;
}

.decision-reply {
    background: #22c55e !important;
    color: #ffffff !important;
}

.decision-ignore {
    background: #ef4444 !important;
    color: #ffffff !important;
}

.timestamp {
    display: inline-flex !important;
    align-items: center !important;
    font-size: 11px !important;
    line-height: 1.2 !important;
    white-space: nowrap !important;
    color: var(--text-color) !important;
    opacity: 0.65 !important;
    flex: 0 0 auto !important;
}


/* ============================================================
   REASON
   ============================================================ */

.reason-row {
    margin: 8px 0 0 0 !important;
    padding: 0 !important;

    color: var(--text-color);

    font-size: 13px;
    line-height: 1.5;
}

.reason-label {
    font-weight: 700;
}


/* ============================================================
   GENERATED REPLY
   ============================================================ */

.reply-row {
    display: flex;
    align-items: flex-start;

    gap: 7px;

    margin: 8px 0 0 0 !important;
    padding: 0 !important;

    flex-wrap: wrap;

    font-size: 13px;
    line-height: 1.5;
}

.reply-label {
    flex: 0 0 auto;

    font-size: 13px;
    font-weight: 700;
    line-height: 1.5;
}

.reply-box {
    flex: 1 1 200px;
    min-width: 0;

    padding: 5px 8px;

    border-radius: 6px;

    background: color-mix(
        in srgb,
        #16a34a 10%,
        var(--background-color)
    );

    border: 1px solid color-mix(
        in srgb,
        #16a34a 25%,
        var(--background-color)
    );

    font-size: 13px;
    line-height: 1.5;

    overflow-wrap: anywhere;
}

.reply-none {
    color: var(--text-color);
    opacity: 0.6;

    font-size: 13px;
    line-height: 1.5;
}


/* ============================================================
   RETRIEVAL TRACE
   ============================================================ */
.retrieval-card {
    border: 1px solid color-mix(
        in srgb,
        var(--text-color) 12%,
        transparent
    );

    border-radius: 7px;

    padding: 7px 9px;

    margin: 0 0 5px 0 !important;

    background: var(--background-color);

   
}

/* ============================================================
    RETRIEVAL TRACE CONTENT
    ============================================================ */

.retrieval-scroll {
    width: 100% !important;
    max-height: none !important;

    overflow-y: visible !important;
    overflow-x: hidden !important;

    box-sizing: border-box !important;

    padding-right: 6px !important;
}

.retrieval-label {
    font-size: 12px;
    font-weight: 700;
    line-height: 1.4;

    margin: 0 0 5px 0 !important;
}

.retrieval-row {
    margin: 0 0 4px 0 !important;
    padding: 0 !important;

    font-size: 13px;
    line-height: 1.5;
}

.retrieval-key {
    font-weight: 600;
}

.retrieval-value {
    margin-left: 3px;

    overflow-wrap: anywhere;
}

.retrieval-distance {
    margin: 3px 0 0 0 !important;
    padding: 0 !important;

    font-size: 11px;
    line-height: 1.4;

    color: var(--text-color);
    opacity: 0.65;
}


/* ============================================================
   WHOLE DASHBOARD PAGE SCROLL
   ============================================================ */

html,
body {
    overflow-y: auto !important;
    overflow-x: hidden !important;
}

[data-testid="stAppViewContainer"] {
    overflow: visible !important;
}

[data-testid="stMain"] {
    overflow-y: auto !important;
    overflow-x: hidden !important;
}

[data-testid="stMainBlockContainer"] {
    padding-top: 0.9rem !important;
    padding-bottom: 2rem !important;
    overflow: visible !important;
}

[data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"] {
    overflow: visible !important;
}

/* ============================================================
   NORMAL WHOLE-PAGE SCROLL
   ============================================================ */

html,
body {
    overflow-y: auto !important;
    overflow-x: hidden !important;
}

[data-testid="stAppViewContainer"] {
    overflow: visible !important;
}



[data-testid="stMainBlockContainer"] {
    padding-top: 0.9rem !important;
    padding-bottom: 2rem !important;
    overflow: visible !important;
}

[data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"] {
    overflow: visible !important;
}


/* ============================================================
   MAIN BACKGROUND
   ============================================================ */

[data-testid="stAppViewContainer"]:has(.dashboard-title),
[data-testid="stAppViewContainer"] > div:has(> [data-testid="stMain"]),
[data-testid="stMain"],
[data-testid="stMainBlockContainer"],
[data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"] {
    background-color: inherit !important;
}


/* ============================================================
   SIDEBAR STICKY TITLE
   ============================================================ */

[data-testid="stSidebarContent"],
[data-testid="stSidebarUserContent"],
[data-testid="stSidebarUserContent"] > div,
[data-testid="stVerticalBlock"]:has(.sidebar-title) {
    background-color: inherit !important;
}

[data-testid="stSidebarContent"] [data-testid="stElementContainer"]:has(.sidebar-title) {
    position: sticky !important;

    top: 0 !important;

    z-index: 10000 !important;

    box-sizing: border-box !important;

    display: flex !important;
    align-items: center !important;

    height: 60px !important;
    min-height: 60px !important;

    background-color: inherit !important;

    margin-top: -17px !important;
    margin-bottom: 0 !important;

    padding: 0 !important;
}


/* ============================================================
    RETRIEVAL TRACE PAGE FLOW
    ============================================================ */

[data-testid="stExpander"] {
    margin-top: 0 !important;
    margin-bottom: 4px !important;
}

/* Let expanded retrieval content grow with the dashboard page. */
[data-testid="stExpanderDetails"] {
    max-height: none !important;
    overflow-y: visible !important;
    overflow-x: hidden !important;
    padding-right: 8px !important;
    box-sizing: border-box !important;
}


/* ============================================================
   SIDEBAR SPACING
   ============================================================ */

[data-testid="stSidebar"] > div:first-child {
    padding-top: 0.1rem !important;
}

[data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
    gap: 0.3rem !important;
}

</style>
""",
    unsafe_allow_html=True,
)

# header_text_color = st.get_option("theme.textColor")

# if not header_text_color:
#     header_text_color = (
#         "#f8fafc"
#         if st.get_option("theme.base") == "dark"
#         else "#1f2937"
#     )

# st.markdown(
#     f"""
# <style>

# [data-testid="stHeading"] h1,
# h1 {{
#     display: block !important;

#     width: 100% !important;
#     max-width: 100% !important;

#     box-sizing: border-box !important;

#     margin: 0 !important;
#     padding: 0 !important;

#     color: {html.escape(header_text_color, quote=True)} !important;

#     font-size: 30px !important;
#     font-weight: 750 !important;

#     line-height: 1.3 !important;

#     letter-spacing: -0.35px !important;

#     white-space: nowrap !important;

#     overflow: visible !important;
#     overflow-wrap: normal !important;

#     visibility: visible !important;
#     opacity: 1 !important;

#     position: relative !important;
#     top: 2px !important;
# }}

# </style>
# """,
#     unsafe_allow_html=True,
# )


# ============================================================
# HELPERS
# ============================================================

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
                    records.append(
                        json.loads(line)
                    )

                except json.JSONDecodeError:
                    continue

    except OSError:
        return []

    return records[-limit:][::-1]


def load_settings():
    try:
        with SETTINGS_PATH.open(
            "r",
            encoding="utf-8",
        ) as f:

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


def kill_switch_active():
    return KILL_SWITCH_PATH.exists()


def activate_kill_switch():
    KILL_SWITCH_PATH.touch()


def clear_kill_switch():
    try:
        KILL_SWITCH_PATH.unlink()

    except FileNotFoundError:
        pass


def relationship_style(relationship):

    styles = {
        "family": {
            "name": "Family",
            "dot": "dot-family",
            "pill": "pill-family",
        },

        "friend": {
            "name": "Friend",
            "dot": "dot-friend",
            "pill": "pill-friend",
        },

        "professional": {
            "name": "Professional",
            "dot": "dot-professional",
            "pill": "pill-professional",
        },

        "unknown": {
            "name": "Unknown",
            "dot": "dot-unknown",
            "pill": "pill-unknown",
        },

        "group": {
            "name": "Group",
            "dot": "dot-group",
            "pill": "pill-group",
        },
    }

    return styles.get(
        relationship,
        {
            "name": str(relationship).title(),
            "dot": "dot-unknown",
            "pill": "pill-unknown",
        },
    )


def format_timestamp(timestamp):

    if not timestamp:
        return ""

    try:
        date_part, time_part = timestamp.split(
            "T",
            1,
        )

        time_part = time_part.split(
            "+",
            1,
        )[0]

        time_part = time_part.split(
            "Z",
            1,
        )[0]

        time_part = time_part.split(
            ".",
            1,
        )[0]

        return f"{date_part} {time_part}"

    except Exception:
        return str(timestamp)


def safe_text(value):

    return html.escape(
        str(
            value
            if value is not None
            else ""
        )
    )


# ============================================================
# LOAD DATA
# ============================================================

logs = load_logs(
    limit=20
)

settings = load_settings()

dry_run = bool(
    settings.get(
        "dry_run",
        True,
    )
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


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.html(
        """
        <div class="sidebar-title">
            Cruise Control
        </div>
        """,
    )
    
    replies_generated = sum(
        1
        for item in logs
        if item.get("decision") == "reply"
        and item.get("reply")
    )

    st.divider()

    # --------------------------------------------------------
    # MODE
    # --------------------------------------------------------

    st.subheader("Mode")

    live_mode = st.toggle(
        "LIVE",
        value=not dry_run,
        help="OFF = DRY RUN. ON = LIVE sending.",
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

    # --------------------------------------------------------
    # SEND DELAY
    # --------------------------------------------------------

    st.subheader("Send Delay")

    new_min_delay = st.number_input(
        "Minimum delay (seconds)",
        min_value=1,
        max_value=300,
        value=max(
            1,
            min_delay,
        ),
        step=1,
    )

    new_max_delay = st.number_input(
        "Maximum delay (seconds)",
        min_value=1,
        max_value=600,
        value=max(
            1,
            max_delay,
        ),
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

    # --------------------------------------------------------
    # SAFETY
    # --------------------------------------------------------

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

    st.divider()

    st.subheader("Metrics")

    st.metric(
        "Total messages processed",
        len(logs),
    )

    st.metric(
        "Total replies sent",
        replies_generated,
    )


# ============================================================
# PAGE HEADER
# ============================================================

# recent_title_html = (
#     '<div class="recent-title">Recent Messages</div>'
#     if logs
#     else ""
# )

# header_html = textwrap.dedent(
#     f"""
#     <div class="dashboard-title">

#         <div class="dashboard-title-icon">
#             <img
#                 src="https://upload.wikimedia.org/wikipedia/commons/6/6b/WhatsApp.svg"
#                 width="38"
#                 height="38"
#                 alt="WhatsApp"
#             >
#         </div>

#         <div class="dashboard-title-text">
#             WhatsApp Cruise Control
#         </div>

#     </div>

#     <div class="dashboard-subtitle">
#         Live message feed and AI reply decisions
#     </div>
#     {recent_title_html}
#     """
# )

# st.html(header_html)



# ---------------------------------
# ============================================================
# PAGE HEADER
# ============================================================

whatsapp_icon_url = "https://upload.wikimedia.org/wikipedia/commons/6/6b/WhatsApp.svg"

header_html = f"""
<div class="dashboard-header">

<div class="dashboard-title dashboard-title-row">

    <div class="dashboard-title-icon">
        <img src="{whatsapp_icon_url}" alt="WhatsApp logo">
    </div>

    <div class="dashboard-title-text">
        WhatsApp Cruise Control
    </div>

</div>

<div class="dashboard-subtitle">
    Live message feed and AI reply decisions
</div>

</div>
"""

st.html(header_html)

if logs:
    st.html(
        """
        <div class="recent-title">
            Recent Messages
        </div>
        """
    )

# ============================================================
# KILL SWITCH WARNING
# ============================================================

if kill_switch_active():

    st.error(
        "🛑 KILL SWITCH ACTIVE — WhatsApp processing is disabled."
    )


# ============================================================
# RECENT MESSAGES
# ============================================================

if not logs:

    st.info(
        "Waiting for first message..."
    )

else:
    for item in logs:

        # ----------------------------------------------------
        # MESSAGE DATA
        # ----------------------------------------------------

        relationship = item.get(
            "relationship",
            "unknown",
        )

        style = relationship_style(
            relationship
        )

        relationship_name = style["name"]

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

        formatted_timestamp = format_timestamp(
            timestamp
        )

        # ----------------------------------------------------
        # SAFE VALUES
        # ----------------------------------------------------

        safe_relationship = safe_text(
            relationship_name
        )

        safe_jid = safe_text(
            jid
        )

        safe_reason = safe_text(
            reason
        )

        safe_timestamp = safe_text(
            formatted_timestamp
        )

        # ----------------------------------------------------
        # DECISION
        # ----------------------------------------------------

        if decision == "reply":

            decision_text = "Decision: REPLY"

            decision_class = (
                "decision-pill decision-reply"
            )

        else:

            decision_text = "Decision: IGNORE"

            decision_class = (
                "decision-pill decision-ignore"
            )

        # ----------------------------------------------------
        # REPLY HTML
        # ----------------------------------------------------

        if reply:

            safe_reply = safe_text(
                reply
            )

            reply_html = textwrap.dedent(
                f"""
                <div class="reply-row">

                    <span class="reply-label">
                        Generated reply:
                    </span>

                    <span class="reply-box">
                        {safe_reply}
                    </span>

                </div>
                """
            )

        else:

            reply_html = textwrap.dedent(
                """
                <div class="reply-row">

                    <span class="reply-label">
                        Generated reply:
                    </span>

                    <span class="reply-none">
                        None
                    </span>

                </div>
                """
            )

        # ----------------------------------------------------
        # MESSAGE CARD
        # ----------------------------------------------------

        message_card = textwrap.dedent(
            f"""
            <div class="message-card">

                <div class="message-top-row">

                    <div class="sender-section">

                        <span class="relationship-dot {style["dot"]}">
                        </span>

                        <span class="relationship-pill {style["pill"]}">
                            {safe_relationship}
                        </span>

                        <span class="jid-separator">
                            •
                        </span>

                        <span class="jid" title="{safe_jid}">
                            {safe_jid}
                        </span>

                    </div>

                    <div class="message-status-section">

                        <span class="{decision_class}">
                            {decision_text}
                        </span>

                        <span class="timestamp">
                            {safe_timestamp}
                        </span>

                    </div>

                </div>

                <div class="reason-row">

                    <span class="reason-label">
                        Reason:
                    </span>

                    {safe_reason}

                </div>

                {reply_html}

            </div>
            """
        )

        # IMPORTANT:
        # Use st.html() for HTML.
        # Do NOT use st.markdown() here.

        st.html(
            message_card
        )

        # ----------------------------------------------------
        # RETRIEVAL TRACE
        # ----------------------------------------------------

        retrieval_trace = item.get(
            "retrieval_trace",
            [],
        )

        if not isinstance(
            retrieval_trace,
            list,
        ):

            retrieval_trace = []

        with st.expander(
            f"Retrieval trace ({len(retrieval_trace)} results)"
        ):

            if retrieval_trace:

                for result in retrieval_trace:

                    if isinstance(result, dict):

                        their_message = safe_text(
                            result.get("their_message", "")
                        )

                        my_reply = safe_text(
                            result.get("my_reply", "")
                        )

                        distance = result.get(
                            "distance",
                            ""
                        )

                        retrieval_card = textwrap.dedent(
                            f"""
                            <div class="retrieval-scroll">
                                <div class="retrieval-card">

                                    <div class="retrieval-label">
                                        Retrieved conversation
                                    </div>

                                    <div class="retrieval-row">

                                        <span class="retrieval-key">
                                            Their message:
                                        </span>

                                        <span class="retrieval-value">
                                            {their_message}
                                        </span>

                                    </div>

                                    <div class="retrieval-row">

                                        <span class="retrieval-key">
                                            My reply:
                                        </span>

                                        <span class="retrieval-value">
                                            {my_reply}
                                        </span>

                                    </div>

                                    <div class="retrieval-distance">
                                        Distance: {distance}
                                    </div>
                                </div>
                            </div>
                            """
                        )

                        st.html(retrieval_card)

                    else:

                        st.write(result)

            else:

                st.caption(
                    "No retrieval results for this message."
                )
# ----------------------------------------------

