import os
from google import genai
from dotenv import load_dotenv
load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
# response = client.models.generate_content(model="gemini-3.5-flash", contents="Say hello in one word.")
response = client.models.generate_content(model="gemini-2.5-flash", contents="Say hello in one word.")
print(response.text)


# -------------------------------------------------------------
# 5. Check the API test-
# python .\test.py
# (.venv) PS C:\Users\psinh\Desktop\MasaiProjects\WhatsApp_On-Cruise-Control\week1> python .\test.py
# Direct use of automatic function calling (AFC) in Models.generate_content is not recommended. Instead, we recommend to use AFC in Chat.send_message. Similarly, direct use of AFC in Models.generate_content_stream is not recommended. Instead, we recommend to use AFC in Chat.send_message_stream.
# Hello
# (.venv) PS C:\Users\psinh\Desktop\MasaiProjects\WhatsApp_On-Cruise-Control\week1> 

# ------------------------------------------------------------------------------------------------
# 4. python .\persona\test_persona.py-
# (.venv) PS C:\Users\psinh\Desktop\MasaiProjects\WhatsApp_On-Cruise-Control\week1> python .\persona\test_persona.py
# Direct use of automatic function calling (AFC) in Models.generate_content is not recommended. Instead, we recommend to use AFC in Chat.send_message. Similarly, direct use of AFC in Models.generate_content_stream is not recommended. Instead, we recommend to use AFC in Chat.send_message_stream.
# [friends] I am going to be late today, can you pick me up? -> Achaa, chalega. Main aa jaati hoon pick karne. Time bata de bas. 😂
# [family] Diwali pe ghar aaoge kya? -> Haan, I'll definitely be there! ❤️
# [professional] I have a new video ready. When can we connect? -> Badhiya hai, yaar! Kab connect karein?
# [friends] Coffee chale this evening? -> Haan, shaam ko free hoon, chalein? ☕
# [family] Dinner mein kya khana hai? -> Kuch simple bana lein? Jo aapko theek lage.
# (.venv) PS C:\Users\psinh\Desktop\MasaiProjects\WhatsApp_On-Cruise-Control\week1> 

# ----------------------------------------------------------------------------------------
# 3. Check style_signals.json Run-
# python -m json.tool .\persona\style_signals.json > $null
# if ($LASTEXITCODE -eq 0) { "style_signals.json: VALID" } else { "style_signals.json: INVALID" }
# (.venv) PS C:\Users\psinh\Desktop\MasaiProjects\WhatsApp_On-Cruise-Control\week1> python -m json.tool .\persona\style_signals.json > $null
# (.venv) PS C:\Users\psinh\Desktop\MasaiProjects\WhatsApp_On-Cruise-Control\week1> if ($LASTEXITCODE -eq 0) { "style_signals.json: VALID" } else { "style_signals.json: INVALID" }
# style_signals.json: VALID
# (.venv) PS C:\Users\psinh\Desktop\MasaiProjects\WhatsApp_On-Cruise-Control\week1> 

# ----------------------------------------------------------------------------------------
# 2. Check persona.json Run
# python -m json.tool .\persona\persona.json > $null
# if ($LASTEXITCODE -eq 0) { "persona.json: VALID" } else { "persona.json: INVALID" }

# (.venv) PS C:\Users\psinh\Desktop\MasaiProjects\WhatsApp_On-Cruise-Control\week1> python -m json.tool .\persona\persona.json > $null
# (.venv) PS C:\Users\psinh\Desktop\MasaiProjects\WhatsApp_On-Cruise-Control\week1> if ($LASTEXITCODE -eq 0) { "persona.json: VALID" } else { "persona.json: INVALID" }
# persona.json: VALID
# (.venv) PS C:\Users\psinh\Desktop\MasaiProjects\WhatsApp_On-Cruise-Control\week1> 
# -----------------------------------------------------------------------------------









# import html
# import json
# import os
# import textwrap
# from pathlib import Path

