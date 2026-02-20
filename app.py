import os
import logging
from datetime import datetime, timezone
from flask import Flask, request
from twilio.twiml.voice_response import VoiceResponse
from twilio.rest import Client
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("buzzer")

BUZZER_NUMBER = os.environ.get("BUZZER_NUMBER", "")
YOUR_PHONE = os.environ.get("YOUR_PHONE_NUMBER", "")
TWILIO_PHONE = os.environ.get("TWILIO_PHONE_NUMBER", "")
TWILIO_SID = os.environ.get("TWILIO_ACCOUNT_SID", "")
TWILIO_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN", "")
DTMF_DIGIT = os.environ.get("DTMF_DIGIT", "9")
NOTIFY_SMS = os.environ.get("NOTIFY_SMS", "true").lower() == "true"
PAUSE_SECONDS = int(os.environ.get("PAUSE_BEFORE_DTMF", "1"))


def normalize_phone(number: str) -> str:
    """Strip formatting so +1 (555) 123-4567 and +15551234567 both match."""
    return "".join(c for c in number if c.isdigit() or c == "+")


def send_notification(caller: str):
    if not (NOTIFY_SMS and TWILIO_SID and TWILIO_TOKEN and TWILIO_PHONE and YOUR_PHONE):
        return
    try:
        client = Client(TWILIO_SID, TWILIO_TOKEN)
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        client.messages.create(
            body=f"Door buzzer opened automatically at {timestamp} (caller: {caller})",
            from_=TWILIO_PHONE,
            to=YOUR_PHONE,
        )
        logger.info("SMS notification sent to %s", YOUR_PHONE)
    except Exception as e:
        logger.error("Failed to send SMS: %s", e)


@app.route("/voice", methods=["POST"])
def handle_call():
    """Twilio webhook: receives incoming calls and decides what to do."""
    caller = request.form.get("From", "")
    logger.info("Incoming call from %s", caller)

    resp = VoiceResponse()

    if normalize_phone(caller) == normalize_phone(BUZZER_NUMBER):
        logger.info("Buzzer number detected — sending DTMF '%s'", DTMF_DIGIT)
        resp.pause(length=PAUSE_SECONDS)
        resp.play(digits=f"w{DTMF_DIGIT}")
        resp.pause(length=2)
        resp.hangup()
        send_notification(caller)
    else:
        logger.info("Non-buzzer call from %s — forwarding to your phone", caller)
        resp.dial(YOUR_PHONE, caller_id=caller, timeout=30)

    return str(resp)


@app.route("/health", methods=["GET"])
def health():
    return {"status": "ok", "buzzer_number": BUZZER_NUMBER[:4] + "****"}


if __name__ == "__main__":
    if not BUZZER_NUMBER:
        logger.warning("BUZZER_NUMBER not set — all calls will be forwarded")
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
