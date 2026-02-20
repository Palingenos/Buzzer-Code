# Buzzer Automation

Automatically opens your door buzzer by detecting the intercom's incoming call and sending a DTMF tone — no manual interaction needed.

## How It Works

```
Buzzer calls your phone number
        │
        ▼
Call is instantly forwarded to Twilio (unconditional forwarding)
        │
        ▼
Twilio webhook (this server) answers immediately
        │
        ▼
Detects buzzer caller ID → sends DTMF "9" (x3 for reliability)
        │
        ▼
Door opens. You get an SMS notification.
```

Non-buzzer calls are forwarded through to your phone normally.

---

## Setup Guide

### Step 1: Twilio Account & Number

1. Sign up at [twilio.com](https://www.twilio.com/try-twilio) (free trial gives you $15 credit)
2. Buy a phone number (~$1.15/month) from the Twilio console
3. Note your **Account SID**, **Auth Token**, and **Twilio phone number**

### Step 2: Deploy This Server

You need this server running on a public URL. Choose one:

#### Option A: Railway (easiest, free tier available)

1. Push this code to a GitHub repo
2. Go to [railway.app](https://railway.app), create a new project from the repo
3. Add environment variables (see `.env.example`)
4. Railway gives you a public URL like `https://your-app.up.railway.app`

#### Option B: Render

1. Push to GitHub
2. Go to [render.com](https://render.com), create a new Web Service
3. Set build command: `pip install -r requirements.txt`
4. Set start command: `gunicorn app:app`
5. Add environment variables


#### Option C: Local + ngrok (for testing)

```bash
pip install -r requirements.txt
cp .env.example .env   # then edit .env with your values
python app.py
```

In another terminal:
```bash
ngrok http 5000
```

Use the ngrok URL for the Twilio webhook.

### Step 3: Configure Twilio Webhook

1. Go to [Twilio Console → Phone Numbers](https://console.twilio.com/us1/develop/phone-numbers/manage/incoming)
2. Click your purchased number
3. Under **Voice Configuration → A Call Comes In**:
   - Set to **Webhook**
   - URL: `https://YOUR-DOMAIN/voice`
   - Method: **POST**
4. Save

### Step 4: Find Your Buzzer's Caller ID

If you don't know the exact number your buzzer calls from:

1. Check your recent call history for the buzzer's calls
2. It may show as a local number or a number with an area code
3. Include the full number with country code (e.g., `+14155551234`)

### Step 5: Set Up iPhone Call Forwarding (Unconditional)

Forward **all** calls to Twilio so the buzzer call goes directly there with no delay.

#### On iPhone:

Go to **Settings → Phone → Call Forwarding** → toggle it **ON** → enter your Twilio phone number.

#### Or using carrier codes:

Open the **Phone** app and dial:

```
*21*YOUR_TWILIO_NUMBER#
```

Replace `YOUR_TWILIO_NUMBER` with your Twilio number (digits only, e.g., `*21*14155559999#`).

> **Note:** This varies by carrier. If the code above doesn't work:
> - **AT&T / T-Mobile:** The `*21*` code usually works
> - **Verizon:** Go to My Verizon app → call forwarding settings, or dial `*72` followed by the number
> - **Other carriers:** Contact your carrier or check their website for "unconditional call forwarding"

To **disable** forwarding later: dial `##21#` (or toggle off in Settings → Phone → Call Forwarding)

#### How this works with regular calls

All calls now go through Twilio, but the server handles them correctly:
- **Buzzer calls** → auto-answers with DTMF "9", door opens instantly
- **All other calls** → Twilio forwards them to your phone, so you still receive them normally

---

## Environment Variables

| Variable | Description | Example |
|---|---|---|
| `BUZZER_NUMBER` | The phone number your buzzer calls FROM | `+14155551234` |
| `YOUR_PHONE_NUMBER` | Your personal phone number | `+14155559999` |
| `TWILIO_PHONE_NUMBER` | Your purchased Twilio number | `+14155550000` |
| `TWILIO_ACCOUNT_SID` | From Twilio console | `ACXXXX...` |
| `TWILIO_AUTH_TOKEN` | From Twilio console | `xxxx...` |
| `DTMF_DIGIT` | Key to press (default: `9`) | `9` |
| `PAUSE_BEFORE_DTMF` | Seconds to wait before pressing (default: `1`) | `1` |
| `NOTIFY_SMS` | Send SMS when buzzer triggers (default: `true`) | `true` |

---

## Testing

1. Once deployed, check the health endpoint: `https://YOUR-DOMAIN/health`
2. Use [Twilio's test tools](https://console.twilio.com) to simulate an incoming call
3. Or have someone buzz your apartment and verify the door opens

## Cost

- **Twilio phone number:** ~$1.15/month
- **Incoming calls:** ~$0.0085/min (a 10-second buzzer call costs less than $0.01)
- **SMS notifications:** ~$0.0079/message
- **Hosting:** Free tier on Railway/Render is sufficient

Total: **~$1-2/month** for typical usage.