# import streamlit as st
# from streamlit_autorefresh import st_autorefresh


# # ============================================================
# # PATHS
# # ============================================================

# BASE_DIR = Path(__file__).resolve().parents[1]

# LOG_PATH = BASE_DIR / "logs" / "console_feed.jsonl"
# SETTINGS_PATH = BASE_DIR / "config" / "settings.json"
# KILL_SWITCH_PATH = BASE_DIR / "kill_switch.flag"


# # ============================================================
# # DEFAULT SETTINGS
# # ============================================================

# DEFAULT_SETTINGS = {
#     "dry_run": True,
#     "min_delay_seconds": 3,
#     "max_delay_seconds": 12,
# }


# # ============================================================
# # PAGE CONFIG
# # ============================================================

# st.set_page_config(
#     page_title="WhatsApp Cruise Control",
#     page_icon="💬",
#     layout="wide",
# )


# # ============================================================
# # AUTO REFRESH
# # ============================================================

# st_autorefresh(
#     interval=2000,
#     key="console_refresh",
# )


# # ============================================================
# # CSS
# # ============================================================
# st.markdown(
#     """
# <style>

# .dashboard-title {
#     display: flex;
#     align-items: center;
#     gap: 8px;
#     min-height: 38px;
#     flex-wrap: wrap;
#     margin: 0 !important;
#     padding: 0 !important;
# }

# .dashboard-title-icon {
#     width: 38px;
#     height: 38px;
#     flex: 0 0 38px;
#     display: flex;
#     align-items: center;
#     justify-content: center;
#     margin: 0 !important;
#     padding: 0 !important;
# }

# .dashboard-title-icon img {
#     display: block;
#     width: 38px;
#     height: 38px;
#     object-fit: contain;
# }

# .dashboard-title-text {
#     flex: 1 1 auto;
#     min-width: 0;
#     color: var(--text-color);
#     font-size: 25px;
#     font-weight: 700;
#     line-height: 1.2;
#     overflow-wrap: anywhere;
#     margin: 0 !important;
#     padding: 0 !important;
# }

# .sidebar-title {
#     font-size: 25px;
#     font-weight: 700;
#     line-height: 38px;
#     height: 38px;
#     margin: 0 !important;
#     padding: 0 !important;
# }

# .dashboard-subtitle {
#     color: var(--text-color);
#     font-size: 13px;
#     line-height: 1.4;
#     opacity: 0.7;
#     margin: 0 0 8px 0 !important;
#     padding: 0 !important;
# }

# .recent-title {
#     font-size: 18px;
#     font-weight: 700;
#     margin: 0 0 6px 0 !important;
#     padding: 0 !important;
# }

# .message-card {
#     border: 1px solid #e5e7eb;
#     border-radius: 10px;
#     padding: 8px 10px;
#     margin: 0 0 5px 0 !important;
#     background: white;
# }

# .message-top-row {
#     display: flex;
#     align-items: center;
#     gap: 7px;
#     flex-wrap: wrap;
# }

# .sender-section {
#     display: flex;
#     align-items: center;
#     gap: 5px;
#     flex: 1;
#     min-width: 220px;
# }

# .relationship-dot {
#     width: 7px;
#     height: 7px;
#     border-radius: 50%;
#     display: inline-block;
# }

# .dot-family {
#     background: #8b5cf6;
# }

# .dot-friend {
#     background: #22c55e;
# }

# .dot-professional {
#     background: #3b82f6;
# }

# .dot-unknown {
#     background: #9ca3af;
# }

# .dot-group {
#     background: #f59e0b;
# }

# .relationship-pill {
#     padding: 2px 6px;
#     border-radius: 999px;
#     font-size: 10px;
#     font-weight: 600;
# }

# .pill-family {
#     background: #ede9fe;
#     color: #6d28d9;
# }

# .pill-friend {
#     background: #dcfce7;
#     color: #15803d;
# }

# .pill-professional {
#     background: #dbeafe;
#     color: #1d4ed8;
# }

