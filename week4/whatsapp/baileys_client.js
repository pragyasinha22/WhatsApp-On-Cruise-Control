require("dotenv").config();

const fs = require("fs");
const path = require("path");

const {
  default: makeWASocket,
  useMultiFileAuthState,
  DisconnectReason,
  fetchLatestBaileysVersion,
} = require("@whiskeysockets/baileys");

const qrcode = require("qrcode-terminal");
const P = require("pino");
const axios = require("axios");

const BASE_DIR = path.join(__dirname, "..");

const SETTINGS_PATH = path.join(
  BASE_DIR,
  "config",
  "settings.json"
);

const RELATIONSHIP_MAP_PATH = path.join(
  BASE_DIR,
  "config",
  "relationship_map.json"
);

const KILL_SWITCH_PATH = path.join(
  BASE_DIR,
  "kill_switch.flag"
);

const DEFAULT_SETTINGS = {
  dry_run: true,
  min_delay_seconds: 3,
  max_delay_seconds: 12,
};

// Flask bridge
const BRIDGE_URL = "http://127.0.0.1:5001/process";


function loadSettings() {
  try {
    const raw = fs.readFileSync(
      SETTINGS_PATH,
      "utf8"
    );

    const data = JSON.parse(raw);

    if (!data || typeof data !== "object") {
      return { ...DEFAULT_SETTINGS };
    }

    const settings = {
      ...DEFAULT_SETTINGS,
      ...data,
    };

    const minDelay = Number(settings.min_delay_seconds);
    const maxDelay = Number(settings.max_delay_seconds);

    if (
      !Number.isFinite(minDelay) ||
      !Number.isFinite(maxDelay) ||
      minDelay <= 0 ||
      maxDelay <= 0 ||
      minDelay >= maxDelay
    ) {
      return { ...DEFAULT_SETTINGS };
    }

    settings.min_delay_seconds = minDelay;
    settings.max_delay_seconds = maxDelay;
    settings.dry_run = Boolean(settings.dry_run);

    return settings;
  } catch (error) {
    console.log(
      "[WARN] Could not read settings.json. Using safe defaults."
    );

    return { ...DEFAULT_SETTINGS };
  }
}


function enforceAllowlist(jid) {
  try {
    const raw = fs.readFileSync(
      RELATIONSHIP_MAP_PATH,
      "utf8"
    );

    const relationshipMap = JSON.parse(raw);

    if (
      !relationshipMap ||
      typeof relationshipMap !== "object"
    ) {
      return false;
    }

    const number = jid
      ? jid.split("@", 1)[0]
      : "";

    if (!number) {
      return false;
    }

    const relationship = relationshipMap[number];

    if (!relationship) {
      return false;
    }

    if (relationship === "unknown") {
      return false;
    }

    return true;
  } catch (error) {
    console.log(
      "[WARN] Could not read relationship_map.json."
    );

    return false;
  }
}


function extractMessageText(message) {
  if (!message) return "";

  if (message.conversation) {
    return message.conversation;
  }

  if (message.extendedTextMessage?.text) {
    return message.extendedTextMessage.text;
  }

  if (message.imageMessage?.caption) {
    return message.imageMessage.caption;
  }

  if (message.videoMessage?.caption) {
    return message.videoMessage.caption;
  }

  if (message.documentMessage?.caption) {
    return message.documentMessage.caption;
  }

  return "";
}


function getMessageType(message) {
  if (!message) return "other";

  if (
    message.conversation ||
    message.extendedTextMessage
  ) {
    return "text";
  }

  if (message.imageMessage) return "image";
  if (message.videoMessage) return "video";
  if (message.audioMessage) return "audio";

  return "other";
}


function isForwardedMessage(message) {
  const contextInfo =
    message?.extendedTextMessage?.contextInfo ||
    message?.imageMessage?.contextInfo ||
    message?.videoMessage?.contextInfo ||
    message?.documentMessage?.contextInfo;

  return Boolean(contextInfo?.isForwarded);
}


async function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}