# .pill-unknown {
#     background: #f3f4f6;
#     color: #4b5563;
# }

# .pill-group {
#     background: #fef3c7;
#     color: #b45309;
# }

# .jid-separator {
#     color: #aaa;
# }

# .jid {
#     color: #555;
#     font-size: 11px;
#     overflow-wrap: anywhere;
# }

# .decision-pill {
#     padding: 2px 7px;
#     border-radius: 999px;
#     font-size: 10px;
#     font-weight: 700;
# }

# .decision-reply {
#     background: #dcfce7;
#     color: #166534;
# }

# .decision-ignore {
#     background: #f3f4f6;
#     color: #6b7280;
# }

# .timestamp {
#     color: #888;
#     font-size: 10px;
# }

# .reason-row {
#     margin: 5px 0 0 0 !important;
#     padding: 0 !important;
#     font-size: 12px;
#     color: #444;
# }

# .reason-label {
#     font-weight: 600;
# }

# .reply-row {
#     margin: 5px 0 0 0 !important;
#     padding: 0 !important;
#     display: flex;
#     align-items: flex-start;
#     gap: 5px;
#     flex-wrap: wrap;
# }

# .reply-label {
#     font-weight: 600;
#     font-size: 12px;
# }

# .reply-box {
#     padding: 4px 7px;
#     border-radius: 6px;
#     background: #f0fdf4;
#     border: 1px solid #bbf7d0;
#     font-size: 12px;
#     flex: 1;
#     min-width: 200px;
# }

# .reply-none {
#     color: #999;
#     font-size: 12px;
# }

# .retrieval-card {
#     border: 1px solid #e5e7eb;
#     border-radius: 7px;
#     padding: 6px 8px;
#     margin: 0 0 4px 0 !important;
#     background: #fafafa;
# }

# .retrieval-label {
#     font-size: 10px;
#     font-weight: 700;
#     margin: 0 0 3px 0 !important;
# }

# .retrieval-row {
#     margin: 0 0 2px 0 !important;
#     padding: 0 !important;
#     font-size: 11px;
# }

# .retrieval-key {
#     font-weight: 600;
# }

# .retrieval-value {
#     margin-left: 3px;
# }

# .retrieval-distance {
#     margin: 2px 0 0 0 !important;
#     padding: 0 !important;
#     font-size: 9px;
#     color: #777;
# }


# /* ============================================================
#    REMOVE STREAMLIT DEFAULT VERTICAL SPACE
#    ============================================================ */



# [data-testid="stMainBlockContainer"] {
#     padding-top: 2rem !important;
#     padding-bottom: 0 !important;
# }

# [data-testid="stVerticalBlock"] {
#     gap: 0.3rem !important;
# }

# [data-testid="stElementContainer"] {
#     margin-bottom: 0 !important;
#     padding-bottom: 0 !important;
#     overflow: visible !important;
# }



# [data-testid="stExpander"] {
#     margin-top: 0 !important;
#     margin-bottom: 4px !important;
# }
# [data-testid="stSidebar"] > div:first-child {
#     padding-top: 2rem !important;
# }

# [data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
#     gap: 0.3rem !important;
# }

# </style>
# """,
#     unsafe_allow_html=True,
# )


# # ============================================================
# # HELPERS
# # ============================================================

# def load_logs(limit=20):
#     if not LOG_PATH.exists():
#         return []

#     records = []

#     try:
#         with LOG_PATH.open("r", encoding="utf-8") as f:

#             for line in f:
#                 line = line.strip()

#                 if not line:
#                     continue

#                 try:
#                     records.append(
#                         json.loads(line)
#                     )

#                 except json.JSONDecodeError:
#                     continue

#     except OSError:
#         return []

#     return records[-limit:][::-1]


# def load_settings():
#     try:
#         with SETTINGS_PATH.open(
#             "r",
#             encoding="utf-8",
#         ) as f:

#             data = json.load(f)

#         if not isinstance(data, dict):
#             return DEFAULT_SETTINGS.copy()