async function startWhatsApp() {
  const { state, saveCreds } =
    await useMultiFileAuthState(
      path.join(BASE_DIR, "auth_info_baileys")
    );

  let version;

  try {
    const latest =
      await fetchLatestBaileysVersion();

    version = latest.version;
  } catch (error) {
    console.log(
      "[WARN] Could not fetch latest Baileys version."
    );
  }

  const sock = makeWASocket({
    auth: state,
    version,
    logger: P({ level: "silent" }),
    printQRInTerminal: false,
    browser: [
      "WhatsApp Cruise Control",
      "Chrome",
      "1.0.0",
    ],
  });

  sock.ev.on("creds.update", saveCreds);

  sock.ev.on(
    "connection.update",
    async (update) => {
      const {
        connection,
        lastDisconnect,
        qr,
      } = update;

      if (qr) {
        console.log(
          "[QR] Scan this QR code with your secondary WhatsApp number:"
        );

        qrcode.generate(qr, {
          small: true,
        });
      }

      if (connection === "open") {
        const settings = loadSettings();

        console.log(
          "[READY] WhatsApp connected."
        );

        console.log(
          `[MODE] ${
            settings.dry_run
              ? "DRY_RUN"
              : "LIVE"
          }`
        );
      }

      if (connection === "close") {
        const statusCode =
          lastDisconnect?.error?.output
            ?.statusCode;

        const shouldReconnect =
          statusCode !==
          DisconnectReason.loggedOut;

        console.log(
          `[DISCONNECT] Connection closed. Reconnect: ${shouldReconnect}`
        );

        if (shouldReconnect) {
          await startWhatsApp();
        }
      }
    }
  );


  sock.ev.on(
    "messages.upsert",
    async ({ type, messages }) => {
      if (type !== "notify") {
        console.log(
          "[SKIP] history sync message, ignoring"
        );

        return;
      }

      for (const message of messages) {
        if (!message?.message) {
          continue;
        }

        /*
         * Fresh safety settings are loaded before
         * processing each message.
         */
        const settings = loadSettings();

        /*
         * Kill switch check.
         */
        if (fs.existsSync(KILL_SWITCH_PATH)) {
          console.log(
            "[KILL SWITCH] active, skipping all processing"
          );

          continue;
        }

        if (message.key?.fromMe) {
          console.log("[SKIP] own message");
          continue;
        }

        const jid =
          message.key?.remoteJid;

        if (!jid) {
          console.log(
            "[SKIP] missing remote JID"
          );

          continue;
        }

        if (jid.endsWith("@g.us")) {
          console.log(
            "[SKIP] group message"
          );

          continue;
        }

        const messageContent =
          message.message;

        const text =
          extractMessageText(
            messageContent
          );

        const messageType =
          getMessageType(
            messageContent
          );

        const isForwarded =
          isForwardedMessage(
            messageContent
          );

        console.log(
          `[ROUTE] ${jid}`
        );

        console.log(
          `[ROUTE] type=${messageType}`
        );

        console.log(
          `[ROUTE] text=${text || "(no text)"}`
        );

        try {
          const response =
            await axios.post(
              BRIDGE_URL,
              {
                jid,
                text,
                message_type:
                  messageType,
                is_forwarded:
                  isForwarded,
                from_me: false,
              },
              {
                timeout: 30000,
              }
            );

          const result =
            response.data;

          console.log(
            `[DECISION] ${
              result.should_reply
                ? "reply"
                : "ignore"
            } — ${result.reason}`
          );

          if (
            !result.should_reply ||
            !result.reply
          ) {
            continue;
          }

          console.log(
            `[REPLY] ${result.reply}`
          );

          /*
           * DRY RUN:
           * Never call sendMessage.
           */
          if (settings.dry_run) {
            console.log(
              `[DRY_RUN] would reply to ${jid}: ${result.reply}`
            );

            continue;
          }

          /*
           * Independent allowlist check.
           * This check happens immediately
           * before the send.
           */
          if (!enforceAllowlist(jid)) {
            console.log(
              "[BLOCKED] failed independent allowlist check"
            );

            continue;
          }

          const minDelayMs =
            settings.min_delay_seconds *
            1000;

          const maxDelayMs =
            settings.max_delay_seconds *
            1000;

          const delayMs =
            Math.floor(
              Math.random() *
                (maxDelayMs -
                  minDelayMs +
                  1)
            ) +
            minDelayMs;

          console.log(
            `[SEND] waiting ${Math.round(
              delayMs / 1000
            )} seconds...`
          );

          await sleep(delayMs);

          /*
           * Final kill-switch check immediately
           * before sending.
           */
          if (fs.existsSync(KILL_SWITCH_PATH)) {
            console.log(
              "[KILL SWITCH] active, skipping all processing"
            );

            continue;
          }

          await sock.sendMessage(jid, {
            text: result.reply,
          });

          console.log(
            `[SEND] reply sent to ${jid}`
          );
        } catch (error) {
          console.error(
            "[ERROR] Could not process message:",
            error.response?.data ||
              error.message
          );
        }
      }
    }
  );
}


startWhatsApp().catch((error) => {
  console.error(
    "[FATAL]",
    error
  );
});