#         settings = DEFAULT_SETTINGS.copy()
#         settings.update(data)

#         return settings

#     except (
#         FileNotFoundError,
#         json.JSONDecodeError,
#         OSError,
#         TypeError,
#     ):
#         return DEFAULT_SETTINGS.copy()


# def save_settings(settings):
#     SETTINGS_PATH.parent.mkdir(
#         parents=True,
#         exist_ok=True,
#     )

#     temp_path = SETTINGS_PATH.with_suffix(
#         ".tmp"
#     )

#     temp_path.write_text(
#         json.dumps(
#             settings,
#             indent=2,
#         ),
#         encoding="utf-8",
#     )

#     os.replace(
#         temp_path,
#         SETTINGS_PATH,
#     )


# def kill_switch_active():
#     return KILL_SWITCH_PATH.exists()


# def activate_kill_switch():
#     KILL_SWITCH_PATH.touch()


# def clear_kill_switch():
#     try:
#         KILL_SWITCH_PATH.unlink()

#     except FileNotFoundError:
#         pass


# def relationship_style(relationship):

#     styles = {
#         "family": {
#             "name": "Family",
#             "dot": "dot-family",
#             "pill": "pill-family",
#         },

#         "friend": {
#             "name": "Friend",
#             "dot": "dot-friend",
#             "pill": "pill-friend",
#         },

#         "professional": {
#             "name": "Professional",
#             "dot": "dot-professional",
#             "pill": "pill-professional",
#         },

#         "unknown": {
#             "name": "Unknown",
#             "dot": "dot-unknown",
#             "pill": "pill-unknown",
#         },

#         "group": {
#             "name": "Group",
#             "dot": "dot-group",
#             "pill": "pill-group",
#         },
#     }

#     return styles.get(
#         relationship,
#         {
#             "name": str(relationship).title(),
#             "dot": "dot-unknown",
#             "pill": "pill-unknown",
#         },
#     )


# def format_timestamp(timestamp):

#     if not timestamp:
#         return ""

#     try:
#         date_part, time_part = timestamp.split(
#             "T",
#             1,
#         )

#         time_part = time_part.split(
#             "+",
#             1,
#         )[0]

#         time_part = time_part.split(
#             "Z",
#             1,
#         )[0]

#         time_part = time_part.split(
#             ".",
#             1,
#         )[0]

#         return f"{date_part} {time_part}"

#     except Exception:
#         return str(timestamp)


# def safe_text(value):

#     return html.escape(
#         str(
#             value
#             if value is not None
#             else ""
#         )
#     )


# # ============================================================
# # LOAD DATA
# # ============================================================

# logs = load_logs(
#     limit=20
# )

# settings = load_settings()

# dry_run = bool(
#     settings.get(
#         "dry_run",
#         True,
#     )
# )

# try:
#     min_delay = int(
#         settings.get(
#             "min_delay_seconds",
#             3,
#         )
#     )

# except (TypeError, ValueError):
#     min_delay = 3


# try:
#     max_delay = int(
#         settings.get(
#             "max_delay_seconds",
#             12,
#         )
#     )

# except (TypeError, ValueError):
#     max_delay = 12


# # ============================================================
# # SIDEBAR
# # ============================================================

# with st.sidebar:

#     st.html(
#         """
#         <div class="sidebar-title">
#             Cruise Control
#         </div>
#         """,
#     )
    
#     st.metric(
#         "Messages processed",
#         len(logs),
#     )

#     replies_generated = sum(
#         1
#         for item in logs
#         if item.get("decision") == "reply"
#         and item.get("reply")
#     )

#     st.metric(
#         "Replies generated",
#         replies_generated,
#     )

#     st.divider()

#     # --------------------------------------------------------
#     # MODE
#     # --------------------------------------------------------

#     st.subheader("Mode")

#     live_mode = st.toggle(
#         "LIVE",
#         value=not dry_run,
#         help="OFF = DRY RUN. ON = LIVE sending.",
#     )

#     new_dry_run = not live_mode

#     if new_dry_run != dry_run:

#         settings["dry_run"] = new_dry_run

#         save_settings(settings)

#         st.rerun()

#     if new_dry_run:

#         st.info("🧪 DRY RUN")

#         st.caption(
#             "Replies are generated but never sent."
#         )

#     else:

#         st.warning("🔴 LIVE")

#         st.caption(
#             "Real WhatsApp replies can be sent."
#         )

#     st.divider()

#     # --------------------------------------------------------
#     # SEND DELAY
#     # --------------------------------------------------------

#     st.subheader("Send Delay")

#     new_min_delay = st.number_input(
#         "Minimum delay (seconds)",
#         min_value=1,
#         max_value=300,
#         value=max(
#             1,
#             min_delay,
#         ),
#         step=1,
#     )

#     new_max_delay = st.number_input(
#         "Maximum delay (seconds)",
#         min_value=1,
#         max_value=600,
#         value=max(
#             1,
#             max_delay,
#         ),
#         step=1,
#     )

#     if new_min_delay >= new_max_delay:

#         st.error(
#             "Minimum delay must be less than maximum delay."
#         )

#     else:

#         if (
#             new_min_delay != min_delay
#             or new_max_delay != max_delay
#         ):

#             settings[
#                 "min_delay_seconds"
#             ] = int(new_min_delay)

#             settings[
#                 "max_delay_seconds"
#             ] = int(new_max_delay)

#             save_settings(settings)

#             st.rerun()

#     st.divider()

#     # --------------------------------------------------------
#     # SAFETY
#     # --------------------------------------------------------

#     st.subheader("Safety")

#     if kill_switch_active():

#         st.error(
#             "🛑 KILL SWITCH ACTIVE"
#         )

#         st.caption(
#             "All incoming messages are being skipped."
#         )

#         if st.button(
#             "Clear kill switch",
#             type="secondary",
#             use_container_width=True,
#         ):

#             clear_kill_switch()

#             st.rerun()

#     else:

#         if st.button(
#             "🛑 KILL SWITCH",
#             type="primary",
#             use_container_width=True,
#         ):

#             activate_kill_switch()

#             st.rerun()


# # ============================================================
# # PAGE HEADER
# # ============================================================

# header_html = textwrap.dedent(
#     """
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
#     """
# )

# st.html(header_html)

# # ============================================================
# # KILL SWITCH WARNING
# # ============================================================

# if kill_switch_active():

#     st.error(
#         "🛑 KILL SWITCH ACTIVE — WhatsApp processing is disabled."
#     )


# # ============================================================
# # RECENT MESSAGES
# # ============================================================

# if not logs:

#     st.info(
#         "Waiting for first message..."
#     )

# else:

#     recent_title = textwrap.dedent(
#         """
#         <div class="recent-title">
#             Recent Messages
#         </div>
#         """
#     )

#     st.html(recent_title)

#     for item in logs:

#         # ----------------------------------------------------
#         # MESSAGE DATA
#         # ----------------------------------------------------

#         relationship = item.get(
#             "relationship",
#             "unknown",
#         )

#         style = relationship_style(
#             relationship
#         )

#         relationship_name = style["name"]

#         decision = item.get(
#             "decision",
#             "ignore",
#         )

#         reason = item.get(
#             "reason",
#             "",
#         )

#         reply = item.get(
#             "reply"
#         )

#         timestamp = item.get(
#             "timestamp",
#             "",
#         )

#         jid = item.get(
#             "jid",
#             "",
#         )

#         formatted_timestamp = format_timestamp(
#             timestamp
#         )

#         # ----------------------------------------------------
#         # SAFE VALUES
#         # ----------------------------------------------------

#         safe_relationship = safe_text(
#             relationship_name
#         )

#         safe_jid = safe_text(
#             jid
#         )

#         safe_reason = safe_text(
#             reason
#         )

#         safe_timestamp = safe_text(
#             formatted_timestamp
#         )

#         # ----------------------------------------------------
#         # DECISION
#         # ----------------------------------------------------

#         if decision == "reply":

#             decision_text = "Decision: REPLY"

#             decision_class = (
#                 "decision-pill decision-reply"
#             )

#         else:

#             decision_text = "Decision: IGNORE"

#             decision_class = (
#                 "decision-pill decision-ignore"
#             )

#         # ----------------------------------------------------
#         # REPLY HTML
#         # ----------------------------------------------------

#         if reply:

#             safe_reply = safe_text(
#                 reply
#             )

#             reply_html = textwrap.dedent(
#                 f"""
#                 <div class="reply-row">

#                     <span class="reply-label">
#                         Generated reply:
#                     </span>

#                     <span class="reply-box">
#                         {safe_reply}
#                     </span>

#                 </div>
#                 """
#             )

#         else:

#             reply_html = textwrap.dedent(
#                 """
#                 <div class="reply-row">

#                     <span class="reply-label">
#                         Generated reply:
#                     </span>

#                     <span class="reply-none">
#                         None
#                     </span>

#                 </div>
#                 """
#             )

#         # ----------------------------------------------------
#         # MESSAGE CARD
#         # ----------------------------------------------------

#         message_card = textwrap.dedent(
#             f"""
#             <div class="message-card">

#                 <div class="message-top-row">

#                     <div class="sender-section">

#                         <span class="relationship-dot {style["dot"]}">
#                         </span>

#                         <span class="relationship-pill {style["pill"]}">
#                             {safe_relationship}
#                         </span>

#                         <span class="jid-separator">
#                             •
#                         </span>

#                         <span class="jid" title="{safe_jid}">
#                             {safe_jid}
#                         </span>

#                     </div>

#                     <span class="{decision_class}">
#                         {decision_text}
#                     </span>

#                     <span class="timestamp">
#                         {safe_timestamp}
#                     </span>

#                 </div>

#                 <div class="reason-row">

#                     <span class="reason-label">
#                         Reason:
#                     </span>

#                     {safe_reason}

#                 </div>

#                 {reply_html}

#             </div>
#             """
#         )

#         # IMPORTANT:
#         # Use st.html() for HTML.
#         # Do NOT use st.markdown() here.

#         st.html(
#             message_card
#         )

#         # ----------------------------------------------------
#         # RETRIEVAL TRACE
#         # ----------------------------------------------------

#         retrieval_trace = item.get(
#             "retrieval_trace",
#             [],
#         )

#         if not isinstance(
#             retrieval_trace,
#             list,
#         ):

#             retrieval_trace = []

#         with st.expander(
#             f"Retrieval trace ({len(retrieval_trace)} results)"
#         ):

#             if retrieval_trace:

#                 for result in retrieval_trace:

#                     if isinstance(result, dict):

#                         their_message = safe_text(
#                             result.get("their_message", "")
#                         )

#                         my_reply = safe_text(
#                             result.get("my_reply", "")
#                         )

#                         distance = result.get(
#                             "distance",
#                             ""
#                         )

#                         retrieval_card = textwrap.dedent(
#                             f"""
#                             <div class="retrieval-card">

#                                 <div class="retrieval-label">
#                                     Retrieved conversation
#                                 </div>

#                                 <div class="retrieval-row">

#                                     <span class="retrieval-key">
#                                         Their message:
#                                     </span>

#                                     <span class="retrieval-value">
#                                         {their_message}
#                                     </span>

#                                 </div>

#                                 <div class="retrieval-row">

#                                     <span class="retrieval-key">
#                                         My reply:
#                                     </span>

#                                     <span class="retrieval-value">
#                                         {my_reply}
#                                     </span>

#                                 </div>

#                                 <div class="retrieval-distance">
#                                     Distance: {distance}
#                                 </div>

#                             </div>
#                             """
#                         )

#                         st.html(retrieval_card)

#                     else:

#                         st.write(result)

#             else:

#                 st.caption(
#                     "No retrieval results for this message."
#                 )